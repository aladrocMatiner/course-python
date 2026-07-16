## ADDED Requirements

### Requirement: Appendix C teaches decisions before pattern names
`appendix-software-design-patterns/README.md` and its Spanish, Catalan,
Swedish, and Arabic siblings SHALL begin from working direct code and teach this
repeatable decision record: problem, forces and ownership, simplest Python
option, named pattern if justified, cost, expected failure, verification, and
when to remove the abstraction. Every required pattern SHALL include a simpler
Python alternative and a case where no pattern is the better decision.

The appendix SHALL provide a progression-first index plus secondary indexes by
creational, structural, behavioral, architectural, and network family and by
observable symptom. Each index row SHALL identify pattern or technique,
symptom/problem, family, route, status (`executable`, `decision-card`, or
`cross-link`), simpler alternative, and checkpoint rather than presenting an
alphabetical catalogue as a learning order or implying a link is executable.

#### Scenario: Visible change pressure justifies a refactor
- **WHEN** a second implementation or ownership rule creates duplicated branching, incompatible shape, hidden state, or repeated orchestration
- **THEN** the lesson names the observed problem before introducing a pattern
- **AND** tests preserve behavior while the learner explains the new seam and its cost

#### Scenario: Direct Python is sufficient
- **WHEN** a function, module, mapping, closure, context manager, generator, or direct composition expresses the required behavior clearly
- **THEN** the decision record keeps that design and explains why a pattern object or hierarchy adds ceremony
- **AND** the route rubric accepts the justified non-pattern solution

#### Scenario: Premature abstraction is recoverable
- **WHEN** a learner adds a global Singleton, abstract hierarchy, Factory, Facade, or event bus without a second implementation or ownership pressure
- **THEN** the exercise identifies the unnecessary indirection or hidden lifecycle without blame
- **AND** recovery returns to direct code or records the future pressure that would justify the abstraction

#### Scenario: Learning transfers beyond the job runner
- **WHEN** the learner receives a second domain of approximately twenty lines with one concrete change pressure
- **THEN** they choose direct code or one studied pattern and complete the same decision record
- **AND** copying the job-runner structure without explaining forces and consequences does not satisfy the checkpoint

### Requirement: Routes are small, explicit, and independently stoppable
Appendix C SHALL expose six checkpoints in an explicit branch-and-join graph with incremental
estimates: Essential at two 60–75 minute sessions, Professional at two,
Advanced at one or two, Network resilience at three, Network capacity at one or
two, and Network crosswalk at one. Essential SHALL branch into
Professional→Advanced and Network resilience→Network capacity; Crosswalk SHALL
require both Advanced and Capacity. The complete graph SHALL be described as
10–12 sessions or approximately 10–15 hours. Each session SHALL use 25–35 minute
microcycles and each route SHALL state prerequisites, observable result,
starter/recovery point, completion criteria, rubric, reflection, and safe stop.

Essential SHALL require the Chapter 11 foundational checkpoint, the Chapter 12
essential checkpoint plus section 4 composition, and the Chapter 14, 15, and
18 checkpoints. Professional SHALL require Essential; Advanced SHALL require
Professional. Network resilience SHALL require Essential plus Chapters 19 and
21 and Chapter 23 intermediate. Network capacity SHALL additionally require
resilience plus Chapter 23 sections 7–8 and its concurrency/cleanup assessment
outcome. Network crosswalk SHALL require capacity plus Advanced. There SHALL be
no informal network mini-bridge and no Appendix C checkpoint SHALL become a
prerequisite for an existing route.

#### Scenario: Essential remains offline and calm
- **WHEN** a learner satisfies the Essential entry self-assessment but has not studied networking, type checking, `dataclasses`, or third-party frameworks
- **THEN** they complete pattern literacy, Strategy, a function Factory, and Adapter using the standard library
- **AND** one tested job runner demonstrates normal, invalid, and recovered behavior after a brief bridge maps Chapter 18 Arrange/Act/Assert knowledge to the minimum `unittest.TestCase`, `assertEqual`, and `assertRaises` syntax

#### Scenario: Professional and Advanced remain separable
- **WHEN** the Essential checkpoint passes
- **THEN** Professional adds Decorator and bounded synchronous Observer before Advanced introduces dependency injection, a composition root, one execution port, and an in-memory Adapter
- **AND** the learner may stop after either checkpoint without losing the completed result

