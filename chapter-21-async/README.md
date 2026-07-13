# Chapter 21 · Friendly Concurrency: Intro to `asyncio`

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll explore why concurrency exists, the difference between threads and async, and build small async tasks with `asyncio`. We’ll simulate slow API calls and see how `await` lets your program move forward without blocking.

## Learning path
1. **Motivation**: tasks that wait (I/O).
2. **Basic `async`/`await`**.
3. **`asyncio.sleep`, `gather`, `create_task`**.
4. **Common mistakes and cancellation**.
5. **Bonus level (optional)**: async HTTP with external libraries.

## Learning objectives
- Understand CPU work vs I/O work.
- Write `async def` functions and use `await`.
- Run multiple tasks “at the same time” with `asyncio.run` and `gather`.
- Handle exceptions in async tasks.

## Why it matters
Modern services often wait for external responses (APIs, databases). Async programming lets you use that waiting time to do other things.

### Mini adventure
Imagine you work in a café. While you wait for the coffee machine, you serve water or take another order. That’s what `asyncio` does: while one task “cooks”, you can move on to another instead of staring at the machine.

### One important sentence
If this feels weird at first, that’s normal. The key idea today is: **when a task is waiting**, your program can keep making progress elsewhere.

## Prerequisites
- Functions, exceptions, loops, and a clear distinction between CPU work and waiting for I/O.
- CPython 3.11+; every required example is local and uses only the standard library.

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

## 2. Running tasks concurrently

```python illustrative
async def procesar(usuario):
    await asyncio.sleep(1)
    return f"Listo {usuario}"

async def main():
    usuarios = ["Noor", "Frej", "Taha"]
    tareas = [asyncio.create_task(procesar(u)) for u in usuarios]
    for tarea in tareas:
        print(await tarea)

asyncio.run(main())
```

- All tasks start almost at the same time.

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

- `gather` returns a list of results in order.

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

Cancellation is a recoverable control path: use `finally` to release resources, then await the cancelled task and handle `CancelledError` at the coordinating boundary.

---

## Guided exercises (with TODOs)
1. **21-1 · Concurrent timer**
   ```python todo
   # TODO 1: launch 3 tasks that sleep different times and observe the order
   ```
   *Hint*: return each delay from the task and collect completion order separately from creation order.

2. **21-2 · API simulator (no Internet)**
   ```python todo
   # TODO 1: create async def fake_get(url): await asyncio.sleep(1); return {"url": url, "ok": True}
   # TODO 2: use asyncio.gather to request 3 "urls" concurrently
   # TODO 3: print the result list
   ```
   *Hint*: pass the coroutines directly to `asyncio.gather` and run one top-level `main()`.

3. **21-3 · Handle cancellations**
   ```python todo
   # TODO 1: cancel a task with task.cancel()
   # TODO 2: handle asyncio.CancelledError
   ```
   *Hint*: await the cancelled task inside `try/except` and put resource cleanup in the task's `finally` block.

---

## Common mistakes
- Forgetting `await` and getting `coroutine` objects.
- Calling `asyncio.run` inside a function that is already async (not allowed).
- Mixing blocking calls (`requests`) inside async functions ⇒ you lose the benefit.

---

## Explained solutions
1. **Timer**: `asyncio.sleep` with different seconds shows tasks finish by duration.
2. **API simulator**: `fake_get` returns a dict after waiting; `asyncio.gather` collects all results into a list.
3. **Cancellation**: `task.cancel()` triggers `CancelledError`, which you can catch to clean up.

---

## Summary
With `asyncio` you can coordinate I/O-waiting tasks without blocking the whole program, preparing your mind for async frameworks like FastAPI.

## Checkpoint and rubric
- **Correctness**: one event loop runs concurrent tasks and preserves result ordering where promised.
- **Readability**: coroutine, task, and coordinator responsibilities are distinct.
- **Error handling**: task failure and cancellation both clean up resources.
- **Verification**: execute each runnable block and observe results and cancellation messages.
- **Explanation**: explain when async helps and why blocking calls remove the benefit.

## Closing reflection
Use this introduction to recognize when async is helpful. Not everything needs it — but when used well, it can make your services much more efficient.
