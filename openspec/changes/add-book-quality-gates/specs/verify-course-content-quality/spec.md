## ADDED Requirements

### Requirement: Deterministic standard-library quality CLI

The repository SHALL provide `tools/validate_book.py` as a CPython 3.11+ standard-library-only, read-only entry point with stable text and JSON diagnostics.

#### Scenario: Full validation succeeds
- **WHEN** a contributor runs `python -B tools/validate_book.py` from any working directory on a conforming repository
- **THEN** the validator discovers the repository from its script path, runs every generic rule, compares the reviewed baseline, and exits zero
- **AND** it creates or modifies no source, cache, bytecode, baseline, inventory, or generated artifact

#### Scenario: Diagnostics are deterministic and safe
- **WHEN** the same failing tree is validated twice in text or JSON mode
- **THEN** diagnostics have stable ordering, schema version, rule ID, severity, repository-relative path, optional location, safe message, and remediation
- **AND** they contain no absolute path, timestamp, platform traceback, secret value, or learner data

#### Scenario: Configuration or internal failure is distinct
- **WHEN** configuration, diagnostic schema, or internal processing is invalid
- **THEN** the command exits `2` with an actionable safe diagnostic
- **AND** ordinary quality violations exit `1` while a clean baseline-aware run exits `0`

### Requirement: Stable multilingual content discovery

The validator SHALL discover each non-root chapter or appendix with canonical `README.md` and require its Spanish, Catalan, Swedish, and Arabic siblings without changing stable directory names or URLs.

#### Scenario: Complete unit is accepted
- **WHEN** a unit contains `README.md`, `README.es.md`, `README.ca.md`, `README.sv.md`, and `README.ar.md` under its stable directory
- **THEN** the five files are associated as one unit with English as the canonical source

#### Scenario: Missing or misnamed language is rejected
- **WHEN** a discovered unit lacks a required sibling or uses an unrecognized localized filename
- **THEN** validation identifies the unit and exact missing or unexpected file

#### Scenario: Stable content path is removed or renamed
- **WHEN** changed-scope discovery observes a deleted or renamed chapter/appendix path without an approved exact migration entry
- **THEN** validation fails rather than treating the replacement as an unrelated new unit

#### Scenario: Discovery cannot escape the repository
- **WHEN** a configured root, exclusion, symlink, or unit path resolves outside the repository
- **THEN** validation fails closed without reading the external target

### Requirement: Root mirrors and localized navigation

The validator SHALL enforce root English mirroring, standard unit language selectors, language-correct root navigation, and target-before-index integration.

#### Scenario: Root English mirror is exact
- **WHEN** root `README.md` and `README.en.md` are compared
- **THEN** they MUST be byte-for-byte identical

#### Scenario: Unit selector is valid
- **WHEN** a unit language file is scanned
- **THEN** its selector lists English, Spanish, Catalan, Swedish, and Arabic in the standard order
- **AND** every link stays in the unit, targets the matching sibling, and the current language is not a self-link

#### Scenario: Localized index target is valid
- **WHEN** a root index links a chapter or appendix
- **THEN** the target exists and uses the reader's language when that sibling exists
- **AND** canonical English navigation appears identically in both English root mirrors

#### Scenario: Concurrent advanced chapters are integrated
- **WHEN** chapters 23, 24, or 25 are added to root indexes
- **THEN** only existing targets are linked, implemented order is 23 then 24 then 25 before appendices, and any later implemented chapters are preserved

### Requirement: Offline internal link and anchor validation

The validator SHALL resolve local Markdown and HTML links, images, fragments, and explicit anchors deterministically without fetching external URLs.

#### Scenario: Local path and fragment resolve
- **WHEN** a link contains relative segments, percent encoding, Unicode, query text, or a heading fragment
- **THEN** its normalized target remains inside the repository and the target path and anchor exist

#### Scenario: Broken or escaping target fails
- **WHEN** a local link/image is missing, has an unknown fragment, or traverses outside the repository
- **THEN** validation reports the source location and normalized safe target without opening an external path

#### Scenario: External URL remains offline
- **WHEN** an HTTP or HTTPS link has valid syntax
- **THEN** the validator does not request it and records no availability claim

#### Scenario: Code examples do not create links
- **WHEN** link-like text occurs inside an inline-code span or fenced block
- **THEN** the link scanner ignores it while still checking the enclosing Markdown structure

### Requirement: Markdown, RTL, and machine-checkable accessibility structure

The validator SHALL enforce conservative Markdown hierarchy, balanced fenced blocks, Arabic RTL wrapping, descriptive links, image alternatives, and readable table structure while identifying semantic accessibility review as a human responsibility.

#### Scenario: Heading hierarchy is accessible
- **WHEN** a content file is scanned
- **THEN** it contains one H1, does not skip heading levels, and produces unambiguous deterministic anchors