#### Scenario: Network entry has no hidden bridge
- **WHEN** a learner selects Network resilience
- **THEN** the route requires the Essential checkpoint and the declared Chapter 19, 21, and 23 gates rather than compressing Strategy, state, and ports into an unassessed introduction
- **AND** unmet prerequisites link to exact localized recovery material

#### Scenario: Advanced network reading is correctly gated
- **WHEN** a learner has Chapter 23 intermediate but not sections 7–8 and their concurrency/cleanup outcome
- **THEN** they may complete Retry and Circuit Breaker but not Capacity or the Reactor/TaskGroup crosswalk
- **AND** the appendix links the missing Chapter 23 material without reteaching sockets, selectors, streams, or TLS

#### Scenario: Returning learner enters at a proven checkpoint
- **WHEN** a learner already demonstrates an earlier route's published completion criteria
- **THEN** an explicit self-assessment permits entry at the next route
- **AND** optional examples are not converted into hidden prerequisites or invented checkpoint credit

### Requirement: The executable core stays Pythonic and compact
The synthetic job runner SHALL implement Strategy as callables, a validating
function Factory, Adapter through explicit conversion, Decorator through
composition, bounded synchronous Observer, and explicit dependency injection
with one execution port and in-memory Adapter. It SHALL preserve one direct
baseline and contract tests through every refactor. The `Job`/`Result` model
SHALL NOT require `dataclass` knowledge.

The non-executable inventory SHALL be exact: Essential SHALL contrast function
Factory with Factory Method; Professional SHALL contain decision cards for
Command, Singleton, Proxy, and Template Method; Advanced SHALL contain one
Facade decision card; Iterator/Generator and Repository/service layer SHALL be
cross-links only. Builder and Composite SHALL be omitted from this delivery.
The lesson SHALL contrast Decorator pattern with `@decorator`, Adapter with
Proxy/Facade/Decorator, and Circuit Breaker State with direct conditionals,
`match`, or a transition table.

#### Scenario: Strategy separates selection from execution
- **WHEN** two interchangeable policies compute the same job decision
- **THEN** the caller receives one selected callable and tests both policies plus an injected fake
- **AND** unknown selection is a stable recoverable error rather than a partially constructed object

#### Scenario: Factory and Adapter each own one boundary
- **WHEN** configuration selects between two implementations and one legacy collaborator exposes an incompatible method/data/error shape
- **THEN** the Factory validates construction once and the Adapter translates only the collaborator boundary
- **AND** direct construction remains the documented alternative when only one implementation exists

#### Scenario: Decorator preserves the wrapped contract
- **WHEN** one measurement or bounded diagnostic is composed around job execution
- **THEN** return values and declared failures remain unchanged while wrapper order is observable
- **AND** the lesson explains that Python decorator syntax is a mechanism, not proof of the Decorator pattern's intent

#### Scenario: Observer is bounded and removable
- **WHEN** the subject notifies synchronous observers
- **THEN** registration is capped, iteration stays stable during removal, unsubscribe is idempotent, and one observer failure follows the documented isolation rule
- **AND** no event history or dead observer is retained without bound and the callback list is not called a network event bus

#### Scenario: Composition root owns dependencies
- **WHEN** domain work needs time, identifiers, output, or execution
- **THEN** the outer composition root injects deterministic collaborators and the domain test uses fakes
- **AND** changing the in-memory Adapter leaves domain code and its core tests unchanged without importing a framework or database

#### Scenario: Recognition card does not manufacture implementation pressure
- **WHEN** a learner studies Command, Facade, Singleton, Proxy, or Template Method
- **THEN** the card records its threshold, simpler Python alternative, consequence, and removal path
- **AND** no required companion implementation is added solely to display the pattern name

### Requirement: Retry preserves operation safety and one total deadline
The Network resilience route SHALL retry only `TransientDependencyError` and
only when the operation is retry-safe. An operation is retry-safe when it is
side-effect free or idempotent by contract, or when the dependency demonstrably
enforces deduplication for one stable idempotency key during the complete lab.
Merely attaching a key SHALL NOT make an operation retry-safe.

