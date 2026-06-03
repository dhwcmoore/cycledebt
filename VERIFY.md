# Independent Verification of the Actual Object Certificate

This document shows how to verify the warrant-debt certificate for the actual object
`actual_gluing_object_v1` from scratch, using only the file
`certificates/finite_nerve_warrant_debt_certificate.json`.

No trust in the computation scripts is required. Everything can be checked by
hand or with the ten-line script at the end of this document.

---

## The relevant certificate fields

```
residue:                [1, 1, 1, -2]
L1_matrix:             [[2,-1,0,1],[-1,2,-1,0],[0,-1,2,1],[1,0,1,2]]
harmonic_basis_vectors: [[-1,-1,-1,1]]
p_periods:             [-5]
r_debt_vector:         [5/4, 5/4, 5/4, -5/4]
debt_norm_squared:     25/4
case:                  warrant_debt
arithmetic:            exact rational (sympy Q)
```

---

## Eight-step hand verification

### Step 1. Read the Hodge Laplacian

$$
L_1 =
\begin{pmatrix}
2 & -1 & 0 & 1 \\
-1 & 2 & -1 & 0 \\
0 & -1 & 2 & 1 \\
1 & 0 & 1 & 2
\end{pmatrix}.
$$

### Step 2. Verify $h \in \ker(L_1)$

Certificate gives $h = (-1,-1,-1,1)^T$. Compute $L_1 h$:

$$
L_1 h =
\begin{pmatrix}
2(-1)+(-1)(-1)+0(-1)+1(1) \\
(-1)(-1)+2(-1)+(-1)(-1)+0(1) \\
0(-1)+(-1)(-1)+2(-1)+1(1) \\
1(-1)+0(-1)+1(-1)+2(1)
\end{pmatrix}
=
\begin{pmatrix}
-2+1+0+1 \\ 1-2+1+0 \\ 0+1-2+1 \\ -1+0-1+2
\end{pmatrix}
=
\begin{pmatrix}
0 \\ 0 \\ 0 \\ 0
\end{pmatrix}.
$$

$h$ is in the null space of $L_1$. ✓

### Step 3. Compute the period

$$
p = \langle h, r \rangle = (-1)(1) + (-1)(1) + (-1)(1) + (1)(-2) = -1-1-1-2 = -5.
$$

Matches certificate field `p_periods = [-5]`. ✓

### Step 4. Compute the harmonic norm $\langle h, h\rangle$

$$
\langle h, h\rangle = (-1)^2 + (-1)^2 + (-1)^2 + 1^2 = 4.
$$

### Step 5. Compute the debt vector

$$
r^{\text{debt}}
= \frac{\langle h, r\rangle}{\langle h, h\rangle}\, h
= \frac{-5}{4}\,(-1,-1,-1,1)^T
= \left(\tfrac{5}{4},\tfrac{5}{4},\tfrac{5}{4},-\tfrac{5}{4}\right)^T.
$$

Matches certificate field `r_debt_vector = [5/4, 5/4, 5/4, -5/4]`. ✓

### Step 6. Compute the debt magnitude

$$
D = \|r^{\text{debt}}\|^2
= \left(\tfrac{5}{4}\right)^2 \times 3 + \left(-\tfrac{5}{4}\right)^2
= 4 \times \frac{25}{16}
= \frac{25}{4}.
$$

Matches certificate field `debt_norm_squared = 25/4`. ✓

### Step 7. Confirm four-cycle formula

$$
D = \frac{p^2}{\langle h,h\rangle} = \frac{(-5)^2}{4} = \frac{25}{4}. \quad\checkmark
$$

### Step 8. Confirm case

$D = 25/4 > 0$ and `is_cocycle = true`, so the correct case is `warrant_debt`. ✓

---

## What these eight steps prove

Given the certificate:
1. $L_1 h = 0$ shows $h$ is a genuine harmonic 1-cochain (Step 2).
2. $p = -5 \neq 0$ shows $r$ has nonzero pairing with the obstruction (Step 3).
3. $D = 25/4 > 0$ shows the harmonic projection of $r$ is nonzero (Steps 5–6).
4. By the Finite Nerve Warrant Debt Theorem (PROOF.md §0c): $D > 0 \Rightarrow [r] \neq 0 \in H^1 \Rightarrow$ no globally consistent claim exists.

No script is trusted; only the certificate data and arithmetic are used.

---

## Ten-line Python verification

```python
import sympy as sp, json

cert   = json.load(open("certificates/finite_nerve_warrant_debt_certificate.json"))
entry  = next(r for r in cert["results"] if r["case"] == "warrant_debt")

L1     = sp.Matrix([[sp.Rational(v) for v in row] for row in entry["L1_matrix"]])
h      = sp.Matrix([sp.Rational(v) for v in entry["harmonic_basis_vectors"][0]])
r      = sp.Matrix([sp.Rational(v) for v in entry["residue"]])

assert L1 * h == sp.zeros(len(r), 1),              "Step 2: L1 h != 0"
p      = h.dot(r)
r_debt = sp.Rational(p, h.dot(h)) * h
D      = r_debt.dot(r_debt)
assert D == sp.Rational(entry["debt_norm_squared"]), "Step 6: D mismatch"
assert entry["case"] == "warrant_debt",              "Step 8: wrong case"
print(f"VERIFIED  p={p}  D={D}  case={entry['case']}")
```

Run:

```
python -c "exec(open('VERIFY.md').read().split('python\n')[1].split('\n```')[0])"
```

or copy the block into any Python 3 session with `sympy` installed.

Expected output:

```
VERIFIED  p=-5  D=25/4  case=warrant_debt
```

---

## Additional check: the admissible case

The certificate also contains `r = [1,1,1,3]` with `case = globally_admissible`.
The same steps give $p = \langle h, r\rangle = -1-1-1+3 = 0$, so $r^{\text{debt}} = 0$
and $D = 0$. The verdict is correct because there is no nonzero harmonic component.
