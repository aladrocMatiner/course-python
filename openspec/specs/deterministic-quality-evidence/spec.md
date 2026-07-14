# deterministic-quality-evidence Specification

## Purpose
Define a closed, versioned quality matrix and bounded read-only orchestration
runner that emits deterministic, truthful local and CI evidence, fails closed
on configuration, execution, containment, prerequisite, or mutation problems,
and preserves existing validator interfaces and human review boundaries.

## Requirements
### Requirement: Quality matrix is versioned and closed
The repository SHALL define a standard-library-readable matrix with one supported schema version, globally bounded resources, unique stable check IDs, explicit profiles, a closed adapter vocabulary, and repository-relative adapter fields. The parser MUST enforce the mandatory `core`, domain, and `handoff` memberships/bindings before execution and MUST reject arbitrary shell text, unknown fields, duplicate IDs, missing/profile-tampered references, traversal, unsafe symlinks, wildcard selection, invalid prerequisites, and limits outside documented hard maxima.

#### Scenario: Core matrix is valid
- **WHEN** the schema-v1 matrix is loaded
- **THEN** `core` selects tool unittests, curriculum validation, parity validation, and generic book validation in deterministic order
- **AND** every referenced check has one known adapter and bounded resources

#### Scenario: Domain selection is explicit
- **WHEN** a maintainer selects `network-domain`, `cpp-domain`, or `rust-domain`
- **THEN** only the exact declared plugin check is selected in addition to no implicit domain work
- **AND** all other domain checks report `not-selected`

#### Scenario: Malformed matrix fails closed and recovers
- **WHEN** a fixture adds an unknown key, duplicate ID, missing reference, arbitrary command, escaping path, unsafe symlink, or excessive limit
- **THEN** the runner exits `2` before running repository code and names only the stable configuration error
- **AND WHEN** the fixture is restored to the schema
- **THEN** selection succeeds without a suppression or migration flag

### Requirement: Runner executes bounded read-only checks
The runner SHALL execute selected trusted-repository checks as argv without a shell, with stdin closed, a minimal non-secret environment, hard time/output bounds, controlled process descendants, temporary output outside the repository, and a content-hash snapshot. It MUST NOT restore or silently accept a repository mutation.

#### Scenario: Selected checks pass
- **WHEN** all commands in a selected profile exit `0`, stay within bounds, leave no descendant, and preserve the repository snapshot
- **THEN** every selected check reports `pass`, every unselected check reports `not-selected`, and the runner exits `0`

#### Scenario: Quality failure remains distinguishable
- **WHEN** a selected validator executes normally and exits `1`
- **THEN** that check reports `fail`, other safe selected checks still run, and the aggregate exits `1` unless an infrastructure error also occurs

#### Scenario: Infrastructure failure fails evidence
- **WHEN** a selected check crashes with its contract error code, times out, exceeds output, or leaves a descendant
- **THEN** it reports `error`, freezes the observed owned process tree before bounded termination/reaping, and the aggregate exits `2`
- **AND** correcting the fixture allows the next run to pass without retained process or temporary state

#### Scenario: Output flood is physically bounded
- **WHEN** a child writes far beyond a small configured output limit
- **THEN** the runner detects the first overflow through bounded streaming, persists no oversized log, terminates the complete subtree, and reports `error`

#### Scenario: Missing prerequisite is not a pass
- **WHEN** a selected check declares an executable that is unavailable
- **THEN** it reports `unsupported`, repository code for that check does not run, and the aggregate exits `2`
- **AND** installing/providing the prerequisite causes a later run to report the real executed result

#### Scenario: Source mutation stops unreliable execution
- **WHEN** a child adds, deletes, rewrites, or replaces a repository file
- **THEN** the check reports `error`, the path/value detail is redacted to safe relative evidence, later selected commands do not run, and the runner does not overwrite user work

#### Scenario: Platform cannot guarantee descendant cleanup
- **WHEN** the host lacks the tested process-tree primitive required to observe a descendant that detaches with a new session
- **THEN** selected execution reports `unsupported` before child code runs rather than claiming equivalent containment

#### Scenario: Process observability disappears
- **WHEN** the initial process map is unavailable or omits the runner
- **THEN** the check fails before child execution
- **AND WHEN** a later map is unreadable, malformed, or omits a live direct or previously observed descendant PID
- **THEN** the check reports an infrastructure `error`, freezes/kills every known PID, and states that cleanup of an unobserved descendant cannot be proved rather than reporting `pass`

#### Scenario: Descendant detaches into another session
- **WHEN** a child spawns a delayed descendant that calls `setsid()`, the direct process exits, and the supported executor observes that owned descendant
- **THEN** the executor immediately reports the surviving-descendant infrastructure condition, freezes the observed owned tree before another cleanup window, terminates and reaps it, and only then returns `error`
- **AND** the recorded descendant PID is no longer live and a post-result release signal cannot produce a delayed repository write

