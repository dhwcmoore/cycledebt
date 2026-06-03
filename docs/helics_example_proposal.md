# HELICS example proposal

This is proposed as an external example / use case, not as a HELICS core feature.

CycleDebt_Auditor is a HELICS observer federate. It subscribes to seam residues, emits obstruction certificates, and verifies them using the Rocq-extracted checker.

The demo is intentionally minimal: four mock federates, one auditor, and two diagnostic time steps.
