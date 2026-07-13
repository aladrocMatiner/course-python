## Phase 1: Freeze contracts with tests

### Task 1.1: Define configuration and diagnostic schemas

- [x] 1.1 Implement versioned TOML configuration plus deterministic text/JSON diagnostic models.
- **Objective:** Make every later rule consume one explicit, reviewable contract.
- **Deliverables:** `tools/book_quality.toml` and schema/model code in `tools/validate_book.py`.
- **Validation:** Unit tests reject unknown keys/schema versions, path escapes, wildcard suppressions, malformed limits, and unstable/absolute diagnostic fields.
- **Risk:** An over-flexible config becomes a suppression system; allow only exact exclusions and bounded values.
- **Scope:** M.

### Task 1.2: Build the isolated unittest harness

- [x] 1.2 Add positive and negative temporary-repository builders and CLI capture helpers.
- **Objective:** Test behavior without mutating or depending on the real book tree.
- **Deliverables:** `tools/tests/test_validate_book.py` and minimal byte-sensitive fixtures under `tools/tests/fixtures/` only where needed.
- **Validation:** `python -B -m unittest discover -s tools/tests -v` leaves no cache, temp, or repository artifacts and is order-independent.
- **Scope:** M.

### Task 1.3: Implement repository discovery and read-only guarantees

- [x] 1.3 Discover root indexes, units, changed paths, Git state, and safe repository-relative paths.
- **Objective:** Establish a deterministic scope without following symlinks outside the repository.
- **Deliverables:** Discovery/change-scope functions in `tools/validate_book.py`.
- **Validation:** Tests cover spaces/non-ASCII paths, NUL-delimited Git output, add/delete/rename, symlink escape, exclusions, foreign working directories, and a before/after tree snapshot.
- **Scope:** M.

## Phase 2: Add generic book and Markdown rules

### Task 2.1: Validate the multilingual unit shape

- [x] 2.1 Enforce canonical English plus Spanish, Catalan, Swedish, and Arabic siblings for every unit.
- **Objective:** Prevent incomplete units and accidental public-link changes.
- **Deliverables:** Unit-structure rule and fixtures.
- **Validation:** Missing, extra/misnamed, deleted, renamed, excluded, and valid unit scenarios emit stable rule IDs.
- **Scope:** S.

### Task 2.2: Validate root mirrors, selectors, and index navigation

- [x] 2.2 Enforce byte-identical root English files, standard selector order/targets, localized root targets, and target-before-index integration.
- **Objective:** Keep every reader in the selected language and avoid dangling navigation.
- **Deliverables:** Mirror/selector/navigation rules and tests.
- **Validation:** Tests cover wrong language, self-link, selector order, root byte drift, missing target, chapters 23→24→25 ordering, appendices, and later preserved chapters.
- **Risk:** Concurrent proposals edit shared indexes; changed-scope diagnostics must identify the conflicting target precisely.
- **Scope:** M.

### Task 2.3: Validate local links, images, and anchors

- [x] 2.3 Resolve Markdown/HTML paths and fragments without network requests or repository escape.
- **Objective:** Catch broken internal learning paths deterministically and offline.
- **Deliverables:** Link/image/anchor scanner and fixtures.
- **Validation:** Tests cover percent encoding, Unicode, duplicate heading slugs, explicit anchors, query/fragment combinations, fenced-code shielding, external URLs, missing targets, and traversal.
- **Scope:** M.

### Task 2.4: Validate headings, fences, RTL, and accessible structure

- [x] 2.4 Add conservative Markdown state-machine rules for document hierarchy and machine-checkable accessibility.
- **Objective:** Make structural readability and Arabic wrapper correctness part of acceptance.
- **Deliverables:** Heading/fence/RTL/alt/link/table rules and documented parser limitations.
- **Validation:** Tests cover one H1, skipped levels, duplicate slugs, fence delimiter/type balance, one outer Arabic RTL wrapper, code shielding, descriptive links, image alt/text equivalent, decorative markers, table headers/alternatives, and heuristic-only review prompts.
- **Risk:** Regex-only parsing can invent failures; use a state machine and adversarial fixtures.
- **Scope:** L.

## Phase 3: Make example claims verifiable

### Task 3.1: Parse and validate the fenced-block taxonomy

- [x] 3.1 Require one language and one accepted classification on new/changed fences and parse adjacent `bookcheck` metadata.
- **Objective:** Ensure readers can tell what can be run, what should fail, and what is only explanatory.
- **Deliverables:** Fence classification/metadata parser plus parity-signal output.
- **Validation:** Tests cover all seven classifications, missing/multiple/unknown classes, duplicate/unknown metadata keys, orphan output, invalid source-ref metadata, legacy baseline behavior, and corresponding sibling sequences.
- **Scope:** M.

### Task 3.2: Implement bounded trusted-Python execution

