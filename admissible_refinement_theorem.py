"""
Cycle-Lift Persistence Theorem — verification script.

Theorem (Cycle-lift persistence):
  Let N be a finite oriented nerve and r in C^1(N;Q) a cocycle.
  Suppose z in Z_1(N;Q) with <z,r> != 0.
  Let rho: N' -> N be a refinement with maps
      rho*: C^1(N;Q) -> C^1(N';Q)   (cochain pullback)
      rho_*: C_1(N';Q) -> C_1(N;Q) (chain pushforward, adjoint to rho*)
  satisfying:
      <z', rho*(alpha)> = <rho_*(z'), alpha>  for all z', alpha   [adjointness]
  If there exists a refined cycle z' in Z_1(N';Q) and nonzero lambda in Q* with
      rho_*(z') = lambda * z                                       [cycle-lift]
  then
      [rho*(r)] != 0 in H^1(N';Q).

Proof sketch:
  Assume rho*(r) = delta'^0 b'. Since z' is a cycle, partial'z' = 0, so
      <z', rho*(r)> = <z', delta'^0 b'> = <partial'z', b'> = 0.
  But by adjointness and cycle-lift:
      <z', rho*(r)> = <rho_*(z'), r> = <lambda*z, r> = lambda*<z,r> != 0.
  Contradiction.

This script:
  1. Builds rho* (pullback) and rho_* = (rho*)^T (pushforward) for each refinement.
  2. Verifies the adjointness identity (automatic by construction).
  3. Tests the cycle-lift condition rho_*(z') = lambda*z.
  4. Classifies each refinement: THEOREM or DIRECT_PAIRING.
  5. Emits a machine-readable certificate.
"""

import json
import sys
import sympy as sp
from fractions import Fraction
from pathlib import Path


BASE_EDGES = ["U1-U2", "U2-U3", "U3-U4", "U1-U4"]
BASE_R = [sp.Integer(1), sp.Integer(1), sp.Integer(1), sp.Integer(-2)]
BASE_Z = [sp.Integer(-1), sp.Integer(-1), sp.Integer(-1), sp.Integer(1)]


def build_matrices(refined_edges, transfer):
    """
    Build rho* (pullback, n_ref x n_base) and rho_* (pushforward, n_base x n_ref).

    transfer: dict  refined_edge_name -> {base_edge_name: rational_coefficient}
    """
    n_base = len(BASE_EDGES)
    n_ref = len(refined_edges)
    base_idx = {e: i for i, e in enumerate(BASE_EDGES)}
    ref_idx = {e: i for i, e in enumerate(refined_edges)}

    rho_star = sp.zeros(n_ref, n_base)
    for e_ref, mapping in transfer.items():
        i = ref_idx[e_ref]
        for e_base, coeff in mapping.items():
            j = base_idx[e_base]
            rho_star[i, j] = sp.Rational(coeff)

    rho_push = rho_star.T
    return rho_star, rho_push


def check_cycle_lift(rho_push, z_prime):
    """
    Check if rho_*(z') = lambda * z for some nonzero lambda in Q*.
    Returns (True, lambda) or (False, None).
    """
    z = sp.Matrix(BASE_Z)
    pz = rho_push * sp.Matrix([sp.Rational(v) for v in z_prime])

    # All-zero pushforward cannot satisfy cycle-lift (lambda must be nonzero)
    if pz == sp.zeros(len(BASE_EDGES), 1):
        return False, None

    lambdas = []
    for i in range(len(BASE_EDGES)):
        if z[i] == 0:
            if pz[i] != 0:
                return False, None
        else:
            lambdas.append(sp.Rational(pz[i]) / z[i])

    if len(set(lambdas)) == 1 and lambdas[0] != 0:
        return True, lambdas[0]
    return False, None


