"""
Invariance test suite for the residue obstruction classifier.

Tests whether the classification is stable under harmless re-presentations:
  1. Region renaming
  2. Edge orientation reversal
  3. Non-zero rational scaling
  4. Gauge perturbation by an exact coboundary
  5. Edge order permutation
  6. Refinement (pending: requires transfer map definition)

A passing invariance suite demonstrates that the obstruction is not an
artefact of arbitrary choices, but is stable under presentation changes.
"""

import json
import subprocess
import sympy as sp
from pathlib import Path
from residue_test import load_object_from_json, classify_residue, build_matrices


def generate_variant_region_renaming(base_obj):
    """Variant 1: Region renaming (cosmetic change)."""
    variant = base_obj.copy()
    variant["name"] = f"{base_obj['name']}_renamed"
    
    # Rename regions: U1 → A, U2 → B, U3 → C, U4 → D
    old_regions = variant["regions"]
    new_names = ["A", "B", "C", "D"][:len(old_regions)]
    rename_map = {old: new for old, new in zip(old_regions, new_names)}
    
    variant["regions"] = new_names
    variant["edges"] = [[rename_map[e[0]], rename_map[e[1]]] for e in variant["edges"]]
    variant["faces"] = [[rename_map[r] for r in f] for f in variant["faces"]]
    
    # Update residue keys
    new_residue = {}
    for edge_key, val in variant["residue"].items():
        # edge_key is like "U1-U2"
        parts = edge_key.split("-")
        if len(parts) == 2:
            new_e = f"{rename_map[parts[0]]}-{rename_map[parts[1]]}"
        else:
            new_e = edge_key
        new_residue[new_e] = val
    variant["residue"] = new_residue
    
    return variant


def generate_variant_edge_orientation_reversal(base_obj):
    """Variant 2: Reverse orientation of first edge and flip residue sign."""
    variant = base_obj.copy()
    variant["name"] = f"{base_obj['name']}_edge_reversed"
    
    # Reverse first edge
    if variant["edges"]:
        first_edge = variant["edges"][0]
        variant["edges"][0] = [first_edge[1], first_edge[0]]
        
        # Update residue: flip sign on reversed edge
        old_key = f"{first_edge[0]}-{first_edge[1]}"
        new_key = f"{first_edge[1]}-{first_edge[0]}"
        
        residue = variant["residue"]
        if old_key in residue:
            val = residue.pop(old_key)
            # Negate the value since we reversed the edge
            residue[new_key] = str(-sp.Rational(val))
        elif new_key in residue:
            val = residue[new_key]
            residue[new_key] = str(-sp.Rational(val))
    
    return variant


def generate_variant_nonzero_rational_scaling(base_obj, scale_factor=5):
    """Variant 3: Multiply all residues by nonzero rational."""
    variant = base_obj.copy()
    variant["name"] = f"{base_obj['name']}_scaled_by_{scale_factor}"
    
    new_residue = {}
    for key, val in variant["residue"].items():
        scaled = sp.Rational(val) * scale_factor
        new_residue[key] = str(scaled)
    variant["residue"] = new_residue
    
    return variant


def generate_variant_gauge_perturbation(base_obj, regions, edges, faces, r_values):
    """
    Variant 4: Add an exact coboundary δ⁰b to the residue.
    
    Choose a 0-cochain b = (1, 0, 0, 0), compute δ⁰b, and add to r.
    r' = r + δ⁰b  (in the same H¹ class, should give same classification)
    """
    variant = base_obj.copy()
    variant["name"] = f"{base_obj['name']}_gauge_perturbed"
    
    # Build D0 matrix
    D0, _ = build_matrices(regions, edges, faces)
    
    # Choose gauge: b = (1, 0, 0, ...)
    b = sp.zeros(len(regions), 1)
    b[0] = 1
    
    # Compute δ⁰b
    delta0_b = D0 * b
    
    # Add to residue: r' = r + δ⁰b
    r = sp.Matrix([sp.Rational(v) for v in r_values])
    r_prime = r + delta0_b
    
    # Update residue values
    new_residue = {}
    for (edge, val_prime) in zip(edges, r_prime):
        key = f"{edge[0]}-{edge[1]}"
        new_residue[key] = str(val_prime)
    variant["residue"] = new_residue
    
    return variant


