## ADDED Requirements

### Requirement: Chapter 28 provides independently completable longitudinal stages

The course SHALL publish `chapter-28-professional-capstone/README.md` plus `README.es.md`, `README.ca.md`, `README.sv.md`, and `README.ar.md`. The chapter SHALL evolve one `chapter-28-professional-capstone/examples/order-tracker/` project without renaming prior chapter paths or introducing an unrelated final-project domain. It SHALL expose these independently completable stages:

- **Foundation, after Chapter 12:** immutable order values, status rules, and an in-memory service;
- **Practical, after Chapter 18:** SQLite repository, command-line interface, explicit configuration, safe logging, and normal/boundary/invalid/recovery tests;
- **Systems extension, after Chapter 23:** an optional bounded loopback adapter that reuses the same service contract; and
- **Hero packaging:** a pure-Python `pyproject.toml`, sdist and wheel evidence, rebuild from sdist, clean install, foreign-directory import/CLI smoke, and cleanup without publication.

Each stage SHALL name exact earlier checkpoints for every required concept, estimated sessions, observable outcome, exit criteria, and safe stopping point. The systems extension and packaging stage SHALL NOT be prerequisites for completing the practical stage.

#### Scenario: Learner completes the foundation stage

- **WHEN** a learner has completed the Chapter 12 checkpoint
- **THEN** the learner creates and advances synthetic orders through an in-memory service with no database, network, third-party dependency, or packaging tool
- **AND** can stop with a runnable tested domain artifact

#### Scenario: Learner resumes at the practical stage

- **WHEN** a learner already satisfies the foundation exit criteria and the Chapters 13 through 18 checkpoints named by the route
- **THEN** the chapter starts from the same order contract and adds persistence, CLI, configuration, logging, and tests one boundary at a time
- **AND** does not require rebuilding the domain as an unrelated project

#### Scenario: Optional systems tooling is unavailable

- **WHEN** the learner cannot or does not want to run the localhost adapter
- **THEN** the practical and packaging checkpoints remain independently executable
- **AND** the unavailable optional extension is not reported as completed

#### Scenario: Assessment introduces a new framework

- **WHEN** a required capstone solution depends on Django, FastAPI, a cloud service, a production database, a GUI, or another programming model not taught by its declared prerequisites
- **THEN** the capstone traceability gate fails
- **AND** maintainers remove that dependency or place it in a separately proposed optional route

### Requirement: The order-tracker domain has a stable bounded contract

The distribution name SHALL be `course-order-tracker`, the import package SHALL be `order_tracker`, and the console command SHALL be `order-tracker`. The `src/order_tracker/` package SHALL define an immutable `Order` value with `order_id`, `item`, `quantity`, and `status`; status values SHALL be exactly `pending`, `packed`, and `shipped`. It SHALL reject order identifiers that are empty or longer than 32 characters, item labels that are empty or longer than 80 characters, built-in-integer quantities outside 1 through 1,000, or boolean quantities.

The domain service SHALL create an order in `pending`, transition only `pending -> packed -> shipped`, list orders deterministically by `order_id`, and expose stable domain exceptions for duplicate identifiers, unknown identifiers, validation failure, and invalid transitions. A rejected operation MUST preserve all prior state.

#### Scenario: Happy order lifecycle

- **WHEN** the service creates `ORD-001` for two synthetic `widget` items and advances it twice
- **THEN** the observable statuses are `pending`, then `packed`, then `shipped`
- **AND** listing returns the immutable current order in deterministic identifier order

#### Scenario: Boundary values are accepted

- **WHEN** an order uses an identifier of 32 characters, an item label of 80 characters, and quantity 1 or 1,000
- **THEN** the domain accepts those inclusive boundary values
- **AND** tests distinguish them from the first invalid values outside each boundary

#### Scenario: Boolean quantity is rejected

- **WHEN** an order receives `True` or `False` as its quantity
- **THEN** the domain raises the documented validation exception
- **AND** no order is added even though `bool` is an `int` subclass

#### Scenario: Invalid transition is attempted

- **WHEN** code attempts to advance an already `shipped` order or skip/backtrack a status
- **THEN** the service raises the stable invalid-transition exception
- **AND** recovery reloads the order, reports its current status, and leaves repository state unchanged

#### Scenario: Duplicate identifier is attempted

- **WHEN** a second order uses an existing `order_id`
- **THEN** the service raises the stable duplicate-order exception without replacing the original
- **AND** a corrected unique identifier succeeds on a subsequent operation

### Requirement: SQLite persistence and CLI preserve the domain contract

