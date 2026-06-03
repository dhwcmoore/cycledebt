#!/usr/bin/env python3
"""
CycleDebt — certificate-producing diagnostic tool for cyclic systems.

Detects when local monitoring data is coherent but insufficient to warrant
a global diagnostic claim, and produces an independently checkable
obstruction certificate showing exactly what refinement is needed.

Three possible verdicts:
  WARRANT DEBT        — local data coherent; cyclic obstruction blocks the claim
  GLOBALLY ADMISSIBLE — no obstruction; claim is warranted
  COHERENCE FAILURE   — local data is self-contradictory; H^1 question does not arise

The independent verifier reads only from the certificate JSON on disk.
It does not call any engine function.  It checks from first principles:
  (1) L1 h = 0            (each stored basis vector is genuinely harmonic)
  (2) p = <h, r>          (periods match the stored claim)
  (3) r_debt = G^{-1}p h  (harmonic projection is correctly stored)
  (4) D = ||r_debt||²     (debt magnitude is correctly stored)
  (5) D1 r = 0 iff is_cocycle (cocycle condition matches stored flag)
  (6) case is consistent   (verdict follows from D and cocycle flag)

Usage:
    python scripts/cyclediagnostic_demo.py examples/cps_loop_fault.json
    python scripts/cyclediagnostic_demo.py examples/cps_loop_refined_sensor.json
    python scripts/cyclediagnostic_demo.py examples/cps_loop_coherence_failure.json
"""

import json
import sys
import sympy as sp
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from residue_test import classify_residue, build_matrices
from finite_nerve_warrant_debt import (
    hodge_laplacian_1,
    harmonic_basis_1,
    gram_matrix as _gram_matrix,
    period_vector,
    debt_magnitude,
    harmonic_project,
)


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def resolve_path(path_str: str) -> Path:
    p = Path(path_str)
    if p.is_absolute() or p.exists():
        return p
    return REPO_ROOT / path_str


def load_model(path_str: str) -> dict:
    with open(resolve_path(path_str)) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Analysis pipeline  (engine — produces certificate data)
# ---------------------------------------------------------------------------

def analyse(obj: dict) -> dict:
    regions = obj["regions"]
    edges   = [list(e) for e in obj["edges"]]
    faces   = [list(f) for f in obj.get("faces", [])]
    etup    = [tuple(e) for e in edges]

    residue_dict = obj.get("residue", {})
    residue = []
    for e in edges:
        key = f"{e[0]}-{e[1]}"
        alt = f"{e[1]}-{e[0]}"
        val = residue_dict.get(key, residue_dict.get(alt, "0"))
        residue.append(sp.Rational(str(val)))

    base = classify_residue(regions, etup, faces, residue)

    D0, D1 = build_matrices(regions, etup, faces)
    L1     = hodge_laplacian_1(D0, D1)
    basis  = harmonic_basis_1(D0, D1)
    G      = _gram_matrix(basis)
    p      = period_vector(residue, basis)
    D      = debt_magnitude(p, G)
    r_debt = harmonic_project(residue, basis)
    D_chk  = r_debt.dot(r_debt)

    if not base["is_cocycle"]:
        case = "coherence_failure"
    elif base["is_coboundary"]:
        case = "globally_admissible"
    else:
        case = "warrant_debt"

    # Refinement suggestions — computed here so they appear in the certificate too
    suggested_refinement = None
    if case == "warrant_debt":
        r_vec        = sp.Matrix(residue)
        delta_min    = -r_debt          # subtract the harmonic debt component
        r_admissible = r_vec + delta_min

        ref = {
            "option_1_minimal_correction": {
                "description": "subtract harmonic debt; adjusts all interfaces proportionally",
                "delta_r":     [str(v) for v in delta_min],
                "new_residue": [str(v) for v in r_admissible],
            },
        }

        if len(basis) == 1:             # single-cycle case: one-edge fixes are tractable
            z_vec = basis[0]
            p_val = p[0]
            fixes = []
            for k in range(len(residue)):
                if z_vec[k] != 0:
                    delta_k = -p_val / z_vec[k]
                    fixes.append({
                        "edge":       f"{etup[k][0]}-{etup[k][1]}",
                        "from_r":     str(residue[k]),
                        "delta":      str(delta_k),
                        "to_r":       str(residue[k] + delta_k),
                        "_sort_key":  (abs(delta_k), 0 if delta_k > 0 else 1),
                    })
            fixes.sort(key=lambda f: f["_sort_key"])
            for f in fixes:
                del f["_sort_key"]
            ref["option_2_single_interface_fixes"] = fixes

        suggested_refinement = ref

    return {
        "arithmetic":             "exact rational (sympy Q)",
        "case":                   case,
        "is_cocycle":             base["is_cocycle"],
        "is_admissible":          base["is_coboundary"],
        "dim_H1":                 len(basis),
        "residue":                [str(v) for v in residue],
        "edges":                  [f"{e[0]}-{e[1]}" for e in etup],
        # Matrices stored for independent verification
        "L1_matrix":              [[str(L1[i, j]) for j in range(L1.shape[1])]
                                   for i in range(L1.shape[0])],
        "D1_matrix":              [[str(D1[i, j]) for j in range(D1.shape[1])]
                                   for i in range(D1.shape[0])],
        "harmonic_basis_vectors": [[str(v) for v in h] for h in basis],
        "G":                      [[str(G[i, j]) for j in range(G.shape[1])]
                                   for i in range(G.shape[0])] if basis else [],
        "p_periods":              [str(v) for v in p],
        "r_debt_vector":          [str(v) for v in r_debt],
        "debt_norm_squared":      str(D),
        "gram_harmonic_agree":    bool(D == D_chk),
        "suggested_refinement":   suggested_refinement,
        # Private — stripped from certificate
        "_cocycle_witness":       base.get("witness", {}),
    }


