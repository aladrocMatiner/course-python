## Why

The course teaches Python syntax, objects, modules, tests, HTTP, `asyncio`, and
network mechanics, but it does not yet give learners a calm method for
recognizing recurring design pressure and deciding whether a named pattern is
better than a simpler Python construct. Appendix C closes that gap with one
bounded project and gives extra depth to network resilience without duplicating
Chapter 23.

## What Changes

- **BREAKING:** Move the unpublished Appendix C scaffold from
  `appendix-software-design-patterns` to the portable physical directory
  `zz_Appendix C Software Design Patterns` so it sorts after the numbered
  course material. Keep the visible title **Appendix C: Software Design
  Patterns in Python**; the colon is deliberately excluded from the path
  because it cannot be checked out on Windows.
- Give every included pattern or crosswalk technique one directory named
  `<family> - <Pattern Name>`, containing a focused `README.md` and a bounded
  `example.py`. Add a closed local catalogue and a root table grouped by family
  with a plain-language explanation, pressure, simpler Python alternative,
  pedagogical status, and link for every entry.
- Keep Appendix C as one publication/parity unit. Nested pattern pages are
  catalogue-owned companions: executable entries own runnable examples;
  decision cards own small verified contrasts; and cross-links own bounded
  usage or reading examples without duplicating the implementation maintained
  by another chapter.
- Publish canonical English and semantically equivalent Spanish, Catalan,
  Swedish, and Arabic routes while preserving the same catalogue contract.
- Organize a clear learning graph: Essential branches into
  Professional→Advanced and Network Resilience→Capacity, then the optional
  Crosswalk joins Advanced and Capacity. Add secondary indexes by pattern
  family and by the problem or symptom being solved.
- Grow one standard-library synthetic job runner from direct working code.
  Every exercise uses the same decision record: problem, forces, simplest
  Python option, chosen pattern, cost, expected failure, verification, and when
  to remove the abstraction.
- Keep the executable core deliberately small: Strategy, a function Factory,
  Adapter, Decorator, bounded synchronous Observer, explicit dependency
  injection, and one job-execution port with an in-memory adapter. Teach State
  through Circuit Breaker. Use Command, Singleton, Proxy, Template Method, and
  Facade as route-specific decision cards; Factory Method as an Essential
  contrast; and Iterator/Generator plus Repository/service layer as links.
  Builder and Composite are outside this delivery.
- Add an optional network deep dive with bounded Retry, enforced idempotency or
  deduplication, Circuit Breaker, two simplified Bulkheads, and optional queued
  Pub/Sub. Reuse Chapter 21 `TaskGroup` and Chapter 23 selector/lifecycle code
  for guided ownership and Reactor-like reading; do not add another server,
  framing protocol, loopback adapter, or custom Supervisor.
- Add tested companions, starters/recovery points, a transfer exercise,
  glossary, sources, traceability, verification notes, and isolated
  `patterns:core-suite` and `patterns:network-suite` checks through a minimal
  domain plugin.
- Publish the curriculum route, six root-index links, and additive parity
  evidence only after every localized target and owned check exists.

## Capabilities

### New Capabilities

- `teach-python-software-design-patterns`: Teach problem-first pattern
  selection, Python-specific trade-offs, a compact executable spine, and a
  bounded network-pattern deep dive.

### Modified Capabilities

- `maintain-course-learning-progression`: Add independently stoppable Appendix
  C routes and explicit Chapter 21/23 gates without changing any existing
  route's prerequisites.
- `complete-published-quality-evidence`: Register Appendix C, its localized
  pages, companions, sources, and isolated pattern checks without inheriting or
  manufacturing human approval.
- `deterministic-quality-evidence`: Add the exact `patterns-domain` binding to
  the closed quality matrix and least-privilege CI while reusing generic runner
  containment.
- `partitioned-parity-evidence`: Support the explicit additive
  32/128→33/132 publication transition while preserving unrelated evidence and
  all human acceptance boundaries.

## Impact

### Goals and measurable definition of done

- A learner can describe context, forces, ownership, and consequences; choose a
  pattern or justify direct Python; preserve behavior through a refactor; and
  verify a happy path, boundary, and recoverable failure.
