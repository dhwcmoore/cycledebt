# Verified HELICS Run

Command:

```bash
helics run --path=helics_demo/runner.json
```

Observed results:

```text
t=2.0: verdict=warrant_debt, period=-5, D=25/4, python_verified=True, extracted_verified=True, verified=True
t=3.0: verdict=globally_admissible, period=0, D=0, python_verified=True, extracted_verified=True, verified=True
```

Generated certificates:

```text
helics_demo/outputs/certificates/t002_certificate.json
helics_demo/outputs/certificates/t003_certificate.json
```

Verifier:

```text
Rocq-extracted verifier, generated from coq/DebtCertificate.v using Extract.v.
```
