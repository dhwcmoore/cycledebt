# Frozen Result Manifest

Object: `actual_gluing_object_v1.json`

## Base classification

The finite regional residue classifier returns:

```text
classification: nontrivial_H1_obstruction
is_cocycle: true
is_coboundary: false
loop_sum: 1
```

Thus the residue (r) satisfies:

\[
r \in \ker \delta^1
\qquad
r \notin \operatorname{im}\delta^0.
\]

Hence:

\[
0 \neq [r] \in H^1.
\]

## Invariance tests

The obstruction verdict is stable under:

1. Region renaming
2. Orientation reversal
3. Non-zero rational scaling
4. Gauge perturbation by an exact coboundary
5. Edge reordering

## Refinement test

The obstruction survives the tested refinement in which (U_1) is subdivided into (U_{1a}) and (U_{1b}).

The refined object is again classified as:

```text
classification: nontrivial_H1_obstruction
refinement_claim: obstruction_survives_refinement
```

Therefore:

\[
0 \neq [\rho^\ast r] \in H^1(\mathfrak V).
\]

## Claim licensed by these files

The seam-supported residue is not a fragile artefact of presentation. It is a persistent finite regional obstruction relative to the declared cover, coefficient system, gauge freedom, and tested refinement.

## Strongest paper sentence licensed by the computation

The residue is not merely non-zero as a cochain; it represents a non-zero cohomology class that persists under the tested regional refinement.