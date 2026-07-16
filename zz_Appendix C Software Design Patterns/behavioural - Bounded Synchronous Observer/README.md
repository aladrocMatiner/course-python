# Bounded Synchronous Observer

| Field | Value |
|---|---|
| Family | Behavioural |
| Status | Executable pattern |
| Route | Professional |
| Prerequisites | Callables, lists, closures, exceptions, tests |
| Estimated time | 35–45 minutes |

## Start with the pressure

A completed job must notify an audit view and a progress view. Listeners are
local, must be removable, and may change while notification is in progress.
The program also needs a clear upper bound and an explicit policy for a broken
listener. Those ownership pressures—not the desire for an “event system”—earn
a small Observer.

## The basic idea

The subject stores token-and-callback subscriptions and synchronously invokes a
stable snapshot. `subscribe()` returns a token-specific, idempotent removal
closure, so registering the same callback twice still creates two independently
owned subscriptions. A positive integer listener limit prevents unbounded
growth. One failing listener is reported while later listeners can still run;
this is a deliberate local policy, not a universal Observer rule.

This is not a background queue or network Pub/Sub. `notify()` finishes all
local work before returning.

## Simpler option, fit, and cost

- **Simpler option:** call one callback explicitly, or pass a short list of
  callbacks to one function.
- **Use it when:** several local listeners vary independently and require
  explicit registration and removal.
- **Do not use it when:** there is one required collaborator or delivery must
  survive process failure.
- **Cost:** ordering and failure policy, lifetime cleanup, capacity, and harder
  control-flow tracing.

## Predict, run, observe

Predict whether the healthy audit listener still receives the event when the
second listener raises, and whether removal frees capacity.

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  'zz_Appendix C Software Design Patterns/behavioural - Bounded Synchronous Observer/example.py'
```

```text illustrative
normal=delivered:2,received:['job-finished', 'job-finished']
failure=cannot record job-finished
boundary=listener limit reached
callback-boundary=listener must be callable
recovery=(1, ())
```

The duplicate entries show that two subscriptions of the same callback both
run. One token is removed twice without affecting the other; the tuple `(1, ())`
then means one remaining delivery and no listener errors after the broken
listener is removed.

## Normal, boundary, and recoverable behavior

- Normal: two subscriptions of one callable both receive the event in
  registration order.
- Boundary: a fourth subscription is rejected at capacity; `None` is rejected
  before registration. Boolean, non-integer, and non-positive limits are also
  invalid.
- Recoverable failure: a listener exception is returned as evidence; removing
  that listener restores clean notification.
- Stable iteration: `tuple(self._subscriptions)` prevents in-flight removal
  from skipping an unrelated listener.

Do not catch `BaseException`; cancellation and process-exit signals are not
ordinary listener failures. For production code, prefer a narrower documented
exception contract than the teaching companion's `Exception` boundary.

## Guided exercise

Add a listener that unsubscribes itself when it receives its first event. Emit
two events.

**Hint:** store the removal closure in a small list so the callback can call it.
The current snapshot means it completes the first notification but is absent
from the second.

**Success criterion:** the self-removing listener records only the first event;
the audit listener records both; capacity is available afterward.

## Explained solution and decision record

Snapshot iteration defines what an in-flight change means. A unique token—not
callback equality—identifies each subscription. Idempotent token removal makes
cleanup safe in normal and recovery paths, even when one callback is registered
twice. If all listeners become fixed and mandatory, replace the subject with
explicit collaborator calls.

```text illustrative
several removable local notifications → ordering, failure, cleanup, capacity
→ explicit callback calls → bounded synchronous Observer
→ cost: lifecycle and delivery policy
→ verify snapshot, cap, failure report, removal, and recovery
→ remove when the collaborator set becomes fixed
```

## Checkpoint and navigation

Can you state who owns each subscription, when it is removed, the capacity, the
delivery order, and the listener-failure policy? If any answer is missing, the
Observer is not ready.

[Return to the Appendix C catalogue](../README.md#family-index) ·
[Continue the Professional route](../README.md#professional-route-cross-cutting-behavior-and-notifications)
