"""
Residue-Admissibility Bridge Theorem.

Theorem:
  Let N be a finite regional nerve and r in C^1(N; Q) a seam residue
  satisfying the cocycle condition (delta^1 r = 0).

  The following are equivalent:
    (1) Gauge-admissible:     exists b in C^0 with delta^0 b = r.
    (2) Globally consistent:  exists a global claim Phi with Phi_j - Phi_i = r_ij
                              for every overlap (U_i, U_j).
    (3) Cohomologically zero: [r] = 0 in H^1(N; Q).

  Proof of (1) <=> (3): definition of H^1 = C^1 / im(delta^0).
  Proof of (2) <=> (1): set b = Phi (the region-values are the gauge).
    Then (delta^0 b)_ij = b_j - b_i = Phi_j - Phi_i = r_ij. Conversely, if
    delta^0 b = r then the global claim Phi_i := b_i is consistent. QED.

  Corollary (Warrant Debt):
    If [r] != 0, no globally consistent claim exists. The class [r] in H^1
    quantifies the warrant debt: the irreducible, gauge-invariant inconsistency
    built into the seam data.

Harmonic decomposition (Warrant Debt Decomposition):
  Over Q with the standard inner product, C^1 decomposes orthogonally:
    C^1 = im(delta^0)  +  Z_1
  Any seam residue splits uniquely as:
    r = r_admissible + r_debt
  where:
    r_admissible in im(delta^0):  closest consistent residue to r.
    r_debt       in Z_1:          the irremovable warrant debt component.
  The gauge b* with delta^0 b* = r_admissible is the local correction that
  would make the system just-admissible; r_debt persists regardless.

This script verifies the theorem on the actual object and one admissible
comparison, emitting a machine-readable certificate.
"""

import sympy as sp
import json
import sys
from pathlib import Path
from residue_test import classify_residue, build_matrices


def gram_schmidt(vecs):
    """Gram-Schmidt over Q. Returns pairwise-orthogonal basis (not normalised)."""
    result = []
    for v in vecs:
        w = v.copy()
        for u in result:
            denom = u.dot(u)
            if denom != 0:
                w = w - sp.Rational(u.dot(v), denom) * u
        if w.dot(w) != 0:
            result.append(w)
    return result


def harmonic_split(residue_vals, D0):
    """
    Decompose r = r_admissible + r_debt over Q.

    r_debt       = projection of r onto Z_1 = ker(D0^T)
    r_admissible = r - r_debt  (lies in im(D0), the admissible part)
    """
    r = sp.Matrix([sp.Rational(v) for v in residue_vals])
    raw = D0.T.nullspace()
    ortho = gram_schmidt(raw)

    r_debt = sp.zeros(len(residue_vals), 1)
    for z in ortho:
        coeff = z.dot(r) / z.dot(z)
        r_debt = r_debt + coeff * z

    r_adm = r - r_debt
    return r_adm, r_debt


def admissible_gauge(r_adm, D0, n_regions):
    """
    Solve delta^0 b = r_adm with gauge fix b_0 = 0.
    Returns list of rationals or None.
    """
    g = sp.symbols(f"g:{n_regions}")
    G = sp.Matrix(list(g))
    eqs = list(D0 * G - r_adm)
    sol = sp.solve(eqs, g, dict=True)
    if not sol:
        return None
    s = sol[0]
    vals = []
    for sym in g:
        v = s.get(sym, sp.Integer(0))
        for fs in list(v.free_symbols if hasattr(v, 'free_symbols') else []):
            v = v.subs(fs, sp.Integer(0))
        vals.append(v)
    return vals


def analyse(regions, edges, faces, residue, label=""):
    """
    Full residue-admissibility analysis.
    Returns a certificate dict.
    """
    etup = [tuple(e) for e in edges]
    D0, _ = build_matrices(regions, etup, faces)
    r = sp.Matrix([sp.Rational(v) for v in residue])

    # Standard classification
    base = classify_residue(regions, etup, faces, residue)
    is_adm = base["is_coboundary"]

    # Cycle pairings
    raw_z = D0.T.nullspace()
    pairings = []
    for z in raw_z:
        p = z.dot(r)
        pairings.append({
            "z": [str(v) for v in z],
            "pairing": str(p),
            "is_nonzero": bool(p != 0),
        })

    # Harmonic decomposition
    r_adm_vec, r_debt_vec = harmonic_split(residue, D0)

    # Closest admissible gauge
    gauge = admissible_gauge(r_adm_vec, D0, len(regions))

    # Verification: delta^0 b* = r_adm
    if gauge is not None:
        b_mat = sp.Matrix([sp.Rational(v) for v in gauge])
        check = D0 * b_mat
        gauge_verified = (check == r_adm_vec)
    else:
        gauge_verified = None

    debt_norm_sq = r_debt_vec.dot(r_debt_vec)

    return {
        "label": label,
        "residue": [str(v) for v in r],
        "is_globally_admissible": is_adm,
        "warrant_debt_present": not is_adm,
        "cycle_pairings": pairings,
        "harmonic_decomposition": {
            "r_admissible": [str(v) for v in r_adm_vec],
            "r_debt":       [str(v) for v in r_debt_vec],
            "debt_norm_sq": str(debt_norm_sq),
        },
        "closest_admissible_gauge": {
            "b_star": [str(v) for v in gauge] if gauge else None,
            "delta0_b_star_equals_r_adm": gauge_verified,
        },
        "theorem_verified": is_adm == (debt_norm_sq == 0),
    }


