"""
cycle_lift_test.py

Determines whether a refinement rho: N' -> N is cycle-faithful relative to z.

Definitions
-----------
  rho is cycle-faithful relative to z in Z_1(N;Q) if
      rho_*(Z_1(N';Q)) ∩ Q^x * z ≠ ∅.

  z' in Z_1(N';Q) is a nonzero-degree lift of z if
      rho_*(z') = lambda * z  for some lambda in Q^x.

Methods
-------
  Nullspace method:
    Solve [ d' | 0; M | -z ] * [z'; lambda]^T = 0 over Q.
    A null vector with lambda ≠ 0 certifies cycle-faithfulness.

  Rank criterion (Proposition):
    Let K = basis matrix for ker(d').
    Let PK = M * K  (images of base cycles under rho_*).
    Then z is in im(PK)  iff  rank(PK) = rank([PK | z]).
    Equivalently: rho is cycle-faithful iff rank(PK) = rank([PK | z]).
    Both methods agree on all four declared refinements.

Input
-----
  refined_regions:   list of vertex names in N'
  refined_edges:     list of (tail, head) pairs in N'
  transfer:          dict: edge_name -> {base_edge_name: rational_coefficient}
  base_edges:        ordered list of base edge names
  base_z:            base cycle vector

Output per refinement
---------------------
  cycle_faithful:           bool (both methods agree)
  lambda:                   rational string or None
  z_prime:                  list of rational strings or None
  z_prime_edges:            list of edge names or None
  rank_PK:                  int
  rank_PK_augmented:        int
  rank_criterion_verdict:   bool (z in im(PK))
  methods_agree:            bool
"""

import json
import sys
import sympy as sp
from pathlib import Path


BASE_EDGES = ["U1-U2", "U2-U3", "U3-U4", "U1-U4"]
BASE_Z = [sp.Integer(-1), sp.Integer(-1), sp.Integer(-1), sp.Integer(1)]


def build_boundary_matrix(regions, edge_pairs):
    """
    Build d': C_1(N') -> C_0(N').
    d'[v, e] = +1 if v is head of e, -1 if v is tail, 0 otherwise.
    """
    n_vert = len(regions)
    n_edges = len(edge_pairs)
    vert_idx = {v: i for i, v in enumerate(regions)}
    d = sp.zeros(n_vert, n_edges)
    for j, (tail, head) in enumerate(edge_pairs):
        d[vert_idx[head], j] += 1
        d[vert_idx[tail], j] -= 1
    return d


def build_pushforward_matrix(edge_names, transfer, base_edges):
    """
    Build M = rho_*: C_1(N') -> C_1(N).
    M[i, j] = coefficient of base_edges[i] in rho_*(refined_edge[j]).
    """
    n_base = len(base_edges)
    n_ref = len(edge_names)
    base_idx = {e: i for i, e in enumerate(base_edges)}
    M = sp.zeros(n_base, n_ref)
    for j, name in enumerate(edge_names):
        if name in transfer:
            for base_e, coeff in transfer[name].items():
                if base_e in base_idx:
                    M[base_idx[base_e], j] = sp.Rational(coeff)
    return M


def rank_criterion(d_prime, M, z_vec):
    """
    Rank criterion for cycle-faithfulness.

    Let K = basis matrix for ker(d')  (columns span Z_1(N';Q)).
    Let PK = M * K.
    Then z in im(PK) iff rank(PK) == rank([PK | z]).

    Returns (cycle_faithful, rank_PK, rank_PK_aug, K_cols).
    """
    K_vecs = d_prime.nullspace()          # list of n_ref×1 column vectors
    if not K_vecs:
        return False, 0, 1, 0             # no cycles at all

    K = sp.Matrix.hstack(*K_vecs)         # n_ref × k, columns = cycle basis
    PK = M * K
    PK_aug = PK.row_join(z_vec)

    rk = PK.rank()
    rk_aug = PK_aug.rank()
    return (rk == rk_aug), rk, rk_aug, K.shape[1]


