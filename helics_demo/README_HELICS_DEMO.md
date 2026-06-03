# HELICS demo wrapper for CycleDebt

This folder adds a minimal HELICS federation that mirrors the existing four-cycle CPS demo.

## What it does

- Four mock federates publish seam residues for the diagnostic loop.
- The `CycleDebt_Auditor` federate subscribes to those residues, computes the exact certificate, writes it to disk, and verifies it with the Rocq-extracted checker.
- The auditor publishes a small diagnostic stream for the federation:
  - `CycleDebt/verdict`
  - `CycleDebt/period`
  - `CycleDebt/debt_norm_squared`
  - `CycleDebt/certificate_path`
  - `CycleDebt/verified`

## Run

From the repository root:

```bash
helics run --path=helics_demo/runner.json
```

The first audit checkpoint reports the warrant-debt residues (`-2`) and the second reports the refined residues (`3`). In this minimal HELICS time-step schedule the two audit points appear as the next available grants after the publication exchange, which are logged as `t=2.0` and `t=3.0`.
