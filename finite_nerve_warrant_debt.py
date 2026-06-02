"""
Finite Nerve Warrant Debt Engine — General JSON-Driven Pipeline.

This is the general obstruction engine. It takes any finite regional nerve
(graph or simplicial complex) via JSON input and computes the full warrant
debt pipeline using the Hodge Laplacian.

Theorem (Finite Graph Period Classification):
  Let G be a finite connected oriented graph over Q. For r in C^1(G; Q), TFAE:
    (1) Gauge-admissible:    exists b in C^0 with delta^0 b = r.
    (2) Globally consistent: exists Phi with Phi_j - Phi_i = r_ij.
    (3) Cycle pairings zero: <z, r> = 0 for every z in Z_1(G; Q).
    (4) Cohomologically zero: [r] = 0 in H^1(G; Q).

  Proof:
    (1) <=> (4): definition of H^1 = C^1 / im(delta^0).
    (1) <=> (2): the bridge theorem (see PROOF.md §11b).
    (1) => (3): r = delta^0 b => <z, r> = <(delta^0)^T z, b> = 0.
    (3) => (1): dim Z_1 = |E| - |V| + 1 (Euler, connected).
                dim im(delta^0) = |V| - 1 (rank of coboundary).
                Sum = |E| = dim C^1.
                Since im(delta^0) subset Z_1^perp (by (1)=>(3)) and both
                subspaces have complementary dimensions, im(delta^0) = Z_1^perp.
                So r perp Z_1 implies r in im(delta^0). QED.

  Corollary (Four-cycle): Z_1 = span(z), z = (-1,-1,-1,1).
    [r] = 0  iff  <z,r> = 0  iff  -a-b-c+d = 0.
    Actual object q(r) = -5 != 0, so [r] != 0.

Nerve Extension (simplicial complex with faces):
  H^1(N; Q) = ker(delta^1) / im(delta^0).
  The harmonic 1-cochains are ker(L_1) where L_1 = D0*D0^T + D1^T*D1.
  For r in ker(delta^1): [r] = 0  iff  <h, r> = 0 for all h in ker(L_1).
  Proof: same Hodge dimension argument. ker(L_1) represents H^1 harmonically.

  For graphs (no faces): D1 = 0, L_1 = D0*D0^T, ker(L_1) = ker(D0^T) = Z_1. Consistent.

General Debt Formula:
  Let {h_1, ..., h_k} be a basis for ker(L_1). Define:
    G_ij = <h_i, h_j>      (Gram matrix)
    p_i(r) = <h_i, r>      (harmonic period vector)
    D(r) = p^T G^{-1} p    (warrant debt magnitude)

  Special cases:
    k = 1 (four-cycle): D = p^2 / ||z||^2 = p^2 / 4.
    Orthogonal basis:   D = sum_i p_i^2 / ||h_i||^2.
    General:            D = p^T G^{-1} p.

Usage:
    python finite_nerve_warrant_debt.py  [--json FILE]
    python finite_nerve_warrant_debt.py  (runs built-in test cases)
"""

import sympy as sp
import json
import sys
from pathlib import Path
from residue_test import classify_residue, build_matrices
from admissibility_bridge import gram_schmidt


# ---------------------------------------------------------------------------
# Hodge machinery
# ---------------------------------------------------------------------------

def hodge_laplacian_1(D0, D1):
    """L_1 = D0 D0^T + D1^T D1  (Hodge Laplacian on 1-cochains)."""
    return D0 * D0.T + D1.T * D1


def harmonic_basis_1(D0, D1):
    """Basis for ker(L_1) = harmonic 1-cochains representing H^1."""
    L1 = hodge_laplacian_1(D0, D1)
    return L1.nullspace()


def gram_matrix(basis):
    """G_ij = <h_i, h_j>. Sympy Matrix."""
    k = len(basis)
    if k == 0:
        return sp.zeros(0, 0)
    G = sp.zeros(k, k)
    for i, hi in enumerate(basis):
        for j, hj in enumerate(basis):
            G[i, j] = hi.dot(hj)
    return G