`chapter-28-professional-capstone/examples/order-tracker/` SHALL use a `src` layout and a standard-library SQLite repository behind the same service boundary as the in-memory repository. Schema creation SHALL be idempotent; writes and transitions SHALL be transactional; database connections SHALL use a documented bounded busy timeout; and failed validation, duplicate insertion, invalid transition, or database exception SHALL NOT leave a partial order or partial status change.

The CLI SHALL support `order-tracker --database PATH add ORDER_ID ITEM QUANTITY`, `order-tracker --database PATH advance ORDER_ID`, and `order-tracker --database PATH list`. `--database` SHALL take precedence over `ORDER_TRACKER_DB`; if neither is provided, the command SHALL fail before creating a database. Successful machine-stable output SHALL identify the order and resulting status. Usage/configuration failures SHALL exit 2, domain/repository failures SHALL exit 1, and success SHALL exit 0; diagnostics SHALL go to stderr without a traceback in normal learner-facing errors.

#### Scenario: CLI creates and lists an order

- **WHEN** the installed `order-tracker` command receives an explicit database inside a temporary directory and runs `add ORD-001 widget 2` followed by `list`
- **THEN** both commands exit 0 and listing reports `ORD-001`, `widget`, `2`, and `pending` in the documented stable format
- **AND** the database file exists only at the explicitly selected temporary path

#### Scenario: Environment configuration is overridden

- **WHEN** `ORDER_TRACKER_DB` names one disposable database and `--database` names another
- **THEN** only the command-line path is opened or changed
- **AND** the lesson explains the precedence without printing either absolute path as normal output

#### Scenario: Database configuration is absent

- **WHEN** neither `--database` nor `ORDER_TRACKER_DB` is supplied
- **THEN** the CLI exits 2 with a concise recovery instruction
- **AND** creates no database, configuration file, cache, or log file in the working tree

#### Scenario: SQLite write fails

- **WHEN** the selected database is unavailable, locked beyond the bounded timeout, corrupt, or otherwise cannot commit
- **THEN** the CLI exits 1 with the failing persistence phase and non-sensitive context
- **AND** recovery uses a corrected disposable path or releases the test lock and reruns without deleting unrelated files

#### Scenario: CLI receives invalid quantity

- **WHEN** `add` receives a non-integer, zero, or greater-than-1,000 quantity
- **THEN** it exits with the documented usage/domain status and does not insert an order
- **AND** a subsequent valid invocation against the same database succeeds

### Requirement: Configuration, logging, and optional systems adapters are local-first

The practical stage SHALL configure only through explicit CLI arguments and documented environment variables, use fake values, and log to stderr. Logs SHALL identify phase/event, stable order identifier when appropriate, and outcome without recording item text, complete database paths, environment values, SQL statements with bound data, credentials, or traceback details during expected errors.

The optional systems extension SHALL reuse the tested order service, bind only to loopback (`127.0.0.1` or `::1`) on an operating-system-assigned port, impose explicit connection/request-size/request-count/concurrency/time bounds, and cleanly cancel or close every task, socket, and database connection. It SHALL NOT claim authentication, TLS, Internet exposure, or production deployment, and SHALL NOT become a runtime or artifact-verification prerequisite for the base package.

#### Scenario: Verbose local operation is logged

- **WHEN** a learner enables documented verbose logging and creates a synthetic order
- **THEN** stderr records the create phase, order identifier, and success outcome while stdout retains the stable CLI result
- **AND** neither stream reveals item text, full database path, environment value, or secret

#### Scenario: Expected error is logged

- **WHEN** a duplicate or invalid transition occurs
- **THEN** the log records the stable error category and recovery phase without a learner-facing traceback
- **AND** the original domain exception remains testable independently from presentation

#### Scenario: Loopback adapter handles a bounded request

- **WHEN** the optional adapter receives one valid request below its documented size limit on an OS-assigned loopback port
- **THEN** it invokes the same service contract and returns the documented bounded response
- **AND** the test completes within its timeout without contacting a public host

#### Scenario: Adapter limit is exceeded

- **WHEN** a client exceeds the request-size, connection, concurrency, or total-request bound
- **THEN** the adapter rejects or closes that request with the documented stable outcome
- **AND** bounded recovery proves a later valid local request or clean shutdown without an unbounded queue

#### Scenario: Async operation is cancelled

- **WHEN** the optional async client or handler is cancelled or reaches its timeout
- **THEN** cancellation propagates after documented cleanup
- **AND** no background task, socket, fixed sleep, or database handle remains active

### Requirement: Capstone behavior is tested at the appropriate boundary

