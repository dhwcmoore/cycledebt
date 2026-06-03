# CycleDebt: Obstruction Certificates for Cyclic Diagnostic Models

A certificate-producing diagnostic tool for cyclic systems.

It detects when local monitoring data is coherent but structurally insufficient
to warrant a global diagnostic claim, produces an independently checkable
obstruction certificate, and checks it through a four-layer verification stack
ending in a formally proved Rocq core.

---

## Quick start

For the verified HELICS federation run, see [helics_demo/outputs/auditor.log](helics_demo/outputs/auditor.log) for the raw runtime transitions and [HELICS_VERIFIED_RUN.md](HELICS_VERIFIED_RUN.md) for the recorded summary.

```bash
# Python demo — three diagnostic cases
python scripts/cyclediagnostic_demo.py examples/cps_loop_fault.json
python scripts/cyclediagnostic_demo.py examples/cps_loop_refined_sensor.json
python scripts/cyclediagnostic_demo.py examples/cps_loop_coherence_failure.json

# Independent OCaml/Zarith verifier
cd verify && make && make test

# Rocq-extracted verifier (requires Coq 8.18 + Zarith)
cd coq && make all

# Harness tests (12 tests of the JSON → certificate path)
cd coq && python3 test_harness.py
```

---

## Three verdicts

Every certificate has one of three formally accountable outcomes:

| Verdict | Condition | Meaning |
|---|---|---|
| `WARRANT DEBT` | D > 0 | Local data is coherent; a cyclic obstruction blocks the global claim |
| `GLOBALLY ADMISSIBLE` | D = 0 | No obstruction; the diagnostic claim is warranted |
| `COHERENCE FAILURE` | δ¹r ≠ 0 | Local data is self-contradictory; the H¹ question does not arise |

---

## Architecture

Four layers, from user-facing to formally proved:

```
Python demo engine  (scripts/cyclediagnostic_demo.py)
  generates cyclic diagnostic examples
  emits JSON certificates
    ↓
JSON certificate format  (certificates/*.json, certificates/certificate_schema.json)
  portable wire format, schema-validated
    ↓
Typed OCaml/Zarith verifier  (verify/verify_certificate.ml)
  independent of the engine
  six algebraic checks, exact Zarith rational arithmetic
    ↓
Rocq certificate core  (coq/DebtCertificate.v)
  formally proved soundness — five of six checks proved
  no Admitted, no Axiom, coqchk passes
    ↓ Extract.v (ExtrOcamlZBigInt)
Rocq-extracted OCaml verifier  (coq/run_extracted)
  compiled directly from the proved Rocq verify function
  arbitrary-precision integer arithmetic, no overflow
```

---

## Mathematics

Given a finite oriented graph G with interface residue r ∈ C¹(G; ℚ):

1. **Coherence test**: δ¹r = 0? If not → COHERENCE FAILURE.
2. **Admissibility test**: does δ⁰b = r have a solution? If yes → GLOBALLY ADMISSIBLE.
3. **Obstruction**: D(r) = ‖P_{H¹} r‖² = pᵀ G⁻¹ p via the Hodge Laplacian L₁ = δ⁰(δ⁰)ᵀ + (δ¹)ᵀδ¹. D > 0 → WARRANT DEBT.

For a single-cycle graph: D = p²/‖z‖² where p = ⟨z, r⟩ is the cyclic period.

Four-node CPS demo (z = (−1,−1,−1,1), r = (1,1,1,−2)):

    p = −5,   D = 25/4,   verdict = WARRANT DEBT

After sensor refinement (r = (1,1,1,3)):

    p = 0,    D = 0,      verdict = GLOBALLY ADMISSIBLE

---

## Demo output

```
$ python scripts/cyclediagnostic_demo.py examples/cps_loop_fault.json

CycleDebt Diagnostic Report

System: four-node CPS diagnostic loop
Claim:  fault_origin = B_Controller

Verdict: WARRANT DEBT

  Exact witness:
    cycle z = (-1, -1, -1, 1)
    residue r = (1, 1, 1, -2)
    period <z,r> = -5
    debt magnitude D = 25/4

  Suggested refinements:
    Option 1 — subtract harmonic debt (delta_r = (-5/4, -5/4, -5/4, 5/4))
    Option 2 — single-interface fix: A_Sensor-D_Monitor: -2 → 3

Independent verification:  PASS
```

---

## Rocq proof status

`coq/DebtCertificate.v` — no `Admitted`, no `Axiom`, `coqchk` passes,
all theorems `Closed under the global context`.

| Check | What it verifies | Rocq status |
|---|---|---|
| check1 | Each basis vector in ker(L₁) | **Proved** |
| check2 | Stored periods agree with ⟨h_i, r⟩ | **Proved** |
| check3 | r\_debt = G⁻¹p·h (harmonic direction) | Open — requires Gaussian elimination in Rocq |
| check4 | Stored D equals ‖r\_debt‖² | **Proved** |
| check5 | Cocycle flag agrees with D₁r = 0 | **Proved** |
| check6 | Verdict consistent with D and is\_cocycle | **Proved** |

Soundness theorems (all `Qed`):
- `harmonic_basis_sound`
- `globally_admissible_soundness`
- `warrant_debt_soundness`
- `stored_debt_norm_squared_correct`

Trusted execution path:

```
coqc DebtCertificate.v   →  proved verify function
coqc Extract.v           →  verify_extracted.ml  (BigInt via ExtrOcamlZBigInt)
ocamlfind ocamlopt ...   →  run_extracted binary
./run_extracted cert.json  →  PASS
```

---

## Repository layout

```
scripts/cyclediagnostic_demo.py     Python demo engine
examples/                           CPS diagnostic input models (3 cases)
certificates/                       Generated JSON certificates
certificates/certificate_schema.json  JSON Schema Draft-7

verify/
  verify_certificate.ml             Independent OCaml/Zarith verifier (6 checks)
  Makefile

coq/
  DebtCertificate.v                 Rocq types, checks, soundness theorems
  Extract.v                         Extraction directives (ExtrOcamlZBigInt)
  verify_extracted.ml               Generated by coqc Extract.v
  run_extracted.ml                  Harness: JSON → DebtCertificate → verify
  Makefile
  test_harness.py                   12 harness-layer tests

docs/
  caltais_one_page_demo.md          One-page technical overview

Core engine (imported by demo):
  residue_test.py                   Čech coboundary machinery
  admissibility_bridge.py           Harmonic decomposition
  finite_nerve_warrant_debt.py      Hodge Laplacian pipeline
  general_warrant_debt.py           Gram matrix debt formula
```

---

## Requirements

Python: `pip install -r requirements.txt` (sympy, numpy)

OCaml + Rocq: opam switch with Coq 8.18 and Zarith 1.14:
```bash
eval $(opam env --switch=coq818)
cd verify && make && make test
cd coq   && make all
```
