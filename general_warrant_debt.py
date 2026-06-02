"""
General Warrant Debt Formula: Gram Matrix Formulation.

For a finite connected oriented graph with cycle basis {z_1, ..., z_k},
the warrant debt magnitude is:

    D(r) = p(r)^T * G^{-1} * p(r)

where:
    p_i(r) = <z_i, r>           (obstruction period — inner-product-independent)
    G_ij   = <z_i, z_j>         (Gram matrix of the cycle basis)
    G^{-1}                       (rational inverse of G)

Special cases:
    k=1 (single cycle):    D = p^2 / ||z||^2                   (four-cycle: 1/4)
    Orthogonal basis:      D = sum_i p_i^2 / ||z_i||^2         (decoupled)
    General:               D = p^T G^{-1} p                    (Gram-coupled)

Both this formula and the harmonic_split projection in admissibility_bridge.py
give identical results. This script verifies that identity and demonstrates
the Gram matrix structure for three graph types.

Theorem (General Warrant Debt):
    D(r) = 0  <=>  [r] = 0 in H^1  <=>  globally admissible.
    D(r) > 0  <=>  irremovable warrant debt.

Dynamic version:
    D(t) = p(t)^T G^{-1} p(t)
    W(T) = sum_{t=0}^T D(t)   (cumulative debt load)

Caveat: D and G^{-1} depend on the inner product. The period vector p and the
admissibility verdict are inner-product-independent.
"""

import sympy as sp
import json
import sys
from pathlib import Path
from residue_test import classify_residue, build_matrices
from admissibility_bridge import gram_schmidt, harmonic_split


# ---------------------------------------------------------------------------
# Core Gram matrix debt machinery
# ---------------------------------------------------------------------------

def cycle_basis(regions, edges, faces):
    """Return raw (not gram-schmidt'd) cycle basis from null(delta^0^T)."""
    D0, _ = build_matrices(regions, [tuple(e) for e in edges], faces)
    return D0.T.nullspace(), D0


def gram_matrix(z_basis):
    """G_ij = <z_i, z_j>. Returns sympy Matrix."""
    k = len(z_basis)
    G = sp.zeros(k, k)
    for i, zi in enumerate(z_basis):
        for j, zj in enumerate(z_basis):
            G[i, j] = zi.dot(zj)
    return G


def period_vector(r_vals, z_basis):
    """p_i = <z_i, r> for each basis cycle."""
    r = sp.Matrix([sp.Rational(v) for v in r_vals])
    return sp.Matrix([z.dot(r) for z in z_basis])


def debt_gram(p_vec, G):
    """D = p^T G^{-1} p over Q."""
    G_inv = G.inv()
    return (p_vec.T * G_inv * p_vec)[0, 0]


def analyse_gram(regions, edges, faces, residue):
    """
    Compute D via Gram matrix formula and verify against harmonic_split.
    Returns a result dict.
    """
    z_basis, D0 = cycle_basis(regions, edges, faces)
    if not z_basis:
        return {"dim_H1": 0, "D_gram": "0", "D_harmonic": "0", "agree": True,
                "G": [], "G_inv": [], "p": []}

    G = gram_matrix(z_basis)
    p = period_vector(residue, z_basis)
    D_g = debt_gram(p, G)

    # Verify against harmonic_split (gram-schmidt projection)
    _, r_debt = harmonic_split(residue, D0)
    D_h = r_debt.dot(r_debt)

    return {
        "dim_H1": len(z_basis),
        "G": [[str(G[i, j]) for j in range(G.shape[1])] for i in range(G.shape[0])],
        "G_inv": [[str(G.inv()[i, j]) for j in range(G.shape[1])] for i in range(G.shape[0])],
        "p": [str(v) for v in p],
        "D_gram": str(D_g),
        "D_harmonic": str(D_h),
        "agree": bool(D_g == D_h),
    }


# ---------------------------------------------------------------------------
# Dynamic trajectory via Gram formula
# ---------------------------------------------------------------------------

