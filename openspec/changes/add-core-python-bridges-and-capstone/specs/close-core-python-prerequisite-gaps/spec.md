## ADDED Requirements

### Requirement: Chapter 1 teaches the complete edit, save, run, diagnose, and rerun loop

`chapter-01-introduction/README.md` and its exact Spanish, Catalan, Swedish,
and Arabic siblings SHALL teach a first-time learner how an editor, a saved
`.py` source file, a shell working directory, the selected Python interpreter,
standard output, and the interactive REPL differ before Chapter 2 requires
that knowledge. The essential route SHALL have the learner create `hello.py`
in a learner-owned disposable working directory, save
`print("Hello, Python!")`, run `python hello.py` or the interpreter spelling
established by the Chapter 1 setup check, and observe exactly:

```text
Hello, Python!
```

The lesson SHALL explain how to open a terminal in the file's directory,
verify the filename including the `.py` suffix, leave the REPL before entering
a shell command, and rerun the same file after each edit. It SHALL include one
truthfully classified `NameError` exercise caused by the misspelled built-in
name `pritn`, teach the learner to locate the source path and line, read the
final exception type and message without depending on a version-specific full
traceback, correct the spelling to `print`, save, and observe the successful
output. No function, variable, conditional, exception handler, test framework,
package, or editor-specific run button SHALL be a prerequisite of this loop.

#### Scenario: Happy path from source file to output

- **WHEN** a learner saves the documented `hello.py` in the working directory and invokes it with the interpreter command established by the setup check
- **THEN** the process exits successfully and standard output is exactly `Hello, Python!` followed by a newline
- **AND** the learner can identify the editor, source file, shell command, interpreter, and output as distinct parts of the run loop

#### Scenario: Edge case for a filename or directory containing spaces

- **WHEN** the learner uses an editor or working-directory path containing spaces
- **THEN** the chapter shows a copyable, platform-appropriate quoted path or a change-directory workflow that preserves the complete path
- **AND** the learner does not rename a personal or system directory merely to satisfy the exercise

#### Scenario: Failure from the wrong working directory

- **WHEN** Python cannot open `hello.py` because the shell is in a different directory or the file was saved with an unintended suffix
- **THEN** the lesson identifies the stable fact that the requested source path was not found rather than promising exact platform-specific diagnostic text
- **AND** it does not tell the learner to reinstall Python, elevate privileges, or move the file into a system directory

#### Scenario: Recovery from the first traceback

- **WHEN** the expected-error version containing `pritn("Hello, Python!")` terminates with `NameError`
- **THEN** the learner uses the reported file, line, exception type, and misspelled name to change only `pritn` to `print`, saves the file, and reruns it
- **AND** the recovered run exits successfully with the documented output

#### Scenario: Accessible distinction between shell, source, and output

- **WHEN** the subsection is read without syntax colors or an editor screenshot
- **THEN** prose and truthful fence labels identify which text belongs in `hello.py`, which text is a shell command, which text is output, and which block is expected to fail
- **AND** instructions do not depend on a button's color, icon, or visual position

#### Scenario: Localized run-loop contract

- **WHEN** the subsection is implemented in Spanish, Catalan, Swedish, or Arabic
- **THEN** it preserves the same commands, filename, code behavior, expected-error signal, repair, output, checkpoint, and safe directory contract while explaining them naturally in that language
- **AND** every prerequisite and continuation link targets the reader's matching language sibling

#### Scenario: Verification hygiene for the first program

- **WHEN** maintainers execute the runnable and expected-error examples
- **THEN** execution is bounded, offline, non-privileged, and uses a disposable directory or an isolated verifier
- **AND** no bytecode, virtual environment, editor state, absolute maintainer path, credential, or learner data remains in the repository

### Requirement: Chapter 2 establishes truth, absence, comparison, and safe floating-point observations

`chapter-02-variables/README.md` and its four localized siblings SHALL extend
the essential scalar route before any required conditional with `bool`, the
literal values `True` and `False`, `None` as an explicit absence sentinel,
comparison expressions and their Boolean results, and the operators `==`,
`!=`, `<`, `<=`, `>`, and `>=`. The lesson SHALL distinguish value equality
from the identity test `value is None`, distinguish `None` from `0`, `""`, and
`False`, and state that a comparison produces a Boolean without requiring an
`if` statement.

