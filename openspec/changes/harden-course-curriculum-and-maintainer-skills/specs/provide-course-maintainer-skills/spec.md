## ADDED Requirements

### Requirement: Exactly five repository-local maintainer skills are added

The change SHALL add exactly these five new skill directories under `.codex/skills/`:

- `verify-python-learning-assets`;
- `engineer-python-network-labs`;
- `python-packaging-release`;
- `engineer-python-native-interop`; and
- `maintain-book-quality-tooling`.

Each new directory SHALL be initialized with the installed `skill-creator/scripts/init_skill.py` targeting `.codex/skills`, SHALL contain a completed `SKILL.md` and generated `agents/openai.yaml`, and SHALL contain only resources required by its workflow. Existing unrelated skills SHALL remain available but SHALL NOT be modified or described as required by this course.

#### Scenario: Happy-path initialization

- **WHEN** a new maintainer skill is created
- **THEN** `init_skill.py` receives the exact kebab-case name, `.codex/skills` output path, required resource directories, and explicit `display_name`, `short_description`, and `default_prompt` interface values
- **AND** every generated TODO or unused example placeholder is replaced or removed before validation

#### Scenario: Edge case for an existing directory

- **WHEN** initialization finds one of the exact skill paths already present
- **THEN** implementation stops for that path rather than overwriting it
- **AND** reconciles the existing contents through a reviewed patch before continuing

#### Scenario: Failure on an extra or renamed skill

- **WHEN** the change adds a sixth maintainer skill or substitutes a different name for one of the five required names
- **THEN** the skill-contract test fails and identifies the unexpected or missing relative path
- **AND** no broad allowlist can suppress the mismatch

#### Scenario: Recovery from stale generated metadata

- **WHEN** `agents/openai.yaml` no longer describes its `SKILL.md`
- **THEN** maintainers regenerate it with `skill-creator/scripts/generate_openai_yaml.py` and explicit interface values
- **AND** do not hand-edit optional icon, color, or policy fields that were not requested

#### Scenario: Repository hygiene

- **WHEN** initialization and validation complete
- **THEN** no skill contains `README.md`, changelog, installation guide, quick-reference duplicate, unused asset, cache, bytecode, environment, credential, learner data, or generated test artifact
- **AND** the source tree contains only reviewed skill instructions and reusable resources

### Requirement: Skill metadata and progressive disclosure are bounded

Each new or extended `SKILL.md` SHALL use YAML frontmatter containing only `name` and a trigger-complete `description`, SHALL use imperative or infinitive instructions, and SHALL keep its core workflow concise and below 500 lines. Detailed domain material SHALL live in directly linked one-level `references/` files and SHALL be loaded only when the selected task requires it.

#### Scenario: General workflow loads minimal context

- **WHEN** a request triggers a maintainer skill but does not require a domain variant
- **THEN** its description selects the correct skill and `SKILL.md` provides the complete core workflow
- **AND** the agent does not need to load unrelated reference files

#### Scenario: Conditional native reference

- **WHEN** `engineer-python-native-interop` handles C++ work
- **THEN** it loads `references/cpp.md` and does not require `references/rust.md`
- **AND** Rust work loads `references/rust.md` without requiring `references/cpp.md`

#### Scenario: Failure on deep or duplicate documentation

- **WHEN** a reference is reachable only through another reference, duplicates the core workflow, or leaves a required workflow undiscoverable from `SKILL.md`
- **THEN** the skill-contract test fails
- **AND** maintainers move the routing link into `SKILL.md` and keep one authoritative copy of each instruction

#### Scenario: Accessible skill instructions

- **WHEN** a maintainer reads a workflow, command, warning, or decision table
- **THEN** headings and descriptive links expose the same sequence in plain text
- **AND** no required action depends only on color, icon, position, or unexplained abbreviation

### Requirement: Python learning assets are reproducibly verified

