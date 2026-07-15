## ADDED Requirements

### Requirement: Chapter 26 provides three independently completable iteration routes

The course SHALL provide `chapter-26-iteration-generators/README.md` plus
`README.es.md`, `README.ca.md`, `README.sv.md`, and `README.ar.md` as a
prerequisite-ordered bridge from familiar loops and functions to lazy
iteration. Its required entry checkpoint SHALL be the foundational Chapter 11
checkpoint; numerical catalogue placement after Chapter 25 SHALL NOT make
networking, C++, or Rust a prerequisite.

The chapter SHALL publish these independently stoppable routes with estimated
multi-session time, observable outcome, entry check, completion criterion, and
continuation:

- an **essential route** for readable list, dictionary, and set
  comprehensions, `enumerate`, and `zip` on small materialized inputs;
- a **professional route** for iterable versus iterator, `iter`, `next`,
  exhaustion, `StopIteration`, one-shot consumption, and recovery with a new
  iterator; and
- an **optional advanced route** for generator expressions, generator
  functions with `yield`, bounded lazy pipelines, delegation, delayed errors,
  and cleanup.

Every route SHALL follow the repository learning loop: objectives and
prerequisites, motivating context, minimal theory, prediction, bounded
runnable evidence, guided TODO and hint, normal and boundary behavior,
recoverable failure, common mistakes, explained solution, observable
checkpoint, rubric, and reflection. Async iterators, third-party streaming
frameworks, performance benchmarking, and custom class-based iterator depth
SHALL NOT be required to complete the chapter.

#### Scenario: Happy path through the essential route

- **WHEN** a learner has completed the Chapter 11 foundational checkpoint and follows the Chapter 26 essential sequence
- **THEN** the learner can transform and pair small collections, observe the result, and explain the equivalent ordinary loop
- **AND** no generator, custom iterator class, exception handler, native toolchain, or third-party package is required

#### Scenario: Edge case for a learner who stops early

- **WHEN** the learner completes the essential checkpoint but does not select the professional or advanced route
- **THEN** the chapter names a safe continuation that does not assume iterator-protocol or generator mastery
- **AND** advanced sections do not silently become prerequisites of an earlier course route

#### Scenario: Failure from a missing prerequisite

- **WHEN** a learner cannot yet predict a `for` loop, call a foundational function, or interpret a returned collection
- **THEN** the route entry check links to the exact localized Chapter 10 or Chapter 11 checkpoint to revisit
- **AND** the lesson does not conceal the missing concept inside a solution

#### Scenario: Recovery for a returning learner

- **WHEN** a returning learner demonstrates the named entry and route checkpoint behavior
- **THEN** the route map permits entry at the next route without requiring all earlier prose to be reread
- **AND** it identifies the exact self-assessment used as readiness evidence

#### Scenario: Route order remains acyclic

- **WHEN** Chapter 26 is added to `tools/curriculum_map.toml`
- **THEN** its concepts and checkpoints resolve to existing stable paths, all required edges point from taught prerequisites to later uses, and graph validation reports no cycle
- **AND** the alternate pedagogical route does not rename or renumber Chapters 01 through 25

### Requirement: The essential route teaches readable comprehensions, enumeration, and strict pairing

The essential route SHALL derive each list, dictionary, and set comprehension
from an already understood `for` loop before using compact syntax. It SHALL
teach expression, target, iterable, and an optional single condition in that
dependency order; nested or side-effecting comprehensions SHALL be moved out
of essential work or rewritten as ordinary loops. Examples SHALL explain that
list and dictionary results preserve their documented insertion order, while
set order SHALL NOT be used as output or correctness evidence.

The route SHALL teach `enumerate(values, start=1)` instead of a manually
managed display counter and `zip(left, right, strict=True)` when equal lengths
are a correctness contract. It SHALL explain that ordinary `zip` stops at the
shorter iterable and SHALL make that truncation deliberate rather than an
unnoticed data-loss pattern. Required examples SHALL include empty input,
duplicate set values, and unequal pair lengths.

#### Scenario: Happy path builds a list comprehension

- **WHEN** the learner runs `doubled = [score * 2 for score in [3, 5, 8]]` and prints the result
- **THEN** output is exactly `[6, 10, 16]` followed by a newline
- **AND** the lesson traces the expression, target, iterable, and append-equivalent loop in execution order

#### Scenario: Happy path enumerates human-facing positions

