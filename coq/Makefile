.PHONY: all proof extract run clean

COQC      := /data/home-duston/.opam/coq818/bin/coqc
OCAMLFIND := /data/home-duston/.opam/coq818/bin/ocamlfind

all: proof extract run

# Compile and kernel-check the Rocq proof
proof: DebtCertificate.vo
	@echo "Rocq proof compiled."

DebtCertificate.vo: DebtCertificate.v
	$(COQC) DebtCertificate.v

# Generate extracted OCaml from proved Rocq code
extract: verify_extracted.ml

verify_extracted.ml verify_extracted.mli: DebtCertificate.vo Extract.v
	$(COQC) Extract.v
	@echo "Extraction complete: verify_extracted.ml"

# Compile and run the extracted verifier against all three certificates
run: run_extracted
	@echo "--- warrant debt ---"
	./run_extracted ../certificates/cps_loop_fault_certificate.json
	@echo "--- globally admissible ---"
	./run_extracted ../certificates/cps_loop_refined_sensor_certificate.json
	@echo "--- coherence failure ---"
	./run_extracted ../certificates/cps_loop_coherence_failure_certificate.json

run_extracted: verify_extracted.mli verify_extracted.ml run_extracted.ml
	$(OCAMLFIND) ocamlopt -package zarith -linkpkg \
	  verify_extracted.mli verify_extracted.ml run_extracted.ml -o run_extracted

clean:
	rm -f *.vo *.vos *.vok *.glob run_extracted *.cmi *.cmx *.o
