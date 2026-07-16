"""Read the State transitions owned by the canonical Circuit Breaker example."""

import importlib.util
from pathlib import Path


def load_circuit_breaker_owner():
    """Load the fixed sibling companion without accepting an external path."""
    appendix_root = Path(__file__).resolve().parents[1]
    owner_path = (
        appendix_root / "network - Circuit Breaker" / "example.py"
    ).resolve()
    if owner_path.parents[1] != appendix_root or not owner_path.is_file():
        raise RuntimeError("canonical Circuit Breaker companion is unavailable")

    specification = importlib.util.spec_from_file_location(
        "appendix_c_network_circuit_breaker_owner",
        owner_path,
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("canonical Circuit Breaker companion cannot be loaded")
    owner = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(owner)
    return owner


def main():
    owner = load_circuit_breaker_owner()
    clock = owner.FakeClock()
    breaker = owner.CircuitBreaker(clock)

    print(f"initial={breaker.state.name}")

    for _number in range(owner.FAILURE_THRESHOLD):
        try:
            breaker.call(
                owner.ScriptedDependency([owner.TransientFailure("temporary")])
            )
        except owner.TransientFailure:
            pass
    print(
        f"threshold={breaker.state.name} "
        f"failures={breaker.consecutive_failures}"
    )

    blocked = owner.ScriptedDependency(["must-not-run"])
    try:
        breaker.call(blocked)
    except owner.CircuitOpen as error:
        print(f"boundary={error} dependency_calls={blocked.calls}")

    failed_probe_states = []

    def failed_probe():
        failed_probe_states.append(breaker.state.name)
        raise owner.TransientFailure("probe-failed")

    clock.advance(owner.COOLDOWN_SECONDS)
    try:
        breaker.call(failed_probe)
    except owner.TransientFailure:
        print(
            f"failed-probe-observed={failed_probe_states[0]} "
            f"after={breaker.state.name}"
        )

    recovery_probe_states = []

    def healthy_probe():
        recovery_probe_states.append(breaker.state.name)
        return "healthy"

    clock.advance(owner.COOLDOWN_SECONDS)
    result = breaker.call(healthy_probe)
    print(
        f"recovery-probe-observed={recovery_probe_states[0]} "
        f"result={result} after={breaker.state.name}"
    )


if __name__ == "__main__":
    main()
