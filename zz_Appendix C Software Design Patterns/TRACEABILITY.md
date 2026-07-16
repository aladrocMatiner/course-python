# Appendix C learning and evidence traceability

## Traceability contract

This record maps the canonical objectives to teaching anchors, learner work,
normal/boundary/recovery evidence, checkpoints, companions, and evidence
owners. It was drafted on **2026-07-16**. A planned row is not an executed or
accepted row; current outcomes are in [VERIFICATION.md](VERIFICATION.md).

## Objective-to-assessment matrix

<!-- bookcheck: table-alternative -->
| ID | Observable objective | Teaching anchor | Learner work and hint | Happy/boundary/recovery evidence | Checkpoint and rubric | Companion/check owner |
|---|---|---|---|---|---|---|
| C-01 | choose from observed pressure and record a simpler option, cost, failure, verification, and removal | [decision record](README.md#the-decision-record-used-in-every-required-exercise) | complete the eight-field record in every required exercise; direct Python is an accepted hint | one justified pattern, one justified direct solution, and one removal decision | assessed in all six route checkpoints | `domain.py` decision fixture; `patterns:core-suite` where executable |
| C-02 | navigate the branch/join route without a hidden network bridge | [routes and time](README.md#routes-dependency-graph-and-time-budget), [dual indexes](README.md#family-index) | entry diagnostic and route choice; recovery links return to Chapters 11/12/14/15/18 | eligible start, blocked prerequisite, safe stop | route exits; 10–12 sessions/10–15 h complete budget | prose/graph/manual curriculum review |
| C-E1 | separate behavior selection with Strategy callables | [Essential](README.md#essential-route-earn-the-first-three-seams) | two policies; hint: pass, do not call, the callable | equivalent direct/refactored result; unknown selection; next valid run | Essential rubric | `direct.py`, `essential.py`, `test_core_patterns.py`; `patterns:core-suite` |
| C-E2 | centralize validated construction in a function Factory and distinguish Factory Method | [Essential explained solution](README.md#essential-explained-solution-and-decisions) | build selected executor; hint: mapping can beat hierarchy | known construction; unknown name before execution; unchanged valid path | Essential rubric | `essential.py`, `test_core_patterns.py`; `patterns:core-suite` |
| C-E3 | translate data, method, output, and error at one Adapter boundary | [Essential cases](README.md#essential-happy-boundary-and-recovery-cases) | wrap unchanged legacy fake; hint: write translations separately | valid translation; invalid boundary; chained cause and later recovery | Essential rubric | `essential.py`, `test_core_patterns.py`; `patterns:core-suite` |
| C-P1 | wrap one contract with composition while preserving return and failure | [Decorator](README.md#decorator-through-composition) | add measurement in `finally`; hint: one wrapper before nesting | same result; documented nesting; same failure plus measurement | Professional rubric | `professional.py`, `test_core_patterns.py`; `patterns:core-suite` |
| C-P2 | notify a capped synchronous subscriber set with stable iteration and idempotent removal | [Observer](README.md#bounded-synchronous-observer) | subscribe/notify/remove; hint: snapshot iteration | two subscribers; cap; observer failure and later usable subject | Professional rubric | `professional.py`, `test_core_patterns.py`; `patterns:core-suite` |
| C-P3 | recognize Command, Singleton, Proxy, and Template Method without promoting them to route implementations | [decision cards](README.md#professional-decision-cards) and their catalogue pages | full decision record plus one bounded contrast for each card | justified use; simpler alternative; removal threshold; verified local contrast | Professional card review | local `example.py` files and manual decision review; status `decision-card` |
| C-P4 | transfer selection reasoning to a small shipping domain | [transfer exercise](README.md#transfer-exercise-choose-instead-of-copy) | choose branch or Strategy; hint: two callables may be enough | standard/express; invalid distance; unknown-mode recovery | Professional rubric accepts both designs | `direct.py`, `essential.py`, `test_core_patterns.py`; `patterns:core-suite` |
| C-A1 | make time, IDs, output, and execution explicitly owned at one composition root | [Advanced ownership](README.md#ownership-before-abstraction) | inject one collaborator at a time | deterministic run; exhausted fake/error; fresh root has no residue | Advanced rubric | `architecture.py`, `test_core_patterns.py`; `patterns:core-suite` |
| C-A2 | define one execution port/in-memory Adapter without duplicating persistence architecture | [Advanced cross-links](README.md#facade-decision-card-and-owned-cross-links) | swap in-memory Adapter; compare direct composition | same domain behavior; adapter rejection; clean new root | Advanced rubric accepts justified direct composition | `architecture.py`, `test_core_patterns.py`; `patterns:core-suite` |
| C-A3 | assess Facade and defer Repository/service layer to owners | [Facade card](README.md#facade-decision-card-and-owned-cross-links) and their catalogue pages | bounded Facade contrast plus Chapter 17/28 client readings | justified card; no duplicated owner implementation; removal case | Advanced card review | local examples/manual decision plus Chapters 17/28 cross-links |
| C-R1 | allow Retry only for transient, demonstrably retry-safe work | [Resilience session 1](README.md#session-1-classify-retry-safety) | classify four operations; hint: key is not enforcement | safe recovery; key-without-enforcement; permanent/unsafe one call | Resilience rubric | `resilience.py`, `test_network_patterns.py`; `patterns:network-suite` |
| C-R2 | share one 500 ms monotonic budget across ≤3 attempts, ≤100 ms per attempt, and 50/100 ms backoff | [Resilience session 2](README.md#session-2-one-deadline-owns-attempts-and-backoff) | inject clock/delay; predict full-backoff-fit boundary | transient then success; insufficient full delay; timeout cancellation/await and chained exhaustion | Resilience rubric | `resilience.py`, `test_network_patterns.py`; `patterns:network-suite` |
| C-R3 | apply consistent positive/negative/neutral health observations across CLOSED/OPEN/HALF_OPEN | [Resilience session 3](README.md#session-3-circuit-breaker-as-justified-state) | compose without Capacity; contrast State with conditional/table | positive reset; nine-call opening and zero-call OPEN; pre-result cancellation neutral; post-transient cancellation one negative; exclusive/cancelled probe recovery | Resilience rubric | `resilience.py`, `test_network_patterns.py`; `patterns:network-suite` |
| C-C1 | isolate local and remote capacity with one running and one waiting slot each | [Capacity lab](README.md#required-saturation-lab) | saturate remote; hint: lease per attempt, release before backoff | local/remote success; third remote overload; promotion and timeout/cancellation cleanup | required Capacity rubric | `capacity.py`, `test_network_patterns.py`; `patterns:network-suite` |
| C-C2 | classify admission as local while preserving total deadline, Retry cause, breaker probe, and residue contracts | [Capacity cases](README.md#required-saturation-lab) | place admission after Retry permission and before each dependency attempt | zero-call neutral rejection; prior-transient exhaustion/cancellation keeps one negative; HALF_OPEN eligibility recovery | required Capacity rubric | `capacity.py`, `test_network_patterns.py`; `patterns:network-suite` |
| C-C3 | optionally enqueue bounded local fan-out without delivery claims | [optional Pub/Sub](README.md#optional-second-session-enqueue-only-local-pubsub) | fill one subscriber; hint: count-only discard | healthy enqueue; fifth registration; slow disconnect and slot reuse | optional, excluded from required Capacity score | `pubsub.py`, `test_network_patterns.py`; `patterns:network-suite` |
| C-X1 | trace Reactor-like registration, interest, readiness, dispatch, expiry, and close in existing Chapter 23 code | [Chapter 23 reading](README.md#chapter-23-reactor-like-reading) | worksheet starter before answer key | readable peer; partial-write boundary; idle/error close recovery | Crosswalk rubric | Chapter 23 `selector_hub.py`; existing `network:network-suite` plus reading interpretation |
| C-X2 | trace `TaskGroup` owner, sibling/caller cancellation, `ExceptionGroup`, timeout, propagation, and cleanup | [Chapter 21 reading](README.md#chapter-21-taskgroup-reading) | worksheet and cancellation trace | group success; child failure; caller cancellation after cleanup | Crosswalk rubric | Chapter 21 `structured_async.py` and tests; generic/manual evidence, no invented check ID |
| C-X3 | defend streams + `TaskGroup` or a more complex design with one cross-route decision | [synthesis](README.md#synthesis-decision-and-reading-cases) | eight-field record and longitudinal responsibility map | normal/boundary/recovery reading cases; no new server code | final Crosswalk rubric | prose/manual review over existing Chapters 21/23 |

List equivalent by checkpoint: C-01/C-02 assess decision literacy and route
entry; C-E1–C-E3 assess Strategy, function Factory, and Adapter in the core
suite; C-P1–C-P4 assess Decorator, Observer, four cards, and transfer; C-A1–C-A3
assess explicit ownership, one port/Adapter, and the Facade/Repository boundary;
C-R1–C-R3 assess Retry safety, one deadline, and Circuit Breaker health; C-C1
and C-C2 assess required isolation/admission while C-C3 is optional Pub/Sub;
C-X1–C-X3 assess the existing Chapter 23/21 responsibility trace and one
synthesis decision. Every executable row requires happy, boundary, recovery,
and the named suite; cards/cross-links require a bounded verified contrast or
client plus manual explanation rather than a new route-level or duplicated
owner implementation.

## Exact pattern inventory and delivery status

| Pattern/technique | Delivery status | Route/checkpoint | Source owner |
|---|---|---|---|
| Strategy callable, function Factory, Adapter | executable | Essential | Appendix C core suite |
| Factory Method | decision-card contrast | Essential | Appendix C local example + prose |
| composition Decorator, bounded synchronous Observer | executable | Professional | Appendix C core suite |
| Command, Singleton, Proxy, Template Method | decision-card | Professional | Appendix C local examples + prose |
| dependency injection, composition root, execution port, in-memory Adapter | executable | Advanced | Appendix C core suite |
| Facade | decision-card | Advanced | Appendix C local example + prose |
| Retry and Circuit Breaker | executable | Resilience | Appendix C network suite |
| State | cross-link view over Circuit Breaker | Resilience | Appendix C Circuit Breaker example + catalogue check |
| two Bulkheads | executable | required Capacity | Appendix C network suite |
| bounded Pub/Sub | executable but optional | optional Capacity | Appendix C network suite |
| Reactor-like and `TaskGroup`/Supervisor-like responsibility maps | cross-link/reading | Crosswalk | Chapters 23 and 21 respectively |
| Iterator/Generator | cross-link only | Chapter 26 | Chapter 26 |
| Repository/service layer | cross-link only | Chapters 17/28 | Chapters 17/28 |
| Builder and Composite | omitted | none | none |

## Source-reference and evidence ownership

| Lesson reference | Companion path | Check ID/evidence mode | Current contract |
|---|---|---|---|
| direct, Essential, Professional, Advanced excerpts | `zz_Appendix C Software Design Patterns/_shared/patterns/{direct,essential,professional,architecture}.py` | `patterns:core-suite` | sources exist and 21 focused tests pass; shared known-check ownership must still accept every excerpt before publication |
| Resilience, Capacity, Pub/Sub excerpts | `zz_Appendix C Software Design Patterns/_shared/patterns/{resilience,capacity,pubsub}.py` | `patterns:network-suite` | corrected sources pass 47 focused tests on CPython 3.11.14/3.12.12/3.13.11/3.14.2 and independent adversarial review; shared known-check acceptance remains pending |
| root family table and all 25 catalogue pages/examples | `catalog.toml`, `<family> - <Pattern Name>/{README.md,example.py}` | `patterns:core-suite` via `test_core_catalog.py` | seven closed-catalogue tests prove manifest/table/filesystem bijection, local links, page identity, bounded import-safe examples, and successful execution; localization and human review remain pending |
| Reactor-like excerpt | `chapter-23-network-programming/examples/telemetry/selector_hub.py` | existing `network:network-suite` | Appendix C may reference but neither replace nor report the Chapter 23 check as its own |
| `TaskGroup` excerpt | `chapter-21-async/structured_async.py` | generic/manual companion evidence | no `bookcheck` check ID is invented; interpretation remains manual |

The present Appendix C test paths are `tests/test_core_patterns.py`,
`tests/test_core_catalog.py`, and `tests/test_network_patterns.py`. Generic check execution is bounded
to 30 seconds and 64 KiB captured output; the future `patterns-domain` profile
is bounded to 120 seconds and 512 KiB. These are containment limits, not
performance targets.

At this evidence cut, both focused suites and the minimal plugin exist. Core's
21 route tests plus seven catalogue tests and network's corrected 47 tests are
green on the authoring CPython; the complete local appendix suite is 75/75. The
original route suites remain green across CPython
3.11.14/3.12.12/3.13.11/3.14.2. An
independent adversarial review also passes the 25-test Resilience-only run with
Capacity/Pub/Sub imports blocked and reports no CRITICAL/WARNING finding. The
plugin's eight synthetic selection/failure fixtures and real core/network
checks are green. Shared source-reference acceptance and the human gates below
remain pending; machine passes do not replace either boundary.

## Human gates not represented by test IDs

- target-profile cold read across all six required checkpoints and published
  upper time bounds;
- pedagogical and technical review of explanations, solutions, and rubrics;
- natural Spanish, Catalan, Swedish, and Arabic semantic-parity review;
- rendered accessibility and Arabic bidi review;
- provenance/license review against final digests; and
- final publication approval.

Records must identify reviewer roles, scope, date, inputs, findings, corrections,
and retest outcome, but must not store participant names or other personal data.
Automation cannot change any of these rows to accepted.
