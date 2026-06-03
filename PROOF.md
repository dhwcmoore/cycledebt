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

## 0. General Finite Regional Obstruction Theorem

This section states and proves the general theory. Sections 1–2 are corollaries
for the specific four-region loop nerve.

### §0a. Finite Graph Period Classification Theorem

**Setup.** Let $G = (V, E)$ be a finite connected oriented graph. The cochain
complex over $\mathbb{Q}$ is:
$$
C^0(G;\mathbb{Q}) = \mathbb{Q}^{|V|}
\xrightarrow{\delta^0}
C^1(G;\mathbb{Q}) = \mathbb{Q}^{|E|}
\xrightarrow{0} 0.
$$
Every $r \in C^1$ is automatically a cocycle. The cycle space
$Z_1(G;\mathbb{Q}) = \ker((\delta^0)^T)$ and the cut space $\operatorname{im}\delta^0$
are orthogonal complements in $C^1$ with respect to the standard inner product.

**Theorem (Finite Graph Period Classification).** For $r \in C^1(G;\mathbb{Q})$,
the following four conditions are equivalent:

1. **Gauge-admissible:** $\exists\, b \in C^0$ with $\delta^0 b = r$.
2. **Globally consistent:** $\exists\, \Phi$ with $\Phi_j - \Phi_i = r_{ij}$ at every overlap.
3. **Zero cycle pairings:** $\langle z, r\rangle = 0$ for every $z \in Z_1(G;\mathbb{Q})$.
4. **Cohomologically trivial:** $[r] = 0 \in H^1(G;\mathbb{Q})$.

**Proof.**

$(1) \Leftrightarrow (4)$: Definition of $H^1 = C^1/\operatorname{im}\delta^0$.

$(1) \Leftrightarrow (2)$: Proved in §11b (the Residue-Admissibility Bridge Theorem).

$(1) \Rightarrow (3)$: If $r = \delta^0 b$ then
$\langle z, r\rangle = \langle (\delta^0)^T z, b\rangle = \langle 0, b\rangle = 0$
for every $z \in Z_1 = \ker((\delta^0)^T)$.

$(3) \Rightarrow (1)$: We show $\operatorname{im}\delta^0 = Z_1^\perp$.

Dimension count for connected $G$:
$$
\dim Z_1 = |E| - |V| + 1, \qquad
\dim\operatorname{im}\delta^0 = \operatorname{rank}(\delta^0) = |V| - 1.
$$
(The rank is $|V|-1$ because $\ker\delta^0 = \mathbb{Q}$, the constant functions.)

Sum: $(|E| - |V| + 1) + (|V| - 1) = |E| = \dim C^1$.

By $(1)\Rightarrow(3)$, $\operatorname{im}\delta^0 \subseteq Z_1^\perp$. Since both sides
have dimension $|V|-1$ and $|E|-(|V|-1) = |E|-|V|+1 = \dim Z_1$, they are equal:
$$
\operatorname{im}\delta^0 = Z_1^\perp.
$$
Therefore $r \perp Z_1$ implies $r \in Z_1^\perp = \operatorname{im}\delta^0$. $\square$

**Corollary (Cycle-period criterion).**
$$
[r] \neq 0 \quad\Longleftrightarrow\quad \exists\, z \in Z_1 \text{ with } \langle z,r\rangle \neq 0.
$$

**Dimension and structure.** For a connected graph $G$:
$$
\dim H^1(G;\mathbb{Q}) = |E| - |V| + 1 = \text{circuit rank of } G.
$$

| Graph | $H^1$ | Obstruction space |
|---|---|---|
| Path or tree | $0$ | Every residue removable |
| $n$-cycle | $\mathbb{Q}$ | One invariant: the circulation |
| 4-cycle + chord | $\mathbb{Q}^2$ | Two independent pairings |
| Complete $K_4$ | $\mathbb{Q}^3$ | Three independent pairings |

Verified on seven graph types by `general_obstruction_classifier.py`.

### §0b. Nerve Extension (Simplicial Complexes with Faces)

For a simplicial complex $N$ with 2-faces, the cochain complex extends:
$$
C^0(N;\mathbb{Q}) \xrightarrow{\delta^0} C^1(N;\mathbb{Q}) \xrightarrow{\delta^1} C^2(N;\mathbb{Q}).
$$
A residue $r$ now requires the cocycle condition $\delta^1 r = 0$ to represent
an $H^1$ class. The obstruction group is:
$$
H^1(N;\mathbb{Q}) = \ker(\delta^1) / \operatorname{im}(\delta^0).
$$

