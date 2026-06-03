#!/usr/bin/env bash
set -euo pipefail

./coq/run_extracted helics_demo/outputs/certificates/t002_certificate.json
./coq/run_extracted helics_demo/outputs/certificates/t003_certificate.json

python verify_certificate.py helics_demo/outputs/certificates/t002_certificate.json
python verify_certificate.py helics_demo/outputs/certificates/t003_certificate.json