#### Scenario: Fences are structurally valid
- **WHEN** backtick or tilde fences contain Markdown-like text
- **THEN** the scanner respects delimiter type and length, shields fenced content from prose rules, and rejects an unclosed or mismatched fence

#### Scenario: Arabic outer wrapper is valid
- **WHEN** `README.ar.md` is scanned
- **THEN** exactly one outer `<div dir="rtl">` wrapper encloses the document and is balanced
- **AND** code, commands, paths, identifiers, and fenced metadata remain parseable left-to-right

#### Scenario: Link and image text is inspectable
- **WHEN** prose contains a link or meaningful image
- **THEN** link text and image alt text are non-empty and descriptive rather than positional or generic
- **AND** a meaningful visual has a nearby prose equivalent while a decorative visual has the documented marker and empty alt

#### Scenario: Complex table has an alternative
- **WHEN** a Markdown table has no header separator or exceeds the configured narrow-screen complexity threshold without a text/list alternative
- **THEN** validation fails with the exact missing structural requirement

#### Scenario: Semantic accessibility cannot be inferred
- **WHEN** structural checks pass or heuristic wording produces a review signal
- **THEN** the result does not claim that alt prose, table alternatives, color usage, or the full lesson is accessible
- **AND** a human accessibility/content review remains required

### Requirement: Explicit fenced-block classification

Every new or changed fenced block SHALL declare a language token and exactly one of `runnable`, `expected-error`, `compile-only`, `source-ref`, `todo`, `illustrative`, or `output`, with versioned adjacent metadata where required; exact untouched legacy findings remain governed by the baseline ratchet.

#### Scenario: Runnable and output are paired correctly
- **WHEN** a `python runnable` fence has observable expected output
- **THEN** an immediately associated `output` fence or declared expectation defines the normalized comparison
- **AND** prose may call the block runnable only after its accepted execution check passes

#### Scenario: Expected error declares recovery evidence
- **WHEN** a `python expected-error` fence is present
- **THEN** metadata declares the expected diagnostic substring, execution must exit non-zero within its bound, and surrounding prose explains recovery

#### Scenario: Non-executable classes remain inert
- **WHEN** a fence is classified `todo`, `illustrative`, or `output`
- **THEN** generic validation never executes it and rejects prose that falsely marks it as a verified runnable example

#### Scenario: Compile-only and source-reference claims are explicit
- **WHEN** a block is `compile-only` or `source-ref`
- **THEN** Python compile-only content is compiled without execution
- **AND** other languages or partial/dependency-heavy content name an in-repository companion path and stable verifier/plugin check ID

#### Scenario: Classification metadata is invalid
- **WHEN** a changed fence has no language, no class, multiple classes, an unknown class, duplicate/unknown metadata keys, or an orphan `output`
- **THEN** validation fails with the fence location and accepted contract

#### Scenario: Language siblings expose corresponding evidence
- **WHEN** the five files of one unit are compared
- **THEN** classification order and companion-source identities are emitted as structural parity checks
- **AND** equal sequences are never reported as proof of semantic translation parity

### Requirement: Bounded trusted-Python snippet execution

The generic validator SHALL execute only opted-in trusted Python snippets under documented temporary-directory, environment, time, input, output, and process-cleanup bounds and SHALL state that those controls are not a security sandbox.

#### Scenario: Safe runnable succeeds in isolation
- **WHEN** an eligible `python runnable` block is executed
- **THEN** CPython runs with `-I -B`, no stdin, a minimal allowlisted environment, an empty temporary current directory, and no repository write access by contract
- **AND** normalized exit/output matches the declared expectation and the temporary tree is removed

#### Scenario: Expected failure is observed
- **WHEN** an eligible `python expected-error` block exits non-zero with its declared diagnostic within the bound
- **THEN** validation accepts the expected failure while retaining its recovery explanation requirement

#### Scenario: Execution exceeds a safety bound
- **WHEN** a snippet times out, spawns a surviving descendant, exceeds 64 KiB combined output, attempts a path escape, or uses an obviously forbidden network/process/privilege/destructive operation
- **THEN** validation terminates the process group where applicable, fails the snippet, cleans its temporary tree, and emits no captured secret value

#### Scenario: Unsupported execution is delegated
- **WHEN** shell, network, multi-process, package-install, dependency-bearing, C++, or Rust behavior needs execution
- **THEN** the generic runner refuses it and requires `source-ref` plus a domain companion test/plugin

#### Scenario: Sandbox limitation is visible
- **WHEN** execution documentation or CI policy is reviewed
- **THEN** it explicitly says snippets are trusted repository input and the runner is not safe for hostile code
- **AND** CI grants no elevated token, secret, or write permission to snippet execution

### Requirement: Traceable source references and domain plugins

