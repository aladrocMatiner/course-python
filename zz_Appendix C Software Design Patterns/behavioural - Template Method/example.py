"""Contrast function composition with a small Template Method hierarchy."""


class InvalidPayload(ValueError):
    """Raised when a pipeline cannot process the supplied payload."""


def validate(payload):
    if not isinstance(payload, str) or not payload.strip():
        raise InvalidPayload("payload must not be blank")


def process(payload, transform):
    """The simpler option: fixed steps composed with one callable."""
    validate(payload)
    transformed = transform(payload)
    return f"stored:{transformed}"


class Pipeline:
    """Template Method: run fixes order; subclasses replace one step."""

    def run(self, payload):
        validate(payload)
        transformed = self.transform(payload)
        return f"stored:{transformed}"

    def transform(self, payload):
        return payload


class UppercasePipeline(Pipeline):
    def transform(self, payload):
        return payload.upper()


def main():
    print(f"function-composition={process('mixed', str.upper)}")
    print(f"template-method={UppercasePipeline().run('mixed')}")
    try:
        UppercasePipeline().run(" ")
    except InvalidPayload as error:
        print(f"boundary={error}")
    print(f"recovery={process('safe', str.lower)}")


if __name__ == "__main__":
    main()