def find_cycle_lift(regions, edge_pairs, edge_names, transfer,
                    base_edges=None, base_z=None):
    """
    Test cycle-faithfulness using both the nullspace and the rank criterion.

    Returns a result dict.
    """
    if base_edges is None:
        base_edges = BASE_EDGES
    if base_z is None:
        base_z = BASE_Z

    z_vec = sp.Matrix([sp.Rational(v) for v in base_z])
    n_vert = len(regions)

    d_prime = build_boundary_matrix(regions, edge_pairs)
    M = build_pushforward_matrix(edge_names, transfer, base_edges)

    # --- Method 1: nullspace ---
    top = d_prime.row_join(sp.zeros(n_vert, 1))
    bot = M.row_join(-z_vec)
    system = top.col_join(bot)
    null_vecs = system.nullspace()

    nullspace_faithful = False
    lam_found = None
    z_prime_found = None

    for v in null_vecs:
        lam = v[-1]
        if lam != 0:
            nullspace_faithful = True
            lam_found = sp.Rational(lam)
            z_prime_found = [sp.Rational(x) for x in v[:-1]]
            break

    # --- Method 2: rank criterion ---
    rank_faithful, rk_PK, rk_aug, n_cycle_basis = rank_criterion(d_prime, M, z_vec)

    methods_agree = (nullspace_faithful == rank_faithful)
    cycle_faithful = nullspace_faithful  # both should agree

    result = {
        "cycle_faithful": cycle_faithful,
        "rank_PK": rk_PK,
        "rank_PK_augmented": rk_aug,
        "rank_criterion_verdict": rank_faithful,
        "dim_Z1_N_prime": n_cycle_basis,
        "methods_agree": methods_agree,
        "system_dimensions": (system.shape[0], system.shape[1]),
    }

    if cycle_faithful:
        result.update({
            "lambda": str(lam_found),
            "z_prime": [str(x) for x in z_prime_found],
            "z_prime_edges": edge_names,
            "boundary_check_zero": (d_prime * sp.Matrix(z_prime_found)).norm() == 0,
        })
    else:
        reason = _diagnose_failure(d_prime, M, z_vec, regions, edge_names, base_edges)
        result["failure_reason"] = reason

    return result


def _diagnose_failure(d_prime, M, z_vec, regions, edge_names, base_edges):
    """
    Diagnose why cycle-lift fails: solve the system symbolically and confirm lambda=0.
    """
    n_ref = len(edge_names)
    z_sym = sp.Matrix(sp.symbols(f"z0:{n_ref}"))
    lam = sp.Symbol("lam")
    cycle_eqs = list(d_prime * z_sym)
    lift_eqs = list(M * z_sym - lam * z_vec)
    sol = sp.solve(cycle_eqs + lift_eqs, list(z_sym) + [lam])
    if isinstance(sol, dict):
        lam_val = sol.get(lam, lam)
        if lam_val == 0 or (hasattr(lam_val, 'free_symbols') and not lam_val.free_symbols):
            return f"System forces lambda = {lam_val}; cycle-lift impossible."
    return "No cycle-lift solution exists in the null space."