- [x] 3.2 Execute eligible Python blocks in temporary child processes with strict limits.
- **Objective:** Back generic runnable and expected-error claims with observable execution.
- **Deliverables:** Runner using `-I -B`, minimal environment, no stdin, temp cwd, fixture-copy guard, timeout/process-group cleanup, output cap, and normalized comparisons.
- **Validation:** Tests cover success/output, declared error, unexpected success/failure, timeout, descendant cleanup, output overflow, attempted path escape, obvious unsafe operation rejection, no bytecode, and no source-tree writes.
- **Risk:** The runner is not a security sandbox; tests and docs must state trusted-input limits prominently.
- **Scope:** L.

### Task 3.3: Implement source-reference verification

- [x] 3.3 Validate companion paths and stable verifier/check IDs for non-inline examples.
- **Objective:** Trace every dependency-heavy or partial code claim to tested source.
- **Deliverables:** `source-ref` resolver, duplicate/reference graph diagnostics, and tests.
- **Validation:** Tests cover existing/missing/escaping path, renamed verifier, uncovered source, localized identity drift, and a verifier reported as not run versus passed.
- **Scope:** M.

### Task 3.4: Implement the chapter plugin protocol

- [x] 3.4 Add versioned registration and bounded child-process dispatch for explicitly selected domain plugins.
- **Objective:** Reuse root diagnostics while isolating network/native/Rust verification ownership.
- **Deliverables:** Registry/context protocol, `--plugin`, schema validation, namespacing, preflight, and a fixture plugin.
- **Validation:** Tests cover valid results, duplicate IDs, API mismatch, unmet prerequisites, timeout, crash, malformed/oversized output, source-tree mutation detection, path escape, and attempts to suppress root rules.
- **Risk:** Plugins execute trusted repository code; CI permissions and explicit selection remain mandatory.
- **Scope:** L.

## Phase 4: Protect repository and provenance hygiene

### Task 4.1: Add artifact and sensitive-data hygiene rules

- [x] 4.1 Inspect tracked, untracked, and ignored paths and bounded text without deleting or exposing findings.
- **Objective:** Keep generated outputs, credentials, and learner data out of the book.
- **Deliverables:** Artifact patterns, exact allowlist contract, redacted sensitive-data diagnostics, and tests.
- **Validation:** Fixtures cover Python/test/venv/build/CMake/Cargo/native/package outputs, ignored artifacts, fake-secret allowlist, suspected live token redaction, personal-data marker, binary skip, large-file bound, and read-only behavior.
- **Scope:** L.

### Task 4.2: Create the attribution inventory schema

- [x] 4.2 Add a standard-library-readable inventory for provenance decisions and required notices.
- **Objective:** Make attribution evidence reviewable without asking automation to decide legality.
- **Deliverables:** `ATTRIBUTIONS.toml`, schema validation, and neutral status vocabulary.
- **Validation:** Tests cover original/licensed/public-domain/review-required records, field conditions, duplicate/missing paths, source URL syntax, notice location, and messages that never assert infringement or compatibility.
- **Risk:** A schema cannot verify ownership; every substantive status is human-reviewed.
- **Scope:** M.

### Task 4.3: Audit current assets and marked adaptations

- [ ] 4.3 Perform a read-only inventory of images, diagrams, datasets, exercises, and explicit attribution markers.
- **Objective:** Establish known evidence and unresolved review work without silently guessing provenance.
- **Deliverables:** Reviewed initial `ATTRIBUTIONS.toml` entries and a recorded audit summary in the implementation review.
- **Validation:** Every covered path exists; required visible notices are present; unresolved items say “provenance review required”; a human confirms no diagnostic makes a legal accusation.
- **Risk:** Automated candidate discovery misses copied prose; contributor declarations and human review remain required.
- **Scope:** M.

## Phase 5: Adopt a non-growing legacy baseline

### Task 5.1: Implement stable issue fingerprints

- [x] 5.1 Hash rule version, path, normalized construct, and duplicate ordinal independently of line movement.
- **Objective:** Track exact legacy debt without broad suppressions.
- **Deliverables:** Fingerprint algorithm, schema version, and collision/normalization tests.
- **Validation:** Line movement stays stable; content/rule/path changes do not; duplicate constructs are distinct; platform/path separators produce identical IDs.
- **Scope:** M.

### Task 5.2: Implement baseline and changed-scope ratchets

- [x] 5.2 Reject new issues and stale baseline entries while permitting exact untouched debt.
- **Objective:** Let quality improve monotonically from the real legacy state.
- **Deliverables:** Comparator, `--changed-from`, reduction-only `--update-baseline`, and tests.
- **Validation:** Tests cover equal/subset/superset, changed/new/deleted/renamed content, stale removal, reintroduction, config/rule version mismatch, no wildcard waiver, and refusal to add debt through update mode.
- **Risk:** Baseline churn can obscure reviews; JSON is sorted and updates contain deletions only.
- **Scope:** L.

