"""A tiny Repository client; Chapters 17 and 28 own the full pattern."""


class JobStatus:
    """The small domain value returned across this teaching boundary."""

    def __init__(self, job_id, status):
        self.job_id = job_id
        self.status = status


class RepositoryContractError(RuntimeError):
    def __init__(self):
        self.code = "invalid_repository_result"
        super().__init__("repository returned an invalid job status")


def job_summary(repository, job_id):
    """Use the smallest read operation needed by this client."""

    if not isinstance(job_id, str) or not job_id.strip():
        raise ValueError("job_id must be non-empty text")
    record = repository.get(job_id)
    if record is None:
        return f"{job_id}:not-found"
    if (
        not isinstance(record, JobStatus)
        or record.job_id != job_id
        or record.status not in {"queued", "completed"}
    ):
        raise RepositoryContractError()
    return f"{record.job_id}:{record.status}"


class FakeRepository:
    """A bounded test collaborator, not a persistence tutorial."""

    def __init__(self, records=None, failure=None):
        self.records = dict(records or {})
        self.failure = failure

    def get(self, job_id):
        if self.failure is not None:
            raise self.failure
        return self.records.get(job_id)


class MalformedRepository:
    def get(self, job_id):
        del job_id
        return "completed"


def main():
    repository = FakeRepository({"job-1": JobStatus("job-1", "completed")})
    print(job_summary(repository, "job-1"))
    print(job_summary(repository, "job-2"))

    try:
        job_summary(repository, "")
    except ValueError as error:
        print(f"boundary:{error}")

    try:
        job_summary(MalformedRepository(), "job-3")
    except RepositoryContractError as error:
        print(f"malformed:{error.code}")

    unavailable = FakeRepository(failure=RuntimeError("storage unavailable"))
    try:
        job_summary(unavailable, "job-3")
    except RuntimeError as error:
        print(f"recoverable:{error}")
    print(f"recovered:{job_summary(repository, 'job-1')}")


if __name__ == "__main__":
    main()
