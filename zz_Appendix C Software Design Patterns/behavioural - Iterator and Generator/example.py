"""A bounded generator client; Chapter 26 owns the complete lesson."""

from itertools import islice


def _require_positive_integer(name, value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


def first_job_names(records, limit, max_scanned):
    """Yield names within explicit result and source-scan bounds."""
    _require_positive_integer("limit", limit)
    _require_positive_integer("max_scanned", max_scanned)
    yielded = 0
    for record in islice(records, max_scanned):
        if not isinstance(record, str):
            raise TypeError("record must be text")
        name = record.strip()
        if not name:
            continue
        yield name
        yielded += 1
        if yielded == limit:
            return


def main():
    records = [" build ", "", "test", "publish"]
    print(f"normal={list(first_job_names(records, limit=2, max_scanned=4))}")
    blanks_then_value = ["", "", "", "too-late"]
    print(
        "scan-boundary="
        f"{list(first_job_names(blanks_then_value, limit=1, max_scanned=3))}"
    )
    try:
        list(first_job_names(records, limit=1, max_scanned=0))
    except ValueError as error:
        print(f"failure={error}")
    print(
        "recovery="
        f"{list(first_job_names(records, limit=3, max_scanned=4))}"
    )


if __name__ == "__main__":
    main()
