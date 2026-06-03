# CycleDebt — Running the Demo

Run all commands from the repository root (`residue-test/`).

---

## 1. Python demo engine

Three diagnostic cases, each producing a JSON certificate:

```bash
python scripts/cyclediagnostic_demo.py examples/cps_loop_fault.json
python scripts/cyclediagnostic_demo.py examples/cps_loop_refined_sensor.json
python scripts/cyclediagnostic_demo.py examples/cps_loop_coherence_failure.json
```

Expected results:

| File | Verdict | D | period |
|---|---|---|---|
| `cps_loop_fault.json` | WARRANT DEBT | 25/4 | −5 |
| `cps_loop_refined_sensor.json` | GLOBALLY ADMISSIBLE | 0 | 0 |
| `cps_loop_coherence_failure.json` | COHERENCE FAILURE | — | — |

All three print `Independent verification: PASS`.

The demo also prints suggested refinements for the warrant-debt case:
- Option 1: distribute the correction across all interfaces (minimal-norm delta)
- Option 2: single-interface fix (`A_Sensor-D_Monitor: -2 → 3`)

---

## 2. Independent OCaml/Zarith verifier

Reads only from the certificate JSON on disk.  Calls no engine function.

```bash
cd verify && make
make test
```

Expected output — six checks, all PASS, for all three certificates:

```
Check 1   L1_h0_in_ker_L1          PASS
Check 2   periods_match_stored      PASS
Check 3   r_debt_matches_stored     PASS
Check 4   D_matches_stored          PASS
Check 5   cocycle_flag_matches_D1_r PASS
Check 6   verdict_case_consistent   PASS
Result: ALL CHECKS PASS
```

---

## 3. Rocq-extracted verifier

Compiled from the proved Rocq `verify` function.
Uses Zarith arbitrary-precision integers (no native-int overflow).

```bash
cd coq && make all
```

The `Makefile` runs three steps:

1. `coqc DebtCertificate.v` — compiles the proved Rocq certificate core
2. `coqc Extract.v` — extracts `verify` to OCaml via `ExtrOcamlZBigInt`
3. Compiles `run_extracted` and runs it against all three certificates

Expected output:

```
Declared verdict: WARRANT DEBT        Extracted verify: PASS
Declared verdict: GLOBALLY ADMISSIBLE Extracted verify: PASS
Declared verdict: COHERENCE FAILURE   Extracted verify: PASS
```

---

## 4. Harness tests

Tests the JSON → `DebtCertificate` parsing layer and tamper detection:

```bash
cd coq && python3 test_harness.py
```

Expected: `12/12 tests passed`

| Test | Tests |
|---|---|
| Oversized integers | k=10¹⁵ scale still passes (BigInt handles it) |
| Malformed rational | unparseable → exit 2 |
| Zero denominator | harness validation rejects → exit 1 |
| Negative denominator | harness validation rejects → exit 1 |
| check1–check6 tamper | each tampered field individually causes FAIL |
| check3 gap (test 12) | wrong r\_debt direction, correct norm → passes (check3 open) |

---

## What each verifier checks

| Check | Python verifier | OCaml/Zarith verifier | Rocq extracted |
|---|---|---|---|
| check1: L1 h = 0 | ✓ | ✓ | ✓ proved |
| check2: p = ⟨h,r⟩ | ✓ | ✓ | ✓ proved |
| check3: r\_debt = G⁻¹p·h | ✓ | ✓ | open |
| check4: D = ‖r\_debt‖² | ✓ | ✓ | ✓ proved |
| check5: D₁r = 0 ↔ is\_cocycle | ✓ | ✓ | ✓ proved |
| check6: verdict consistent | ✓ | ✓ | ✓ proved |
