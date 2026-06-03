# CycleDebt: Exact Obstruction Certificates for Cyclic Diagnostic Models

---

## 1. Problem

A cyber-physical monitoring system produces local diagnostic readings at each
subsystem interface. The local data can be internally consistent yet still fail
to warrant a global root-cause claim — because the available observations
collapse states that the claim requires to be distinct.

**Existing tools** detect whether a claim *fits* the observations.  
**CycleDebt** detects whether the observations are *sufficient* to warrant the claim,
and produces a machine-checkable certificate explaining exactly why they are not.

---

## 2. Formal object

Let *G* be a finite oriented graph whose nodes are monitored subsystems and
whose edges carry interface residues `r ∈ C¹(G; ℚ)`.

The diagnostic claim is **globally admissible** iff

    [r] = 0  in  H¹(G; ℚ)

equivalently: there exists a gauge `b ∈ C⁰` such that `δ⁰b = r`.

When `[r] ≠ 0`, define the **warrant debt magnitude**

    D(r) = p(r)ᵀ G⁻¹ p(r)

where `p_i(r) = ⟨h_i, r⟩` is the obstruction period against the *i*-th
harmonic basis vector `h_i ∈ ker(L₁)`, and `G_ij = ⟨h_i, h_j⟩` is the Gram
matrix.  All arithmetic is exact rational (SymPy ℚ).

For a single-cycle system, this reduces to `D = p²/‖z‖²`.

**Three verdicts:**

| Verdict | Condition | Meaning |
|---|---|---|
| `COHERENCE FAILURE` | `δ¹r ≠ 0` | Local data is self-contradictory; H¹ question does not arise |
| `GLOBALLY ADMISSIBLE` | `[r] = 0`, `D = 0` | Claim is warranted; consistent global root-cause assignment exists |
| `WARRANT DEBT` | `[r] ≠ 0`, `D > 0` | Local data coherent; cyclic obstruction blocks the claim |

---

## 3. Three verdicts

The tool distinguishes three diagnostically distinct situations.
In engineering terms:

- **Coherence failure**: sensor readings at three pairwise interfaces contradict
  each other. The A-B and B-C readings imply A-C = 2, but the A-C sensor says 1.
  Fix the sensors before asking about root cause.

- **Warrant debt**: all pairwise readings are internally consistent, but they
  cannot warrant the proposed root-cause claim because the observation map
  collapses the fault states the claim requires to be distinct. The obstruction
  is non-removable: no gauge choice eliminates it.

- **Globally admissible**: a refined observation (e.g., a new sensor that
  distinguishes previously collapsed states) makes the cyclic period vanish.
  The claim is now warranted, and a certificate confirms it.

---

## 4. CPS diagnostic example

**System**: four-node monitoring loop  
`A_Sensor → B_Controller → C_Actuator → D_Monitor → A_Sensor`

**Claim**: `fault_origin = B_Controller`

**Observation map**: sensors at the A–B and B–C interfaces cannot distinguish
two internal fault states of B_Controller (B_fault_1, B_fault_2).

**Residues** (local diagnostic readings):

    r_AB = 1,  r_BC = 1,  r_CD = 1,  r_AD = −2

**Result**: the residues form a valid cocycle (`δ¹r = 0`), so there is no
internal contradiction. But the cyclic period is:

    ⟨z, r⟩  =  (−1)(1) + (−1)(1) + (−1)(1) + (1)(−2)  =  −5  ≠  0

No global consistent root-cause assignment exists.
The warrant debt magnitude is `D = (−5)²/4 = 25/4`.

**After refinement**: adding a sensor that resolves B_fault_1 from B_fault_2
changes `r_AD` to 3 (the correct value under the finer observation).
The cyclic period becomes 0, D = 0, and the claim is warranted.

---

## 5. Certificate output

```
$ python scripts/cyclediagnostic_demo.py examples/cps_loop_fault.json

CycleDebt Diagnostic Report

System: four-node CPS diagnostic loop
Claim:  fault_origin = B_Controller

Verdict: WARRANT DEBT

Reason:
  The local diagnostic residues are coherent.
  However, the diagnostic claim does not factor through the observation map.
  A non-zero cyclic obstruction remains.

  Exact witness:
    cycle z = (-1, -1, -1, 1)
    residue r = (1, 1, 1, -2)
    period <z,r> = -5
    debt magnitude D = 25/4

Certificate:
  certificates/cps_loop_fault_certificate.json

Independent verification:
  PASS
```

```
$ python scripts/cyclediagnostic_demo.py examples/cps_loop_refined_sensor.json

Verdict: GLOBALLY ADMISSIBLE

The added observation distinguishes the formerly collapsed states.
The obstruction vanishes.
The diagnostic claim is now warranted.
```

The certificate JSON contains: `L1_matrix`, `harmonic_basis_vectors`, `p_periods`,
`r_debt_vector`, `debt_norm_squared`.  The independent verifier re-derives
everything from those fields using only exact rational arithmetic, without
trusting the engine that produced them.

---

## 6. Relevance to ZORRO / cyclic structures / formal methods

**ZORRO** (Zero Downtime in Cyber-Physical Systems, partners: TNO-ESI, ASML,
Canon, Philips, Thermo Fisher) frames diagnostic workflows as formalised
knowledge pipelines over monitored CPS.  CycleDebt offers a formal
**pre-check**: before a root-cause claim enters the diagnostic pipeline, it
verifies whether the available monitoring data can structurally warrant that
claim.  A non-zero obstruction certificate is a *refinement prescription*: it
identifies exactly what additional observation would collapse the debt to zero.

**Cyclic Structures in Programs and Proofs** (NWO ENW-XL, Caltais et al.):
the warrant debt object `[r] ∈ H¹(G; ℚ)` is a cyclic obstruction in the
precise sense of the project — a non-trivial cohomology class carried by a
feedback loop in the monitoring graph.  The harmonic representative `r_debt`
is the minimal cyclic component that cannot be eliminated by local gauge
correction.

**Formal methods connections**:

| CycleDebt concept | FMT / process-algebra analogue |
|---|---|
| Harmonic basis `ker(L₁)` | Minimal cycle basis of the monitoring graph |
| Period `⟨h, r⟩ ≠ 0` | Non-bisimilar behaviour under observation quotient |
| Gauge correction `b*` | Local state correction that removes coboundary debt |
| Certificate `[r] ∈ H¹` | Exact obstruction to lifting a local bisimulation |
| Refinement that kills debt | Sensor addition that recovers observational equivalence |

The certificate format is machine-checkable in exact ℚ arithmetic and could
be expressed as a small proof obligation in a process-algebra or coalgebraic
type theory.

---

## 7. Possible collaboration

The tool is runnable now (`python scripts/cyclediagnostic_demo.py`).
Three worked examples are included: warrant debt, globally admissible,
and coherence failure.

**The ask is modest and specific**:

> I would value your advice on whether the obstruction-certificate idea can
> be reformulated in the language of process algebra, coalgebra, or
> model-based diagnostics, and whether a small ZORRO-style demonstrator
> would be a reasonable way to develop it further.

Possible directions:
- Express the H¹ obstruction as a bisimulation failure in a process-algebraic model
- Use coalgebraic type theory to give the certificate a formal proof-term
- Extend the topology from graphs to Kripke structures or labelled transition systems
- Connect to fault-tree synthesis (CPS → fault tree via observation quotient)

The tool is small, the mathematics is exact, and the CPS framing is already there.
