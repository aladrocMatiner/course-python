## Why

The published route is structurally valid, but beginners still meet three undeclared prerequisites—creating and running a file, scalar truth/absence, and importing the standard library—and the course has no dedicated bridge for iteration/generators, gradual typing, or a longitudinal practical assessment. Because all current publication reviews are still pending, closing these gaps now avoids invalidating completed human approvals later.

## What Changes

- Extend Chapters 1, 2, and 7 in English, Spanish, Catalan, Swedish, and Arabic with prerequisite-ordered subsections for the file/run/debug loop, `bool`/`None`/comparisons/safe floating-point comparison, and the standard-library import model.
- Add `chapter-26-iteration-generators` with essential, professional, and optional advanced routes covering comprehensions, `enumerate`/`zip`, the iterable/iterator protocol, exhaustion, generator expressions, `yield`, lazy bounded pipelines, recovery, exercises, and tested companion code.
- Add `chapter-27-python-typing` with gradual typing, annotations versus runtime validation, unions and narrowing, typed collections, `Callable`, `TypedDict`, structural `Protocol`, basic generics, checker diagnostics, recovery, exercises, and a reproducible companion contract.
- Add `chapter-28-professional-capstone` as one staged local project that reuses Chapters 12–20: a domain model, SQLite repository, CLI, configuration, logging, tests, packaging metadata, artifact verification, and optional bounded HTTP/async adapters without introducing a web framework or public service.
- Publish all five language siblings for Chapters 26–28, update all six root indexes atomically, and extend the acyclic route/checkpoint map without renaming existing paths or forcing hero content into the essential route.
- Expand publication/parity evidence from 27 canonical units and 108 locale records to 30 canonical units and 120 locale records. New human linguistic, technical, accessibility, bidi, provenance, and publication decisions remain pending.
- Coordinate with `restore-multilingual-content-parity`: this change depends on its completed evidence-schema/packet Tasks 1.4–1.5 and owns the additive 30/120 topology migration; the restoration change retains ownership of reviews for the original 27 units.

### Non-goals

- No Django/FastAPI, data-science, GUI, public deployment, offensive-security, general threads/processes course, or profiling curriculum.
- No renaming or renumbering of Chapters 01–25 or the appendices.
- No automatic linguistic, pedagogical, accessibility, bidi, provenance, license, or release approval.
- No upload to PyPI or any production package index.

### Migration and rollback

- Create the three complete five-language units and their verified companions before publishing navigation or topology changes.
- Reconcile the partitioned evidence store through its explicit write path so existing compatible human fields are preserved and only the three new units begin pending.
- Roll back by removing the new index/checkpoint/topology entries and the three additive unit trees together; existing paths and the original 27-unit evidence remain intact.

### Definition of done

- The declared graph is acyclic and every new required objective maps to explanation, prediction, bounded evidence, guided work, recovery, solution, checkpoint, rubric, and reflection.
- All 30 canonical and 120 localized paths exist, root English mirrors are byte-identical, Arabic wrappers are balanced, and the parity store validates at 30/120 without manufactured approvals.
- Companion tests, artifact verification, the full tooling suite, relevant quality profiles, strict OpenSpec validation, hygiene, and `git diff --check` complete with only explicitly documented human gates pending.

## Capabilities

### New Capabilities

- `close-core-python-prerequisite-gaps`: Beginner-safe file execution, scalar truth/absence/comparison, and standard-library import bridges across all languages.
- `teach-python-iteration-generators`: Prerequisite-ordered comprehensions, iterables, iterators, generators, bounded lazy processing, and assessment.
- `teach-python-gradual-typing`: Gradual typing and static-analysis contracts from annotations through structural protocols and basic generics.
- `provide-longitudinal-python-capstone`: A staged, local-first project that traces practical and systems outcomes to earlier checkpoints and verifies a distributable pure-Python artifact.

### Modified Capabilities

- `maintain-course-learning-progression`: Add Chapters 26–28 to explicit alternate pedagogical routes, prerequisites, outcomes, checkpoints, and multilingual navigation.
- `partitioned-parity-evidence`: Expand the exact discovered publication topology and review packets from 27/108 to 30/120 while preserving existing evidence.
- `complete-published-quality-evidence`: Require the three new units and their root navigation in publication evidence and final sign-off inputs.

## Impact

- Content: Chapters 1, 2, and 7; three new chapter directories with five Markdown siblings and companion sources/tests; all six root indexes.
- Curriculum and evidence: `tools/curriculum_map.toml`, book configuration, parity index/source/locale leaves, root publication evidence, and pending publication sign-off input.
- Tooling/tests: only additive discovery/topology expectations and companion verification; generic validators remain domain-neutral and read-only.
- Dependencies: CPython 3.11+ and the standard library for essential examples; isolated packaging verification uses the already declared local build inputs and never publishes an artifact.
- Risks: translation/review load, route cognitive load, stale evidence, packaging environment availability, and active-change overlap. The design must keep routes independently stoppable, preserve human review boundaries, and make rollback additive.