The project SHALL provide deterministic unit tests for values/transitions, contract tests shared by in-memory and SQLite repositories, service tests, CLI subprocess tests, and optional adapter tests. Tests SHALL cover normal, boundary, invalid, and recovery behavior using temporary directories, synthetic data, operating-system-assigned ports, bounded subprocess output, and bounded timeouts. Each feature in the chapter traceability table SHALL map to the earlier checkpoint that teaches it and to at least one observable test or manual rubric item.

#### Scenario: Both repositories satisfy the same contract

- **WHEN** the repository contract suite runs against the in-memory and SQLite implementations
- **THEN** both produce the same create/get/list/advance outcomes and stable domain exceptions
- **AND** the SQLite run uses an isolated temporary database

#### Scenario: CLI is tested as a subprocess

- **WHEN** CLI tests exercise success, invalid input, duplicate, missing configuration, and recovery
- **THEN** they assert exit status, stdout/stderr separation, state, and bounded output
- **AND** cannot pass by calling private command functions while bypassing entry-point parsing

#### Scenario: Failure occurs halfway through a persistence operation

- **WHEN** a controlled test double or SQLite failure interrupts a write before commit
- **THEN** the test observes the documented repository error and unchanged prior state
- **AND** a later clean transaction succeeds without manual editing of database internals

#### Scenario: Objective lacks prior teaching or evidence

- **WHEN** traceability finds a required feature first introduced in the final solution or a required objective with no observable assessment
- **THEN** the capstone gate fails with the exact stage and feature
- **AND** maintainers add prerequisite-ordered teaching/evidence or remove the feature from required completion

### Requirement: The pure-Python distribution is verified from artifacts without publication

`chapter-28-professional-capstone/examples/order-tracker/pyproject.toml` SHALL declare the `course-order-tracker` distribution, `order_tracker` package under `src/`, `order-tracker` console entry point, `Requires-Python >=3.11`, standard-library-only runtime, build-system requirements separate from runtime requirements, and the intended license/readme metadata. The accepted verification command SHALL be `python -B chapter-28-professional-capstone/examples/order-tracker/tools/verify_artifact.py`.

The verifier SHALL use independent temporary source-snapshot, build/output, install-environment, and foreign-working-directory roots. With build isolation enabled, it SHALL build and inspect an sdist and pure-Python wheel, unpack the exact sdist, rebuild a wheel from that distributed source, inspect metadata/member paths and the `py3-none-any` declaration, install the exact rebuilt wheel into a fresh environment, run `pip check`, verify distribution metadata, import `order_tracker` outside the checkout, exercise the public domain API and installed `order-tracker` entry point, report artifact SHA-256 digests plus executed tool/interpreter versions, and remove all temporary state on success or failure.

The lesson MUST describe direct pins, constraints, snapshots, and locks accurately; a wheel tag SHALL be treated as a compatibility declaration rather than evidence for unexecuted hosts. Verification SHALL NOT upload, publish, sign, attest, request an index token, or create a production release.

#### Scenario: Sdist and initial wheel are built

- **WHEN** provisioned build inputs satisfy `pyproject.toml` and isolated PEP 517 builds run from the temporary source snapshot
- **THEN** the output area contains the expected sdist and `py3-none-any` wheel for `course-order-tracker`
- **AND** the repository tree is not used as an output, environment, or cache directory

#### Scenario: Sdist is complete enough to rebuild

- **WHEN** the verifier inspects and unpacks the exact sdist in a second temporary source root
- **THEN** it finds metadata, license/readme, `pyproject.toml`, complete `src/order_tracker` sources, and every declared required package datum
- **AND** rebuilding a wheel uses that unpacked sdist rather than files from the original checkout

#### Scenario: Installed artifact works outside the source tree

- **WHEN** the exact rebuilt wheel is installed without source-tree fallback into a fresh environment
- **THEN** `pip check`, distribution/version metadata, public import, normal/boundary/invalid/recovery behavior, and the installed `order-tracker` smoke all pass from a foreign working directory
- **AND** `order_tracker.__file__` resolves inside the install environment rather than the repository or unpacked sdist

#### Scenario: Archive contains forbidden material

- **WHEN** sdist or wheel inspection finds a credential, `.env`, database, learner data, venv, cache, bytecode, test-only network hook, prior wheel/sdist, generated report, or undeclared package file
- **THEN** artifact verification fails in the archive-inspection phase before installation
- **AND** recovery removes the source cause, starts from clean temporary roots, rebuilds, and repeats every downstream phase

#### Scenario: Build prerequisite is unavailable

- **WHEN** the declared build frontend/backend or an isolated build input cannot be obtained from the explicitly provisioned source
- **THEN** verification reports the build-prerequisite phase as unavailable or failed with non-zero status
- **AND** does not disable isolation silently, use maintainer-global packages as proof, reach a private index, or claim artifact success

#### Scenario: Publication is requested inside the lesson

