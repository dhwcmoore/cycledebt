(* CycleDebt certificate verifier — OCaml/Zarith

   Reads a certificate JSON file produced by scripts/cyclediagnostic_demo.py
   and re-derives all six algebraic checks from first principles.

   No engine code is imported.  The trust boundary starts here:
     untrusted JSON → parse → typed DebtCertificate → verify → PASS/FAIL

   Six checks (matching scripts/cyclediagnostic_demo.py verify_from_file):
     1.  L1 h = 0          each harmonic basis vector is in ker(L1)
     2.  p = ⟨h,r⟩         obstruction periods match stored values
     3.  r_debt = G⁻¹p·h   harmonic projection matches stored vector
     4.  D = ‖r_debt‖²     debt magnitude matches stored value
     5.  D1 r = 0 ↔ is_cocycle   (from stored D1_matrix)
     6.  verdict consistent with D and is_cocycle

   Arithmetic: exact rationals via Zarith (Q module).
   Depends on: zarith (ocamlfind package).  See Makefile.
*)

(* ===== Minimal JSON parser ===== *)

type json =
  | JNull
  | JBool   of bool
  | JString of string
  | JNumber of string    (* raw number literal — only appears in dim_H1 etc., not used by verifier *)
  | JArray  of json list
  | JObject of (string * json) list

exception Json_error of string

let parse_json (s : string) : json =
  let pos = ref 0 in
  let n   = String.length s in
  let chr () = s.[!pos] in
  let adv () = incr pos in
  let ws  () =
    while !pos < n &&
      (chr () = ' ' || chr () = '\t' || chr () = '\n' || chr () = '\r')
    do adv () done in
  let expect c =
    if !pos < n && chr () = c then adv ()
    else raise (Json_error
      (Printf.sprintf "expected '%c' at pos %d (got '%c')"
         c !pos (if !pos < n then chr () else '?'))) in
  let parse_str () =
    expect '"';
    let buf = Buffer.create 32 in
    let rec lp () =
      if !pos >= n then raise (Json_error "unterminated string");
      match chr () with
      | '"'  -> adv ()
      | '\\' ->
        adv ();
        let c = match chr () with
          | '"'  -> '"'  | '\\'  -> '\\'
          | 'n'  -> '\n' | 't'   -> '\t'
          | 'r'  -> '\r' | c     -> c  in
        Buffer.add_char buf c; adv (); lp ()
      | c -> Buffer.add_char buf c; adv (); lp ()
    in
    lp (); Buffer.contents buf
  in
  let rec value () =
    ws ();
    if !pos >= n then raise (Json_error "unexpected EOF");
    match chr () with
    | '"' -> JString (parse_str ())
    | '[' ->
      adv (); ws ();
      if !pos < n && chr () = ']' then (adv (); JArray [])
      else
        let rec lp acc =
          let v = value () in ws ();
          if !pos < n && chr () = ','
          then (adv (); lp (v :: acc))
          else (expect ']'; JArray (List.rev (v :: acc)))
        in lp []
    | '{' ->
      adv (); ws ();
      if !pos < n && chr () = '}' then (adv (); JObject [])
      else
        let rec lp acc =
          ws ();
          let k = parse_str () in ws (); expect ':'; ws ();
          let v = value () in ws ();
          if !pos < n && chr () = ','
          then (adv (); lp ((k, v) :: acc))
          else (expect '}'; JObject (List.rev ((k, v) :: acc)))
        in lp []
    | 't' when !pos + 4 <= n && String.sub s !pos 4 = "true"  ->
      pos := !pos + 4; JBool true
    | 'f' when !pos + 5 <= n && String.sub s !pos 5 = "false" ->
      pos := !pos + 5; JBool false
    | 'n' when !pos + 4 <= n && String.sub s !pos 4 = "null"  ->
      pos := !pos + 4; JNull
    | c when c = '-' || (c >= '0' && c <= '9') ->
      (* JSON number literal (integer or decimal).  The verifier doesn't use
         these fields directly; we just consume them without error. *)
      let start = !pos in
      if !pos < n && chr () = '-' then adv ();
      while !pos < n && chr () >= '0' && chr () <= '9' do adv () done;
      if !pos < n && chr () = '.' then begin
        adv ();
        while !pos < n && chr () >= '0' && chr () <= '9' do adv () done
      end;
      if !pos < n && (chr () = 'e' || chr () = 'E') then begin
        adv ();
        if !pos < n && (chr () = '+' || chr () = '-') then adv ();
        while !pos < n && chr () >= '0' && chr () <= '9' do adv () done
      end;
      JNumber (String.sub s start (!pos - start))
    | c -> raise (Json_error
        (Printf.sprintf "unexpected '%c' at pos %d" c !pos))
  in
  ws ();
  let v = value () in
  ws ();
  if !pos < n then raise (Json_error "trailing content after JSON value");
  v


(* ===== JSON field accessors ===== *)