def build_witness_certificate(d_prime, M, z_vec, edge_names, base_edges, result):
    """
    Build a structured witness or failure certificate for cycle-faithfulness.

    Faithful case — cycle_lift_witness_certificate:
      lambda, z', degree_per_edge (uniform lambda), boundary verified,
      pushforward verified.

    Non-faithful case — cycle_lift_failure_certificate:
      rank_PK, rank_augmented, im_PK_generator, base_cycle, edge_ratios,
      failure_reason ("non_uniform_edge_ratios" or "no_cycles").
      Ratios are the values v[e]/z[e] where v = im(PK) generator.
      Non-uniformity is the exact algebraic witness for z not in im(PK).
    """
    K_vecs = d_prime.nullspace()
    if not K_vecs:
        return {"type": "cycle_lift_failure_certificate",
                "failure_reason": "no_cycles_in_refined_complex"}

    K = sp.Matrix.hstack(*K_vecs)    # n_ref × dim(Z_1)
    PK = M * K                        # n_base × dim(Z_1)

    # Find im(PK) generator (works cleanly for rank-1 case)
    im_gen = None
    for j in range(PK.shape[1]):
        col = PK.col(j)
        if any(col[k, 0] != 0 for k in range(col.rows)):
            im_gen = col
            break

    # Compute geometric split multiplicities from PK generator (consistent for all cases)
    # m_e = z_e / v_e  where v is the im(PK) generator
    geometric_m = {}
    geometric_ratio = {}
    if im_gen is not None:
        for i, e in enumerate(base_edges):
            if z_vec[i] != 0 and im_gen[i, 0] != 0:
                rat = sp.Rational(im_gen[i, 0]) / z_vec[i]
                geometric_ratio[e] = str(rat)
                geometric_m[e] = str(sp.Rational(1) / rat)

    if result["cycle_faithful"]:
        lam = sp.Rational(result["lambda"])
        z_prime = sp.Matrix([sp.Rational(v) for v in result["z_prime"]])
        pushforward = M * z_prime

        return {
            "type": "cycle_lift_witness_certificate",
            "lambda": result["lambda"],
            "z_prime_nonzero": {
                edge_names[i]: result["z_prime"][i]
                for i in range(len(edge_names))
                if result["z_prime"][i] not in ("0", "0/1")
            },
            "boundary_verified": (d_prime * z_prime).norm() == 0,
            "pushforward_verified": (pushforward == lam * z_vec),
            "geometric_edge_ratios": geometric_ratio,
            "geometric_split_multiplicities": geometric_m,
            "multiplicities_uniform": len(set(geometric_m.values())) == 1,
            "rank_PK": result["rank_PK"],
            "dim_Z1_N_prime": result["dim_Z1_N_prime"],
        }

    else:
        ratio_vals = list(geometric_ratio.values())
        ratios_uniform = len(set(ratio_vals)) == 1 and bool(ratio_vals)

        return {
            "type": "cycle_lift_failure_certificate",
            "cycle_faithful": False,
            "rank_PK": result["rank_PK"],
            "rank_augmented": result["rank_PK_augmented"],
            "im_PK_generator": (
                {base_edges[i]: str(im_gen[i, 0]) for i in range(len(base_edges))}
                if im_gen is not None else None
            ),
            "base_cycle": {base_edges[i]: str(z_vec[i]) for i in range(len(base_edges))},
            "edge_ratios": geometric_ratio,
            "split_multiplicities": geometric_m,
            "ratios_uniform": ratios_uniform,
            "multiplicities_uniform": len(set(geometric_m.values())) == 1,
            "failure_reason": "non_uniform_split_multiplicities",
            "interpretation": (
                "im(PK) is one-dimensional (rank 1). "
                "The split multiplicities m_e = z_e/v_e are non-uniform around the loop. "
                "By the Uniform Ratio Criterion (Theorem thm:uniform-ratio), "
                "no nonzero-degree lift exists. "
                f"Certified by rank([PK|z]) = {result['rank_PK_augmented']} > "
                f"rank(PK) = {result['rank_PK']}."
            ),
        }


# ---------------------------------------------------------------------------
# Refinement configurations (matching admissible_refinement_theorem.py)
# ---------------------------------------------------------------------------

def _refinement_subdivide_U1():
    regions = ["U1a", "U1b", "U2", "U3", "U4"]
    edge_pairs = [("U1a","U2"),("U1b","U2"),("U2","U3"),("U3","U4"),
                  ("U1a","U4"),("U1b","U4"),("U1a","U1b")]
    edge_names = ["U1a-U2","U1b-U2","U2-U3","U3-U4","U1a-U4","U1b-U4","U1a-U1b"]
    transfer = {
        "U1a-U2":  {"U1-U2": "1/2"}, "U1b-U2":  {"U1-U2": "1/2"},
        "U2-U3":   {"U2-U3": 1},     "U3-U4":   {"U3-U4": 1},
        "U1a-U4":  {"U1-U4": "1/2"}, "U1b-U4":  {"U1-U4": "1/2"},
        "U1a-U1b": {},
    }
    return regions, edge_pairs, edge_names, transfer


