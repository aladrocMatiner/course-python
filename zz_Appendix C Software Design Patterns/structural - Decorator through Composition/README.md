# Structural · Decorator through Composition

## Pattern card

| Field | Value |
|---|---|
| Family | Structural |
| Status | Executable |
| Route | Professional |
| Prerequisites | Composition, exceptions, injected callables, Essential checkpoint |
| Time | 35–45 minutes |

You will add deterministic measurement around one executor without changing
its return value or failure type.

## Start with the pressure

Several executors need the same before/after behavior. Copying a timer into
each executor risks recording success but losing failure, or changing what the
caller receives. Inheriting from every concrete executor couples the concern
to class hierarchies it does not own.

The pressure is consistent cross-cutting behavior around one stable contract.
Only then does **Decorator through composition** earn its name.

## The pattern in plain language

The wrapper exposes the same `execute(payload)` operation as the wrapped
object. It performs work before and after delegation, then returns the same
result or re-raises the same exception. Composition means the wrapper stores a
collaborator instead of inheriting from it.

For one call site, a local `try`/`except`/`finally` block or a helper function is
simpler. A function decorator is also valid when the boundary is a function,
but it is not needed to learn this object contract.

### Use it, avoid it, count its cost

- Use it when multiple implementations share the same wrapper behavior and
  callers must continue seeing one contract.
- Do not use it to hide business decisions or to stack wrappers whose order no
  one can explain.
- Its cost is another level in the call stack, ordering rules, and success plus
  failure tests for every cross-cutting concern.
- Remove it when one local call owns the concern or the measurement is no
  longer required.

## Predict, run, observe

Predict whether the wrapper should convert the planned `RuntimeError`. Also
predict the two fake elapsed times before execution.

Run the verified companion from the repository root:

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B "zz_Appendix C Software Design Patterns/structural - Decorator through Composition/example.py"
```

Expected output:

```text illustrative
completed:pack-books
measurement:('completed', 0.25)
boundary:payload must be non-empty text
measurement:('error', 0.0)
preserved-original:True
recovered:completed:pack-books
```

In the [composition-based Decorator source](example.py), the fake clock makes
the normal evidence deterministic. Observation is deliberately best-effort:
clock or measurement-sink failure is contained, while bare `raise` preserves
the exact wrapped exception. The last two lines prove that a broken sink cannot
replace that error and an exhausted clock cannot block a later healthy call.

## Normal, boundary, and recoverable behavior

- **Normal:** the wrapper records `completed` and returns the exact wrapped
  result.
- **Boundary:** an empty payload still raises the wrapped executor's
  `ValueError`; the wrapper records it as an error instead of inventing output.
- **Recoverable:** even when the observation sink raises and the fake clock is
  later exhausted, the original execution error survives and a later healthy
  operation returns normally.

A common mistake is using `finally` to record every call as success. Another is
catching and replacing the wrapped exception even though this concern owns no
recovery policy. Keep observation separate from business behavior. Because
this implementation drops unavailable measurements, it is unsuitable for
mandatory audit or security evidence; those need an explicit fail-closed
contract rather than a transparent best-effort Decorator.

## Guided exercise

Make the wrapped executor raise one stored exception while the measurement sink
also raises. Then let the wrapped executor succeed while the fake clock is
exhausted.

**Hint:** compare the caught error with the stored object using `is`. Keep
observation inside `_record`; do not add a broad catch around delegation.

**Success criterion:** the same failure object is re-raised, neither sink nor
clock failure escapes, a later healthy result is unchanged, and ordinary
observation still records its deterministic measurement.

## Explained solution and decision record

The wrapper should catch `Exception` only to observe and immediately re-raise.
It should not catch `BaseException`, choose retries, or turn failure into a
successful value. `_read_clock` and `_record` separately contain best-effort
observation failures so they cannot replace either the wrapped result or error.
Those responsibilities belong elsewhere. An injected clock makes elapsed time
controllable without sleeping.

```text illustrative
problem → measurement must surround several executors consistently
forces → preserve return and failure contracts; avoid inheritance coupling
simplest option → one local try/finally block
chosen pattern → composition Decorator after the concern repeats
cost → wrapper order and two-path verification
expected failure → a wrapped error is swallowed or replaced by sink failure
verification → deterministic success, same-error identity, broken observation,
               and later healthy-call checks
when to remove it → only one call site still needs measurement
```

## Checkpoint and navigation

Continue when you can draw caller → wrapper → wrapped object, explain both
return paths, and state why injected time is safer than sleeping in a test.

[Return to the Appendix C family catalogue](../README.md#family-index) ·
[Continue the Professional route](../README.md#professional-route-cross-cutting-behavior-and-notifications)
