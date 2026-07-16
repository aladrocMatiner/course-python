# Bulkhead — isolate local and remote admission capacity

Canonical English lesson. Localized editions are not part of this implementation slice.

## At a glance

| Field | Contract |
|---|---|
| Family | Network capacity |
| Status | Executable |
| Route | Required Capacity checkpoint |
| Prerequisites | Resilience checkpoint; Chapter 23 selectors, bounded concurrency, and cleanup |
| Time | 45–60 minutes |
| Runtime | Standard library; course target CPython 3.11+; authoring run on CPython 3.13.11 |
| Companion | [`example.py`](example.py), offline and import-safe |
| Explicit limits | Published run per compartment: 1 running, 1 waiting, 50 ms fake timeout; hard caps: 64 running, 64 waiting, 60 finite seconds, 64-character names/IDs |

By the checkpoint, you should be able to show that remote saturation consumes
no local admission, that a third remote proposal is rejected immediately, and
that timed-out capacity is reusable.

## Pressure before the pattern name

Imagine a job runner that performs both local disk work and calls to a slow
remote dependency. One shared concurrency cap prevents unlimited work, but a
remote stall can occupy every slot and stop healthy local work. An unlimited
wait queue merely moves the overload into memory and latency.

A Bulkhead creates a finite admission compartment for a failure domain. This
lesson uses exactly two: `local` and `remote`. Each admits one running request
and retains at most one waiting proposal. A third proposal to the same full
compartment fails with `overloaded` without allocating a task or queue entry.

Bulkhead is admission isolation. It is not a timeout, Retry, Circuit Breaker,
rate limiter, or stream `drain()` mechanism. Those responsibilities may be
composed, but they own different decisions.

## The simplest option first

Use one semaphore or fail-fast counter when one shared cap is the real policy.
Use no pattern for small sequential programs. Two compartments are justified
only when local and remote work form observable, independently recoverable
failure domains.

### Use it when

- one dependency's saturation must not consume another domain's capacity;
- running work and waiting admission have explicit finite bounds;
- timeout/cancellation can remove a waiter exactly once; and
- later work must recover the released slot predictably.

### Do not use it when

- all work genuinely shares one capacity budget;
- a queue has no declared maximum or admission deadline;
- priorities or fairness are required but not designed; or
- it is being used as a false health signal for Circuit Breaker.

The cost is explicit admission state, failure-domain classification, cleanup
for waiting/running ownership, and more boundary tests. Remove the split when a
single cap is the measured policy or isolation provides no observable benefit.

## Predict, run, observe

First predict: remote request 1 is running and request 2 is waiting. What does
remote request 3 allocate? Can local request 1 still run? After the only
remote waiter reaches its 50 ms deadline, can a later remote request enter?

Run `python -I -B "zz_Appendix C Software Design Patterns/network - Bulkhead/example.py"`
from the repository root. The example advances an injected fake clock. It
creates no worker task, socket, sleep, or hidden queue.

Observe:

- `remote:overloaded` appears with one remote running and one remote waiting;
- `local-1` is admitted while the remote compartment remains full; and
- `remote-2` expires, the running lease is released, and
  `remote-recovery` enters with zero waiters.

The cleanup observation releases `remote-recovery` twice: the second call is
an idempotent no-op and the running count stays zero. The configuration
boundary rejects `waiting_limit=True`; boolean values cannot masquerade as
integer capacity and existing local/remote state is unchanged.

## Normal, boundary, and recoverable paths

**Normal path:** one local and one remote lease coexist because their owners
are independent. Releasing a lease removes it exactly once. If a live waiter
exists, release promotes only that one waiter.

**Boundary:** one running plus one waiting is the exact maximum per
compartment. A third proposal raises `Overloaded` immediately and retains no
request state. Saturating remote changes no local count.

Configured running/waiting values must be bounded integers, never booleans:
running is `1..64`, waiting is `0..64`, and admission time is finite, positive,
and at most 60 fake seconds. Names and request IDs are non-empty text bounded to
64 characters. A non-finite/backwards clock or an overflowing deadline is
rejected before a new admission is retained.

**Recoverable error:** fake time reaches the waiting deadline. Expiry marks and
removes the waiter before later admission. Releasing the running lease restores
capacity; a fresh remote request then enters. In an asynchronous production
version, caller cancellation must perform the same one-time removal and remain
visible to its caller. This synchronous lesson does not claim task-cancellation
evidence.

Lease ownership is explicit. Releasing a live lease removes it once; repeating
that release safely returns `None`, while a lease from another compartment is a
stable `lease_does_not_belong_to_bulkhead` error. Correct invalid configuration
and try a later admission rather than coercing or widening the cap.

Admission failure before a dependency call is local and neutral to Circuit
Breaker health. If a prior Retry attempt already produced a transient result,
that transient remains the final health evidence; overload must not invent a
second negative.

Common mistakes are one shared compartment for unrelated domains, an unlimited
wait queue, holding a lease during Retry backoff, counting overload as remote
failure, and releasing the same lease through several cleanup paths.

## Guided exercise

In a temporary copy, add a scenario that releases `remote-1` **before** the
50 ms waiter deadline. Capture the object returned by `release()`.

**Hint:** a live `WaitingAdmission` changes to `promoted`; the returned
`Lease` should carry the same request ID.

**Observable success criterion:** `remote-2` becomes the only running lease,
the remote waiting count becomes zero, and local counts do not change. Release
the promoted lease and verify a fresh remote request can enter.

### Explained solution

Promotion belongs to `release()` because that method owns the transition from
occupied to available capacity. It first removes the exact lease, expires
stale waiters, and promotes at most one live waiter. Letting the caller mutate
the internal deque would split ownership and make cancellation races harder to
reason about.

Decision record:

> remote saturation blocks healthy local work → independent domains and finite
> admission → one shared semaphore or fail-fast counter → two Bulkheads →
> admission state and cleanup → overload, timeout, or leaked lease → exact
> count/isolation/recovery checks with fake time → remove when one shared cap is
> the real policy

## Checkpoint and navigation

You pass this local checkpoint when you can:

- prove remote saturation leaves local admission available;
- state the one-running/one-waiting/50 ms limits without hidden capacity;
- recover after promotion, expiry, and release with no residual waiter; and
- reject boolean/over-cap/non-finite configuration and make repeated owned
  release idempotent; and
- distinguish admission from timeout, Retry, health gating, and backpressure.

Previous: [Circuit Breaker](<../network - Circuit Breaker/README.md>). The
[bounded local Publish/Subscribe lesson](<../network - Bounded Local Publish Subscribe/README.md>)
is optional and supplies no required Capacity points. Complete the required
[Capacity checkpoint](../README.md#capacity-checkpoint-rubric-and-stop) before
entering the network crosswalk.

Safe stop: use one finite semaphore/fail-fast counter when separate failure
domains are not yet established.
