## ADDED Requirements

### Requirement: Chapter 27 provides a progressive gradual-typing learning path

The course SHALL publish `chapter-27-python-typing/README.md` plus `README.es.md`, `README.ca.md`, `README.sv.md`, and `README.ar.md` as a CPython 3.11+ learning unit. The chapter SHALL declare the foundational checkpoints of Chapters 11, 15, 18, 22, and the Chapter 26 essential iteration bridge as prerequisites and SHALL separate these independently completable routes:

- **Essential:** parameter, return, scalar, collection, union, and optional-value annotations; `None` narrowing; and the distinction between static analysis and runtime behavior;
- **Professional:** `Callable`, `TypedDict`, structural `Protocol`, `Self`, and basic `TypeVar`-based generics against one inventory domain; and
- **Advanced optional:** a reproducible checker run, deliberately invalid consumers, stable diagnostic categories, and correction to a clean result.

Each route SHALL state its prerequisite, estimated session range, observable outcome, completion criteria, and safe continuation or stopping point. Advanced checker setup SHALL NOT be required to complete the essential route.

#### Scenario: Beginner completes the essential route

- **WHEN** a learner can already define and test functions but has never used type annotations
- **THEN** the learner annotates an inventory function, predicts a normal and optional-value result, runs the function, and explains what the annotations communicate
- **AND** completes the essential checkpoint without `Protocol`, generics, a third-party checker, packaging, or native tooling

#### Scenario: Returning learner enters the professional route

- **WHEN** a learner demonstrates the essential checkpoint without rereading the complete chapter
- **THEN** the route map names the exact professional entry checkpoint and the inventory contract it extends
- **AND** does not treat an optional advanced checker exercise as an earlier prerequisite

#### Scenario: Advanced material leaks into required work

- **WHEN** an essential example, TODO, solution, or checkpoint requires `Protocol`, `Self`, `TypeVar`, checker configuration, or an unexplained diagnostic category
- **THEN** the pedagogical gate fails that objective-to-assessment trace
- **AND** maintainers either teach the prerequisite first or move the dependency behind the professional or advanced route boundary

#### Scenario: Learner chooses a safe stopping point

- **WHEN** the learner finishes the essential or professional checkpoint but cannot install the pinned checker tools
- **THEN** the chapter records the completed runtime-observable outcome as a valid stopping point
- **AND** labels checker evidence as unavailable rather than implying that the unavailable run passed

### Requirement: The chapter distinguishes static annotations from runtime validation

The chapter SHALL explain that Python annotations support tools and readers but do not, by themselves, reject a runtime argument. It SHALL teach `list[str]`, `dict[str, int]`, `T | None`, `is None`, `isinstance`, and explicit boundary validation in prerequisite order. It MUST distinguish absence from other false values, narrowing from conversion, and a static checker diagnostic from a Python exception.

#### Scenario: Annotated call receives valid values

- **WHEN** a function annotated with concrete parameter and return types receives values inside its documented domain
- **THEN** it returns the documented result under CPython 3.11+
- **AND** the lesson separately identifies which claim is runtime behavior and which claim is static analysis

#### Scenario: Annotation receives a wrong runtime value

- **WHEN** an annotated function without explicit validation receives a value that contradicts its annotation but its executed operations still accept that value
- **THEN** the lesson demonstrates that Python does not automatically reject the call merely because of the annotation
- **AND** does not describe a checker result as runtime enforcement

#### Scenario: Boundary validation rejects invalid data

- **WHEN** untrusted `object`-typed inventory input is missing a required field, uses the wrong runtime type, or violates the documented quantity/SKU bounds
- **THEN** explicit validation raises the documented `TypeError` or `ValueError` before the value enters the typed core
- **AND** the recovery example corrects the input, reruns both runtime and static checks, and preserves the original input object

#### Scenario: Optional value is false but present

- **WHEN** a typed value can be `0`, an empty collection, or `None`
- **THEN** the example uses `is None` to narrow absence without discarding valid false values
- **AND** explains why a truthiness check would change the domain contract

### Requirement: The typed inventory companion exposes an exact executable contract

`chapter-27-python-typing/examples/typed_inventory.py` SHALL be the executable authority for the chapter's professional examples and SHALL export these stable teaching contracts:

