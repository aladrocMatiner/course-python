## Context

The implemented course has 30 chapter directories and two published appendices.
`appendix-software-design-patterns` is the requested stable Appendix C path, but
it currently contains only `.gitkeep`; generic discovery can therefore see an
incomplete thirty-third unit before its five required pages exist.

Pattern-related material is already distributed across the course. Chapter 11
owns functions, Chapter 12 composition, Chapter 14 recoverable exceptions,
Chapter 15 module boundaries, Chapter 18 testing, Chapter 19 an introductory
retry example, Chapter 21 structured asynchronous work, Chapter 23 network
mechanics, Chapter 26 iterators/generators, and Chapters 17/28 persistence and
repository/service-layer depth. Appendix C must connect those ideas without
becoming an encyclopaedia or a second networking or order-management course.

The audience includes motivated beginners and young readers. Required work is
standard-library-only, offline, bounded, recoverable, and testable on CPython
3.11+. Canonical English plus Spanish, Catalan, Swedish, and Arabic siblings
must preserve semantic learning parity. Human linguistic, pedagogical,
accessibility, bidi, provenance, and publication decisions remain distinct from
automation.

Four active changes overlap root navigation, quality profiles, the 32/128
parity topology, and publication sign-off. Appendix-local drafting can proceed,
but shared edits and spec sync require a fresh baseline and explicit ownership
coordination. The implemented tree already contains Learning/Environment
profiles and a 32/128/root store that base specs do not yet fully describe.
Appendix C's cumulative delta protects those contracts provisionally; it must
not become their permanent owner when changes are synced.

## Goals / Non-Goals

**Goals:**

- Teach a repeatable problem-first selection method and a compact executable
  set of Python patterns through one synthetic job runner.
- Offer a progression-first route plus family/problem indexes so cataloguing
  never controls cognitive order.
- Give networking additional depth through corrected Retry, Circuit Breaker,
  Bulkhead, and optional Pub/Sub policies while Chapter 21/23 retain lifecycle
  and transport ownership.
- Provide deterministic companions and separately selected
  `patterns:core-suite` and `patterns:network-suite` evidence.
- Publish five equivalent lessons, accessible navigation, source/provenance
  records, and an explicit additive 32/128→33/132 evidence migration.

**Non-Goals:**

- An exhaustive pattern catalogue, framework survey, production architecture,
  performance benchmark, or claim that patterns beat direct Python by default.
- A new selector loop, `asyncio` server, listener, framing codec, wire schema,
  socket Adapter, restart Supervisor, broker, database, or second capstone.
- Public targets, real credentials, unbounded resources, fixed sleeps as
  correctness evidence, third-party dependencies, or automated human approval.
- Renaming existing paths, changing Chapter 23's plugin/contract, or silently
  rebasing another active change's exact-count delta.

## Decisions

### 1. Use one job runner and one decision record

The project begins with a direct `run(job)` function, a small explicit
`Job`/`Result` model, and deterministic tests. The model does not require
`dataclass` knowledge. Each refactor responds to a visible second variation or
ownership pressure while keeping domain vocabulary and behavior stable.

Every required exercise produces this decision record:

```text
problem → forces → simplest Python option → chosen pattern → cost
        → expected failure → verification → when to remove it
```

A justified function, module, mapping, closure, context manager, or direct
composition is a successful result. Alternatives considered were unrelated
examples per pattern, which hide integration cost, and a telemetry or orders
domain, which would duplicate Chapters 23 or 28.

### 2. Make progression primary and taxonomy secondary

The public lesson order and incremental budget are:

