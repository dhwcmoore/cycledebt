# Proof of Non-Removability of the Seam Residue

## Object

Finite nerve $N$ with regions $U_1, U_2, U_3, U_4$ and oriented edges

$$
U_1U_2,\quad U_2U_3,\quad U_3U_4,\quad U_1U_4.
$$

No 2-simplices: $C^2 = 0$.

Cochain complex over $\mathbb{Q}$:

$$
C^0 = \mathbb{Q}^4
\xrightarrow{\delta^0}
C^1 = \mathbb{Q}^4
\xrightarrow{\delta^1 = 0}
0.
$$

Residue:

$$
r = (1,\,1,\,1,\,-2) \in C^1.
$$

---

## Theorem (Finite cohomology classifier)

Let $C^0 \xrightarrow{\delta^0} C^1 \xrightarrow{\delta^1} C^2$ be a finite cochain complex over $\mathbb{Q}$.
For $r \in C^1$:

$$
[r] \neq 0 \in H^1
\quad\Longleftrightarrow\quad
\delta^1 r = 0
\;\text{ and }\;
r \notin \operatorname{im}\delta^0.
$$

*This is the definition of cohomology* $H^1 = \ker\delta^1 / \operatorname{im}\delta^0$. No experiment is needed for this step.

---

## 1. Base obstruction

**Proposition.** $0 \neq [r] \in H^1(N;\mathbb{Q})$.

**Proof.**

Since $C^2 = 0$, we have $\delta^1 = 0$, so $\delta^1 r = 0$ trivially. It remains to show $r \notin \operatorname{im}\delta^0$.

The coboundary matrix, with columns indexed by regions and rows by edges, is:

$$
\delta^0 =
\begin{pmatrix}
-1 & 1 & 0 & 0 \\
0 & -1 & 1 & 0 \\
0 & 0 & -1 & 1 \\
-1 & 0 & 0 & 1
\end{pmatrix}.
$$

That is, $(\delta^0 b)_e = b_j - b_i$ for oriented edge $U_iU_j$.

Suppose for contradiction that $\delta^0 b = r$ for some $b = (b_1, b_2, b_3, b_4)$. Then:

$$
b_2 - b_1 = 1, \qquad b_3 - b_2 = 1, \qquad b_4 - b_3 = 1.
$$

Adding: $b_4 - b_1 = 3$.

But the fourth row requires $b_4 - b_1 = -2$. Contradiction. $\square$

### Cycle witness (independent positive proof)

The same fact follows from the cycle-pairing duality without solving any linear system.

The vector $z = (-1,-1,-1,1)$ satisfies $\delta^{0,T} z = 0$, i.e., it is a cycle ($\partial z = 0$). Computing:

$$
\langle z, r \rangle
= (-1)(1) + (-1)(1) + (-1)(1) + (1)(-2)
= -5.
$$

If $r = \delta^0 b$ were a coboundary, then:

$$
\langle z, r \rangle = \langle z, \delta^0 b \rangle = \langle \delta^{0,T} z, b \rangle = \langle 0, b \rangle = 0.
$$

Since $\langle z, r \rangle = -5 \neq 0$, we conclude $r \notin \operatorname{im}\delta^0$. $\square$

The cycle witness is the stronger proof artifact: it is a single rational computation that certifies non-coboundary status without solving a linear system.

---

## 2. Presentation invariance

**Claim.** The verdict $[r] \neq 0$ is stable under the following presentation changes:

| Change | Algebraic action |
|---|---|
| Region renaming | Permutation on $C^0$ and $C^1$ |
| Edge reordering | Permutation on $C^1$ |
| Edge orientation reversal | Diagonal $\pm 1$ matrix on $C^1$ |
| Nonzero rational scaling | $r \mapsto \lambda r$, $\lambda \in \mathbb{Q}^\times$ |
| Gauge perturbation | $r \mapsto r + \delta^0 b$ |

**Proof.**

