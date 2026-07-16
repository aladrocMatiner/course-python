"""Direct working baseline and the short transfer exercise."""

from .domain import DecisionRecord, PatternError, Result, UnknownSelection
from .domain import require_job


MAX_SHIPPING_DISTANCE = 100


def run(job):
    """Execute one job directly, with no pattern object or global state."""

    job = require_job(job)
    return Result(
        job.job_id,
        "completed",
        f"processed:{job.payload}",
    )


def validate_distance(distance_km):
    if (
        isinstance(distance_km, bool)
        or not isinstance(distance_km, int)
        or not 0 <= distance_km <= MAX_SHIPPING_DISTANCE
    ):
        raise PatternError(
            "invalid_distance",
            f"distance_km must be from 0 to {MAX_SHIPPING_DISTANCE}",
        )
    return distance_km


def shipping_cost_direct(distance_km, express=False):
    """Keep one clear branch while the transfer problem has two choices."""

    distance_km = validate_distance(distance_km)
    if not isinstance(express, bool):
        raise PatternError("invalid_service", "express must be true or false")
    if express:
        return 8 + (2 * distance_km)
    return 5 + distance_km


def transfer_decision(pattern_name=None):
    """Build a complete decision record for either valid transfer solution."""

    shared = {
        "problem": "calculate a bounded shipping fee",
        "forces": (
            "the caller owns service selection",
            "the calculation must stay deterministic",
        ),
        "expected_failure": "an invalid distance is rejected before calculation",
        "verification": "normal, boundary, and recovery tests pass",
    }
    if pattern_name is None:
        return DecisionRecord(
            **shared,
            simplest_option="one function with one explicit branch",
            pattern=None,
            cost="the branch grows if service policies multiply",
            remove_when="replace it only after a third changing policy appears",
        )
    if pattern_name == "Strategy":
        return DecisionRecord(
            **shared,
            simplest_option="one function with one explicit branch",
            pattern="Strategy",
            cost="the caller must pass and name a policy callable",
            remove_when="return to the branch when policies stop varying",
        )
    raise UnknownSelection(pattern_name)