The required route SHALL demonstrate that binary floating-point arithmetic can
make `0.1 + 0.2 == 0.3` evaluate to `False`, and SHALL teach a tolerance-based
comparison whose observed result is `True`. An absolute-difference expression
using only already introduced built-ins SHALL keep the essential checkpoint
independent of imports. `math.isclose` SHALL be shown as a clearly labelled,
copyable optional preview with its `import math` line, named tolerances, and a
localized forward link to the Chapter 7 import bridge; it SHALL NOT be
described as exact decimal arithmetic. If `Decimal` is named as later
enrichment, it SHALL NOT be required or used without teaching its string-input
contract and import prerequisite.

#### Scenario: Happy path observes comparison results without conditionals

- **WHEN** the learner runs the required scalar example containing `print(3 < 5)`, `print(3 == 3)`, and `print(None is None)`
- **THEN** it exits successfully and prints three observable `True` values in the documented order
- **AND** the explanation connects each result to the comparison or identity expression that produced it

#### Scenario: Edge case distinguishes absence from false-like values

- **WHEN** the learner compares `None` with `0`, an empty string, and `False`
- **THEN** the lesson shows that none of those three values is the absence sentinel and uses `is None` for that decision
- **AND** it separately explains that Boolean/numeric equality such as `False == 0` does not make the values interchangeable in a domain model

#### Scenario: Edge case uses an explicit floating-point tolerance

- **WHEN** the learner evaluates `0.1 + 0.2 == 0.3` and then compares the absolute difference with the chapter's small positive tolerance
- **THEN** the first observation is `False` and the tolerance-based observation is `True` on the declared CPython evidence interpreter
- **AND** the lesson explains that the tolerance must be selected for the problem rather than copied as a universal constant

#### Scenario: Failure from ordering incompatible scalar types

- **WHEN** the expected-error example evaluates `3 < "5"`
- **THEN** it terminates with the stable signal `TypeError` without requiring an exact version-specific message
- **AND** the text explains that ordered comparisons require compatible meanings rather than implying that Python silently converts the string

#### Scenario: Recovery after an incompatible comparison

- **WHEN** the learner repairs the expected-error example by deliberately comparing two integers or two strings
- **THEN** the recovered expression produces the documented Boolean and the learner explains why the chosen types now have a common ordering
- **AND** the recovery does not introduce an undeclared `try`, function, or validation helper

#### Scenario: Optional `math.isclose` preview remains skippable

- **WHEN** a learner has not yet studied imports
- **THEN** the chapter provides the already taught absolute-difference path for the essential checkpoint and labels `import math` plus `math.isclose(...)` as **Optional preview**
- **AND** skipping that preview does not block Chapter 3 or any Chapter 2 assessment item

#### Scenario: Accessible and localized scalar semantics

- **WHEN** the new scalar material is rendered or translated
- **THEN** code, operators, literals, output order, expected-error classification, tolerance meaning, TODO, hint, solution, rubric, and reflection remain semantically equivalent and readable without color
- **AND** Arabic keeps code, operators, commands, and output left-to-right inside its single outer right-to-left wrapper

#### Scenario: Scalar-example hygiene

- **WHEN** maintainers verify the required scalar and expected-error blocks
- **THEN** the examples are deterministic, bounded, standard-library-only, and make no claim that tolerance comparison is suitable for money or every numerical domain
- **AND** verification leaves no cache, bytecode, environment, generated report, credential, personal data, or edited learner file in source control

### Requirement: Chapter 7 introduces imports immediately before the first required standard-library use

`chapter-07-queues/README.md` and its four localized siblings SHALL introduce
the import model before the first required `collections.deque` example. The
bridge SHALL explain, in prerequisite-ordered plain language, that a module is
loaded by the selected interpreter; that the standard library ships with the
declared Python installation; that `import collections` requires qualified
access as `collections.deque`; and that `from collections import deque` binds
the selected public name directly. It SHALL distinguish standard-library,
local, and third-party modules without asking the learner to install
`collections` with `pip`, while linking package design to localized Chapter 15
as later depth.

The bridge SHALL show `python -m module_name` as an interpreter-bound way to
execute an importable local module from its parent working directory. A small
`queue_demo.py` using `from collections import deque` SHALL be runnable both as
`python queue_demo.py` and, from that directory, `python -m queue_demo`, with
the same documented queue result. The lesson SHALL warn that local files or
directories named `collections.py`, `typing.py`, `random.py`, or another
imported module can shadow the intended module. Recovery SHALL inspect and
rename only the learner-owned conflicting source, restart the process, and
rerun; it SHALL NOT delete or modify the Python installation.

