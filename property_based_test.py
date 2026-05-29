"""
Property-based regression testing for finite regional residue classifier.

Tests that for random rational residues on a 4-cycle:
  <r, z> == 0  <==>  coboundary (removable)
  <r, z> != 0  <==>  nontrivial_H1_obstruction
"""

import random
import sympy as sp
from residue_test import classify_residue, build_matrices

def run_property_based_tests(iterations=1000):
    regions = ["U1", "U2", "U3", "U4"]
    edges = [("U1", "U2"), ("U2", "U3"), ("U3", "U4"), ("U1", "U4")]
    faces = []
    
    # Precompute the cycle vector for this specific edge orientation
    D0, _ = build_matrices(regions, edges, faces)
    Z1_basis = (D0.T).nullspace()
    z = Z1_basis[0] 
    
    passed = 0
    failed = 0
    
    for _ in range(iterations):
        # Generate random rational residues
        r_values = [
            sp.Rational(random.randint(-10, 10), random.choice([1, 2, 3, 4, 5]))
            for _ in range(4)
        ]
        
        # 50% chance to force it to be a coboundary
        if random.random() < 0.5:
            forced_r3 = -(z[0]*r_values[0] + z[1]*r_values[1] + z[2]*r_values[2]) / z[3]
            r_values[3] = forced_r3
            
        r = sp.Matrix(r_values)
        pairing = (z.T * r)[0]
        expected_class = "coboundary_removable" if pairing == 0 else "nontrivial_H1_obstruction"
        
        result = classify_residue(regions, edges, faces, r_values)
        actual_class = result["classification"]
        
        if actual_class == expected_class:
            passed += 1
        else:
            failed += 1
            
    print(f"Property-based tests completed: {passed} passed, {failed} failed.")
    return failed == 0

if __name__ == "__main__":
    success = run_property_based_tests()
    if not success:
        exit(1)