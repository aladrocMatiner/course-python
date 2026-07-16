"""A small, offline Adapter example for an incompatible job runner."""


class Job:
    def __init__(self, job_id, payload):
        self.job_id = job_id
        self.payload = payload


class Result:
    def __init__(self, job_id, status, output):
        self.job_id = job_id
        self.status = status
        self.output = output

    def summary(self):
        return f"{self.job_id}:{self.status}:{self.output}"


class LegacyRunnerError(Exception):
    """The error type owned by the incompatible collaborator."""


class ExecutionBoundaryError(Exception):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


class LegacyRunner:
    """A deterministic fake with a legacy method and reply shape."""

    def __init__(self, reply=None, failure=None):
        self.reply = reply
        self.failure = failure

    def process(self, identifier, contents):
        if self.failure is not None:
            raise self.failure
        if self.reply is not None:
            return self.reply
        return {
            "identifier": identifier,
            "state": "DONE",
            "body": contents.upper(),
        }


class LegacyRunnerAdapter:
    """Present execute(Job) while translating the legacy boundary."""

    def __init__(self, legacy_runner):
        if not callable(getattr(legacy_runner, "process", None)):
            raise ExecutionBoundaryError(
                "invalid_runner",
                "legacy runner must provide process(identifier, contents)",
            )
        self.legacy_runner = legacy_runner

    def execute(self, job):
        if not isinstance(job, Job):
            raise ExecutionBoundaryError("invalid_job", "expected a Job")
        try:
            reply = self.legacy_runner.process(job.job_id, job.payload)
        except LegacyRunnerError as error:
            raise ExecutionBoundaryError(
                "legacy_failure",
                "legacy runner could not execute the job",
            ) from error

        if not self._valid_reply(reply, job.job_id):
            raise ExecutionBoundaryError(
                "invalid_reply",
                "legacy runner returned an incompatible reply",
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


def main():
    healthy = LegacyRunnerAdapter(LegacyRunner())
    print(healthy.execute(Job("job-1", "pack books")).summary())

    malformed = LegacyRunnerAdapter(
        LegacyRunner(reply={"identifier": "wrong", "state": "DONE", "body": "x"})
    )
    try:
        malformed.execute(Job("job-2", "pack pens"))
    except ExecutionBoundaryError as error:
        print(f"boundary:{error.code}")

    failing = LegacyRunnerAdapter(
        LegacyRunner(failure=LegacyRunnerError("offline"))
    )
    try:
        failing.execute(Job("job-3", "pack paper"))
    except ExecutionBoundaryError as error:
        print(f"recoverable:{error.code}:cause={type(error.__cause__).__name__}")
    print(f"recovered:{healthy.execute(Job('job-4', 'pack folders')).summary()}")


if __name__ == "__main__":
    main()