- `InventoryRow`, a `TypedDict` containing `sku: str` and `quantity: int`;
- `PriceSource`, a structural `Protocol` with `unit_price(sku: str) -> float | None`;
- `parse_row(raw: Mapping[str, object]) -> InventoryRow`;
- `first_matching(items: Iterable[T], predicate: Callable[[T], bool]) -> T | None` using a basic `TypeVar`; and
- an `Inventory` example whose fluent `add(...)` operation returns `Self`.

`parse_row` SHALL strip and uppercase an SKU, accept a non-empty SKU of at most 32 characters, and accept only a built-in non-boolean `int` quantity in the inclusive range 0 through 1,000,000. A missing/wrong-typed field SHALL raise `TypeError`; an empty/oversized SKU or out-of-range quantity SHALL raise `ValueError`; rejection SHALL NOT mutate `raw`. `first_matching` SHALL stop at the first match and return `None` for an empty or unmatched iterable without reusing an exhausted iterator.

#### Scenario: Valid row enters the typed core

- **WHEN** `parse_row` receives `{"sku": "  part-7 ", "quantity": 0}`
- **THEN** it returns `{"sku": "PART-7", "quantity": 0}`
- **AND** the returned object satisfies the `InventoryRow` static contract

#### Scenario: Boolean is supplied as a quantity

- **WHEN** `parse_row` receives `True` or `False` as `quantity`
- **THEN** it raises `TypeError` even though `bool` is an `int` subclass at runtime
- **AND** the input mapping remains unchanged

#### Scenario: Generic search consumes a one-shot iterable

- **WHEN** `first_matching` receives a generator and a predicate that matches its third value
- **THEN** it returns that value after evaluating no later values
- **AND** the lesson explains that a consumed iterator must be recreated rather than assumed reusable

#### Scenario: Structural implementation satisfies the price protocol

- **WHEN** a class that does not inherit from `PriceSource` implements the exact `unit_price` method contract
- **THEN** the positive checker consumer accepts it structurally
- **AND** the runtime lesson avoids claiming that static protocol acceptance validates returned values at runtime

#### Scenario: Fluent subclass uses Self

- **WHEN** an `Inventory` subclass calls the inherited fluent `add(...)` operation
- **THEN** the documented static result preserves the subclass type
- **AND** the runtime result is the same instance rather than an unrelated replacement object

### Requirement: Static-analysis evidence is bounded, reproducible, and recoverable

The chapter SHALL provide `chapter-27-python-typing/tests/test_typed_inventory.py`, `examples/checker_positive.py`, `examples/checker_negative.py`, `requirements-dev.lock`, and `tools/verify.py`. `requirements-dev.lock` MUST be described accurately as exact direct development-tool pins for the declared verified host, not as a resolver-generated, hash-complete, cross-platform lock. Initial acquisition MAY require network access and SHALL be separated from the offline runtime lesson.

`python -B chapter-27-python-typing/tools/verify.py --runtime` SHALL run bounded runtime tests using the declared CPython interpreter. `python -B chapter-27-python-typing/tools/verify.py --checker` SHALL run the exact provisioned checker version over the companion and positive consumer, require a clean result, run the negative consumer separately, require non-zero status plus the declared stable error categories, and then prove the corrected consumer is clean. Full version-specific diagnostic prose SHALL NOT be a golden contract.

#### Scenario: Runtime and checker contracts pass

- **WHEN** the provisioned CPython and pinned development tools match the declared verification inputs
- **THEN** the runtime mode passes normal, boundary, invalid, and recovery cases and the checker mode accepts the typed companion plus positive consumer
- **AND** the negative consumer fails only in the separately identified expected-failure phase

#### Scenario: Negative consumer exposes several mistakes

- **WHEN** the checker analyzes `examples/checker_negative.py`
- **THEN** it reports the declared stable categories for an incompatible argument, an invalid `TypedDict` field, and a protocol method mismatch
- **AND** acceptance depends on categories and non-zero status rather than complete wording, path prefixes, timing, or terminal coloring

#### Scenario: Learner recovers from a checker failure

- **WHEN** the exercise corrects the mismatched argument, field, or protocol signature
- **THEN** the corrected positive consumer passes the same checker configuration
- **AND** runtime tests still pass so the correction cannot replace behavior with a static-only stub

#### Scenario: Checker prerequisite is absent

