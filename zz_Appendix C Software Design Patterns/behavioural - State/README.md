# State — a Circuit Breaker reading view

| Field | Value |
|---|---|
| Family | Behavioural view over network resilience |
| Status | Cross-link with a runnable client; no second State implementation |
| Route | Network resilience; executable route check belongs to Circuit Breaker |
| Prerequisites | Exceptions, injected time, Chapter 23 Intermediate checkpoint |
| Estimated time | 20–30 minutes here, then the owner lesson |
| Canonical owner | [Network · Circuit Breaker](<../network - Circuit Breaker/README.md>) |

## Start with the pressure

Calls that were allowed a moment ago may need to be denied after repeated
negative dependency-health observations. Later, one controlled probe must be
allowed while ordinary calls remain blocked. The same operation therefore
behaves differently according to remembered lifecycle state.

That is the State pressure worth recognizing. It does not justify a second
breaker, a parallel transition table, or one class per state in this appendix.
The only executable implementation and resilience route check belong to the
[canonical Circuit Breaker companion](<../network - Circuit Breaker/example.py>).

## The basic idea

State organizes behavior that changes with an object's current state. The owner
companion represents that state with the `CircuitState` enum:

- `CLOSED` permits calls and records final health observations;
- `OPEN` denies calls locally until the injected cooldown is eligible; and
- `HALF_OPEN` grants the one owned recovery probe.

The owner uses explicit conditionals because three readable states do not need
a class hierarchy. This page is only a client and reading lens: its `example.py`
loads that fixed sibling by a repository-owned path with `importlib`, constructs
the owner's objects, and observes their public state. It defines no
`CircuitBreaker`, thresholds, cooldowns, or transition policy of its own.

## Simpler option, fit, and cost

- **Simpler option:** a direct call, one conditional, or a small transition
  table when there is no shared lifecycle.
- **Use a State view when:** allowed behavior genuinely changes with remembered
  state and naming those states makes transitions auditable.
- **Do not use it when:** one Boolean guard explains the whole behavior or the
  variation is an independently selected Strategy.
- **Cost:** state ownership, legal-transition checks, recovery rules, and more
  paths to verify.

For the network mechanism itself, use the owner lesson's fuller decision: a
Circuit Breaker also costs shared dependency-health evidence, fake-clock tests,
and exclusive probe ownership.

## Predict, run, observe

Before running, predict which state is visible *inside* an eligible probe. Also
predict whether an `OPEN` denial consumes the dependency's scripted value.

Run this bounded client from the repository root:

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -I -B \
  'zz_Appendix C Software Design Patterns/behavioural - State/example.py'
```

```text illustrative
initial=CLOSED
threshold=OPEN failures=3
boundary=circuit_open dependency_calls=0
failed-probe-observed=HALF_OPEN after=OPEN
recovery-probe-observed=HALF_OPEN result=healthy after=CLOSED
```

The client reads `FAILURE_THRESHOLD` and `COOLDOWN_SECONDS` from the owner; it
does not repeat their values as local policy. The zero dependency-call count
proves the `OPEN` boundary. Each probe observes `HALF_OPEN` while it owns
permission. A negative probe returns to `OPEN`; a positive probe recovers to
`CLOSED`.

## Normal, boundary, and recoverable behavior

- **Normal:** the owner's breaker begins `CLOSED`, so a permitted operation may
  reach the dependency.
- **Boundary:** after the owner's configured negative threshold, it is `OPEN`;
  a premature call raises the owner's stable `CircuitOpen("circuit_open")`
  without invoking the dependency.
- **Recoverable:** after advancing the owner's fake clock by its cooldown, the
  operation observes `HALF_OPEN`. A failed probe reopens; a later successful
  probe returns `healthy` and closes.

The example is import-safe, offline, single-process, and finite. It is not
independent evidence for thresholds, concurrency, Retry composition, or
cancellation. Those contracts and their executable checkpoint remain in the
[Circuit Breaker owner lesson](<../network - Circuit Breaker/README.md>).

## Guided cross-link exercise

In a temporary copy of this client, replace the first recovery probe with a
function that records `breaker.state.name` and raises `PermanentFailure`.
Predict both the state and propagated result before running.

**Hint:** inspect the owner's `call()` exception classification and `_positive()`
transition. A permanent request rejection is an application failure but a
positive dependency-health observation.

**Success criterion:** the probe observes `HALF_OPEN`, `PermanentFailure` still
reaches the caller, and the owner ends `CLOSED`. You change only the client; do
not copy or modify the transition implementation.

## Explained solution and decision record

Catch the owner's `PermanentFailure` outside `breaker.call()` and print the
final state. The owner calls `_positive()` before re-raising, because the
dependency responded even though it rejected this request. State describes
dependency-health permission; it does not turn an application rejection into
success.

```text illustrative
behavior changes with remembered dependency health
→ CLOSED, OPEN, and HALF_OPEN make permissions auditable
→ direct conditional or transition table in the canonical owner
→ State is a reading view, not a duplicate implementation
→ cost: lifecycle and transition evidence
→ verify through the Network Circuit Breaker route check
→ remove this cross-link if it stops clarifying the owner's transitions
```

## Checkpoint and navigation

You pass this cross-link when you can trace `CLOSED → OPEN → HALF_OPEN → OPEN`
and `CLOSED → OPEN → HALF_OPEN → CLOSED`, name the observation that causes each
transition, and explain why this page must not own another breaker.

[Return to the Appendix C family catalogue](../README.md#family-index) ·
[Study and verify the canonical Circuit Breaker](<../network - Circuit Breaker/README.md>) ·
[Continue the Network resilience route](../README.md#network-resilience-route-safe-retries-before-state)