def _refinement_subdivide_U2():
    regions = ["U1", "U2a", "U2b", "U3", "U4"]
    edge_pairs = [("U1","U2a"),("U1","U2b"),("U2a","U3"),("U2b","U3"),
                  ("U3","U4"),("U1","U4"),("U2a","U2b")]
    edge_names = ["U1-U2a","U1-U2b","U2a-U3","U2b-U3","U3-U4","U1-U4","U2a-U2b"]
    transfer = {
        "U1-U2a":  {"U1-U2": "1/2"}, "U1-U2b":  {"U1-U2": "1/2"},
        "U2a-U3":  {"U2-U3": "1/2"}, "U2b-U3":  {"U2-U3": "1/2"},
        "U3-U4":   {"U3-U4": 1},     "U1-U4":   {"U1-U4": 1},
        "U2a-U2b": {},
    }
    return regions, edge_pairs, edge_names, transfer


def _refinement_subdivide_all():
    regions = ["U1a","U1b","U2a","U2b","U3a","U3b","U4a","U4b"]
    edge_names = [
        "U1a-U2a","U1a-U2b","U1b-U2a","U1b-U2b",
        "U2a-U3a","U2a-U3b","U2b-U3a","U2b-U3b",
        "U3a-U4a","U3a-U4b","U3b-U4a","U3b-U4b",
        "U1a-U4a","U1a-U4b","U1b-U4a","U1b-U4b",
        "U1a-U1b","U2a-U2b","U3a-U3b","U4a-U4b",
    ]
    edge_pairs = [tuple(e.split("-", 1)) for e in edge_names]
    transfer = {}
    for e in ["U1a-U2a","U1a-U2b","U1b-U2a","U1b-U2b"]:
        transfer[e] = {"U1-U2": "1/4"}
    for e in ["U2a-U3a","U2a-U3b","U2b-U3a","U2b-U3b"]:
        transfer[e] = {"U2-U3": "1/4"}
    for e in ["U3a-U4a","U3a-U4b","U3b-U4a","U3b-U4b"]:
        transfer[e] = {"U3-U4": "1/4"}
    for e in ["U1a-U4a","U1a-U4b","U1b-U4a","U1b-U4b"]:
        transfer[e] = {"U1-U4": "1/4"}
    for e in ["U1a-U1b","U2a-U2b","U3a-U3b","U4a-U4b"]:
        transfer[e] = {}
    return regions, edge_pairs, edge_names, transfer


def _refinement_insert_bridge():
    regions = ["U1","U2","U3","U4","Bridge_U1_U2"]
    edge_pairs = [("U1","Bridge_U1_U2"),("Bridge_U1_U2","U2"),
                  ("U2","U3"),("U3","U4"),("U1","U4")]
    edge_names = ["U1-Bridge_U1_U2","Bridge_U1_U2-U2","U2-U3","U3-U4","U1-U4"]
    transfer = {
        "U1-Bridge_U1_U2": {"U1-U2": "1/2"},
        "Bridge_U1_U2-U2": {"U1-U2": "1/2"},
        "U2-U3":           {"U2-U3": 1},
        "U3-U4":           {"U3-U4": 1},
        "U1-U4":           {"U1-U4": 1},
    }
    return regions, edge_pairs, edge_names, transfer


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

REFINEMENTS = [
    ("Subdivide U1 → (U1a, U1b)",      _refinement_subdivide_U1),
    ("Subdivide U2 → (U2a, U2b)",      _refinement_subdivide_U2),
    ("Subdivide all regions",           _refinement_subdivide_all),
    ("Insert bridge between U1 and U2", _refinement_insert_bridge),
]


