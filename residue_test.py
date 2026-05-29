import sympy as sp
import json
import sys
import os
from pathlib import Path


def load_object_from_json(filepath):
    """
    Load a finite regional object from JSON file.
    
    Expected structure:
    {
      "name": "...",
      "regions": ["U1", "U2", ...],
      "edges": [["U1", "U2"], ...],
      "faces": [["U1", "U2", "U3"], ...],
      "residue": {"U1-U2": "1", ...},
      "coefficient_domain": "Q"
    }
    """
    with open(filepath, 'r') as f:
        obj = json.load(f)
    
    regions = obj.get("regions", [])
    edges = obj.get("edges", [])
    faces = obj.get("faces", [])
    residue_dict = obj.get("residue", {})
    coeff_domain = obj.get("coefficient_domain", "Q")
    
    # Convert edges and faces to tuples
    edges = [tuple(e) for e in edges]
    faces = [tuple(f) for f in faces]
    
    # Extract residue values in edge order
    r_values = []
    for edge in edges:
        # Try both orderings
        key1 = f"{edge[0]}-{edge[1]}"
        key2 = f"{edge[1]}-{edge[0]}"
        if key1 in residue_dict:
            r_values.append(sp.Rational(residue_dict[key1]))
        elif key2 in residue_dict:
            r_values.append(sp.Rational(residue_dict[key2]))
        else:
            raise ValueError(f"No residue value found for edge {edge}")
    
    return regions, edges, faces, r_values, coeff_domain


