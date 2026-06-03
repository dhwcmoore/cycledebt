#!/usr/bin/env python3
"""HELICS auditor federate that computes CycleDebt certificates at each time step."""

import json
import subprocess
import sys
from pathlib import Path

import helics

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from cyclediagnostic_demo import analyse, verify_from_file, write_certificate  # noqa: E402


EDGE_NAMES = [
    "A_Sensor-B_Controller",
    "B_Controller-C_Actuator",
    "C_Actuator-D_Monitor",
    "A_Sensor-D_Monitor",
]


def make_model(residue_values: list[str]) -> dict:
    return {
        "name": "helics_demo_case",
        "system_name": "four-node CPS diagnostic loop (HELICS wrapper)",
        "diagnostic_claim": {
            "statement": "fault_origin = B_Controller",
        },
        "observation_note": "HELICS publishes the seam residues for the co-simulation diagnostic loop.",
        "regions": ["A_Sensor", "B_Controller", "C_Actuator", "D_Monitor"],
        "edges": [
            ["A_Sensor", "B_Controller"],
            ["B_Controller", "C_Actuator"],
            ["C_Actuator", "D_Monitor"],
            ["A_Sensor", "D_Monitor"],
        ],
        "faces": [],
        "residue": {edge: value for edge, value in zip(EDGE_NAMES, residue_values)},
    }


def main() -> None:
    info = helics.helicsCreateFederateInfo()
    helics.helicsFederateInfoSetCoreTypeFromString(info, "zmq")
    helics.helicsFederateInfoSetTimeProperty(info, helics.HELICS_PROPERTY_TIME_PERIOD, 1.0)
    fed = helics.helicsCreateValueFederate("CycleDebt_Auditor", info)

    subs = [
        helics.helicsFederateRegisterSubscription(fed, f"{edge}/residue")
        for edge in EDGE_NAMES
    ]
    verdict_pub = helics.helicsFederateRegisterGlobalPublication(
        fed, "CycleDebt/verdict", helics.HELICS_DATA_TYPE_STRING
    )
    period_pub = helics.helicsFederateRegisterGlobalPublication(
        fed, "CycleDebt/period", helics.HELICS_DATA_TYPE_STRING
    )
    debt_pub = helics.helicsFederateRegisterGlobalPublication(
        fed, "CycleDebt/debt_norm_squared", helics.HELICS_DATA_TYPE_STRING
    )
    cert_pub = helics.helicsFederateRegisterGlobalPublication(
        fed, "CycleDebt/certificate_path", helics.HELICS_DATA_TYPE_STRING
    )
    verified_pub = helics.helicsFederateRegisterGlobalPublication(
        fed, "CycleDebt/verified", helics.HELICS_DATA_TYPE_STRING
    )

    helics.helicsFederateEnterInitializingMode(fed)
    helics.helicsFederateEnterExecutingMode(fed)

    for target_time in (1.0, 2.0, 3.0):
        current_time = helics.helicsFederateRequestTime(fed, target_time)

        if current_time < 2.0:
            continue

        residue_values = [helics.helicsInputGetString(sub) for sub in subs]
        model = make_model(residue_values)
        result = analyse(model)

        cert_path = REPO_ROOT / "helics_demo" / "outputs" / "certificates" / f"t{int(current_time):03d}_certificate.json"
        cert_path.parent.mkdir(parents=True, exist_ok=True)
        write_certificate(model, result, cert_path)
        verify_ok, _ = verify_from_file(cert_path)

        subprocess.run(
            ["./run_extracted", str(cert_path)],
            cwd=REPO_ROOT / "coq",
            check=False,
            capture_output=True,
            text=True,
        )

        verdict = result["case"]
        period = result["p_periods"][0] if result.get("p_periods") else "0"
        debt = result["debt_norm_squared"]

        print(f"[CycleDebt_Auditor] t={current_time}: verdict={verdict}, period={period}, D={debt}, verified={verify_ok}")

        helics.helicsPublicationPublishString(verdict_pub, verdict)
        helics.helicsPublicationPublishString(period_pub, period)
        helics.helicsPublicationPublishString(debt_pub, debt)
        helics.helicsPublicationPublishString(cert_pub, str(cert_path.relative_to(REPO_ROOT)))
        helics.helicsPublicationPublishString(verified_pub, str(verify_ok).lower())

    helics.helicsFederateFinalize(fed)
    helics.helicsFederateFree(fed)


if __name__ == "__main__":
    main()