#### Scenario: Happy path imports and runs a standard-library queue

- **WHEN** the learner runs the required example `from collections import deque` followed by `print(deque(["A", "B"]).popleft())`
- **THEN** it exits successfully and prints exactly `A` followed by a newline
- **AND** the learner can state that `deque` came from the installed standard-library module `collections`

#### Scenario: Equivalent qualified import form

- **WHEN** the learner changes the example to `import collections` and constructs `collections.deque(["A", "B"])`
- **THEN** queue behavior and output remain equivalent
- **AND** the lesson explains why bare `deque(...)` is not bound by `import collections`

#### Scenario: Edge case executes the local module with `-m`

- **WHEN** `queue_demo.py` is saved in the current learner-owned directory and the learner runs `python -m queue_demo` from its parent import location
- **THEN** the selected interpreter executes the module once and produces the same declared output as `python queue_demo.py`
- **AND** the lesson does not generalize this single-file example into unintroduced package-relative-import rules

#### Scenario: Failure from an unavailable or misspelled module

- **WHEN** an expected-error observation imports a deliberately nonexistent course module
- **THEN** it reports the stable exception category `ModuleNotFoundError` without promising the complete environment-dependent diagnostic
- **AND** the lesson first checks spelling, working directory, and whether the module is standard-library/local/third-party instead of immediately installing an arbitrary package

#### Scenario: Failure from accidental local shadowing

- **WHEN** import diagnostics show that a learner-owned file or directory has the same name as the intended module
- **THEN** the chapter identifies shadowing as a source-resolution problem and shows how to inspect the conflicting local path
- **AND** it does not advise deleting a standard-library file, using administrator privileges, or clearing unrelated global caches

#### Scenario: Recovery from shadowing

- **WHEN** the learner renames the conflicting local source to a domain-specific name and starts a fresh interpreter process from the intended working directory
- **THEN** `from collections import deque` resolves to the standard library and the queue example again prints `A`
- **AND** any cleanup is limited to artifacts created inside the disposable exercise directory

#### Scenario: Accessible import explanation

- **WHEN** the import bridge is read with a screen reader or without a diagram
- **THEN** prose names the resolution sequence, namespace difference, command location, and recovery steps in order
- **AND** meaning does not depend on arrows, indentation color, an editor tree icon, or the visual position of a filename

#### Scenario: Localized import contract

- **WHEN** the Chapter 7 bridge is translated
- **THEN** module names, Python identifiers, commands, outputs, failure categories, safety warning, and Chapter 15 link retain their technical contract across all five languages
- **AND** the explanations are fluent rather than reduced to a heading-equivalent summary

#### Scenario: Import-verification hygiene

- **WHEN** maintainers verify normal, `-m`, missing-module, and shadowing cases
- **THEN** the verifier uses an isolated temporary directory, a bounded subprocess, and the repository's declared interpreter
- **AND** it removes its conflicting fixture and leaves no `__pycache__`, `.pyc`, environment, installed dependency, altered interpreter file, credential, or absolute maintainer path in the repository

### Requirement: Each prerequisite bridge has a complete, independently verifiable learning loop

The Chapter 1, Chapter 2, and Chapter 7 additions SHALL each state concrete
objectives, existing prerequisites, estimated essential time, an observable
outcome, and a safe stopping point. Each bridge SHALL trace every required
objective through plain-language context, minimal theory, a prediction,
truthfully classified runnable evidence, a guided TODO and useful hint, normal
behavior, a boundary case, one recoverable expected error, common mistakes, an
explained solution, a checkpoint rubric, and a closing reflection. Required
work SHALL use only concepts already introduced at that point; any later
concept SHALL be an explicitly skippable **Optional preview** with the minimum
copyable context and an exact localized forward link.

Runnable claims SHALL be executed on the declared CPython interpreter or bound
to a registered tested companion source. Expected-error evidence SHALL assert
stable exception categories or stable semantic signals, not an entire traceback
whose wording can vary. The curriculum evidence SHALL identify the three
bridges as prerequisites of the first checkpoint that requires them without
creating a cycle or treating an optional preview as a required dependency.

#### Scenario: Happy path completes a bridge checkpoint