def generate_variant_edge_order_permutation(base_obj):
    """Variant 5: Permute the edge list (reorder the 1-cochains)."""
    variant = base_obj.copy()
    variant["name"] = f"{base_obj['name']}_edges_permuted"
    
    # Rotate edges: move first edge to end
    if len(variant["edges"]) > 1:
        edges = variant["edges"]
        variant["edges"] = edges[1:] + [edges[0]]
        
        # Also rotate residue values correspondingly
        old_residue = variant["residue"]
        old_edges = base_obj["edges"]
        new_residue = {}
        
        for i, edge in enumerate(variant["edges"]):
            # This edge is at index i in the new list
            # Find which index it was at in the old list
            old_idx = old_edges.index(edge)
            # Get the old edge at position i
            old_edge_at_i = old_edges[i]
            old_key = f"{old_edge_at_i[0]}-{old_edge_at_i[1]}"
            if old_key in old_residue:
                val = old_residue[old_key]
            else:
                # Try reverse
                old_key_rev = f"{old_edge_at_i[1]}-{old_edge_at_i[0]}"
                val = old_residue.get(old_key_rev, "0")
            
            new_key = f"{edge[0]}-{edge[1]}"
            new_residue[new_key] = val
        
        variant["residue"] = new_residue
    
    return variant


