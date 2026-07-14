## 1. Freeze the matrix and report contracts

- [x] 1.1 Add schema-v1 `tools/quality_matrix.toml` and a fail-closed parser.
  - **Objective:** Make check/profile identity and bounds reviewable without accepting arbitrary commands.
  - **Deliverables:** Matrix plus parser/model code in `tools/run_quality.py`.
  - **Validation:** Tests cover valid and tampered mandatory profiles, unknown keys/adapters, duplicates, missing refs, unsafe paths/symlinks, arbitrary argv, invalid prerequisites, and hard maxima.
  - **Risk:** A flexible matrix becomes a command launcher; keep a closed adapter vocabulary and exact fields.
  - **Scope:** M.

- [x] 1.2 Implement the ordered result model and text/JSON/Markdown renderers.
  - **Objective:** Represent `pass|fail|error|unsupported|not-selected` once without volatile or unsafe evidence.
  - **Deliverables:** Schema-v1 JSON and accessible text/Markdown projections.
  - **Validation:** Golden/behavior tests prove byte stability, ordering, Unicode, ANSI/token/path rejection or redaction (including spaced POSIX/drive/UNC paths), no absolute/temp paths, no timestamps/durations, and an explicit human-gate boundary.
  - **Scope:** M.

## 2. Implement bounded orchestration

- [x] 2.1 Add bounded child execution and repository mutation detection.
  - **Objective:** Close stdin, avoid a shell, bound time/output, control descendants, and fail-detect source writes.
  - **Deliverables:** Executor with minimal environment, process-tree capability check, content-hash snapshot, and temporary-output cleanup.
  - **Validation:** Positive, timeout, strict persisted-byte overflow, crash, process-group and detached-session descendants, empty/partial/malformed `/proc` maps, malicious in-repo TMPDIR, unavailable-platform, add/delete/rewrite, and cleanup/recovery fixtures pass without restoring user files.
  - **Risk:** This is trusted-code accident reduction, not a hostile-code sandbox; docs and diagnostics say so.
  - **Scope:** L.

- [x] 2.2 Add explicit selection, exit aggregation, prerequisites, and changed-scope routing.
  - **Objective:** Execute named evidence without converting missing/incomplete work into success.
  - **Deliverables:** `--profile`, repeated `--check`, `--changed-from`, `--format`, stable exits `0|1|2`, and adapter dispatch.
  - **Validation:** Tests cover default/explicit/mutually exclusive/unknown selection, ordinary failure continuation, infrastructure precedence, unsupported prerequisites and recovery, and changed scope reaching only generic book validation.
  - **Scope:** M.

- [x] 2.3 Implement adapters for the existing quality owners.
  - **Objective:** Aggregate, not duplicate, unittests, curriculum, parity, generic/plugin validation, OpenSpec strict validation, and whitespace evidence.
  - **Deliverables:** Closed adapters preserving the existing CLIs and direct exit behavior.
  - **Validation:** Adapter fixtures assert exact argv, plugin paths, no `shell=True`, no unselected execution, and truthful scope for lightweight versus full native evidence.
  - **Scope:** M.

## 3. Align profiles, CI, and maintainer handoff

- [x] 3.1 Define and contract-test `core`, three domain profiles, and `handoff`.
  - **Objective:** Remove manual matrix drift and add the missing curriculum gate.
  - **Deliverables:** Exact profile membership/order and tests that compare it with adapter/plugin contracts.
  - **Validation:** `core` contains tools/curriculum/parity/book; each domain selects one explicit plugin; handoff adds strict OpenSpec/diff; unselected checks remain visible.
  - **Scope:** S.

- [x] 3.2 Route least-privilege CI through named profiles.
  - **Objective:** Make pull-request/push/domain jobs consume the same matrix without broadening authority.
  - **Deliverables:** Updated `.github/workflows/book-quality.yml` and workflow contract tests.
  - **Validation:** Every block/quoted/inline YAML `uses` ref is exactly 40 hex; `contents: read`, job timeouts, PR changed scope, push full scope, separate named domain profiles, no `continue-on-error`, and parser-enforced curriculum/tests-in-core assertions pass.
  - **Risk:** CI configuration is provisioned evidence only until a hosted run executes; local review must not mark unexecuted platforms passed.
  - **Scope:** M.

- [x] 3.3 Update maintainer guidance and evidence ownership.
  - **Objective:** Replace copied command/count tables with reproducible runner output while preserving human review language.
  - **Deliverables:** `tools/BOOK_QUALITY_REVIEW.md`, the book-quality skill CI reference, and change implementation review notes.
  - **Validation:** Docs name direct-command fallback, report formats, observed-host scope, trusted-code limits, domain selection, and pending pedagogy/accessibility/bidi/provenance gates.
  - **Scope:** S.

## 4. Integrated verification

- [x] 4.1 Run runner-specific and full tooling regression suites.
  - **Objective:** Demonstrate every happy, edge, failure, and recovery scenario without source mutation.
  - **Deliverables:** Passing `test_run_quality.py`, all `tools/tests`, and deterministic repeat-output evidence.
  - **Validation:** Two identical core JSON/Markdown projections match byte-for-byte; negative fixtures return their specified states/exits; repository snapshot is unchanged.
  - **Scope:** M.

- [x] 4.2 Run the real profiles and reconcile evidence truthfully.
  - **Objective:** Prove local core/domain/handoff behavior on the current host without widening compatibility claims.
  - **Deliverables:** Exact observed command/result matrix in `IMPLEMENTATION_REVIEW.md`.
  - **Validation:** Available profiles pass or record prerequisite-specific `unsupported`; direct validators agree; no heavy native/platform claim is inferred.
  - **Scope:** M.

- [x] 4.3 Complete OpenSpec and repository hygiene checks.
  - **Objective:** Leave an apply-complete, coherent, reversible change.
  - **Deliverables:** Completed checklist only after evidence passes.
  - **Validation:** `openspec validate add-deterministic-quality-evidence-runner --strict`; strict validation of coordinated active changes; `openspec doctor`; `git diff --check`; no generated reports/caches/artifacts.
  - **Scope:** S.
