"""
Refinement invariance test for the finite regional residue obstruction.

Tests whether the obstruction class [r] survives when the regional cover
is refined. This is the final piece needed to claim intrinsicness.

Strategy:
  1. Subdivide one region (U1 → U1a, U1b)
  2. Define transfer map ρ*: C¹(𝔘) → C¹(𝔙) (equal distribution)
  3. Compute ρ*(r) on refined edges
  4. Test refined object: is [ρ*(r)] still nonzero?

Expected: nontrivial_H1_obstruction (obstruction persists)
"""

import json
import subprocess
import sympy as sp
from pathlib import Path
from residue_test import load_object_from_json, classify_residue, build_matrices


class RegionalRefinement:
    """
    Base class for refining a regional cover and testing obstruction persistence.
    """
    
    def __init__(self, base_object_file, refinement_type="subdivide_region_equally"):
        """
        Args:
            base_object_file: Path to JSON file with base object
            refinement_type: Type of refinement to apply
        """
        self.base_object_file = base_object_file
        self.refinement_type = refinement_type
        
        # Load base object
        with open(base_object_file, 'r') as f:
            self.base_object = json.load(f)
        
        self.base_regions, self.base_edges, self.base_faces, self.base_r_values, self.coeff_domain = \
            load_object_from_json(base_object_file)
    
    def subdivide_region_equally(self, region_to_split):
        """
        Subdivide one region into two subregions.
        Transfer: split edge values equally across refined edges.
        Internal edge: value 0.
        """
        refined_regions = []
        edge_map = {}  # old edge → list of (new_edge, multiplier)
        
        # Update regions
        for r in self.base_regions:
            if r == region_to_split:
                refined_regions.append(f"{r}a")
                refined_regions.append(f"{r}b")
            else:
                refined_regions.append(r)
        
        # Map old edges to refined edges
        refined_edges = []
        refined_r_values = []
        
        for edge, r_val in zip(self.base_edges, self.base_r_values):
            e1, e2 = edge
            
            if e1 == region_to_split:
                # Edge from split region to other region → two edges
                # e.g., U1-U2 becomes U1a-U2 and U1b-U2, each gets r_val/2
                refined_edges.append((f"{e1}a", e2))
                refined_edges.append((f"{e1}b", e2))
                refined_r_values.append(sp.Rational(r_val) / 2)
                refined_r_values.append(sp.Rational(r_val) / 2)
            
            elif e2 == region_to_split:
                # Edge from other region to split region → two edges
                refined_edges.append((e1, f"{e2}a"))
                refined_edges.append((e1, f"{e2}b"))
                refined_r_values.append(sp.Rational(r_val) / 2)
                refined_r_values.append(sp.Rational(r_val) / 2)
            
            else:
                # Edge between non-split regions → unchanged
                refined_edges.append(edge)
                refined_r_values.append(sp.Rational(r_val))
        
        # Add internal edge (subdivided region to itself) with value 0
        refined_edges.append((f"{region_to_split}a", f"{region_to_split}b"))
        refined_r_values.append(sp.Rational(0))
        
        # Faces: for now, none (your base object has no faces)
        refined_faces = self.base_faces  # Empty list
        
        return refined_regions, refined_edges, refined_faces, refined_r_values
    
    def subdivide_all_regions_equally(self):
        refined_regions = []
        for r in self.base_regions:
            refined_regions.extend([f"{r}a", f"{r}b"])
            
        refined_edges = []
        refined_r_values = []
        
        for edge, val in zip(self.base_edges, self.base_r_values):
            u, v = edge
            refined_edges.append((f"{u}a", f"{v}a"))
            refined_edges.append((f"{u}a", f"{v}b"))
            refined_edges.append((f"{u}b", f"{v}a"))
            refined_edges.append((f"{u}b", f"{v}b"))
            refined_r_values.extend([sp.Rational(val)/4]*4)
            
        for r in self.base_regions:
            refined_edges.append((f"{r}a", f"{r}b"))
            refined_r_values.append(sp.Rational(0))
            
        return refined_regions, refined_edges, self.base_faces, refined_r_values

    def insert_bridge_region(self, r1, r2):
        refined_regions = self.base_regions.copy()
        bridge = f"Bridge_{r1}_{r2}"
        refined_regions.append(bridge)
        
        refined_edges = []
        refined_r_values = []
        
        for edge, val in zip(self.base_edges, self.base_r_values):
            if set(edge) == {r1, r2}:
                if edge[0] == r1:
                    refined_edges.append((r1, bridge))
                    refined_edges.append((bridge, r2))
                else:
                    refined_edges.append((r2, bridge))
                    refined_edges.append((bridge, r1))
                refined_r_values.extend([sp.Rational(val)/2]*2)
            else:
                refined_edges.append(edge)
                refined_r_values.append(val)
                
        return refined_regions, refined_edges, self.base_faces, refined_r_values

    def build_refined_object(self):
        """Build the refined regional object."""
        if self.refinement_type == "subdivide_U1_equally":
            refined_regions, refined_edges, refined_faces, refined_r_values = \
                self.subdivide_region_equally("U1")
        elif self.refinement_type == "subdivide_U2_equally":
            refined_regions, refined_edges, refined_faces, refined_r_values = \
                self.subdivide_region_equally("U2")
        elif self.refinement_type == "subdivide_all_regions_equally":
            refined_regions, refined_edges, refined_faces, refined_r_values = \
                self.subdivide_all_regions_equally()
        elif self.refinement_type == "insert_bridge_U1_U2":
            refined_regions, refined_edges, refined_faces, refined_r_values = \
                self.insert_bridge_region("U1", "U2")
        else:
            raise ValueError(f"Unknown refinement type: {self.refinement_type}")
        
        # Build refined JSON object
        refined_object = {
            "name": f"{self.base_object['name']}_refined_{self.refinement_type}",
            "description": f"Refined by {self.refinement_type}: subdivided U1",
            "coefficient_domain": self.coeff_domain,
            "regions": refined_regions,
            "edges": refined_edges,
            "faces": refined_faces,
            "residue": {}
        }
        
        # Populate residue values
        for edge, val in zip(refined_edges, refined_r_values):
            key = f"{edge[0]}-{edge[1]}"
            refined_object["residue"][key] = str(val)
        
        return refined_object, refined_regions, refined_edges, refined_faces, refined_r_values
    
    def test_refinement(self):
        """Test whether obstruction survives refinement."""
        # Build refined object
        refined_object, refined_regions, refined_edges, refined_faces, refined_r_values = \
            self.build_refined_object()
        
        # Write to file
        refined_file = Path("refinement_tests") / f"{refined_object['name']}_input.json"
        Path("refinement_tests").mkdir(exist_ok=True)
        with open(refined_file, 'w') as f:
            json.dump(refined_object, f, indent=2)
        
        # Classify refined object
        refined_cert = classify_residue(refined_regions, refined_edges, refined_faces, 
                                       refined_r_values, self.coeff_domain)
        
        return {
            "refinement_type": self.refinement_type,
            "base_object": self.base_object["name"],
            "refined_object": refined_object["name"],
            "refined_nerve": {
                "regions": refined_regions,
                "edges": [f"{e[0]}-{e[1]}" for e in refined_edges],
                "faces": refined_faces,
                "num_edges": len(refined_edges)
            },
            "transfer_strategy": "equal_distribution",
            "transfer_map_description": (
                "Old edge values split equally across refined edges. "
                "Internal edges have value 0."
            ),
            "refined_residue_values": {
                f"{e[0]}-{e[1]}": str(v) for e, v in zip(refined_edges, refined_r_values)
            },
            "base_classification": self.base_object.get("base_classification", "nontrivial_H1_obstruction"),
            "refined_certificate": refined_cert,
            "refined_classification": refined_cert["classification"],
            "obstruction_persists": refined_cert["classification"] == "nontrivial_H1_obstruction"
        }


