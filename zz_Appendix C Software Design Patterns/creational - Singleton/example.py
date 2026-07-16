"""Contrast hidden Singleton state with an explicitly owned object."""


class DuplicateName(ValueError):
    """Raised when mutable registry state already contains a name."""


class Registry:
    def __init__(self):
        self._names = set()

    def add(self, name):
        if name in self._names:
            raise DuplicateName(f"duplicate name: {name}")
        self._names.add(name)

    def contains(self, name):
        return name in self._names


_shared_registry = None


def module_owned_registry():
    """Return module-owned shared state; this does not enforce a Singleton."""
    global _shared_registry
    if _shared_registry is None:
        _shared_registry = Registry()
    return _shared_registry


def main():
    first = Registry()
    second = Registry()
    first.add("job-a")
    print(f"explicit-isolated={not second.contains('job-a')}")

    shared_a = module_owned_registry()
    shared_b = module_owned_registry()
    shared_a.add("job-b")
    print(f"module-accessor-shared={shared_b.contains('job-b')}")
    try:
        shared_b.add("job-b")
    except DuplicateName as error:
        print(f"boundary={error}")

    recovered = Registry()
    recovered.add("job-b")
    print(f"recovery-explicit-owner={recovered.contains('job-b')}")


if __name__ == "__main__":
    main()