- **WHEN** the learner enumerates `["Noor", "Frej"]` with `start=1`
- **THEN** the observed pairs are `(1, "Noor")` and `(2, "Frej")` in that order
- **AND** the explanation distinguishes the display position from a collection's zero-based index

#### Scenario: Edge case preserves empty and duplicate semantics

- **WHEN** an empty iterable is used in each taught comprehension and repeated values are used in a set comprehension
- **THEN** the list, dictionary, and set results are empty for empty input, while the set contains each equal value only once
- **AND** no assertion depends on a set's rendered order

#### Scenario: Failure from unequal strict pairing

- **WHEN** `zip(["Noor", "Frej"], [7], strict=True)` is fully consumed in the expected-error example
- **THEN** it terminates with the stable exception category `ValueError` without requiring exact version-specific diagnostic text
- **AND** the lesson explains that the mismatch is detected during iteration rather than necessarily when `zip` is constructed

#### Scenario: Recovery from unequal pairing

- **WHEN** the learner corrects the source lengths or explicitly chooses documented truncation for a domain that permits it
- **THEN** the rerun produces the stated pairs and the learner explains whether unequal trailing values are rejected or intentionally ignored
- **AND** the solution does not silently remove `strict=True` from a task whose contract requires equal lengths

#### Scenario: Comprehension readability is the governing boundary

- **WHEN** a proposed comprehension contains nested loops, several conditions, assignment expressions, exception handling, or side effects
- **THEN** the essential solution uses named intermediate values and ordinary loops or moves the depth to optional material
- **AND** the rubric rewards explainable behavior rather than minimum line count

### Requirement: The professional route makes the iterable and iterator protocol observable

The professional route SHALL distinguish an iterable that can produce an
iterator from the stateful iterator that produces successive values. It SHALL
demonstrate `iter(iterable)`, `next(iterator)`, `next(iterator, default)`, the
stable `StopIteration` exhaustion signal, and the way a `for` loop consumes
until exhaustion. It SHALL show that `iter(existing_iterator) is
existing_iterator`, that a consumed iterator is one-shot, and that calling
`iter` on a reusable collection can create a fresh traversal.

The lesson SHALL distinguish iterator state from source collection state and
SHALL warn against changing a collection structurally while iterating unless a
specific behavior has been taught and tested. An expected-error block SHALL
observe exhaustion; its recovery SHALL use a fresh iterator or the default
argument to `next`, not broad exception swallowing.

#### Scenario: Happy path consumes an iterator step by step

- **WHEN** the learner creates `cursor = iter(["A", "B"])` and calls `next(cursor)` twice
- **THEN** the observations are `A` and then `B`
- **AND** the learner can identify that progress belongs to `cursor`, not to an integer index they manage

#### Scenario: Edge case uses an exhaustion default

- **WHEN** an empty iterator is passed to `next(cursor, "done")`
- **THEN** the result is exactly `done` without an exception
- **AND** the lesson states that the default is ambiguous when the same value is valid data and shows a domain-appropriate sentinel when needed

#### Scenario: Failure after one-shot exhaustion

- **WHEN** the expected-error exercise calls `next` again after consuming both values from `cursor`
- **THEN** it terminates with `StopIteration`
- **AND** the evidence asserts the exception category rather than unstable traceback wording

#### Scenario: Recovery creates a deliberate traversal

- **WHEN** the learner needs to traverse the original list again after exhausting `cursor`
- **THEN** the recovered example obtains a new iterator with `iter(original_values)` or uses a new `for` loop and observes `A`, then `B`
- **AND** it does not imply that an arbitrary generator can be rewound

#### Scenario: Mutation during traversal is not normalized

- **WHEN** a proposed exercise adds or removes elements from the same collection being traversed
- **THEN** the required route replaces it with iteration over an intentional snapshot or accumulation into a separate result
- **AND** any optional mutation example states and verifies its exact collection-specific contract

### Requirement: The advanced route teaches generators as bounded, one-shot computations

The optional advanced route SHALL teach generator expressions before generator
functions, then show that calling a function containing `yield` returns a
generator whose body advances only when consumed. It SHALL cover yielded
values, generator exhaustion, `return` as normal termination, errors that arise
later during consumption, `yield from` delegation, and `try/finally` cleanup at
a declared prerequisite point. It SHALL state that explicitly raising
`StopIteration` inside a generator body is incorrect on the declared CPython
runtime and SHALL recover by using `return`.