#### Scenario: Descendant forks during cleanup acquisition
- **WHEN** an owned process forks between an ownership scan and delivery of the stop signal
- **THEN** bounded recursive/adopted-child rescans freeze and terminate the newly observed PID or cleanup reports non-convergence or lost observability
- **AND** the runner never reports `pass` from incomplete cleanup evidence

#### Scenario: Caller points temporary directory into the repository
- **WHEN** `TMPDIR`, `TMP`, or `TEMP` resolves inside the source tree
- **THEN** the runner creates its private temporary state in a verified external location or exits `2` before child execution

### Requirement: Result model and reports are deterministic and truthful
The runner SHALL expose `text`, schema-v1 `json`, and `markdown` projections of one ordered result model with `pass`, `fail`, `error`, `unsupported`, and `not-selected`. Reports MUST omit timestamps, durations, absolute/temporary paths, secret environment values, and successful raw logs; failure evidence MUST be bounded and redacted.

#### Scenario: Repeated evidence is byte-stable
- **WHEN** the repository, revision, matrix, selection, observed environment identity, and fixture output are unchanged
- **THEN** two JSON reports and two Markdown reports are byte-identical

#### Scenario: Observed environment is scoped
- **WHEN** a report includes revision, Python, operating-system, architecture, or tool version evidence
- **THEN** it labels those values as the observed host only and makes no broader compatibility or performance claim

#### Scenario: Failure output contains sensitive-looking data
- **WHEN** a failure contains a token-like value, home path, temporary path, POSIX path, Windows drive path, or UNC path
- **THEN** all report formats replace the value with stable redacted/repository-relative text and remain within the configured output bound

#### Scenario: Matrix-owned public text is unsafe
- **WHEN** a global/check evidence scope or human boundary contains a secret-like assignment, ANSI/control character, or absolute path including one with spaces
- **THEN** matrix parsing exits `2` without reflecting the unsafe field and no check runs

#### Scenario: Markdown is accessible without color
- **WHEN** Markdown evidence is rendered or read as plain text
- **THEN** every check has an explicit status word and scope in a textual table
- **AND** the report states that linguistic, pedagogical, rendered-accessibility, bidi, and provenance reviews remain human gates

#### Scenario: Non-ASCII repository path is diagnosed
- **WHEN** a safe check or fixture uses a repository-relative non-ASCII path
- **THEN** the report preserves valid Unicode without emitting an absolute path or changing result order

### Requirement: CLI selection and compatibility remain stable
`tools/run_quality.py` SHALL accept one named profile or explicit repeated check IDs, optional changed-scope input where supported, and one output format. Existing `validate_book.py`, `validate_curriculum.py`, `parity_review.py`, plugin paths, and their direct exit behavior MUST remain callable independently.

#### Scenario: Unknown selection is a usage error
- **WHEN** a caller selects an unknown profile/check, combines mutually exclusive selection modes, or applies changed scope to an unsupported selection
- **THEN** the runner exits `2` before executing a check and prints a stable actionable diagnostic

#### Scenario: Changed scope does not hide shared checks
- **WHEN** CI selects `core --changed-from <base>` for a pull request
- **THEN** only the generic book adapter receives the base revision
- **AND** unittests, curriculum, and parity still execute their full contracts

#### Scenario: Existing direct commands remain usable
- **WHEN** a maintainer invokes an existing validator or explicit plugin command directly
- **THEN** its public CLI and ownership remain unchanged and do not require the aggregate runner

### Requirement: CI consumes named evidence profiles with least privilege
The book-quality workflow SHALL invoke the `core` profile on pull requests and main pushes, invoke each domain profile in a separately named bounded job, retain SHA-pinned actions and read-only contents permission, and contain no `continue-on-error` that converts required evidence to success.

#### Scenario: Curriculum cannot drift out of CI
- **WHEN** the workflow contract tests compare `core` with the matrix
- **THEN** removal of curriculum validation from the profile or replacement with a narrower unregistered command fails the tests

#### Scenario: Generic success does not imply domain success
- **WHEN** only `core` has run or a domain job is absent/not selected
- **THEN** every domain check remains `not-selected` and no report says its network/compiler/package/ABI behavior passed

#### Scenario: Domain job invokes exact profile
- **WHEN** a domain job runs
- **THEN** its name and command identify exactly one of `network-domain`, `cpp-domain`, or `rust-domain`
- **AND** a failure/unsupported result fails that job rather than being waived

#### Scenario: Every workflow action is immutable
- **WHEN** any `uses:` entry is added or changed
- **THEN** the workflow contract requires its complete ref to be exactly a 40-hex commit SHA and rejects a tag, branch, or partial hash
- **AND** whitespace before the colon, quoted `uses` keys, and inline YAML mappings cannot evade the check

#### Scenario: Heavy native evidence remains scoped
- **WHEN** the lightweight domain profiles pass
- **THEN** the report claims only their declared plugin checks and does not claim full C++/Rust builds, wheels, sanitizers, ABI matrices, or unexecuted platforms
