"""Select a small behavior policy as an ordinary Python callable."""


class UnknownStrategy(ValueError):
    """Raised when configuration requests no registered strategy."""


class InvalidStrategyName(ValueError):
    """Raised when a strategy selection is not usable text."""


class InvalidStrategy(TypeError):
    """Raised when execution receives something that is not callable."""


class InvalidPayload(ValueError):
    """Raised before a strategy receives an invalid payload."""


def keep(payload):
    return payload


def uppercase(payload):
    return payload.upper()


def select_strategy(name):
    if not isinstance(name, str) or not name:
        raise InvalidStrategyName("strategy name must be non-empty text")
    strategies = {"keep": keep, "uppercase": uppercase}
    try:
        return strategies[name]
    except KeyError as error:
        raise UnknownStrategy(f"unknown strategy: {name}") from error


def run(payload, strategy):
    if not isinstance(payload, str) or not payload or len(payload) > 16:
        raise InvalidPayload("payload must contain 1 to 16 characters")
    if not callable(strategy):
        raise InvalidStrategy("strategy must be callable")
    return f"processed:{strategy(payload)}"


def main():
    print(f"normal={run('mixed', keep)}")
    print(f"variation={run('mixed', select_strategy('uppercase'))}")
    try:
        select_strategy(None)
    except InvalidStrategyName as error:
        print(f"name-boundary={error}")
    try:
        select_strategy("missing")
    except UnknownStrategy as error:
        print(f"boundary={error}")
    try:
        run("mixed", None)
    except InvalidStrategy as error:
        print(f"callable-boundary={error}")
    print(f"recovery={run('safe', select_strategy('keep'))}")


if __name__ == "__main__":
    main()
