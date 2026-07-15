# Chapter 7 · Queues and Stacks with `collections.deque`

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
You’ll learn to use `collections.deque` to model queues (FIFO), stacks (LIFO), and sliding windows. We’ll implement examples inspired by task queues, log buffers, and lightweight rate limiters — ready to integrate into Django services or automation scripts.

## Learning path
1. **Quick reminder about lists**: why `list.pop(0)` doesn’t scale.
2. **Import bridge**: ask the selected interpreter for a standard-library module and diagnose lookup failures safely.
3. **Meet `deque`**: creation and basic operations.
4. **FIFO queue**: enqueue/dequeue with `append`/`popleft`.
5. **LIFO stack**: `append`/`pop` with `deque` for consistency.
6. **Sliding windows and rate limiting**: `maxlen`, counting within time.
7. **Validation and tests**: making sure capacity and order are respected.

## Learning objectives
- Create `deque` (bounded or unbounded) and understand why it beats lists for queues.
- Distinguish standard-library, local, and third-party modules and use `import module`, `from module import name`, and `python -m module` deliberately.
- Diagnose a missing or accidentally shadowed module without installing arbitrary packages or modifying Python itself.
- Implement queues and stacks with O(1) operations on both ends.
- Use `maxlen` to build rotating buffers.
- Build sliding windows for metrics or request limiting.
- Test your queues so order and invariants are guaranteed.

## Prerequisites and routes
[Lists](../chapter-03-lists/README.md) and the Chapter 1 file/run loop are the only required prerequisites. The import bridge below teaches the additional concept immediately before `deque` first needs it.

- **Essential route · 60–80 min:** section 1, the complete import bridge, sections 2–4, the direct `maxlen` example in section 5, and exercises 7-import/7-0. Outcome: run one local standard-library module in two ways and trace FIFO, LIFO, and bounded-buffer state using only imports and `deque` operations. No conditional, function, class, exception handling, package installation, or test is required.
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

## Import bridge: modules before `deque`

An import asks the **same selected Python interpreter** that runs your file to locate and load a module. A module is usually a `.py` file or a module supplied by Python. There are three sources to distinguish:

- the **standard library** ships with the declared Python installation; `collections` and `random` are examples, so do not install them with `pip`;
- a **local module** is your own importable `.py` file, such as `queue_demo.py`;
- a **third-party package** is installed separately in an environment. Chapter 16 teaches that workflow; this essential route needs none.

Package structure and reusable public APIs get their full treatment in [Chapter 15](../chapter-15-modulos/README.md). Here we need only enough import knowledge to use `deque` honestly.

### Two import forms, two namespaces

Predict which spelling constructs the queue in each complete example:

```python runnable
import collections

queue = collections.deque(["A", "B"])
print(queue.popleft())
```

`import collections` binds the module name, so access is qualified as `collections.deque`. By contrast:

```python runnable
from collections import deque

queue = deque(["A", "B"])
print(queue.popleft())
```

`from collections import deque` binds that selected public name directly. Both print exactly `A`. A bare `deque(...)` is not available after only `import collections` because the two forms bind different names.

### Run a local module with the selected interpreter

Save this as `queue_demo.py` in a learner-owned disposable directory:

```python runnable
from collections import deque

queue = deque(["A", "B"])
print(queue.popleft())
```

From that directory, these shell commands each execute the file once and produce the same line:

```bash illustrative
python queue_demo.py
python -m queue_demo
```

The `-m` form tells this interpreter to find the importable local module named `queue_demo` from the current import location. It does not include `.py`. This single-file example does not yet introduce package-relative imports.

### Predict and observe a missing module

This deliberately invented course module does not exist:

```python illustrative
import course_module_that_does_not_exist
```

The executable chapter contract runs this import in an isolated subprocess. The stable category is `ModuleNotFoundError`; the full environment-dependent message is not the contract. Diagnose in this order:

