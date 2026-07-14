# Chapter 7 · Queues and Stacks with `collections.deque`

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
You’ll learn to use `collections.deque` to model queues (FIFO), stacks (LIFO), and sliding windows. We’ll implement examples inspired by task queues, log buffers, and lightweight rate limiters — ready to integrate into Django services or automation scripts.

## Learning path
1. **Quick reminder about lists**: why `list.pop(0)` doesn’t scale.
2. **Meet `deque`**: creation and basic operations.
3. **FIFO queue**: enqueue/dequeue with `append`/`popleft`.
4. **LIFO stack**: `append`/`pop` with `deque` for consistency.
5. **Sliding windows and rate limiting**: `maxlen`, counting within time.
6. **Validation and tests**: making sure capacity and order are respected.

## Learning objectives
- Create `deque` (bounded or unbounded) and understand why it beats lists for queues.
- Implement queues and stacks with O(1) operations on both ends.
- Use `maxlen` to build rotating buffers.
- Build sliding windows for metrics or request limiting.
- Test your queues so order and invariants are guaranteed.

## Prerequisites and routes
[Lists](../chapter-03-lists/README.md) are the only required prerequisite.

- **Essential route · 45–60 min:** sections 1–4, the direct `maxlen` example in section 5, and exercise 7-0. Outcome: trace FIFO, LIFO, and bounded-buffer state using only `deque` operations. No conditional, function, class, exception handling, or test is required.
- **Intermediate route · 25–35 min:** exercise 7-2 after you know [loops](../chapter-10-loops/README.md). Outcome: fill a fixed-size log buffer and explain which value is discarded.
- **Optional professional preview · 60–90 min:** the class, rate limiter, sections 6, and exercises 7-1/7-3. These preview [conditionals](../chapter-08-conditionals/README.md), [functions](../chapter-11-functions/README.md), [classes](../chapter-12-oop/README.md), [exceptions](../chapter-14-exceptions/README.md), and [testing](../chapter-18-testing/README.md). Copy the complete examples or skip them; they are not required for the essential checkpoint.

## Why it matters
In backend systems it’s common to process events in arrival order or keep a fixed-size history. `deque` is more efficient than lists for these patterns and it’s in the standard library (no extra dependencies).

### Mini adventure
Think of a theme park line: the first person to arrive is the first to ride. With `deque` you build that line efficiently: add people at the end and take from the front without pushing everyone forward.

## Predict before running
Before the first operations, draw the deque after each `append`, `popleft`, and `pop`. Predict which item a `deque(maxlen=3)` discards when a fourth item is appended. The rate-limiter prediction belongs to the optional professional preview.

---

## 1. Why not only use lists?
`list.pop(0)` must shift the remaining elements, which makes it O(n). For task queues or logs, that becomes a bottleneck. `deque` was designed to insert and remove on both ends in O(1).

---

## 2. Creation and basic operations

```python runnable
from collections import deque

queue = deque(["task-1", "task-2"])
queue.append("task-3")
print(queue)

last = queue.pop()
print(f"Last removed: {last}")
```

- With no arguments, `deque()` creates an empty structure.
- You can pass `maxlen` to limit the maximum size.

---

## 3. FIFO queue (first in, first out)

```python runnable
from collections import deque

queue = deque(["ticket-a", "ticket-b"])
queue.append("ticket-c")
first = queue.popleft()
print(first)
print(list(queue))
```

`append` adds at the arrival end and `popleft` removes the oldest item. That is the complete essential FIFO model.

### Optional preview: wrapping the queue in a class

```python runnable
from collections import deque

class SupportQueue:
    def __init__(self):
        self._queue = deque()

    def enqueue(self, ticket):
        self._queue.append(ticket)

    def handle_next(self):
        if not self._queue:
            return None
        return self._queue.popleft()  # O(1)

    def pending(self):
        return list(self._queue)
```

- `append` and `popleft` keep arrival order.
- Converting to a list (`list(self._queue)`) makes it easy to display state in UI or logs.

---

## 4. LIFO stack with the same structure

```python runnable
from collections import deque

stack = deque()
stack.append("deploy")
stack.append("rollback")

last = stack.pop()
print(last)
```

- Using `deque` for stacks unifies your data structures. You can switch behavior without switching types.

---

## 5. Sliding windows, `maxlen`, and rate limiting

```python runnable
from collections import deque

logs = deque(["start", "connect", "query"], maxlen=3)
logs.append("disconnect")
print(list(logs))  # ['connect', 'query', 'disconnect']
```

The fourth append discards the oldest value. This direct bounded buffer is part of the essential route.

### Optional professional preview: time-based rate limiter

```python runnable
from collections import deque
from time import monotonic

class RateLimiter:
    def __init__(self, max_requests, window_seconds, clock=monotonic):
        if isinstance(max_requests, bool) or not isinstance(max_requests, int) or max_requests <= 0:
            raise ValueError("max_requests must be a positive integer")
        if isinstance(window_seconds, bool) or not isinstance(window_seconds, (int, float)) or window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        if not callable(clock):
            raise TypeError("clock must be callable")
        self.window = float(window_seconds)
        self.max_requests = max_requests
        self.timestamps = deque()
        self._clock = clock

    def allow(self):
        now = self._clock()
        cutoff = now - self.window
        while self.timestamps and self.timestamps[0] <= cutoff:
            self.timestamps.popleft()
        if len(self.timestamps) >= self.max_requests:
            return False
        self.timestamps.append(now)
        return True

ticks = iter([0.0, 1.0, 2.0, 10.0])
limiter = RateLimiter(2, 10, clock=lambda: next(ticks))
assert [limiter.allow() for _ in range(4)] == [True, True, False, True]
```

