## 1. Maintainer skills

- [x] 1.1 Initialize the exact five repository-local skill directories with skill-creator.
  - **Objective:** Establish valid discoverable skeletons before writing domain instructions.
  - **Deliverables:** `.codex/skills/{verify-python-learning-assets,engineer-python-network-labs,python-packaging-release,engineer-python-native-interop,maintain-book-quality-tooling}/` with generated `agents/openai.yaml`.
  - **Validation:** Folder/name/interface inventory is exact; no initializer TODO/example remains.
  - **Risk:** Initializer overwrite; fail if a target already exists.
  - **Scope:** M.

- [x] 1.2 Implement Python-learning, network-lab, and packaging skill workflows.
  - **Objective:** Make executable examples, bounded local networking, and artifact-backed packaging repeatable.
  - **Deliverables:** Three concise `SKILL.md` files and only directly needed references/scripts.
  - **Validation:** Trigger, scope, failure/skip, cleanup, and declared commands map to their specs; references resolve directly.
  - **Scope:** M.

- [x] 1.3 Implement native-interop and book-quality-tooling skill workflows.
  - **Objective:** Route C++/Rust work conditionally and protect validator/parity/plugin truthfulness.
  - **Deliverables:** Two `SKILL.md` files, `engineer-python-native-interop/references/{cpp,rust}.md`, and focused tooling references.
  - **Validation:** C++ does not require Rust context and vice versa; no false-pass or human-approval path exists.
  - **Scope:** M.

- [x] 1.4 Extend professor and book-editor with course-wide maintenance modes.
  - **Objective:** Add prerequisite/cognitive-load/assessment and onboarding/provenance/rendered-review handoffs without duplicating new domain skills.
  - **Deliverables:** Updated `.codex/skills/professor/` and `.codex/skills/book-editor/` instructions/references and current UI metadata.
  - **Validation:** Existing triggers remain valid; new workflow is directly discoverable; human boundaries are explicit.
  - **Scope:** M.

- [x] 1.5 Add and run skill contract validation.
  - **Objective:** Prevent stale metadata, missing references, placeholders, extra skills, or prohibited auxiliary files.
  - **Deliverables:** Standard-library tests under `tools/tests/` for the seven affected skills.
  - **Validation:** `quick_validate.py` passes all seven; skill tests include a negative fixture; fresh-context forward checks for complex skills leave no artifacts.
  - **Scope:** M.

## 2. Curriculum progression and beginner recovery

- [x] 2.1 Add a versioned acyclic curriculum contract and validator tests.
  - **Objective:** Make route/checkpoint prerequisites auditable without pretending automation proves pedagogy.
  - **Deliverables:** `tools/curriculum_map.toml`, `tools/validate_curriculum.py`, and focused unit tests.
  - **Validation:** Valid map passes; missing path/anchor, unknown concept, forward required dependency, and cycle fixtures fail safely.
  - **Risk:** False confidence; diagnostics call this declared-contract evidence only.
  - **Scope:** L.

- [x] 2.2 Publish localized course routes in all six root indexes.
  - **Objective:** Give beginners, returning learners, practical learners, systems learners, and native learners clear entry/exit criteria.
  - **Deliverables:** Atomic route sections in root `README*` with numerical table of contents preserved.
  - **Validation:** `README.md == README.en.md`; localized links target matching siblings; route outcomes/durations/stopping points are equivalent; root navigation gate passes.
  - **Scope:** M.

- [x] 2.3 Make Chapters 02–07 essential routes solvable without later concepts.
  - **Objective:** Remove conditionals/functions/classes/exceptions/tests from required work before their teaching chapters, while keeping useful depth optional.
  - **Deliverables:** Five-language route, preview, checkpoint, solution, and prerequisite corrections per touched unit.
  - **Validation:** Curriculum validator plus runnable snippets; each essential checkpoint has normal/boundary/recovery evidence and no hidden prerequisite.
  - **Risk:** Large multilingual diff; edit and validate as one five-file unit at a time.
  - **Scope:** L.

- [x] 2.4 Reconcile foundational routes in Chapters 08–10 and Chapter 12.
  - **Objective:** Teach booleans/`None`, basic input/validation, and loops/OOP before optional exceptions, functions, pytest, pattern matching, or complexity depth is required.
  - **Deliverables:** Five-language prerequisite/route/checkpoint/solution corrections.
  - **Validation:** Essential route can be followed sequentially; optional material is skippable and locally linked; relevant runnable examples pass.
  - **Scope:** L.

