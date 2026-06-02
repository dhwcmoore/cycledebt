# Finite Regional Warrant Debt Pipeline

## Status

**Complete finite four-cycle warrant-debt pipeline. Version 0.4.**

This project is a certified finite cohomological framework for detecting,
decomposing, and tracking warrant debt in local-to-global regional systems.

### Verified components

| # | Component | Script | Certificate |
|---|---|---|---|
| 1 | General H¹ obstruction classifier (arbitrary graphs) | `residue_test.py` | `*_certificate.json` |
| 2 | Complete four-cycle classification theorem ($q = 0 \iff$ removable) | `classification_theorem.py` | `classification_theorem_certificate.json` |
| 3 | Integral period theorem ($H^1(N;\mathbb{Z}) \cong \mathbb{Z}$, period $= -5$) | `classification_theorem.py` | same |
| 4 | Modular coefficient sensitivity ($[r]=0$ iff $\operatorname{char}(k) = 5$) | `classification_theorem.py` | same |
| 5 | General cycle-detection theorem (7 graph types) | `general_obstruction_classifier.py` | `general_obstruction_classifier_certificate.json` |
| 6 | Presentation invariance (5 changes) | `invariance_test.py` | `*_invariance_report.json` |
| 7 | Refinement persistence (4 refinements; cycle-lift theorem) | `admissible_refinement_theorem.py` | `admissible_refinement_theorem_certificate.json` |
| 8 | Residue-Admissibility Bridge Theorem | `admissibility_bridge.py` | `admissibility_bridge_certificate.json` |
| 9 | Warrant debt decomposition $r = r^{\mathrm{adm}} + r^{\mathrm{debt}}$ | `admissibility_bridge.py` | same |
| 10 | Dynamic warrant debt: $D(t) = p(t)^2/4$, trajectories | `dynamic_warrant_debt.py` | `dynamic_warrant_debt_certificate.json` |
| 11 | General Gram matrix debt formula: $D = p^T G^{-1} p$ | `general_warrant_debt.py` | `general_warrant_debt_certificate.json` |

### The full pipeline

```
r_t  →  [r_t] ∈ H¹  →  p(t) = ⟨z, r_t⟩  →  D(t) = p(t)² / ‖z‖²
```

- **p(t)**: obstruction period — inner-product-independent integer
- **D(t)**: warrant debt magnitude — metric-relative, closed form from period
- **W(T) = Σ D(t)**: cumulative debt load over trajectory

For the actual object $r = (1,1,1,-2)$: $p = -5$, $D = 25/4$.

### The central theorem (Residue-Admissibility Bridge)

These three conditions are equivalent:
1. $\exists\, b$ with $\delta^0 b = r$ (gauge-admissible)
2. $\exists\, \Phi$ with $\Phi_j - \Phi_i = r_{ij}$ (globally consistent claim)
3. $[r] = 0 \in H^1$ (cohomologically trivial)

Non-zero $[r]$ is a **warrant debt certificate**: the local observations cannot
be assembled into any globally consistent claim.

---

## Quick start

```bash
# Classify the actual object
python residue_test.py actual/actual_gluing_object_v1.json

# Run the full pipeline on the actual object
python classification_theorem.py      # integral period, modular sensitivity
python admissibility_bridge.py        # bridge theorem + debt decomposition
python dynamic_warrant_debt.py        # time-indexed debt trajectories
python general_warrant_debt.py        # Gram matrix formula, arbitrary graphs

# Verify on arbitrary graph types (path, triangle, diamond, K4, ...)
python general_obstruction_classifier.py

# Invariance and refinement persistence
python invariance_test.py actual/actual_gluing_object_v1.json
python admissible_refinement_theorem.py
```

---

## Mathematical content

### Object

Finite nerve $N$: regions $U_1, U_2, U_3, U_4$, edges $U_1U_2, U_2U_3, U_3U_4,
U_1U_4$. Residue $r = (1,1,1,-2) \in C^1(N;\mathbb{Q})$.