`.codex/skills/verify-python-learning-assets` SHALL define how to inventory Markdown fences and companion sources, distinguish `runnable`, `expected-error`, `compile-only`, `source-ref`, `todo`, `illustrative`, and `output`, execute eligible Python with the declared CPython matrix, compare stable outputs or diagnostics, and report evidence without treating illustrative content as executed.

#### Scenario: Happy-path runnable example

- **WHEN** a trusted standard-library Python block is labeled runnable
- **THEN** the skill executes it with `-I -B`, bounded output and time, no stdin, a minimal environment, and a disposable working directory
- **AND** records the Python version, exit status, meaningful output comparison, and source path

#### Scenario: Expected failure and recovery

- **WHEN** a lesson intentionally demonstrates an error
- **THEN** the skill verifies a nonzero result and stable diagnostic signal within the bound
- **AND** confirms the lesson explains a correction followed by a successful recovery case

#### Scenario: Unsupported execution is delegated

- **WHEN** a block needs networking, package installation, multiple processes, C++, Rust, or another domain toolchain
- **THEN** the skill refuses to imply generic execution
- **AND** requires an existing companion source and an explicit domain verifier or plugin check ID

#### Scenario: Execution hygiene

- **WHEN** verification succeeds, fails, or times out
- **THEN** temporary paths and child processes are cleaned and captured values are bounded and safe
- **AND** no repository file, cache, bytecode, credential, or learner datum is created or printed

### Requirement: Network labs use bounded local-first verification

`.codex/skills/engineer-python-network-labs` SHALL define reusable review and execution workflows for HTTP, TCP, UDP, selectors, `asyncio`, framing, TLS, cancellation, backpressure, timeouts, retries, and lifecycle cleanup. Required examples SHALL use loopback or offline fixtures and explicit resource limits; public or production targets SHALL NOT be used for verification.

#### Scenario: Happy-path local lab

- **WHEN** a network example is verified
- **THEN** the skill binds loopback on an ephemeral port, coordinates readiness without a fixed sleep, bounds body/frame/buffer/output/runtime sizes, and tears down peers deterministically
- **AND** verifies both learner-visible behavior and cleanup

#### Scenario: Edge and failure behavior

- **WHEN** a peer sends an empty datagram, fragmented frame, oversized or negative length, stalls mid-message, disconnects, or triggers cancellation
- **THEN** the skill requires a deterministic bounded outcome and stable diagnostic
- **AND** rejects indefinite accumulation, blocking reads, leaked tasks, or fabricated success

#### Scenario: TLS recovery

- **WHEN** a local TLS exercise encounters an untrusted certificate or hostname mismatch
- **THEN** the skill verifies the expected failure before any corrected trust configuration
- **AND** forbids teaching global certificate-verification disablement as the recovery

#### Scenario: Sensitive network hygiene

- **WHEN** certificates, keys, tokens, addresses, or payload fixtures are needed
- **THEN** they are explicitly didactic, scoped, fake, and inventoried or generated only in temporary storage
- **AND** logs and diagnostics do not expose secret values or learner information

### Requirement: Packaging and release claims are artifact-backed

`.codex/skills/python-packaging-release` SHALL define workflows for virtual environments, `pyproject.toml`, build isolation, direct requirements, constraints, resolved lock evidence, sdists, pure and native wheels, compatibility tags, clean installation, import from a foreign working directory, and reproducible release checks. It SHALL distinguish a direct-dependency pin from a complete resolved lock and SHALL never publish an artifact unless separately authorized.

#### Scenario: Happy-path package verification

- **WHEN** a lesson claims a project builds and installs
- **THEN** the skill builds in a clean temporary environment, inspects sdist and wheel contents/tags, installs the produced artifact into another clean environment, and tests its public import outside the source tree
- **AND** records tool and interpreter versions without claiming an untested platform

#### Scenario: Edge case for dependency records

