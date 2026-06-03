(* run_extracted.ml — harness for the Rocq-extracted CycleDebt verifier.

   Reads a certificate JSON, feeds it into the verify function generated
   from coq/DebtCertificate.v by Coq extraction, and reports PASS/FAIL.

   The extracted function carries the soundness guarantee proved in Rocq:
     verify returns true  ↔  all six algebraic conditions hold.

   Uses ExtrOcamlZBigInt: the extracted Q is
     { qnum : Big_int_Z.big_int; qden : Big_int_Z.big_int }
   so arithmetic is arbitrary-precision — no native-int overflow risk.

   Compile:
     ocamlfind ocamlopt -package zarith -linkpkg \
       verify_extracted.mli verify_extracted.ml run_extracted.ml -o run_extracted
*)

open Verify_extracted   (* brings q, verdict, debtCertificate, verify into scope *)


(* ===== Minimal JSON parser (self-contained) ===== *)

type json =
  | JNull | JBool of bool | JString of string | JNumber of string
  | JArray of json list | JObject of (string * json) list

exception Json_error of string

let parse_json (s : string) : json =
  let pos = ref 0 and n = String.length s in
  let chr () = s.[!pos] in
  let adv () = incr pos in
  let ws  () =
    while !pos < n &&
      (chr()=' ' || chr()='\t' || chr()='\n' || chr()='\r')
    do adv () done in
  let expect c =
    if !pos < n && chr() = c then adv ()
    else raise (Json_error (Printf.sprintf "expected '%c' at pos %d" c !pos)) in
  let parse_str () =
    expect '"';
    let buf = Buffer.create 32 in
    let rec lp () =
      if !pos >= n then raise (Json_error "unterminated string");
      match chr () with
      | '"' -> adv ()
      | '\\' ->
        adv ();
        let c = match chr() with '"'->'"' | '\\'->'\\'
                               | 'n'->'\n' | 't'->'\t' | c->c in
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
      if !pos < n && chr() = ']' then (adv (); JArray [])
      else
        let rec lp acc =
          let v = value () in ws ();
          if !pos < n && chr() = ',' then (adv (); lp (v :: acc))
          else (expect ']'; JArray (List.rev (v :: acc)))
        in lp []
    | '{' ->
      adv (); ws ();
      if !pos < n && chr() = '}' then (adv (); JObject [])
      else
        let rec lp acc =
          ws ();
          let k = parse_str () in ws (); expect ':'; ws ();
          let v = value () in ws ();
          if !pos < n && chr() = ',' then (adv (); lp ((k,v) :: acc))
          else (expect '}'; JObject (List.rev ((k,v) :: acc)))
        in lp []
    | 't' when !pos+4 <= n && String.sub s !pos 4 = "true" ->
      pos := !pos+4; JBool true
    | 'f' when !pos+5 <= n && String.sub s !pos 5 = "false" ->
      pos := !pos+5; JBool false
    | 'n' when !pos+4 <= n && String.sub s !pos 4 = "null" ->
      pos := !pos+4; JNull
    | c when c='-' || (c>='0' && c<='9') ->
      let start = !pos in
      if chr()='-' then adv ();
      while !pos<n && chr()>='0' && chr()<='9' do adv() done;
      if !pos<n && chr()='.' then (adv(); while !pos<n && chr()>='0'&&chr()<='9' do adv() done);
      JNumber (String.sub s start (!pos-start))
    | c -> raise (Json_error (Printf.sprintf "unexpected '%c' at pos %d" c !pos))
  in
  ws (); let v = value () in ws ();
  if !pos < n then raise (Json_error "trailing content");
  v

let field key = function
  | JObject pairs ->
    (match List.assoc_opt key pairs with
     | Some v -> v
     | None -> raise (Json_error ("missing field: " ^ key)))
  | _ -> raise (Json_error ("expected object for: " ^ key))