- **WHEN** a learner reaches the end of artifact verification
- **THEN** the chapter stops after local inspection/install evidence and explains that publication requires separate release authorization and controls
- **AND** no command invokes an upload endpoint, consumes a token, signs, attests, or modifies a package index

#### Scenario: Verification exits after failure

- **WHEN** metadata, build, inspection, install, import, behavior, CLI, or cleanup fails
- **THEN** the report names that phase with bounded redacted evidence and does not overstate later phases
- **AND** temporary environments, artifacts, caches, databases, and child processes are removed before exit

### Requirement: Capstone assessment is prerequisite-ordered and explainable

Every required Chapter 28 stage SHALL provide objectives, real-world context using synthetic orders, minimal theory, prediction, a bounded runnable example or exact source reference, guided TODO and hint, happy/edge/recoverable-error paths, common mistakes, explained solution, checkpoint, stage rubric, and reflection. The final rubric SHALL assess domain correctness, separation of concerns, persistence atomicity, CLI/configuration behavior, logging privacy, testing/recovery, artifact evidence where selected, and the learner's explanation.

#### Scenario: Learner extends the existing project

- **WHEN** a stage asks the learner to add a repository, command, or adapter
- **THEN** the TODO identifies the existing interface to preserve, supplies a useful hint, and asks for a predicted normal and failure outcome before execution
- **AND** the solution explains the new boundary without replacing the project with unrelated final code

#### Scenario: Hero packaging is not selected

- **WHEN** a learner completes the practical checkpoint but stops before packaging
- **THEN** the practical rubric can be completed without artifact points
- **AND** the course reports that stage honestly rather than calling the distribution verified

#### Scenario: Final artifact passes but explanation is missing

- **WHEN** tests and packaging verification pass but the learner cannot explain a transaction, configuration precedence, error recovery, or source-versus-installed evidence
- **THEN** the corresponding rubric category remains incomplete
- **AND** the learner is directed to the exact earlier explanation and a focused retry

#### Scenario: Capstone is assessed

- **WHEN** a learner submits a selected-stage completion
- **THEN** no required category for that stage may score zero and evidence names the exact executed checkpoint/toolchain
- **AND** optional systems or hero work cannot hide a failure in foundation or practical correctness

### Requirement: Capstone publication remains multilingual, accessible, attributable, and clean

All five Chapter 28 siblings SHALL preserve semantic parity for stage boundaries, objectives, public package/distribution/CLI identifiers, commands, outputs, data/error contracts, bounds, TODOs, hints, tests, solutions, rubrics, links, and publication limits. Prose SHALL be natural in each language while program behavior stays stable. Arabic SHALL retain exactly one balanced outer `<div dir="rtl">`; commands, code, paths, identifiers, output, database names, and diagnostics SHALL remain readable left-to-right.

The chapter SHALL use hierarchical headings, descriptive links, alt text and prose equivalents for architecture diagrams, and list alternatives for wide traceability/schema tables. Synthetic order data SHALL NOT solicit learner names, addresses, emails, payment data, live credentials, or public targets. Third-party build inputs and any adapted material SHALL have recorded provenance/license evidence; automated structure or execution SHALL NOT grant linguistic, accessibility, bidi, provenance, or publication approval.

#### Scenario: Localized stage is reviewed

- **WHEN** a fluent Spanish, Catalan, Swedish, or Arabic reviewer follows a selected stage
- **THEN** the localized learner can produce the same observable domain, CLI, recovery, and artifact outcomes as canonical English
- **AND** the human decision is bound to the current localized and companion evidence rather than inferred from similar structure

#### Scenario: Architecture is conveyed without visual position

- **WHEN** a diagram shows CLI, service, repository, SQLite, and optional adapter boundaries
- **THEN** alt text and adjacent prose describe the same data/control sequence and optional boundary
- **AND** meaning does not depend only on arrows, color, left/right placement, or screen width

#### Scenario: Arabic mixed-direction artifact commands are rendered

- **WHEN** the Arabic page displays `course-order-tracker`, `order_tracker`, `order-tracker`, a filesystem path, or an artifact command
- **THEN** each token is legible and copyable left-to-right inside right-to-left prose
- **AND** rendered accessibility and bidirectional review remain pending until competent reviewers record decisions

#### Scenario: Repository hygiene is audited

- **WHEN** all content, behavior, optional adapter, and artifact checks finish or fail as designed
- **THEN** an explicit ignored-inclusive scan finds no `.venv`, `build`, `dist`, wheel, sdist, database, cache, bytecode, coverage, generated metadata, credential, learner data, socket, or child process in the chapter tree
- **AND** only reviewed source, tests, metadata, documentation, and declared provenance records remain
