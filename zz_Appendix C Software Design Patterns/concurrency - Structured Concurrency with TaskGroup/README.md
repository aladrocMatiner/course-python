# Structured concurrency with `TaskGroup` — Chapter 21 cross-link

Canonical English lesson. Localized editions are not part of this implementation slice.

## At a glance

| Field | Contract |
|---|---|
| Family | Concurrency ownership |
| Status | Cross-link; Chapter 21 owns implementation and behavioral evidence |
| Route | Network Crosswalk, after Advanced and required Capacity checkpoints |
| Prerequisites | Chapter 21 `async`/`await`, failure, cancellation, and cleanup; Appendix C ownership vocabulary |
| Time | 25–35 minutes |
| Runtime | Read-only standard-library AST trace; authoring run on CPython 3.13.11 |
| Owner | [`chapter-21-async/structured_async.py`](../../chapter-21-async/structured_async.py) and its tests |
| Local companion | [`example.py`](example.py), import-safe and offline |

This page does not duplicate Chapter 21 or present `TaskGroup` as a new named
design-pattern implementation. It is a guided ownership reading. By the local
checkpoint, you should be able to identify who creates each task, who waits
for it, how sibling failure propagates, and where cleanup finishes.

## Pressure before the comparison

A coroutine can call `asyncio.create_task()` and return while that work still
runs. Once the task loses a visible owner, shutdown, failure, and cancellation
become difficult to reason about. A list of tasks is not enough unless some
scope is responsible for waiting for every member on success and failure.

**Structured concurrency** means concurrent work lives inside a lexical owner:
child lifetime cannot silently outlive that scope. In Python 3.11+,
`asyncio.TaskGroup` provides that ownership boundary for related tasks. On a
non-cancellation child failure it cancels unfinished siblings, waits for their
cleanup, and reports grouped failures at group exit.

The plain-language question is: **who can return only after every child has
finished or cleaned up?** If the answer is unclear, ownership is incomplete.

## The simplest option first

Use sequential `await` when work need not overlap. Use `asyncio.gather` when
its ordered-result contract is the main requirement and its failure semantics
are deliberately accepted. Use one `TaskGroup` when related concurrent work
must share a clear lifetime and sibling-cleanup boundary.

### Use this ownership shape when

- child tasks are required parts of one operation;
- the enclosing coroutine must not return with owned children alive;
- sibling failure should cancel unfinished sibling work; and
- each child has a `finally` cleanup path.

### Do not reach for it when

- one sequential await is clearer;
- work intentionally has a longer application lifetime and already has a
  different explicit owner; or
- blocking or CPU-heavy calls would still block the event-loop thread.

The cost is cancellation-aware child code, `ExceptionGroup` handling, explicit
timeouts, and tests for cleanup. Remove unnecessary concurrency when overlap
does not improve the design or observable behavior.

## Predict, trace, observe

Before tracing, predict:

1. Which Chapter 21 functions contain a `TaskGroup`?
2. Where does the timeout owner surround the group?
3. Which function contains the `finally` cleanup marker?

Run `python -I -B "zz_Appendix C Software Design Patterns/concurrency - Structured Concurrency with TaskGroup/example.py"`
from the repository root. The script parses the owning source without importing
or executing it. It therefore creates no task and makes no timing claim.

The trace reports three owned scopes—`successful_group`, `failing_group`, and
`timed_group`—six `create_task` call sites, a timeout in `timed_group`, and the
worker's cleanup function. The final line says explicitly that Chapter 21 tests
own behavioral evidence.

To verify behavior, use Chapter 21's documented command from
[`README.md`](../../chapter-21-async/README.md#cancellation-and-cleanup). Do not
turn this static trace into a claim that failure, cancellation, or cleanup ran.

## Normal, boundary, and recoverable readings

**Normal reading:** `successful_group` creates two tasks inside one group and
reads results only after the context exits. Result-list order comes from the
saved task objects; it is not a promise about completion order.

**Boundary reading:** `failing_group` gives both children the same owner. The
failure of one child causes unfinished sibling cancellation, and the source
handles only the declared `ValueError` leaves with `except*` after group exit.
Unexpected leaves must remain visible.

**Recoverable reading:** `timed_group` places the group inside
`asyncio.timeout`. Expiry cancels the owned operation, each worker reaches
`finally`, the group waits, and `TimeoutError` is handled outside the timeout
context. Recovery means cleanup completes and the caller receives the declared
outcome; it does not mean swallowing cancellation inside a worker.

A missing or syntactically invalid owner file makes the local trace fail with a
stable `SourceTraceError`. Restore the complete repository source and rerun;
never copy a stale Chapter 21 implementation into this appendix.

Common mistakes are creating tasks before entering their owner, reading results
before group exit, swallowing `CancelledError`, catching all grouped leaves,
and using fixed sleeps as cleanup evidence.

## Guided exercise

Complete this ownership worksheet for `timed_group` without editing Chapter 21:

- creator of each child;
- owner that waits for all children;
- signal that starts cancellation;
- location of child cleanup; and
- boundary that receives the recovered timeout.

**Hint:** follow nesting from the outer `asyncio.timeout`, into `TaskGroup`, to
`worker`, and then back out. “The event loop” is too broad to be the owner in
this worksheet.

**Observable success criterion:** your answer names the enclosing coroutine,
the `TaskGroup` context, the timeout expiry, `worker`'s `finally`, and the
`except TimeoutError` boundary in that order. It claims no restart behavior.

### Explained solution

`timed_group` is the operation owner. Its timeout bounds the whole nested scope.
The group owns the two created child tasks and cannot finish its exit until
their cleanup finishes. Timeout initiates cancellation; `worker` owns its
resource cleanup; only after group exit can the outer handler record
`timeout:handled`. This is lifetime ownership, not a restart policy.

Decision record:

> related tasks risk escaping their caller → one lifetime, sibling failure,
> bounded cleanup → sequential awaits → `TaskGroup` ownership from Chapter 21
> → cancellation and grouped-error complexity → swallowed cancellation or
> unfinished child → Chapter 21 success/failure/timeout/cleanup tests → remove
> concurrency when sequential work is sufficient

## Checkpoint and navigation

You pass this cross-link checkpoint when you can:

- trace create → own → cancel/fail → cleanup → propagate for every child;
- distinguish result order from completion order;
- keep static source evidence separate from Chapter 21 behavioral evidence; and
- explain why `TaskGroup` alone supplies no restart policy.

Review the owning
[Chapter 21 section](../../chapter-21-async/README.md#2-own-concurrent-tasks-with-taskgroup),
then continue to the
[Supervisor-like comparison](<../concurrency - Supervisor Like Ownership/README.md>)
and [Reactor-like source trace](<../network - Reactor/README.md>).

Safe stop: sequential awaits remain a complete, explicit ownership choice.
