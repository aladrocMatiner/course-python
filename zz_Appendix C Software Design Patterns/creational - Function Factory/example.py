"""A small function Factory with validation at the construction boundary."""


class UnknownExecutor(ValueError):
    """Raised when a caller requests an executor that is not registered."""


class InvalidExecutorName(ValueError):
    """Raised when an executor selection is not usable text."""


class PayloadExecutor:
    """A product created by the Factory for one transformation policy."""

    def __init__(self, transform):
        self._transform = transform

    def execute(self, payload):
        return self._transform(payload)


def build_executor(name):
    """Construct a new executor selected by a stable public name."""
    if not isinstance(name, str) or not name:
        raise InvalidExecutorName("executor name must be non-empty text")
    builders = {
        "direct": lambda: PayloadExecutor(lambda payload: payload),
        "uppercase": lambda: PayloadExecutor(lambda payload: payload.upper()),
    }
    try:
        builder = builders[name]
    except KeyError as error:
        raise UnknownExecutor(f"unknown executor: {name}") from error
    return builder()


def main():
    first = build_executor("direct")
    second = build_executor("direct")
    print(f"fresh-product={first is not second}")
    print(f"normal={first.execute('mixed')}")
    print(f"variation={build_executor('uppercase').execute('mixed')}")
    try:
        build_executor(None)
    except InvalidExecutorName as error:
        print(f"name-boundary={error}")
    try:
        build_executor("missing")
    except UnknownExecutor as error:
        print(f"boundary={error}")
    print(f"recovery={build_executor('direct').execute('safe')}")


if __name__ == "__main__":
    main()
