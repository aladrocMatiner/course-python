# Command

| Field | Value |
|---|---|
| Family | Behavioural |
| Status | Decision card with verified contrast |
| Route | Professional |
| Prerequisites | Functions, closures, classes, exceptions |
| Estimated time | 20–30 minutes |

## Start with the pressure

Work must be stored now and executed later. The stored request may eventually
need an identity, audit metadata, undo data, or serialization. The first
pressure—delayed execution—does not by itself require a class: a closure can
store a function and its arguments.

## The basic idea

A Command turns a request into a value with an execution operation. Python
functions and closures are already executable values. A command object becomes
useful only when the request needs meaningful state or behavior beyond “call
this function with these arguments.”

The companion compares both shapes. It is a card, not a requirement to replace
ordinary callbacks with classes.

## Simpler option, fit, and cost

- **Simpler option:** a function plus arguments, closure, or `functools.partial`.
- **Use it when:** stored work needs stable identity, metadata, validation,
  undo, or a domain-specific lifecycle.
- **Do not use it when:** a callback is executed immediately or the class only
  wraps one call.
- **Cost:** more objects, naming, validation, queue ownership, and failure
  policy.

## Predict, run, observe

Predict which approach supplies `command_id` and whether that identity changes
the rename result.

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  'zz_Appendix C Software Design Patterns/behavioural - Command/example.py'
```

```text illustrative
function-command=draft->ready
object-command=cmd-1:draft->ready
boundary=new name must not be blank
recovery=draft->safe
```

Both execute the same domain operation. Only the object carries an identity;
that extra requirement must justify its extra structure.

## Normal, boundary, and recoverable behavior

- Normal: the closure stores valid arguments and runs later.
- Boundary: a blank target name fails when the stored request executes.
- Recovery: replace or correct the invalid request, then execute the valid one.

For a real queue, decide whether validation happens before enqueue or during
execution. The teaching example makes the latter visible; production systems
often validate immutable command data at construction.

## Guided exercise

Decide whether a scheduled `send_reminder(address)` needs a closure or a
`ReminderCommand`.

**Hint:** begin with a closure. Add a class only if a tested requirement needs
identity, metadata, retries, or another operation on the stored request.

**Success criterion:** your decision names the required data, failure moment,
queue owner, and removal threshold.

## Explained solution and decision record

With only delayed execution, keep the closure. If the scheduler must cancel by
stable ID and inspect due time without executing, those observed operations can
earn a command object.

```text illustrative
stored executable request → delayed call, perhaps identity/metadata
→ closure first → Command object only for behavior-rich request values
→ cost: object and lifecycle policy → verify invalid and recovery paths
→ remove the class when it becomes a one-method wrapper
```

## Checkpoint and navigation

Can you explain what the object form provides that a closure cannot express as
clearly? “It is the Command pattern” is not sufficient evidence.

[Return to the Appendix C catalogue](../README.md#family-index) ·
[Review the Professional decision cards](../README.md#professional-decision-cards)
