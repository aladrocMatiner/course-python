"""Essential Strategy, function Factory, and Adapter examples."""

from .direct import run, validate_distance
from .domain import (
    ExecutionBoundaryError,
    Job,
    PatternError,
    Result,
    UnknownSelection,
    require_job,
)


def keep_payload(job):
    """Strategy that keeps the direct baseline unchanged."""

    return require_job(job)


def uppercase_payload(job):
    """Strategy that creates a job with normalized uppercase payload."""

    job = require_job(job)
    return Job(job.job_id, job.payload.upper())


def select_policy(name):
    """Select a policy without executing or constructing an executor."""

    policies = {
        "keep": keep_payload,
        "uppercase": uppercase_payload,
    }
    try:
        return policies[name]
    except (KeyError, TypeError) as error:
        raise UnknownSelection(name) from error


def run_with_policy(job, policy):
    """Execute with an injected callable Strategy."""

    if not callable(policy):
        raise PatternError("invalid_policy", "policy must be callable")
    selected_job = policy(require_job(job))
    return run(require_job(selected_job))


class DirectExecutor:
    """Direct construction remains enough when only one behavior is needed."""

    def execute(self, job):
        return run(job)


class PolicyExecutor:
    """Executor whose varying decision is supplied as a callable."""

    def __init__(self, policy):
        if not callable(policy):
            raise PatternError("invalid_policy", "policy must be callable")
        self.policy = policy

    def execute(self, job):
        return run_with_policy(job, self.policy)


def build_executor(name):
    """Validating function Factory for the two configured executors."""

    if name == "direct":
        return DirectExecutor()
    if name == "uppercase":
        return PolicyExecutor(uppercase_payload)
    raise UnknownSelection(name)


class LegacyRunnerError(Exception):
    """Error shape owned by the deliberately incompatible fake."""


class LegacyRunnerFake:
    """Small deterministic collaborator with a legacy method/data shape."""

    def __init__(self, failure=None, response=None):
        self.failure = failure
        self.response = response
        self.calls = []

    def process(self, identifier, contents):
        self.calls.append((identifier, contents))
        if self.failure is not None:
            raise self.failure
        if self.response is not None:
            return self.response
        return {
            "identifier": identifier,
            "state": "DONE",
            "body": f"processed:{contents}",
        }


class LegacyRunnerAdapter:
    """Translate one legacy method, data shape, and error boundary."""

    def __init__(self, legacy_runner):
        process = getattr(legacy_runner, "process", None)
        if not callable(process):
            raise ExecutionBoundaryError(
                "invalid_legacy_runner",
                "legacy runner must provide process(identifier, contents)",
            )
        self.legacy_runner = legacy_runner

    def execute(self, job):
        job = require_job(job)
        try:
            reply = self.legacy_runner.process(job.job_id, job.payload)
        except LegacyRunnerError as error:
            raise ExecutionBoundaryError(
                "legacy_failure",
                "legacy runner could not execute the job",
            ) from error

        if not self._valid_reply(reply, job.job_id):
            raise ExecutionBoundaryError(
                "invalid_legacy_result",
                "legacy runner returned an incompatible result",
            )
        return Result(reply["identifier"], "completed", reply["body"])

    @staticmethod
    def _valid_reply(reply, job_id):
        return (
            isinstance(reply, dict)
            and reply.get("identifier") == job_id
            and reply.get("state") == "DONE"
            and isinstance(reply.get("body"), str)
            and bool(reply["body"].strip())
        )


def standard_shipping(distance_km):
    """Callable Strategy for standard shipping."""

    return 5 + distance_km


def express_shipping(distance_km):
    """Callable Strategy for express shipping."""

    return 8 + (2 * distance_km)


def shipping_cost_with_policy(distance_km, policy):
    """Transfer solution justified only when shipping policies vary."""

    distance_km = validate_distance(distance_km)
    if not callable(policy):
        raise PatternError("invalid_policy", "policy must be callable")
    return policy(distance_km)