def period_vector(r_vals, basis):
    """p_i = <h_i, r>. Sympy column vector."""
    if not basis:
        return sp.zeros(0, 1)
    r = sp.Matrix([sp.Rational(v) for v in r_vals])
    return sp.Matrix([h.dot(r) for h in basis])


def debt_magnitude(p, G):
    """D = p^T G^{-1} p."""
    if G.shape == (0, 0):
        return sp.Integer(0)
    return (p.T * G.inv() * p)[0, 0]


def harmonic_project(r_vals, basis):
    """Project r onto span(basis) via Gram-Schmidt. Returns r_debt vector."""
    if not basis:
        return sp.zeros(len(r_vals), 1)
    r = sp.Matrix([sp.Rational(v) for v in r_vals])
    ortho = gram_schmidt(basis)
    proj = sp.zeros(len(r_vals), 1)
    for h in ortho:
        proj += h.dot(r) / h.dot(h) * h
    return proj


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def analyse(regions, edges, faces, residue, label=""):
    """
    Full warrant debt analysis for any finite nerve.
    Returns a certificate dict.
    """
    etup = [tuple(e) for e in edges]
    D0, D1 = build_matrices(regions, etup, faces)
    r_rat = [sp.Rational(v) for v in residue]

    # Classification (cocycle / coboundary)
    base = classify_residue(regions, etup, faces, residue)

    # Hodge basis and Gram matrix
    basis = harmonic_basis_1(D0, D1)
    G = gram_matrix(basis)
    p = period_vector(residue, basis)
    D = debt_magnitude(p, G)

    # Cross-check: harmonic projection
    r_debt = harmonic_project(residue, basis)
    D_check = r_debt.dot(r_debt)
    agree = bool(D == D_check)

    # Certificate soundness: determine which theorem case applies
    if not base["is_cocycle"]:
        case = "coherence_failure"
        theorem = (
            "delta^1 r != 0: local coherence fails. "
            "The H^1 admissibility question does not arise. "
            "[PROOF.md §0b]"
        )
    elif base["is_coboundary"]:
        case = "globally_admissible"
        theorem = (
            "[r] = 0 in H^1(N;Q): D(r) = ||P_{H^1} r||^2 = 0. "
            "A global consistent claim Phi exists. "
            "[PROOF.md §0b + §11b]"
        )
    else:
        case = "warrant_debt"
        theorem = (
            "[r] != 0 in H^1(N;Q): D(r) = ||P_{H^1} r||^2 > 0. "
            "No global consistent claim exists. "
            "[PROOF.md §0b + §11b]"
        )

    return {
        "label": label,
        "residue": [str(sp.Rational(v)) for v in residue],
        "dim_H1": len(basis),
        "is_cocycle": base["is_cocycle"],
        "is_admissible": base["is_coboundary"],
        "case": case,
        "theorem_invoked": theorem,
        "basis_type": (
            "harmonic ker(L_1) = ker((delta^0)^T) cap ker(delta^1) via Hodge Laplacian"
        ),
        "G": [[str(G[i, j]) for j in range(G.shape[1])]
              for i in range(G.shape[0])],
        "p": [str(v) for v in p],
        "D_gram": str(D),
        "D_harmonic_check": str(D_check),
        "gram_harmonic_agree": agree,
    }


def analyse_json(path):
    """Load a JSON file and run full analysis."""
    with open(path) as f:
        obj = json.load(f)
    regions = obj["regions"]
    edges   = [list(e) for e in obj["edges"]]
    faces   = [list(f) for f in obj.get("faces", [])]
    residue_dict = obj.get("residue", {})
    residue = []
    for e in edges:
        key = f"{e[0]}-{e[1]}"
        val = residue_dict.get(key, residue_dict.get(f"{e[1]}-{e[0]}", "0"))
        residue.append(sp.Rational(str(val)))
    return analyse(regions, edges, faces, residue, label=obj.get("name", path))