| Route | Content | Sessions | Observable exit |
| --- | --- | ---: | --- |
| Essential | literacy, Strategy, function Factory, Adapter | 2 × 60–75 min | policy, construction, and one incompatible boundary are separated with green tests |
| Professional | Decorator, bounded Observer, decision cards | 2 × 60–75 min | cross-cutting behavior and removable notifications preserve their contracts |
| Advanced | dependency injection, composition root, one execution port and in-memory Adapter | 1–2 × 60–75 min | time/IDs/output/execution are owned without globals or frameworks |
| Network resilience | Retry, deduplication, Circuit Breaker/State | 3 × 60–75 min | safe attempts and dependency-health transitions are proved with injected time |
| Network capacity | two Bulkheads; optional queued Pub/Sub | 1–2 × 60–75 min | required: remote saturation cannot consume local capacity and admission recovers |
| Network crosswalk | Reactor-like and `TaskGroup` ownership reading | 1 × 60–75 min | existing readiness and structured-concurrency responsibilities are traced |

The route graph is:

```text
              ┌→ Professional → Advanced ───────────┐
Essential ────┤                                     ├→ Network crosswalk
              └→ Network resilience → Capacity ─────┘
```

In prose: Essential is the common entry; the core and network branches can be
completed independently through Advanced or Capacity; Crosswalk requires both
branch exits. The complete graph is 10–12 sessions, approximately 10–15 hours.
For a learner who already completed Advanced, the Resilience→Capacity→Crosswalk
sequence adds 5–6 sessions; from Essential, reaching Crosswalk also requires
the 3–4 Professional/Advanced sessions. Each session is
split into 25–35 minute microcycles with prediction, execution or bounded
reading, observation, modification, verification, and explanation.

The main index follows this order. A family index maps creational, structural,
behavioral, architectural, and network patterns. A problem index maps symptoms
such as construction choice, incompatible interface, cross-cutting concern,
notification ownership, unstable dependency, saturation, and slow consumer.
Each index row contains pattern/technique, symptom or problem, family, route,
status (`executable`, `decision-card`, or `cross-link`), simpler alternative,
and checkpoint. This prevents a card or link from looking executable.

Essential requires the Chapter 11 foundational checkpoint, Chapter 12
essential checkpoint plus section 4 composition, and the Chapter 14, 15, and
18 checkpoints. Professional requires Essential; Advanced requires
Professional. Network resilience requires Essential plus Chapters 19 and 21
and Chapter 23 intermediate. Capacity additionally requires the resilience
checkpoint and Chapter 23 sections 7–8 with its concurrency/cleanup outcome.
The final crosswalk requires Capacity and Advanced. There is no informal
network mini-bridge and Appendix C is never required by an existing route.

### 3. Keep only patterns that create an observed seam executable

The executable core is:

- Strategy as an interchangeable callable, separated from selection.
- Factory as a validating function at the composition boundary.
- Adapter as explicit data, method, and error translation.
- Decorator through composition, contrasted with Python's `@decorator` syntax.
- A bounded synchronous Observer with stable iteration and idempotent removal.
- Explicit dependency injection, one execution port, and an in-memory Adapter.

The exact non-executable inventory is intentionally smaller:

- Essential contrasts function Factory with Factory Method.
- Professional contains decision cards for Command, Singleton, Proxy, and
  Template Method.
- Advanced contains one Facade decision card.
- Iterator/Generator and Repository/service layer are cross-links only.
- Builder and Composite are omitted from this delivery.

State is executable only where Circuit Breaker creates genuine transition
pressure and is contrasted there with direct conditionals or a transition
table. Cards use the same decision record and do not create companion
implementations.

Python-specific contrasts include function Factory versus Factory Method,
Decorator pattern versus decorator syntax, Adapter versus Proxy/Facade/
Decorator, and State versus a clear `if`, `match`, or transition table. One
small transfer exercise uses a second domain of roughly twenty lines so a
learner must select direct code or a pattern rather than repeat the job runner.

### 4. Treat Chapters 21 and 23 as lifecycle and transport authorities

Appendix C links Chapter 19's broad retry loop as an introductory baseline and
Chapter 23's warning against automatic write retries as the stronger starting
boundary. It links, rather than restates, Chapter 23 framing, peer, buffer,
history, timeout, and cleanup limits and their `network:network-suite` evidence.

