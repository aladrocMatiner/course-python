# Strategy as a Callable

| Field | Value |
|---|---|
| Family | Behavioural |
| Status | Executable pattern |
| Route | Essential |
| Prerequisites | Functions as values, dictionaries, exceptions |
| Estimated time | 25–35 minutes |

## Start with the pressure

The job-running steps stay the same, but a second payload policy appears. The
caller must choose that behavior independently of execution. One growing
`if`/`elif` block could work; the pressure becomes interesting when policies
change, are tested, or are selected independently.

## The basic idea

Strategy separates a stable caller from a replaceable behavior. In Python a
callable is usually enough: `run(payload, strategy)` accepts a function, and a
small mapping translates a public name into that function. No abstract base
class is required for this contract.

## Simpler option, fit, and cost

- **Simpler option:** one direct function or a short `if`/`match` at the call
  site.
- **Use it when:** at least two policies share one input/output contract and
  callers choose them independently.
- **Do not use it when:** one fixed behavior exists.
- **Cost:** an indirect call, a policy contract, and selection errors to test.

## Predict, run, observe

Before running, predict whether `run()` knows the name `uppercase`, and which
function owns that translation.

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  'zz_Appendix C Software Design Patterns/behavioural - Strategy Callable/example.py'
```

```text illustrative
normal=processed:mixed
variation=processed:MIXED
name-boundary=strategy name must be non-empty text
boundary=unknown strategy: missing
callable-boundary=strategy must be callable
recovery=processed:safe
```

`run()` knows only the callable contract. `select_strategy()` owns names and
rejects an invalid name type or unknown choice before any payload is processed.
`run()` rejects a non-callable policy with its own stable error before trying to
invoke it.

## Normal, boundary, and recoverable behavior

- Normal: `keep` preserves a valid payload.
- Variation: `uppercase` changes policy without changing `run()`.
- Boundary: a non-text or empty name raises `InvalidStrategyName`; an unknown
  valid name raises `UnknownStrategy`; a non-callable policy raises
  `InvalidStrategy`; an empty or over-16-character payload raises
  `InvalidPayload` before policy execution.
- Recovery: correct the name or payload and call again; no state is retained.

A common mistake is calling the policy during injection:
`run(payload, uppercase(payload))`. Pass `uppercase`, not its result.

## Guided exercise

Add a `reverse` strategy and select it by name.

**Hint:** its contract is `reverse(payload) -> str`; add one function and one
registry entry. Do not edit `run()`.

**Success criterion:** `run("abc", select_strategy("reverse"))` returns
`processed:cba`, while invalid-name, unknown-name, non-callable, and invalid
payload behavior stay intact.

## Explained solution and decision record

The stable execution function should not change because the new variation is
policy, not mechanism. If only one policy survives later, pass it directly or
inline it and remove the registry.

```text illustrative
second independent payload policy → shared callable contract
→ direct conditional → callable Strategy
→ cost: selection and contract tests
→ verify normal, unknown, invalid, and recovery cases
→ remove when runtime policy selection disappears
```

## Checkpoint and navigation

Can you inject a fake callable, prove it was called once, and explain why the
selection mapping is outside `run()`? If yes, continue.

[Return to the Appendix C catalogue](../README.md#family-index) ·
[Continue the Essential route](../README.md#essential-route-earn-the-first-three-seams)