def print_case(a):
    w = 72
    label = a["label"] or "(unlabelled)"
    print(f"Object: {label}")
    print(f"Seam residue r = {a['residue']}")
    print()
    if a["is_globally_admissible"]:
        print("VERDICT: GLOBALLY ADMISSIBLE")
        print("  A consistent global claim Phi exists.")
        b = a["closest_admissible_gauge"]["b_star"]
        print(f"  Global claim (gauge) b = {b}")
        print("  Phi_i := b_i makes every seam consistent: Phi_j - Phi_i = r_ij.")
    else:
        print("VERDICT: WARRANT DEBT — NOT GLOBALLY ADMISSIBLE")
        print("  No global consistent claim Phi exists.")
        print()
        print("  Cycle witnesses carrying the debt:")
        for cp in a["cycle_pairings"]:
            if cp["is_nonzero"]:
                print(f"    z = {cp['z']}   <z,r> = {cp['pairing']}")
        print()
        dec = a["harmonic_decomposition"]
        print("  Harmonic decomposition  r = r_admissible + r_debt:")
        print(f"    r_admissible = {dec['r_admissible']}")
        print(f"       (closest consistent residue; reachable by gauge b* below)")
        print(f"    r_debt       = {dec['r_debt']}")
        print(f"       (irremovable; lives in Z_1; no gauge choice touches it)")
        print(f"    ||r_debt||^2 = {dec['debt_norm_sq']}")
        print()
        b = a["closest_admissible_gauge"]["b_star"]
        ok = a["closest_admissible_gauge"]["delta0_b_star_equals_r_adm"]
        print(f"  Closest admissible gauge b* = {b}  (delta^0 b* = r_admissible: {ok})")
        print("  Adjusting local claims by b* yields the nearest admissible system.")
        print("  r_debt persists regardless; it cannot be gauged away.")
    print()
    tv = a["theorem_verified"]
    print(f"  Bridge theorem verified: {tv}")
    print("-" * w)


if __name__ == "__main__":
    REGIONS = ["U1", "U2", "U3", "U4"]
    EDGES   = [["U1","U2"], ["U2","U3"], ["U3","U4"], ["U1","U4"]]
    FACES   = []

    print("=" * 72)
    print("RESIDUE-ADMISSIBILITY BRIDGE THEOREM — WARRANT DEBT ANALYSIS")
    print("=" * 72)
    print()

    # Case 1: the actual object (inadmissible)
    a1 = analyse(REGIONS, EDGES, FACES, [1, 1, 1, -2],
                 label="actual_gluing_object_v1  [r=(1,1,1,-2), period=-5]")
    print_case(a1)

    print()

    # Case 2: a residue with zero circulation (admissible)
    a2 = analyse(REGIONS, EDGES, FACES, [1, 1, 1, 3],
                 label="admissible comparison  [r=(1,1,1,3), period=0]")
    print_case(a2)

    print()

    # Case 3: an asymmetric inadmissible case (one large debt)
    a3 = analyse(REGIONS, EDGES, FACES, [3, 0, 0, 0],
                 label="single-edge perturbation  [r=(3,0,0,0), period=-3]")
    print_case(a3)

    cert = {
        "theorem": "residue_admissibility_bridge",
        "statement": (
            "[r] = 0 in H^1  iff  exists global claim Phi with Phi_j - Phi_i = r_ij."
        ),
        "cases": [a1, a2, a3],
        "all_verified": all(c["theorem_verified"] for c in [a1, a2, a3]),
    }
    out = Path("certificates") / "admissibility_bridge_certificate.json"
    out.write_text(json.dumps(cert, indent=2))
    print(f"Certificate saved to: {out}")
    sys.exit(0 if cert["all_verified"] else 1)