Lazy examples SHALL be locally bounded by finite input or an explicit limiter
such as `itertools.islice`. The canonical observation SHALL include a squares
pipeline whose first five values are exactly `[0, 1, 4, 9, 16]`. The chapter
SHALL explain that laziness can avoid materializing all intermediate values but
does not make an infinite source safe if the consumer requests an unbounded
`list`, retains every result, performs unbounded work, or owns a resource that
is never closed. It SHALL make no universal speed or memory-complexity claim
without measured, current evidence and stated inputs.

#### Scenario: Happy path yields a finite countdown

- **WHEN** the learner consumes `countdown(3)` from the tested companion
- **THEN** it yields exactly `3`, `2`, and `1`, then terminates normally
- **AND** a second traversal requires a newly created generator

#### Scenario: Edge case bounds an infinite source

- **WHEN** the learner combines an intentionally infinite integer source with `itertools.islice(..., 5)` and squares each consumed value
- **THEN** the process terminates and materializes exactly `[0, 1, 4, 9, 16]`
- **AND** the unbounded form is explanatory non-runnable text rather than a command the learner is told to execute

#### Scenario: Failure is delayed until consumption

- **WHEN** a generator is constructed successfully but encounters invalid data on a later `next` call
- **THEN** the expected-error evidence identifies the value already yielded, the stable exception category, and the consumption step that failed
- **AND** the lesson does not claim that generator construction validated every future item

#### Scenario: Recovery from an explicit StopIteration

- **WHEN** an expected-error generator explicitly raises `StopIteration` in its body on the declared CPython interpreter
- **THEN** the lesson identifies the resulting stable `RuntimeError` category and replaces the explicit raise with `return`
- **AND** the recovered generator terminates normally when consumed

#### Scenario: Cleanup runs after early termination

- **WHEN** the advanced cleanup example stops before consuming every value and explicitly closes the generator
- **THEN** its bounded `finally` evidence runs exactly once and releases only the local fake resource owned by that generator
- **AND** the lesson states that garbage-collection timing is not a portable cleanup strategy

#### Scenario: Unsafe unbounded consumption is rejected

- **WHEN** a runnable block would materialize an infinite generator, loop without an explicit bound, retain unbounded learner input, or wait on an external source
- **THEN** content verification rejects or reclassifies the block
- **AND** recovery adds a finite fixture, item/time bound, local source, and deterministic completion condition

### Requirement: Companion sources and assessments provide deterministic executable evidence

Canonical executable behavior SHALL live in
`chapter-26-iteration-generators/examples/iteration_pipeline.py`, with tests in
`chapter-26-iteration-generators/examples/tests/test_iteration_pipeline.py`
and an importable test package marker when required by the selected standard
library test command. The companion SHALL expose small documented contracts
for strict pairing, a finite countdown, bounded square production, and
delegation; it SHALL NOT perform work, consume input, start a process, or write
a file merely on import.

From the repository root, the standard-library-only verification command SHALL
be:

```text
python -m unittest discover -s chapter-26-iteration-generators/examples/tests -t chapter-26-iteration-generators/examples -p 'test_*.py'
```

Tests SHALL cover normal, empty, unequal-length, invalid-bound, exhaustion,
delayed-failure, recovery, and cleanup behavior and SHALL complete under the
repository's bounded timeout. `chapter-26-iteration-generators/TRACEABILITY.md`
SHALL map every required objective and checkpoint to its canonical section,
example, TODO/hint, solution, and exact test or executable evidence. Markdown
excerpts whose behavior is owned by the companion SHALL use registered exact
`source-ref` metadata; illustrative, TODO, output, and expected-error blocks
SHALL retain truthful classifications.

#### Scenario: Happy path verifies the companion

- **WHEN** the documented command runs with the repository's declared CPython 3.11-or-newer evidence interpreter and all prerequisites are present
- **THEN** every Chapter 26 companion test passes with exit status zero within the configured timeout
- **AND** the tested outputs match the snippets bound by source references

#### Scenario: Edge behavior is part of the assessment

- **WHEN** the companion receives empty inputs, duplicate values, a zero item limit, or an already exhausted iterator
- **THEN** tests assert the explicitly documented result for each boundary
- **AND** the learner checkpoint asks for at least one prediction and explanation rather than only a green test run