`PermanentDependencyError`, validation failure, `CircuitOpen`, and caller
cancellation SHALL NOT be retried. Validation and
retry-safety classification SHALL happen before the first dependency call.
After validation and breaker permission succeed, an unsafe operation SHALL make
its one requested call unless a later Capacity gate rejects it first. Across
every composition it SHALL make at most one dependency call and SHALL NOT make
an automatic second call.

One logical operation SHALL have a 500 ms monotonic total deadline, at most
three dependency attempts, a 100 ms per-attempt maximum, and injected 50 ms and
100 ms backoff before attempts two and three. Attempts and backoff SHALL consume
the same total deadline. A scheduled backoff SHALL start only when its complete
duration fits the remaining budget; otherwise the operation SHALL exhaust
without starting that delay or another attempt. Before any attempt, the policy
SHALL check remaining budget; its attempt limit SHALL be the lesser of 100 ms
and that budget. A timed-out owned attempt SHALL be cancelled and awaited before
mapping to `TransientDependencyError(code="attempt_timeout")`. Caller
`asyncio.CancelledError` SHALL propagate unchanged, and `RetryExhausted` SHALL
chain the last transient cause.

#### Scenario: Retry-safe transient operation recovers
- **WHEN** a retry-safe operation fails transiently twice and succeeds on its third attempt
- **THEN** exactly three dependency calls occur with injected 50/100 ms backoff
- **AND** every complete delay and call stays inside the 500 ms total deadline

#### Scenario: Enforced deduplication prevents duplicate effects
- **WHEN** a side-effecting operation carries one stable key to a fake dependency that enforces the declared deduplication contract
- **THEN** every attempt carries that key and the fake records exactly one logical effect
- **AND** removing enforcement makes the operation ineligible for automatic retry

#### Scenario: Unsafe or permanent failure is not retried
- **WHEN** a valid admitted operation reaches the dependency without an enforced deduplication contract or its first response is `PermanentDependencyError`
- **THEN** exactly one dependency call occurs with no backoff
- **AND** validation, open-circuit, or Capacity admission failure before invocation produces zero dependency calls

#### Scenario: Timeout, exhaustion, and cancellation clean up
- **WHEN** an owned attempt stalls, every allowed transient attempt fails, the total budget expires, or the caller cancels
- **THEN** every started attempt either finishes or, if still active at timeout or cancellation, is cancelled and awaited
- **AND** exhaustion preserves the last transient cause, cancellation propagates without mapping, and no late task mutates state

### Requirement: Circuit Breaker records dependency health consistently
The Network resilience route SHALL create one Circuit Breaker per declared
dependency-health domain, not per request or across unrelated dependencies. It
SHALL classify final outcomes as follows: raw `TransientDependencyError` when
retry is unavailable or bypassed, and `RetryExhausted` caused by one after
retries, are negative; dependency success or responsive
`PermanentDependencyError` is positive; validation and caller cancellation
without a dependency-health result are neutral. Each logical operation SHALL
produce at most one health observation.

In CLOSED, three negative observations with no positive observation between
them SHALL open the circuit. Positive SHALL reset the count; neutral SHALL
neither increment nor reset it. OPEN SHALL return
`CircuitOpen(code="circuit_open")` without invoking the dependency. After an
injected one-second cooldown, at most one caller SHALL acquire the HALF_OPEN
probe lease and make one 100 ms dependency attempt with no retry or backoff.

Probe success or responsive `PermanentDependencyError` SHALL close/reset the
breaker while preserving the operation result. Probe transient failure or
timeout SHALL reopen with a fresh cooldown. Caller cancellation SHALL propagate,
release the probe lease, and return to OPEN without starting another cooldown;
the already elapsed probe eligibility SHALL remain available to a later caller.

#### Scenario: Positive health resets consecutive negatives
- **WHEN** two transient retry exhaustions are followed by success or a responsive permanent response and then two more transient exhaustions
- **THEN** the breaker remains CLOSED because the positive observation reset the count
- **AND** a permanent operation error still propagates to its caller

#### Scenario: Open circuit fails without a dependency call
- **WHEN** three negative health observations with no positive observation between them open the circuit
- **THEN** the next normal operation returns `circuit_open`
- **AND** it makes no dependency call

