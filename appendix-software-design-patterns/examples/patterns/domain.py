"""Small domain values shared by the Appendix C core examples.

The classes are deliberately explicit.  Learners can read them after the
course's class chapter without first learning ``dataclasses``.
"""


MAX_JOB_ID_LENGTH = 32
MAX_PAYLOAD_LENGTH = 256


class PatternError(Exception):
    """Base error with a stable code suitable for tests and recovery."""

    def __init__(self, code, message):
        self.code = code
        super().__init__(f"{code}: {message}")


class InvalidJob(PatternError):
    """Raised when a job cannot be created or executed safely."""

    def __init__(self, message):
        super().__init__("invalid_job", message)


class InvalidDecisionRecord(PatternError):
    """Raised when a pattern decision omits evidence needed for review."""

    def __init__(self, message):
        super().__init__("invalid_decision_record", message)


class UnknownSelection(PatternError):
    """Raised when configuration names an unavailable choice."""

    def __init__(self, selection):
        self.selection = selection
        super().__init__("unknown_selection", f"unknown choice: {selection!r}")


class ExecutionBoundaryError(PatternError):
    """A stable application error translated from a collaborator boundary."""


def _required_text(value, field, maximum=None):
    if not isinstance(value, str) or not value.strip():
        raise InvalidJob(f"{field} must be a non-empty string")
    if maximum is not None and len(value) > maximum:
        raise InvalidJob(f"{field} must contain at most {maximum} characters")
    return value


def validate_payload(payload):
    """Validate payload before an outer layer consumes an identifier."""

    return _required_text(payload, "payload", MAX_PAYLOAD_LENGTH)


def require_job(job):
    """Return *job* or raise the core's stable invalid-input error."""

    if not isinstance(job, Job):
        raise InvalidJob("run expects a Job instance")
    return job


class Job:
    """One synthetic unit of work."""

    def __init__(self, job_id, payload):
        self.job_id = _required_text(
            job_id,
            "job_id",
            MAX_JOB_ID_LENGTH,
        )
        self.payload = validate_payload(payload)

    def __eq__(self, other):
        return (
            isinstance(other, Job)
            and self.job_id == other.job_id
            and self.payload == other.payload
        )

    def __repr__(self):
        return f"Job(job_id={self.job_id!r}, payload={self.payload!r})"


class Result:
    """The stable observable result returned by every core executor."""

    def __init__(self, job_id, status, output):
        self.job_id = _required_text(
            job_id,
            "job_id",
            MAX_JOB_ID_LENGTH,
        )
        self.status = _required_text(status, "status")
        self.output = _required_text(output, "output")

    def __eq__(self, other):
        return (
            isinstance(other, Result)
            and self.job_id == other.job_id
            and self.status == other.status
            and self.output == other.output
        )

    def __repr__(self):
        return (
            "Result("
            f"job_id={self.job_id!r}, "
            f"status={self.status!r}, "
            f"output={self.output!r})"
        )


class DecisionRecord:
    """Evidence for choosing a pattern or deliberately keeping direct code."""

    def __init__(
        self,
        *,
        problem,
        forces,
        simplest_option,
        pattern,
        cost,
        expected_failure,
        verification,
        remove_when,
    ):
        self.problem = self._text(problem, "problem")
        self.forces = self._forces(forces)
        self.simplest_option = self._text(
            simplest_option,
            "simplest_option",
        )
        if pattern is not None:
            pattern = self._text(pattern, "pattern")
        self.pattern = pattern
        self.cost = self._text(cost, "cost")
        self.expected_failure = self._text(
            expected_failure,
            "expected_failure",
        )
        self.verification = self._text(verification, "verification")
        self.remove_when = self._text(remove_when, "remove_when")

    @staticmethod
    def _text(value, field):
        if not isinstance(value, str) or not value.strip():
            raise InvalidDecisionRecord(f"{field} must be a non-empty string")
        return value

    @classmethod
    def _forces(cls, values):
        if isinstance(values, str):
            raise InvalidDecisionRecord("forces must be a sequence of strings")
        try:
            forces = tuple(values)
        except TypeError as error:
            raise InvalidDecisionRecord(
                "forces must be a sequence of strings"
            ) from error
        if not forces:
            raise InvalidDecisionRecord("forces must not be empty")
        for force in forces:
            cls._text(force, "force")
        return forces

    def as_dict(self):
        """Return the stable eight-field review shape used by exercises."""

        return {
            "problem": self.problem,
            "forces": self.forces,
            "simplest_option": self.simplest_option,
            "pattern": self.pattern,
            "cost": self.cost,
            "expected_failure": self.expected_failure,
            "verification": self.verification,
            "remove_when": self.remove_when,
        }
