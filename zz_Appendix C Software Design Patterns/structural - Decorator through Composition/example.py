"""Measure an executor through composition while preserving its contract."""


class StepClock:
    """Return a finite sequence of fake timestamps; never read wall time."""

    def __init__(self, values):
        self.values = list(values)

    def __call__(self):
        if not self.values:
            raise RuntimeError("fake clock exhausted")
        return self.values.pop(0)


class DirectExecutor:
    def execute(self, payload):
        if not isinstance(payload, str) or not payload.strip():
            raise ValueError("payload must be non-empty text")
        if payload == "fail":
            raise RuntimeError("planned execution failure")
        return f"completed:{payload}"


class MeasuringExecutor:
    """Best-effort observation that never replaces the wrapped outcome."""

    def __init__(self, wrapped, clock, measurements):
        if not callable(getattr(wrapped, "execute", None)):
            raise TypeError("wrapped object must provide execute(payload)")
        if not callable(clock):
            raise TypeError("clock must be callable")
        self.wrapped = wrapped
        self.clock = clock
        self.measurements = measurements

    def execute(self, payload):
        started = self._read_clock()
        try:
            result = self.wrapped.execute(payload)
        except Exception:
            self._record("error", started)
            raise
        self._record("completed", started)
        return result

    def _read_clock(self):
        try:
            return self.clock()
        except Exception:
            return None

    def _record(self, outcome, started):
        if started is None:
            return
        try:
            elapsed = self.clock() - started
            self.measurements.append((outcome, elapsed))
        except Exception:
            return


class FailOnceExecutor:
    """Raise one exact error, then recover for the next independent call."""

    def __init__(self, error):
        self.error = error

    def execute(self, payload):
        if self.error is not None:
            error = self.error
            self.error = None
            raise error
        return DirectExecutor().execute(payload)


class BrokenMeasurements:
    def append(self, measurement):
        del measurement
        raise RuntimeError("measurement sink unavailable")


def main():
    success_measurements = []
    measured = MeasuringExecutor(
        DirectExecutor(), StepClock([10.0, 10.25]), success_measurements
    )
    print(measured.execute("pack-books"))
    print(f"measurement:{success_measurements[0]}")

    boundary_measurements = []
    measured_boundary = MeasuringExecutor(
        DirectExecutor(), StepClock([15.0, 15.0]), boundary_measurements
    )
    try:
        measured_boundary.execute("")
    except ValueError as error:
        print(f"boundary:{error}")
    print(f"measurement:{boundary_measurements[0]}")

    original_error = RuntimeError("planned execution failure")
    fail_once = FailOnceExecutor(original_error)
    measured_failure = MeasuringExecutor(
        fail_once, StepClock([20.0, 20.5]), BrokenMeasurements()
    )
    try:
        measured_failure.execute("pack-books")
    except RuntimeError as error:
        print(f"preserved-original:{error is original_error}")
    print(f"recovered:{measured_failure.execute('pack-books')}")


if __name__ == "__main__":
    main()
