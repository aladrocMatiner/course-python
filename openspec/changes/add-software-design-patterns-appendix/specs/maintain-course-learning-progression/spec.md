## ADDED Requirements

### Requirement: Appendix C is an optional progression-first route with three network checkpoints
The six root indexes and `tools/curriculum_map.toml` SHALL publish
physical path `zz_Appendix C Software Design Patterns` under stable logical ID
`appendix-software-design-patterns` as **Appendix C: Software Design Patterns
in Python** after Appendices A and B. The declared path migration SHALL be
complete before publication. The main route order, incremental estimates, and
observable outcomes SHALL be:

- **Essential · 2 × 60–75 minutes:** after the Chapter 11 foundational
  checkpoint, Chapter 12 essential checkpoint plus section 4 composition, and
  the Chapter 14, 15, and 18 checkpoints. Outcome: pattern literacy, Strategy,
  function Factory, and Adapter in one tested job runner, including one
  justified non-pattern choice.
- **Professional · 2 × 60–75 minutes:** after Essential. Outcome: Decorator,
  bounded synchronous Observer, Python-specific contrasts, and decision cards.
- **Advanced · 1–2 × 60–75 minutes:** after Professional. Outcome: explicit
  dependency injection, composition root, one execution port, and an in-memory
  Adapter with deterministic fakes.
- **Network resilience · 3 × 60–75 minutes:** after Essential, Chapters 19 and
  21, and Chapter 23's localized intermediate checkpoint. Outcome: safe bounded
  Retry/deduplication and Circuit Breaker/State with injected time.
- **Network capacity · 1–2 × 60–75 minutes:** after Network resilience and
  Chapter 23 sections 7–8 plus its concurrency/cleanup assessment outcome.
  Required outcome: two isolating Bulkheads with bounded admission and recovery.
  Separately skippable extension: bounded queued Pub/Sub.
- **Network crosswalk · 1 × 60–75 minutes:** after Network capacity and
  Advanced. Outcome: evidence-backed Reactor-like and `TaskGroup` ownership
  reading over Chapters 21/23 without another implementation.

Essential SHALL be the common entry to two branches:
Professional→Advanced and Network resilience→Network capacity. Network
crosswalk SHALL join both branch exits by requiring Advanced and Capacity. The
complete graph SHALL be described as 10–12 sessions, approximately 10–15 hours;
for a learner who already completed Advanced, Resilience→Capacity→Crosswalk
SHALL add 5–6 sessions, while a learner starting from Essential SHALL also
complete the 3–4 Professional/Advanced sessions before Crosswalk. Every route
SHALL name a tested or observed artifact, completion
criteria, rubric, recovery point, and safe stopping/continuation choice. The
family and problem indexes SHALL remain secondary navigation and SHALL NOT move
a pattern into an earlier route. No Appendix C route SHALL become a prerequisite
for an existing chapter, appendix, native route, environment route, or capstone.

#### Scenario: Essential entry verifies real prerequisites
- **WHEN** a learner has only Chapter 12's essential class/instance outcome
- **THEN** Appendix C links the localized Chapter 11 foundational checkpoint, Chapter 12 section 4 composition, and the Chapter 14, 15, and 18 checkpoints
- **AND** an entry self-assessment verifies a callable, composition, one recoverable exception, a module boundary, and one deterministic test

#### Scenario: Pattern placement follows progression
- **WHEN** lesson or curriculum navigation is rendered
- **THEN** Essential owns Strategy/Factory/Adapter, Professional owns Decorator/Observer, Advanced owns dependency injection/port/in-memory Adapter, and Circuit Breaker owns executable State
- **AND** family classification and decision cards do not move later concepts into an earlier checkpoint

#### Scenario: Learner stops safely
- **WHEN** any Essential, Professional, Advanced, or network checkpoint passes
- **THEN** its runnable or observed result, completion criteria, and recovery point remain independently useful
- **AND** later optional content is not required to retain that completed outcome

#### Scenario: Network resilience starts from an honest baseline
- **WHEN** a learner selects Network resilience
- **THEN** Appendix C identifies Chapter 19's broad retry example as introductory rather than proof of retry safety
- **AND** it combines Chapter 23's no-auto-retry-writes boundary with Appendix C's deduplication and dependency-health contracts

#### Scenario: Network entry does not hide a mini-bridge
- **WHEN** a learner meets the Chapter 19, 21, and 23 network prerequisites but has not completed Appendix C Essential
- **THEN** the route directs them to the Essential self-assessment and recovery path
- **AND** it does not compress Strategy, State, or Adapter into an informal unassessed preface

#### Scenario: Capacity and crosswalk remain advanced
- **WHEN** a learner has only Chapter 23 intermediate and Network resilience
- **THEN** Capacity still requires Chapter 23 sections 7–8 and their concurrency/cleanup outcome
- **AND** Crosswalk additionally requires Advanced, so no hidden port or ownership prerequisite appears during assessment

#### Scenario: Chapter 23 intermediate is represented without weakening Chapter 23
- **WHEN** Appendix C curriculum nodes are registered
- **THEN** a stable `chapter-23-intermediate` bridge targets `chapter-23-network-programming/README.md#intermediate-checkpoint`
- **AND** the bridge explicitly depends on `chapter-14` and `chapter-18`; the final `chapter-23` node retains its direct `chapter-14`, `chapter-18`, and `chapter-21` prerequisites and additionally follows the bridge, while Appendix C resilience depends on the bridge and later network checkpoints depend on final Chapter 23 as declared

#### Scenario: Existing routes skip Appendix C
- **WHEN** a learner follows any existing foundations, practical, systems, environment, typing, native, or capstone route
- **THEN** every existing checkpoint remains reachable with its prior prerequisites
- **AND** no existing route gains an incoming requirement from Appendix C

#### Scenario: Incomplete scaffold is not published
- **WHEN** Appendix C lacks canonical English, any localized sibling, companion, source record, or registered `patterns:*` check required by its source references
- **THEN** global publication validation remains non-pass and no root index advertises Appendix C
- **AND** completing all targets is the documented recovery

#### Scenario: Root navigation is atomic and durations stay honest
- **WHEN** every Appendix C target and owned check exists
- **THEN** all six root indexes add language-matched links to `zz_Appendix C Software Design Patterns` after A/B in one publication wave and keep `README.md`/`README.en.md` byte-identical
- **AND** A/B retain their current estimate while Appendix C displays its own six route estimates, branch/join prerequisites, and approximately 10–15 hour complete graph

#### Scenario: Route navigation remains accessible
- **WHEN** the route map is read on a narrow screen or with assistive technology
- **THEN** a list states the same order, prerequisites, durations, optional edges, and completion criteria as any table or graph
- **AND** Arabic navigation preserves one RTL wrapper while identifiers, times, and paths remain legible left-to-right