# ---------------------------------------------------------------------------
# Built-in test cases
# ---------------------------------------------------------------------------

TEST_CASES = [
    # Graphs (no faces) — should match general_warrant_debt.py results
    {
        "label": "four_cycle  [graph, H1=Q, D=25/4]",
        "regions": ["U1","U2","U3","U4"],
        "edges":   [["U1","U2"],["U2","U3"],["U3","U4"],["U1","U4"]],
        "faces":   [],
        "residue": [1, 1, 1, -2],
        "expected_D": "25/4",
    },
    {
        "label": "four_cycle admissible  [graph, H1=Q, D=0]",
        "regions": ["U1","U2","U3","U4"],
        "edges":   [["U1","U2"],["U2","U3"],["U3","U4"],["U1","U4"]],
        "faces":   [],
        "residue": [1, 1, 1, 3],
        "expected_D": "0",
    },
    {
        "label": "diamond  [graph, H1=Q^2, D=51/8]",
        "regions": ["A","B","C","D"],
        "edges":   [["A","B"],["B","C"],["C","D"],["A","D"],["A","C"]],
        "faces":   [],
        "residue": [1, 1, 1, -2, 0],
        "expected_D": "51/8",
    },
    {
        "label": "complete K4  [graph, H1=Q^3, D=13]",
        "regions": ["A","B","C","D"],
        "edges":   [["A","B"],["A","C"],["A","D"],["B","C"],["B","D"],["C","D"]],
        "faces":   [],
        "residue": [1, 1, 1, 1, 1, -5],
        "expected_D": "13",
    },
    # Nerves (with faces)
    {
        "label": "filled triangle  [nerve, H1=0, D=0 for cocycle]",
        "regions": ["A","B","C"],
        "edges":   [["A","B"],["B","C"],["A","C"]],
        "faces":   [["A","B","C"]],
        "residue": [1, 2, 3],       # cocycle: 2-3+1=0 ✓
        "expected_D": "0",
    },
    {
        "label": "filled triangle incoherent  [coherence_failure]",
        "regions": ["A","B","C"],
        "edges":   [["A","B"],["B","C"],["A","C"]],
        "faces":   [["A","B","C"]],
        "residue": [1, 1, 1],           # NOT a cocycle: 1-1+1=1 != 0
        "expected_D": "0",              # D=0 because harmonic space is empty (H1=0)
    },
    {
        "label": "four_cycle minus one face  [nerve, H1=0]",
        # Four-cycle with the triangle A-B-D filled (adds edge A-D already present)
        # Use a simpler example: 3-cycle with filled face, then extra edge
        # Actually: use the filled triangle (3 vertices, 3 edges, 1 face) + extra vertex
        "regions": ["A","B","C","D"],
        "edges":   [["A","B"],["B","C"],["A","C"],["C","D"]],
        "faces":   [["A","B","C"]],
        # r must be a cocycle: r[BC] - r[AC] + r[AB] = 0 => r[1]-r[2]+r[0]=0
        "residue": [1, 2, 3, 1],    # face: 2-3+1=0 ✓; C→D: free
        "expected_D": "0",          # H1=0 so D=0 for any cocycle
    },
]