def verify_refinement(name, refined_edges, transfer, z_prime_vals, r_prime_vals):
    """
    Full verification for one refinement.
    Returns a result dict.
    """
    rho_star, rho_push = build_matrices(refined_edges, transfer)

    z = sp.Matrix(BASE_Z)
    r = sp.Matrix(BASE_R)
    z_prime = sp.Matrix([sp.Rational(v) for v in z_prime_vals])
    r_prime = sp.Matrix([sp.Rational(v) for v in r_prime_vals])

    # Verify rho*(r) matches the supplied r_prime
    rho_star_r = rho_star * r
    pullback_matches = (rho_star_r == r_prime)

    # Adjointness: <z', rho*(r)> == <rho_*(z'), r>
    lhs = z_prime.dot(rho_star_r)
    rho_push_z = rho_push * z_prime
    rhs = rho_push_z.dot(r)
    adjoint_ok = (lhs == rhs)

    # Direct pairing
    direct_pairing = z_prime.dot(r_prime)

    # Cycle-lift
    lift_ok, lam = check_cycle_lift(rho_push, z_prime_vals)

    if lift_ok:
        proof_method = "universal_theorem"
        theorem_pairing = lam * z.dot(r)
        assert theorem_pairing == direct_pairing, (
            f"Theorem pairing {theorem_pairing} != direct {direct_pairing}"
        )
    else:
        proof_method = "direct_cycle_pairing"
        lam = None
        theorem_pairing = None

    return {
        "refinement": name,
        "n_refined_edges": len(refined_edges),
        "pullback_matches_r_prime": bool(pullback_matches),
        "adjointness_holds": bool(adjoint_ok),
        "rho_push_z_prime": [str(x) for x in rho_push_z],
        "cycle_lift_holds": lift_ok,
        "lambda": str(lam) if lam is not None else None,
        "direct_pairing": str(direct_pairing),
        "theorem_pairing": str(theorem_pairing) if theorem_pairing is not None else None,
        "obstruction_persists": direct_pairing != 0,
        "proof_method": proof_method,
    }


def run_all():
    results = {}

    # --- Refinement 1: Subdivide U1 ---
    r1_edges = ["U1a-U2", "U1b-U2", "U2-U3", "U3-U4", "U1a-U4", "U1b-U4", "U1a-U1b"]
    r1_transfer = {
        "U1a-U2":  {"U1-U2": "1/2"},
        "U1b-U2":  {"U1-U2": "1/2"},
        "U2-U3":   {"U2-U3": 1},
        "U3-U4":   {"U3-U4": 1},
        "U1a-U4":  {"U1-U4": "1/2"},
        "U1b-U4":  {"U1-U4": "1/2"},
        "U1a-U1b": {},
    }
    r1_z = ["-1", "0", "-1", "-1", "1", "0", "0"]
    r1_r = ["1/2", "1/2", "1", "1", "-1", "-1", "0"]
    results["subdivide_U1"] = verify_refinement(
        "Subdivide U1 → (U1a, U1b)", r1_edges, r1_transfer, r1_z, r1_r
    )

    # --- Refinement 2: Subdivide U2 ---
    r2_edges = ["U1-U2a", "U1-U2b", "U2a-U3", "U2b-U3", "U3-U4", "U1-U4", "U2a-U2b"]
    r2_transfer = {
        "U1-U2a":  {"U1-U2": "1/2"},
        "U1-U2b":  {"U1-U2": "1/2"},
        "U2a-U3":  {"U2-U3": "1/2"},
        "U2b-U3":  {"U2-U3": "1/2"},
        "U3-U4":   {"U3-U4": 1},
        "U1-U4":   {"U1-U4": 1},
        "U2a-U2b": {},
    }
    r2_z = ["-1", "0", "-1", "0", "-1", "1", "0"]
    r2_r = ["1/2", "1/2", "1/2", "1/2", "1", "-2", "0"]
    results["subdivide_U2"] = verify_refinement(
        "Subdivide U2 → (U2a, U2b)", r2_edges, r2_transfer, r2_z, r2_r
    )

    # --- Refinement 3: Subdivide all regions ---
    r3_edges = [
        "U1a-U2a", "U1a-U2b", "U1b-U2a", "U1b-U2b",
        "U2a-U3a", "U2a-U3b", "U2b-U3a", "U2b-U3b",
        "U3a-U4a", "U3a-U4b", "U3b-U4a", "U3b-U4b",
        "U1a-U4a", "U1a-U4b", "U1b-U4a", "U1b-U4b",
        "U1a-U1b", "U2a-U2b", "U3a-U3b", "U4a-U4b",
    ]
    r3_transfer = {}
    for e in ["U1a-U2a", "U1a-U2b", "U1b-U2a", "U1b-U2b"]:
        r3_transfer[e] = {"U1-U2": "1/4"}
    for e in ["U2a-U3a", "U2a-U3b", "U2b-U3a", "U2b-U3b"]:
        r3_transfer[e] = {"U2-U3": "1/4"}
    for e in ["U3a-U4a", "U3a-U4b", "U3b-U4a", "U3b-U4b"]:
        r3_transfer[e] = {"U3-U4": "1/4"}
    for e in ["U1a-U4a", "U1a-U4b", "U1b-U4a", "U1b-U4b"]:
        r3_transfer[e] = {"U1-U4": "1/4"}
    for e in ["U1a-U1b", "U2a-U2b", "U3a-U3b", "U4a-U4b"]:
        r3_transfer[e] = {}
    r3_z = ["-1","0","0","0","-1","0","0","0","-1","0","0","0","1","0","0","0","0","0","0","0"]
    r3_r = ["1/4","1/4","1/4","1/4","1/4","1/4","1/4","1/4","1/4","1/4","1/4","1/4",
            "-1/2","-1/2","-1/2","-1/2","0","0","0","0"]
    results["subdivide_all"] = verify_refinement(
        "Subdivide all regions", r3_edges, r3_transfer, r3_z, r3_r
    )

    # --- Refinement 4: Insert bridge ---
    r4_edges = ["U1-Bridge_U1_U2", "Bridge_U1_U2-U2", "U2-U3", "U3-U4", "U1-U4"]
    r4_transfer = {
        "U1-Bridge_U1_U2": {"U1-U2": "1/2"},
        "Bridge_U1_U2-U2": {"U1-U2": "1/2"},
        "U2-U3":           {"U2-U3": 1},
        "U3-U4":           {"U3-U4": 1},
        "U1-U4":           {"U1-U4": 1},
    }
    r4_z = ["-1", "-1", "-1", "-1", "1"]
    r4_r = ["1/2", "1/2", "1", "1", "-2"]
    results["insert_bridge"] = verify_refinement(
        "Insert bridge between U1 and U2", r4_edges, r4_transfer, r4_z, r4_r
    )

    return results