# ---------------------------------------------------------------------------
# Certificate writer
# ---------------------------------------------------------------------------

VERDICTS = {
    "coherence_failure":   "LOCAL DATA SELF-CONTRADICTORY",
    "globally_admissible": "GLOBALLY ADMISSIBLE",
    "warrant_debt":        "WARRANT DEBT",
}


def write_certificate(obj: dict, result: dict, cert_path: Path) -> None:
    cert = {
        "tool":    "CycleDebt",
        "version": "1.0",
        "system_name":      obj.get("system_name", obj.get("name")),
        "diagnostic_claim": obj.get("diagnostic_claim", {}),
        "verdict":          VERDICTS[result["case"]],
        **{k: v for k, v in result.items() if not k.startswith("_")},
    }
    cert_path.parent.mkdir(parents=True, exist_ok=True)
    cert_path.write_text(json.dumps(cert, indent=2))


# ---------------------------------------------------------------------------
# Independent verifier  (reads only from the certificate file on disk)
#
# No engine functions are called here.  Every check is re-derived from
# the matrix and vector data stored in the JSON certificate.
# ---------------------------------------------------------------------------

def verify_from_file(cert_path: Path) -> tuple:
    cert = json.loads(cert_path.read_text())

    n     = len(cert["residue"])
    L1    = sp.Matrix([[sp.Rational(v) for v in row]
                       for row in cert["L1_matrix"]])
    D1    = sp.Matrix([[sp.Rational(v) for v in row]
                       for row in cert["D1_matrix"]]) if cert["D1_matrix"] else sp.zeros(0, n)
    basis = [sp.Matrix([sp.Rational(v) for v in h])
             for h in cert["harmonic_basis_vectors"]]
    r     = sp.Matrix([sp.Rational(v) for v in cert["residue"]])

    checks = {}

    # (1) Each stored harmonic basis vector lies in ker(L1)
    for i, h in enumerate(basis):
        checks[f"L1_h{i}_in_ker_L1"] = bool(L1 * h == sp.zeros(n, 1))

    # (2) Obstruction periods match stored values
    p_recomputed = [h.dot(r) for h in basis]
    p_stored     = [sp.Rational(v) for v in cert["p_periods"]]
    checks["periods_match_stored"] = (p_recomputed == p_stored)

    # (3) r_debt is correctly computed as the Gram projection
    if basis:
        Gm = sp.Matrix([[basis[i].dot(basis[j]) for j in range(len(basis))]
                        for i in range(len(basis))])
        c  = Gm.inv() * sp.Matrix(p_recomputed)
        r_debt_recomputed = sp.zeros(n, 1)
        for i in range(len(basis)):
            r_debt_recomputed += c[i] * basis[i]
    else:
        r_debt_recomputed = sp.zeros(n, 1)

    r_debt_stored = sp.Matrix([sp.Rational(v) for v in cert["r_debt_vector"]])
    checks["r_debt_matches_stored"] = bool(r_debt_recomputed == r_debt_stored)

    # (4) Debt magnitude D = ||r_debt||²
    D_recomputed = r_debt_recomputed.dot(r_debt_recomputed)
    D_stored     = sp.Rational(cert["debt_norm_squared"])
    checks["D_matches_stored"] = bool(D_recomputed == D_stored)

    # (5) Cocycle condition: D1 r = 0  iff  is_cocycle
    if D1.shape[0] > 0:
        delta1_r = D1 * r
        is_cocycle_recomputed = all(x == 0 for x in delta1_r)
    else:
        is_cocycle_recomputed = True  # no faces → cocycle condition vacuous
    checks["cocycle_flag_matches_D1_r"] = (is_cocycle_recomputed == cert["is_cocycle"])

    # (6) Verdict is consistent with re-derived D and cocycle flag
    if not is_cocycle_recomputed:
        expected_case = "coherence_failure"
    elif D_recomputed == 0:
        expected_case = "globally_admissible"
    else:
        expected_case = "warrant_debt"
    checks["verdict_case_consistent"] = (cert["case"] == expected_case)

    return all(checks.values()), checks


