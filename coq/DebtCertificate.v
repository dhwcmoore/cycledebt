(* DebtCertificate.v — Rocq/Coq 8.18 specification for CycleDebt certificates.

   Stage 3 of the three-layer trust architecture:
     JSON (wire format)
       ↓  parse + validate (certificate_schema.json)
     Typed OCaml (verify/verify_certificate.ml — exact Zarith arithmetic)
       ↓  mirror + prove
     Rocq specification (this file — formal soundness theorems)

   The verifier is a concrete Rocq function.  Five checks are implemented:

     check1  h ∈ ker(L1)               (basis is harmonic)
     check2  p_i = ⟨h_i, r⟩           (stored periods are correct)
     check4  D = ‖r_debt‖²            (stored debt magnitude matches norm²)
     check5  D1 r = 0 ↔ is_cocycle   (cocycle flag is correct)
     check6  verdict consistent with D and is_cocycle

   Not yet implemented in Rocq: check3 (r_debt = G⁻¹p·h).
   This requires Gaussian elimination; acknowledged as the open formalization item.

   Four soundness theorems are proved: Qed.

   Coq 8.18 / Rocq.  Compile with:
     coqc DebtCertificate.v
*)

(* "From Coq" is the Coq 8.x form; Coq/Rocq 9.x uses "From Stdlib". *)
From Coq Require Import List QArith Bool.
Import ListNotations.
Open Scope Q_scope.

(* ===== Formal types ===== *)

Inductive Verdict : Type :=
  | GloballyAdmissible : Verdict
  | WarrantDebt        : Verdict
  | CoherenceFailure   : Verdict.

Record FiniteNerve : Type := mkNerve {
  nerve_nodes : list nat;
  nerve_edges : list (nat * nat);
  nerve_faces : list (nat * nat * nat)
}.

Record DebtCertificate : Type := mkCert {
  cert_nerve        : FiniteNerve;
  cert_residue      : list Q;
  cert_L1           : list (list Q);
  cert_D1           : list (list Q);
  cert_basis        : list (list Q);
  cert_periods      : list Q;
  cert_debt_vec     : list Q;
  cert_debt_sq      : Q;
  cert_is_cocycle   : bool;
  cert_verdict      : Verdict
}.


(* ===== Rational linear algebra ===== *)

Definition dot (u v : list Q) : Q :=
  fold_right Qplus 0
    (map (fun p => fst p * snd p) (combine u v)).

Definition mat_vec (M : list (list Q)) (v : list Q) : list Q :=
  map (fun row => dot row v) M.

Definition all_zero (v : list Q) : Prop :=
  Forall (fun x => x == 0) v.


(* ===== Key predicates ===== *)

Definition is_harmonic (L1 : list (list Q)) (h : list Q) : Prop :=
  all_zero (mat_vec L1 h).

Definition basis_is_harmonic (cert : DebtCertificate) : Prop :=
  Forall (is_harmonic (cert_L1 cert)) (cert_basis cert).

Definition cocycle_condition (cert : DebtCertificate) : Prop :=
  all_zero (mat_vec (cert_D1 cert) (cert_residue cert)).

Definition has_warrant_debt (cert : DebtCertificate) : Prop :=
  ~ (cert_debt_sq cert == 0).


(* ===== Boolean zero check and its soundness lemma ===== *)

Definition Qeq_bool0 (x : Q) : bool := Qeq_bool x 0.

Lemma Qeq_bool0_iff : forall x, Qeq_bool0 x = true <-> x == 0.
Proof.
  intro x. unfold Qeq_bool0. apply Qeq_bool_iff.
Qed.

Definition vec_is_zero_b (v : list Q) : bool :=
  forallb Qeq_bool0 v.

Lemma vec_is_zero_b_sound : forall v,
  vec_is_zero_b v = true -> all_zero v.
Proof.
  intros v Hv.
  unfold vec_is_zero_b in Hv.
  unfold all_zero.
  rewrite Forall_forall.
  intros x Hx.
  rewrite forallb_forall in Hv.
  apply Qeq_bool0_iff.
  exact (Hv x Hx).
Qed.


(* ===== Concrete verifier — five boolean checks ===== *)

(** Check 1: every harmonic basis vector lies in ker(L1). *)
Definition check1 (cert : DebtCertificate) : bool :=
  forallb
    (fun h => vec_is_zero_b (mat_vec (cert_L1 cert) h))
    (cert_basis cert).

(** Check 2: stored periods agree with actual inner products ⟨h_i, r⟩. *)
Definition check2 (cert : DebtCertificate) : bool :=
  forallb (fun p => Qeq_bool (fst p) (snd p))
    (combine
      (map (fun h => dot h (cert_residue cert)) (cert_basis cert))
      (cert_periods cert)).

(** Check 4: stored debt magnitude agrees with ‖cert_debt_vec‖².
    (check3 — r_debt = G⁻¹p·h — is not yet formalised: see file header.) *)
