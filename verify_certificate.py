"""
Independent certificate verifier.

Loads certificates/finite_nerve_warrant_debt_certificate.json and verifies
the actual-object entry from scratch using only the certificate data.

No trust in the engine scripts is required. The verification uses only:
  - exact rational arithmetic (sympy)
  - the certificate JSON fields: L1_matrix, harmonic_basis_vectors, residue,
    p_periods, r_debt_vector, debt_norm_squared, case

Steps (following VERIFY.md):
  1. Load L1, h, r from the certificate.
  2. Verify L1 h = 0  (h is genuinely harmonic).
  3. Compute p = <h, r>  (obstruction period).
  4. Compute r_debt = (p / <h,h>) * h  (harmonic projection).
  5. Compute D = ||r_debt||^2  (debt magnitude).
  6. Compare p, r_debt, D against certificate values.
  7. Confirm case = "warrant_debt" iff D > 0.
"""

import sympy as sp
import json
import sys
from pathlib import Path


def verify_entry(entry):
    label = entry.get("label", "unlabelled")
    r_str = entry["residue"]
    n = len(r_str)

    L1 = sp.Matrix([[sp.Rational(v) for v in row]
                    for row in entry["L1_matrix"]])
    basis = [sp.Matrix([sp.Rational(v) for v in h])
             for h in entry["harmonic_basis_vectors"]]
    r = sp.Matrix([sp.Rational(v) for v in r_str])

    checks = {}

    # Step 2: L1 h = 0 for each basis vector
    for i, h in enumerate(basis):
        lh = L1 * h
        checks[f"L1_h{i}_is_zero"] = bool(lh == sp.zeros(n, 1))

    # Step 3: period vector p_i = <h_i, r>
    p_computed = [h.dot(r) for h in basis]
    p_cert = [sp.Rational(v) for v in entry["p_periods"]]
    checks["periods_match_certificate"] = (p_computed == p_cert)

    # Step 4+5: harmonic projection via Gram matrix
    # r_debt = sum_i c_i h_i  where c = G^{-1} p
    if basis:
        from sympy import zeros as szeros
        G = sp.Matrix([[basis[i].dot(basis[j]) for j in range(len(basis))]
                       for i in range(len(basis))])
        p_vec = sp.Matrix(p_computed)
        c = G.inv() * p_vec
        r_debt_computed = sp.zeros(n, 1)
        for i in range(len(basis)):
            r_debt_computed = r_debt_computed + c[i] * basis[i]
    else:
        r_debt_computed = sp.zeros(n, 1)

    r_debt_cert = sp.Matrix([sp.Rational(v) for v in entry["r_debt_vector"]])
    checks["r_debt_matches_certificate"] = bool(r_debt_computed == r_debt_cert)

    D_computed = r_debt_computed.dot(r_debt_computed)
    D_cert = sp.Rational(entry["debt_norm_squared"])
    checks["D_matches_certificate"] = bool(D_computed == D_cert)

    # Step 7: case consistency
    case = entry["case"]
    if not entry["is_cocycle"]:
        expected_case = "coherence_failure"
    elif D_computed == 0:
        expected_case = "globally_admissible"
    else:
        expected_case = "warrant_debt"
    checks["case_consistent"] = (case == expected_case)

    all_ok = all(checks.values())

    return {
        "label": label,
        "case": case,
        "p": [str(v) for v in p_computed],
        "D": str(D_computed),
        "all_checks_pass": all_ok,
        "checks": {k: ("PASS" if v else "FAIL") for k, v in checks.items()},
    }


def main():
    cert_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("certificates/finite_nerve_warrant_debt_certificate.json")
    if not cert_path.exists():
        print(f"Certificate not found: {cert_path}")
        sys.exit(1)

    cert = json.load(open(cert_path))
    entries = cert.get("results", [cert])

    print("=" * 60)
    print("INDEPENDENT CERTIFICATE VERIFICATION")
    print("=" * 60)
    print(f"Source: {cert_path}")
    print(f"Arithmetic: {entries[0].get('arithmetic', '?')}")
    print()

    all_ok = True
    for entry in entries:
        result = verify_entry(entry)
        label = result["label"][:55]
        status = "PASS" if result["all_checks_pass"] else "FAIL"
        if not result["all_checks_pass"]:
            all_ok = False
        print(f"  [{status}]  {label}")
        print(f"         case={result['case']}  p={result['p']}  D={result['D']}")
        if not result["all_checks_pass"]:
            for k, v in result["checks"].items():
                if v == "FAIL":
                    print(f"         FAILED CHECK: {k}")
    print()
    print(f"Overall: {'ALL VERIFIED' if all_ok else 'VERIFICATION FAILURES'}")

    # Detailed output for the warrant_debt case
    wdc = next((e for e in entries if e.get("case") == "warrant_debt"), None)
    if wdc:
        res = verify_entry(wdc)
        print()
        print("Detailed checks for warrant_debt entry:")
        for k, v in res["checks"].items():
            print(f"  {k:45} {v}")

    return all_ok


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
