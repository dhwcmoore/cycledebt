#!/usr/bin/env python3
"""Mock HELICS federate publishing the A_Sensor → B_Controller seam residue."""

import helics


def main() -> None:
    info = helics.helicsCreateFederateInfo()
    helics.helicsFederateInfoSetCoreTypeFromString(info, "zmq")
    helics.helicsFederateInfoSetTimeProperty(info, helics.HELICS_PROPERTY_TIME_PERIOD, 1.0)
    fed = helics.helicsCreateValueFederate("A_Sensor", info)
    pub = helics.helicsFederateRegisterGlobalPublication(
        fed,
        "A_Sensor-B_Controller/residue",
        helics.HELICS_DATA_TYPE_STRING,
    )

    helics.helicsFederateEnterInitializingMode(fed)
    helics.helicsFederateEnterExecutingMode(fed)

    for target_time, value in ((1.0, "1"), (2.0, "1")):
        current_time = helics.helicsFederateRequestTime(fed, target_time)
        helics.helicsPublicationPublishString(pub, value)
        print(f"[A_Sensor] t={current_time}: published {value}")

    helics.helicsFederateFinalize(fed)
    helics.helicsFederateFree(fed)


if __name__ == "__main__":
    main()