let as_bool = function JBool b -> b | _ -> raise (Json_error "expected bool")
let as_str  = function JString s -> s | _ -> raise (Json_error "expected string")
let as_arr  = function JArray a -> a | _ -> raise (Json_error "expected array")


(* ===== q construction from certificate strings ===== *)

(* Parse "n" or "n/d" into the extracted q type
   { qnum : Big_int_Z.big_int; qden : Big_int_Z.big_int }.
   Validates: denominator must be strictly positive. *)
let q_of_str s =
  match String.index_opt s '/' with
  | None   ->
    { qnum = Big_int_Z.big_int_of_string s;
      qden = Big_int_Z.unit_big_int }
  | Some i ->
    let n = Big_int_Z.big_int_of_string (String.sub s 0 i) in
    let d = Big_int_Z.big_int_of_string
              (String.sub s (i+1) (String.length s - i - 1)) in
    if Big_int_Z.le_big_int d Big_int_Z.zero_big_int then
      failwith (Printf.sprintf "q denominator must be positive in '%s'" s);
    { qnum = n; qden = d }

let q_list j = List.map (fun x -> q_of_str (as_str x)) (as_arr j)
let q_mat  j = List.map q_list (as_arr j)

let verdict_of_str = function
  | "warrant_debt"        -> WarrantDebt
  | "globally_admissible" -> GloballyAdmissible
  | "coherence_failure"   -> CoherenceFailure
  | s -> raise (Json_error ("unknown verdict: " ^ s))


(* ===== Certificate parser ===== *)

(* cert_nerve is not used by verify; populate with empty lists. *)
let dummy_nerve = { nerve_nodes = []; nerve_edges = []; nerve_faces = [] }

let parse_cert j = {
  cert_nerve      = dummy_nerve;
  cert_residue    = q_list   (field "residue"                j);
  cert_L1         = q_mat    (field "L1_matrix"              j);
  cert_D1         = q_mat    (field "D1_matrix"              j);
  cert_basis      = q_mat    (field "harmonic_basis_vectors"  j);
  cert_periods    = q_list   (field "p_periods"              j);
  cert_debt_vec   = q_list   (field "r_debt_vector"          j);
  cert_debt_sq    = q_of_str (as_str (field "debt_norm_squared" j));
  cert_is_cocycle = as_bool  (field "is_cocycle"             j);
  cert_verdict    = verdict_of_str (as_str (field "case"     j));
}

let verdict_str = function
  | GloballyAdmissible -> "GLOBALLY ADMISSIBLE"
  | WarrantDebt        -> "WARRANT DEBT"
  | CoherenceFailure   -> "COHERENCE FAILURE"


(* ===== Main ===== *)

let () =
  if Array.length Sys.argv < 2 then begin
    Printf.eprintf "Usage: run_extracted <cert.json> [<cert2.json> ...]\n";
    exit 1
  end;
  let overall = ref true in
  for k = 1 to Array.length Sys.argv - 1 do
    let path = Sys.argv.(k) in
    Printf.printf "\nCycleDebt — Rocq-Extracted Verifier  (Zarith arbitrary-precision arithmetic)\n";
    Printf.printf "Certificate: %s\n\n" path;
    (try
      let ic  = open_in path in
      let src = really_input_string ic (in_channel_length ic) in
      close_in ic;
      let j    = parse_json src in
      let cert = parse_cert j in
      Printf.printf "Declared verdict: %s\n" (verdict_str cert.cert_verdict);
      let ok = verify cert in
      Printf.printf "Extracted verify: %s\n" (if ok then "PASS" else "FAIL");
      if not ok then overall := false
    with
    | Json_error msg -> Printf.eprintf "JSON error: %s\n"      msg; overall := false
    | Failure msg    -> Printf.eprintf "Validation error: %s\n" msg; overall := false
    | exn            -> Printf.eprintf "Parse error: %s\n"
                          (Printexc.to_string exn); exit 2);
    Printf.printf "\n"
  done;
  exit (if !overall then 0 else 1)