let field key = function
  | JObject pairs ->
    (match List.assoc_opt key pairs with
     | Some v -> v
     | None   -> raise (Json_error (Printf.sprintf "missing field '%s'" key)))
  | _ -> raise (Json_error (Printf.sprintf "expected object for field '%s'" key))

let as_bool    = function JBool b -> b | _ -> raise (Json_error "expected bool")
let as_string  = function JString s -> s | _ -> raise (Json_error "expected string")
let as_array   = function JArray a  -> a | _ -> raise (Json_error "expected array")

(* Parse a string like "5", "-3", "25/4", "-5/4" into a Zarith Q rational. *)
let as_q j =
  let s = as_string j in
  match String.index_opt s '/' with
  | None   -> Q.of_string s
  | Some i ->
    let num = String.sub s 0 i in
    let den = String.sub s (i + 1) (String.length s - i - 1) in
    Q.div (Q.of_string num) (Q.of_string den)

let as_q_vec  j = Array.of_list (List.map as_q (as_array j))
let as_q_mat  j = Array.of_list (List.map as_q_vec (as_array j))


(* ===== Typed certificate ===== *)

type verdict = Globally_admissible | Warrant_debt | Coherence_failure

type debt_certificate = {
  residue        : Q.t array;
  l1_matrix      : Q.t array array;
  d1_matrix      : Q.t array array;   (* empty if no faces *)
  harmonic_basis : Q.t array array;   (* each row is one harmonic vector *)
  p_periods      : Q.t array;
  r_debt_vector  : Q.t array;
  debt_norm_sq   : Q.t;
  is_cocycle     : bool;
  verdict        : verdict;
}

let parse_verdict = function
  | "globally_admissible" -> Globally_admissible
  | "warrant_debt"        -> Warrant_debt
  | "coherence_failure"   -> Coherence_failure
  | s -> raise (Json_error (Printf.sprintf "unknown verdict '%s'" s))

let parse_certificate j =
  { residue        = as_q_vec (field "residue"               j);
    l1_matrix      = as_q_mat (field "L1_matrix"             j);
    d1_matrix      = as_q_mat (field "D1_matrix"             j);
    harmonic_basis = as_q_mat (field "harmonic_basis_vectors"j);
    p_periods      = as_q_vec (field "p_periods"             j);
    r_debt_vector  = as_q_vec (field "r_debt_vector"         j);
    debt_norm_sq   = as_q     (field "debt_norm_squared"     j);
    is_cocycle     = as_bool  (field "is_cocycle"            j);
    verdict        = parse_verdict (as_string (field "case"  j));
  }


(* ===== Exact rational linear algebra ===== *)

let dot (a : Q.t array) (b : Q.t array) : Q.t =
  assert (Array.length a = Array.length b);
  let s = ref Q.zero in
  for i = 0 to Array.length a - 1 do
    s := Q.add !s (Q.mul a.(i) b.(i))
  done;
  !s

let mat_vec (m : Q.t array array) (v : Q.t array) : Q.t array =
  Array.map (fun row -> dot row v) m

(* Gauss-Jordan elimination: solve A x = b over Q.
   A is n×n, b is length n.  Raises Failure if A is singular. *)
let q_solve (a : Q.t array array) (b : Q.t array) : Q.t array =
  let n = Array.length b in
  assert (n = Array.length a);
  (* Build augmented matrix [A | b] *)
  let aug = Array.init n (fun i ->
    Array.init (n + 1) (fun j -> if j < n then a.(i).(j) else b.(i))) in
  for col = 0 to n - 1 do
    (* Find non-zero pivot *)
    let pivot = ref (-1) in
    for row = col to n - 1 do
      if !pivot = -1 && not (Q.equal aug.(row).(col) Q.zero)
      then pivot := row
    done;
    if !pivot = -1 then failwith "singular Gram matrix in harmonic projection";
    (* Swap rows — begin/end prevents the next let-binding from being parsed
       as part of the if-then body by the OCaml parser. *)
    if !pivot <> col then begin
      let t = aug.(col) in
      aug.(col) <- aug.(!pivot);
      aug.(!pivot) <- t
    end;
    (* Scale pivot row to have leading 1 *)
    let p = aug.(col).(col) in
    for j = 0 to n do aug.(col).(j) <- Q.div aug.(col).(j) p done;
    (* Eliminate column from all other rows *)
    for row = 0 to n - 1 do
      if row <> col then begin
        let f = aug.(row).(col) in
        if not (Q.equal f Q.zero) then
          for j = 0 to n do
            aug.(row).(j) <- Q.sub aug.(row).(j) (Q.mul f aug.(col).(j))
          done
      end
    done
  done;
  Array.map (fun row -> row.(n)) aug

(* Compute r_debt = G^{-1}p · h, where G[i][j] = <h_i, h_j>, p_i = <h_i, r>.
   Returns the zero vector when basis is empty. *)