def dynamic_gram(regions, edges, faces, time_series, label=""):
    """
    Compute D(t) = p(t)^T G^{-1} p(t) for a time series.
    time_series: list of (t, residue_vals) pairs.
    """
    z_basis, D0 = cycle_basis(regions, edges, faces)
    G = gram_matrix(z_basis) if z_basis else sp.zeros(0, 0)

    steps = []
    D_prev = sp.Integer(0)
    for t, residue in time_series:
        p = period_vector(residue, z_basis) if z_basis else sp.zeros(0, 1)
        D = debt_gram(p, G) if z_basis else sp.Integer(0)
        cert = classify_residue(regions, [tuple(e) for e in edges], faces, residue)
        steps.append({
            "t": t,
            "residue": [str(sp.Rational(v)) for v in residue],
            "p": [str(v) for v in p],
            "D": str(D),
            "fatigue": str(D - D_prev),
            "is_admissible": cert["is_coboundary"],
        })
        D_prev = D

    W = sum(sp.sympify(s["D"]) for s in steps)
    return {
        "label": label,
        "dim_H1": len(z_basis),
        "G": [[str(G[i, j]) for j in range(G.shape[1])] for i in range(G.shape[0])],
        "steps": steps,
        "W_cumulative": str(W),
        "D_max": str(max(sp.sympify(s["D"]) for s in steps)),
    }


def print_trajectory(traj):
    print(f"  {traj['label']}")
    print(f"  dim H¹ = {traj['dim_H1']}   G = {traj['G']}   W = {traj['W_cumulative']}")
    hdr = f"    {'t':>3}  {'residue':<26} {'p':>18} {'D(t)':>8} {'fat':>8} {'adm':>5}"
    print(hdr)
    print("    " + "-" * 72)
    for s in traj["steps"]:
        r_str = "(" + ",".join(s["residue"]) + ")"
        p_str = "(" + ",".join(s["p"]) + ")"
        fat = s["fatigue"]
        fat_str = ("+" if not fat.startswith("-") else "") + fat
        adm = "Y" if s["is_admissible"] else "n"
        print(f"    {s['t']:>3}  {r_str:<26} {p_str:>18} {s['D']:>8} {fat_str:>8} {adm:>5}")
    print()


# ---------------------------------------------------------------------------
# Graph definitions
# ---------------------------------------------------------------------------

GRAPHS = {
    "four_cycle": {
        "regions": ["U1", "U2", "U3", "U4"],
        "edges":   [["U1","U2"], ["U2","U3"], ["U3","U4"], ["U1","U4"]],
        "faces":   [],
    },
    "diamond": {
        "regions": ["A", "B", "C", "D"],
        "edges":   [["A","B"], ["B","C"], ["C","D"], ["A","D"], ["A","C"]],
        "faces":   [],
    },
    "K4": {
        "regions": ["A", "B", "C", "D"],
        "edges":   [["A","B"], ["A","C"], ["A","D"], ["B","C"], ["B","D"], ["C","D"]],
        "faces":   [],
    },
}


