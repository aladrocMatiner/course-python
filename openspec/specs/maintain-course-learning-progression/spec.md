# maintain-course-learning-progression Specification

## Purpose
Define stable multilingual course routes and an acyclic prerequisite model that
separates essential from optional work, separates foundational functions from
optional higher-order programming in Chapter 11, and gives essential
assessments runnable recovery, accessible navigation, and repository-safe
verification.

## Requirements
### Requirement: Published course routes preserve stable content links

The course SHALL publish a course-level route map in root `README.md`, `README.en.md`, `README.es.md`, `README.ca.md`, `README.sv.md`, and `README.ar.md` without renaming any existing chapter or appendix directory, and SHALL retain the numerical chapter table of contents as the stable reference order.

The English route SHALL define these independently completable paths and localized indexes SHALL preserve their meaning:

- **Essential foundations:** Chapters 01–02, the essential checkpoints of Chapters 03–07, Chapters 08–10, the foundational route of Chapter 11, and Chapter 12;
- **Practical Python:** Chapters 13–18 after essential foundations;
- **Systems Python:** Chapters 19–23 after Chapters 13–18;
- **Optional native hero routes:** Chapter 24 for Python with C++ and Chapter 25 for Python with Rust, each selectable independently after its declared prerequisites; and
- **Appendix routes:** each appendix placed after the chapters named by that appendix's prerequisite contract.

Each route SHALL name its prerequisite, estimated multi-session duration, observable outcome, completion criteria, and a safe continuation or stopping point.

#### Scenario: Happy path through essential foundations

- **WHEN** a beginner starts from a root index and follows the essential-foundations route
- **THEN** every required checkpoint is reachable using only concepts already taught in an earlier required checkpoint
- **AND** optional professional or hero material can be skipped without losing the next essential continuation link

#### Scenario: Edge case for a returning learner

- **WHEN** a learner already meets the stated completion criteria for a route stage
- **THEN** the route map permits entry at the next stage and names the exact checkpoint used to self-assess readiness
- **AND** does not require rereading optional previews as if they were prerequisites

#### Scenario: Failure when a route target is unavailable

- **WHEN** a root route or table-of-contents entry would point to a missing unit or missing language sibling
- **THEN** publication validation fails before the link is added
- **AND** the existing root indexes and stable links remain unchanged

#### Scenario: Recovery after a route correction

- **WHEN** a prerequisite audit changes a route transition but no public path migration is approved
- **THEN** maintainers update route prose and links rather than renaming or renumbering directories
- **AND** rerun navigation, mirror, and prerequisite checks before publishing

#### Scenario: Localized route navigation

- **WHEN** a learner reads a Spanish, Catalan, Swedish, or Arabic root route
- **THEN** every in-course route link targets the corresponding localized sibling
- **AND** the route order, outcomes, completion criteria, and optional boundaries are semantically equivalent to canonical English

#### Scenario: Accessible route presentation

- **WHEN** route choices are rendered on a narrow screen or read with assistive technology
- **THEN** the same sequence and dependencies are available as descriptive text or a simple list
- **AND** no decision depends only on a table position, color, icon, arrow, or visual layout

### Requirement: Required work has an explicit acyclic prerequisite contract

Every chapter and appendix SHALL distinguish required prerequisites from optional previews. Required examples, exercises, solutions, checkpoints, and assessment SHALL use only concepts introduced in that unit's required route or in its declared prerequisites. The course SHALL maintain an auditable acyclic dependency map from each required checkpoint to the earlier explanations that teach every required concept.

#### Scenario: Happy path for a required concept

- **WHEN** a required exercise uses a concept such as a conditional, loop, function, exception, class, dependency, or test
- **THEN** the unit links to an already completed required explanation or teaches the concept before the exercise
- **AND** the explained solution introduces no hidden prerequisite

#### Scenario: Edge case for Chapters 03 through 07

- **WHEN** a collection chapter demonstrates a later concept before Chapters 08–18 teach it fully
- **THEN** that demonstration is outside the essential checkpoint and is labeled **Optional preview**
- **AND** the essential exercise has an equivalent solution using only the chapter's declared earlier prerequisites

#### Scenario: Failure on a dependency cycle

- **WHEN** the dependency map finds that checkpoint A requires checkpoint B while B directly or transitively requires A
- **THEN** the prerequisite gate fails with both unit paths and the shortest detected cycle
- **AND** neither checkpoint is described as beginner-completable

#### Scenario: Recovery from an intentional preview

- **WHEN** a later concept is useful for motivation but is not needed for current mastery
- **THEN** the preview explains the minimum idea, provides a copyable or skippable path, and links to the exact localized chapter that teaches it fully
- **AND** the learner can resume at the current unit's required checkpoint without installing or understanding the preview's advanced tooling

#### Scenario: Hygiene of the dependency evidence

- **WHEN** maintainers validate the prerequisite map
- **THEN** all paths are repository-relative stable paths and all concepts resolve to an existing section or checkpoint
- **AND** the evidence contains no absolute maintainer path, generated cache, learner data, credential, or stale proposed-only target

### Requirement: Chapter 11 separates foundational functions from higher-order programming

`chapter-11-functions/README.md` and its four localized siblings SHALL expose a foundational route that teaches function definition and invocation, parameters and arguments, positional and keyword calls, safe default values, `return`, implicit `None`, local scope, naming, docstrings, and single responsibility before any required use of callbacks or decorators. First-class functions, `Callable`, closures, decorators, timing, and pytest SHALL be an explicitly optional intermediate or advanced route.

#### Scenario: Happy path through the foundational route

