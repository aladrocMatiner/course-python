from __future__ import annotations

from array import array

import faststats_cpp


summary: faststats_cpp.Summary = faststats_cpp.summarize([1, 2.0], threshold=1)
count: int = summary.count
mean: float = summary.mean

online = faststats_cpp.OnlineStats()
online.extend([1, 2.0])
maybe_mean: float | None = online.mean

buffer = array("d", [1.0, 3.0])
faststats_cpp.normalize_in_place(buffer)

dataset = faststats_cpp.Dataset("typed")
label: str = dataset.metadata.label

assert count == 2 and mean == 1.5 and maybe_mean == 1.5 and label == "typed"
