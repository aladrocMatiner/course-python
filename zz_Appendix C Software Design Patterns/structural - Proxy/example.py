"""A verified Proxy contrast; a direct guard is often enough in Python."""


class InvalidActor(ValueError):
    def __init__(self):
        self.code = "invalid_actor"
        super().__init__("actor must be non-empty text")


class AccessDenied(PermissionError):
    def __init__(self):
        self.code = "access_denied"
        super().__init__("actor is not allowed")


class DocumentNotFound(LookupError):
    def __init__(self, document_id):
        self.code = "document_not_found"
        super().__init__(f"document not found: {document_id}")


class DocumentReader:
    """The real object. The actor argument keeps both interfaces identical."""

    def __init__(self, documents):
        self.documents = dict(documents)

    def read(self, document_id, actor):
        del actor
        try:
            return self.documents[document_id]
        except KeyError as error:
            raise DocumentNotFound(document_id) from error


def require_allowed_actor(actor, allowed_actors):
    """Give the direct guard and Proxy exactly the same access boundary."""

    if not isinstance(actor, str) or not actor.strip():
        raise InvalidActor()
    if actor not in allowed_actors:
        raise AccessDenied()


def read_with_guard(reader, document_id, actor, allowed_actors):
    """Simpler Python alternative when only one call site needs the guard."""

    require_allowed_actor(actor, allowed_actors)
    return reader.read(document_id, actor)


class ReadProxy:
    """Keep read(document_id, actor), but control access before delegation."""

    def __init__(self, reader, allowed_actors):
        if not callable(getattr(reader, "read", None)):
            raise TypeError("reader must provide read(document_id, actor)")
        self.reader = reader
        self.allowed_actors = frozenset(allowed_actors)

    def read(self, document_id, actor):
        require_allowed_actor(actor, self.allowed_actors)
        return self.reader.read(document_id, actor)


def main():
    real_reader = DocumentReader({"guide": "safe local content"})
    proxy = ReadProxy(real_reader, {"learner"})
    print(
        "direct:"
        + read_with_guard(real_reader, "guide", "learner", {"learner"})
    )
    print(f"proxy:{proxy.read('guide', 'learner')}")

    for label, read in (
        (
            "direct",
            lambda actor: read_with_guard(
                real_reader, "guide", actor, {"learner"}
            ),
        ),
        ("proxy", lambda actor: proxy.read("guide", actor)),
    ):
        try:
            read("")
        except InvalidActor as error:
            print(f"{label}-invalid:{error.code}")
        try:
            read("guest")
        except AccessDenied as error:
            print(f"{label}-denied:{error.code}")

    try:
        proxy.read("missing", "learner")
    except DocumentNotFound as error:
        print(f"missing:{error.code}")
    print(f"recovered:{proxy.read('guide', 'learner')}")


if __name__ == "__main__":
    main()