- Remove timestamps at or before the cutoff, so the active interval is `(now - window, now]`.
- Reject when `len(self.timestamps) >= max_requests`; the injected monotonic clock makes the boundary deterministic in tests.
- An injected clock must be callable and return non-decreasing numeric values, matching `monotonic()`.

### Circular buffers with `maxlen`
```python illustrative
logs = deque(maxlen=3)
for event in ["start", "connect", "query", "disconnect"]:
    logs.append(event)
print(list(logs))  # only keeps the last 3 events
```

---

## 6. Validation and tests

```python runnable
# queues.py
from collections import deque

class BoundedQueue:
    def __init__(self, maxlen):
        if maxlen <= 0:
            raise ValueError("maxlen must be positive")
        self._data = deque(maxlen=maxlen)

    def push(self, value):
        if len(self._data) == self._data.maxlen:
            raise OverflowError("Queue full")
        self._data.append(value)

    def pop(self):
        if not self._data:
            raise IndexError("Queue empty")
        return self._data.popleft()
```

```python illustrative
# tests/test_queues.py
import pytest
from queues import BoundedQueue

def test_bounded_queue_keeps_order():
    queue = BoundedQueue(maxlen=2)
    queue.push("a")
    queue.push("b")
    assert queue.pop() == "a"

def test_bounded_queue_respects_maxlen():
    queue = BoundedQueue(maxlen=1)
    queue.push("a")
    with pytest.raises(OverflowError):
        queue.push("b")
```

---

## Guided exercises (with TODOs)
0. **7-0 · Essential queue trace**
   ```python todo
   from collections import deque
   tickets = deque(["A", "B"])
   # TODO 1: append "C" and remove the oldest ticket with popleft
   # TODO 2: use another deque as a stack and remove its newest item with pop
   # TODO 3: create deque(["one", "two"], maxlen=2), append "three", and predict the result
   ```
   *Hint*: draw the two ends after every operation; no `if`, function, class, or test is needed.

The remaining exercises are optional previews and use later chapters.

1. **7-1 · Email queue**
   ```python todo
   from collections import deque
   emails = deque()
   # TODO 1: add three fake emails
   # TODO 2: write send_next(queue) that does popleft and returns the email
   # TODO 3: handle empty queue by returning None
   ```
   *Hint*: use `SupportQueue` as inspiration.

2. **7-2 · Bounded log buffer**
   ```python todo
   from collections import deque
   logs = deque(maxlen=5)
   events = ["start", "init", "load", "ready", "request", "error"]
   # TODO 1: append each event to the deque
   # TODO 2: print only the events that stayed in the buffer
   # TODO 3: explain why maxlen prevents using more memory
   ```
   *Hint*: convert to a list to display the final buffer.

3. **7-3 · Sliding window for metrics**
   ```python todo
   from collections import deque
   measurements = deque(maxlen=3)
   # TODO 1: write add_measurement(value) that appends and returns the current average
   # TODO 2: compute the average only with the values in the current window
   # TODO 3: add a test confirming the window never exceeds maxlen
   ```
   *Hint*: compute `sum(measurements)/len(measurements)` after adding.

---

## Common mistakes
- **Using lists for heavy queues** ⇒ slow. Switch to `deque` when you do `pop(0)`/`insert(0)` often.
- **Not removing old elements** ⇒ time windows grow forever. Clean with a `while` like in `RateLimiter`.
- **Assuming `maxlen` raises errors** ⇒ by default it discards items on the other end; if you want errors, check `len` before `append` (like `BoundedQueue`).
- **Sharing the same `deque` across threads without locks** ⇒ use locks or thread-safe queues (like `queue.Queue`) when you have concurrency.

---

## Explained solutions
### 7-0 essential trace and recovery
`append` changes the right end, `popleft` the left end, `pop` the right end, and `maxlen` discards from the opposite end.

```python runnable
from collections import deque
tickets = deque(["A", "B"])
tickets.append("C")
print(tickets.popleft())
stack = deque(["draft", "publish"])
print(stack.pop())
bounded = deque(["one", "two"], maxlen=2)
bounded.append("three")
print(list(bounded))
```

An extra `popleft` on an empty deque fails with the stable signal `IndexError`:

<!-- bookcheck: expect-error="IndexError" -->
```python expected-error
from collections import deque
deque().popleft()
```

Recover by checking the drawn or printed length and rerunning only a valid removal:

```python runnable
from collections import deque
tickets = deque(["A"])
print(tickets.popleft())
```

1. **Email queue**: `send_next` calls `popleft()` and returns `None` if empty, avoiding exceptions and making the function idempotent.
2. **Bounded log buffer**: iterating and doing `logs.append(event)` keeps only the last five; `list(logs)` shows final content.
3. **Sliding window metrics**: after each insert, compute `average = sum(measurements) / len(measurements)`; the test checks that after many inserts, `len(measurements)` is still 3.

---

## Checkpoint and self-assessment
Complete 7-0, predict every removed or discarded value, run the normal case, deliberately observe the documented empty-deque `IndexError`, and rerun the recovered case. The rate limiter and its time boundary belong to the optional professional preview.

Score one point for **FIFO correctness**, **LIFO correctness**, **the `maxlen` boundary**, **error recovery**, and **explaining both deque ends**. A score of 4/5 completes the essential route; otherwise revisit sections 2–5 and redraw the state.

## Summary
`collections.deque` is an efficient solution for queues, stacks, and sliding windows. You know when to prefer it over lists, how to use `maxlen`, and how to validate behavior with simple tests.

## Closing reflection
With robust queues you can build rate limiters, buffers, and event processors that scale better. You now have the foundation to integrate these structures into APIs, workers, and observability tools — completing a strong intro to core Python data structures.