The final reading maps
`chapter-23-network-programming/examples/telemetry/selector_hub.py` registration,
READ/WRITE interest, readiness selection, dispatch, idle expiry, and idempotent
close to Reactor-like responsibilities. It distinguishes the readiness
demultiplexer from the whole responsibility map and does not claim every
`asyncio` backend or Chapter 23 nominally implements Reactor.

A Chapter 21 `TaskGroup` reading maps owner, sibling cancellation,
`ExceptionGroup`, timeout, and cleanup. “Supervisor-like ownership” is only a
comparison: a real Supervisor would add explicit restart, isolation, or
escalation policy, which is outside this change.

### 5. Complete resilience before adding capacity

The independently completable resilience order is:

```text
validation → breaker permission → retry loop → per-attempt timeout → dependency
```

One Circuit Breaker belongs to one dependency-health domain. An open circuit
fails with stable `circuit_open` without invoking the dependency. Capacity is
introduced only in the next checkpoint, so Resilience does not depend on an
unseen Bulkhead abstraction.

Retry is eligible only for `TransientDependencyError` and a retry-safe
operation. An operation is retry-safe when it is side-effect free or idempotent
by contract, or when the fake dependency demonstrably enforces deduplication
for one stable key during the complete lab. Merely carrying a key is not enough.
After validation and breaker permission, an unsafe operation makes exactly its
one requested dependency call; a later Capacity rejection can prevent that
call. Across every composition it makes at most one dependency call. A
permanent failure also stops after its first call.

One logical operation has a 500 ms monotonic total deadline, at most three
attempts, a per-attempt bound of the lesser of 100 ms and remaining budget, and
injected 50/100 ms backoff. Attempts and backoff consume the same budget. A
scheduled backoff begins only when its full duration fits the remaining budget;
otherwise the operation exhausts without starting the delay or another call. A
timed-out owned attempt is cancelled and awaited before becoming
`TransientDependencyError(code="attempt_timeout")`; caller cancellation
propagates unchanged. Exhaustion chains the final transient cause.

Breaker observations are consistent in CLOSED and HALF_OPEN:

- negative: a final raw `TransientDependencyError` when retry is unavailable or
  bypassed, or `RetryExhausted(cause=TransientDependencyError)` after retries;
- positive: dependency success or responsive `PermanentDependencyError`;
- neutral/local: validation or caller cancellation before a dependency-health
  result.

Three negative observations with no positive observation between them open the
circuit; neutral observations are ignored and positive resets the count. After an injected one-second cooldown,
exactly one caller may perform one 100 ms HALF_OPEN attempt without retry.
Positive closes and resets while preserving the operation result; transient or
timeout reopens with a fresh cooldown. Cancellation releases the probe lease,
propagates, and leaves OPEN without manufacturing a new cooldown, so the
already elapsed eligibility remains available to a later caller.

### 6. Demonstrate isolation with the smallest useful capacity model

Capacity extends the already passing resilience pipeline at one explicit seam:

```text
validation → breaker permission → retry loop
           → Bulkhead lease per attempt → per-attempt timeout → dependency
```

Admission consumes the same 500 ms logical-operation deadline. Admission
failure is local and is not retried. Before any dependency result in the logical operation it
returns stable `admission_timeout` or `overloaded`, makes zero dependency calls,
and is neutral to breaker health. After a prior transient attempt it stops Retry
as `RetryExhausted` chained from that transient; admission adds no second health
observation. An open circuit fails before capacity. A lease covers one attempt
and is released before backoff. If a HALF_OPEN probe is cancelled or cannot
obtain capacity before observing dependency health, its probe lease is released
and the breaker stays OPEN with its already elapsed eligibility.

