Title: Obstruction Persistence and Witness Failure in Finite Regional Cohomology

Abstract
--------
We present a finite cohomological obstruction classifier with machine‑readable
certificates for seam residues in finite regional covers. The framework
distinguishes direct obstruction persistence in refined nerves from witness
(cycle) persistence, and characterizes cycle‑faithfulness via rational rank
tests. We give algorithms to produce audit‑grade JSON certificates and
rank/failure witnesses, prove correctness of the tests, and demonstrate
persistence (or its certified failure) across several refinement strategies.
All code, inputs, and certificates are provided for full reproducibility.

Outline
-------
- Introduction
  - Motivation: seam residues, cohomological obstructions
  - Summary of contributions

- Background and notation
  - Finite nerves, cochains, coboundary operators
  - Definitions: cocycle, coboundary, H^1 class

- Classification algorithm
  - Cocycle test, coboundary linear system
  - Certificate format (JSON)

- Invariance under presentation
  - Permutations, orientation, scaling, gauge perturbation
  - Implementation details and proof sketches

- Refinements and transfer maps
  - Equal-distribution transfer and other strategies
  - Definitions: direct persistence vs witness persistence

- Cycle-faithfulness and rational rank tests
  - Nullspace formulation and rank criterion
  - Failure certificates and non-uniform ratio witnesses

- Experiments and certificates
  - Canonical examples (loop obstruction, coboundary, invalid cocycle)
  - Actual object: classification, invariance, refinements
  - Tables of rank results and pairings

- Discussion
  - Implications for persistence theory and computational topology
  - Open problems and conjectures (balanced loop refinement)

- Appendices
  - Proofs (formal statements from `PROOF.md`)
  - Reproducibility instructions
