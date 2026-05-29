# Finite Regional Residue Obstruction Classifier

## Overview

This framework classifies seam residues in finite geometric constructions using Čech cohomology. It determines whether a residue is:
1. A **coherence failure** (δ¹r ≠ 0)
2. A **removable coboundary** (δ¹r = 0 and δ⁰b = r solvable)
3. A **nontrivial H¹ obstruction** (δ¹r = 0 and δ⁰b = r unsolvable)

## Quick Start

### Run classification on actual object:
```bash
python residue_test.py actual/actual_gluing_object_v1.json
```
Output: `certificates/actual_gluing_object_v1_certificate.json`

### Run all inline regression tests:
```bash
python residue_test.py
```
Displays three canonical examples (Examples A, B, C).

### Run invariance test suite:
```bash
python invariance_test.py actual/actual_gluing_object_v1.json
```
Output: `certificates/actual_gluing_object_v1_invariance_report.json`

### Run refinement invariance test:
```bash
python refinement_invariance_test.py actual/actual_gluing_object_v1.json
```
Output: `certificates/actual_gluing_object_v1_refinement_test_report.json`

## Workflow

### Stage 1: Classification
- **Input:** JSON file with regions, edges, faces, residue values
- **Process:** Apply two sequential tests (cocycle, then coboundary)
- **Output:** JSON certificate with classification and audit trail

