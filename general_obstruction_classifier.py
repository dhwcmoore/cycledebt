"""
General Finite Regional Obstruction Classifier.

Theorem (General finite graph cycle-detection):
  Let G be a finite connected oriented graph over a field k.
  For any r in C^1(G; k):

      [r] = 0 in H^1(G; k)   iff   <z, r> = 0 for all z in Z_1(G; k).

Proof:
  (=>) If r = delta^0 b then <z, r> = <delta^{0,T} z, b> = <0, b> = 0.
  (<=) Over a field, Z_1 = (im delta^0)^perp under the standard pairing
       (rank-nullity: dim Z_1 + dim im delta^0 = dim C^1, and im delta^0 is
       self-orthogonal to Z_1 by (=>)). So r perp Z_1 implies r in im delta^0.

For a simplicial complex N (with 2-faces), the same holds restricted to
cocycles (delta^1 r = 0): [r] = 0 in H^1(N; k) iff delta^1 r = 0 and
<z, r> = 0 for all z in Z_1(N; k).

This script verifies the theorem on six graph structures and demonstrates that
classify_residue (residue_test.py) functions as a general obstruction engine.
"""

import sympy as sp
import json
import sys
from pathlib import Path
from residue_test import classify_residue, build_matrices


def cycle_basis(regions, edges, faces):
    """Return a basis for Z_1(G; Q) = null(delta^{0,T})."""
    D0, _ = build_matrices(regions, edges, faces)
    return D0.T.nullspace()


def all_cycle_pairings(r_vec, z_basis):
    """Return list of <z, r> for each basis cycle z."""
    r = sp.Matrix([sp.Rational(v) for v in r_vec])
    return [z.dot(r) for z in z_basis]


def h1_dim(regions, edges, faces):
    """Dimension of H^1 over Q."""
    D0, D1 = build_matrices(regions, edges, faces)
    n1 = len(edges)
    n2 = len(faces)
    rank_D0 = D0.rank()
    rank_D1 = D1.rank() if n2 > 0 else 0
    return (n1 - rank_D1) - rank_D0


def verify_case(case):
    """
    For one test case, verify:
      is_coboundary  iff  all cycle pairings are zero.
    Returns a result dict.
    """
    regions = case["regions"]
    edges   = [tuple(e) for e in case["edges"]]
    faces   = [tuple(f) for f in case.get("faces", [])]
    r_vals  = case["residue"]
    desc    = case["description"]

    cert = classify_residue(regions, edges, faces, r_vals)
    is_cobdy = cert["is_coboundary"]
    is_cocyc = cert["is_cocycle"]

    z_basis = cycle_basis(regions, edges, faces)
    pairings = all_cycle_pairings(r_vals, z_basis)
    all_zero = all(p == 0 for p in pairings)

    # Theorem check: for cocycles, is_coboundary ↔ all_zero
    if is_cocyc:
        theorem_holds = (is_cobdy == all_zero)
    else:
        theorem_holds = True  # theorem only applies to cocycles

    expected_H1 = case.get("expected_H1_dim")
    actual_H1   = h1_dim(regions, edges, faces)
    H1_ok = (expected_H1 is None) or (actual_H1 == expected_H1)

    return {
        "name": case["name"],
        "description": desc,
        "dim_H1": actual_H1,
        "dim_H1_expected": expected_H1,
        "dim_H1_correct": H1_ok,
        "is_cocycle": is_cocyc,
        "is_coboundary": is_cobdy,
        "classification": cert["classification"],
        "cycle_pairings": [str(p) for p in pairings],
        "all_pairings_zero": all_zero,
        "theorem_holds": theorem_holds,
        "passed": theorem_holds and H1_ok,
    }


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