def save_certificate(certificate, output_dir, name):
    """Save certificate JSON to file."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_file = Path(output_dir) / f"{name}_certificate.json"
    with open(output_file, 'w') as f:
        json.dump(certificate, f, indent=2)
    return str(output_file)


def build_matrices(regions, edges, faces):
    """Build the Cech coboundary matrices D0: C0->C1 and D1: C1->C2."""
    n0, n1, n2 = len(regions), len(edges), len(faces)

    D0 = sp.zeros(n1, n0)
    for row, (i, j) in enumerate(edges):
        D0[row, regions.index(i)] = -1
        D0[row, regions.index(j)] = 1

    D1 = sp.zeros(n2, n1)
    edge_index = {edge: k for k, edge in enumerate(edges)}

    def oriented_edge(a, b):
        # returns (canonical_edge, sign) where canonical form is (min, max)
        if a < b:
            return (a, b), 1
        else:
            return (b, a), -1

    for row, (i, j, k) in enumerate(faces):
        # (delta1 r)_{ijk} = r_{jk} - r_{ik} + r_{ij}
        for a, b, coeff in [(j, k, 1), (i, k, -1), (i, j, 1)]:
            edge, sign = oriented_edge(a, b)
            col = edge_index[edge]
            D1[row, col] += coeff * sign

    return D0, D1


def classify_residue(regions, edges, faces, r_values, coeff_domain="Q"):
    """
    Test whether a 1-cochain r is a cocycle and/or coboundary.

    Workflow (per finite regional cohomology):
      1. Test: Is δ¹r = 0?  (cocycle test)
         If no: coherence failure (not a degree-1 obstruction).
      2. Test: Does δ⁰b = r have a solution?  (coboundary test, only if cocycle)
         If yes: coboundary, removable by gauge choice.
         If no: genuine H¹ obstruction (forced, intrinsic).

    Returns a dict certificate with full audit trail.
    """
    r = sp.Matrix([sp.Rational(v) for v in r_values])

    D0, D1 = build_matrices(regions, edges, faces)

    # --- Cohomology dimensions and ranks ---
    n0, n1, n2 = len(regions), len(edges), len(faces)
    rank_D0 = D0.rank()
    rank_D1 = D1.rank() if n2 > 0 else 0
    ker_D1_dim = n1 - rank_D1
    H1_dim = ker_D1_dim - rank_D0

    # --- Test 1: cocycle test ---
    delta1_r = D1 * r
    is_cocycle = all(x == 0 for x in delta1_r)

    # --- Test 2: coboundary test (only meaningful if cocycle) ---
    b_syms = sp.symbols(f"b0:{len(regions)}")
    b = sp.Matrix(b_syms)
    equations = list(D0 * b - r)
    solution = sp.solve(equations, b_syms, dict=True)
    is_coboundary = len(solution) > 0

    if not is_cocycle:
        classification = "coherence_failure"
    elif is_coboundary:
        classification = "coboundary_removable"
    else:
        classification = "nontrivial_H1_obstruction"

    # Build witness data
    witness = {}
    if not is_cocycle:
        # Cocycle test failed: show the non-zero coboundary values
        witness["cocycle_test_failed"] = True
        witness["delta1_r"] = {
            str(faces[i]): str(delta1_r[i]) for i in range(len(faces))
        }
    elif is_coboundary:
        # Coboundary test succeeded: report gauge correction
        witness["cocycle_test_passed"] = True
        witness["coboundary_test_passed"] = True
        # Present the solution (may be parametric, which is fine)
        witness["gauge_correction"] = {
            f"b{regions[i]}": str(solution[0].get(b_syms[i], 0))
            for i in range(len(regions))
        }
        witness["gauge_correction_meaning"] = (
            "These local values can be added to each region to remove the residue."
        )
    else:
        # Coboundary test failed: genuine obstruction
        witness["cocycle_test_passed"] = True
        witness["coboundary_test_passed"] = False
        witness["failed_linear_system"] = "D0 b = r has no solution; residue is forced."
        # For a loop, the obstruction is the loop sum
        if len(faces) == 0:
            loop_sum = sum(r_values)
            witness["loop_sum"] = str(loop_sum)
            witness["loop_obstruction_meaning"] = (
                "Non-zero accumulation around loop; cannot be gauged away."
            )

    # --- Cycle pairing witness (positive obstruction proof) ---
    cycle_witness_dict = None
    if is_cocycle and not is_coboundary:
        Z1_basis = (D0.T).nullspace()
        for z in Z1_basis:
            pairing = (z.T * r)[0]
            if pairing != 0:
                cycle_edges_list = []
                for idx, val in enumerate(z):
                    if val != 0:
                        cycle_edges_list.append(f"{edges[idx][0]}-{edges[idx][1]}")
                cycle_witness_dict = {
                    "cycle_edges": cycle_edges_list,
                    "cycle_vector": [str(val) for val in z],
                    "boundary_of_cycle": "0",
                    "pairing_with_residue": str(pairing),
                    "conclusion": "residue_not_coboundary_by_nonzero_pairing"
                }
                break

    cohomology_summary = {
        "dim_C0": n0,
        "dim_C1": n1,
        "dim_C2": n2,
        "rank_delta0": rank_D0,
        "rank_delta1": rank_D1,
        "dim_kernel_delta1": ker_D1_dim,
        "dim_H1": H1_dim
    }

    result = {
        "residue_degree": 1,
        "coefficient_domain": coeff_domain,
        "is_cocycle": is_cocycle,
        "is_coboundary": is_coboundary,
        "classification": classification,
        "support": [f"{e[0]}-{e[1]}" for e in edges],
        "residue_values": {
            f"{e[0]}-{e[1]}": str(v)
            for e, v in zip(edges, r_values)
        },
        "cohomology_summary": cohomology_summary,
        "witness": witness,
    }

    if cycle_witness_dict:
        result["cycle_witness"] = cycle_witness_dict
        
    return result


def print_matrices(regions, edges, faces):
    D0, D1 = build_matrices(regions, edges, faces)
    print("D0 (delta^0: C^0 -> C^1):")
    sp.pprint(D0)
    print("\nD1 (delta^1: C^1 -> C^2):")
    sp.pprint(D1)


# ---------------------------------------------------------------------------
# Example A: loop with NO filled triple overlap
# Nerve: 0 - 1 - 2 - 3 - 0  (a 4-cycle, no 2-faces)
# Residue: (1, 1, 1, -2) -- loop sum = 1+1+1+(-2) = 1 != 0
# Expected: nontrivial H^1 obstruction
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Example A: loop with NO filled triple overlap
# Nerve: 0 - 1 - 2 - 3 - 0  (a 4-cycle, no 2-faces)
# Residue: (1, 1, 1, -2) -- loop sum = 1+1+1+(-2) = 1 != 0
# Expected: nontrivial H^1 obstruction
# ---------------------------------------------------------------------------

def run_inline_examples():
    """Run inline test examples (for regression testing)."""
    
    print("=" * 60)
    print("EXAMPLE A: loop nerve, no triple overlaps")
    print("=" * 60)

    regions_A = [0, 1, 2, 3]
    edges_A   = [(0, 1), (1, 2), (2, 3), (0, 3)]
    faces_A   = []
    r_A       = [1, 1, 1, -2]

    print_matrices(regions_A, edges_A, faces_A)
    result_A = classify_residue(regions_A, edges_A, faces_A, r_A)
    print("\nResult:")
    print(json.dumps(result_A, indent=2))


    # ---------------------------------------------------------------------------
    # Example B: filled triangle -- every cocycle is a coboundary
    # Nerve: 0 - 1 - 2  with triple overlap {0,1,2}
    # Residue: r12=1, r23=2, r13=3  (satisfies cocycle: r13 = r12 + r23)
    # Expected: coboundary_removable
    # ---------------------------------------------------------------------------

    print("\n" + "=" * 60)
    print("EXAMPLE B: filled triangle, cocycle that is a coboundary")
    print("=" * 60)

    regions_B = [0, 1, 2]
    edges_B   = [(0, 1), (1, 2), (0, 2)]
    faces_B   = [(0, 1, 2)]
    r_B       = [1, 2, 3]

    print_matrices(regions_B, edges_B, faces_B)
    result_B = classify_residue(regions_B, edges_B, faces_B, r_B)
    print("\nResult:")
    print(json.dumps(result_B, indent=2))


    # ---------------------------------------------------------------------------
    # Example C: coherence failure
    # Same triangle but residue violates the cocycle condition
    # r12=1, r23=2, r13=99  -- (delta1 r)_012 = 2 - 99 + 1 = -96 != 0
    # Expected: coherence_failure
    # ---------------------------------------------------------------------------

    print("\n" + "=" * 60)
    print("EXAMPLE C: coherence failure (residue is not a cocycle)")
    print("=" * 60)

    regions_C = [0, 1, 2]
    edges_C   = [(0, 1), (1, 2), (0, 2)]
    faces_C   = [(0, 1, 2)]
    r_C       = [1, 2, 99]

    print_matrices(regions_C, edges_C, faces_C)
    result_C = classify_residue(regions_C, edges_C, faces_C, r_C)
    print("\nResult:")
    print(json.dumps(result_C, indent=2))


    # ---------------------------------------------------------------------------
    # Interpretation Guide
    # ---------------------------------------------------------------------------

    print("\n" + "=" * 60)
    print("CLASSIFICATION SUMMARY")
    print("=" * 60)

    summary_text = """
