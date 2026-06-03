# Release history

---

## v0.6-self-contained-verification

This release completes the finite-nerve warrant-debt pipeline. The project now
presents a six-layer structure:

| Layer | Role |
|---|---|
| 1 | General finite graph theorem |
| 2 | Finite nerve / Hodge extension |
| 3 | Four-cycle corollary |
| 4 | Admissibility bridge |
| 5 | Dynamic warrant debt |
| 6 | Exact certificate and independent verifier |

Certificates now contain exact rational Hodge data (`L1_matrix`,
`harmonic_basis_vectors`, `p_periods`, `r_debt_vector`, `debt_norm_squared`).
The standalone verifier (`verify_certificate.py`) reconstructs each verdict from
the certificate alone, without importing or re-running the engine.

The six-layer vocabulary is consistent across `README.md`, `PROOF.md §9`,
`VERIFY.md`, and `jact_full.tex` Discussion. The Python blocks in `VERIFY.md`
and Appendix A of the manuscript are byte-for-byte identical (normalised).

Run `python verify_certificate.py` to verify the actual object certificate
independently. Expected output: `ALL VERIFIED`.

---

## v0.5-finite-nerve-warrant-debt

Extended the obstruction theory from finite graphs to arbitrary finite nerves
via the Hodge Laplacian $L_1 = \delta^0(\delta^0)^T + (\delta^1)^T\delta^1$.
The harmonic 1-cochain space $\mathcal{H}^1 = \ker(L_1)$ correctly accounts
for faces that kill apparent graph cycles. Warrant debt is
$D(r) = \|P_{\mathcal{H}^1}r\|^2$.

The Finite Nerve Warrant Debt Theorem (PROOF.md §0c) gives three formally
accountable certificate cases (`coherence_failure`, `globally_admissible`,
`warrant_debt`). Engine: `finite_nerve_warrant_debt.py`.

---

## v0.4-warrant-debt-pipeline

Added the admissibility bridge, harmonic decomposition, dynamic warrant debt
trajectories, and the Gram matrix formula $D = p^T G^{-1} p$. The pipeline:
$r_t \to [r_t] \to p(t) \to D(t)$.

For the four-cycle: $D(t) = p(t)^2/4$; actual object has $p=-5$, $D=25/4$.

---

## v0.3-ci-verified

Added GitHub Actions CI, property-based tests, and reproducible execution via
`requirements.txt`. All tests run automatically on push.

---

## v0.2-proof-witnesses

Added cycle witnesses, admissible refinement theorem (cycle-lift persistence),
rank criterion for cycle-faithfulness, and four refinement test cases.

---

## v0.1-frozen-residue-obstruction

Initial release. Proof that $r=(1,1,1,-2)$ represents a nonzero $H^1$ class on
the four-region loop nerve, with JSON certificate and invariance tests.

---

## Zenodo / archiving instructions

To archive a release with a permanent DOI:

1. Ensure `requirements.txt` lists all Python dependencies (`sympy`).
2. Update `CITATION.cff` with the current version tag and release date.
3. Push the tag to GitHub and create a GitHub Release with this text.
4. Enable Zenodo integration at https://zenodo.org/ (Account → GitHub integrations).
5. Zenodo mints a DOI automatically on GitHub Release creation.
6. Add the DOI badge and `doi:` field to `CITATION.cff` and `README.md`.
