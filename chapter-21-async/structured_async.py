"""Structured-concurrency examples for Chapter 21."""

import asyncio


async def worker(
    name: str,
    delay: float,
    *,
    fail: bool = False,
    events: list[str] | None = None,
) -> str:
    if events is None:
        events = []
    events.append(f"{name}:start")
    try:
        await asyncio.sleep(delay)
        if fail:
            raise ValueError(f"{name} failed")
        return f"{name}:done"
    finally:
        events.append(f"{name}:cleanup")


async def successful_group() -> list[str]:
    async with asyncio.TaskGroup() as group:
        first = group.create_task(worker("first", 0))
        second = group.create_task(worker("second", 0))
    return [first.result(), second.result()]


async def failing_group() -> list[str]:
    events: list[str] = []
    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(worker("failure", 0, fail=True, events=events))
            group.create_task(worker("sibling", 10, events=events))
    except* ValueError:
        events.append("failure:handled")
    return events


async def timed_group(deadline: float = 0.02) -> list[str]:
    events: list[str] = []
    try:
        async with asyncio.timeout(deadline):
            async with asyncio.TaskGroup() as group:
                group.create_task(worker("slow-a", 10, events=events))
                group.create_task(worker("slow-b", 10, events=events))
    except TimeoutError:
        events.append("timeout:handled")
    return events