**Hodge decomposition.** The Hodge Laplacian on $C^1$ is:
$$
L_1 = \delta^0 (\delta^0)^T + (\delta^1)^T \delta^1 \;:\; C^1 \to C^1.
$$
Its kernel is the space of **harmonic 1-cochains**:
$$
\mathcal{H}^1 = \ker(L_1) = \ker((\delta^0)^T) \cap \ker(\delta^1).
$$
The orthogonal decomposition $C^1 = \operatorname{im}\delta^0 \oplus \mathcal{H}^1 \oplus \operatorname{im}((\delta^1)^T)$
gives a canonical isomorphism $H^1(N;\mathbb{Q}) \cong \mathcal{H}^1$.

**Theorem (Nerve Extension).** For $r \in \ker(\delta^1)$ (a cocycle):
$$
[r] = 0 \in H^1(N;\mathbb{Q})
\quad\Longleftrightarrow\quad
\langle h, r\rangle = 0 \text{ for every harmonic } h \in \mathcal{H}^1.
$$

*Proof.* The same dimension argument applies within $\ker(\delta^1)$: $\mathcal{H}^1$
is the orthogonal complement of $\operatorname{im}\delta^0$ inside $\ker(\delta^1)$. $\square$

**Consequence for warrant debt.** The general debt formula $D(r) = p(r)^T G^{-1} p(r)$
uses the harmonic basis $\{h_1, \ldots, h_k\}$ for $\mathcal{H}^1$:
$$
p_i(r) = \langle h_i, r\rangle, \qquad G_{ij} = \langle h_i, h_j\rangle.
$$
For graphs ($\delta^1 = 0$), $\mathcal{H}^1 = Z_1$ and this reduces to the Gram matrix
formula in §11d.

Verified on graphs (four-cycle, diamond, $K_4$) and nerves (filled triangle,
four-cycle minus face) by `finite_nerve_warrant_debt.py`.

### §0c. Finite Nerve Warrant Debt Theorem (Capstone)

This collects §0a, §0b, and the bridge theorem (§11b) into a single statement.

**Theorem (Finite Nerve Warrant Debt).** Let $N$ be a finite nerve over $\mathbb{Q}$,
with cochain complex $C^0 \xrightarrow{\delta^0} C^1 \xrightarrow{\delta^1} C^2$.
Let $r \in C^1(N;\mathbb{Q})$ be a seam residue. Define $D(r) = \|P_{\mathcal{H}^1} r\|^2$
(standard inner product, harmonic projection via $L_1$). Then:

| Certificate output | Mathematical fact | Theorem |
|---|---|---|
| $\delta^1 r \neq 0$ | Local coherence fails; $H^1$ question does not arise | computation |
| $\delta^1 r = 0$, $D(r) = 0$ | $[r] = 0 \in H^1$; globally consistent claim exists | §0b + §11b |
| $\delta^1 r = 0$, $D(r) > 0$ | $[r] \neq 0 \in H^1$; warrant debt, no global claim | §0b + §11b |

**Soundness.** The engine `finite_nerve_warrant_debt.py` computes exactly these three cases.
Its output is formally accountable: each case directly corresponds to a proved theorem.

**Precision (when $D_\mathrm{gram} = D_\mathrm{harmonic}$).**
The Gram formula $D = p^T G^{-1} p$ agrees with the harmonic projection formula
$D = \|P_{\mathcal{H}^1} r\|^2$ **if and only if** the period basis $\{h_i\}$ spans
the correct obstruction space $\mathcal{H}^1 = \ker(L_1)$.

Using raw graph-cycle vectors without accounting for faces gives incorrect results
for nerves. Example: a filled triangle has $\ker(L_1) = \{0\}$ (the face kills the
apparent graph cycle), so $D = 0$ for any cocycle. A naive graph-cycle computation
using the boundary vector $z$ would give $\langle z, r\rangle = \delta^1 r = 0$
for any cocycle — which also gives zero — but this coincidence holds only because
$z$ is itself the face boundary. For more complex nerves where graph cycles are
partially killed by faces, naive cycle-pairing can give wrong answers. The Hodge
Laplacian implementation is the safe canonical choice.