### Stage 2: Invariance Testing
- **Tests:** 5 presentation transformations verified stable
  1. Region renaming (cosmetic)
  2. Edge orientation reversal (sign correction)
  3. Non-zero rational scaling
  4. Gauge perturbation (r' = r + δ⁰b)
  5. Edge order permutation
- **Output:** Invariance report with "stable_under_tested_presentations" claim

### Stage 3: Refinement Invariance Testing
- **Test:** Subdivide one region (U1 → U1a, U1b) with equal-distribution transfer map
- **Transfer map:** Old edge values split equally across refined edges; internal edge (U1a-U1b) gets value 0
- **Output:** Refinement report confirming obstruction persists in refined cover

## File Organization

```
residue_test.py                    # Classification engine
invariance_test.py                 # Invariance test suite (5 presentation tests)
refinement_invariance_test.py      # Refinement test (cover subdivision)
REFINEMENT_STRATEGY.py             # Transfer map strategy notes
PAPER_FORMULATION.py               # Paper-ready statement drafts

actual/
  actual_gluing_object_v1.json     # Your actual object

examples/
  loop_obstruction.json            # Example A: H¹ obstruction
  filled_triangle_coboundary.json  # Example B: removable
  invalid_cocycle.json             # Example C: coherence failure

certificates/
  *_certificate.json               # Classification certificates
  *_invariance_report.json         # Invariance test reports
  *_refinement_test_report.json    # Refinement test reports

invariance_tests/
  *.json                           # Variant input objects (renaming, scaling, etc.)

refinement_tests/
  *.json                           # Refined input objects (subdivided covers)
```

## JSON Input Format

```json
{
  "name": "object_name",
  "description": "...",
  "coefficient_domain": "Q",
  "regions": ["U1", "U2", "U3", "U4"],
  "edges": [
    ["U1", "U2"],
    ["U2", "U3"],
    ["U3", "U4"],
    ["U1", "U4"]
  ],
  "faces": [],
  "residue": {
    "U1-U2": "1",
    "U2-U3": "1",
    "U3-U4": "1",
    "U1-U4": "-2"
  }
}
```

## Certificate Format

```json
{
  "residue_degree": 1,
  "coefficient_domain": "Q",
  "is_cocycle": true,
  "is_coboundary": false,
  "classification": "nontrivial_H1_obstruction",
  "support": ["U1-U2", "U2-U3", "U3-U4", "U1-U4"],
  "residue_values": {...},
  "cohomology_summary": {
    "dim_C0": 4,
    "dim_C1": 4,
    "dim_C2": 0,
    "rank_delta0": 3,
    "rank_delta1": 0,
    "dim_kernel_delta1": 4,
    "dim_H1": 1
  },
  "witness": {
    "cocycle_test_passed": true,
    "coboundary_test_passed": false,
    "failed_linear_system": "D0 b = r has no solution; residue is forced.",
    "loop_sum": "1",
    "loop_obstruction_meaning": "Non-zero accumulation around loop..."
  },
  "cycle_witness": {
    "cycle_edges": ["U1-U2", "U2-U3", "U3-U4", "U1-U4"],
    "cycle_vector": ["1", "1", "1", "1"],
    "boundary_of_cycle": "0",
    "pairing_with_residue": "1",
    "conclusion": "residue_not_coboundary_by_nonzero_pairing"
  }
}
```

## Interpretation

### Nontrivial H¹ Obstruction (✓ Your result)
```
δ¹r = 0          (cocycle condition satisfied)
δ⁰b = r          (no solution exists)
```
**Meaning:** The residue is forced; it cannot be removed by re-choice of local representatives.

### Coboundary (Removable)
```
δ¹r = 0          (cocycle condition satisfied)
δ⁰b = r          (solution exists: b is the gauge correction)
```
**Meaning:** The residue is a presentation artefact. Apply b to trivialize it.

### Coherence Failure
```
δ¹r ≠ 0          (cocycle condition failed)
```
**Meaning:** The residue is not a degree-1 obstruction. The failure is at a higher level (degree 2 or above).

## Invariance Report

After `invariance_test.py` completes:
- All 5 tested transformations passed? → `"stable_under_tested_presentations"`
- Any test failed? → `"failed_some_invariance_tests"`

The report confirms the obstruction is not fragile under:
- Renaming regions
- Reversing edge orientations  
- Scaling by nonzero rationals
- Adding exact coboundaries
- Reordering edges

**Status:** Proven stable under tested re-presentations.

## Refinement Invariance Report

After `refinement_invariance_test.py` completes:
- `obstruction_persists: true` → obstruction survives cover subdivision
- Transfer map used: equal distribution (old edge values halved across refined edges)

The report confirms the obstruction is not an artefact of the coarse cover: splitting U1 into (U1a, U1b) leaves `[r]` non-zero in the refined nerve.

**Status:** Obstruction survives tested refinement.

## Key Results for Your Actual Object

```
Base Classification: nontrivial_H1_obstruction
├── is_cocycle: true
├── is_coboundary: false
└── loop_sum: 1

Invariance Testing: stable_under_tested_presentations
├── region_renaming: PASS
├── orientation_reversal: PASS
├── nonzero_rational_scaling: PASS
├── gauge_perturbation: PASS
└── edge_order_permutation: PASS

Refinement Testing: obstruction_survives_refinement
└── subdivide_U1_equal (U1 → U1a, U1b): PASS
    ├── refined regions: [U1a, U1b, U2, U3, U4]
    ├── refined edges: 7 (4 split + 2 from U1-U4 + 1 internal)
    ├── transfer map: equal distribution (r/2 per refined edge)
    └── refined classification: nontrivial_H1_obstruction
```

## Paper Statement

**After classification:**
> The finite construction produces a seam-supported residue whose cohomology class is non-zero; hence the defect is not removable by re-choice of local representatives.

**After invariance tests:**
> The obstruction is not an artefact of region naming, edge orientation, edge ordering, rational rescaling, or addition of exact gauge terms. Across these re-presentations, the classifier returns the same non-zero (H¹) verdict.

**After refinement test:**
> The non-zero cohomology class [r] persists when the regional cover is refined (U1 subdivided into U1a, U1b). This is strong evidence that the obstruction is intrinsic to the regional system and not an artefact of the coarse cover.

**After formal lemma:**
> Therefore the obstruction is invariant under the declared presentation equivalence and survives cover refinement.

## Technical Notes

- Exact rational arithmetic via SymPy (no floating-point errors)
- Proper sign conventions for oriented edges and faces
- Linear system solving for coboundary test
- Full audit trail in each certificate (no hidden assumptions)

## Next Steps

1. ~~**Refinement invariance**: Define transfer maps for subdivided covers~~ ✓ Done (equal-distribution transfer map, U1 subdivision)
2. **Additional refinement strategies**: Test other transfer maps (e.g., restriction maps, non-equal splits) and refine other regions
3. **Parameter stability**: Vary coefficient system, test persistence of obstruction
4. **Multiple actual objects**: Compare obstruction across different constructions
5. **Total complex variant**: Test against Hochschild/Gerstenhaber-Schack if applicable