#### Scenario: Half-open probe is exclusive
- **WHEN** the cooldown has elapsed and concurrent callers arrive
- **THEN** exactly one caller performs one bounded probe and every other caller receives `circuit_open`
- **AND** positive health closes, while transient failure or timeout reopens with a fresh cooldown

#### Scenario: Cancelled probe is not a health failure
- **WHEN** the caller cancels the HALF_OPEN probe before a dependency-health result exists
- **THEN** cancellation propagates and the lease is released exactly once
- **AND** the breaker remains OPEN with already elapsed eligibility so a later caller may compete for a probe

#### Scenario: Retry attempts do not amplify breaker counts
- **WHEN** three logical operations each exhaust their three attempts
- **THEN** the breaker sees three negative final observations and opens after exactly nine dependency calls
- **AND** the next open-circuit call invokes the dependency zero times

#### Scenario: Unsafe transient outcome is one negative observation
- **WHEN** a retry-unsafe operation receives one `TransientDependencyError`
- **THEN** the breaker records exactly one negative health observation without an automatic retry
- **AND** three such logical operations can open the breaker after exactly three dependency calls

### Requirement: Bulkheads prove isolation and optional Pub/Sub avoids delivery claims
After the Resilience checkpoint passes, Capacity SHALL extend its composition to
`validation → breaker permission → retry loop → Bulkhead lease per attempt →
per-attempt timeout → dependency`. A Bulkhead lease SHALL cover one attempt and
be released before retry backoff. Admission SHALL consume the same 500 ms total
deadline. Admission failure itself SHALL be neither retried nor treated as a
new breaker health observation, and an open circuit SHALL fail before acquiring
capacity. If a HALF_OPEN probe is cancelled or admission fails before dependency
health is observed, its probe lease SHALL be released and the breaker SHALL
stay OPEN with the already elapsed probe eligibility.

The capacity route SHALL use exactly two independent Bulkheads named `local`
and `remote`. Each SHALL own one execution lease and one queued-admission slot,
with no persistent worker task or second external-waiter queue. A third proposal
to the same full compartment SHALL fail immediately with
`Overloaded(code="overloaded")` without allocating an additional owned task,
waiter, or lease. The queued admission SHALL expire after the lesser of an
injected 50 ms admission deadline and the caller's remaining total deadline;
timeout or cancellation
SHALL remove it exactly once. If admission expires or rejects before any
dependency result in the logical operation, the operation SHALL
return local `Overloaded(code="admission_timeout")` or
`Overloaded(code="overloaded")` with zero dependency calls and neutral breaker
health. If a prior attempt in the same operation already produced a transient
result, admission failure SHALL stop the retry loop and return
`RetryExhausted` chained from that last transient cause; the local admission
event SHALL NOT add a second health observation.

Pub/Sub SHALL be labelled an optional process-local extension, not a requirement
for any later checkpoint. Its companion SHALL be in-memory, non-durable, and
free of background consumer tasks, network transport, replay, or retained
history. It SHALL allow at most four subscribers and eight queued events per
subscriber. `publish()` SHALL report opaque `enqueued` and `disconnected` IDs
and SHALL NOT call an enqueued event delivered or processed.

The required Capacity checkpoint SHALL assess Bulkhead isolation and admission
recovery only. If the learner completes Pub/Sub, its additional criterion SHALL
be distinguishing enqueue from delivery; skipping it SHALL NOT block Crosswalk.
Publication tests SHALL still verify the optional companion as a maintained
learning asset.

#### Scenario: Remote saturation leaves local capacity independent
- **WHEN** `remote` has one executing operation and one queued admission and a third remote proposal arrives
- **THEN** the third proposal fails immediately with `overloaded`
- **AND** one `local` operation acquires its independent lease and completes

#### Scenario: Waiting capacity recovers
- **WHEN** the one queued admission expires or is cancelled
- **THEN** its slot is removed exactly once, expiration before a first dependency call returns `admission_timeout`, and one later proposal may occupy it
- **AND** completion or cancellation of the executing operation promotes at most one queued admission without leaking a lease or task

#### Scenario: Admission expiry after a transient preserves the real cause
- **WHEN** one dependency attempt fails transiently and admission for the next attempt expires within the total deadline
- **THEN** no next dependency call starts and `RetryExhausted` chains the prior `TransientDependencyError`
- **AND** the admission event creates no additional breaker observation or retained waiter

