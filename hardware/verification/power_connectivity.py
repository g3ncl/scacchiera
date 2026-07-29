"""Extract the power board connector and no-connect nets as JSON."""

import json

from skidl import Circuit, Part

from hardware.pcb.power import NO_CONNECTS, build_power


def _part(circuit: Circuit, reference: str) -> Part:
    return next(part for part in circuit.parts if str(part.ref) == reference)


def _pin_net(circuit: Circuit, reference: str, pin: str) -> str:
    return str(_part(circuit, reference)[pin].net.name)


def power_connectivity() -> dict[str, dict[str, list[str]]]:
    circuit = build_power()
    return {
        "connectors": {
            reference: [
                _pin_net(circuit, reference, str(pin))
                for pin in range(1, pin_count + 1)
            ]
            for reference, pin_count in {"J1": 7, "J2": 8, "J3": 2}.items()
        },
        "no_connects": {
            reference: [_pin_net(circuit, reference, pin) for pin in pins]
            for reference, pins in NO_CONNECTS.items()
        },
    }


if __name__ == "__main__":
    print(json.dumps(power_connectivity()))
