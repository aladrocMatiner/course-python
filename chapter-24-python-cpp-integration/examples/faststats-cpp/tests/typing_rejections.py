from __future__ import annotations

import faststats_cpp


# These objects are returned by native factories/functions. Their constructors
# are intentionally unavailable to Python consumers; each independent function
# must fail mypy. Keeping the probes in separate flows matters because a
# constructor returning Never makes the remainder of its function unreachable.
def reject_summary() -> None:
    faststats_cpp.Summary()


def reject_metadata() -> None:
    faststats_cpp.Metadata()


def reject_resource() -> None:
    faststats_cpp.TrackedResource("direct")
