"""Build and connect an application in one explicit outer function."""


class SequentialIds:
    def __init__(self):
        self.next_number = 1

    def __call__(self):
        value = f"job-{self.next_number}"
        self.next_number += 1
        return value


class DirectExecutor:
    def execute(self, job_id, payload):
        return f"completed:{job_id}:{payload}"


class JobApplication:
    def __init__(self, new_id, executor, write):
        self.new_id = new_id
        self.executor = executor
        self.write = write

    def submit(self, payload):
        if not isinstance(payload, str) or not payload.strip():
            raise ValueError("payload must be non-empty text")
        job_id = self.new_id()
        result = self.executor.execute(job_id, payload.strip())
        self.write(result)
        return result


def build_application(write):
    """Composition root: choose concrete collaborators only here."""

    if not callable(write):
        raise TypeError("write must be callable")
    return JobApplication(
        new_id=SequentialIds(),
        executor=DirectExecutor(),
        write=write,
    )


def main():
    messages = []
    application = build_application(messages.append)
    print(application.submit("pack books"))
    print(f"owned-output:{messages}")

    try:
        application.submit("")
    except ValueError as error:
        print(f"boundary:{error}")
    print(f"recovered:{application.submit('pack pens')}")


if __name__ == "__main__":
    main()