- [x] 2.5 Rebuild Chapter 11 around foundational functions before higher-order depth.
  - **Objective:** Teach call model, parameters/arguments, `return`/implicit `None`, scope, safe defaults, and manual verification first.
  - **Deliverables:** Equivalent five-language foundational, intermediate, and advanced routes with executable recovery and modern Python 3.11 type syntax.
  - **Validation:** Foundational checkpoint requires no `Callable`, closure, decorator, pytest, or timing API; all five variants pass generic validation.
  - **Scope:** L.

- [x] 2.6 Complete explained recovery for audited Chapters 07, 11, and 12.
  - **Objective:** Replace summary-only solutions with runnable reasoning, boundary behavior, error recovery, and rubrics.
  - **Deliverables:** Five-language solution/checkpoint improvements scoped to the audited exercises.
  - **Validation:** Objective→example→TODO→hint→solution→observable check trace is complete and runnable/source-referenced.
  - **Scope:** L.

## 3. Standard-library and packaging lesson corrections

- [x] 3.1 Correct package layout and reproducibility terminology in Chapters 15–16.
  - **Objective:** Teach a real installable `src/<package>` layout and distinguish snapshots, direct pins, constraints, and locks.
  - **Deliverables:** Equivalent five-language content and self-contained verification examples.
  - **Validation:** Clean build/install/import example passes; no hermetic/cross-platform claim exceeds evidence.
  - **Scope:** M.

- [x] 3.2 Harden HTTP and logging lessons in Chapters 19–20.
  - **Objective:** Reject negative/malformed/oversized bodies and define the `dictConfig` trust boundary.
  - **Deliverables:** Five-language corrected snippets, explanations, edge/failure/recovery cases, and regression tests or executable snippets.
  - **Validation:** Negative-length probe terminates with `4xx`; arbitrary untrusted logging dictionaries are never presented as safe; generic gate passes.
  - **Scope:** M.

- [x] 3.3 Complete structured-concurrency and introspection safety in Chapters 21–22.
  - **Objective:** Explain task/thread distinction, `TaskGroup`, timeout/cancellation cleanup, and executable introspection hooks with real imports.
  - **Deliverables:** Equivalent five-language content and bounded examples.
  - **Validation:** Async success/failure/timeout leave no tasks; introspection test imports and passes; warnings cover descriptor/property execution.
  - **Scope:** M.

- [x] 3.4 Correct CLI and algorithm appendix contracts.
  - **Objective:** Use narrow expected errors and explicit `main(argv)->int`, and state BFS hashability/average-cost assumptions accurately.
  - **Deliverables:** Equivalent five-language appendix edits with runnable recovery.
  - **Validation:** CLI valid/invalid cases return stable codes; BFS example and complexity explanation agree; generic gate passes.
  - **Scope:** M.

## 4. Bounded networking implementation

- [x] 4.1 Bound retained telemetry state with long-session regression tests.
  - **Objective:** Prevent valid persistent clients from growing `readings` or accepted-output history without limit.
  - **Deliverables:** Protocol/hub bounded retention or aggregation and tests beyond the retention boundary.
  - **Validation:** Sequence behavior remains correct and measured state stays at or below the declared cap.
  - **Scope:** M.

- [x] 4.2 Add selector idle expiry and portable TLS verification.
  - **Objective:** Release capacity held by partial peers and remove private `ssl._ssl` test dependency.
  - **Deliverables:** Monotonic idle-deadline lifecycle, deterministic tests, and public/portable certificate test strategy.
  - **Validation:** 32 stalled peers expire in bounded time; EOF/cancel/shutdown clean state; TLS success/trust/hostname/expiry cases pass without private APIs.
  - **Risk:** Timing flakiness; use injected clock/readiness rather than fixed sleeps.
  - **Scope:** L.

- [x] 4.3 Reconcile all five Chapter 23 lessons and traceability with the bounded implementation.
  - **Objective:** Teach the exact retention, timeout, backpressure, and cleanup contract learners can verify.
  - **Deliverables:** Five READMEs plus `TRACEABILITY.md` and plugin token checks as needed.
  - **Validation:** Network suite and explicit root plugin pass; numerical limits match source and translations.
  - **Scope:** M.

## 5. Native interoperability corrections

- [x] 5.1 Make C++ sanitizer, typing, and dependency evidence truthful.
  - **Objective:** Distinguish supported sanitizer execution from skip, narrow stub allowances, and fail missing runtime dependencies.
  - **Deliverables:** CMake/verifier/stub/typing tests and domain-plugin contract updates.
  - **Validation:** Debug/release pass; supported sanitizer proves flags and passes, unsupported emits explicit skip; stub and dependency negative probes fail correctly.
  - **Scope:** L.

