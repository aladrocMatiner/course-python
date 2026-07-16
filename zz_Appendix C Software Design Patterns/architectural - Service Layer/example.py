"""A tiny Service Layer client; Chapter 28 owns the implementation."""


class ServiceBusy(Exception):
    pass


class CompletionResult:
    """The application-facing result value for this one use case."""

    def __init__(self, job_id, status):
        self.job_id = job_id
        self.status = status


class ServiceContractError(RuntimeError):
    def __init__(self):
        self.code = "invalid_service_result"
        super().__init__("service returned an invalid completion result")


def complete_job(service, job_id):
    """Client code asks for one use case instead of coordinating storage."""

    if not isinstance(job_id, str) or not job_id.strip():
        raise ValueError("job_id must be non-empty text")
    result = service.complete(job_id)
    if (
        not isinstance(result, CompletionResult)
        or result.job_id != job_id
        or result.status != "completed"
    ):
        raise ServiceContractError()
    return f"{result.job_id}:{result.status}"


class FakeJobService:
    """A controlled collaborator; it is not the Service Layer itself."""

    def __init__(self, failure=None):
        self.failure = failure
        self.calls = []

    def complete(self, job_id):
        self.calls.append(job_id)
        if self.failure is not None:
            raise self.failure
        return CompletionResult(job_id, "completed")


class MalformedService:
    def complete(self, job_id):
        return CompletionResult(job_id, "pending")


def main():
    service = FakeJobService()
    print(complete_job(service, "job-1"))
    print(f"calls:{service.calls}")

    try:
        complete_job(service, "")
    except ValueError as error:
        print(f"boundary:{error}")

    try:
        complete_job(MalformedService(), "job-2")
    except ServiceContractError as error:
        print(f"malformed:{error.code}")

    busy = FakeJobService(failure=ServiceBusy("try later"))
    try:
        complete_job(busy, "job-2")
    except ServiceBusy as error:
        print(f"recoverable:{error}")
    print(f"recovered:{complete_job(service, 'job-2')}")


if __name__ == "__main__":
    main()