#### Scenario: Retry releases capacity before backoff
- **WHEN** a dependency attempt fails transiently and Retry schedules another attempt
- **THEN** the attempt lease is released before backoff begins
- **AND** another admitted operation may use the compartment while the logical operation waits

#### Scenario: Open or locally rejected probe preserves capacity and health
- **WHEN** the circuit is OPEN, or a permitted HALF_OPEN probe cannot obtain Bulkhead capacity
- **THEN** the open call acquires no lease, while local rejection releases the probe lease and returns the admission result without a dependency call
- **AND** neither result changes dependency health and the locally rejected probe retains already elapsed probe eligibility

#### Scenario: Slow subscriber is isolated
- **WHEN** one subscriber holds eight pending events and a ninth event is published
- **THEN** that subscriber is disconnected, the ninth event is not enqueued for it, and eight discarded events are reported by count without content
- **AND** every healthy subscriber enqueues the ninth event in its own FIFO order

#### Scenario: Subscriber capacity fails closed and recovers
- **WHEN** four subscribers exist and a fifth registration is proposed
- **THEN** registration fails with `resource_limit` without changing the four existing subscriptions
- **AND** idempotently removing one subscriber permits one later registration

#### Scenario: Enqueue is not delivery
- **WHEN** `publish()` returns an `enqueued` subscriber ID
- **THEN** the lesson claims only that the event entered that bounded local queue
- **AND** it claims no processing, acknowledgement, durability, replay, global ordering, or network delivery

#### Scenario: Capacity terms are not conflated
- **WHEN** the learner compares timeout, Retry, Circuit Breaker, Bulkhead, rate limiting, load shedding, Pub/Sub, and Chapter 23 `writer.drain()`
- **THEN** a table and equivalent list distinguish purpose, owner, failure signal, and recovery
- **AND** application admission is not called end-to-end backpressure or transport flow control

### Requirement: Reactor and supervision remain evidence-backed readings
The final Network crosswalk SHALL reuse Chapter 21 and Chapter 23 sources.
Appendix C SHALL NOT implement another selector loop, `asyncio` server,
listener, framing codec, wire schema, socket Adapter, or task-restart system.

The Reactor reading SHALL map Chapter 23's selector, registered sockets,
READ/WRITE interests, dispatch, idle expiry, and idempotent close to
Reactor-like responsibilities while distinguishing the readiness demultiplexer
from the complete pattern. The structured-concurrency reading SHALL map Chapter
21 `TaskGroup` ownership, sibling cancellation, `ExceptionGroup`, timeout, and
cleanup. It SHALL explain that a Supervisor would add an explicit restart,
isolation, or escalation policy and SHALL use “Supervisor-like” only as a
comparison label.

#### Scenario: Learner traces Reactor-like readiness
- **WHEN** the learner traces one partial peer and one ready peer through the existing Chapter 23 selector companion
- **THEN** they identify registration, readiness selection, dispatch, interest changes, idle expiry, and close
- **AND** executable framing/lifecycle evidence remains owned by `network:network-suite`

#### Scenario: Learner traces structured task ownership
- **WHEN** the learner traces success, child failure, timeout, and caller cancellation through a Chapter 21 `TaskGroup` example
- **THEN** they identify owner, sibling-cancellation rule, propagated exception, and cleanup boundary
- **AND** they do not relabel `TaskGroup` as a restart Supervisor

#### Scenario: Simpler network abstraction remains valid
- **WHEN** streams plus `TaskGroup` already express the required flow and ownership
- **THEN** the checkpoint accepts them instead of requiring a custom Reactor or Supervisor
- **AND** the learner explains what additional pressure would justify lower-level readiness or explicit supervision policy

### Requirement: Appendix C verification is bounded and truthfully owned
Appendix C SHALL provide tested companion sources, standard-library unit tests,
`SOURCES.md`, `TRACEABILITY.md`, `VERIFICATION.md`, and one minimal plugin that
registers exactly `patterns:core-suite` and `patterns:network-suite`. The plugin
SHALL invoke only its known tests and SHALL NOT implement a second process-tree
manager, output collector, repository snapshot, or aggregate clock.

