# Results

This repository contains a finite regional residue obstruction classifier and a worked obstruction example.

## Main object

The actual object is:

```text
actual/actual_gluing_object_v1.json
```

It has four regions:

```text
U1, U2, U3, U4
```

and four declared overlaps:

```text
U1-U2, U2-U3, U3-U4, U1-U4
```

The residue is:

```text
r = (1, 1, 1, -2)
```

over the coefficient field $\mathbb Q$.

## Base obstruction result

The classifier returns:

```text
classification: nontrivial_H1_obstruction
is_cocycle: true
is_coboundary: false
dim_H1: 1
```

Thus the residue satisfies:

\[
r \in \ker \delta^1
\]

and

\[
r \notin \operatorname{im}\delta^0.
\]

Therefore:

\[
0 \neq [r] \in H^1.
\]

The primary proof witness is the cycle pairing:

\[
z=(-1,-1,-1,1)
\]

with

\[
\langle z,r\rangle=-5.
\]

Since every coboundary pairs to zero with every cycle, this nonzero pairing proves that $r$ is not a coboundary.

## Presentation invariance

The obstruction verdict is stable under the declared presentation changes:

1. region renaming;
2. edge orientation reversal;
3. nonzero rational scaling;
4. gauge perturbation by an exact coboundary;
5. edge ordering permutation.

These are either invertible changes of presentation or exact translations, so they do not remove the cohomology class.

## Refinement persistence

The obstruction persists under the four declared refinement witnesses:

| Refinement                                    | Verdict                       | Pairing |
| --------------------------------------------- | ----------------------------- | ------: |
| subdivide $U_1$                               | nontrivial $H^1$ obstruction  |  $-7/2$ |
| subdivide $U_2$                               | nontrivial $H^1$ obstruction  |    $-4$ |
| subdivide all regions                         | nontrivial $H^1$ obstruction  |  $-5/4$ |
| insert bridge region between $U_1$ and $U_2$ | nontrivial $H^1$ obstruction  |    $-5$ |

Each refinement is certified by an explicit nonzero cycle pairing.

## Property-based regression

The property-based regression test runs 1000 random rational residues on the four-cycle and checks the classifier against the cycle-pairing criterion.

The current run passes:

```text
1000 passed, 0 failed
```

## Scope

The repository proves persistence for the declared object, presentation transformations, and refinement witnesses.

It does not yet prove persistence under all possible refinements.

A universal refinement theorem would require a general admissible-refinement class and a pairing-preservation diagram of the form:

\[
\langle z',\rho^\ast r\rangle
=
\langle \rho_\ast z',r\rangle.
\]