def run_refinement_tests(base_object_file):
    """Run refinement invariance tests."""
    print("=" * 80)
    print("REFINEMENT INVARIANCE TEST")
    print("=" * 80)
    print()
    
    # Load base object
    with open(base_object_file, 'r') as f:
        base_obj = json.load(f)
    
    print(f"Base object: {base_obj['name']}")
    print(f"Regions: {base_obj['regions']}")
    print(f"Edges: {[f'{e[0]}-{e[1]}' for e in base_obj['edges']]}")
    print(f"Residue: {base_obj['residue']}")
    print()
    
    results = {
        "base_object": base_obj["name"],
        "refinement_tests": {}
    }
    
    refinements_to_test = [
        ("TEST 1: Subdivide U1 → (U1a, U1b)", "subdivide_U1_equally"),
        ("TEST 2: Subdivide U2 → (U2a, U2b)", "subdivide_U2_equally"),
        ("TEST 3: Subdivide all regions", "subdivide_all_regions_equally"),
        ("TEST 4: Insert bridge region between U1 and U2", "insert_bridge_U1_U2")
    ]
    
    for test_name, ref_type in refinements_to_test:
        print(test_name)
        print("-" * 80)
        refiner = RegionalRefinement(base_object_file, ref_type)
        test_result = refiner.test_refinement()
        
        print(f"Refined nerve:")
        print(f"  Regions: {test_result['refined_nerve']['regions']}")
        print(f"  Edges: {test_result['refined_nerve']['edges']}")
        print()
        print(f"Refined classification: {test_result['refined_classification']}")
        
        if test_result["obstruction_persists"]:
            print("  ✓ OBSTRUCTION PERSISTS after refinement!")
            if "cycle_witness" in test_result["refined_certificate"]:
                pairing = test_result["refined_certificate"]["cycle_witness"]["pairing_with_residue"]
                print(f"  ✓ Refined cycle pairing: {pairing}")
        else:
            print("  ✗ Obstruction disappeared after refinement")
        
        print()
        results["refinement_tests"][ref_type] = test_result
    
    # Summary
    print("=" * 80)
    print("REFINEMENT TEST SUMMARY")
    print("=" * 80)
    print()
    
    all_passed = all(
        test["obstruction_persists"]
        for test in results["refinement_tests"].values()
    )
    
    if all_passed:
        results["refinement_claim"] = "obstruction_survives_refinement"
        print("✓ RESULT: Obstruction survives tested refinement(s)")
        print()
        print("Interpretation:")
        print("  The non-zero cohomology class [r] persists when the regional")
        print("  cover is refined. This is strong evidence that the obstruction")
        print("  is not an artefact of the coarse cover, but is intrinsic to")
        print("  the regional system.")
    else:
        results["refinement_claim"] = "obstruction_fragile_under_refinement"
        print("✗ RESULT: Obstruction is fragile under refinement")
        print()
        print("Interpretation:")
        print("  The obstruction did not survive when the cover was refined.")
        print("  This suggests the obstruction may depend on the choice of cover.")
        print("  Possible causes:")
        print("    1. Transfer map specification needs revision")
        print("    2. Obstruction is not intrinsic but cover-dependent")
        print("    3. Implementation error in refinement")
    
    print()
    print("=" * 80)
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        base_obj_file = sys.argv[1]
    else:
        base_obj_file = "actual/actual_gluing_object_v1.json"
    
    results = run_refinement_tests(base_obj_file)
    
    # Save results
    obj_name = Path(base_obj_file).stem
    report_file = Path("certificates") / f"{obj_name}_refinement_test_report.json"
    Path("certificates").mkdir(exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"Full report saved to: {report_file}")
