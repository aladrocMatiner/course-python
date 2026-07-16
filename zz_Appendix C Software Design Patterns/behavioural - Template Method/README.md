# Template Method

| Field | Value |
|---|---|
| Family | Behavioural |
| Status | Decision card with verified contrast |
| Route | Professional |
| Prerequisites | Function composition, inheritance, method overriding |
| Estimated time | 20–30 minutes |

## Start with the pressure

Several variants must preserve the same ordered algorithm while changing one
or two steps. The order is an invariant, and existing meaningful subclasses
already own the variation. Without that inheritance pressure, composing
functions is normally the smaller Python design.

## The basic idea

Template Method defines the fixed algorithm in a base-class method and calls
overridable step methods. The companion contrasts that hierarchy with
`process(payload, transform)`, where a callable supplies the varying step.

This decision card teaches recognition. It does not require a hierarchy in the
job runner.

## Simpler option, fit, and cost

- **Simpler option:** function composition or an injected Strategy callable.
- **Use it when:** a real subclass family shares a strict algorithm order and
  subclasses already represent meaningful types.
- **Do not use it when:** callers merely select independent policies.
- **Cost:** base/subclass coupling, fragile override rules, and more difficult
  combinations of variation.

## Predict, run, observe

Predict why both designs produce the same output and which one can accept a new
callable without defining a type.

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  'zz_Appendix C Software Design Patterns/behavioural - Template Method/example.py'
```

```text illustrative
function-composition=stored:MIXED
template-method=stored:MIXED
boundary=payload must not be blank
recovery=stored:safe
```

Function composition accepts another callable directly. Template Method
requires another override when the subclass owns the variation.

## Normal, boundary, and recoverable behavior

- Normal: validation, transformation, and storage-labeling keep a fixed order.
- Boundary: blank input fails before the overridable transformation step.
- Recovery: correct the payload and rerun through the smaller composed
  function.

A common mistake is allowing subclasses to override the whole template method.
That removes the invariant that was meant to justify the pattern.

## Guided exercise

Add whitespace trimming as another variation. Decide between a callable and a
subclass before coding.

**Hint:** if trimming is selected independently, pass `str.strip` to
`process()`. A subclass needs stronger domain meaning than one formatting flag.

**Success criterion:** the fixed validation-before-transform order remains
observable, and your decision states who owns the variation.

## Explained solution and decision record

Use function composition for this exercise because the policy is independent
and combinable. Keep Template Method only where meaningful subtypes own steps
and the base algorithm must enforce their order.

```text illustrative
fixed algorithm with subtype-owned steps → order is an invariant
→ composed callables first → Template Method for a genuine subclass family
→ cost: hierarchy coupling → verify order and rejected invalid input
→ remove when policies vary independently
```

## Checkpoint and navigation

Can you identify the non-overridable invariant and explain why the subtype,
rather than configuration, owns each hook? If not, use composition.

[Return to the Appendix C catalogue](../README.md#family-index) ·
[Review the Professional decision cards](../README.md#professional-decision-cards)
