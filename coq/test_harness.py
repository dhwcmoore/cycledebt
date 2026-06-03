#!/usr/bin/env python3
"""
Harness-layer tests for run_extracted — the Rocq-extracted CycleDebt verifier.

Tests cover the remaining trust boundary: the JSON parser and the five
algebraic checks implemented in the Rocq verify function.

Exit codes:
  0 — certificate verified (all checks pass)
  1 — certificate rejected (Failure / algebraically invalid)
  2 — certificate unparseable (uncaught exception: bad string, bad JSON)

Twelve tests:
  1. Oversized integers: k=10^15 scale still passes (BigInt not overflow)
  2. Malformed rational string: unparseable → exit 2
  3. Zero denominator: harness validation rejects → exit 1
  4. Negative denominator: harness validation rejects → exit 1
  5. Tampered harmonic basis (check1 fails): L1*h ≠ 0
  6. Wrong period stored (check2 fails): p ≠ ⟨h,r⟩
  7. Wrong r_debt magnitude (check4 fails): ‖r_debt‖² ≠ D
  8. Wrong debt_norm_squared (check4 fails): stored D ≠ ‖r_debt‖²
  9. Flipped is_cocycle flag (check5 fails)
 10. Wrong verdict (check6 fails)
 11. Original certificate unmodified: passes
 12. Wrong r_debt DIRECTION but correct norm: check4 passes (check3 gap documented)
"""

import json, os, subprocess, sys, tempfile
from copy import deepcopy
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUN  = REPO / "coq" / "run_extracted"
BASE = REPO / "certificates" / "cps_loop_fault_certificate.json"


def run_cert(cert: dict) -> int:
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
        json.dump(cert, f)
        path = f.name
    try:
        r = subprocess.run([str(RUN), path], capture_output=True, text=True)
        return r.returncode
    finally:
        os.unlink(path)


def test(label: str, cert: dict, expect: str) -> bool:
    """expect: 'pass' (0) | 'fail' (1) | 'error' (2)."""
    rc = run_cert(cert)
    expected_rc = {"pass": 0, "fail": 1, "error": 2}[expect]
    ok = (rc == expected_rc)
    mark = "✓" if ok else "✗"
    print(f"  {mark}  {label:<62}  expect={expect}  got={rc}")
    return ok


def base() -> dict:
    return json.loads(BASE.read_text())


def scale_rat(s: str, k: int) -> str:
    """Multiply rational string 'n' or 'n/d' by k."""
    if "/" in s:
        n, d = s.split("/")
        return f"{int(n)*k}/{d}"
    return str(int(s) * k)


def scale_cert(c: dict, k: int) -> dict:
    """
    Scale a certificate by k so that entries exceed native-int range.

    Scaling rules (from linearity of the algebraic checks):
      residue, L1_matrix, harmonic_basis_vectors  → each entry × k
      p_periods, debt_norm_squared                → each entry × k²
      r_debt_vector                               → each entry × k
    All five algebraic checks remain satisfied after scaling.
    """
    k2 = k * k
    s = deepcopy(c)
    s["residue"]                = [scale_rat(v, k)  for v in c["residue"]]
    s["L1_matrix"]              = [[scale_rat(x, k)  for x in row]
                                   for row in c["L1_matrix"]]
    s["harmonic_basis_vectors"] = [[scale_rat(x, k)  for x in row]
                                   for row in c["harmonic_basis_vectors"]]
    s["p_periods"]              = [scale_rat(v, k2) for v in c["p_periods"]]
    s["r_debt_vector"]          = [scale_rat(v, k)  for v in c["r_debt_vector"]]
    s["debt_norm_squared"]      = scale_rat(c["debt_norm_squared"], k2)
    return s


print("\nCycleDebt harness-layer tests\n")
results = []

# 1. Oversized integers: scale by 10^15 — BigInt handles it, checks still hold
results.append(test(
    "oversized integers (k=10^15, all five checks hold)",
    scale_cert(base(), 10**15), "pass"))

# 2. Malformed rational — big_int_of_string raises Invalid_argument → exit 2
c = base(); c["debt_norm_squared"] = "banana"
results.append(test(
    "malformed rational string → unparseable (exit 2)",
    c, "error"))

# 3. Zero denominator — harness failwith → Failure caught → exit 1
c = base(); c["debt_norm_squared"] = "25/0"
results.append(test(
    "zero denominator → harness validation rejects (exit 1)",
    c, "fail"))

# 4. Negative denominator — same path as above
c = base(); c["debt_norm_squared"] = "25/-4"
results.append(test(
    "negative denominator → harness validation rejects (exit 1)",
    c, "fail"))

# 5. Tampered harmonic basis → check1 (L1*h = 0) fails
c = base(); c["harmonic_basis_vectors"] = [["1", "0", "0", "0"]]
results.append(test(
    "tampered harmonic basis (check1: L1*h ≠ 0)",
    c, "fail"))

# 6. Wrong period stored → check2 (p = ⟨h,r⟩) fails
c = base(); c["p_periods"] = ["0"]          # correct is -5
results.append(test(
    "wrong p_periods stored (check2: p ≠ ⟨h,r⟩)",
    c, "fail"))

# 7. Wrong r_debt magnitude → check4 (D = ‖r_debt‖²) fails
#    Change r_debt_vec to a vector whose norm ≠ cert_debt_sq=25/4
c = base(); c["r_debt_vector"] = ["1", "0", "0", "0"]  # ‖[1,0,0,0]‖² = 1 ≠ 25/4
results.append(test(
    "wrong r_debt magnitude (check4: ‖r_debt‖² = 1 but D stored = 25/4)",
    c, "fail"))

# 8. Wrong debt_norm_squared → check4 fails
c = base(); c["debt_norm_squared"] = "99/1"  # correct is 25/4; ‖r_debt‖²=25/4 ≠ 99
results.append(test(
    "wrong debt_norm_squared (check4: stored D = 99 but ‖r_debt‖² = 25/4)",
    c, "fail"))

# 9. Flipped is_cocycle flag → check5 fails
c = base(); c["is_cocycle"] = False          # correct is True
results.append(test(
    "flipped is_cocycle flag (check5 fails)",
    c, "fail"))

# 10. Wrong verdict → check6 fails
c = base(); c["case"] = "globally_admissible"  # but D=25/4 ≠ 0
results.append(test(
    "wrong verdict (check6: GLOBALLY_ADMISSIBLE but D ≠ 0)",
    c, "fail"))

# 11. Original certificate unmodified — must still pass
results.append(test(
    "original certificate unmodified (all five checks hold)",
    base(), "pass"))

# 12. DOCUMENTED GAP: wrong r_debt direction but correct norm
#     Vector [5/2, 0, 0, 0] has ‖v‖² = 25/4 = D, so check4 PASSES.
#     check3 (r_debt = G⁻¹p·h) is not yet in the Rocq verify.
#     This test documents the open formalization item.
c = base()
c["r_debt_vector"]      = ["5/2", "0", "0", "0"]   # wrong direction, right norm
c["debt_norm_squared"]  = "25/4"                     # consistent with this r_debt
results.append(test(
    "wrong r_debt direction, correct norm → check4 passes (check3 gap)",
    c, "pass"))

print()
n_pass = sum(results)
n_total = len(results)
print(f"{n_pass}/{n_total} tests passed")
if n_pass < n_total:
    print("\nNote: test 12 documenting the check3 gap should show 'pass' (expected).")
print()
sys.exit(0 if n_pass == n_total else 1)