def print_report(results):
    print("=" * 72)
    print("FINITE NERVE WARRANT DEBT ENGINE — GENERAL PIPELINE")
    print("=" * 72)
    print()
    print("Theorem: D(r) = ||P_{H^1} r||^2 = p^T G^{-1} p")
    print("Basis:   harmonic ker(L_1) = ker((delta^0)^T) cap ker(delta^1)")
    print("Caution: D_gram correct only with this harmonic basis; raw graph cycles")
    print("         give wrong D for nerves with faces (see PROOF.md §0c).")
    print()
    hdr = f"  {'Case':<42} {'H1':>4} {'D':>8} {'cert-case':>18} {'chk':>5}"
    print(hdr)
    print("  " + "-" * 72)
    all_ok = True
    for res in results:
        exp = res.get("expected_D")
        d_ok = (exp is None) or (str(sp.sympify(res["D_gram"])) == str(sp.sympify(exp)))
        if not d_ok:
            all_ok = False
        chk = "OK" if d_ok else "FAIL"
        label = res["label"][:41]
        ccase = res.get("case", "?")[:17]
        print(f"  {label:<42} {res['dim_H1']:>4} {res['D_gram']:>8} {ccase:>18} {chk:>5}")
    print()
    print(f"  {'Gram==Harmonic for all':50} "
          f"{'ALL OK' if all(r['gram_harmonic_agree'] for r in results) else 'FAIL'}")
    print(f"  {'Expected D matched':50} "
          f"{'ALL OK' if all_ok else 'FAIL'}")
    print()
    # Show soundness breakdown
    cases = {"coherence_failure": 0, "globally_admissible": 0, "warrant_debt": 0}
    for r in results:
        cases[r.get("case", "?")] = cases.get(r.get("case", "?"), 0) + 1
    print("  Certificate soundness (three-case breakdown):")
    print(f"    coherence_failure:   {cases['coherence_failure']}  "
          f"(delta^1 r != 0; H^1 question does not arise)")
    print(f"    globally_admissible: {cases['globally_admissible']}  "
          f"([r]=0; D=0; global claim exists)")
    print(f"    warrant_debt:        {cases['warrant_debt']}  "
          f"([r]!=0; D>0; no global claim)")
    print()
    # Show actual object
    act = next((r for r in results if "four_cycle" in r["label"] and "25/4" in r["label"]), None)
    if act:
        print(f"  Actual object:  G={act['G']}  p={act['p']}  D={act['D_gram']}")
        print(f"  Four-cycle formula: D = p^2/4 = {act['p'][0]}^2/4 = "
              f"{sp.Rational(act['p'][0])**2/4}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        path = sys.argv[2]
        res = analyse_json(path)
        print(json.dumps(res, indent=2))
        cert_out = Path("certificates") / (Path(path).stem + "_nerve_warrant_debt.json")
        cert_out.write_text(json.dumps(res, indent=2))
        print(f"\nCertificate: {cert_out}")
        sys.exit(0)

    # Built-in test suite
    results = []
    for tc in TEST_CASES:
        res = analyse(tc["regions"], tc["edges"], tc["faces"], tc["residue"],
                      label=tc["label"])
        res["expected_D"] = tc.get("expected_D")
        results.append(res)

    print_report(results)

    # Also run on actual object JSON
    actual_json = Path("actual/actual_gluing_object_v1.json")
    if actual_json.exists():
        res_actual = analyse_json(str(actual_json))
        print(f"  JSON input (actual object):  D = {res_actual['D_gram']}  "
              f"H1 dim = {res_actual['dim_H1']}  admissible = {res_actual['is_admissible']}")
        print()

    all_ok = all(
        (tc.get("expected_D") is None) or
        (str(sp.sympify(r["D_gram"])) == str(sp.sympify(tc["expected_D"])))
        for r, tc in zip(results, TEST_CASES)
    ) and all(r["gram_harmonic_agree"] for r in results)

    cert = {
        "engine": "finite_nerve_warrant_debt",
        "theorem": "Finite Graph Period Classification + Nerve Extension",
        "formula": "D(r) = p^T G^{-1} p  via Hodge Laplacian ker(L_1)",
        "results": results,
        "all_passed": all_ok,
    }
    out = Path("certificates") / "finite_nerve_warrant_debt_certificate.json"
    out.write_text(json.dumps(cert, indent=2))
    print(f"Certificate saved to: {out}")
    sys.exit(0 if all_ok else 1)
