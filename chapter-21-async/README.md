# Chapter 21 · Friendly Concurrency: Intro to `asyncio`

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll explore why concurrency exists, the difference between threads and async, and build small async tasks with `asyncio`. We’ll simulate slow API calls and see how `await` lets your program move forward without blocking.

## Learning path
1. **Motivation**: tasks that wait (I/O).
2. **Basic `async`/`await`**.
3. **Owned concurrency with `TaskGroup`**, then `gather` for ordered results.
4. **Timeouts, failures, cancellation, and cleanup**.
5. **Bonus level (optional)**: async HTTP with external libraries.

## Learning objectives
- Understand CPU work vs I/O work.
- Write `async def` functions and use `await`.
- Distinguish cooperative asyncio tasks from operating-system threads.
- Own concurrent work with `TaskGroup` and bound it with `asyncio.timeout` on Python 3.11+.
- Handle task failure and cancellation without swallowing cleanup signals or leaving background work.

## Why it matters
Modern services often wait for external responses (APIs, databases). Async programming lets you use that waiting time to do other things.

### Mini adventure
Imagine you work in a café. While you wait for the coffee machine, you serve water or take another order. That’s what `asyncio` does: while one task “cooks”, you can move on to another instead of staring at the machine.

### One important sentence
If this feels weird at first, that’s normal. The key idea today is: **when a task is waiting**, your program can keep making progress elsewhere.

### Tasks are not threads
An asyncio task is cooperatively scheduled by one event loop, normally in one operating-system thread. It gives other tasks a turn only when it reaches an `await` that can suspend. A thread is scheduled by the operating system and can run blocking code independently, with different synchronization risks. Therefore, putting `requests.get()` or CPU-heavy work directly inside `async def` still blocks the event-loop thread; use an async library, split CPU work appropriately, or deliberately isolate a blocking call with `asyncio.to_thread` when that trade-off is justified.

## Prerequisites
- Functions, exceptions, loops, and a clear distinction between CPU work and waiting for I/O.
- CPython 3.11+; every required example is local and uses only the standard library.

## Predict before you run
Before awaiting the first coroutine, predict when its body starts and which statement can let another task run. After executing the bounded example, compare the observed order with your prediction without using a fixed sleep as proof of scheduling.

---

## 1. An async function

```python illustrative
import asyncio

async def saludar(nombre):
    await asyncio.sleep(1)
    return f"Hola {nombre}"

async def main():
    mensaje = await saludar("Noor")
    print(mensaje)

asyncio.run(main())
```

- `asyncio.sleep` simulates I/O work.
- `await` means “wait here, but let other tasks run if they can”.

---

## 2. Own concurrent tasks with `TaskGroup`

```python runnable
import asyncio

async def procesar(usuario):
    await asyncio.sleep(0)
    return f"Listo {usuario}"

async def main():
    usuarios = ["Noor", "Frej", "Taha"]
    async with asyncio.TaskGroup() as group:
        tareas = [group.create_task(procesar(u)) for u in usuarios]
    print([tarea.result() for tarea in tareas])

asyncio.run(main())
```

- The context owns every created task and does not exit until all of them finish.
- If one child fails, `TaskGroup` cancels its unfinished siblings, waits for their cleanup, and raises an `ExceptionGroup`. Catch an expected leaf failure with `except*` outside the group; do not discard unexpected failures.

---

## 3. `asyncio.gather`

```python runnable
import asyncio

async def procesar(usuario):
    await asyncio.sleep(0)
    return f"Listo {usuario}"

async def main():
    resultados = await asyncio.gather(
        procesar("Noor"),
        procesar("Frej"),
    )
    print(resultados)

asyncio.run(main())
```

- `gather` returns a list of results in input order. It remains useful when that result contract is the main goal, but `TaskGroup` makes task lifetime and sibling cleanup explicit for required concurrent work.

---

## 4. Errors in tasks

```python runnable
import asyncio

async def puede_fallar():
    raise ValueError("Oops")

async def main():
    try:
        await puede_fallar()
    except ValueError as exc:
        print("Capturado", exc)

asyncio.run(main())
```

- Handle exceptions like normal functions, but with `await`.

