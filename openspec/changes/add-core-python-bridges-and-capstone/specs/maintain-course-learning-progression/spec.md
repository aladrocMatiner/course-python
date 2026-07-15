## MODIFIED Requirements

### Requirement: Published course routes preserve stable content links

The course SHALL publish a course-level route map in root `README.md`, `README.en.md`, `README.es.md`, `README.ca.md`, `README.sv.md`, and `README.ar.md` without renaming any existing chapter or appendix directory, and SHALL retain the numerical chapter table of contents as the stable reference order.

The English route SHALL define these independently completable paths and localized indexes SHALL preserve their meaning:

- **Essential foundations:** Chapters 01–02, the essential checkpoints of Chapters 03–07, Chapters 08–10, the foundational route of Chapter 11, the essential route of Chapter 26, and Chapter 12;
- **Practical Python:** Chapters 13–18 after essential foundations, with Chapter 18 as a complete stopping point;
- **Systems Python:** Chapters 19–23 after the practical route, with Chapter 22 as an earlier safe stopping point;
- **Gradual typing bridge:** Chapter 27 after Chapters 15, 18, 22, and the Chapter 26 essential bridge, with its checker route optional;
- **Optional native hero routes:** Chapter 24 for Python with C++ and Chapter 25 for Python with Rust, each selectable independently after Chapters 15, 16, 18, and the Chapter 27 typing checkpoint;
- **Longitudinal capstone stages:** Chapter 28 foundation, practical, systems, and packaging stages, each available only after its named prior checkpoint and each independently stoppable; and
- **Appendix routes:** each appendix placed after the chapters named by that appendix's prerequisite contract.

Each route SHALL name its prerequisite, exact non-numerical learning sequence where it differs from catalogue order, estimated multi-session duration, observable outcome, completion criteria, and a safe continuation or stopping point.

#### Scenario: Happy path through essential foundations

- **WHEN** a beginner starts from a root index and follows the essential-foundations route
- **THEN** every required checkpoint, including the Chapter 26 essential bridge, is reachable using only concepts already taught in an earlier required checkpoint
- **AND** optional professional or hero material can be skipped without losing the next essential continuation link

#### Scenario: Edge case for a returning learner

- **WHEN** a learner already meets the stated completion criteria for a route stage
- **THEN** the route map permits entry at the next stage and names the exact checkpoint used to self-assess readiness
- **AND** does not require rereading optional previews or earlier Chapter 28 stages as if they were prerequisites

#### Scenario: Failure when a route target is unavailable

- **WHEN** a root route or table-of-contents entry would point to a missing unit, companion checkpoint, or language sibling
- **THEN** publication validation fails before the link is added
- **AND** the existing root indexes and stable links remain unchanged

#### Scenario: Recovery after a route correction

- **WHEN** a prerequisite audit changes a route transition but no public path migration is approved
- **THEN** maintainers update route prose, checkpoint edges, and localized links rather than renaming or renumbering directories
- **AND** rerun navigation, mirror, and prerequisite checks before publishing

#### Scenario: Localized route navigation

- **WHEN** a learner reads a Spanish, Catalan, Swedish, or Arabic root route
- **THEN** every in-course route link targets the corresponding localized sibling
- **AND** the non-numerical route order, outcomes, completion criteria, capstone stages, and optional boundaries are semantically equivalent to canonical English

#### Scenario: Accessible route presentation

- **WHEN** route choices are rendered on a narrow screen or read with assistive technology
- **THEN** the same sequence and dependencies are available as descriptive text or a simple list
- **AND** no decision depends only on a table position, color, icon, arrow, or visual layout

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

- **WHEN** an exercise would use a public target, real secret, learner identity, destructive path, unbounded loop, fixed external wait, package-index upload, or unverified compatibility claim
- **THEN** the content gate rejects it
- **AND** recovery replaces it with fake data, a disposable path, a local service, explicit resource bounds, a local artifact simulation, or an accurately scoped tested claim

#### Scenario: Repository hygiene after verification

- **WHEN** route examples, checker evidence, package builds, and assessment tests finish successfully or fail as expected
- **THEN** temporary directories and child processes are cleaned
- **AND** no `.venv`, cache, bytecode, wheel, sdist, native build output, credential, generated certificate, coverage file, or learner data remains in the source tree

#### Scenario: Root indexes are integrated atomically

- **WHEN** course routes or navigation change
- **THEN** all six root indexes are updated only after all five siblings and companion targets for Chapters 26–28 exist
- **AND** root `README.md` and `README.en.md` remain byte-for-byte identical while Chapters 23–28 stay ordered before the appendices