def run_classifier_on_variant(variant_obj, output_dir):
    """
    Write variant to JSON file and run classifier.
    Return classification result.
    """
    # Write variant to file
    variant_name = variant_obj["name"]
    variant_file = Path(output_dir) / f"{variant_name}_input.json"
    with open(variant_file, 'w') as f:
        json.dump(variant_obj, f, indent=2)
    
    # Run classifier
    result = subprocess.run(
        ["python", "residue_test.py", str(variant_file)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    
    if result.returncode != 0:
        return {
            "error": result.stderr,
            "classification": None
        }
    
    # Extract certificate from output (last JSON object printed)
    lines = result.stdout.strip().split('\n')
    # Find the line that starts the JSON certificate
    cert_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith('"residue_degree"'):
            cert_start = i - 1
            break
    
    if cert_start is None:
        return {"error": "Could not find certificate in output", "classification": None}
    
    try:
        cert_json = '\n'.join(lines[cert_start:])
        # Find closing brace
        cert_json = cert_json[:cert_json.rfind('}') + 1]
        certificate = json.loads(cert_json)
        return {
            "classification": certificate.get("classification"),
            "is_cocycle": certificate.get("is_cocycle"),
            "is_coboundary": certificate.get("is_coboundary"),
            "certificate": certificate
        }
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {e}", "classification": None}


def run_invariance_tests(base_obj_file):
    """
    Run full invariance test suite.
    
    Returns a comprehensive report.
    """
    # Load base object
    regions, edges, faces, r_values, coeff_domain = load_object_from_json(base_obj_file)
    with open(base_obj_file, 'r') as f:
        base_obj = json.load(f)
    
    # Compute base classification
    base_cert = classify_residue(regions, edges, faces, r_values, coeff_domain)
    base_classification = base_cert["classification"]
    
    print("=" * 70)
    print("INVARIANCE TEST SUITE")
    print("=" * 70)
    print(f"\nBase object: {base_obj['name']}")
    print(f"Base classification: {base_classification}")
    print(f"Base is_cocycle: {base_cert['is_cocycle']}")
    print(f"Base is_coboundary: {base_cert['is_coboundary']}")
    print()
    
    # Create output directory
    output_dir = "invariance_tests"
    Path(output_dir).mkdir(exist_ok=True)
    
    results = {
        "base_object": base_obj["name"],
        "base_classification": base_classification,
        "base_is_cocycle": base_cert["is_cocycle"],
        "base_is_coboundary": base_cert["is_coboundary"],
        "invariance_tests": {}
    }
    
    # Test 1: Region renaming
    print("TEST 1: Region Renaming")
    print("-" * 70)
    variant = generate_variant_region_renaming(base_obj)
    result = run_classifier_on_variant(variant, output_dir)
    passed = result.get("classification") == base_classification
    results["invariance_tests"]["region_renaming"] = {
        "passed": passed,
        "classification": result.get("classification"),
        "error": result.get("error")
    }
    print(f"Result: {'PASS' if passed else 'FAIL'}")
    print(f"Classification: {result.get('classification')}")
    print()
    
    # Test 2: Edge orientation reversal
    print("TEST 2: Edge Orientation Reversal")
    print("-" * 70)
    variant = generate_variant_edge_orientation_reversal(base_obj)
    result = run_classifier_on_variant(variant, output_dir)
    passed = result.get("classification") == base_classification
    results["invariance_tests"]["orientation_reversal"] = {
        "passed": passed,
        "classification": result.get("classification"),
        "error": result.get("error")
    }
    print(f"Result: {'PASS' if passed else 'FAIL'}")
    print(f"Classification: {result.get('classification')}")
    print()
    
    # Test 3: Non-zero rational scaling
    print("TEST 3: Non-zero Rational Scaling (by 5)")
    print("-" * 70)
    variant = generate_variant_nonzero_rational_scaling(base_obj, scale_factor=5)
    result = run_classifier_on_variant(variant, output_dir)
    passed = result.get("classification") == base_classification
    results["invariance_tests"]["nonzero_rational_scaling"] = {
        "passed": passed,
        "classification": result.get("classification"),
        "error": result.get("error")
    }
    print(f"Result: {'PASS' if passed else 'FAIL'}")
    print(f"Classification: {result.get('classification')}")
    print()
    
    # Test 4: Gauge perturbation
    print("TEST 4: Gauge Perturbation (adding δ⁰b)")
    print("-" * 70)
    variant = generate_variant_gauge_perturbation(base_obj, regions, edges, faces, r_values)
    result = run_classifier_on_variant(variant, output_dir)
    passed = result.get("classification") == base_classification
    results["invariance_tests"]["gauge_perturbation"] = {
        "passed": passed,
        "classification": result.get("classification"),
        "error": result.get("error")
    }
    print(f"Result: {'PASS' if passed else 'FAIL'}")
    print(f"Classification: {result.get('classification')}")
    print()
    
    # Test 5: Edge order permutation
    print("TEST 5: Edge Order Permutation")
    print("-" * 70)
    variant = generate_variant_edge_order_permutation(base_obj)
    result = run_classifier_on_variant(variant, output_dir)
    passed = result.get("classification") == base_classification
    results["invariance_tests"]["edge_order_permutation"] = {
        "passed": passed,
        "classification": result.get("classification"),
        "error": result.get("error")
    }
    print(f"Result: {'PASS' if passed else 'FAIL'}")
    print(f"Classification: {result.get('classification')}")
    print()
    
    # Test 6: Refinement (pending)
    print("TEST 6: Refinement (PENDING)")
    print("-" * 70)
    print("Refinement invariance requires defining the transfer map from the")
    print("coarse to refined cover. This must be specified for each geometry.")
    print()
    results["invariance_tests"]["refinement"] = {
        "passed": None,
        "status": "pending",
        "reason": "Requires transfer map definition"
    }
    
    # Compute summary
    all_passed = all(
        v.get("passed") for k, v in results["invariance_tests"].items()
        if k != "refinement"
    )
    
    results["invariance_claim"] = (
        "stable_under_tested_presentations" if all_passed
        else "failed_some_invariance_tests"
    )
    
    # Print summary
    print("=" * 70)
    print("INVARIANCE TEST SUMMARY")
    print("=" * 70)
    for test_name, test_result in results["invariance_tests"].items():
        if test_name == "refinement":
            print(f"{test_name}: PENDING")
        else:
            status = "PASS" if test_result["passed"] else "FAIL"
            print(f"{test_name}: {status}")
    print()
    print(f"Overall claim: {results['invariance_claim']}")
    print()
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        base_obj_file = sys.argv[1]
    else:
        base_obj_file = "actual/actual_gluing_object_v1.json"
    
    results = run_invariance_tests(base_obj_file)
    
    # Save invariance report
    obj_name = Path(base_obj_file).stem
    report_file = Path("certificates") / f"{obj_name}_invariance_report.json"
    Path("certificates").mkdir(exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Full report saved to: {report_file}")

    if results.get("invariance_claim") != "stable_under_tested_presentations":
        sys.exit(1)
