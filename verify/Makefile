.PHONY: all clean test

# Use the opam coq818 switch where Zarith has proper .cmi files.
# Falls back to the system ocamlfind if the opam switch is not present.
OPAM_SWITCH := /data/home-duston/.opam/coq818/bin
OCAMLFIND   := $(if $(wildcard $(OPAM_SWITCH)/ocamlfind),$(OPAM_SWITCH)/ocamlfind,ocamlfind)
OCAMLOPT    := $(if $(wildcard $(OPAM_SWITCH)/ocamlopt),$(OPAM_SWITCH)/ocamlopt,ocamlopt)

all: verify_certificate

verify_certificate: verify_certificate.ml
	$(OCAMLFIND) ocamlopt -package zarith -linkpkg $< -o $@

# Run all three CPS certificates as a smoke test.
test: verify_certificate
	@echo "--- warrant debt ---"
	./verify_certificate ../certificates/cps_loop_fault_certificate.json
	@echo "--- globally admissible ---"
	./verify_certificate ../certificates/cps_loop_refined_sensor_certificate.json
	@echo "--- coherence failure ---"
	./verify_certificate ../certificates/cps_loop_coherence_failure_certificate.json

clean:
	rm -f verify_certificate *.cmx *.cmi *.o
