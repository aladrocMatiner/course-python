## MODIFIED Requirements

### Requirement: Quality matrix is versioned and closed
The repository SHALL define a standard-library-readable matrix with one
supported schema version, globally bounded resources, unique stable check IDs,
explicit profiles, a closed adapter vocabulary, and repository-relative
adapter fields. The parser MUST enforce the mandatory `core`,
`learning-bridges`, `environment-domain`, `network-domain`, `cpp-domain`,
`rust-domain`, `patterns-domain`, `all-automated`, and `handoff`
memberships/bindings before execution and MUST reject arbitrary shell text,
unknown fields, duplicate IDs, missing/profile-tampered references, traversal,
unsafe symlinks, wildcard selection, invalid prerequisites, and limits outside
documented hard maxima.

#### Scenario: Core matrix is valid
- **WHEN** the schema-v1 matrix is loaded
- **THEN** `core` selects tool unittests, curriculum validation, parity validation, and generic book validation in deterministic order
- **AND** every referenced check has one known adapter and bounded resources

#### Scenario: Domain selection is explicit
- **WHEN** a maintainer selects `learning-bridges`, `environment-domain`, `network-domain`, `cpp-domain`, `rust-domain`, or `patterns-domain`
- **THEN** only the exact declared plugin check is selected with no implicit domain work
- **AND** all other domain checks report `not-selected`

#### Scenario: Patterns binding is exact
- **WHEN** the repository matrix is validated
- **THEN** `patterns-domain` binds exactly one `book-plugin` check to `appendix-software-design-patterns/tools/bookcheck_plugin.py`
- **AND** its quality-matrix outer timeout/output limits are exactly 120 seconds/512 KiB, while `all-automated` and `handoff` include it once before `openspec-strict` without changing the relative order or binding of existing checks

#### Scenario: Patterns selection does not impersonate network evidence
- **WHEN** only `patterns-domain` is selected
- **THEN** `patterns:core-suite` and `patterns:network-suite` may execute through the one Appendix C plugin while `network-domain` remains `not-selected`
- **AND** the result cannot report Chapter 23's `network:network-suite` as passed

#### Scenario: Malformed matrix fails closed and recovers
- **WHEN** a fixture adds an unknown key, duplicate ID, missing reference, arbitrary command, escaping path, unsafe symlink, excessive limit, removes `patterns-domain`, or rebinds it to another plugin
- **THEN** the runner exits `2` before running repository code and names only the stable configuration error
- **AND WHEN** the fixture is restored to the schema
- **THEN** selection succeeds without a suppression or migration flag

### Requirement: CI consumes named evidence profiles with least privilege
The book-quality workflow SHALL invoke the `core` profile on pull requests and
main pushes, invoke each `learning-bridges`, `environment-domain`,
`network-domain`, `cpp-domain`, `rust-domain`, and `patterns-domain` profile in
a separately named bounded job, retain SHA-pinned actions and read-only
contents permission, and contain no `continue-on-error` that converts required
evidence to success.

#### Scenario: Curriculum cannot drift out of CI
- **WHEN** the workflow contract tests compare `core` with the matrix
- **THEN** removal of curriculum validation from the profile or replacement with a narrower unregistered command fails the tests

#### Scenario: Generic success does not imply domain success
- **WHEN** only `core` has run or a domain job is absent/not selected
- **THEN** every domain check remains `not-selected` and no report says its learning/environment/network/pattern/compiler/package/ABI behavior passed

#### Scenario: Domain job invokes exact profile
- **WHEN** a domain job runs
- **THEN** its name and command identify exactly one of `learning-bridges`, `environment-domain`, `network-domain`, `cpp-domain`, `rust-domain`, or `patterns-domain`
- **AND** a failure or unsupported result fails that job rather than being waived

#### Scenario: Patterns CI remains local and bounded
- **WHEN** the `patterns-domain` job runs
- **THEN** it uses no secret, public target, package installation, external service, elevated permission, or fixed sleep for readiness
- **AND** the minimal plugin launches no second process manager and relies on `validate_book.py` for the configured 30-second per-check timeout, 64 KiB output limit, plugin-contract execution, descendant cleanup, and repository mutation snapshot
- **AND** the quality-matrix runner retains the real 120-second/512 KiB outer process limits

#### Scenario: Every workflow action is immutable
- **WHEN** any `uses:` entry is added or changed
- **THEN** the workflow contract requires its complete ref to be exactly a 40-hex commit SHA and rejects a tag, branch, or partial hash
- **AND** whitespace before the colon, quoted `uses` keys, and inline YAML mappings cannot evade the check

#### Scenario: Heavy or optional evidence remains scoped
- **WHEN** lightweight domain profiles pass
- **THEN** the report claims only their declared plugin checks and does not claim production network readiness, broad compatibility/performance, external brokers/services, full C++/Rust builds, wheels, sanitizers, ABI matrices, or unexecuted platforms