- **WHEN** a file pins only direct requirements or omits transitive hashes
- **THEN** the skill labels it accurately as a requirements or constraints input rather than a complete reproducible lock
- **AND** explains what additional resolver evidence would be required for the stronger claim

#### Scenario: Build or install failure recovery

- **WHEN** isolation, metadata, wheel tagging, missing native runtime, or import verification fails
- **THEN** the workflow preserves a bounded safe diagnostic and identifies the failed phase
- **AND** rebuilds from a clean tree after the correction instead of accepting a previously cached artifact

#### Scenario: Release hygiene

- **WHEN** packaging verification finishes
- **THEN** generated `.venv`, `build/`, `dist/`, wheel, sdist, cache, compiled object, and credential files remain outside the source tree or are removed
- **AND** no index upload, signing, or production release occurs implicitly

### Requirement: Native interoperability uses language-specific evidence

`.codex/skills/engineer-python-native-interop` SHALL provide a concise shared workflow plus `references/cpp.md` for CMake/pybind11/C++ and `references/rust.md` for Cargo/PyO3/maturin. It SHALL verify ownership and lifetime contracts, Python exceptions, Global Interpreter Lock behavior, typing surfaces, source and wheel artifacts, ABI/platform scope, and declared toolchain versions without merging C++ and Rust-specific claims.

#### Scenario: C++ path is selected

- **WHEN** the task concerns the Chapter 24 companion project
- **THEN** the skill uses `references/cpp.md` to verify configure/build modes, actual compiler flags, sanitizer enablement or explicit supported skip, extension imports, stubs, artifacts, and lifetime/GIL tests
- **AND** does not report a requested sanitizer as run when CMake omitted it

#### Scenario: Rust path is selected

- **WHEN** the task concerns the Chapter 25 companion project
- **THEN** the skill uses `references/rust.md` to distinguish minimum supported Rust version from an exactly pinned toolchain and to verify GNU/MSVC-aware preflight, Cargo/PyO3 behavior, maturin artifacts, typing, ownership, errors, and concurrency
- **AND** does not broaden the verified target matrix

#### Scenario: Toolchain is unavailable

- **WHEN** the required compiler, linker, build frontend, interpreter ABI, sanitizer, or platform is absent
- **THEN** the workflow reports an explicit prerequisite-specific supported skip or failure according to the chapter contract
- **AND** never converts an unexecuted check into a pass

#### Scenario: Native failure recovery and hygiene

- **WHEN** a build, import, sanitizer, ownership, or artifact check fails
- **THEN** the skill preserves the actionable bounded diagnostic, cleans the build environment, and reruns from a clean configuration after correction
- **AND** leaves no native binary, Cargo/CMake tree, wheel, sdist, cache, credential, or core dump in source

### Requirement: Book-quality tooling remains truthful and extensible

`.codex/skills/maintain-book-quality-tooling` SHALL define how to evolve `tools/validate_book.py`, `tools/parity_review.py`, `tools/parity_manifest.json`, domain-plugin registration, baseline/config files, tests, review guides, and `.github/workflows/book-quality.yml`. It SHALL keep generic structural checks separate from explicitly invoked domain execution and SHALL keep automated signals separate from human linguistic, technical/pedagogical, accessibility, provenance, and legal approvals.

#### Scenario: Happy-path tooling change

- **WHEN** a validator, inventory, plugin protocol, or workflow changes
- **THEN** the skill maps the change to positive and negative fixtures, stable safe diagnostics, read-only behavior, versioned configuration, and least-privilege CI
- **AND** reruns generic checks plus only the explicitly provisioned domain plugins

#### Scenario: Automated evidence is incomplete

- **WHEN** structure, snippets, parity signals, or domain tests pass but a required competent human review is absent
- **THEN** the tooling reports the automated evidence and leaves the human gate pending
- **AND** neither the manifest nor CI promotes the record to accepted

#### Scenario: Plugin failure recovery