# ---------------------------------------------------------------------------
# Report printer
# ---------------------------------------------------------------------------

SEP = "─" * 60


def print_report(obj: dict, result: dict, cert_rel: str,
                 verify_ok: bool, checks: dict) -> None:
    system_name = obj.get("system_name", obj.get("name", "unnamed"))
    claim_stmt  = obj.get("diagnostic_claim", {}).get("statement", "(none)")

    print()
    print(SEP)
    print("CycleDebt Diagnostic Report")
    print(SEP)
    print()
    print(f"System: {system_name}")
    print(f"Claim:  {claim_stmt}")
    print()

    case = result["case"]

    if case == "coherence_failure":
        print("Verdict: COHERENCE FAILURE")
        print()
        print("Reason:")
        print("  The local diagnostic residues are mutually inconsistent.")
        print("  The cocycle condition (delta^1 r = 0) is violated.")
        print("  The H^1 admissibility question does not arise.")
        delta1 = result["_cocycle_witness"].get("delta1_r", {})
        if delta1:
            print()
            print("  Inconsistent triple overlaps:")
            for face_str, val in delta1.items():
                print(f"    {face_str}:  delta^1 r = {val}")
        print()
        print("  Interpretation:")
        print("  The pairwise sensor readings cannot all be simultaneously correct.")
        print("  Check sensor calibration before proceeding to fault attribution.")

    elif case == "globally_admissible":
        print("Verdict: GLOBALLY ADMISSIBLE")
        print()
        obs = obj.get("observation_note", "")
        if obs:
            print(obs)
        print("The obstruction vanishes.")
        print("The diagnostic claim is now warranted.")
        print()
        if result["p_periods"]:
            print(f"  Obstruction period: <z, r> = {result['p_periods'][0]}")
        print(f"  Debt magnitude D = {result['debt_norm_squared']}")

    else:  # warrant_debt
        print("Verdict: WARRANT DEBT")
        print()
        print("Reason:")
        print("  The local diagnostic residues are coherent.")
        print("  However, the diagnostic claim does not factor through the observation map.")
        print("  A non-zero cyclic obstruction remains.")
        print()
        if result["harmonic_basis_vectors"]:
            h      = result["harmonic_basis_vectors"][0]
            r_vals = result["residue"]
            p      = result["p_periods"][0] if result["p_periods"] else "0"
            D      = result["debt_norm_squared"]
            print("  Exact witness:")
            print(f"    cycle z = ({', '.join(h)})")
            print(f"    residue r = ({', '.join(r_vals)})")
            print(f"    period <z,r> = {p}")
            print(f"    debt magnitude D = {D}")

        ref = result.get("suggested_refinement")
        if ref:
            print()
            print("  Suggested refinements:")
            opt1 = ref["option_1_minimal_correction"]
            print(f"    Option 1 — {opt1['description']}:")
            print(f"      delta_r = ({', '.join(opt1['delta_r'])})")
            print(f"      new r'  = ({', '.join(opt1['new_residue'])})")
            fixes = ref.get("option_2_single_interface_fixes", [])
            if fixes:
                best     = fixes[0]
                n_others = len(fixes) - 1
                print()
                print("    Option 2 — single-interface fix:")
                print(f"      {best['edge']}:  {best['from_r']}  →  {best['to_r']}  (delta = {best['delta']})")
                if n_others:
                    print(f"      [{n_others} other cycle edge(s) have identical correction cost]")

    print()
    print(f"Certificate:")
    print(f"  {cert_rel}")
    print()
    v_str = "PASS" if verify_ok else "FAIL"
    print(f"Independent verification:")
    print(f"  {v_str}")
    if not verify_ok:
        for k, v in checks.items():
            if not v:
                print(f"  FAILED CHECK: {k}")
    print()
    print(SEP)
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/cyclediagnostic_demo.py <model.json>")
        print()
        print("Examples:")
        print("  python scripts/cyclediagnostic_demo.py examples/cps_loop_fault.json")
        print("  python scripts/cyclediagnostic_demo.py examples/cps_loop_refined_sensor.json")
        print("  python scripts/cyclediagnostic_demo.py examples/cps_loop_coherence_failure.json")
        sys.exit(1)

    path_str = sys.argv[1]
    obj      = load_model(path_str)
    result   = analyse(obj)

    stem      = Path(path_str).stem
    cert_path = REPO_ROOT / "certificates" / f"{stem}_certificate.json"
    cert_rel  = f"certificates/{stem}_certificate.json"

    # Write certificate first, then verify from the file — verifier reads
    # only from disk and calls no engine function.
    write_certificate(obj, result, cert_path)
    verify_ok, checks = verify_from_file(cert_path)

    print_report(obj, result, cert_rel, verify_ok, checks)


if __name__ == "__main__":
    main()
