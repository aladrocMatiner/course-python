"""A small Facade contrast around three deterministic subsystem steps."""


class Validator:
    def check(self, payload):
        if not isinstance(payload, str) or not payload.strip():
            raise ValueError("payload must be non-empty text")
        return payload.strip()


class MemoryStore:
    def __init__(self):
        self.items = []

    def save(self, payload):
        job_id = f"job-{len(self.items) + 1}"
        self.items.append((job_id, payload))
        return job_id


class AuditLog:
    def __init__(self):
        self.entries = []

    def record(self, job_id):
        self.entries.append(f"submitted:{job_id}")


def submit_job(payload, validator, store, audit):
    """Simpler module function: prefer this until several clients need an API."""

    clean_payload = validator.check(payload)
    job_id = store.save(clean_payload)
    audit.record(job_id)
    return job_id


class JobFacade:
    """Give repeated clients one entry point to the three-step subsystem."""

    def __init__(self, validator, store, audit):
        self.validator = validator
        self.store = store
        self.audit = audit

    def submit(self, payload):
        return submit_job(payload, self.validator, self.store, self.audit)


def main():
    store = MemoryStore()
    audit = AuditLog()
    facade = JobFacade(Validator(), store, audit)
    print(facade.submit(" pack books "))
    print(f"stored:{store.items}")
    print(f"audit:{audit.entries}")

    try:
        facade.submit(" ")
    except ValueError as error:
        print(f"boundary:{error}")
    print(f"state-after-boundary:{len(store.items)}:{len(audit.entries)}")
    print(f"recovered:{facade.submit('pack pens')}")


if __name__ == "__main__":
    main()