def print_report(results):
    print("=" * 72)
    print("UNIVERSAL ADMISSIBLE REFINEMENT THEOREM — VERIFICATION REPORT")
    print("=" * 72)
    print()
    print(f"Base residue:  r = (1, 1, 1, -2)")
    print(f"Base cycle:    z = (-1,-1,-1, 1)")
    print(f"Base pairing:  <z,r> = -5")
    print()
    print(f"{'Refinement':<30} {'dim C1':<8} {'Lift?':<6} {'lambda':<8} "
          f"{'Pairing':<10} {'Method'}")
    print("-" * 72)
    for key, res in results.items():
        lift = "YES" if res["cycle_lift_holds"] else "NO"
        lam = res["lambda"] if res["lambda"] else "—"
        method = "Theorem" if res["proof_method"] == "universal_theorem" else "Direct"
        print(f"{res['refinement']:<30} {res['n_refined_edges']:<8} {lift:<6} "
              f"{lam:<8} {res['direct_pairing']:<10} {method}")
    print()
    print("All adjointness conditions hold:", all(r["adjointness_holds"] for r in results.values()))
    print("All obstructions persist:        ", all(r["obstruction_persists"] for r in results.values()))
    print()
    print("Notes:")
    print("  Subdivide U1 / U2: cycle-lift IMPOSSIBLE for equal-distribution transfer.")
    print("  The flow-conservation equation at the junction vertex forces")
    print("  rho_*(z')[U_src-U_split] = (1/2)*rho_*(z')[U_split-U_next],")
    print("  breaking proportionality with z. Proved by direct cycle-pairing.")
    print()
    print("  Subdivide all / Insert bridge: cycle-lift holds.")
    print("  Universal Theorem applies; pairing = lambda * <z,r> = lambda * (-5).")


if __name__ == "__main__":
    results = run_all()
    print_report(results)

    cert = {
        "theorem": "universal_admissible_refinement",
        "base_object": "actual_gluing_object_v1",
        "base_pairing": "-5",
        "base_cycle": ["-1", "-1", "-1", "1"],
        "refinement_results": results,
    }
    out = Path("certificates") / "cycle_lift_persistence_certificate.json"
    out.write_text(json.dumps(cert, indent=2))
    print(f"\nCertificate saved to: {out}")

    all_ok = all(r["obstruction_persists"] for r in results.values())
    sys.exit(0 if all_ok else 1)