- Essential is two 60–75 minute sessions, Professional is two, Advanced is one
  or two, and—when Advanced is already complete—the Network branch through
  Crosswalk adds five or six. The complete graph is therefore approximately
  10–15 hours and every route has an observable
  checkpoint and safe stopping point.
- Retry proves that a key alone is insufficient without dependency-side
  deduplication; Circuit Breaker uses consistent positive, negative, and neutral
  health observations; Bulkhead proves `local`/`remote` isolation with one
  running and one waiting operation each; Pub/Sub distinguishes enqueue from
  delivery; cancellation and cleanup leave no owned work.
- Canonical companion tests, both explicit plugin checks, curriculum/parity/root
  validation, strict OpenSpec validation, whitespace, and repository-hygiene
  checks pass without overstating compatibility or human review.
- All five lesson languages preserve learning outcomes, contracts, exercises,
  rubrics, links, safety, and Arabic bidi/LTR readability. A canonical cold-read
  pilot happens before localization; competent human release gates remain
  pending until actually completed.

### Non-goals

- Do not create an exhaustive Gang-of-Four catalogue, require memorization, or
  present patterns as inherently better than functions, modules, mappings,
  closures, context managers, or direct composition.
- Do not reproduce Chapter 23's sockets, framing, selectors, TLS, server, or
  protocol laboratories; implement restart supervision; deploy a public
  service; benchmark architectures; or claim production readiness.
- Do not add frameworks, brokers, databases, public targets, real credentials,
  unbounded queues/retries, fixed sleeps as correctness synchronization, or a
  second capstone domain.
- Do not rename Appendices A/B or any numbered chapter, and do not complete
  another active change's unchecked coordination or human-review task.

### Affected paths and systems

- `zz_Appendix C Software Design Patterns/**`, including the root/localized
  route pages, one documented example directory per catalogue entry, the
  closed catalogue, shared integration companions, tests, plugin,
  `SOURCES.md`, `TRACEABILITY.md`, and `VERIFICATION.md`.
- The six root READMEs and `tools/curriculum_map.toml`.
- Focused quality configuration, matrix tests, and least-privilege CI required
  to register `patterns-domain`; Chapter 23's plugin remains unchanged.
- Parity topology/evidence, attribution, and publication-signoff inputs for the
  additive 33/132 publication scope.

### Active-change coordination and risks

- `restore-multilingual-content-parity`, `add-book-quality-gates`,
  `add-core-python-bridges-and-capstone`, and
  `add-python-environment-toolchains` overlap shared quality, root, and parity
  surfaces. Appendix-local work may proceed, but implementation MUST reconcile
  their current spec ownership and re-read live digests before any shared edit.
- Implemented quality/parity state already contains Learning, Environment, and
  32/128 contracts that the base specs do not yet fully own. Appendix C's
  cumulative deltas are temporary conflict protection, not authority over those
  earlier changes; their owners MUST reconcile and sync first.
- Shared parity work starts only from a maintainer-confirmed valid 32/128
  baseline and applies Appendix C's 33/132 delta last. A changed baseline
  requires updating this plan instead of guessing new counts.
- Cognitive overload is mitigated by one project, two indexes, small
  microcycles, comparison with direct Python, recoverable starters, a transfer
  exercise, and independently stoppable routes.
- Network overclaiming is mitigated by injected time/failures, explicit bounds,
  no new wire protocol, exact ownership, and reuse of Chapter 21/23 evidence.

### Migration and rollback

Implementation first revises the change contract, then moves the Appendix C
tree to `zz_Appendix C Software Design Patterns`, adds its closed catalogue and
per-pattern pages, and rewrites every Appendix-local reference. Before public
navigation is added, shared discovery maps the portable physical path to the
stable logical unit ID `appendix-software-design-patterns`, checks the documented
old→new path migration, and aggregates nested pages into the same Appendix C
publication/parity unit. The canonical route and companions receive a cold-read
pilot before four localized siblings and pattern checks enter the public
catalogue. Rollback removes only unaccepted Appendix C navigation and isolated
profile/check registration, restores the former scaffold path if the physical
migration has not published, restores the prior reviewed topology/sign-off
inputs, and reruns the previous profiles. It does not alter Chapter 23 or delete
unrelated reviewer evidence.
