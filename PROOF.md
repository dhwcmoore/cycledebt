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

## 4. Universal admissible refinement theorem

The following theorem gives a general sufficient condition for persistence
that subsumes the cycle-pairing argument.

**Theorem (Persistence under admissible refinement).**
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

Verification: `admissible_refinement_theorem.py`.

---

## 5. Scope of the proof

What is proved:

> The residue $r = (1,1,1,-2)$ on the declared finite nerve represents a nonzero $H^1$ class. This class is preserved under the five declared presentation changes and persists under the four declared refinement maps with equal-distribution transfer. For two of the four refinements (subdivide all, insert bridge), persistence follows from the Universal Admissible Refinement Theorem. For the remaining two (subdivide $U_1$, subdivide $U_2$), persistence is proved by the direct cycle-pairing lemma applied in the refined complex.

What is not yet proved:

> The obstruction persists under *all* admissible refinements.

A universal result requires identifying which refinements admit a nonzero
cycle-lift, and proving the lift exists.  The present paper does not claim
that theorem.  The declared finite tests constitute proved witnesses.

---

## 6. Certificate files

All computations above are certified by the files in `certificates/`:

| File | Content |
|---|---|
| `actual_gluing_object_v1_certificate.json` | Base classification and cycle witness |
| `actual_gluing_object_v1_invariance_report.json` | Five invariance tests |
| `actual_gluing_object_v1_refinement_test_report.json` | Four refinement tests with pairings |
| `admissible_refinement_theorem_certificate.json` | Theorem verification: adjointness, cycle-lift, proof method per refinement |

These files are frozen; see `MANIFEST.md` for the claim licensed by them.
