# Structural · Facade

## Pattern card

| Field | Value |
|---|---|
| Family | Structural |
| Status | Decision-card; the code is a verified contrast, not required architecture |
| Route | Advanced |
| Prerequisites | Functions, composition, exception boundaries, Professional checkpoint |
| Time | 20–30 minutes |

You will decide whether repeated clients need one stable entry point to a
multi-step subsystem, or whether one module function already provides it.

## Start with the pressure

Submitting a job requires validation, storage, and audit recording in a fixed
order. If several clients coordinate those steps themselves, one may skip
validation or record audit too early. With one caller, a well-named function is
already a clear boundary.

The pressure is repeated subsystem coordination. That pressure may justify a
**Facade**; the existence of three classes does not.

## The pattern in plain language

A Facade presents a small, task-oriented entry point over a more detailed
subsystem. It does not make validation, storage, or audit disappear. It gives
their order and ownership one home.

Python modules naturally act as lightweight facades. The companion's
`submit_job` function is the preferred alternative until clients need a
long-lived object with configured collaborators.

### Use it, avoid it, count its cost

- Consider it when several clients repeat the same safe orchestration and need
  one stable entry point.
- Avoid it when it becomes a “god object” containing unrelated use cases or
  when one module function is sufficient.
- Its cost is another public API and the risk of hiding important failure
  ownership.
- Remove it when there is one caller or when the subsystem itself exposes the
  correct task-oriented operation.

## Predict, run, observe

Before running, predict whether an empty payload reaches `MemoryStore.save` and
whether a failed submission adds an audit entry.

Run the verified contrast:

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B "zz_Appendix C Software Design Patterns/structural - Facade/example.py"
```

Expected output:

```text illustrative
job-1
stored:[('job-1', 'pack books')]
audit:['submitted:job-1']
boundary:payload must be non-empty text
state-after-boundary:1:1
recovered:job-2
```

The [Facade decision-card source](example.py) keeps the module function and the
class side by side. That makes the simpler choice impossible to forget.

## Normal, boundary, and recoverable behavior

- **Normal:** validation precedes storage, which precedes the audit record.
- **Boundary:** empty text fails before storage; no false audit record appears.
- **Recoverable:** after correcting the input, a new submission succeeds and
  receives the next identifier.

This bounded card proves only successful ordering and the invalid-input
no-mutation boundary. It does **not** simulate a store or audit failure and does
not claim rollback, atomicity, transactions, or safe retry. In particular, a
real audit failure after storage could leave partial state; its owner must
define and verify that policy before publication.

Common mistakes are claiming atomicity merely because calls share one Facade,
swallowing subsystem failures, or adding one method for every unrelated
subsystem operation.

## Guided decision exercise

Imagine there is one command-line client today and a web plus batch client next
month. Record what evidence would make you replace the function with
`JobFacade`, and what public methods the Facade must refuse to absorb.

**Hint:** repeated orchestration is evidence; a prediction about future clients
is not implemented evidence. Keep the current function until the second client
arrives.

**Success criterion:** the decision names a measurable adoption threshold, the
failure ordering, the Facade's narrow scope, and a removal condition.

## Explained solution and decision record

Keep `submit_job` for the single client. When multiple clients need configured
subsystem collaborators and the same order, `JobFacade.submit` can become the
stable entry. Validation must still happen before mutation, and failures must
remain visible to callers. This contrast leaves post-storage failure policy to
the owning subsystem instead of presenting an unverified recovery story.

```text illustrative
problem → multiple clients repeat one three-step submission flow
forces → preserve ordering, early validation, and visible failures
simplest option → one module function
chosen pattern → Facade only after repeated clients need one configured API
cost → another public surface and possible over-centralization
expected failure → invalid input mutates storage or records a false audit entry
verification → success, invalid-input no-mutation, and corrected-input recovery
when to remove it → one caller remains or the subsystem owns submit directly
```

## Checkpoint and navigation

You pass this card when you can explain why a module can be a Pythonic facade,
and why “many classes” is not enough evidence for a Facade class.

[Return to the Appendix C family catalogue](../README.md#family-index) ·
[Continue the Advanced route](../README.md#advanced-route-make-ownership-explicit)
