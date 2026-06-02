"""
Complete Four-Cycle Classification Theorem and Integral/Modular Coefficient Theorem.

Theorem 1 (Complete four-cycle H^1 classifier).
  For the four-region loop nerve N with coboundary matrix delta^0, the circulation
  functional q(a,b,c,d) = -a-b-c+d is the complete invariant:
      [r] = 0  in H^1(N;Q)  iff  q(r) = 0.

Theorem 2 (Integral period).
  H^1(N;Z) is isomorphic to Z via q. The actual residue r = (1,1,1,-2) has
  integral period q(r) = -5, hence [r] = -5 in Z ~= H^1(N;Z).

Theorem 3 (Modular sensitivity).
  For any field k:
      [r] != 0  in H^1(N;k)  iff  char(k) does not divide 5.
  In particular [r] vanishes over F_5 and is nonzero over every other prime field.
"""

import json
import sys
import sympy as sp
from pathlib import Path


DELTA0 = sp.Matrix([
    [-1,  1,  0,  0],
    [ 0, -1,  1,  0],
    [ 0,  0, -1,  1],
    [-1,  0,  0,  1],
])

RESIDUE = sp.Matrix([1, 1, 1, -2])
CYCLE_Z = sp.Matrix([-1, -1, -1, 1])


def circulation(r):
    """q(a,b,c,d) = -a - b - c + d  (inner product with z = (-1,-1,-1,1))."""
    return CYCLE_Z.dot(r)


def coboundary_solution(r_vec):
    """
    Solve delta^0 b = r over Q. Returns the solution (with b[0]=0 gauge fix)
    if one exists, else None.
    """
    b = sp.symbols("b0 b1 b2 b3")
    B = sp.Matrix(b)
    eqs = list(DELTA0 * B - r_vec)
    sol = sp.solve(eqs, b, dict=True)
    if not sol:
        return None
    return {str(k): sol[0][k] for k in b if k in sol[0]}


# ---------------------------------------------------------------------------
# Theorem 1: Complete four-cycle classifier
# ---------------------------------------------------------------------------

def verify_complete_classifier():
    """
    Verify Theorem 1 for a sample of 100 random rational vectors:
      q(r) == 0  iff  r in im(delta^0).
    Also verify the constructive direction: given q(r)=0, the explicit solution
    b = (0, a, a+b, a+b+c) works.
    """
    import random
    random.seed(42)

    failures = []
    for _ in range(100):
        # Random rational 4-vector
        nums = [random.randint(-10, 10) for _ in range(4)]
        dens = [random.randint(1, 5) for _ in range(4)]
        r = sp.Matrix([sp.Rational(n, d) for n, d in zip(nums, dens)])

        q_val = circulation(r)
        sol = coboundary_solution(r)
        is_coboundary = sol is not None

        # Theorem: q(r) == 0  iff  coboundary
        expected_cobdy = (q_val == 0)
        if is_coboundary != expected_cobdy:
            failures.append({"r": [str(v) for v in r], "q": str(q_val),
                             "is_coboundary": is_coboundary})

        # Constructive direction: if q(r)=0, verify b = (0, a, a+b_coeff, a+b_coeff+c)
        if q_val == 0:
            a, b_coeff, c = r[0], r[1], r[2]
            b_explicit = sp.Matrix([0, a, a + b_coeff, a + b_coeff + c])
            residual = DELTA0 * b_explicit - r
            if residual != sp.zeros(4, 1):
                failures.append({"constructive_failure": [str(v) for v in r]})

    return {
        "theorem": "complete_four_cycle_classifier",
        "samples_tested": 100,
        "failures": failures,
        "passed": len(failures) == 0,
    }


# ---------------------------------------------------------------------------
# Theorem 2: Integral period
# ---------------------------------------------------------------------------