### Task 5.3: Review and check in the initial baseline

- [x] 5.3 Run the full audit, correct parser false positives, and record exact accepted legacy findings.
- **Objective:** Make the current default branch pass without claiming existing debt is good content.
- **Deliverables:** `tools/book_quality_baseline.json` with review commit/schema and a categorized implementation summary.
- **Validation:** Full validation passes; injecting one new issue fails; removing one issue requires baseline deletion; reviewers inspect every rule category and confirm no broad suppression.
- **Scope:** L.

## Phase 6: Integrate proposals and CI

### Task 6.1: Reconcile chapter 23 network verification

- [x] 6.1 Move generic docs/hygiene acceptance to the root contract and define the network-only plugin boundary.
- **Objective:** Avoid duplicate parsers while preserving bounded socket/TLS/async behavior checks.
- **Deliverables:** Updated network proposal/design/tasks/spec, planned `bookcheck_plugin.py` ownership, and exact-path root-config entries for its declared public didactic PEM fixtures under `chapter-23-network-programming/examples/certificates/`.
- **Validation:** Both changes validate strictly; every removed local generic check maps to a root scenario; domain scenarios remain present; only the declared lab certificate/key fixtures are allowed and an adjacent generated or unlisted key still fails with redacted output.
- **Risk:** Apply only after both proposal owners agree on sequencing.
- **Scope:** M.

### Task 6.2: Reconcile chapter 24 C++ verification

- [x] 6.2 Move generic docs/hygiene acceptance to the root contract and retain native build/package/ABI checks.
- **Objective:** Preserve toolchain evidence without maintaining a second Markdown validator.
- **Deliverables:** Updated C++ proposal/design/tasks/spec and planned plugin/source-ref adapter.
- **Validation:** Both changes validate strictly; root checks cover generic scenarios; debug/release, sdist/wheel, typing, embedding, ABI, and artifact tests remain domain-owned.
- **Scope:** M.

### Task 6.3: Reconcile chapter 25 Rust verification

- [x] 6.3 Move generic docs/hygiene acceptance to the root contract and retain Cargo/maturin/package checks.
- **Objective:** Preserve Rust toolchain evidence without duplicating shared quality logic.
- **Deliverables:** Updated Rust proposal/design/tasks/spec and planned plugin/source-ref adapter.
- **Validation:** Both changes validate strictly; root checks cover generic scenarios; fmt/clippy/Cargo, PyO3, wheel, typing, and artifact tests remain domain-owned.
- **Scope:** M.

### Task 6.4: Coordinate multilingual remediation ownership

- [x] 6.4 Expose structural parity diagnostics to the proposed multilingual restoration change without treating them as linguistic proof.
- **Objective:** Keep automation and fluent semantic review complementary.
- **Deliverables:** Cross-change dependency note and shared diagnostic IDs/commands.
- **Validation:** No task claims that counts or structure prove translation quality; the multilingual change retains fluent technical review and all affected changes validate strictly.
- **Scope:** S.

### Task 6.5: Add enforcing least-privilege CI

- [x] 6.5 Run tests, baseline-aware validation, and diff checks on pull requests and protected-branch pushes.
- **Objective:** Make local acceptance reproducible before merging.
- **Deliverables:** `.github/workflows/book-quality.yml` with SHA-pinned actions, `contents: read`, bounded job, base-ref handling, and no third-party Python install.
- **Validation:** Workflow syntax review plus a passing branch run and failing fixture branch; PR uses changed scope, push uses full scope, and no unrequested domain plugin is reported passed.
- **Risk:** Fork code is untrusted; no elevated secrets/permissions and no generic shell snippet execution.
- **Scope:** M.

## Phase 7: Final verification and handoff

### Task 7.1: Run the complete acceptance matrix

- [ ] 7.1 Verify rules, safety bounds, baseline, attribution, CI, and cross-change consistency from a clean checkout.
- **Objective:** Demonstrate every spec scenario with deterministic evidence.
- **Deliverables:** Clean command logs and scenario-to-test mapping in the implementation review.
- **Validation:** `python -B -m unittest discover -s tools/tests -v`; `python -B tools/validate_book.py`; changed-scope negative probe; `openspec validate add-book-quality-gates --strict`; strict validation of reconciled changes; `git diff --check`; clean status without generated artifacts.
- **Scope:** M.

### Task 7.2: Complete human quality review

- [ ] 7.2 Review parser limitations, diagnostic language, provenance wording, and the pedagogical boundary.
- **Objective:** Prevent automated checks from overstating what they establish.
- **Deliverables:** Reviewer sign-off from a book editor/professor, accessibility reviewer, and provenance owner as applicable.
- **Validation:** Sign-off confirms structural parity is only a signal, runnable is evidence-backed, accessibility semantics still receive human review, and no attribution diagnostic asserts infringement.
- **Scope:** S.