---

## 1. Complete Four-Cycle Classification Theorem

*This section is a corollary of §0a: the four-region loop nerve is the case
where $Z_1$ is one-dimensional, generated by $z = (-1,-1,-1,1)$, so the cycle
period is a single number $q(r) = \langle z, r\rangle$.*

**Theorem (Complete four-cycle $H^1$ classifier).** For the four-region loop
nerve $N$ with the coboundary matrix $\delta^0$ defined above, the *circulation
functional*
$$
q(a,b,c,d) \;=\; -a - b - c + d \;=\; \langle z, r\rangle, \quad z = (-1,-1,-1,1),
$$
is the complete invariant of the cohomology class: for any residue
$r = (a,b,c,d) \in C^1$,
$$
[r] = 0 \in H^1(N;\mathbb{Q})
\quad\Longleftrightarrow\quad
-a - b - c + d = 0.
$$

**Proof.** $(\Rightarrow)$ If $r = \delta^0 b$ then $\langle z, r\rangle =
\langle \delta^{0,T}z, b\rangle = \langle 0, b\rangle = 0$, so $q(r) = 0$.

$(\Leftarrow)$ Suppose $q(r) = 0$, i.e., $d = a + b + c$. Set
$$
b^* = \bigl(0,\; a,\; a+b,\; a+b+c\bigr).
$$
Then $(\delta^0 b^*)_e = b^*_j - b^*_i$ for each oriented edge $U_iU_j$:
$$
b^*_2 - b^*_1 = a,\quad
b^*_3 - b^*_2 = b,\quad
b^*_4 - b^*_3 = c,\quad
b^*_4 - b^*_1 = a+b+c = d.
$$
So $\delta^0 b^* = (a,b,c,d) = r$, and $r \in \operatorname{im}\delta^0$. $\square$

**Corollary (Actual object).** For $r = (1,1,1,-2)$:
$$
q(r) = -1 - 1 - 1 + (-2) = -5 \neq 0,
$$
so $[r] \neq 0 \in H^1(N;\mathbb{Q})$. $\square$

The theorem classifies every residue on the four-cycle completely. The actual
object is a corollary, not merely an example.

---

## 2. Integral Cohomology and Modular Sensitivity

**Theorem (Integral period).** Over $\mathbb{Z}$, the circulation map
$q : \mathbb{Z}^4 \to \mathbb{Z}$ induces an isomorphism
$$
H^1(N;\mathbb{Z}) \;=\; \mathbb{Z}^4 / \operatorname{im}\delta^0 \;\cong\; \mathbb{Z}.
$$
The actual residue $r = (1,1,1,-2)$ satisfies $[r] = -5 \in \mathbb{Z} \cong H^1(N;\mathbb{Z})$.

**Proof.** The map $q$ is surjective over $\mathbb{Z}$ since $q(0,0,0,1) = 1$.
By Theorem 1 (whose constructive direction works integrally: if $-a-b-c+d = 0$
then $b^* \in \mathbb{Z}^4$), we have $\ker q = \operatorname{im}\delta^0$ over
$\mathbb{Z}$. Therefore
$$
\mathbb{Z}^4 / \operatorname{im}\delta^0 = \mathbb{Z}^4/\ker q \;\cong\; \mathbb{Z}.
$$
The class of $r$ is $q(r) = -5$. $\square$

**Theorem (Modular sensitivity).** Let $k$ be any field. Then
$$
[r] \neq 0 \in H^1(N;k)
\quad\Longleftrightarrow\quad
\operatorname{char}(k) \nmid 5.
$$

**Proof.** Over $k$, the same analysis gives $H^1(N;k) \cong k$ via $q_k$,
where $q_k(a,b,c,d) = -a-b-c+d$ in $k$. Then $[r] = -5 \cdot 1_k \in k$.
This is zero if and only if $\operatorname{char}(k) \mid 5$, i.e., $\operatorname{char}(k) = 5$.

In particular:
- $[r] \neq 0$ over $\mathbb{Q},\,\mathbb{R},\,\mathbb{C},\,\mathbb{F}_2,\,\mathbb{F}_3,\,\mathbb{F}_7,\ldots$
- $[r] = 0$ over $\mathbb{F}_5$, with explicit coboundary certificate $b = (0,1,2,3)$,
  since $b_4 - b_1 = 3 \equiv -2 \pmod{5}$. $\square$