Three possible outcomes for a residue r:

1. COHERENCE FAILURE (δ¹r ≠ 0):
   ───────────────────────────────
   The residue fails the cocycle condition.
   It is not a degree-1 obstruction, but indicates a coherence failure
   at a higher level (degree 2 or above).
   Action: The residue signals failure of gluing algebra, not descent.

2. COBOUNDARY / REMOVABLE (δ¹r = 0 AND δ⁰b = r solvable):
   ─────────────────────────────────────────────────────
   The residue is in the image of δ⁰.
   It can be removed by choosing different local representatives (gauge correction).
   The residue is a presentation artefact, not intrinsic.
   Action: Apply the gauge correction b to trivialize the residue.

3. NONTRIVIAL H¹ OBSTRUCTION (δ¹r = 0 AND δ⁰b = r unsolvable):
   ──────────────────────────────────────────────────────────
   The residue is a cocycle but not a coboundary.
   It represents a genuine, forced descent obstruction.
   It cannot be removed by any choice of local representatives.
   Action: The obstruction is intrinsic; reconciliation requires global modification.

The decisive fork (Section 15):
   δ¹r = 0  AND  D₀b = r has no solution
   ⟹ genuine H¹ obstruction.
"""

    print(summary_text)


# ---------------------------------------------------------------------------
# Main: Handle JSON input or run inline examples
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Load from JSON file
        input_file = sys.argv[1]
        
        try:
            regions, edges, faces, r_values, coeff_domain = load_object_from_json(input_file)
            
            print(f"Loaded: {input_file}")
            print(f"Regions: {regions}")
            print(f"Edges: {edges}")
            print(f"Faces: {faces}")
            print(f"Residue values: {r_values}")
            print()
            
            # Run classifier
            certificate = classify_residue(regions, edges, faces, r_values, coeff_domain)
            
            # Determine output filename
            obj_name = Path(input_file).stem  # filename without extension
            
            # Save certificate
            cert_file = save_certificate(certificate, "certificates", obj_name)
            
            # Print to stdout
            print("Certificate:")
            print(json.dumps(certificate, indent=2))
            print()
            print(f"Saved to: {cert_file}")
            
        except Exception as e:
            print(f"Error processing {input_file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Run inline examples
        run_inline_examples()
