# Circuit Breaker — dependency-health state with a recovery probe

Canonical English lesson. Localized editions are not part of this implementation slice.

## At a glance

| Field | Contract |
|---|---|
| Family | Network resilience and behavioral state |
| Status | Executable |
| Route | Network resilience, after Retry |
| Prerequisites | [Retry](<../network - Retry/README.md>), exceptions, injected clocks, Chapter 23 failure boundaries |
| Time | 45–60 minutes |
| Runtime | Standard library; course target CPython 3.11+; authoring run on CPython 3.13.11 |
| Companion | [`example.py`](example.py), offline and import-safe |
| Explicit limits | Positive non-boolean integer threshold; finite positive cooldown; 3 negatives, 1 fake second, and 1 HALF_OPEN probe in the published run |

By the checkpoint, you should be able to assign one breaker to one dependency-
health domain, distinguish local failure from a health observation, and trace
every CLOSED, OPEN, and HALF_OPEN transition.

## Pressure before the pattern name

A failing dependency can consume the same timeout and Retry budget for every
caller. Once several complete logical operations report that the dependency
is unhealthy, calling it again immediately may only waste capacity. Yet a
permanent request rejection proves the dependency responded, and a local
validation error says nothing about dependency health.

A Circuit Breaker remembers the health of one dependency domain. CLOSED allows
calls. After the configured negative threshold, OPEN denies calls locally.
Once a fake cooldown has elapsed, HALF_OPEN gives exactly one caller permission
to probe. A positive probe closes; a negative probe opens with a fresh
cooldown.

The three states have different permissions and cleanup, so this is a justified
State contrast. A small `if`/`match` or transition table is still preferable to
a hierarchy while the transitions remain readable.

## The simplest option first

Use a direct call or a simple conditional when there is no shared health
domain, callers already fail cheaply, or only one short-lived operation is
involved. Do not create one breaker per request: it forgets the shared evidence
that gives the mechanism value.

### Use it when

- many logical operations depend on the same health domain;
- repeated unhealthy calls consume meaningful time or capacity;
- positive, negative, and neutral outcomes can be classified; and
- fake time can prove cooldown and probe behavior without waiting.

### Do not use it when

- local validation or admission is being confused with remote health;
- the dependency already provides a cheaper authoritative health gate;
- calls are independent and share no meaningful domain; or
- the team cannot own state transitions and probe exclusivity safely.

The cost is shared state, concurrency control in a real concurrent program,
transition tests, and careful observation semantics. Remove it when callers
already fail cheaply or the claimed health domain is not actually shared.

## Predict, run, observe

Predict before execution:

1. After two negative logical results with threshold three, is the circuit
   OPEN?
2. How many dependency calls does an OPEN denial make?
3. Does a failed HALF_OPEN probe reuse the old cooldown or start a new one?

Run `python -I -B "zz_Appendix C Software Design Patterns/network - Circuit Breaker/example.py"`
from the repository root. The dependency results and monotonic time are
injected; there is no socket, wall-clock sleep, task, or unbounded history.

Observe that negatives one and two leave CLOSED, negative three opens, the
next denial makes zero dependency calls, a failed eligible probe reopens, and
a later successful probe returns `healthy` and closes.

The final two observations exercise configuration recovery. Boolean or
non-positive thresholds fail with `failure_threshold_must_be_positive_int`;
cooldown, clock values, and clock advances must be finite numbers, and booleans
are not accepted as numbers. A rejected `NaN` advance leaves fake time and the
already healthy breaker unchanged.

## Normal, boundary, and recoverable paths

**Normal path:** a success is a positive observation and resets consecutive
negatives. A responsive permanent rejection is also positive for health even
though its application error still propagates.

**Boundary:** three final transient logical results open this example's
circuit. OPEN raises stable `circuit_open` before invoking the dependency.
Only one HALF_OPEN probe may be in flight. The synchronous companion exposes
the ownership flag but does not pretend to prove multi-task races.

Invalid configuration is another boundary, not dependency-health evidence.
`True` is an `int` subclass in Python, so validation rejects it explicitly;
`NaN`, infinity, zero/negative cooldown, a non-finite clock, or a clock moving
backwards also fail with stable configuration codes before they can justify a
state transition.

**Recoverable error:** after one injected second, a probe is eligible. A
transient probe result reopens and starts a fresh cooldown. A successful later
probe clears failures and returns CLOSED. A local exception while owning the
probe is neutral: it releases probe ownership and preserves the already
elapsed eligibility rather than inventing remote failure.

Configuration recovery means correct the invalid value and construct or call
again; it never means converting `NaN`/infinity or a boolean silently. Rejected
fake-clock movement is atomic, so the previous finite value remains usable.

In the full route, Retry attempts contribute one final logical observation,
not one observation per attempt. Caller cancellation before any dependency
result is neutral; a previously observed transient may contribute one negative,
but cancellation itself must not add another.

Common mistakes are using a breaker per call, counting each Retry attempt,
opening on validation/admission errors, allowing several recovery probes, and
using real sleeps in tests.

## Guided exercise

In a temporary copy of `example.py`, insert a successful logical result between
negative two and negative three. Predict the final state before running.

**Hint:** success calls `_positive()`. Inspect which fields it resets; do not
change the threshold.

**Observable success criterion:** after the inserted success, the next single
transient leaves the circuit CLOSED with one consecutive failure. Two more
transients are required before OPEN.

### Explained solution

The successful operation is evidence that the shared dependency responded
normally. Therefore old consecutive negatives no longer describe its current
health. Resetting both the counter and state makes the next transient the first
negative in a new sequence. Lowering the threshold would change the policy and
would not solve the exercise.

Decision record:

> repeated unhealthy logical calls waste budget → shared health evidence,
> cheap denial, exclusive recovery → direct conditional → Circuit Breaker with
> explicit State → shared state and transition tests → false opening or probe
> race → fake-clock state/call-count checks → remove when no shared domain or
> cheap caller failure already exists

## Checkpoint and navigation

You pass this local checkpoint when you can:

- classify positive, negative, and neutral logical outcomes;
- trace threshold opening, zero-call denial, exclusive probe, reopen, and close;
- reject boolean/non-integer thresholds and non-finite cooldown/clock values
  without changing existing healthy state;
- explain why local validation/admission does not damage dependency health; and
- defend one breaker per health domain rather than per request.

Previous: [Retry](<../network - Retry/README.md>). Continue into the required
Capacity route with [Bulkhead](<../network - Bulkhead/README.md>), but remember
that Bulkhead is not a prerequisite for completing the
[Resilience checkpoint](../README.md#resilience-checkpoint-rubric-and-stop).

Safe stop: use the passing bounded Retry/direct-call pipeline if the health
domain or transition ownership is not yet clear.
