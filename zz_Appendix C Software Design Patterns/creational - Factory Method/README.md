# Factory Method

| Field | Value |
|---|---|
| Family | Creational |
| Status | Decision card with verified contrast |
| Route | Essential contrast |
| Prerequisites | Function Factory, inheritance, method overriding |
| Estimated time | 20–30 minutes |

## Start with the pressure

A base workflow is stable, but each subclass must decide which collaborator to
create. Configuration does not own the choice; the subclass does. That specific
pressure may justify Factory Method. If a string from configuration selects the
collaborator, a function Factory is usually clearer.

## The basic idea

Factory Method places a creation hook on a base class and lets subclasses
override that hook. The companion keeps the contrast deliberately small:
`choose_formatter()` constructs a fresh `Formatter` from configuration, while
`LoudReport` overrides `create_formatter()` and constructs the product through
subclass policy.

This is a recognition card, not a required implementation for the job runner.
Its purpose is to prevent a function-selection problem from growing into an
unnecessary inheritance tree.

## Simpler option, fit, and cost

- **Simpler option:** a function Factory, mapping, or injected callable.
- **Use it when:** a useful existing subclass hierarchy genuinely owns creation.
- **Do not use it when:** configuration or a composition root owns selection.
- **Cost:** subclass coupling, more navigation, and a creation hook that tests
  must cover for every subclass.

## Predict, run, observe

Predict whether both routes print the same result, and identify which route
requires inheritance. Run:

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  'zz_Appendix C Software Design Patterns/creational - Factory Method/example.py'
```

```text illustrative
fresh-products=True
function-factory=READY
factory-method=READY
name-boundary=style must be non-empty text
boundary=unknown style: missing
recovery=ready
```

The identity line confirms that the function Factory constructs products rather
than returning one shared object. Equal formatted output does not make the
designs equal. Ownership decides: configuration selects through the function;
a subclass selects through Factory Method.

## Normal, boundary, and recoverable behavior

- Normal: `loud` is selected by configuration and `LoudReport` selects it by
  subclass policy; both routes construct a `Formatter`.
- Boundary: a non-text or empty style raises `InvalidStyle`; unknown valid text
  raises `UnknownStyle` before rendering.
- Recovery: select `plain`; no subclass is required for a configuration typo.

A common mistake is creating one subclass per configuration value. That moves
data into the type hierarchy and makes combinations difficult.

## Guided exercise

Write a two-line decision for a new `quiet` formatter: should it be another
mapping entry or another `Report` subclass?

**Hint:** ask who owns the variation. A user setting points to the mapping. A
meaningful report subtype that owns several behaviors may point to a subclass.

**Success criterion:** your answer states the owner, the simpler option, and one
future observation that would justify changing the choice.

## Explained solution and decision record

For a user-selected formatting string, add `quiet` to the function Factory. A
subclass adds no useful domain meaning. Revisit Factory Method only if real
report subtypes already own creation and the base algorithm must stay fixed.

```text illustrative
subclass-owned creation → stable base workflow and meaningful subtypes
→ function Factory first → Factory Method only if the subtype owns choice
→ cost: hierarchy coupling → verify each creation hook
→ remove when configuration or composition owns selection instead
```

## Checkpoint and navigation

Can you distinguish configuration-owned selection from subclass-owned
construction, and prove that both hooks create products instead of sharing one?
If yes, the card is complete; you do not need to add Factory Method to your
project.

[Return to the Appendix C catalogue](../README.md#family-index) ·
[Return to the Essential route](../README.md#essential-route-earn-the-first-three-seams)