- **WHEN** a plugin is missing, times out, crashes, mutates source, returns malformed evidence, or lacks its toolchain
- **THEN** the workflow fails closed or records the exact supported skip defined by that plugin
- **AND** preserves generic validation results without claiming domain coverage

#### Scenario: Localized and accessible diagnostics

- **WHEN** a quality failure affects a localized learner document or accessibility contract
- **THEN** diagnostics identify the safe repository-relative path, rule, and actionable remediation without asserting semantic fluency or accessibility approval
- **AND** contain no absolute path, secret, learner data, unsafe captured payload, or legal conclusion

### Requirement: Professor and book-editor gain focused course-wide workflows

The existing `.codex/skills/professor/SKILL.md` SHALL add a course-level mode for prerequisite graphs, essential/intermediate/advanced/hero routes, cognitive-load boundaries, longitudinal capstones, estimated sessions, and objective-to-assessment traceability. The existing `.codex/skills/book-editor/SKILL.md` SHALL add maintainer onboarding, provenance evidence, rendered accessibility and bidirectional-review handoff, complete published-unit inventory reconciliation, and explicit human release-boundary workflows. Their existing trigger scope and compatible guidance SHALL be preserved.

#### Scenario: Professor audits a full course

- **WHEN** a request asks for curriculum progression rather than one isolated lesson
- **THEN** `professor` produces an acyclic concept/checkpoint map, route entry and exit criteria, cognitive-load findings, and assessment/capstone traceability
- **AND** distinguishes required learning from optional previews and hero depth

#### Scenario: Book editor prepares publication evidence

- **WHEN** structural and technical checks are complete
- **THEN** `book-editor` inventories unresolved provenance, linguistic, pedagogical, rendered accessibility, and Arabic bidi review
- **AND** provides reviewer-ready evidence without fabricating competence, ownership, license compatibility, or acceptance

#### Scenario: Unrelated skill isolation

- **WHEN** this Python book change is applied
- **THEN** Django, PatternFly, Proxmox, and browser-testing skills are neither modified nor automatically added to the course workflow
- **AND** they remain selectable only for a future request that actually matches their trigger

### Requirement: Every skill has automated and behavioral validation evidence

The implementation SHALL run `skill-creator/scripts/quick_validate.py` against all five new skills and the changed `professor` and `book-editor` skills. Repository tests SHALL assert the exact five-skill inventory, folder/frontmatter name agreement, trigger-complete descriptions, valid `agents/openai.yaml`, direct progressive-disclosure links, absence of placeholders and prohibited auxiliary files, and existence of every referenced resource. Every bundled deterministic script SHALL have a directly executed success test and at least one bounded failure test.

#### Scenario: All static skill checks pass

- **WHEN** the seven affected skill directories are validated
- **THEN** every `quick_validate.py` invocation exits zero
- **AND** the repository skill-contract suite passes from a clean checkout

#### Scenario: Broken metadata or reference fails

- **WHEN** frontmatter is malformed, a folder/name differs, a trigger omits its use context, UI metadata is stale, a direct reference is missing, or a TODO placeholder remains
- **THEN** validation fails with the exact skill-relative path and contract violation
- **AND** rerunning after the narrow correction demonstrates recovery

#### Scenario: Complex skill is forward-tested

- **WHEN** network, packaging, native-interoperability, or quality-tooling instructions are ready
- **THEN** a fresh-context behavioral test receives the skill and a realistic raw task or artifact without the intended diagnosis or answer
- **AND** reviewers confirm the result follows scope, safety, verification, progressive-disclosure, and no-false-pass contracts

#### Scenario: Behavioral test remains clean and bounded

- **WHEN** a forward test succeeds, fails, or reaches an unavailable toolchain
- **THEN** its temporary artifacts and processes are removed and no live external system is changed
- **AND** the evidence records failure or supported skip honestly without credentials, learner data, or leaked expected conclusions