- [x] 5.2 Reconcile all five Chapter 24 lessons with verified packaging/toolchain scope.
  - **Objective:** Explain sanitizer capability, direct dependency pins, artifact audit, and tested platform matrix accurately.
  - **Deliverables:** Five READMEs, companion README/traceability, and terminology updates.
  - **Validation:** C++ plugin plus available full verifier pass; untested hosts remain labeled unverified.
  - **Scope:** M.

- [x] 5.3 Make Rust preflight, error, and benchmark evidence truthful.
  - **Objective:** Separate MSRV/pinned toolchain, support MSVC-aware compiler detection, preserve rendezvous failures, and compare the full public summary.
  - **Deliverables:** Preflight/source/benchmark/tests/plugin corrections.
  - **Validation:** Platform detection unit probes pass; Cargo/pytest/typing or explicit prerequisite skip is recorded; benchmark parity checks all fields.
  - **Scope:** L.

- [x] 5.4 Reconcile all five Chapter 25 lessons and stale traceability.
  - **Objective:** Teach exact toolchain/packaging/error behavior and reflect completed root-index integration.
  - **Deliverables:** Five READMEs, companion README, and corrected `TRACEABILITY.md`.
  - **Validation:** Rust plugin plus available full verifier pass; task 6.4/index evidence and text agree.
  - **Scope:** M.

## 6. Complete quality evidence

- [x] 6.1 Expand parity discovery and manifest to all 27 published units.
  - **Objective:** Inventory Chapters 23–25 without losing old review state or inventing approval.
  - **Deliverables:** `parity_review.py` discovery/tests/guide and reconciled 27-source/108-variant manifest.
  - **Validation:** Old path records preserve valid state; new records are automated-signal/pending-human-review; `--require-accepted` still fails while human reviews are pending.
  - **Risk:** Digest churn; reconcile only after learner content is final.
  - **Scope:** L.

- [x] 6.2 Add explicit least-privilege CI domain-plugin jobs.
  - **Objective:** Run network, C++, and Rust plugin evidence rather than leaving every source-ref unselected in CI.
  - **Deliverables:** Pinned bounded workflow jobs/steps with `contents: read` and no secrets/public targets.
  - **Validation:** Workflow contract tests assert explicit plugin commands, timeouts, permissions, and generic/domain separation.
  - **Scope:** M.

- [x] 6.3 Restore OpenSpec guidance and reconcile active evidence.
  - **Objective:** Make the root assistant pointer resolvable and update stale counts/traceability without completing human gates.
  - **Deliverables:** `openspec/AGENTS.md`, active parity/quality artifact corrections where required, and truthful implementation review.
  - **Validation:** OpenSpec doctor plus strict validation of this and coordinated changes; unchecked human tasks remain unchecked.
  - **Scope:** M.

## 7. Integrated verification

- [x] 7.1 Run skill, curriculum, generic, parity, plugin, and companion test matrices.
  - **Objective:** Demonstrate every automated contract from a clean workspace.
  - **Deliverables:** Updated scenario-to-command evidence in the change implementation review.
  - **Validation:** All seven skill validations; tools unittests; curriculum validator; parity; generic validator; three explicit plugins; touched chapter tests; no source mutation. Change-owned checks pass or report an explicit supported skip; any human provenance/publication blocker from a coordinated active change remains visible and non-zero rather than being waived or misreported as a domain failure.
  - **Scope:** L.

- [x] 7.2 Run available full native/package verification and record the exact matrix.
  - **Objective:** Confirm C++/Rust changes on installed toolchains without inferring other hosts.
  - **Deliverables:** Exact Python/compiler/CMake/Rust/Cargo host evidence or prerequisite-specific supported skip.
  - **Validation:** Existing `verify_all.py`/`verify.py` commands pass where provisioned; generated artifacts remain temporary; unsupported checks are not marked passed.
  - **Scope:** L.

- [x] 7.3 Validate OpenSpec, repository hygiene, and truthful completion.
  - **Objective:** Leave an apply-complete change whose tasks and evidence match reality.
  - **Deliverables:** Final task checkboxes and implementation review; no human sign-off fabrication.
  - **Validation:** `openspec validate harden-course-curriculum-and-maintainer-skills --strict`; coordinated strict validation; `openspec doctor`; `git diff --check`; clean artifact/hygiene scan.
  - **Scope:** M.