- **WHEN** a learner knows lists, dictionaries, conditionals, and loops but has not used higher-order functions
- **THEN** the learner can define, call, test manually, and explain a small function with parameters and a returned value
- **AND** can complete the foundational checkpoint without `Callable`, closures, decorators, pytest, or a timing API

#### Scenario: Edge case for default values and `None`

- **WHEN** the foundational lesson compares an omitted optional argument, an explicit `None`, and an empty mutable collection
- **THEN** the example demonstrates a safe non-mutable default and explains the observable difference between returning a value and falling through without `return`
- **AND** the checkpoint includes the empty-input boundary

#### Scenario: Failure and recovery for an invalid call

- **WHEN** a learner calls a function with a missing, extra, or invalid argument in the expected-error exercise
- **THEN** the lesson identifies the meaningful diagnostic without promising version-unstable full text
- **AND** guides the learner to reconcile the call with the signature and rerun a successful case

#### Scenario: Advanced route remains optional

- **WHEN** the learner reaches first-class functions, callbacks, closures, or decorators
- **THEN** the chapter restates the foundational checkpoint prerequisite, estimates the additional session time, and gives an observable advanced outcome
- **AND** no later foundational chapter treats completion of this advanced route as mandatory unless it explicitly declares that prerequisite

#### Scenario: Localized function semantics

- **WHEN** Chapter 11 is reconciled across Spanish, Catalan, Swedish, and Arabic
- **THEN** public identifiers, signatures, return behavior, diagnostics, runnable classifications, exercises, hints, solutions, and route boundaries remain technically equivalent
- **AND** explanatory prose is natural in each language rather than a summary of canonical English

#### Scenario: Accessible explanation of data flow

- **WHEN** the chapter explains arguments entering and return values leaving a function
- **THEN** equivalent prose names the sequence in addition to any diagram or positional metaphor
- **AND** code, signatures, and output remain readable left-to-right inside Arabic right-to-left prose

### Requirement: Essential assessments include executable recovery

Every essential checkpoint in Chapters 01–12 SHALL trace each learning objective to prerequisite-ordered explanation, a prediction, a bounded runnable example or tested companion source, a guided TODO with a useful hint, happy and boundary behavior, one recoverable error, an explained solution, observable verification, a short rubric, and a closing reflection. A summary-only answer or final code without reasoning SHALL NOT satisfy the solution contract.

#### Scenario: Happy path assessment succeeds

- **WHEN** a learner completes an essential exercise with a normal input
- **THEN** the documented verification produces the stated meaningful behavior in CPython 3.11 or the unit's narrower declared tested matrix
- **AND** the rubric lets the learner check correctness, readability, error handling, verification, and their own explanation

#### Scenario: Edge input is exercised

- **WHEN** the exercise accepts an empty collection, empty string, boundary index, zero, or equivalent unit-specific boundary
- **THEN** the checkpoint states the expected behavior before the solution
- **AND** the explained solution connects that behavior to the concept being assessed

#### Scenario: Expected failure is recoverable

- **WHEN** an assessment intentionally triggers an error
- **THEN** its fence is classified `expected-error`, the stable diagnostic signal is documented, and the learner receives a concrete correction to apply
- **AND** a subsequent bounded run demonstrates recovery

#### Scenario: Runnable evidence is missing

- **WHEN** a block is called runnable but has neither direct execution evidence nor a valid tested companion-source reference
- **THEN** publication validation fails that claim
- **AND** maintainers reclassify the block accurately or add the missing executable evidence before release

#### Scenario: Localized assessment parity

- **WHEN** an essential assessment or recovery explanation changes in canonical English
- **THEN** objectives, TODOs, hints, cases, diagnostics, solution reasoning, rubric, and reflection are propagated semantically to all four localized siblings
- **AND** automated structural similarity alone does not mark any translation accepted

### Requirement: Learner-facing progression remains safe, accessible, and repository-clean

All added or corrected learning-route content SHALL follow `BOOK_STYLE.md`, use one hierarchical heading structure, descriptive links, simple tables or list alternatives, and prose equivalents for meaningful visuals. Examples SHALL be deterministic, bounded, safe to rerun, local or offline by default, and free of live credentials and learner personal data.

#### Scenario: Accessibility review of changed content

- **WHEN** a route, prerequisite section, exercise, table, or visual is changed
- **THEN** structural checks verify heading hierarchy, descriptive links, alt text where applicable, and a text/list equivalent for visual relationships
- **AND** human accessibility review remains pending until a competent reviewer signs off

#### Scenario: Arabic bidirectional content

- **WHEN** an Arabic unit is changed
- **THEN** it retains exactly one balanced outer `<div dir="rtl">` wrapper
- **AND** code, commands, paths, identifiers, output, and diagnostics remain legible and copyable left-to-right

#### Scenario: Unsafe example is proposed

- **WHEN** an exercise would use a public target, real secret, learner identity, destructive path, unbounded loop, fixed external wait, or unverified compatibility claim
- **THEN** the content gate rejects it
- **AND** recovery replaces it with fake data, a disposable path, a local service, explicit resource bounds, or an accurately scoped tested claim

#### Scenario: Repository hygiene after verification

- **WHEN** route examples and assessment tests finish successfully or fail as expected
- **THEN** temporary directories and child processes are cleaned
- **AND** no `.venv`, cache, bytecode, wheel, sdist, native build output, credential, certificate generated during testing, coverage file, or learner data remains in the source tree

#### Scenario: Root indexes are integrated atomically

- **WHEN** course routes or navigation change
- **THEN** all six root indexes are updated only after every target exists
- **AND** root `README.md` and `README.en.md` remain byte-for-byte identical while Chapters 23, 24, and 25 stay ordered before the appendices