The validator SHALL verify companion-source paths and stable check IDs and SHALL provide a versioned, explicitly invoked, fail-closed plugin protocol for chapter-specific verification.

#### Scenario: Source reference is traceable
- **WHEN** a `source-ref` block names a repository-relative file and check ID
- **THEN** the file exists inside the repository and the named built-in, unittest, or registered plugin check exists
- **AND** the report distinguishes “registered/not run” from “executed/passed”

#### Scenario: Valid plugin reports domain checks
- **WHEN** an explicitly selected plugin registers a unique compatible ID and returns schema-valid diagnostics within its bound
- **THEN** results are namespaced, deterministic, and merged without changing generic diagnostics

#### Scenario: Plugin fails closed
- **WHEN** a plugin has an API mismatch, duplicate ID, unmet prerequisite, crash, timeout, malformed/oversized output, path escape, or source-tree mutation
- **THEN** validation fails with exit `2` or its specified domain failure and never reports the plugin passed

#### Scenario: Plugin cannot waive root quality
- **WHEN** a plugin attempts to suppress, downgrade, or replace a generic rule
- **THEN** the protocol rejects the attempt and preserves the root diagnostic

#### Scenario: Unrequested plugin is not implied
- **WHEN** generic validation runs without a domain plugin
- **THEN** it never reports that plugin's compiler, network, package, compatibility, or performance checks as passed

### Requirement: Repository artifact and sensitive-data hygiene

The validator SHALL inspect tracked, untracked, and ignored repository paths for unexpected generated artifacts and SHALL inspect bounded text for suspected live credentials or learner data without deleting files or printing matched values.

#### Scenario: Generated artifact is present
- **WHEN** an unexpected cache, bytecode, virtual environment, coverage/test output, build/dist tree, package, native binary, Cargo/CMake output, key/certificate, editor file, or platform trash exists even under an ignored path
- **THEN** validation identifies its safe relative path and artifact rule

#### Scenario: Suspected sensitive value is present
- **WHEN** a bounded text scan detects a likely live credential or personal learner-data pattern
- **THEN** the diagnostic reports only rule and location with the value redacted
- **AND** validation never uploads, rewrites, deletes, or echoes the suspected value

#### Scenario: Deliberately fake fixture is allowed narrowly
- **WHEN** a teaching fixture contains an unmistakably fake value and its exact path/rule is allowlisted
- **THEN** only that occurrence is accepted and repository-wide glob suppression is rejected

#### Scenario: Hygiene run is read-only and bounded
- **WHEN** large or binary content, unusual filenames, or ignored paths are encountered
- **THEN** reads and output remain bounded, NUL-delimited Git paths are handled, binaries are not dumped, and the repository tree is unchanged

### Requirement: Changed-scope legacy baseline ratchet

The repository SHALL maintain a reviewed exact-fingerprint baseline that permits unchanged legacy findings while preventing new debt, wildcard suppression, stale waivers, and reintroduction.

#### Scenario: Exact reviewed debt remains
- **WHEN** a full run finds the same rule version, relative path, normalized construct digest, and duplicate ordinal recorded in the baseline
- **THEN** the issue remains visible as accepted legacy debt and does not fail unrelated untouched work

#### Scenario: New or changed debt appears
- **WHEN** a finding has no exact reviewed fingerprint or occurs in a new/changed construct selected by `--changed-from`
- **THEN** validation fails even if another issue of the same rule already exists elsewhere

#### Scenario: Legacy issue is fixed
- **WHEN** a previously baselined finding disappears
- **THEN** validation reports the baseline entry stale until it is deleted in the same change
- **AND** a later reintroduction fails because the fingerprint is no longer accepted

#### Scenario: Baseline update is reduction-only
- **WHEN** `--update-baseline` is requested
- **THEN** it may remove resolved exact entries but refuses to add, broaden, rewrite, or wildcard-suppress a finding

#### Scenario: Baseline contract changes
- **WHEN** rule, config, or fingerprint schema versions differ from baseline metadata
- **THEN** validation exits `2` and requires an explicit reviewed migration rather than silently accepting debt

### Requirement: Attribution inventory and neutral provenance audit

The repository SHALL maintain a versioned `ATTRIBUTIONS.toml` inventory for adapted or third-party material and SHALL audit evidence/notice consistency without asserting infringement, ownership, or license compatibility.

#### Scenario: Complete provenance record is accepted
- **WHEN** an inventory entry covers an existing path and its declared status has all required source, author/holder, license, notice, adaptation, and review fields
- **THEN** structural validation accepts the record and checks that any required visible notice exists

#### Scenario: Provenance decision is unresolved
- **WHEN** an existing candidate or explicit marker has status `review-required`
- **THEN** the diagnostic says “provenance review required” and identifies the missing evidence
- **AND** it does not call the material copied, illegal, incompatible, or infringing