- **WHEN** the exact declared checker executable/version is unavailable
- **THEN** the directly selected checker verifier reports a bounded prerequisite-missing result with non-zero status and the `learning-bridges` profile records the optional checker as an informational, non-pass prerequisite state
- **AND** do not install tools implicitly, reach an undeclared index, or convert the missing run into pass evidence

#### Scenario: Broad escape hatch is proposed

- **WHEN** a solution uses unbounded `Any`, an unqualified `# type: ignore`, or `cast` solely to silence a real mismatch
- **THEN** the assessment rejects that solution
- **AND** recovery narrows or validates the boundary, corrects the contract, or documents the smallest code-specific exception with its reason

### Requirement: Typing objectives trace to guided practice and assessment

Every required Chapter 27 objective SHALL trace to prerequisite-ordered explanation, prediction, a runnable example or exact companion source reference, guided TODO, useful hint, happy and edge behavior, recoverable error, common mistake, explained solution, checkpoint, rubric, and reflection. The rubric SHALL assess runtime correctness, annotation clarity, boundary/error handling, static evidence, and the learner's explanation without rewarding annotation density by itself.

#### Scenario: Learner performs the essential TODO

- **WHEN** the learner annotates a previously working inventory function
- **THEN** the exercise first asks for a prediction, gives a hint without revealing the final signature, and asks the learner to run both a valid and optional-value case
- **AND** the solution explains each annotation and preserves the original runtime behavior

#### Scenario: Solution adds a hidden prerequisite

- **WHEN** an explained solution introduces a generic, protocol, decorator, dependency, or checker flag absent from the objective and route prerequisites
- **THEN** the traceability review fails that exercise
- **AND** maintainers simplify the solution or add a prerequisite-ordered explanation before reassessment

#### Scenario: Static success hides a runtime defect

- **WHEN** a consumer passes the checker but fails a documented runtime boundary case
- **THEN** the checkpoint remains incomplete
- **AND** the learner corrects the executable contract and reruns runtime plus static evidence

#### Scenario: Final checkpoint is assessed

- **WHEN** the learner completes a small typed inventory extension
- **THEN** the rubric requires no zero in runtime correctness, boundary recovery, static contract, readability, and explanation
- **AND** optional professional or advanced depth cannot compensate for a failing essential behavior

### Requirement: Typing content remains multilingual, accessible, safe, and repository-clean

All five Chapter 27 siblings SHALL preserve semantic parity for route boundaries, objectives, public identifiers, signatures, type expressions, runtime outputs, diagnostic categories, TODOs, hints, cases, solutions, rubrics, links, and safety claims. Code behavior SHALL remain language-independent while prose is translated naturally. Arabic SHALL retain exactly one balanced outer `<div dir="rtl">`; code, type expressions, commands, paths, outputs, and diagnostics SHALL remain legible left-to-right.

The unit SHALL use hierarchical headings, descriptive links, readable tables with list alternatives, and prose equivalents for any diagrams of static/runtime flow. Examples SHALL use synthetic inventory data, bounded collections/process timeouts, repository-relative paths, and no credentials or learner personal data. Adapted material SHALL have resolved provenance before publication.

#### Scenario: Localized typing lesson is reviewed

- **WHEN** Spanish, Catalan, Swedish, or Arabic Chapter 27 content is compared with canonical English
- **THEN** a fluent reviewer can reach the same typed/runtime outcomes and recovery using the localized instructions
- **AND** automated heading or fence similarity remains a signal rather than linguistic, pedagogical, or technical approval

#### Scenario: Static and runtime flow is presented visually

- **WHEN** a diagram distinguishes source, checker, interpreter, and explicit validation
- **THEN** concise alt text and equivalent prose name the same sequence and boundaries
- **AND** no distinction depends only on color, arrow direction, or visual position

#### Scenario: Arabic mixed-direction content is rendered

- **WHEN** the Arabic lesson displays `dict[str, int]`, `T | None`, `python -B`, a path, or a checker diagnostic
- **THEN** each technical token remains copyable and readable left-to-right within the right-to-left lesson
- **AND** rendered bidirectional approval remains pending until a competent reviewer records it

#### Scenario: Verification completes or fails

- **WHEN** runtime/checker verification exits for any reason
- **THEN** all child processes are bounded and temporary files are removed
- **AND** an explicit scan finds no `.venv`, cache, bytecode, checker cache, credential, learner data, or generated report in the chapter tree, including ignored files