- **WHEN** a learner follows one bridge's essential sequence with its normal input
- **THEN** the documented output or state is observable using only declared prior knowledge
- **AND** the rubric assesses correctness, readability, recovery, verification, and the learner's explanation

#### Scenario: Edge case stays inside the declared route

- **WHEN** a bridge presents a path with spaces, an absence sentinel, an empty value, a tolerance boundary, an empty queue, or an import-location boundary
- **THEN** the learner can predict and observe that boundary without completing an optional later chapter
- **AND** the explained solution introduces no hidden function, conditional, exception handler, class, package manager, or test framework

#### Scenario: Missing executable evidence blocks a runnable claim

- **WHEN** a new block is labelled `runnable` but has neither current direct-execution evidence nor a valid tested `source-ref`
- **THEN** the relevant content gate fails with the unit path and block identity
- **AND** maintainers execute and register the evidence or reclassify the block truthfully before publication

#### Scenario: Recovery evidence is incomplete

- **WHEN** a lesson shows an expected failure but omits the correction or the successful rerun
- **THEN** pedagogical review keeps the bridge incomplete
- **AND** the bridge is revised to connect diagnostic evidence to one concrete repair and a bounded successful observation

#### Scenario: Prerequisite graph remains acyclic

- **WHEN** the three bridge concepts and their consuming checkpoints are added to the declared curriculum map
- **THEN** every required edge points from an earlier taught concept to a later use and graph validation reports no cycle or unknown target
- **AND** optional `math.isclose`, Chapter 15 package depth, and editor-specific conveniences remain non-required previews

### Requirement: Bridge publication preserves multilingual, accessible, provenance, and repository boundaries

The canonical Chapter 1, 2, and 7 additions SHALL stabilize before equivalent
Spanish, Catalan, Swedish, and Arabic material is accepted. All five siblings
SHALL preserve objectives, prerequisites, route boundaries, commands,
identifiers, examples, outputs, edge cases, expected failures, recovery,
warnings, TODOs, hints, solutions, checkpoints, rubrics, and reflections. Each
unit SHALL preserve the selector order `English → Español → Català →
Svenska → العربية`; Arabic SHALL retain exactly one balanced outer
`<div dir="rtl">`, with code, commands, paths, operators, output, and diagnostics
legible left-to-right.

Changed headings SHALL preserve already published anchors or add a documented
compatible alias. Links SHALL be descriptive and localized, heading levels
SHALL be hierarchical, and any meaningful visual SHALL have alt text and an
equivalent prose sequence. Original examples SHALL be preferred; adapted prose,
exercise, image, or dataset SHALL carry verified source and license evidence.
Automation SHALL record current structural and executable evidence but SHALL
NOT mark linguistic fluency, technical/pedagogical equivalence, rendered
accessibility, Arabic bidi, provenance, license acceptance, or publication
approval as human-accepted.

#### Scenario: Localization is structurally complete but not human-approved

- **WHEN** all fifteen changed Markdown siblings pass selectors, links, fences, anchors, and Arabic-wrapper checks
- **THEN** automation records those current signals without manufacturing a linguistic, pedagogical, accessibility, bidi, provenance, or release decision
- **AND** each affected human review remains pending until the competent reviewer signs the current content digest

#### Scenario: Accessibility defect blocks acceptance

- **WHEN** a changed subsection relies on syntax color, spatial placement, an unlabeled image, a skipped heading level, or non-descriptive link text
- **THEN** accessibility review rejects the affected unit with a concrete location
- **AND** the equivalent prose or markup is repaired and rerendered before a new human decision

#### Scenario: Localization changes code behavior

- **WHEN** a localized sibling changes a public identifier, exception category, command, expected output, or exercise success criterion unintentionally
- **THEN** parity review marks that locale incomplete even if heading and fence counts match
- **AND** the localized contract is reconciled with canonical English and reviewed again

#### Scenario: Provenance cannot be resolved

- **WHEN** added bridge material adapts a third-party source whose ownership, license, required notice, or compatibility with the book cannot be verified
- **THEN** publication remains blocked for that material
- **AND** maintainers replace it with an original example or record competent provenance and license acceptance without guessing

#### Scenario: Repository hygiene at bridge handoff

- **WHEN** bridge content, examples, localization checks, and review packets have been generated
- **THEN** tracked changes contain only intentional source, specification, configuration, and evidence files
- **AND** no virtual environment, cache, bytecode, temporary shadow module, test report, editor state, credential, learner data, or unresolved recovery directory is present
