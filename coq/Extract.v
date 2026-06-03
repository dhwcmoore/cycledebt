(* Extract.v — Coq extraction directives for DebtCertificate.v.

   Generates verify_extracted.ml from the proved Rocq verify function.

   This version uses ExtrOcamlZBigInt so that Coq's Z and positive
   both map to Big_int_Z.big_int (Zarith arbitrary-precision integers).
   The extracted verifier is therefore valid for certificates of any size,
   with no native-int overflow risk.

   Run:
     coqc DebtCertificate.v Extract.v

   Compile the harness:
     ocamlfind ocamlopt -package zarith -linkpkg \
       verify_extracted.mli verify_extracted.ml run_extracted.ml -o run_extracted
*)

(* "From Coq" is the Coq 8.x form; Coq/Rocq 9.x uses "From Stdlib". *)
From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlZBigInt.
Load "DebtCertificate".

Set Extraction Output Directory ".".
Extraction "verify_extracted.ml" verify.
