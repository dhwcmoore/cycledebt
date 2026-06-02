"""
Dynamic Warrant Debt Theorem.

Let (r_t)_{t>=0} be a time-indexed sequence of residues on a fixed finite
regional system. For each r_t, decompose:

    r_t = r_t^adm + r_t^debt          (harmonic decomposition, standard inner product)

Define the warrant debt magnitude:

    D(t) = ||r_t^debt||^2              (inner-product-relative; see caveat below)

Theorem (Dynamic Warrant Debt):
    D(t) = 0  <=>  [r_t] = 0  <=>  system is globally admissible at time t.
    D(t) > 0  <=>  system carries irremovable warrant debt at time t.

Fatigue (change in debt between steps):
    F(t0, t1) = D(t1) - D(t0)

Cumulative debt load:
    W(T) = sum_{t=0}^{T} D(t)

Four-Cycle Debt Formula (single-cycle system, standard inner product):
    D(t) = p(t)^2 / ||z||^2 = p(t)^2 / 4

where p(t) = <z, r_t> is the obstruction period at time t and ||z||^2 = 4.

Caveat: D(t), r_t^debt, and W(T) depend on the choice of inner product.
The period p(t) and the class [r_t] are inner-product-independent.

Toy model:
    r_t = (1, 1, 1, 3 - eps_t)
    p(t) = -eps_t
    D(t) = eps_t^2 / 4
    The actual object r = (1,1,1,-2) is the case eps = 5: D = 25/4.
"""

import sympy as sp
import json
import sys
from pathlib import Path
from admissibility_bridge import gram_schmidt, harmonic_split, admissible_gauge
from residue_test import classify_residue, build_matrices

REGIONS = ["U1", "U2", "U3", "U4"]
EDGES   = [["U1", "U2"], ["U2", "U3"], ["U3", "U4"], ["U1", "U4"]]
FACES   = []


def _D0():
    return build_matrices(REGIONS, [tuple(e) for e in EDGES], FACES)[0]


# Precompute D0 and cycle basis once
_d0 = _D0()
_z_raw = _d0.T.nullspace()
_z_ortho = gram_schmidt(_z_raw)
_z_prim = _z_ortho[0]           # (-1,-1,-1,1) for the four-cycle
_z_norm_sq = _z_prim.dot(_z_prim)  # = 4


def analyse_one(residue_vals):
    """Single-step warrant debt analysis. Returns a dict."""
    r = sp.Matrix([sp.Rational(v) for v in residue_vals])

    # Period (obstruction circulation) — inner-product-independent
    period = _z_prim.dot(r)

    # Admissibility
    cert = classify_residue(REGIONS, [tuple(e) for e in EDGES], FACES, residue_vals)
    is_adm = cert["is_coboundary"]

    # Harmonic decomposition — inner-product-relative
    r_adm_vec, r_debt_vec = harmonic_split(residue_vals, _d0)
    D = r_debt_vec.dot(r_debt_vec)

    # Four-Cycle Debt Formula check: D should equal period^2 / ||z||^2
    D_formula = sp.Rational(period**2, _z_norm_sq)
    formula_agrees = (D == D_formula)

    # Closest admissible gauge
    gauge = admissible_gauge(r_adm_vec, _d0, len(REGIONS))

    return {
        "residue": [str(v) for v in r],
        "period": str(period),
        "is_admissible": is_adm,
        "D": str(D),
        "D_formula": str(D_formula),
        "formula_agrees": formula_agrees,
        "r_adm": [str(v) for v in r_adm_vec],
        "r_debt": [str(v) for v in r_debt_vec],
        "b_star": [str(v) for v in gauge] if gauge else None,
    }


def compute_trajectory(time_series, label=""):
    """
    Full dynamic warrant debt analysis for a sequence of (t, residue) pairs.

    Returns trajectory with per-step D(t), fatigue F(t), and cumulative W(T).
    """
    steps = []
    prev_D = sp.Integer(0)

    for t, residue in time_series:
        s = analyse_one(residue)
        D = sp.sympify(s["D"])
        fatigue = D - prev_D
        s["t"] = t
        s["fatigue"] = str(fatigue)
        steps.append(s)
        prev_D = D

    D_vals = [sp.sympify(s["D"]) for s in steps]
    W = sum(D_vals)
    max_D = max(D_vals)
    n_adm = sum(1 for s in steps if s["is_admissible"])

    return {
        "label": label,
        "steps": steps,
        "W_cumulative": str(W),
        "D_max": str(max_D),
        "n_admissible_steps": n_adm,
        "n_steps": len(steps),
        "always_in_debt": n_adm == 0,
        "ever_admissible": n_adm > 0,
        "formula_always_agrees": all(s["formula_agrees"] for s in steps),
    }