### Bound a group with `asyncio.timeout`
```python runnable
import asyncio

async def slow(name, events):
    events.append(f"{name}:start")
    try:
        await asyncio.sleep(10)
    finally:
        events.append(f"{name}:cleanup")

async def main():
    events = []
    try:
        async with asyncio.timeout(0.02):
            async with asyncio.TaskGroup() as group:
                group.create_task(slow("a", events))
                group.create_task(slow("b", events))
    except TimeoutError:
        events.append("timeout:handled")
    print(sorted(events))

asyncio.run(main())
```

The timeout cancels the current operation; the task group propagates cancellation to its children and waits for both `finally` blocks. Catch `TimeoutError` outside the timeout context. A child failure follows the same ownership rule: siblings are cancelled and cleaned before the group reports the failure.

### Cancellation and cleanup
```python runnable
import asyncio

async def trabajo_largo():
    try:
        await asyncio.sleep(10)
    finally:
        print("Limpieza completada")

async def main():
    tarea = asyncio.create_task(trabajo_largo())
    await asyncio.sleep(0)
    tarea.cancel()
    try:
        await tarea
    except asyncio.CancelledError:
        print("Tarea cancelada")

asyncio.run(main())
```

Cancellation is a recoverable control path: use `finally` to release resources, then await the cancelled task and handle `CancelledError` at the coordinating boundary. Inside the cancelled worker, do not catch `CancelledError` and continue as if nothing happened; let it propagate after cleanup.

The companion [structured-concurrency implementation and tests](structured_async.py) cover success, child failure, timeout, sibling cancellation, cleanup, and absence of leftover tasks. From `chapter-21-async/`, run `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

---

## Guided exercises (with TODOs)
1. **21-1 · Concurrent timer**
   ```python todo
   # TODO 1: launch 3 owned tasks in a TaskGroup and observe completion vs result order
   ```
   *Hint*: retain the task objects created by the group; read `.result()` only after the context exits.

2. **21-2 · API simulator (no Internet)**
   ```python todo
   # TODO 1: create async def fake_get(url): await asyncio.sleep(1); return {"url": url, "ok": True}
   # TODO 2: use asyncio.gather to request 3 "urls" concurrently
   # TODO 3: print the result list
   ```
   *Hint*: pass the coroutines directly to `asyncio.gather` and run one top-level `main()`.

3. **21-3 · Handle cancellations**
   ```python todo
   # TODO 1: bound a TaskGroup with asyncio.timeout
   # TODO 2: give each worker a finally cleanup marker
   # TODO 3: verify no child remains after TimeoutError
   ```
   *Hint*: catch `TimeoutError` outside the timeout context and put resource cleanup in each task's `finally` block.

---

## Common mistakes
- Forgetting `await` and getting `coroutine` objects.
- Calling `asyncio.run` inside a function that is already async (not allowed).
- Mixing blocking calls (`requests`) inside async functions ⇒ you lose the benefit.
- Creating tasks without an owner and returning while they still run.
- Swallowing `CancelledError` inside a worker, which can break `TaskGroup` and timeout cleanup.

---

## Explained solutions
1. **Timer**: create all timers inside one `TaskGroup`; after its context exits, every task is complete and `.result()` can be read safely. Record completion order separately if that is what you want to observe.
2. **API simulator**: `fake_get` returns a dict after waiting; `asyncio.gather` collects all results into a list.
3. **Cancellation**: `asyncio.timeout` cancels the owned operation; each worker cleans up in `finally`, the group waits for all siblings, and the coordinator catches `TimeoutError` after the context. Confirm `asyncio.all_tasks()` contains no unfinished task except the current test task.

---

## Summary
With `asyncio` you can coordinate I/O-waiting tasks without blocking the whole program, preparing your mind for async frameworks like FastAPI.

## Checkpoint and rubric
- **Correctness**: one event loop owns concurrent tasks and preserves result ordering only where promised.
- **Readability**: coroutine, task, and coordinator responsibilities are distinct.
- **Error handling**: task failure and timeout cancel siblings, propagate correctly, and clean up resources.
- **Verification**: execute each runnable block and prove success, failure, and timeout leave no background task.
- **Explanation**: explain tasks versus threads, when async helps, and why blocking calls remove the benefit.

## Closing reflection
Use this introduction to recognize when async is helpful. Not everything needs it — but when used well, it can make your services much more efficient.