The single-loop lab owns exactly two Bulkheads, `local` and `remote`. Each has
one execution lease and one waiting admission slot, with no persistent worker
task and no second waiter queue. A third proposal to the same full compartment
fails immediately with `overloaded` without allocating a waiter or lease. The
one waiter expires after the lesser of an injected 50 ms admission deadline and
the caller's remaining total deadline; timeout/cancellation removes it once.
Tests saturate `remote` while a `local` operation completes.

Optional Pub/Sub is process-local, in-memory, non-durable, and free of
background consumer tasks, replay, or history. It owns at most four subscribers
and eight queued events per subscriber. `publish()` reports opaque `enqueued`
and `disconnected` IDs, never delivered or processed. A full subscriber is
removed with `slow_subscriber`; its pending count, not contents, is reported;
healthy subscribers still enqueue the event in per-subscriber FIFO order.
Processing occurs outside the publisher boundary, so no acknowledgement,
global ordering, or consumer-success claim is made.

Bulkhead isolation and admission recovery are the required Capacity checkpoint.
If the learner completes the separately skippable Pub/Sub extension, its
additional exit criterion is distinguishing enqueue from delivery. Companion
tests still verify that published optional asset without making it a prerequisite
for Crosswalk.

The lesson includes a “do not confuse” table for timeout, Retry, Circuit
Breaker, Bulkhead, rate limiting, load shedding, backpressure, and Pub/Sub, with
a narrow-screen list equivalent. It identifies application admission separately
from Chapter 23 transport flow control with `writer.drain()`.

### 7. Keep companions and verification modular

The implementation target is:

```text
appendix-software-design-patterns/
├── README.md, README.es.md, README.ca.md, README.sv.md, README.ar.md
├── SOURCES.md, TRACEABILITY.md, VERIFICATION.md
├── examples/patterns/
│   ├── __init__.py, domain.py, direct.py
│   ├── essential.py, professional.py, architecture.py
│   └── resilience.py, capacity.py, pubsub.py
├── examples/tests/test_core_patterns.py
├── examples/tests/test_network_patterns.py
└── tools/bookcheck_plugin.py
```

Modules provide route-level recovery points without copying a monolithic final
object. Tests characterize direct behavior first, then preserve it through each
refactor. Runnable blocks derive from companion sources; expected failures live
in tests or guarded functions and imports perform no work.

The minimal plugin registers exactly `patterns:core-suite` and
`patterns:network-suite` and invokes only the known standard-library tests. It
does not implement its own process tree, output collector, repository snapshot,
or aggregate clock. The generic plugin runner owns isolated execution,
temporary working state, timeout/output limits, descendant cleanup, schema,
selection, and mutation detection. The quality runner owns the outer
`patterns-domain` profile bound.

### 8. Pilot canonical pedagogy before localization

Canonical English and companions are completed together. A cold-read pilot by
one or more people who did not design the appendix and who match a declared
target entry profile records role-only evidence (no name or personal data),
prerequisites, environment, route coverage, actual time, vocabulary blocks,
recovery steps, and places where help was needed. A checkpoint passes the pilot
only when it finishes within its upper estimate using published hints/recovery
without unplanned external instruction. Exceeding that bound or needing such
help creates a critical scope/pedagogy finding and requires correction plus an
affected-checkpoint retest before translation. The pilot collectively covers
all six checkpoints.

Spanish, Catalan, Swedish, and Arabic then preserve objectives, routes,
contracts, examples, exercises, solutions, rubrics, reflection, safety, and
stopping points. Standard English pattern names remain searchable on first use.
Tables receive list alternatives; visuals receive text equivalents; decisions
do not rely on color, position, icons, or arrow direction. Arabic has exactly
one outer RTL wrapper and keeps code, paths, identifiers, state names, and
output legible left-to-right.

### 9. Publish shared surfaces only after ownership and evidence gates

The five pages and appendix-local companions/checks exist before root
navigation. The curriculum graph adds Essential, two branches through
Professional/Advanced and Resilience/Capacity, and a Crosswalk join while
preserving every existing route.
Root indexes publish Appendix C after A/B in one atomic wave and keep
`README.md`/`README.en.md` byte-identical.