The generic plugin runner SHALL retain ownership of isolated child execution,
temporary working state, the configured 30-second check timeout and 64 KiB
output limit, descendant cleanup, selection/schema diagnostics, and repository
mutation detection. The quality-matrix runner SHALL retain the outer
`patterns-domain` bounds. Required tests SHALL use injected clocks/failures and
offline state; no socket or public-network execution belongs to Appendix C.

#### Scenario: Core suite is selected
- **WHEN** `patterns:core-suite` runs on supported CPython 3.11+
- **THEN** it verifies direct, Essential, Professional, Advanced, recovery, and transfer contracts
- **AND** it does not imply that network policy or any human review passed

#### Scenario: Network suite is selected
- **WHEN** `patterns:network-suite` runs
- **THEN** it verifies Retry/deduplication, Circuit Breaker, Bulkhead, optional Pub/Sub, cancellation, and zero owned residue
- **AND** it performs no socket operation and does not relabel Chapter 21/23 evidence as re-executed

#### Scenario: Generic containment fails closed
- **WHEN** plugin registration/execution crashes, times out, exceeds output, leaves a descendant, emits malformed results, mutates source, or references an unsafe path
- **THEN** the generic runner reports the bounded failure under its existing contract
- **AND** the Appendix plugin does not duplicate or weaken that containment

#### Scenario: Human approval remains separate
- **WHEN** both pattern checks plus generic structure, links, source references, RTL signals, and hygiene pass
- **THEN** automation records only those observations
- **AND** automation neither creates nor changes cold-read or specialist human evidence: absent decisions remain pending and completed records retain their actual current state

### Requirement: Appendix C preserves multilingual and accessible pedagogy
Canonical English and all four localized siblings SHALL preserve objectives,
route gates, pattern/problem mappings, public identifiers, source references,
examples, predictions, TODOs/hints, normal/boundary/recovery cases, explained
solutions, rubrics, cleanup, and reflection. Before localization, a cold-read
pilot by one or more people who did not design the appendix and who match a
declared target entry profile SHALL record role-only evidence without names or
personal data, declared prerequisites, environment, route coverage, real
duration, vocabulary blocks, requested help, and recovery failures. The pilot
SHALL collectively cover all six checkpoints. A checkpoint SHALL pass only when
it finishes within the published upper estimate using documented hints and
recovery without unplanned external instruction. Exceeding that estimate or
requiring such help SHALL create a critical finding; the content SHALL be
corrected and that checkpoint retested before localization.

The unit SHALL use one H1, hierarchical headings, descriptive links, readable
tables with list alternatives, text equivalents for visuals, and exactly one
balanced outer RTL wrapper in Arabic. Technical literals SHALL remain readable
left-to-right.

#### Scenario: Pattern names remain searchable across languages
- **WHEN** Strategy, Adapter, Observer, State, Circuit Breaker, Bulkhead, or Reactor appears in a localized lesson
- **THEN** the explanation gives a natural-language meaning while retaining the stable English name on first use
- **AND** identifiers, diagnostics, capacities, and behavior remain technically equivalent

#### Scenario: Cold-read findings precede translation
- **WHEN** the canonical route and companions are ready for localization
- **THEN** target-profile participants record only role, prerequisites, environment, collective route coverage, time, jargon, blocked steps, starter recovery, and whether published help was sufficient
- **AND** an over-time or unplanned-help checkpoint is corrected and retested, while unresolved critical findings block translation rather than multiplying the defect across four languages

#### Scenario: Arabic route keeps technical content legible
- **WHEN** Arabic prose contains code, commands, state transitions, capacities, paths, hashes, or output
- **THEN** exactly one outer `<div dir="rtl">` remains balanced and technical literals stay legible left-to-right
- **AND** no decision depends on color, icon, visual position, or arrow direction alone

#### Scenario: Root publication is atomic
- **WHEN** Appendix C is ready to enter the catalogue
- **THEN** all five siblings, companions, source records, and both owned checks exist before all six root indexes add language-matched links
- **AND** root `README.md` and `README.en.md` remain byte-identical and all numbered chapters precede Appendices A, B, and C

#### Scenario: Provenance cannot be inferred
- **WHEN** original examples coexist with externally informed terminology or diagrams
- **THEN** sources, licenses, adaptations, and review dates are recorded without copying unsupported prose or inferring republication permission
- **AND** unresolved provenance blocks final publication rather than being baselined away