Definition check4 (cert : DebtCertificate) : bool :=
  Qeq_bool (dot (cert_debt_vec cert) (cert_debt_vec cert)) (cert_debt_sq cert).

(** Check 5: cocycle flag agrees with D1 r = 0. *)
Definition check5 (cert : DebtCertificate) : bool :=
  if cert_is_cocycle cert
  then vec_is_zero_b (mat_vec (cert_D1 cert) (cert_residue cert))
  else negb (vec_is_zero_b (mat_vec (cert_D1 cert) (cert_residue cert))).

(** Check 6: declared verdict is consistent with D and is_cocycle. *)
Definition check6 (cert : DebtCertificate) : bool :=
  match cert_verdict cert with
  | CoherenceFailure   => negb (cert_is_cocycle cert)
  | GloballyAdmissible => cert_is_cocycle cert && Qeq_bool0 (cert_debt_sq cert)
  | WarrantDebt        => cert_is_cocycle cert &&
                          negb (Qeq_bool0 (cert_debt_sq cert))
  end.

Definition verify (cert : DebtCertificate) : bool :=
  check1 cert && check2 cert && check4 cert && check5 cert && check6 cert.


(* ===== Soundness theorems ===== *)

(** Checks 1–2–4–5–6 unfold as a left-associated &&-chain:
      ((((check1 && check2) && check4) && check5) && check6) *)

Theorem harmonic_basis_sound :
  forall cert : DebtCertificate,
    verify cert = true ->
    basis_is_harmonic cert.
Proof.
  intros cert Hv.
  unfold verify in Hv.
  apply andb_true_iff in Hv. destruct Hv as [Hv5 _].
  apply andb_true_iff in Hv5. destruct Hv5 as [Hv4 _].
  apply andb_true_iff in Hv4. destruct Hv4 as [Hv12 _].
  apply andb_true_iff in Hv12. destruct Hv12 as [H1 _].
  unfold check1 in H1.
  unfold basis_is_harmonic, is_harmonic.
  rewrite forallb_forall in H1.
  apply Forall_forall.
  intros h Hh.
  apply vec_is_zero_b_sound.
  exact (H1 h Hh).
Qed.

Theorem globally_admissible_soundness :
  forall cert : DebtCertificate,
    verify cert = true ->
    cert_verdict cert = GloballyAdmissible ->
    cert_debt_sq cert == 0.
Proof.
  intros cert Hv Hverd.
  unfold verify in Hv.
  apply andb_true_iff in Hv. destruct Hv as [_ H6].
  unfold check6 in H6.
  rewrite Hverd in H6.
  apply andb_true_iff in H6. destruct H6 as [_ Hd].
  apply Qeq_bool0_iff.
  exact Hd.
Qed.

Theorem warrant_debt_soundness :
  forall cert : DebtCertificate,
    verify cert = true ->
    cert_verdict cert = WarrantDebt ->
    cocycle_condition cert /\ has_warrant_debt cert.
Proof.
  intros cert Hv Hverd.
  unfold verify in Hv.
  apply andb_true_iff in Hv. destruct Hv as [Hv5 H6].
  apply andb_true_iff in Hv5. destruct Hv5 as [Hv4 H5].
  unfold check6 in H6. rewrite Hverd in H6.
  apply andb_true_iff in H6. destruct H6 as [Hcoc Hnz].
  split.
  - unfold cocycle_condition.
    unfold check5 in H5.
    rewrite Hcoc in H5.
    apply vec_is_zero_b_sound.
    exact H5.
  - unfold has_warrant_debt.
    intro Heq.
    apply negb_true_iff in Hnz.
    assert (Hb : Qeq_bool0 (cert_debt_sq cert) = true).
    { apply Qeq_bool0_iff. exact Heq. }
    rewrite Hb in Hnz.
    discriminate.
Qed.

(** Check 4 guarantees that the stored debt magnitude equals ‖cert_debt_vec‖². *)
Theorem stored_debt_norm_squared_correct :
  forall cert : DebtCertificate,
    verify cert = true ->
    dot (cert_debt_vec cert) (cert_debt_vec cert) == cert_debt_sq cert.
Proof.
  intros cert Hv.
  unfold verify in Hv.
  apply andb_true_iff in Hv. destruct Hv as [Hv5 _].
  apply andb_true_iff in Hv5. destruct Hv5 as [Hv4 _].
  apply andb_true_iff in Hv4. destruct Hv4 as [_ H4].
  unfold check4 in H4.
  apply Qeq_bool_iff in H4.
  exact H4.
Qed.

(** The three verdicts are exhaustive. *)
Theorem verdict_exhaustive :
  forall cert : DebtCertificate,
    cert_verdict cert = GloballyAdmissible \/
    cert_verdict cert = WarrantDebt \/
    cert_verdict cert = CoherenceFailure.
Proof.
  intros cert. destruct (cert_verdict cert); auto.
Qed.
