"""Advanced explicit composition with one job-execution port."""

from .direct import run
from .domain import (
    ExecutionBoundaryError,
    Job,
    PatternError,
    Result,
    validate_payload,
)


class InMemoryExecutionAdapter:
    """Adapt a local callable to the execution port's ``execute`` shape."""

    def __init__(self, runner=run):
        if not callable(runner):
            raise PatternError("invalid_runner", "runner must be callable")
        self.runner = runner

    def execute(self, job):
        return self.runner(job)


class JobApplication:
    """Coordinate injected time, identifiers, output, and execution."""

    def __init__(self, *, execution_port, new_id, clock, write):
        execute = getattr(execution_port, "execute", None)
        if not callable(execute):
            raise PatternError(
                "invalid_execution_port",
                "execution_port must provide execute(job)",
            )
        for name, collaborator in (
            ("new_id", new_id),
            ("clock", clock),
            ("write", write),
        ):
            if not callable(collaborator):
                raise PatternError(
                    "invalid_dependency",
                    f"{name} must be callable",
                )
        self.execution_port = execution_port
        self.new_id = new_id
        self.clock = clock
        self.write = write

    def submit(self, payload):
        """Validate first, then consume dependencies in an explicit order."""

        payload = validate_payload(payload)
        job = Job(self.new_id(), payload)
        result = self.execution_port.execute(job)
        if not isinstance(result, Result) or result.job_id != job.job_id:
            raise ExecutionBoundaryError(
                "invalid_execution_result",
                "execution port must return a Result for the submitted job",
            )
        self.write(
            f"{self.clock():.3f}|{result.job_id}|{result.status}"
        )
        return result


def compose_application(*, execution_port, new_id, clock, write):
    """Composition root: create the application only at the outer boundary."""

    return JobApplication(
        execution_port=execution_port,
        new_id=new_id,
        clock=clock,
        write=write,
    )


class SequenceIds:
    """Deterministic identifier fake used by examples and learner tests."""

    def __init__(self, values):
        self.values = tuple(values)
        self.position = 0

    def __call__(self):
        if self.position >= len(self.values):
            raise PatternError(
                "id_source_exhausted",
                "the deterministic identifier source is empty",
            )
        value = self.values[self.position]
        self.position += 1
        return value


class FixedClock:
    """Deterministic time fake; it never reads the host clock."""

    def __init__(self, value):
        self.value = value

    def __call__(self):
        return self.value


class ListOutput:
    """In-memory output fake with an observable, bounded-by-caller list."""

    def __init__(self):
        self.messages = []

    def __call__(self, message):
        self.messages.append(message)