let harmonic_project (basis : Q.t array array) (r : Q.t array) : Q.t array =
  let k = Array.length basis in
  let nv = Array.length r in
  if k = 0 then Array.make nv Q.zero
  else begin
    let g = Array.init k (fun i -> Array.init k (fun j -> dot basis.(i) basis.(j))) in
    let p = Array.init k (fun i -> dot basis.(i) r) in
    let c = q_solve g p in
    Array.init nv (fun j ->
      let s = ref Q.zero in
      for i = 0 to k - 1 do s := Q.add !s (Q.mul c.(i) basis.(i).(j)) done;
      !s)
  end


(* ===== Verifier: six independent checks ===== *)

let verify (cert : debt_certificate) : bool * (string * bool) list =
  let checks = ref [] in
  let add name ok = checks := (name, ok) :: !checks in

  (* Check 1: each harmonic basis vector h lies in ker(L1) *)
  Array.iteri (fun i h ->
    let l1h = mat_vec cert.l1_matrix h in
    let ok  = Array.for_all (fun x -> Q.equal x Q.zero) l1h in
    add (Printf.sprintf "L1_h%d_in_ker_L1" i) ok)
  cert.harmonic_basis;

  (* Check 2: obstruction periods match stored p_periods *)
  let p_recomp = Array.init (Array.length cert.harmonic_basis)
      (fun i -> dot cert.harmonic_basis.(i) cert.residue) in
  let periods_ok =
    Array.length p_recomp = Array.length cert.p_periods &&
    Array.for_all2 Q.equal p_recomp cert.p_periods in
  add "periods_match_stored" periods_ok;

  (* Checks 3 and 4: recompute r_debt via Gram projection *)
  let r_debt_recomp = harmonic_project cert.harmonic_basis cert.residue in
  let r_debt_ok =
    Array.length r_debt_recomp = Array.length cert.r_debt_vector &&
    Array.for_all2 Q.equal r_debt_recomp cert.r_debt_vector in
  add "r_debt_matches_stored" r_debt_ok;

  let d_recomp = dot r_debt_recomp r_debt_recomp in
  add "D_matches_stored" (Q.equal d_recomp cert.debt_norm_sq);

  (* Check 5: cocycle condition D1 r = 0 ↔ is_cocycle (from stored D1_matrix) *)
  let is_cocycle_recomp =
    if Array.length cert.d1_matrix = 0 then true   (* no faces: vacuously a cocycle *)
    else
      let delta1r = mat_vec cert.d1_matrix cert.residue in
      Array.for_all (fun x -> Q.equal x Q.zero) delta1r
  in
  add "cocycle_flag_matches_D1_r" (is_cocycle_recomp = cert.is_cocycle);

  (* Check 6: verdict is consistent with re-derived D and cocycle flag *)
  let expected_verdict =
    if   not is_cocycle_recomp      then Coherence_failure
    else if Q.equal d_recomp Q.zero then Globally_admissible
    else                                 Warrant_debt
  in
  add "verdict_case_consistent" (cert.verdict = expected_verdict);

  let all = List.rev !checks in
  (List.for_all snd all, all)


(* ===== Entry point ===== *)

let verdict_to_string = function
  | Globally_admissible -> "GLOBALLY ADMISSIBLE"
  | Warrant_debt        -> "WARRANT DEBT"
  | Coherence_failure   -> "COHERENCE FAILURE"

let () =
  if Array.length Sys.argv < 2 then begin
    Printf.eprintf
      "Usage: verify_certificate <cert.json> [<cert2.json> ...]\n"; exit 1
  end;
  let overall = ref true in
  for k = 1 to Array.length Sys.argv - 1 do
    let path = Sys.argv.(k) in
    Printf.printf "\nCycleDebt Certificate Verifier  (OCaml / Zarith — exact Q arithmetic)\n";
    Printf.printf "Certificate: %s\n\n" path;
    (try
      let ic  = open_in path in
      let src = really_input_string ic (in_channel_length ic) in
      close_in ic;
      let j    = parse_json src in
      let cert = parse_certificate j in
      Printf.printf "Declared verdict: %s\n\n" (verdict_to_string cert.verdict);
      let (all_pass, checks) = verify cert in
      List.iteri (fun i (name, ok) ->
        Printf.printf "Check %-2d  %-38s  %s\n"
          (i + 1) name (if ok then "PASS" else "FAIL"))
        checks;
      Printf.printf "\nResult: %s\n"
        (if all_pass then "ALL CHECKS PASS" else "VERIFICATION FAILED");
      if not all_pass then overall := false
    with
    | Json_error msg ->
      Printf.eprintf "JSON error: %s\n" msg; overall := false
    | Failure msg ->
      Printf.eprintf "Arithmetic error: %s\n" msg; overall := false
    | Invalid_argument msg ->
      Printf.eprintf "Shape mismatch: %s\n" msg; overall := false)
  done;
  Printf.printf "\n";
  exit (if !overall then 0 else 1)
