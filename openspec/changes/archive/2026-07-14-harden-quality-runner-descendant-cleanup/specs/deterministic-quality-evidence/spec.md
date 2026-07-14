## MODIFIED Requirements

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
