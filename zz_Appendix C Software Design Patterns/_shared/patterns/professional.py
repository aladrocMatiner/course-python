"""Professional Decorator and bounded synchronous Observer examples."""

from .domain import PatternError, Result


class MeasuringExecutor:
    """Observe an executor through composition without changing its contract."""

    def __init__(self, wrapped, *, label, clock, events, measurements):
        if not callable(getattr(wrapped, "execute", None)):
            raise PatternError(
                "invalid_executor",
                "wrapped object must provide execute(job)",
            )
        if not callable(clock):
            raise PatternError("invalid_clock", "clock must be callable")
        self.wrapped = wrapped
        self.label = label
        self.clock = clock
        self.events = events
        self.measurements = measurements

    def execute(self, job):
        started = self.clock()
        self.events.append(f"{self.label}:before")
        try:
            result = self.wrapped.execute(job)
        except Exception:
            elapsed = self.clock() - started
            self.events.append(f"{self.label}:error")
            self.measurements.append((self.label, "error", elapsed))
            raise
        elapsed = self.clock() - started
        self.events.append(f"{self.label}:after")
        self.measurements.append((self.label, "completed", elapsed))
        return result


class ObserverLimitError(PatternError):
    """Raised without changing existing observers when the cap is full."""

    def __init__(self, limit):
        self.limit = limit
        super().__init__(
            "observer_limit",
            f"at most {limit} observers may be active",
        )


class ObserverFailure:
    """Sanitized evidence that one callback failed and was removed."""

    def __init__(self, observer_id, code):
        self.observer_id = observer_id
        self.code = code

    def __eq__(self, other):
        return (
            isinstance(other, ObserverFailure)
            and self.observer_id == other.observer_id
            and self.code == other.code
        )


class NotificationReport:
    """Only current-call outcomes; it is not retained as event history."""

    def __init__(self, notified, failures):
        self.notified = tuple(notified)
        self.failures = tuple(failures)


class Subscription:
    """A removable handle; calling unsubscribe twice is harmless."""

    def __init__(self, subject, observer_id):
        self._subject = subject
        self.observer_id = observer_id

    @property
    def active(self):
        return self._subject._contains(self.observer_id)

    def unsubscribe(self):
        return self._subject._remove(self.observer_id)


class JobEventSubject:
    """Bounded process-local notifications with snapshot iteration.

    Callbacks present when ``publish`` begins receive that event even if
    another callback unsubscribes them during the same pass.  A callback that
    raises is isolated, reported, and removed before the next publication.
    """

    def __init__(self, limit=4):
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise PatternError(
                "invalid_observer_limit",
                "observer limit must be a positive integer",
            )
        self._limit = limit
        self._observers = {}
        self._next_id = 1

    @property
    def active_count(self):
        return len(self._observers)

    def subscribe(self, callback):
        if not callable(callback):
            raise PatternError(
                "invalid_observer",
                "observer must be callable",
            )
        if len(self._observers) >= self._limit:
            raise ObserverLimitError(self._limit)
        observer_id = f"observer-{self._next_id}"
        self._next_id += 1
        self._observers[observer_id] = callback
        return Subscription(self, observer_id)

    def publish(self, result):
        if not isinstance(result, Result):
            raise PatternError(
                "invalid_event",
                "job event must be a Result",
            )

        notified = []
        failures = []
        for observer_id, callback in tuple(self._observers.items()):
            try:
                callback(result)
            except Exception:
                self._remove(observer_id)
                failures.append(
                    ObserverFailure(observer_id, "observer_failed")
                )
            else:
                notified.append(observer_id)
        return NotificationReport(notified, failures)

    def _contains(self, observer_id):
        return observer_id in self._observers

    def _remove(self, observer_id):
        return self._observers.pop(observer_id, None) is not None