The obstruction is not an absolute binary. It is an arithmetic quantity: its
detectability depends on the characteristic of the coefficient field. Over
$\mathbb{Z}$, the invariant is the integer $-5$; over $\mathbb{F}_5$, that integer
vanishes and the obstruction disappears.

This is verified computationally for primes $2, 3, 5, 7, 11, 13, 17, 19, 23$ by
`classification_theorem.py`, which emits a machine-readable certificate.

---

## 3. Base obstruction

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

## 4. Presentation invariance

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

## 5. Refinement persistence (proved for declared refinements)

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

## 6. Cycle-Lift Persistence Theorem

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

## 7. Rank criterion and classification table

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

## 8. Why single-region subdivisions fail cycle-faithfulness

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

**Proposition (One-dimensional cycle-image criterion).**
Suppose $\operatorname{rank}(PK) = 1$ and let $v \neq 0$ be any generator of
$\operatorname{im}(PK)$. Then $\rho$ is cycle-faithful relative to $z$ if and
only if all ratios $v_e / z_e$ (for $e$ in the support of $z$) are defined,
nonzero, and equal to the same $\lambda \in \mathbb Q^\times$.

*Proof.* $\operatorname{im}(PK) = \mathbb Q v$ (rank 1). So $z \in \operatorname{im}(PK)$
iff $z \in \mathbb Q v$, iff $v = \lambda z$, iff all ratios $v_e/z_e$ are equal
and nonzero. $\square$