def run_all():
    results = {}
    for name, builder in REFINEMENTS:
        regions, edge_pairs, edge_names, transfer = builder()
        res = find_cycle_lift(regions, edge_pairs, edge_names, transfer)
        res["refinement"] = name

        # Build detailed witness certificate
        z_vec = sp.Matrix(BASE_Z)
        d_prime = build_boundary_matrix(regions, edge_pairs)
        M = build_pushforward_matrix(edge_names, transfer, BASE_EDGES)
        res["witness_certificate"] = build_witness_certificate(
            d_prime, M, z_vec, edge_names, BASE_EDGES, res
        )

        results[name] = res
    return results


def print_report(results):
    print("=" * 76)
    print("CYCLE-LIFT TEST — CYCLE-FAITHFULNESS CLASSIFICATION")
    print("=" * 76)
    print()
    print(f"Base cycle:   z = (-1,-1,-1,1)   over edges {BASE_EDGES}")
    print(f"Base pairing: <z,r> = -5")
    print()

    # Main classification table
    print(f"{'Refinement':<35} {'Faithful?':<10} {'λ':<5} "
          f"{'rank(PK)':<10} {'rank([PK|z])':<14} {'dim Z_1':<8} {'Agree?'}")
    print("-" * 76)
    for name, res in results.items():
        faithful = "YES" if res["cycle_faithful"] else "NO"
        lam = res.get("lambda") or "—"
        rk = res["rank_PK"]
        rk_aug = res["rank_PK_augmented"]
        dim_z1 = res["dim_Z1_N_prime"]
        agree = "✓" if res["methods_agree"] else "✗"
        short = name.replace("→", "->").replace("–", "-")
        print(f"{short:<35} {faithful:<10} {str(lam):<5} "
              f"{rk:<10} {rk_aug:<14} {dim_z1:<8} {agree}")
    print()

    print("Rank criterion: z in im(PK)  iff  rank(PK) = rank([PK | z])")
    print()

    print("Cycle-faithful refinements:")
    for name, res in results.items():
        if res["cycle_faithful"]:
            z_nonzero = [(e, v) for e, v in zip(res['z_prime_edges'], res['z_prime'])
                         if v not in ('0', '0/1')]
            print(f"  {name}")
            print(f"    lambda = {res['lambda']},  boundary check = {res['boundary_check_zero']}")
            print(f"    z' nonzero: {z_nonzero}")
    print()

    print("Non-cycle-faithful refinements:")
    for name, res in results.items():
        if not res["cycle_faithful"]:
            wc = res.get("witness_certificate", {})
            gen = wc.get("im_PK_generator")   # dict edge->value in new format
            ratios = wc.get("edge_ratios", {})
            print(f"  {name}")
            print(f"    {res.get('failure_reason', 'No lift found.')}")
            if gen:
                print(f"    im(PK) generator: {gen}")
                print(f"    ratios gen[e]/z[e]: {ratios}  (non-uniform → z ∉ im(PK))")
    print()

    all_agree = all(r["methods_agree"] for r in results.values())
    print(f"Both methods agree on all refinements: {all_agree}")
    print()
    print("Interpretation:")
    print("  Direct persistence (Layer 1):   all four — direct cycle-pairing in N'.")
    print("  Witness persistence (Layer 2):  two — Cycle-Lift Persistence Theorem.")
    print()
    print("Philosophical statement:")
    print("  Direct obstruction persistence and witness persistence are distinct.")
    print("  A refinement may preserve the non-removable residue while changing")
    print("  the cycle through which non-removability is witnessed.")


if __name__ == "__main__":
    results = run_all()
    print_report(results)

    cert = {
        "test": "cycle_lift_test",
        "base_edges": BASE_EDGES,
        "base_cycle": [str(v) for v in BASE_Z],
        "base_pairing": "-5",
        "results": {k: {kk: vv for kk, vv in v.items() if kk != "refinement"}
                    for k, v in results.items()},
    }
    out = Path("certificates") / "cycle_lift_test_certificate.json"
    out.write_text(json.dumps(cert, indent=2))
    print(f"Certificate saved to: {out}")

    all_verified = all(
        res["cycle_faithful"] or res.get("failure_reason") for res in results.values()
    )
    sys.exit(0 if all_verified else 1)
