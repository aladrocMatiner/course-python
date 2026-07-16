"""A verified contrast between a function Factory and Factory Method."""


class UnknownStyle(ValueError):
    """Raised when configuration names no known formatting policy."""


class InvalidStyle(ValueError):
    """Raised when a style selection is not usable text."""


class Formatter:
    """A small product with one formatting operation."""

    def __init__(self, transform):
        self._transform = transform

    def format(self, text):
        return self._transform(text)


def choose_formatter(style):
    """Construct a product when configuration, not subclasses, owns choice."""
    if not isinstance(style, str) or not style:
        raise InvalidStyle("style must be non-empty text")
    builders = {
        "plain": lambda: Formatter(lambda text: text),
        "loud": lambda: Formatter(lambda text: text.upper()),
    }
    try:
        builder = builders[style]
    except KeyError as error:
        raise UnknownStyle(f"unknown style: {style}") from error
    return builder()


class Report:
    """A tiny Factory Method example: subclasses own collaborator creation."""

    def create_formatter(self):
        return Formatter(lambda text: text)

    def render(self, text):
        return self.create_formatter().format(text)


class LoudReport(Report):
    def create_formatter(self):
        return Formatter(lambda text: text.upper())


def main():
    first = choose_formatter("plain")
    second = choose_formatter("plain")
    print(f"fresh-products={first is not second}")
    print(f"function-factory={choose_formatter('loud').format('ready')}")
    print(f"factory-method={LoudReport().render('ready')}")
    try:
        choose_formatter(None)
    except InvalidStyle as error:
        print(f"name-boundary={error}")
    try:
        choose_formatter("missing")
    except UnknownStyle as error:
        print(f"boundary={error}")
    print(f"recovery={choose_formatter('plain').format('ready')}")


if __name__ == "__main__":
    main()