def print_trajectory(traj):
    w = 72
    print(f"Scenario: {traj['label']}")
    print(f"{'t':>3}  {'residue':<22} {'p(t)':>6} {'D(t)':>8} "
          f"{'fatigue':>9} {'admissible':>11}")
    print("-" * w)
    for s in traj["steps"]:
        r_str = "(" + ",".join(s["residue"]) + ")"
        adm = "YES" if s["is_admissible"] else "no"
        fat = s["fatigue"]
        fat_str = (("+" if not fat.startswith("-") else "") + fat)
        print(f"{s['t']:>3}  {r_str:<22} {s['period']:>6} {s['D']:>8} "
              f"{fat_str:>9} {adm:>11}")
    print()
    print(f"  W(T) = {traj['W_cumulative']}   D_max = {traj['D_max']}   "
          f"admissible steps: {traj['n_admissible_steps']}/{traj['n_steps']}")
    print(f"  Four-Cycle Debt Formula D=p^2/4 holds: {traj['formula_always_agrees']}")
    print()


if __name__ == "__main__":
    print("=" * 72)
    print("DYNAMIC WARRANT DEBT THEOREM — TRAJECTORY ANALYSIS")
    print("=" * 72)
    print(f"  D(t) = p(t)^2 / ||z||^2   (four-cycle: ||z||^2 = {_z_norm_sq})")
    print()

    # ------------------------------------------------------------------
    # Scenario 1: Toy model — onset of warrant debt from admissible state
    # r_t = (1, 1, 1, 3 - eps_t), eps_t = 0, 1, 2, 3, 4, 5
    # At t=5: r = (1,1,1,-2) = the actual object
    # ------------------------------------------------------------------
    eps = [0, 1, 2, 3, 4, 5]
    s1_series = [(t, [1, 1, 1, 3 - e]) for t, e in enumerate(eps)]
    t1 = compute_trajectory(s1_series,
         label="Toy model: r_t=(1,1,1,3-eps_t), onset from admissible (eps=0..5)")
    print_trajectory(t1)

    # ------------------------------------------------------------------
    # Scenario 2: Fatigue, partial recovery, re-escalation
    # ------------------------------------------------------------------
    eps2 = [0, 2, 4, 5, 3, 1, 0, 1, 3, 5]
    s2_series = [(t, [1, 1, 1, 3 - e]) for t, e in enumerate(eps2)]
    t2 = compute_trajectory(s2_series,
         label="Fatigue/recovery cycle: onset → partial recovery → re-escalation")
    print_trajectory(t2)

    # ------------------------------------------------------------------
    # Scenario 3: Actual object as fixed debt — constant trajectory
    # ------------------------------------------------------------------
    s3_series = [(t, [1, 1, 1, -2]) for t in range(6)]
    t3 = compute_trajectory(s3_series,
         label="Actual object r=(1,1,1,-2) held fixed — constant debt D=25/4")
    print_trajectory(t3)

    # ------------------------------------------------------------------
    # Verification: D(t) = p(t)^2 / 4 formula
    # ------------------------------------------------------------------
    print("Four-Cycle Debt Formula  D(t) = p(t)^2 / 4:")
    for traj in [t1, t2, t3]:
        status = "OK" if traj["formula_always_agrees"] else "FAIL"
        print(f"  {traj['label'][:55]:<55} {status}")
    print()

    cert = {
        "theorem": "dynamic_warrant_debt",
        "four_cycle_debt_formula": "D(t) = p(t)^2 / ||z||^2, ||z||^2 = 4",
        "caveat": (
            "D(t) and the harmonic decomposition are relative to the standard "
            "rational inner product on the declared edge basis. "
            "The period p(t) = <z, r_t> is inner-product-independent."
        ),
        "scenarios": [t1, t2, t3],
        "all_formula_verified": all(t["formula_always_agrees"] for t in [t1, t2, t3]),
    }
    out = Path("certificates") / "dynamic_warrant_debt_certificate.json"
    out.write_text(json.dumps(cert, indent=2))
    print(f"Certificate saved to: {out}")

    ok = cert["all_formula_verified"]
    sys.exit(0 if ok else 1)
