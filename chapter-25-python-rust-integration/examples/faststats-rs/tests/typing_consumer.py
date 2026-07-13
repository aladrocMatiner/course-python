from faststats_rs import OnlineStats, Summary, describe_payload, summarize

summary: Summary = summarize([1, 2.0, 3], threshold=1.0)
count: int = summary.count
mean: float = summary.mean

online = OnlineStats()
online.add(1)
online.extend([2.0, 3])
maybe_mean: float | None = online.mean

description: tuple[str, int, bool] = describe_payload("demo", b"abc", "note")

reveal_type(count)
reveal_type(mean)
reveal_type(maybe_mean)
reveal_type(description)