def verify_integral_period():
    """
    Verify H^1(N;Z) ~= Z via q, and q(r) = -5 for r = (1,1,1,-2).

    Proof strategy verified here:
      (a) q: Z^4 -> Z is surjective (q(0,0,0,1) = 1).
      (b) ker(q) = im(delta^0) over Z:
            if q(r)=0 then b = (0, a, a+r1, a+r1+r2) is an integer solution.
      (c) Therefore Z^4 / im(delta^0) ~= Z.
      (d) q(1,1,1,-2) = -5, so [r] = -5.
    """
    # (a) surjectivity witness
    e4 = sp.Matrix([0, 0, 0, 1])
    surj_value = circulation(e4)

    # (b) for several integer vectors with q=0, verify integer solution exists
    test_vectors = [
        sp.Matrix([1, 1, 1, 3]),    # q = -1-1-1+3 = 0
        sp.Matrix([2, -3, 5, 0]),   # q = -2+3-5+0 = -4  (not 0)
        sp.Matrix([0, 0, 0, 0]),    # q = 0
        sp.Matrix([3, -1, 2, 4]),   # q = -3+1-2+4 = 0
        sp.Matrix([1, 0, -1, 0]),   # q = -1+0+1+0 = 0
    ]
    kernel_exact_over_Z = True
    kernel_tests = []
    for r_vec in test_vectors:
        q_val = circulation(r_vec)
        if q_val == 0:
            a, b_c, c = r_vec[0], r_vec[1], r_vec[2]
            b_explicit = sp.Matrix([0, a, a + b_c, a + b_c + c])
            residual = DELTA0 * b_explicit - r_vec
            ok = (residual == sp.zeros(4, 1))
            d_val = r_vec[3]
            is_integer = (a + b_c + c == d_val)
            kernel_tests.append({
                "r": [str(v) for v in r_vec],
                "q": str(q_val),
                "b_explicit": [str(v) for v in b_explicit],
                "delta0_b_equals_r": bool(ok),
                "d_equals_a_plus_b_plus_c": bool(is_integer),
            })
            if not ok:
                kernel_exact_over_Z = False

    # (c) actual period
    q_r = circulation(RESIDUE)

    return {
        "theorem": "integral_period",
        "surjectivity_witness": {"e4": [0, 0, 0, 1], "q_e4": str(surj_value)},
        "kernel_equals_image_over_Z": kernel_exact_over_Z,
        "kernel_tests": kernel_tests,
        "integral_period": str(q_r),
        "H1_Z_iso": "Z",
        "class_in_H1_Z": str(q_r),
        "passed": (surj_value == 1 and kernel_exact_over_Z and q_r == -5),
    }


# ---------------------------------------------------------------------------
# Theorem 3: Modular sensitivity
# ---------------------------------------------------------------------------

def verify_modular(p):
    """
    Over F_p, check whether -5 ≡ 0 (mod p).
    If p=5: verify explicitly that b = (0,1,2,3) solves delta^0 b = r mod 5.
    Otherwise: verify that no solution exists by checking the circulation mod p.
    """
    period_mod_p = (-5) % p
    vanishes = (period_mod_p == 0)

    detail = {}
    if vanishes:
        # Construct the coboundary solution mod p
        b_mod = [0, 1 % p, 2 % p, 3 % p]  # (0, a, a+1, a+1+1) with a=1
        # General formula: b = (0, r0, r0+r1, r0+r1+r2) mod p
        r_mod = [int(v) % p for v in [1, 1, 1, -2]]
        a, b_c, c = r_mod[0], r_mod[1], r_mod[2]
        b_explicit = [0, a % p, (a + b_c) % p, (a + b_c + c) % p]
        # Verify delta^0 b ≡ r mod p
        checks = []
        diffs = [
            (b_explicit[1] - b_explicit[0]) % p,
            (b_explicit[2] - b_explicit[1]) % p,
            (b_explicit[3] - b_explicit[2]) % p,
            (b_explicit[3] - b_explicit[0]) % p,
        ]
        for i, (diff, ri) in enumerate(zip(diffs, r_mod)):
            checks.append({"edge_index": i, "diff_mod_p": diff, "r_mod_p": ri,
                           "matches": diff == ri})
        detail["coboundary_certificate_mod_p"] = {
            "b": b_explicit,
            "edge_checks": checks,
            "verified": all(c["matches"] for c in checks),
        }
    else:
        # No solution: circulation is nonzero mod p
        # Any solution would require q(b) = 0 but pairing gives -5 != 0 mod p
        detail["circulation_mod_p"] = period_mod_p

    return {
        "p": p,
        "period_mod_p": period_mod_p,
        "class_vanishes": vanishes,
        "detail": detail,
    }


