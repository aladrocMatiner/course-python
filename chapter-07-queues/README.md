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

## Why it matters
In backend systems it’s common to process events in arrival order or keep a fixed-size history. `deque` is more efficient than lists for these patterns and it’s in the standard library (no extra dependencies).

### Mini adventure
Think of a theme park line: the first person to arrive is the first to ride. With `deque` you build that line efficiently: add people at the end and take from the front without pushing everyone forward.

---

## 1. Why not only use lists?
`list.pop(0)` must shift the remaining elements, which makes it O(n). For task queues or logs, that becomes a bottleneck. `deque` was designed to insert and remove on both ends in O(1).

---

## 2. Creation and basic operations

```python
from collections import deque

cola = deque(["task-1", "task-2"])
cola.append("task-3")
print(cola)

ultimo = cola.pop()
print(f"Último extraído: {ultimo}")
```

- With no arguments, `deque()` creates an empty structure.
- You can pass `maxlen` to limit the maximum size.

---

## 3. FIFO queue (first in, first out)

```python
from collections import deque

class ColaSoporte:
    def __init__(self):
        self._cola = deque()

    def encolar(self, ticket):
        self._cola.append(ticket)

    def atender(self):
        if not self._cola:
            return None
        return self._cola.popleft()  # O(1)

    def pendientes(self):
        return list(self._cola)
```

- `append` and `popleft` keep arrival order.
- Converting to a list (`list(self._cola)`) makes it easy to display state in UI or logs.

---

## 4. LIFO stack with the same structure

```python
from collections import deque

stack = deque()
stack.append("deploy")
stack.append("rollback")

ultimo = stack.pop()
print(ultimo)
```

- Using `deque` for stacks unifies your data structures. You can switch behavior without switching types.

---

## 5. Sliding windows, `maxlen`, and rate limiting

```python
from collections import deque
from time import time

class RateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.window = window_seconds
        self.max_requests = max_requests
        self.timestamps = deque()

    def allow(self):
        ahora = time()
        limite = ahora - self.window
        while self.timestamps and self.timestamps[0] < limite:
            self.timestamps.popleft()
        if len(self.timestamps) >= self.max_requests:
            return False
        self.timestamps.append(ahora)
        return True
```

- Remove from the front everything that is outside the time window.
- `len(self.timestamps)` tells you how many requests are still “active”; if it exceeds the limit, reject.

### Circular buffers with `maxlen`
```python
logs = deque(maxlen=3)
for evento in ["start", "connect", "query", "disconnect"]:
    logs.append(evento)
print(list(logs))  # solo conserva los últimos 3 eventos
```

---

## 6. Validation and tests

```python
# queues.py
from collections import deque

class ColaAcotada:
    def __init__(self, maxlen):
        if maxlen <= 0:
            raise ValueError("maxlen debe ser positivo")
        self._datos = deque(maxlen=maxlen)

    def push(self, valor):
        if len(self._datos) == self._datos.maxlen:
            raise OverflowError("Cola llena")
        self._datos.append(valor)

    def pop(self):
        if not self._datos:
            raise IndexError("Cola vacía")
        return self._datos.popleft()
```

```python
# tests/test_queues.py
import pytest
from queues import ColaAcotada

def test_cola_acotada_mantiene_orden():
    cola = ColaAcotada(maxlen=2)
    cola.push("a")
    cola.push("b")
    assert cola.pop() == "a"

def test_cola_acotada_no_supera_maxlen():
    cola = ColaAcotada(maxlen=1)
    cola.push("a")
    with pytest.raises(OverflowError):
        cola.push("b")
```

---

## Guided exercises (with TODOs)
1. **7-1 · Email queue**
   ```python
   from collections import deque
   emails = deque()
   # TODO 1: add three fake emails
   # TODO 2: write send_next(queue) that does popleft and returns the email
   # TODO 3: handle empty queue by returning None
   ```
   *Hint*: use `ColaSoporte` as inspiration.

2. **7-2 · Bounded log buffer**
   ```python
   from collections import deque
   logs = deque(maxlen=5)
   eventos = ["start", "init", "load", "ready", "request", "error"]
   # TODO 1: append each event to the deque
   # TODO 2: print only the events that stayed in the buffer
   # TODO 3: explain why maxlen prevents using more memory
   ```
   *Hint*: convert to a list to display the final buffer.

3. **7-3 · Sliding window for metrics**
   ```python
   from collections import deque
   mediciones = deque(maxlen=3)
   # TODO 1: write add_measurement(valor) that appends and returns the current average
   # TODO 2: compute the average only with the values in the current window
   # TODO 3: add a test confirming the window never exceeds maxlen
   ```
   *Hint*: compute `sum(mediciones)/len(mediciones)` after adding.

---

## Common mistakes
- **Using lists for heavy queues** ⇒ slow. Switch to `deque` when you do `pop(0)`/`insert(0)` often.
- **Not removing old elements** ⇒ time windows grow forever. Clean with a `while` like in `RateLimiter`.
- **Assuming `maxlen` raises errors** ⇒ by default it discards items on the other end; if you want errors, check `len` before `append` (like `ColaAcotada`).
- **Sharing the same `deque` across threads without locks** ⇒ use locks or thread-safe queues (like `queue.Queue`) when you have concurrency.

---

## Explained solutions
1. **Email queue**: `send_next` calls `popleft()` and returns `None` if empty, avoiding exceptions and making the function idempotent.
2. **Bounded log buffer**: iterating and doing `logs.append(evento)` keeps only the last five; `list(logs)` shows final content.
3. **Sliding window metrics**: after each insert, compute `promedio = sum(mediciones) / len(mediciones)`; the test checks that after many inserts, `len(mediciones)` is still 3.

---

## Summary
`collections.deque` is an efficient solution for queues, stacks, and sliding windows. You know when to prefer it over lists, how to use `maxlen`, and how to validate behavior with simple tests.

## Closing reflection
With robust queues you can build rate limiters, buffers, and event processors that scale better. You now have the foundation to integrate these structures into APIs, workers, and observability tools — completing a strong intro to core Python data structures.
