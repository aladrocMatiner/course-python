# Reactor-like responsibility trace — Chapter 23 cross-link

Canonical English lesson. Localized editions are not part of this implementation slice.

## At a glance

| Field | Contract |
|---|---|
| Family | Network readiness and dispatch reading |
| Status | Cross-link; Chapter 23 owns transport implementation and evidence |
| Route | Final Network Crosswalk after Advanced and required Capacity checkpoints |
| Prerequisites | Chapter 23 sections 7–8; Capacity checkpoint; `TaskGroup` ownership reading |
| Time | 30–40 minutes |
| Runtime | Read-only standard-library AST trace; authoring run on CPython 3.13.11 |
| Owner | [`selector_hub.py`](../../chapter-23-network-programming/examples/telemetry/selector_hub.py) and Chapter 23 network tests |
| Local companion | [`example.py`](example.py), import-safe, offline, and socket-free |

This page neither rebuilds the selector hub nor claims Chapter 23 implements a
named Reactor pattern. It traces an existing source owner's registration,
readiness, dispatch, and cleanup responsibilities and labels “Reactor-like” as
an interpretation.

## Pressure before the interpretation

A sequential server can block inside one peer's `recv()` while another peer is
ready. A selector-based hub registers interests, asks the operating system
which registered object is ready, dispatches a bounded handler, updates the
next interest, and closes idle or failed peers.

Calling `selector.select()` is not the whole design. The owner must also:

- register and unregister the listener and peers;
- distinguish accept, read, and write readiness;
- retain only bounded peer/protocol/output state;
- update READ/WRITE interest as state changes; and
- expire and close every resource idempotently.

Those roles resemble a Reactor responsibility split: readiness events are
demultiplexed and dispatched to handlers. The owning module calls itself a
bounded selectors implementation, not a Reactor. Keep the interpretation and
the source's tested claim separate.

## The simplest option first

Use a blocking sequential server for one controlled peer. Use
`socketserver` when its synchronous packaging fits. Prefer `asyncio` streams
owned by a `TaskGroup` when high-level streams express the needed lifecycle
more clearly. A custom readiness dispatcher is justified only when explicit
interest control and bounded peer state are real requirements.

### Use this reading when

- you must explain who owns selector registration and close;
- READ and WRITE interest changes matter to bounded progress;
- one slow peer must not block an unrelated ready peer; and
- Chapter 23 tests already own real loopback behavior.

### Do not turn it into a new implementation when

- streams plus `TaskGroup` are simpler;
- the goal is merely to attach a pattern name to one API call;
- transport, framing, backpressure, or cleanup would be duplicated; or
- there is no plan to test partial input, stalled output, idle expiry, and
  shutdown.

The cost of a custom selector hub is precise interest state, per-peer limits,
protocol framing, idempotent close, and lifecycle tests. Remove or avoid it
when higher-level streams satisfy the same observable requirements.

## Predict, trace, observe

Before running, predict:

1. Which call asks for readiness?
2. Which three calls own interest registration changes?
3. Which methods dispatch accept, read, and write work?
4. Does the owner source itself use the word `Reactor`?

Run `python -I -B "zz_Appendix C Software Design Patterns/network - Reactor/example.py"`
from the repository root. The script reads and parses `selector_hub.py`; it
does not import the module, instantiate its class, open a socket, run its loop,
or create a task.

The trace reports `select`; `register`, `modify`, and `unregister`; the
`_accept`, `_read`, and `_write` handlers; and idle/peer/final cleanup methods.
It also reports `owner_names_reactor=no` and repeats the interpretation-only
boundary.

Actual partial/coalesced framing, 32-client capacity, idle expiry, backpressure,
and shutdown remain owned by
[Chapter 23's tests and plugin](../../chapter-23-network-programming/README.md#11-run-all-evidence).
The local trace proves only that the inspected source contains the named
responsibility signals.

## Normal, boundary, and recoverable readings

**Normal reading:** the hub registers a peer for READ. When readiness is
reported, `_read` advances bounded decoder state. Once one response is ready,
the hub changes interest to WRITE; `_write` sends only when ready and then
returns interest to READ.

**Boundary:** peer A holds a partial frame or pending response while peer B is
ready. A's state remains bounded; selection can dispatch B. A 33rd client is
closed rather than admitted to hidden capacity. These behaviors are Chapter 23
claims, not outcomes executed by this trace.

**Recoverable error:** protocol/I/O failure or one second without progress
routes to `_close_peer`, which removes owned state, unregisters, and closes.
The top-level `finally` closes all peers, listener, and selector. Repeated
unregister attempts tolerate only the expected ownership errors.

If the owner is missing, syntactically invalid, or loses required responsibility
signals, the trace raises `SourceTraceError`. Restore or review Chapter 23;
do not patch this cross-link with a second transport implementation.

Common mistakes are treating one `select()` call as the full design, leaving a
socket permanently writable, growing output or history without a bound,
forgetting unregister-before-close, and claiming socket behavior from AST.

## Guided exercise

Fill one row for each of these existing responsibilities: registration,
selection, interest update, dispatch, idle expiry, and close. For every row
record owner, input/permission, normal result, boundary/failure, cleanup, and
evidence mode.

**Hint:** start at `SelectorTelemetryHub.__init__`, follow `serve()`, then each
private handler, and finish at `close()`. Use “source trace” for structure and
“Chapter 23 network suite” only for behavior that suite actually executes.

**Observable success criterion:** all six rows name a concrete method; no row
says `select()` owns cleanup; behavioral claims point back to Chapter 23; and
the final design label remains “Reactor-like interpretation.”

### Explained solution

`__init__` owns initial listener registration. `serve()` owns repeated
readiness selection and chooses `_accept`, `_read`, or `_write` from listener
identity and the event mask. Handlers own one bounded state transition and
modify the next interest. `_expire_idle_peers` detects no-progress boundaries;
`_close_peer` owns peer removal/unregister/close; `close` owns final global
release. No single line owns the entire lifecycle.

Decision record:

> slow peers must not block ready peers → explicit readiness, bounded state,
> deterministic cleanup → `asyncio` streams plus `TaskGroup` → retain Chapter
> 23 selector hub and read it Reactor-like → manual interest/lifecycle cost →
> stale interest or leaked peer → Chapter 23 protocol/lifecycle suite plus this
> source trace → prefer streams when explicit readiness control is unnecessary

## Checkpoint and navigation

You pass this cross-link checkpoint when you can:

- trace registration → readiness → bounded dispatch → interest update → close;
- distinguish source structure, Chapter 23 behavior, and pattern interpretation;
- explain why a partial peer does not justify blocking a ready peer; and
- defend streams + `TaskGroup` as the simpler accepted alternative when it fits.

Required prior readings: [Bulkhead](<../network - Bulkhead/README.md>),
[`TaskGroup` ownership](<../concurrency - Structured Concurrency with TaskGroup/README.md>),
and the [Supervisor-like comparison](<../concurrency - Supervisor Like Ownership/README.md>).
Return to the [Appendix C final Crosswalk rubric](../README.md#final-rubric-and-reflection)
and the owning
[Chapter 23 selector lesson](../../chapter-23-network-programming/README.md#7-several-clients-with-selectors).

Safe stop: use Chapter 23's tested stream-based route and keep this page as an
ownership-reading aid.
