# Bounded local Publish/Subscribe — enqueue is not delivery

Canonical English lesson. Localized editions are not part of this implementation slice.

## At a glance

| Field | Contract |
|---|---|
| Family | Behavioral notification and network-capacity comparison |
| Status | Executable, optional |
| Route | Optional Capacity extension; never gates Crosswalk |
| Prerequisites | Observer vocabulary; [Bulkhead](<../network - Bulkhead/README.md>); bounded queues |
| Time | 35–45 minutes |
| Runtime | Standard library; course target CPython 3.11+; authoring run on CPython 3.13.11 |
| Companion | [`example.py`](example.py), process-local, offline, and import-safe |
| Explicit limits | Published run: 4 subscribers and 8 events each; hard caps: 64 subscribers, 1,024 queued each, 64-character IDs, 256-character events; no consumer task/history |

By the checkpoint, you should be able to separate synchronous notification
from bounded enqueueing and refuse every claim that `publish()` proves delivery
or processing.

## Pressure before the pattern name

One job event may interest several local components. Direct synchronous calls
make the publisher wait for every listener, so a slow listener can block the
others. An in-memory event bus can decouple enqueueing, but an unlimited queue
turns a slow subscriber into unbounded memory growth.

This lesson's Publish/Subscribe object owns a separate finite first-in,
first-out queue for each opaque subscriber ID. Publishing enqueues for healthy
subscribers. It does not run a consumer. A full subscriber is disconnected and
only its discarded **count** is reported; healthy queues continue.

This is process-local, non-durable, enqueue-only behavior. There is no network,
broker, replay, acknowledgement, retry, persistent history, or remote-delivery
claim.

## The simplest option first

Use direct calls for one recipient. Use synchronous Observer when listeners are
few, bounded, and should complete now. Use a standard durable broker only when
the application truly needs remote delivery semantics and the team can own its
operational contract; this lesson is not a miniature replacement for one.

### Use it when

- local producers must enqueue independently for several bounded consumers;
- per-subscriber FIFO order is enough;
- slow-subscriber removal is an accepted policy; and
- callers understand that enqueue success ends at the local queue boundary.

### Do not use it when

- synchronous direct notification is simpler;
- durable, remote, exactly-once, replay, or acknowledgement semantics are
  required;
- discarded event contents would be logged or exposed; or
- queues or subscriber registration have no finite limit.

The cost is queue capacity, subscriber lifecycle, overflow policy, and a new
semantic boundary between enqueue and processing. Remove it when there is one
recipient or notification can remain synchronous.

## Predict, run, observe

Predict before running: `slow` has eight queued events while `fast` consumes
each event. On the ninth publish, which subscriber is disconnected, which
subscriber receives an enqueue, and may the result say “delivered”?

Run `python -I -B "zz_Appendix C Software Design Patterns/network - Bounded Local Publish Subscribe/example.py"`
from the repository root. The finite event sequence injects the slow-consumer
condition; the script creates no background consumer, socket, sleep, or
unbounded queue.

Observe that the first result lists `fast` and `slow` under `enqueued` while
only an explicit `consume_one("fast")` observes content. On the ninth publish,
`slow` is disconnected with discarded count eight and `fast` remains healthy.
A replacement reuses the slot. A fifth registration reports `resource_limit`
and leaves the first four registrations unchanged.

The input boundary rejects a 257-character event before touching any queue;
queue counts remain unchanged and a later bounded event still enqueues. The
configuration recovery rejects `max_subscribers=True`: capacity fields must be
real positive integers rather than booleans.

## Normal, boundary, and recoverable paths

**Normal path:** an event is appended once to each healthy queue in stable
subscriber order. Each subscriber consumes its own FIFO independently.
`PublishResult.enqueued` describes only the completed append operation.

**Boundary:** the fifth subscriber is rejected before mutation. The ninth event
does not enter a queue already holding eight items. No queue can silently evict
its oldest event because the code checks fullness before `append()`.

Counts alone do not bound memory if one event or identifier can be arbitrarily
large. Therefore subscriber IDs are non-empty text capped at 64 characters and
events at 256 characters. Configuration is also hard-capped at 64 subscribers
and 1,024 queued events each; booleans and over-cap integers fail with stable
codes before allocation.

**Recoverable error:** the full subscriber is removed, the result exposes only
its opaque ID and discarded count, and healthy queues still receive the event.
A later subscription can reuse the released slot. Consuming an empty or unknown
queue raises a stable local error; the caller may wait for later application
coordination or correct the subscriber ID, but must not invent delivery.

Oversized/empty/non-text input is atomic: correct the input and publish later;
existing queue contents and subscriber membership remain unchanged. Invalid
configuration is corrected by constructing a new bounded bus, never by silently
coercing `True`, `NaN`, or an unbounded value.

Common mistakes are equating enqueue with delivery, starting unowned consumer
tasks, allowing unlimited queues, blocking healthy subscribers behind a slow
one, leaking discarded payloads, and adding broker vocabulary to a local object.

## Guided exercise

In a temporary copy, publish `alpha` then `beta` to two subscribers. Consume
both events from subscriber A and only one from subscriber B.

**Hint:** call `consume_one` explicitly; `publish` never consumes. Preserve the
same order for each queue.

**Observable success criterion:** A observes `alpha`, then `beta`; B observes
`alpha` and retains one queued item. The publish results may list both IDs as
`enqueued` but contain no `delivered` field or wording.

### Explained solution

Each subscriber owns a distinct `deque(maxlen=8)`. Publishing appends to those
queues, while consumption removes from exactly one queue. Keeping these methods
separate makes the semantic boundary visible: producer completion says nothing
about when or whether application processing later succeeds.

Decision record:

> local fan-out must not let one slow subscriber block healthy ones → bounded
> independent queues and honest semantics → direct calls or synchronous
> Observer → bounded local Pub/Sub → queue/removal state → fifth subscriber or
> ninth queued event → four/eight/FIFO/disconnect/count-only checks → remove
> when notification can remain synchronous or one recipient remains

## Checkpoint and navigation

This optional checkpoint is complete when you can:

- demonstrate four/eight limits and per-subscriber FIFO;
- prove count, identifier, and event-size caps and atomic invalid-input recovery;
- explain, without qualification, why enqueue is not delivery;
- disconnect one full subscriber without stopping a healthy one; and
- reuse a removed slot without retaining discarded payload content.

Previous required lesson: [Bulkhead](<../network - Bulkhead/README.md>).
Pub/Sub supplies no required Capacity or Crosswalk credit. After the required
Capacity checkpoint, continue to the
[structured-concurrency cross-link](<../concurrency - Structured Concurrency with TaskGroup/README.md>)
and the [Reactor-like trace](<../network - Reactor/README.md>).

Safe stop: synchronous Observer or direct calls are complete alternatives.