if __name__ == "__main__":
    print("=" * 72)
    print("GENERAL WARRANT DEBT FORMULA — GRAM MATRIX VERIFICATION")
    print("=" * 72)
    print()
    print("Theorem: D(r) = p(r)^T G^{-1} p(r)")
    print("         p_i = <z_i, r>,  G_ij = <z_i, z_j>")
    print()

    # ------------------------------------------------------------------
    # Part 1: Static verification — D_gram == D_harmonic for each graph
    # ------------------------------------------------------------------
    print("Part 1: Static verification on test residues")
    print("-" * 72)
    test_residues = {
        "four_cycle": [1, 1, 1, -2],
        "diamond":    [1, 1, 1, -2, 0],
        "K4":         [1, 1, 1, 1, 1, -5],
    }

    gram_results = {}
    for name, g in GRAPHS.items():
        r = test_residues[name]
        res = analyse_gram(g["regions"], g["edges"], g["faces"], r)
        gram_results[name] = res
        agree = "OK" if res["agree"] else "FAIL"
        print(f"  {name:<15}  dim H¹={res['dim_H1']}  "
              f"p={res['p']}  D_gram={res['D_gram']}  "
              f"D_harmonic={res['D_harmonic']}  [{agree}]")
        print(f"              G = {res['G']}")
        print()

    all_agree = all(r["agree"] for r in gram_results.values())
    print(f"  D_gram == D_harmonic for all graphs: {all_agree}")
    print()

    # ------------------------------------------------------------------
    # Part 2: Dynamic trajectories
    # ------------------------------------------------------------------
    print("Part 2: Dynamic trajectories")
    print("-" * 72)
    print()

    # Four-cycle toy model (sanity check: D = p^2/4)
    fc = GRAPHS["four_cycle"]
    s1 = [(t, [1, 1, 1, 3 - t]) for t in range(6)]
    t1 = dynamic_gram(fc["regions"], fc["edges"], fc["faces"], s1,
                      label="Four-cycle toy model r_t=(1,1,1,3-t): D(t)=t^2/4")
    print_trajectory(t1)

    # Diamond — simultaneous onset in both cycles
    dm = GRAPHS["diamond"]
    # r_t = (1,1,1,3-t,2-t): p(t)=(-t,-t), D(t) = p^T G^{-1} p
    s2 = [(t, [1, 1, 1, 3 - t, 2 - t]) for t in range(6)]
    t2 = dynamic_gram(dm["regions"], dm["edges"], dm["faces"], s2,
                      label="Diamond both cycles: r_t=(1,1,1,3-t,2-t)")
    print_trajectory(t2)

    # Diamond — second cycle only
    s3 = [(t, [1, 1, 1, 3, 2 - t]) for t in range(6)]
    t3 = dynamic_gram(dm["regions"], dm["edges"], dm["faces"], s3,
                      label="Diamond second cycle only: r_t=(1,1,1,3,2-t)")
    print_trajectory(t3)

    # K4 — single period grows
    k4 = GRAPHS["K4"]
    # Start admissible, let one component drift
    # admissible K4 residue: need all cycle pairings = 0
    # Simple: r=(1,1,1,1,1,-5) has specific pairings; let's find admissible base first
    # With r=(0,0,0,0,0,0): all zero, trivially admissible
    # Trajectory: r_t = (0,0,0,0,0,t) — introduce debt in last edge
    s4 = [(t, [0, 0, 0, 0, 0, -t]) for t in range(5)]
    t4 = dynamic_gram(k4["regions"], k4["edges"], k4["faces"], s4,
                      label="K4 one-edge drift: r_t=(0,0,0,0,0,-t)")
    print_trajectory(t4)

    # ------------------------------------------------------------------
    # Part 3: Four-Cycle Debt Formula D = p^2/4 explicit verification
    # ------------------------------------------------------------------
    print("Part 3: Four-Cycle Debt Formula  D(t) = p(t)^2 / 4")
    print("-" * 72)
    all_formula_ok = True
    for s in t1["steps"]:
        p_val = sp.sympify(s["p"][0])
        D_val = sp.sympify(s["D"])
        formula = p_val**2 / 4
        ok = (D_val == formula)
        if not ok:
            all_formula_ok = False
        print(f"  t={s['t']}  p={s['p'][0]}  D={s['D']}  p^2/4={formula}  {'OK' if ok else 'FAIL'}")
    print()

    cert = {
        "theorem": "general_warrant_debt_gram_formula",
        "formula": "D(r) = p(r)^T G^{-1} p(r)",
        "four_cycle_special_case": "D = p^2 / 4  (G = [4], G^{-1} = [1/4])",
        "gram_results": gram_results,
        "trajectories": {
            "four_cycle_toy_model": t1,
            "diamond_simultaneous": t2,
            "diamond_second_cycle": t3,
            "K4_one_edge_drift": t4,
        },
        "all_gram_harmonic_agree": all_agree,
        "four_cycle_formula_verified": all_formula_ok,
    }
    out = Path("certificates") / "general_warrant_debt_certificate.json"
    out.write_text(json.dumps(cert, indent=2))
    print(f"Certificate saved to: {out}")

    ok = all_agree and all_formula_ok
    sys.exit(0 if ok else 1)