**Conjecture (Balanced loop refinement).**
Let $z$ be a simple rational cycle in $N$, and let $\rho: N' \to N$ be a
refinement with $\operatorname{rank}(P|_{Z_1(N')}) = 1$. Let $v \neq 0$ be a
generator of $\operatorname{im}(P|_{Z_1(N')})$. Then $\rho$ is cycle-faithful
relative to $z$ iff the ratios $v_e/z_e$ are uniform and nonzero for all edges $e$
of $z$.

*(Under the rank-1 hypothesis, this is a direct corollary of the One-dimensional
cycle-image criterion. The open geometric question is: which refinement operations
guarantee rank-1 image with uniform ratios?)*

**Failure certificates for non-faithful refinements:**

| Refinement | Generator $v$ | Ratios $v_e/z_e$ | Failure reason |
|---|---|---|---|
| Subdivide $U_1$ | $(-\tfrac{1}{2},-1,-1,\tfrac{1}{2})$ | $(\tfrac{1}{2},1,1,\tfrac{1}{2})$ | non-uniform |
| Subdivide $U_2$ | $(-\tfrac{1}{2},-\tfrac{1}{2},-1,1)$ | $(\tfrac{1}{2},\tfrac{1}{2},1,1)$ | non-uniform |

The failure is not inferred from absence of a witness. It is certified by a rank
separation $\operatorname{rank}([PK\,z]) = 2 > 1 = \operatorname{rank}(PK)$ and a
non-uniform ratio vector, both computed over $\mathbb Q$ by `cycle_lift_test.py`.

---

## 9. Scope of the proof

The proof is organised in six layers (see also §0c and the manuscript Discussion):

| Layer | Role | Sections |
|---|---|---|
| 1 | General finite graph theorem | §0a |
| 2 | Finite nerve / Hodge extension | §0b–§0c |
| 3 | Four-cycle corollary (incl. integral/modular) | §1–§2 |
| 4 | Admissibility bridge | §11b |
| 5 | Dynamic warrant debt | §11c–§11d |
| 6 | Exact certificate and independent verifier | §0c, `verify_certificate.py` |

What is proved in each layer:

1. **General finite graph theorem.** $\operatorname{im}(\delta^0) = Z_1^\perp$; the four conditions gauge-admissibility, global consistency, zero cycle pairings, and $[r]=0$ are equivalent. Proved with explicit dimension count (§0a).

2. **Finite nerve / Hodge extension.** The harmonic 1-cochains $\mathcal{H}^1 = \ker(L_1)$ represent $H^1(N;\mathbb{Q})$. Warrant debt is $D(r) = \|P_{\mathcal{H}^1} r\|^2$. Verified on graphs and nerves (§0b).

3. **Four-cycle corollary.** The four-cycle is the one-cycle case. Every residue $(a,b,c,d)$ is classified by $q = -a-b-c+d$. Integral period $-5$; modular sensitivity $[r]=0$ iff $\operatorname{char}(k)=5$ (§1–§2).

4. **Admissibility bridge.** $[r]\neq 0$ iff no globally consistent claim $\Phi$ exists. The decomposition $r = r^{\mathrm{adm}} + r^{\mathrm{debt}}$ is explicit with $r^{\mathrm{debt}} = (-5/4)z$ for the actual object (§11b).

5. **Dynamic warrant debt.** $D(t) = p(t)^2/4$ tracks debt over time. Cumulative load $W(T) = \sum D(t)$. General Gram matrix formula $D = p^T G^{-1} p$ for multi-cycle systems (§11c–§11d).

6. **Exact certificate and independent verifier.** The engine's certificate carries exact rational $L_1$, harmonic basis, $p$, $r^{\mathrm{debt}}$, and $D$. `verify_certificate.py` reconstructs the verdict from the certificate alone (§0c). Three-case soundness: `coherence_failure`, `globally_admissible`, `warrant_debt`.

What is not yet proved:

> Balanced Loop Refinement Conjecture (characterise all cycle-faithful refinements). Dynamic theory for general nerves with time-varying $\dim\mathcal{H}^1$.

---

## 10. Two-layer interpretation

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

## 11b. Residue-Admissibility Bridge Theorem

This section connects the cohomological obstruction to the failure of global
observational consistency. It is the bridge to warrant-debt theory.

### Setup

Let $N$ be a finite regional nerve with regions $\{U_i\}$ and oriented overlaps
$\{(U_i, U_j)\}$. An **observation map** assigns to each overlap an
independently-measured discrepancy $r_{ij} \in \mathbb{Q}$.

A **global admissible claim** $\Phi$ is an assignment of values $\Phi_i \in
\mathbb{Q}$ to each region, consistent with all seam data:
$$
\Phi_j - \Phi_i = r_{ij} \quad\text{for every overlap } (U_i, U_j).
$$
In terms of the cochain complex, this is: $(\delta^0 \Phi)_{ij} = r_{ij}$, i.e.,
$r = \delta^0 \Phi$.

### Theorem (Residue-Admissibility Bridge)

For $r \in C^1(N;\mathbb{Q})$ satisfying the cocycle condition $\delta^1 r = 0$,
the following are equivalent:

1. **Gauge-admissible:** $\exists\, b \in C^0$ with $\delta^0 b = r$.
2. **Globally consistent:** $\exists\, \Phi$ (global claim) with $\Phi_j - \Phi_i = r_{ij}$ at every overlap.
3. **Cohomologically trivial:** $[r] = 0 \in H^1(N;\mathbb{Q})$.

**Proof.** (1)$\Leftrightarrow$(3) is the definition of $H^1 = C^1/\operatorname{im}\delta^0$.
For (2)$\Leftrightarrow$(1): if $\Phi$ exists, set $b = \Phi$; then
$(\delta^0 b)_{ij} = b_j - b_i = r_{ij}$. Conversely, if $\delta^0 b = r$, define
$\Phi_i := b_i$; the consistency condition holds by construction. $\square$

**Corollary (Warrant Debt).** If $[r] \neq 0$, no globally consistent claim
exists. The class $[r] \in H^1(N;\mathbb{Q})$ is the **warrant debt**: a
quantified, gauge-invariant, irremovable inconsistency in the seam data.

### Warrant Debt Decomposition

**Caveat.** The decomposition below depends on the choice of inner product on
$C^1$. The cohomology class $[r]$ and the obstruction period $\langle z,r\rangle$
are basis- and inner-product-independent. The split $r = r^{\mathrm{adm}} +
r^{\mathrm{debt}}$ and the magnitude $\|r^{\mathrm{debt}}\|^2$ are stated
relative to the standard rational inner product on the declared edge basis.

Over $\mathbb{Q}$ with the standard inner product, the cochain group decomposes
orthogonally:
$$
C^1 = \operatorname{im}\delta^0 \;\oplus\; Z_1.
$$

Any seam residue splits uniquely as:
$$
r = r^{\mathrm{adm}} + r^{\mathrm{debt}},
\qquad
r^{\mathrm{debt}} = \frac{\langle r, z\rangle}{\langle z,z\rangle}\,z
$$
(for a single-cycle system), where:

- $r^{\mathrm{adm}} \in \operatorname{im}\delta^0$: the **admissible component** — the closest consistent residue.
- $r^{\mathrm{debt}} \in Z_1$: the **warrant debt** — irremovable; no gauge touches it.

The gauge $b^*$ with $\delta^0 b^* = r^{\mathrm{adm}}$ gives the nearest-admissible
system.

### Computation for the Actual Object

For $r = (1,1,1,-2)$, `admissibility_bridge.py` computes:

| Quantity | Value |
|---|---|
| Admissible? | No |
| Obstruction period $\langle z,r\rangle$ | $-5$ |
| $\langle z,z\rangle$ | $4$ |
| $r^{\mathrm{adm}}$ | $(-1/4,\,-1/4,\,-1/4,\,-3/4)$ |
| $r^{\mathrm{debt}} = \frac{-5}{4}\,z$ | $(5/4,\,5/4,\,5/4,\,-5/4)$ |
| $\|r^{\mathrm{debt}}\|^2 = 25/4$ | $p^2/\|z\|^2$ |
| Closest admissible gauge $b^*$ | $(3/4,\,1/2,\,1/4,\,0)$ |

The coefficient $-5/4$ comes from $p/\|z\|^2 = -5/4$: the obstruction period
divided by the cycle norm. The integer $-5$ is the invariant; the $4$ is the
norm of the four-edge primitive cycle under the chosen inner product.

For comparison, $r = (1,1,1,3)$ (zero circulation) is globally admissible with
consistent global claim $\Phi = (-3,-2,-1,0)$.

### What the theorem means

The bridge theorem says: the only reason a finite regional system cannot have a
globally consistent claim is that its seam residue fails to be a coboundary.
There is no other obstruction. The H¹ class IS the warrant debt, completely and
exactly.

In plain language:

> **A residue is structurally irremovable if and only if the local observations
> cannot be reconciled by any global assessment. The cohomology class measures
> how irremovable it is.**

---

## 11c. Dynamic Warrant Debt Theorem

**Caveat.** The warrant debt magnitude $D(t)$ and the cumulative load $W(T)$
are relative to the standard rational inner product. The period $p(t)$ and the
admissibility verdict are inner-product-independent.

**Setup.** Let $(r_t)_{t \geq 0}$ be a time-indexed sequence of residues on a
fixed finite regional nerve $N$. For each $r_t$, let
$$
r_t = r_t^{\mathrm{adm}} + r_t^{\mathrm{debt}}
$$
be the harmonic decomposition, and define the **warrant debt magnitude**:
$$
D(t) = \|r_t^{\mathrm{debt}}\|^2.
$$

**Theorem (Dynamic Warrant Debt).**
$$
D(t) = 0
\;\Longleftrightarrow\;
[r_t] = 0
\;\Longleftrightarrow\;
\text{system is globally admissible at time } t.
$$
$$
D(t) > 0
\;\Longleftrightarrow\;
\text{system carries irremovable warrant debt at time } t.
$$

**Four-Cycle Debt Formula.** For the four-region loop nerve with primitive cycle
$z$ (single-cycle system, $\|z\|^2 = 4$):
$$
D(t) = \frac{p(t)^2}{\|z\|^2} = \frac{p(t)^2}{4},
\qquad p(t) = \langle z, r_t\rangle.
$$

This gives a closed-form debt magnitude from the obstruction period alone.

**Derived quantities:**

| Quantity | Formula | Meaning |
|---|---|---|
| Period | $p(t) = \langle z, r_t\rangle$ | Obstruction circulation at time $t$ |
| Debt magnitude | $D(t) = p(t)^2/\|z\|^2$ | Irremovable component size |
| Fatigue | $F(t_0, t_1) = D(t_1) - D(t_0)$ | Change in debt |
| Cumulative load | $W(T) = \sum_{t=0}^T D(t)$ | Total debt accumulated |

**Toy model.** Set $r_t = (1, 1, 1, 3 - \epsilon_t)$:
- $p(t) = -\epsilon_t$, $D(t) = \epsilon_t^2/4$
- At $\epsilon_t = 0$: admissible, $D = 0$
- At $\epsilon_t = 5$: $r_t = (1,1,1,-2)$ — the actual object, $D = 25/4$

| $\epsilon_t$ | $r_t$ | $p(t)$ | $D(t)$ |
|---:|---|---:|---:|
| 0 | $(1,1,1,3)$ | $0$ | $0$ |
| 1 | $(1,1,1,2)$ | $-1$ | $1/4$ |
| 2 | $(1,1,1,1)$ | $-2$ | $1$ |
| 3 | $(1,1,1,0)$ | $-3$ | $9/4$ |
| 4 | $(1,1,1,-1)$ | $-4$ | $4$ |
| 5 | $(1,1,1,-2)$ | $-5$ | $25/4$ |

Cumulative load: $W(5) = 55/4$.

The fatigue scenario (onset, partial recovery, re-escalation over 10 steps) gives
$W(9) = 45/2$, verified by `dynamic_warrant_debt.py`. The actual object held
fixed gives $W(5) = 75/2$.

---

## 11d. General Warrant Debt Formula (Gram Matrix)

The four-cycle formula $D(t) = p(t)^2/4$ is a special case of a general result
that holds for any finite nerve with an arbitrary cycle basis.

**Theorem (General Gram Matrix Debt Formula).** Let $G$ be a finite connected
oriented graph with cycle basis $\{z_1, \ldots, z_k\}$. Define the Gram matrix
$$
G_{ij} = \langle z_i, z_j\rangle
$$
and the period vector
$$
p_i(r) = \langle z_i, r\rangle.
$$
Then the warrant debt magnitude relative to the standard inner product is:
$$
D(r) = p(r)^T G^{-1} p(r).
$$

**Proof.** The harmonic component is $r^{\mathrm{debt}} = \sum_i c_i z_i$ where
$c = G^{-1} p$. Then:
$$
\|r^{\mathrm{debt}}\|^2 = c^T G c = (G^{-1}p)^T G (G^{-1}p) = p^T G^{-1} p. \;\square
$$

**Special cases:**
- $k = 1$ (four-cycle, single cycle): $D = p^2/\|z\|^2$. With $\|z\|^2 = 4$: $D = p^2/4$.
- Orthogonal basis: $G = \operatorname{diag}(\|z_1\|^2,\ldots,\|z_k\|^2)$, $D = \sum_i p_i^2/\|z_i\|^2$.
- General (non-orthogonal): the off-diagonal terms in $G^{-1}$ couple the period components.

**Gram matrices for tested graphs:**

| Graph | $\dim H^1$ | $G$ | $D$ for test residue |
|---|---|---|---|
| Four-cycle $C_4$ | 1 | $(4)$ | $25/4$ |
| Diamond | 2 | $\begin{pmatrix}4&2\\2&3\end{pmatrix}$ | $51/8$ |
| Complete $K_4$ | 3 | $\begin{pmatrix}3&1&-1\\1&3&1\\-1&1&3\end{pmatrix}$ | $13$ |

The off-diagonal entries in the diamond and $K_4$ Gram matrices reflect the
non-orthogonality of the natural cycle basis. The formula $D = p^T G^{-1} p$
accounts for this coupling exactly.

**Dynamic version.** For time-indexed $(r_t)$:
$$
D(t) = p(t)^T G^{-1} p(t), \qquad W(T) = \sum_{t=0}^T D(t).
$$

Verified on four trajectories (four-cycle, diamond simultaneous onset, diamond
second-cycle-only, $K_4$ single-edge drift) by `general_warrant_debt.py`.

---

## 12. Certificate files

All computations above are certified by the files in `certificates/`:

| File | Content |
|---|---|
| `actual_gluing_object_v1_certificate.json` | Base classification and cycle witness |
| `actual_gluing_object_v1_invariance_report.json` | Five invariance tests |
| `actual_gluing_object_v1_refinement_test_report.json` | Four refinement tests with direct pairings |
| `admissible_refinement_theorem_certificate.json` | Adjointness and cycle-lift check for each refinement |
| `cycle_lift_test_certificate.json` | Linear-system proof of cycle-faithfulness / impossibility |
| `classification_theorem_certificate.json` | Complete classifier, integral period, and modular sensitivity |
| `general_obstruction_classifier_certificate.json` | General theorem verified on seven graph types |
| `admissibility_bridge_certificate.json` | Residue-Admissibility Bridge: warrant debt decomposition |
| `dynamic_warrant_debt_certificate.json` | Dynamic Warrant Debt: three trajectories, formula $D=p^2/4$ verified |

These files are frozen; see `MANIFEST.md` for the claim licensed by them.