TEST_CASES = [
    # ------------------------------------------------------------------
    # 1. Path graph P3: 3 vertices, 2 edges. No cycles. H1 = 0.
    #    Every cochain is a coboundary (trivially).
    # ------------------------------------------------------------------
    {
        "name": "path_P3",
        "description": "Path graph: 3 vertices, 2 edges, no cycles. H^1 = 0.",
        "regions": ["A", "B", "C"],
        "edges": [["A", "B"], ["B", "C"]],
        "faces": [],
        "residue": [3, -1],
        "expected_H1_dim": 0,
    },

    # ------------------------------------------------------------------
    # 2. 3-cycle C3 (no face): 3 vertices, 3 edges. H1 = Q.
    #    Cycle: z = (-1, -1, 1) for the oriented triangle A→B→C→A.
    #    Residue (1, 1, -1): pairing = -1-1-1 = ... let's compute.
    #    Actually z_basis depends on orientation; let sympy find it.
    # ------------------------------------------------------------------
    {
        "name": "triangle_C3",
        "description": "3-cycle (no face): H^1 = Q. Non-trivial residue.",
        "regions": ["A", "B", "C"],
        "edges": [["A", "B"], ["B", "C"], ["A", "C"]],
        "faces": [],
        "residue": [1, 1, -3],
        "expected_H1_dim": 1,
    },
    {
        "name": "triangle_C3_coboundary",
        "description": "3-cycle (no face): H^1 = Q. Trivial residue (zero circulation).",
        "regions": ["A", "B", "C"],
        "edges": [["A", "B"], ["B", "C"], ["A", "C"]],
        "faces": [],
        "residue": [1, 1, 2],
        "expected_H1_dim": 1,
    },

    # ------------------------------------------------------------------
    # 3. 4-cycle C4: our actual object. H1 = Q.
    # ------------------------------------------------------------------
    {
        "name": "four_cycle_C4",
        "description": "4-cycle (our object): H^1 = Q. Period -5.",
        "regions": ["U1", "U2", "U3", "U4"],
        "edges": [["U1", "U2"], ["U2", "U3"], ["U3", "U4"], ["U1", "U4"]],
        "faces": [],
        "residue": [1, 1, 1, -2],
        "expected_H1_dim": 1,
    },

    # ------------------------------------------------------------------
    # 4. 5-cycle C5. H1 = Q.
    # ------------------------------------------------------------------
    {
        "name": "five_cycle_C5",
        "description": "5-cycle: H^1 = Q. Residue with non-zero circulation.",
        "regions": ["A", "B", "C", "D", "E"],
        "edges": [["A", "B"], ["B", "C"], ["C", "D"], ["D", "E"], ["A", "E"]],
        "faces": [],
        "residue": [2, 1, 1, 1, -7],
        "expected_H1_dim": 1,
    },

    # ------------------------------------------------------------------
    # 5. 4-cycle with chord (diamond graph): 4 vertices, 5 edges. H1 = Q^2.
    #    Two independent obstruction cycles.
    # ------------------------------------------------------------------
    {
        "name": "diamond_chord",
        "description": "4-cycle plus one chord: H^1 = Q^2. Two independent cycles.",
        "regions": ["A", "B", "C", "D"],
        "edges": [["A", "B"], ["B", "C"], ["C", "D"], ["A", "D"], ["A", "C"]],
        "faces": [],
        "residue": [1, 1, 1, -2, 0],
        "expected_H1_dim": 2,
    },
    {
        "name": "diamond_coboundary",
        "description": "4-cycle plus chord: coboundary = delta^0(0,1,2,1), pairings both zero.",
        "regions": ["A", "B", "C", "D"],
        "edges": [["A", "B"], ["B", "C"], ["C", "D"], ["A", "D"], ["A", "C"]],
        "faces": [],
        "residue": [1, 1, -1, 1, 2],
        "expected_H1_dim": 2,
    },

    # ------------------------------------------------------------------
    # 6. Filled triangle (2-simplex): 3 vertices, 3 edges, 1 face. H1 = 0.
    #    The face kills the only cycle. Every cocycle is a coboundary.
    # ------------------------------------------------------------------
    {
        "name": "filled_triangle",
        "description": "Filled triangle: H^1 = 0. Cocycles are automatically coboundaries.",
        "regions": ["A", "B", "C"],
        "edges": [["A", "B"], ["B", "C"], ["A", "C"]],
        "faces": [["A", "B", "C"]],
        "residue": [1, 2, 3],
        "expected_H1_dim": 0,
    },

    # ------------------------------------------------------------------
    # 7. Complete graph K4: 4 vertices, 6 edges. H1 = Q^3.
    # ------------------------------------------------------------------
    {
        "name": "complete_K4",
        "description": "Complete graph K4: H^1 = Q^3. Three independent obstruction cycles.",
        "regions": ["A", "B", "C", "D"],
        "edges": [
            ["A", "B"], ["A", "C"], ["A", "D"],
            ["B", "C"], ["B", "D"], ["C", "D"],
        ],
        "faces": [],
        "residue": [1, 1, 1, 1, 1, -5],
        "expected_H1_dim": 3,
    },
]


def print_report(results):
    width = 72
    print("=" * width)
    print("GENERAL FINITE REGIONAL OBSTRUCTION CLASSIFIER — THEOREM VERIFICATION")
    print("=" * width)
    print()
    print("Theorem: [r] = 0  iff  <z, r> = 0 for all z in Z_1(G; Q).")
    print()
    hdr = f"{'Name':<25} {'H1':>4} {'Cocycle':>8} {'Cobdy':>7} {'PairingsZero':>13} {'Thm':>5}"
    print(hdr)
    print("-" * width)
    for res in results:
        row = (
            f"{res['name']:<25} "
            f"{res['dim_H1']:>4} "
            f"{'Y' if res['is_cocycle'] else 'N':>8} "
            f"{'Y' if res['is_coboundary'] else 'N':>7} "
            f"{'Y' if res['all_pairings_zero'] else 'N':>13} "
            f"{'OK' if res['theorem_holds'] else 'FAIL':>5}"
        )
        print(row)
    print()
    all_pass = all(r["passed"] for r in results)
    n = len(results)
    n_pass = sum(r["passed"] for r in results)
    print(f"Passed: {n_pass}/{n}   Overall: {'ALL PASS' if all_pass else 'FAILURES PRESENT'}")
    print()
    print("Graph type summary:")
    seen_H1 = {}
    for res in results:
        key = res["dim_H1"]
        if key not in seen_H1:
            seen_H1[key] = []
        seen_H1[key].append(res["name"])
    for dim in sorted(seen_H1):
        label = f"H^1 = Q^{dim}" if dim > 1 else ("H^1 = 0" if dim == 0 else "H^1 = Q")
        print(f"  {label:15}  {', '.join(seen_H1[dim])}")


if __name__ == "__main__":
    results = [verify_case(c) for c in TEST_CASES]
    print_report(results)

    cert = {
        "theorem": "general_finite_graph_cycle_detection",
        "statement": (
            "[r] = 0 in H^1(G; Q) iff <z, r> = 0 for all z in Z_1(G; Q)."
        ),
        "test_cases": results,
        "all_passed": all(r["passed"] for r in results),
    }
    out = Path("certificates") / "general_obstruction_classifier_certificate.json"
    out.write_text(json.dumps(cert, indent=2))
    print(f"\nCertificate saved to: {out}")

    sys.exit(0 if cert["all_passed"] else 1)