#### Scenario: New unresolved material is introduced
- **WHEN** new or changed adapted prose, exercise, dataset, diagram, or other covered asset is declared, marked, or detected by the documented asset inventory rule and lacks a complete reviewed record
- **THEN** changed-scope validation blocks publication pending a human provenance/license decision

#### Scenario: Audit remains offline and bounded
- **WHEN** an entry provides an external source URL or license reference
- **THEN** validation checks syntax and local notice consistency but does not fetch, infer rights, or issue a legal conclusion

#### Scenario: Inventory is not the public notice
- **WHEN** a license requires attribution near material or in a visible dedicated section
- **THEN** a TOML entry alone is insufficient and the validator requires the recorded notice location to exist

### Requirement: Least-privilege continuous integration

The repository SHALL run book-quality unit tests and baseline-aware generic validation in bounded, least-privilege CI using SHA-pinned actions and no third-party Python runtime dependencies.

#### Scenario: Pull request validates changed scope
- **WHEN** CI runs for a pull request
- **THEN** it checks out enough history to resolve the base commit, runs `unittest`, invokes `--changed-from` for generic quality, and runs `git diff --check` for the contribution
- **AND** job permissions are read-only and no example receives a secret or elevated token

#### Scenario: Protected branch validates full state
- **WHEN** CI runs after a protected-branch push
- **THEN** it runs the full baseline-aware generic audit and fails on tests, config, baseline, or quality errors

#### Scenario: CI action and execution are bounded
- **WHEN** workflow dependencies and jobs are inspected
- **THEN** actions use full commit SHAs with human-readable version comments, jobs have time limits, and Python checks install no third-party package

#### Scenario: Domain coverage is not fabricated
- **WHEN** generic CI does not provision a chapter's network/native/Rust prerequisites or invoke its plugin
- **THEN** the report says the domain checks were not run and never marks them passing

### Requirement: Behavior-focused unittest verification

The quality capability SHALL include deterministic standard-library `unittest` coverage for every rule family, failure boundary, and diagnostic safety property using isolated temporary repositories.

#### Scenario: Positive and negative fixtures cover each rule
- **WHEN** `python -B -m unittest discover -s tools/tests -v` runs
- **THEN** each normative rule has a conforming fixture and at least one minimal failing fixture asserting its stable rule ID and remediation

#### Scenario: Resource and failure boundaries are tested
- **WHEN** runner, plugin, Git, parser, baseline, hygiene, or attribution tests execute
- **THEN** timeout, output cap, malformed input, unusual path, process cleanup, redaction, and read-only behavior are exercised deterministically without network access

#### Scenario: Tests are repository-clean
- **WHEN** the suite completes successfully or after an induced failure
- **THEN** temporary trees and child processes are cleaned, no bytecode/cache/artifact remains, and tests are order-independent

### Requirement: Generic and domain validator ownership is coordinated

If this change is approved, the active network, C++, and Rust chapter changes SHALL consume the root generic quality contract and retain only domain-specific verification or thin plugin adapters without weakening any accepted scenario.

#### Scenario: Network proposal is reconciled
- **WHEN** `add-python-network-programming-chapter` is implemented after this capability
- **THEN** root rules own Markdown, links, selectors, structural parity, accessibility, snippet metadata, and generic hygiene
- **AND** its plugin/tests retain bounded localhost TCP, UDP, TLS, selector, and asyncio lifecycle verification
- **AND** exact root configuration allows only its declared public didactic PEM fixtures under `chapter-23-network-programming/examples/certificates/`, while a neighboring, generated, or undeclared key still fails hygiene with its value redacted

#### Scenario: C++ proposal is reconciled
- **WHEN** `add-python-cpp-integration-chapter` is implemented after this capability
- **THEN** root rules own generic documentation and hygiene checks
- **AND** its tools retain compiler/CMake, debug/release, memory, GIL/concurrency, sdist/wheel, typing, embedding, ABI, and native artifact verification

#### Scenario: Rust proposal is reconciled
- **WHEN** `add-python-rust-integration-chapter` is implemented after this capability
- **THEN** root rules own generic documentation and hygiene checks
- **AND** its tools retain rustup/Cargo/fmt/clippy, PyO3, concurrency, maturin, typing, wheel, ABI, and Rust artifact verification

#### Scenario: Another chapter lands first
- **WHEN** a chapter local validator is already implemented before root migration
- **THEN** it remains callable until equivalent root tests pass and ownership is migrated explicitly
- **AND** no accepted behavior is removed merely to eliminate duplicate code

#### Scenario: Multilingual remediation consumes structural signals
- **WHEN** a course-wide translation restoration change uses this capability
- **THEN** it may consume file, selector, link, source-reference, and classification-sequence diagnostics
- **AND** it retains fluent linguistic and technical review because automation does not prove semantic parity
