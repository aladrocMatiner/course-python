"""A small execution port expressed by ordinary Python behavior."""


class Result:
    def __init__(self, job_id, status):
        self.job_id = job_id
        self.status = status

    def summary(self):
        return f"{self.job_id}:{self.status}"


class BoundaryError(Exception):
    pass


class DependencyUnavailable(Exception):
    pass


class JobApplication:
    """Depend only on an object that can execute(job_id, payload)."""

    def __init__(self, execution_port):
        if not callable(getattr(execution_port, "execute", None)):
            raise TypeError("execution port must provide execute(job_id, payload)")
        self.execution_port = execution_port

    def submit(self, job_id, payload):
        result = self.execution_port.execute(job_id, payload)
        if not isinstance(result, Result) or result.job_id != job_id:
            raise BoundaryError("execution port returned an invalid result")
        return result


class LocalExecutionAdapter:
    def execute(self, job_id, payload):
        if not isinstance(payload, str) or not payload.strip():
            raise ValueError("payload must be non-empty text")
        return Result(job_id, "completed")


class BrokenAdapter:
    def execute(self, job_id, payload):
        del job_id, payload
        return {"status": "completed"}


class UnavailableAdapter:
    """Fail before accepting work, so this teaching fallback is unambiguous."""

    def execute(self, job_id, payload):
        del job_id, payload
        raise DependencyUnavailable("dependency is temporarily unavailable")


def main():
    local = JobApplication(LocalExecutionAdapter())
    print(local.submit("job-1", "pack books").summary())

    try:
        JobApplication(BrokenAdapter()).submit("job-2", "pack pens")
    except BoundaryError as error:
        print(f"boundary:{error}")

    try:
        JobApplication(UnavailableAdapter()).submit("job-3", "pack paper")
    except DependencyUnavailable as error:
        print(f"recoverable:{error}")
    print(f"fallback:{local.submit('job-3', 'pack paper').summary()}")


if __name__ == "__main__":
    main()