Before quality, parity, root, attribution, or sign-off edits, implementation
re-reads live owners and digests. Maintainers first reconcile the active
multilingual review-schema/root contracts, preserve the core and environment
expansions that produce the valid 32/128 baseline, and apply Appendix C's
33/132 delta last. One new source and four locale leaves begin pending; no
review identity, date, note, or acceptance is synthesized. That topology step
keeps the root leaf byte-identical while root Markdown is unchanged and makes
the external sign-off stale; root decisions are reconciled only after the six
indexes publish their new digests.

## Risks / Trade-offs

- **[Too many names encourage cargo cults]** → Keep seven core executable seams,
  teach State only through a real breaker, use decision cards for recognition,
  and accept justified direct Python.
- **[The appendix grows back into a course]** → Hold the 10–15 hour graph budget,
  one project, six checkpoints, and no loopback/Supervisor implementation.
- **[Retry duplicates effects]** → Require side-effect freedom, contract
  idempotency, or tested dependency-side deduplication; a key alone is rejected.
- **[Capacity is mislabeled as resilience or backpressure]** → Prove two named
  failure domains and explicitly separate admission, flow control, and delivery.
- **[Async tests leak or flake]** → Inject clocks/failures, use bounded awaits,
  propagate cancellation, and assert no owned waiter, lease, or task remains.
- **[Chapter 23 is duplicated or relabeled]** → Keep Reactor/TaskGroup as guided
  reading and leave every transport executable claim with its owning check.
- **[Translations multiply a flawed lesson]** → Complete the canonical cold-read
  pilot before localization and keep competent human review pending.
- **[Active changes overwrite shared evidence]** → Hard-gate shared mutations on
  current ownership, counts, digests, and cumulative delta comparison.

## Migration Plan

1. Validate this reduced plan and capture the live active-change/quality/parity
   baseline without treating the `.gitkeep` scaffold as passing evidence.
2. Replace the scaffold with the direct/core companion, route tests, source,
   traceability, and verification skeletons.
3. Add Retry/Circuit Breaker, simplified Bulkheads, optional Pub/Sub, and the
   Chapter 21/23 reading trace; no transport fixture is created.
4. Write and companion-verify canonical English, run the cold-read pilot, and
   correct critical findings before localization.
5. Add the four semantic translations; preserve the completed cold-read state
   while new linguistic, accessibility, provenance, and publication decisions
   remain pending.
6. Reconfirm shared ownership, then register the minimal plugin/profile,
   five-page source-reference contracts, and final Appendix C attribution input
   without altering generic domain behavior.
7. From an approved valid 32/128 baseline, add the pending 33/132 parity leaves
   while preserving the unchanged root leaf and invalidating external sign-off.
8. Publish curriculum nodes and all six root links atomically, then reconcile
   the changed root leaf and current sign-off inputs as pending.
9. Run focused and repository-wide machine evidence and prepare a truthful
   human-review handoff.

Rollback removes only unaccepted Appendix C navigation, pattern profile/check
registration, and its five new parity leaves; restores reviewed prior topology
and sign-off inputs; and reruns prior profiles. It never edits Chapter 23 or
deletes unrelated review evidence.

## Open Questions

- **Resolved:** The stable title/path is “Appendix C · Software Design Patterns
  in Python” at `appendix-software-design-patterns`.
- **Resolved:** The final network checkpoint is evidence-backed reading, not a
  socket Adapter, selector implementation, or Supervisor implementation.
- **Implementation gate:** Confirm current shared ownership and exact topology
  immediately before any shared mutation; changed truth requires another plan
  update.
- **Human gate:** Reviewer identities, dates, notes, and outcomes remain unset
  until real canonical, localized, technical/pedagogical, accessibility/bidi,
  provenance, and publication reviews occur.
