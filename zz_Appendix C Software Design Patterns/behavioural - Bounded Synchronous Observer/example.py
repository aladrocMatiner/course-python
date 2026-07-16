"""A bounded local Observer with explicit removal and failure reporting."""


class ObserverLimitError(RuntimeError):
    """Raised before the subject accepts more listeners than its limit."""


class JobEventSubject:
    def __init__(self, listener_limit):
        if (
            isinstance(listener_limit, bool)
            or not isinstance(listener_limit, int)
            or listener_limit < 1
        ):
            raise ValueError("listener_limit must be a positive integer")
        self._listener_limit = listener_limit
        self._subscriptions = []
        self._next_token = 1

    def subscribe(self, listener):
        if not callable(listener):
            raise TypeError("listener must be callable")
        if len(self._subscriptions) >= self._listener_limit:
            raise ObserverLimitError("listener limit reached")
        token = self._next_token
        self._next_token += 1
        self._subscriptions.append((token, listener))

        def unsubscribe():
            self._subscriptions[:] = [
                subscription
                for subscription in self._subscriptions
                if subscription[0] != token
            ]

        return unsubscribe

    def notify(self, event):
        errors = []
        delivered = 0
        for _token, listener in tuple(self._subscriptions):
            try:
                listener(event)
            except Exception as error:
                errors.append(str(error))
            else:
                delivered += 1
        return delivered, tuple(errors)


def main():
    received = []

    def audit(event):
        received.append(event)

    def broken_listener(event):
        raise RuntimeError(f"cannot record {event}")

    subject = JobEventSubject(listener_limit=3)
    remove_first_audit = subject.subscribe(audit)
    subject.subscribe(audit)
    remove_broken = subject.subscribe(broken_listener)
    delivered, errors = subject.notify("job-finished")
    print(f"normal=delivered:{delivered},received:{received}")
    print(f"failure={errors[0]}")
    try:
        subject.subscribe(lambda event: None)
    except ObserverLimitError as error:
        print(f"boundary={error}")
    remove_first_audit()
    remove_first_audit()
    remove_broken()
    try:
        subject.subscribe(None)
    except TypeError as error:
        print(f"callback-boundary={error}")
    print(f"recovery={subject.notify('job-recovered')}")


if __name__ == "__main__":
    main()