### Classification

$[r] \neq 0 \in H^1(N;\mathbb{Q})$.
Proved by: contradiction (no solution to $\delta^0 b = r$) and cycle witness
($\langle z, r\rangle = -5 \neq 0$ for $z = (-1,-1,-1,1)$).

### Complete four-cycle theorem

For any residue $(a,b,c,d)$ on the four-region loop:
$$[r] = 0 \iff -a-b-c+d = 0.$$

### Integral period

$H^1(N;\mathbb{Z}) \cong \mathbb{Z}$ via the circulation $q$. The actual
residue has integral period $q(r) = -5$.

### Modular sensitivity

$[r] \neq 0 \in H^1(N;k) \iff \operatorname{char}(k) \nmid 5$.
Over $\mathbb{F}_5$: explicit coboundary $b = (0,1,2,3)$.

### Warrant debt decomposition

Relative to the standard rational inner product:
$$r = r^{\mathrm{adm}} + r^{\mathrm{debt}}, \qquad r^{\mathrm{debt}} = \frac{p}{\|z\|^2}\,z = -\tfrac{5}{4}\,z.$$
Closest admissible gauge: $b^* = (3/4, 1/2, 1/4, 0)$. Debt magnitude: $D = 25/4$.

### Dynamic warrant debt

For trajectory $r_t = (1, 1, 1, 3-\varepsilon_t)$:
$$p(t) = -\varepsilon_t, \qquad D(t) = \varepsilon_t^2/4.$$
At $\varepsilon = 5$: actual object, $D = 25/4$. Cumulative load $W(5) = 55/4$.

### General Gram matrix formula

For arbitrary finite nerve with cycle basis $\{z_1, \ldots, z_k\}$:
$$D(r) = p(r)^T G^{-1} p(r), \qquad p_i = \langle z_i, r\rangle, \qquad G_{ij} = \langle z_i, z_j\rangle.$$

---

## File organisation

```
residue_test.py                      # General H¹ classifier (any JSON input)
classification_theorem.py            # Complete classifier + integral/modular theorems
general_obstruction_classifier.py    # General cycle-detection on 7 graph types
admissibility_bridge.py              # Bridge theorem + warrant debt decomposition
dynamic_warrant_debt.py              # Time-indexed debt trajectories
general_warrant_debt.py              # Gram matrix formula for arbitrary nerves
invariance_test.py                   # 5 presentation invariance tests
refinement_invariance_test.py        # Refinement persistence tests
admissible_refinement_theorem.py     # Cycle-lift persistence theorem
cycle_lift_test.py                   # Cycle-faithfulness linear-system tests

actual/
  actual_gluing_object_v1.json       # The actual object

examples/
  loop_obstruction.json              # H¹ obstruction example
  filled_triangle_coboundary.json    # Removable example
  invalid_cocycle.json               # Coherence failure example

certificates/                        # All machine-readable certificates
invariance_tests/                    # Presentation-variant inputs
refinement_tests/                    # Refined cover inputs
manuscript/                          # LaTeX manuscript
  jact_full.tex                      # Full manuscript
  proof.tex                          # Formal proof (LaTeX, sourced from PROOF.md)
  references.bib

PROOF.md                             # Authoritative mathematical proof
```

## Input format

```json
{
  "name": "object_name",
  "regions": ["U1", "U2", "U3", "U4"],
  "edges": [["U1","U2"], ["U2","U3"], ["U3","U4"], ["U1","U4"]],
  "faces": [],
  "residue": {"U1-U2": "1", "U2-U3": "1", "U3-U4": "1", "U1-U4": "-2"},
  "coefficient_domain": "Q"
}
```

## Open problems

- **Balanced Loop Refinement Conjecture**: characterise all cycle-faithful refinements.
- **General dynamic theory**: extend to arbitrary finite nerves with multi-dimensional debt vectors.
- **Temporal resolution**: given a debt trajectory, compute the minimal intervention to restore admissibility at each step.