#### Scenario: Failure evidence remains truthful

- **WHEN** a negative fixture triggers `ValueError`, `StopIteration`, `RuntimeError`, or another declared stable category
- **THEN** the test checks the category and relevant semantic state without golden-copying the complete interpreter diagnostic
- **AND** the companion's normal verification still demonstrates the repaired case

#### Scenario: Source reference becomes stale

- **WHEN** a companion region changes without the matching Markdown excerpt and evidence digest being reconciled
- **THEN** source-reference validation fails with the owning unit and reference
- **AND** maintainers update the lesson or companion coherently and rerun narrow verification before translation

#### Scenario: Generic and explicit verification remain separated

- **WHEN** book-wide validation runs without selecting the explicit `learning-bridges` companion check
- **THEN** generic validation checks Markdown, registered references, navigation, localization structure, and eligible snippets without silently executing arbitrary companion code
- **AND** implementation completion requires the explicit companion check in addition to generic validation

### Requirement: Chapter 26 publication is multilingual, accessible, provenance-safe, and clean

All five Chapter 26 siblings SHALL preserve semantic parity for objectives,
route boundaries, prerequisites, terms, code contracts, identifiers, commands,
outputs, predictions, examples, edge cases, warnings, expected errors,
recoveries, exercises, hints, solutions, checkpoints, rubrics, reflection, and
source references. The language selector SHALL keep the order `English →
Español → Català → Svenska → العربية`; Arabic SHALL have exactly one
balanced outer `<div dir="rtl">`, while code, commands, paths, identifiers,
operators, output, and diagnostics remain legible left-to-right.

Headings SHALL be hierarchical, links descriptive and language-matched, tables
simple with a list alternative where needed, and every meaningful visual SHALL
have alt text plus an equivalent prose sequence. Meaning SHALL NOT depend only
on color, arrow direction, icon, or visual position. Original examples SHALL
be preferred; every adaptation SHALL have current source, license, notice, and
compatibility evidence before publication.

The chapter SHALL be linked from root navigation only after all five targets,
companions, source references, and declared automated checks exist. Automated
shape, execution, and digest evidence SHALL NOT manufacture linguistic,
technical/pedagogical, accessibility, Arabic bidi, provenance, license, or
publication acceptance. Verification SHALL be local/offline, bounded, and
repository-clean.

#### Scenario: Accessible protocol explanation

- **WHEN** a learner cannot use a state diagram or syntax highlighting
- **THEN** prose describes creation, each consumption step, exhaustion, recreation, and cleanup in order
- **AND** all runnable, output, TODO, illustrative, and expected-error roles are identified textually

#### Scenario: Localized technical behavior remains equivalent

- **WHEN** Spanish, Catalan, Swedish, or Arabic content is compared with current canonical English
- **THEN** each route teaches and assesses the same observable behavior, bounds, failure categories, recovery, safety constraints, and completion criteria
- **AND** structural similarity alone is not treated as proof of fluent or pedagogically equivalent translation

#### Scenario: Arabic bidi review remains a human gate

- **WHEN** automated checks find one balanced RTL wrapper and valid fences in `README.ar.md`
- **THEN** rendered Arabic code, punctuation, commands, iterator expressions, and traceback fragments still await competent bidi/accessibility review
- **AND** no automation records that human decision as accepted

#### Scenario: Provenance evidence is missing

- **WHEN** a lesson, exercise, diagram, dataset, or substantial explanation derives from a third-party source without a verified compatible license and required notice
- **THEN** publication of the affected material remains blocked
- **AND** maintainers replace it with original work or obtain and record competent provenance and license acceptance

#### Scenario: Navigation publication is atomic

- **WHEN** any Chapter 26 language target, companion file, or required automated evidence is absent
- **THEN** none of the six root indexes publishes the new link
- **AND** once all targets are ready, navigation is updated atomically while `README.md` and `README.en.md` remain byte-identical and Chapters 01 through 25 retain their stable paths

#### Scenario: Repository hygiene after Chapter 26 verification

- **WHEN** runnable blocks, expected failures, companion tests, localization checks, and review-packet generation finish
- **THEN** temporary iterables, subprocesses, and fake resources are closed or removed
- **AND** no `__pycache__`, `.pyc`, virtual environment, coverage file, generated report, build artifact, credential, learner data, absolute maintainer path, or unresolved recovery directory remains in the repository