def verify_modular_sensitivity():
    """
    Check the modular sensitivity theorem for the first several primes.
    """
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    results = [verify_modular(p) for p in primes]
    # Theorem: vanishes iff p | 5 iff p == 5
    theorem_holds = all(
        (r["class_vanishes"] == (r["p"] == 5)) for r in results
    )
    return {
        "theorem": "modular_sensitivity",
        "residue": [1, 1, 1, -2],
        "integral_period": -5,
        "prime_results": results,
        "theorem_holds_for_tested_primes": theorem_holds,
        "passed": theorem_holds,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def print_report(t1, t2, t3):
    print("=" * 72)
    print("CLASSIFICATION THEOREM AND INTEGRAL/MODULAR COEFFICIENT VERIFICATION")
    print("=" * 72)
    print()
    print("Theorem 1: Complete four-cycle H^1 classifier")
    print(f"  q(a,b,c,d) = -a-b-c+d is the complete invariant over Q.")
    print(f"  Samples tested: {t1['samples_tested']}   Failures: {len(t1['failures'])}")
    print(f"  Result: {'PASS' if t1['passed'] else 'FAIL'}")
    print()
    print("Theorem 2: Integral period")
    print(f"  H^1(N;Z) ~= Z via q.  Period of actual residue: q(1,1,1,-2) = {t2['integral_period']}")
    print(f"  Surjectivity witness: q(0,0,0,1) = {t2['surjectivity_witness']['q_e4']}")
    print(f"  ker(q) = im(delta^0) over Z: {t2['kernel_equals_image_over_Z']}")
    print(f"  Result: {'PASS' if t2['passed'] else 'FAIL'}")
    print()
    print("Theorem 3: Modular sensitivity   [r] != 0 in H^1(N;k) iff char(k) does not divide 5")
    print(f"  {'p':>4}  {'period mod p':>14}  {'class vanishes':>15}  {'expected':>10}")
    for r in t3["prime_results"]:
        expected = (r["p"] == 5)
        print(f"  {r['p']:>4}  {r['period_mod_p']:>14}  {str(r['class_vanishes']):>15}  "
              f"  {str(expected):>9}")
    print(f"  Theorem holds for all tested primes: {t3['theorem_holds_for_tested_primes']}")
    print(f"  Result: {'PASS' if t3['passed'] else 'FAIL'}")
    print()
    all_pass = t1["passed"] and t2["passed"] and t3["passed"]
    print(f"Overall: {'ALL PASS' if all_pass else 'FAILURES PRESENT'}")


if __name__ == "__main__":
    t1 = verify_complete_classifier()
    t2 = verify_integral_period()
    t3 = verify_modular_sensitivity()

    print_report(t1, t2, t3)

    cert = {
        "script": "classification_theorem.py",
        "base_object": "actual_gluing_object_v1",
        "residue": [1, 1, 1, -2],
        "cycle_witness": [-1, -1, -1, 1],
        "theorem_1_complete_classifier": t1,
        "theorem_2_integral_period": t2,
        "theorem_3_modular_sensitivity": t3,
    }

    out = Path("certificates") / "classification_theorem_certificate.json"
    out.write_text(json.dumps(cert, indent=2))
    print(f"\nCertificate saved to: {out}")

    all_pass = t1["passed"] and t2["passed"] and t3["passed"]
    sys.exit(0 if all_pass else 1)