1. Check the spelling.
2. Decide whether the name should be standard-library, local, or third-party.
3. For a local module, check its filename and the shell’s working directory.
4. Only for a known third-party dependency, follow that project’s reviewed installation instructions later in Chapter 16.

Do not respond to every missing import by installing a similarly named package from an index.

### Shadowing: when your file hides the intended module

Python’s import search can find a learner-owned file before the intended library module. A file or directory named `collections.py`, `typing.py`, or `random.py` in the exercise folder can therefore **shadow** that module. A symptom may be a surprising source path or a message saying the imported module lacks the expected attribute.

Recovery is local and reversible:

1. Inspect the reported module path in a fresh diagnostic process, for example `python -c "import collections; print(collections.__file__)"`.
2. If that path identifies a conflicting file you created in the disposable exercise folder, rename only that file to a domain name such as `queue_notes.py`.
3. End the old REPL if one is open, start a fresh interpreter process in the intended directory, and rerun `from collections import deque`.
4. Remove only cache files created inside the disposable exercise folder if they remain; never delete or edit a standard-library file.

The recovered queue example prints `A` again. Restarting matters because a running process can retain modules it already imported.

### Guided import TODO, hint, and explained solution

```python todo
# queue_demo.py
# TODO 1: import the standard-library deque name from collections.
# TODO 2: create a deque containing "A" and "B".
# TODO 3: remove and print the oldest value.
# TODO 4: run this file as a path and then with `python -m queue_demo`.
```

**Hint:** the direct form begins `from collections import ...`; `popleft()` removes from the arrival end. The filename belongs in the path command but the `.py` suffix is omitted after `-m`.

```python runnable
from collections import deque

queue = deque(["A", "B"])
print(queue.popleft())
```

```text output
A
```

Complete the import bridge when both shell forms produce this line, you observe and classify the invented module’s expected failure, and you can explain why renaming a learner-owned shadow file is safer than changing the Python installation.

Score one point for **correct direct import**, **correct qualified-form explanation**, **both local execution forms**, **missing/shadowed-module recovery**, and **identifying `collections` as standard library**. A score of 5/5 completes the bridge; Chapter 15 remains later depth.

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
0. **7-import · Import and run `queue_demo`**

   Complete the guided import TODO above, run both documented shell forms, and explain why `collections` needs no separate installation. Keep all files in a disposable learner-owned directory.

   *Hint*: after the two successful runs, use the deliberately nonexistent module block to practice diagnosis; do not install it.

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
- **Installing `collections` from a package index** ⇒ it is already in Python’s standard library; verify the selected interpreter instead.
- **Naming a local file `collections.py` or `typing.py`** ⇒ it can shadow the intended module; rename only your local source and restart the process.
- **Typing `python -m queue_demo.py`** ⇒ module mode uses the import name `queue_demo`, without the file suffix.

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
Complete 7-import and 7-0. Run `queue_demo.py` both as a path and with `-m`, classify the documented `ModuleNotFoundError`, explain shadowing recovery, predict every removed or discarded value, deliberately observe the empty-deque `IndexError`, and rerun the recovered case. The rate limiter and its time boundary belong to the optional professional preview.

Score one point for **import/run correctness**, **FIFO correctness**, **LIFO correctness**, **the `maxlen` boundary**, and **both recovery explanations**. A score of 5/5 completes the essential route; otherwise revisit the import bridge or sections 2–5 and repeat only the missing observation.

## Summary
`collections.deque` is an efficient standard-library solution for queues, stacks, and sliding windows. You know how the selected interpreter resolves it, when to prefer it over lists, how to use `maxlen`, and how to validate behavior with simple tests.

## Closing reflection
Which diagnostic question would you ask first for a missing import: spelling, module source, working directory, or installation? Explain why the answer depends on whether the module is standard-library, local, or third-party. With robust queues you can build rate limiters, buffers, and event processors while keeping module lookup understandable and recoverable.
