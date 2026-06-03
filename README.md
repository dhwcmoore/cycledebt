# Finite Nerve Warrant Debt Engine

## Central theorem

**Warrant debt for finite regional systems is the non-zero harmonic $H^1$-component
of a coherent seam residue.**

Precisely: for a finite nerve $N$ over $\mathbb{Q}$ with cochain complex
$C^0 \xrightarrow{\delta^0} C^1 \xrightarrow{\delta^1} C^2$, a seam residue
$r \in C^1$ has a debt magnitude

$$D(r) = \|P_{\mathcal{H}^1} r\|^2$$

where $\mathcal{H}^1 = \ker((\delta^0)^T) \cap \ker(\delta^1)$ is the harmonic
$H^1$ space, computed via the Hodge Laplacian $L_1 = \delta^0(\delta^0)^T +
(\delta^1)^T \delta^1$. Then:

$$D(r) = 0 \;\Longleftrightarrow\; [r] = 0 \in H^1 \;\Longleftrightarrow\; \text{a global consistent claim exists.}$$
$$D(r) > 0 \;\Longleftrightarrow\; [r] \neq 0 \in H^1 \;\Longleftrightarrow\; \text{warrant debt; no global claim.}$$

## Three-case certificate structure

Every computation returns one of three formally accountable outcomes:

| `case` | Condition | Meaning |
|---|---|---|
| `coherence_failure` | $\delta^1 r \neq 0$ | Not locally coherent; $H^1$ question does not arise |
| `globally_admissible` | $D(r) = 0$ | $[r] = 0$; seam data globally reconcilable |
| `warrant_debt` | $D(r) > 0$ | $[r] \neq 0$; irremovable structural debt |

## The four-cycle as a corollary

The four-region loop nerve $N$ (regions $U_1,U_2,U_3,U_4$) is the case where
$\mathcal{H}^1 = \text{span}(z)$, $z = (-1,-1,-1,1)$, $\|z\|^2 = 4$. The general
formula reduces to:

$$D(r) = \frac{p^2}{4}, \qquad p = \langle z, r\rangle = -a-b-c+d.$$

For the actual seam residue $r = (1,1,1,-2)$: $p = -5$, $D = 25/4$.

The Finite Nerve Warrant Debt Theorem applies to this as a special case;
the complete four-cycle theorem (every residue classified by the single invariant
$q = -a-b-c+d$) is a corollary of the general graph theorem.

---

## What is proved

### General theorems

| Theorem | Statement | Proof location |
|---|---|---|
| Finite Graph Period Classification | $\operatorname{im}(\delta^0) = Z_1^\perp$; four equivalent conditions | PROOF.md §0a |
| Nerve Extension | Harmonic $\mathcal{H}^1 = \ker(L_1)$ represents $H^1(N;\mathbb{Q})$ | PROOF.md §0b |
| Finite Nerve Warrant Debt | Three-case soundness theorem (capstone) | PROOF.md §0c |
| Residue-Admissibility Bridge | $[r]=0 \Leftrightarrow$ global claim exists | PROOF.md §11b |

### Specific results for the four-cycle

| Result | Value | Script |
|---|---|---|
| Complete classification | $q(a,b,c,d) = -a-b-c+d = 0 \Leftrightarrow$ removable | `classification_theorem.py` |
| Integral period | $H^1(N;\mathbb{Z}) \cong \mathbb{Z}$, period $= -5$ | `classification_theorem.py` |
| Modular sensitivity | $[r] = 0$ iff $\text{char}(k) = 5$ | `classification_theorem.py` |
| Debt decomposition | $r^{\text{debt}} = (-5/4)z$, $\|r^{\text{debt}}\|^2 = 25/4$ | `admissibility_bridge.py` |
| Four-cycle formula | $D(t) = p(t)^2/4$ | `dynamic_warrant_debt.py` |
| Gram matrix formula | $D = p^T G^{-1} p$ for any cycle basis | `general_warrant_debt.py` |

---

## Scripts and certificates

```
finite_nerve_warrant_debt.py      # General engine: graphs + nerves, JSON input
classification_theorem.py         # Integral period, modular sensitivity
general_obstruction_classifier.py # General cycle-detection on 7 graph types
admissibility_bridge.py           # Bridge theorem + harmonic decomposition
dynamic_warrant_debt.py           # Time-indexed debt D(t), cumulative load W(T)
general_warrant_debt.py           # Gram matrix D = p^T G^{-1} p, 4 graph types
admissible_refinement_theorem.py  # Cycle-lift persistence theorem
residue_test.py                   # Base H^1 classifier (any JSON input)
```

Every script emits a machine-readable JSON certificate in `certificates/`.
All arithmetic is **exact rational** (sympy). Certificates include $L_1$,
harmonic basis vectors, $r^{\text{debt}}$, and $D$, sufficient for independent
verification.

---

## Quick start

```bash
# Run the general engine on any finite regional nerve
python finite_nerve_warrant_debt.py --json actual/actual_gluing_object_v1.json

# Run built-in test suite (7 cases: graphs + nerves, all three cert branches)
python finite_nerve_warrant_debt.py

# Full pipeline for the four-cycle example
python classification_theorem.py      # period -5, modular sensitivity
python admissibility_bridge.py        # r_adm + r_debt decomposition
python dynamic_warrant_debt.py        # D(t) = p(t)^2/4 trajectories
python general_warrant_debt.py        # Gram matrix, D = p^T G^{-1} p
```

---

## Input format

```json
{
  "name": "my_object",
  "regions": ["U1", "U2", "U3", "U4"],
  "edges": [["U1","U2"], ["U2","U3"], ["U3","U4"], ["U1","U4"]],
  "faces": [],
  "residue": {"U1-U2": "1", "U2-U3": "1", "U3-U4": "1", "U1-U4": "-2"},
  "coefficient_domain": "Q"
}
```

---

## Certificate format (key fields)

```json
{
  "arithmetic": "exact rational (sympy Q)",
  "case": "warrant_debt",
  "theorem_invoked": "[r] != 0 in H^1; D > 0; no global claim [PROOF.md §0b+§11b]",
  "L1_matrix": [...],
  "harmonic_basis_vectors": [["-1","-1","-1","1"]],
  "p_periods": ["-5"],
  "r_debt_vector": ["5/4","5/4","5/4","-5/4"],
  "debt_norm_squared": "25/4",
  "D_harmonic_cross_check": "25/4",
  "gram_harmonic_agree": true
}
```

---

## Precision notes

**Gram formula basis requirement.** The formula $D = p^T G^{-1} p$ gives the
correct debt magnitude only when the period basis $\{h_i\}$ spans the harmonic
obstruction space $\ker(L_1)$. Raw graph-cycle vectors without accounting for
faces give wrong answers for nerves with 2-simplices. The Hodge Laplacian
implementation is the safe canonical choice.

**Inner product dependence.** $D(r)$ and the decomposition $r = r^{\text{adm}} +
r^{\text{debt}}$ depend on the choice of inner product on $C^1$. The admissibility
verdict and the period $p = \langle z, r\rangle$ are inner-product-independent.

---

## Open problems

- **Balanced Loop Refinement Conjecture:** characterise all cycle-faithful refinements.
- **Dynamic theory for arbitrary nerves:** extend $D(t) = p(t)^T G^{-1} p(t)$
  trajectories to nerves where $\dim\mathcal{H}^1$ can change across time steps.
- **Temporal resolution:** given a debt trajectory, compute the minimal intervention
  to restore admissibility at each step.
