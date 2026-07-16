# Retry — bounded repetition with explicit safety

Canonical English lesson. Localized editions are not part of this implementation slice.

## At a glance

| Field | Contract |
|---|---|
| Family | Network resilience |
| Status | Executable |
| Route | Network resilience, before Circuit Breaker |
| Prerequisites | Appendix Essential checkpoint; Chapter 19 retry introduction; Chapter 21 cancellation vocabulary; Chapter 23 Intermediate checkpoint |
| Time | 45–60 minutes |
| Runtime | Standard library; course target CPython 3.11+; authoring run on CPython 3.13.11 |
| Companion | [`example.py`](example.py), offline and import-safe |
| Explicit limits | Published run: 3 attempts, 100 ms per attempt, 500 ms total, 50/100 ms backoffs; hard teaching caps: 10 attempts and 60 finite seconds |

By the checkpoint, you should be able to decide whether an operation is safe
to repeat, keep every attempt and delay inside one budget, and explain why a
request key alone is not proof of deduplication.

## Pressure before the pattern name

A dependency sometimes reports a temporary failure. One more call might
recover, but it might also repeat a payment, message, or write whose first
outcome is unknown. Repetition also consumes time and load. A plain `while`
loop does not answer three design questions: **may this operation repeat, how
much total work is allowed, and who owns the final failure?**

Retry is a policy that repeats only an explicitly eligible transient operation
within finite attempt and time limits. The policy does not make an unsafe
operation safe. Safety must come from a side-effect-free operation, an
idempotent contract, or a stable key whose deduplication is actually enforced
by the receiving boundary.

## The simplest option first

Use one direct call when failure is cheap, the caller already controls another
attempt, or you cannot prove repetition safe. A small caller-owned second call
can be clearer than a reusable policy when there is only one local use case.
Add Retry only after transient recovery is observed and the safety evidence is
testable.

### Use it when

- the failure is classified as transient rather than permanent;
- repeating the exact logical operation is demonstrably safe;
- one total deadline can include attempts and backoff; and
- extra calls will not create a retry storm.

### Do not use it when

- a write may already have taken effect and no enforced deduplication exists;
- validation or authorization failed;
- the dependency says the request is permanently invalid; or
- the caller or platform already owns the retry policy.

The cost is more calls, more latency, cause preservation, cancellation work in
an asynchronous implementation, and tests for every stopping boundary. Remove
the policy when transient recovery is not observed or operations cannot remain
safe to repeat.

## Predict, run, observe

Before running, predict these three results:

1. A side-effect-free read fails transiently once and then succeeds. How many
   calls and backoffs occur?
2. A write has a stable key but no enforced deduplication. Does it make a
   second call?
3. The first transient leaves only 40 ms while the next complete backoff needs
   50 ms. Does a partial delay begin?

From the repository root, run
`python -I -B "zz_Appendix C Software Design Patterns/network - Retry/example.py"`.
The script uses injected outcomes and a fake monotonic clock. It performs no
network call, wall-clock sleep, file write, or background task.

Observe stable facts rather than memorizing formatting:

- the happy read returns `temperature=21` after two calls and one `0.05`
  backoff;
- the unsafe boundary reports `retry_not_safe` after exactly one call;
- the deadline case reports `retry_exhausted:deadline`, starts no partial
  backoff, and makes no second call; and
- a later independent one-call operation still succeeds.

The final configuration observations show that `True` is not accepted as one
attempt merely because Python makes `bool` an `int` subclass. Attempt count is
a positive integer capped at ten. Durations, total budget, fake-clock values,
and every backoff must be finite; an infinite scripted duration is rejected
with a stable code and the earlier recovered result remains valid.

The simulated dependency accepts the remaining per-attempt timeout. If its
scripted duration exceeds that value, it advances only to the timeout and
raises `TransientFailure("attempt_timeout")`. This demonstrates budgeting; it
does not claim to prove real task cancellation. Chapter 21 owns cancellation
behavior.

## Normal, boundary, and recoverable paths

**Normal path:** validation and safety evidence are already established. The
first transient is kept as the current cause, the complete 50 ms delay fits,
and the second call succeeds inside the same 500 ms budget.

**Boundary:** `RetrySafety(idempotency_key="job-7")` is still unsafe when
`deduplication_enforced` is false. The original call is allowed, but automatic
repetition is denied. Permanent failures also propagate without retry.

Configuration is bounded too: booleans are rejected for integer/number fields;
attempts are `1..10`; the backoff count must be exactly attempts minus one;
attempt, total, outcome, and backoff durations are finite and at most 60 fake
seconds. Retry-safety flags must be actual booleans, and an idempotency key is
non-empty bounded text. Invalid configuration makes no dependency call.

**Recoverable error:** when the next complete action cannot fit, the policy
raises `RetryExhausted` chained from the last transient. The caller stops this
logical operation, records a bounded diagnostic, and may start a later,
independent operation with a fresh policy. It must not secretly reset the
deadline for the same operation.

For `NaN`, infinity, a backwards clock, or a mismatched backoff schedule,
recovery is to correct the configuration and start again. The example never
coerces those values or broadens its bounds silently.

Common mistakes are retrying every exception, treating any key as enforced
deduplication, resetting the deadline per attempt, starting a partial backoff,
and discarding the final transient cause.

## Guided exercise

Work in a temporary copy of `example.py`. Add a fourth scenario representing a
write with the stable key `job-8` **and** enforced deduplication. Inject one
transient result followed by `stored-once`.

**Hint:** change the safety evidence, not the retry loop. Use one
`RetrySafety` object for the whole logical operation and keep the key stable.

**Observable success criterion:** the result is `stored-once`, dependency
calls equal two, and one 50 ms backoff is recorded. Then set
`deduplication_enforced=False`; the same script must stop after one call with
`retry_not_safe`.

### Explained solution

`permits_repeat()` accepts the scenario only when the key and enforcement fact
appear together. That is the seam to change because safety is an operation
property; weakening the loop would allow unrelated unsafe writes. The policy
then reuses the same deadline and finite outcome script, so the exercise adds
no hidden time or network dependency.

Decision record:

> retry-safe transient operation may recover → duplicate-effect risk and one
> total deadline → one direct call → bounded Retry → extra calls and policy
> state → unsafe repeat or exhausted budget → injected failure/clock assertions
> → remove when recovery is not observed or safety cannot be proved

## Checkpoint and navigation

You pass this local checkpoint when you can:

- classify side-effect-free, idempotent, enforced-key, unsafe, and permanent
  cases;
- explain why the first unsafe call may occur but its second call may not;
- prove attempt, backoff, and total-budget limits using fake time; and
- reject boolean, non-finite, over-cap, and mismatched schedule inputs before
  unbounded work or a dependency call; and
- preserve the final transient as the cause of exhaustion.

This page's check is not the complete route checkpoint. Continue to
[Circuit Breaker](<../network - Circuit Breaker/README.md>) and then return to
the [Appendix C Resilience checkpoint](../README.md#resilience-checkpoint-rubric-and-stop).
The conceptual starting point remains
[Chapter 19's simple retries](../../chapter-19-http/README.md#3-simple-retries).

Safe stop: keep one validated direct call and its failure handling if you
cannot yet defend automatic repetition.
