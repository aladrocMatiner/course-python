"""Explicit dependency injection with plain constructor arguments."""


class JobApplication:
    def __init__(self, new_id, clock, write, execute):
        dependencies = {
            "new_id": new_id,
            "clock": clock,
            "write": write,
            "execute": execute,
        }
        for name, dependency in dependencies.items():
            if not callable(dependency):
                raise TypeError(f"{name} must be callable")
        self.new_id = new_id
        self.clock = clock
        self.write = write
        self.execute = execute

    def submit(self, payload):
        if not isinstance(payload, str) or not payload.strip():
            raise ValueError("payload must be non-empty text")
        job_id = self.new_id()
        result = self.execute(job_id, payload.strip())
        self.write(f"{self.clock()}|{job_id}|{result}")
        return result


class OneId:
    def __init__(self, value):
        self.value = value
        self.used = False

    def __call__(self):
        if self.used:
            raise RuntimeError("fake ID source exhausted")
        self.used = True
        return self.value


def main():
    messages = []
    application = JobApplication(
        new_id=OneId("job-1"),
        clock=lambda: "12:00",
        write=messages.append,
        execute=lambda job_id, payload: f"completed:{job_id}:{payload}",
    )
    print(application.submit("pack books"))
    print(f"output:{messages[0]}")

    try:
        JobApplication(None, lambda: "12:00", messages.append, print)
    except TypeError as error:
        print(f"boundary:{error}")

    recovered = JobApplication(
        OneId("job-2"), lambda: "12:01", messages.append,
        lambda job_id, payload: f"completed:{job_id}:{payload}",
    )
    print(f"recovered:{recovered.submit('pack pens')}")


if __name__ == "__main__":
    main()