Each of the first four changes is an invertible change of coordinates inducing an isomorphism of cochain complexes. An isomorphism sends nonzero classes to nonzero classes.

For gauge perturbation:

$$
[r + \delta^0 b] = [r] + [\delta^0 b] = [r] + 0 = [r].
$$

The class is exactly preserved, not merely replaced by another nonzero class. $\square$

The invariance test suite (`invariance_test.py`) verifies that the classifier implementation respects these identities for the declared cases.

---

## 3. Refinement persistence (proved for declared refinements)

**Lemma (cycle witness for refinement).** Let

$$
\rho^*: C^1(N;\mathbb{Q}) \to C^1(N';\mathbb{Q})
$$

be a transfer map and let $r' = \rho^* r$. If there exists a cycle $z' \in C_1(N';\mathbb{Q})$ with $\partial z' = 0$ and $\langle z', r' \rangle \neq 0$, then $[r'] \neq 0 \in H^1(N';\mathbb{Q})$.

**Proof.** Assume for contradiction that $r' = \delta'^0 b$ for some $b \in C'^0$. Then:

$$
\langle z', r' \rangle = \langle z', \delta'^0 b \rangle = \langle \partial z', b \rangle = 0.
$$

This contradicts $\langle z', r' \rangle \neq 0$. $\square$

### Refinement witnesses

The four declared refinement maps all use equal-distribution transfer ($r'_e = r_e / k$ across $k$ refined edges replacing one base edge, internal edges zero). The cycle witness test (`refinement_invariance_test.py`) computes:

| Refinement | $\dim C'^0$ | $\dim C'^1$ | $\langle z', r' \rangle$ | Verdict |
|---|---|---|---|---|
| Subdivide $U_1 \to (U_{1a}, U_{1b})$ | 5 | 7 | $-7/2$ | $[r'] \neq 0$ |
| Subdivide $U_2 \to (U_{2a}, U_{2b})$ | 5 | 7 | $-4$ | $[r'] \neq 0$ |
| Subdivide all regions | 8 | 20 | $-5/4$ | $[r'] \neq 0$ |
| Insert bridge between $U_1$ and $U_2$ | 5 | 5 | $-5$ | $[r'] \neq 0$ |

Each nonzero pairing constitutes a proof, by the lemma above, that the transferred residue is not a coboundary in the refined complex.

---

## 4. Cycle-Lift Persistence Theorem

**Definition (Nonzero-degree lift of a cycle).**
Let $z \in Z_1(N;\mathbb Q)$. A cycle $z' \in Z_1(N';\mathbb Q)$ is a
*nonzero-degree lift of $z$* if there exists $\lambda \in \mathbb Q^\times$
such that $\rho_* z' = \lambda z$.

**Definition (Cycle-faithful refinement).**
Let $z \in Z_1(N;\mathbb Q)$. A refinement $\rho: N' \to N$ equipped with
a chain pushforward $\rho_*: C_1(N';\mathbb Q) \to C_1(N;\mathbb Q)$ is
*cycle-faithful relative to $z$* if $z$ admits a nonzero-degree lift, i.e.,
$$
\rho_*(Z_1(N';\mathbb Q)) \cap \mathbb Q^\times z \neq \varnothing.
$$

Cycle-faithfulness has two equivalent computational formulations:

1. **Nullspace method.** Solve $[\partial' \mid 0;\, \rho_* \mid {-z}] \cdot [z';\lambda]^T = 0$
   over $\mathbb Q$. A null vector with $\lambda \neq 0$ certifies faithfulness;
   if only $\lambda = 0$ appears, the system proves faithfulness impossible.

2. **Rank criterion.** Let $K$ be a basis matrix for $\ker \partial' = Z_1(N';\mathbb Q)$
   and $P = \rho_*$. Then $\rho$ is cycle-faithful relative to $z$ iff
   $$
   \operatorname{rank}(PK) = \operatorname{rank}([PK \;\; z]).
   $$

Both methods agree on all four declared refinements (verified in `cycle_lift_test.py`).

---

The following theorem gives a general sufficient condition for persistence.

**Theorem (Cycle-lift persistence).**
Let $N$ be a finite oriented nerve and $r \in C^1(N;\mathbb Q)$ a cocycle.
Suppose $z \in Z_1(N;\mathbb Q)$ with $\langle z, r \rangle \neq 0$.
Let $\rho: N' \to N$ be a refinement equipped with maps
$$
\rho^*: C^1(N;\mathbb Q) \to C^1(N';\mathbb Q),
\qquad
\rho_*: C_1(N';\mathbb Q) \to C_1(N;\mathbb Q),
$$
satisfying the adjointness condition
$$
\langle z', \rho^* \alpha \rangle = \langle \rho_* z', \alpha \rangle
$$
for all $z' \in C_1(N';\mathbb Q)$ and $\alpha \in C^1(N;\mathbb Q)$.

If there exists a refined cycle $z' \in Z_1(N';\mathbb Q)$ and a nonzero rational
$\lambda \in \mathbb Q^\times$ such that
$$
\rho_* z' = \lambda z,
$$
then $[\rho^* r] \neq 0 \in H^1(N';\mathbb Q)$.

**Proof.**
Assume for contradiction that $\rho^* r = \delta'^0 b'$ for some $b' \in C^0(N';\mathbb Q)$.
Since $z'$ is a cycle, $\partial' z' = 0$, so
$$
\langle z', \rho^* r \rangle = \langle z', \delta'^0 b' \rangle = \langle \partial' z', b' \rangle = 0.
$$
But by adjointness and the cycle-lift condition,
$$
\langle z', \rho^* r \rangle = \langle \rho_* z', r \rangle = \langle \lambda z, r \rangle = \lambda \langle z, r \rangle.
$$
Since $\lambda \neq 0$ and $\langle z, r \rangle \neq 0$, this is nonzero. Contradiction. $\square$

### Which refinements satisfy the theorem hypotheses

The adjointness condition holds automatically for all four refinements, because
$\rho_*$ is defined as the transpose of $\rho^*$.  The cycle-lift condition
$\rho_* z' = \lambda z$ holds for two of the four:

| Refinement | $\dim C'^1$ | Cycle-lift | $\lambda$ | $\langle z', r' \rangle$ | Proof method |
|---|---|---|---|---|---|
| Subdivide $U_1$ | 7 | NO | — | $-7/2$ | Direct pairing |
| Subdivide $U_2$ | 7 | NO | — | $-4$ | Direct pairing |
| Subdivide all regions | 20 | **YES** | $1/4$ | $-5/4 = \lambda \cdot (-5)$ | **Theorem** |
| Insert bridge $U_1$–$U_2$ | 5 | **YES** | $1$ | $-5 = \lambda \cdot (-5)$ | **Theorem** |

For **subdivide all regions**: $\rho_* z' = \tfrac{1}{4} z$, so the theorem gives
$\langle z', \rho^* r \rangle = \tfrac{1}{4} \cdot (-5) = -\tfrac{5}{4} \neq 0$.

For **insert bridge**: $\rho_* z' = z$, so $\langle z', \rho^* r \rangle = 1 \cdot (-5) = -5 \neq 0$.

For **subdivide $U_1$** and **subdivide $U_2$**: the cycle-lift condition is
*impossible* for equal-distribution transfer on a single region.
The flow-conservation equation at the junction vertex forces
$\rho_*(z')[e_{\rm in}] = \tfrac{1}{2} \rho_*(z')[e_{\rm out}]$,
which breaks proportionality with $z$ unless $\lambda = 0$.
These two refinements are therefore proved by the direct cycle-pairing
lemma applied in $N'$, not by this theorem.

Cycle-faithfulness is verified by `cycle_lift_test.py`, which solves the
linear system over $\mathbb Q$ and proves algebraically that subdivide-$U_1$
and subdivide-$U_2$ force $\lambda = 0$ (impossible).

---

## 5. Rank criterion and classification table

The rank criterion gives a clean algebraic read-out for each refinement.

**Notation.** $B' = $ boundary matrix of $N'$; $P = \rho_*$; $K = $ basis for $\ker B'$.

| Refinement | $\dim Z_1(N')$ | $\operatorname{rank}(PK)$ | $\operatorname{rank}([PK\;z])$ | Cycle-faithful |
|---|---|---|---|---|
| Subdivide $U_1$ | 3 | 1 | 2 | No |
| Subdivide $U_2$ | 3 | 1 | 2 | No |
| Subdivide all regions | 13 | 1 | 1 | Yes |
| Insert bridge $U_1$–$U_2$ | 1 | 1 | 1 | Yes |

For the non-faithful cases, $\operatorname{rank}(PK) = 1$ but $z \notin \operatorname{im}(PK)$:
the image of $Z_1(N')$ under $\rho_*$ is a one-dimensional subspace of $C_1(N;\mathbb Q)$
that does not contain $z$.

## 6. Why single-region subdivisions fail cycle-faithfulness

For subdivide-$U_1$ with equal-distribution transfer, the junction vertex $U_2$
(an original vertex of $N$, still present in $N'$) has two new incoming edges
$U_{1a}$-$U_2$ and $U_{1b}$-$U_2$ where previously there was only $U_1$-$U_2$.
The cycle conservation law at $U_2$ in $N'$ forces:
$$
z'(U_{1a}\text{-}U_2) + z'(U_{1b}\text{-}U_2) = z'(U_2\text{-}U_3).
$$
The pushforward gives $\rho_*(z')[U_1\text{-}U_2] = \tfrac{1}{2}(z'(U_{1a}\text{-}U_2) + z'(U_{1b}\text{-}U_2))$.
For $\rho_*(z') = \lambda z$, we need $\rho_*(z')[U_1\text{-}U_2] = \rho_*(z')[U_2\text{-}U_3]$.
But flow conservation gives $\rho_*(z')[U_1\text{-}U_2] = \tfrac{1}{2}\rho_*(z')[U_2\text{-}U_3]$.
So $\rho_*(z')[U_2\text{-}U_3] = \tfrac{1}{2}\rho_*(z')[U_2\text{-}U_3]$, forcing
$\rho_*(z')[U_2\text{-}U_3] = 0$, hence $\lambda = 0$.

The cycle-faithful refinements (subdivide-all, insert-bridge) avoid this because
they either eliminate the original junction vertex ($U_2 \to U_{2a}, U_{2b}$) or
replace $U_1$-$U_2$ with a *path* through a new vertex (Bridge), preserving
flow balance without multiplying the parallel edges at the original vertex.

**Definition (Cycle-covering refinement).**
A refinement $\rho: N' \to N$ is *cycle-covering relative to $z$* if there exists
a subcomplex $L' \subseteq N'$ and $z' \in Z_1(L';\mathbb Q)$ such that
$\rho_* z' = \lambda z$ for some $\lambda \in \mathbb Q^\times$.

**Theorem (Cycle-covering refinements are cycle-faithful).**
Every cycle-covering refinement relative to $z$ is cycle-faithful. *(Proof:
cycle-covering directly supplies the nonzero-degree lift.)*

**Theorem (Uniform loop subdivision).**
Let $z$ be a simple rational cycle. Suppose $\rho$ replaces each edge of $z$
by a nonempty oriented path $\Pi(e)$ and these paths chain into a closed loop
$z'$. If the pushforward degree $\rho_*(z')[e] / z(e)$ is the same
$\lambda \in \mathbb Q^\times$ for all edges $e$ of $z$, then $\rho$ is
cycle-faithful relative to $z$.

*Proof.* The chaining condition gives $\partial' z' = 0$. The uniform degree
condition gives $\rho_*(z') = \lambda z$. $\square$

**Why single-region subdivisions fail the uniform degree condition.**

For subdivide-$U_1$, the im(PK) generator is $(-\tfrac{1}{2}, -1, -1, \tfrac{1}{2})$.
The ratio generator[e]/z[e] is $\tfrac{1}{2}$ for the split edges ($U_1U_2, U_1U_4$)
and $1$ for the unchanged edges ($U_2U_3, U_3U_4$). Non-uniform. Therefore
$z \notin \operatorname{im}(PK)$ and $\operatorname{rank}([PK\,z])=2$.

For subdivide-$U_2$, the generator is $(-\tfrac{1}{2}, -\tfrac{1}{2}, -1, 1)$
with ratio $\tfrac{1}{2}$ on $U_1U_2, U_2U_3$ and $1$ on $U_3U_4, U_1U_4$.
Same non-uniformity pattern.

**Complete classification table:**

| Refinement | Direct persistence | Cycle-faithful | Degree $\lambda$ | Reason |
|---|---|---|---|---|
| Subdivide $U_1$ | Yes | No | — | cycle image line misses $z$ |
| Subdivide $U_2$ | Yes | No | — | cycle image line misses $z$ |
| Subdivide all | Yes | Yes | $1/4$ | uniform diagonal loop |
| Insert bridge | Yes | Yes | $1$ | preserved serial loop |

---

**Conjecture (Balanced cycle-fibre).**
Let $z$ be a simple rational cycle in a finite oriented nerve $N$.
Let $\rho: N' \to N$ be a refinement equipped with a chain pushforward $\rho_*$.
Suppose the full preimage of the support of $z$ contains a divergence-free
rational circulation whose pushforward crosses every edge of $z$ with the
same nonzero rational degree. Then $\rho$ is cycle-faithful relative to $z$.

---

## 7. Scope of the proof

What is proved:

> The residue $r = (1,1,1,-2)$ on the declared finite nerve represents a nonzero $H^1$ class. This class is preserved under the five declared presentation changes and persists under the four declared refinement maps with equal-distribution transfer. For two of the four refinements (subdivide all, insert bridge), persistence follows from the Cycle-Lift Persistence Theorem. For the remaining two (subdivide $U_1$, subdivide $U_2$), cycle-faithfulness is algebraically impossible for equal-distribution transfer; persistence is proved by the direct cycle-pairing lemma applied in the refined complex.

What is not yet proved:

> A characterisation of all cycle-faithful refinements, or a proof of the Balanced Loop Refinement Conjecture.

---

## 8. Two-layer interpretation

Refinement persistence has two layers:

1. **Direct obstruction persistence.** There exists a refined cycle $z'$ in $N'$
   with $\langle z', \rho^* r \rangle \neq 0$. All four declared refinements
   satisfy this. This is proved by the Cycle-Pairing Certificate Lemma.

2. **Witness persistence (cycle-faithfulness).** The original obstruction cycle $z$
   admits a nonzero rational lift $z'$ in $N'$ via the pushforward. Two of the four
   declared refinements satisfy this. When it holds, persistence follows from the
   Cycle-Lift Persistence Theorem without computing a new cycle.

The first can hold even when the second fails.

---

## 9. Certificate files

All computations above are certified by the files in `certificates/`:

| File | Content |
|---|---|
| `actual_gluing_object_v1_certificate.json` | Base classification and cycle witness |
| `actual_gluing_object_v1_invariance_report.json` | Five invariance tests |
| `actual_gluing_object_v1_refinement_test_report.json` | Four refinement tests with direct pairings |
| `admissible_refinement_theorem_certificate.json` | Adjointness and cycle-lift check for each refinement |
| `cycle_lift_test_certificate.json` | Linear-system proof of cycle-faithfulness / impossibility |

These files are frozen; see `MANIFEST.md` for the claim licensed by them.
