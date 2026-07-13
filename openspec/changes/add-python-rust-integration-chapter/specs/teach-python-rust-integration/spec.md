## ADDED Requirements

### Requirement: Progressive Zero-to-Hero Python and Rust Curriculum

The course SHALL provide a chapter 25 that teaches Python–Rust integration from no prior Rust knowledge through preparation, Rust-essential, integration, professional, and hero routes using CPython 3.11 or later.

#### Scenario: Learner starts without Rust knowledge

- **WHEN** a Python learner has never used Rust, Cargo, ownership, or a native compiler
- **THEN** the chapter introduces the toolchain and required Rust foundations before PyO3 macros
- **AND** completes a pure Rust program and test before building an extension

#### Scenario: Learner completes a route

- **WHEN** a route checkpoint is reached
- **THEN** the chapter states prerequisites, estimated multi-session duration, runnable outcome, and self-assessment
- **AND** distinguishes the route checkpoint from full chapter completion

#### Scenario: Learner studies a new concept

- **WHEN** ownership, errors, bindings, lifetimes, threads, or packaging is introduced
- **THEN** the subsection follows objective/context, minimal theory, predict, execute, observe, modify, and verify
- **AND** includes happy path, edge case, TODO, hint, common mistake, explained solution, and reflection

#### Scenario: Learner decides whether Rust is appropriate

- **WHEN** pure Python already solves the problem
- **THEN** the chapter requires a correctness reference and measurable reason for native code
- **AND** explains when Python, batching, an existing library, or no rewrite is the better choice

### Requirement: Reproducible Rust and Python Toolchain

The chapter SHALL provide a preflight and reproducible path for CPython 3.11+, pinned Rust 1.97.0/Edition 2024, Cargo, PyO3 0.29, maturin 1.14.1, isolated Python environments, Cargo lock, and exact development-tool lock.

#### Scenario: Supported toolchain is available

- **WHEN** the learner runs preflight
- **THEN** it reports Python/architecture, active venv, rustup, rustc, Cargo, host target, Edition support, PyO3, and maturin versions
- **AND** records the exact toolchain used for validation

#### Scenario: Python or pinned Rust toolchain is unavailable

- **WHEN** Python is below 3.11 or rustup cannot activate the pinned Rust 1.97.0 toolchain
- **THEN** the preflight fails with a specific message and official update path
- **AND** does not continue to unrelated maturin/linker errors

#### Scenario: Tool is missing or PATH is stale

- **WHEN** rustup, rustc, Cargo, maturin, venv activation, or required platform linker tools are unavailable
- **THEN** the chapter identifies the missing layer and platform-specific remedy
- **AND** explains when restarting the shell or installing system build tools is required

#### Scenario: Dependencies are resolved

- **WHEN** the capstone is first built
- **THEN** Cargo resolves the declared PyO3 version and preserves `Cargo.lock`
- **AND** maturin, pytest, and mypy use exact verified versions from `requirements-dev.lock`

#### Scenario: Initial setup needs network access

- **WHEN** rustup, maturin, or crates are not cached
- **THEN** the chapter explicitly marks the Internet/tool-install step
- **AND** does not claim the complete setup is offline

#### Scenario: maturin is installed

- **WHEN** the learner follows the base installation
- **THEN** maturin is installed as a released binary/Python tool through the documented method
- **AND** `cargo install maturin` is not required or presented as equivalent without its different MSRV/build cost

### Requirement: Rust Foundations Before PyO3

The chapter SHALL teach and verify the Rust subset required by the capstone before exposing Python objects to Rust.

#### Scenario: Values and collections are used

- **WHEN** the learner implements the first domain functions
- **THEN** the chapter covers variables, mutability, functions, numeric types, `String`/`str`, `Vec<T>`/slices, structs/impl, and modules
- **AND** examples pass formatting, clippy, and tests

#### Scenario: Ownership move occurs

- **WHEN** a value is moved and reused incorrectly
- **THEN** the learner predicts and reads the compiler diagnostic
- **AND** fixes the design with an appropriate borrow, returned ownership, or justified clone

#### Scenario: Borrow rules are violated

- **WHEN** mutable and immutable borrows conflict or a reference would outlive its owner
- **THEN** the compiler rejects the code and the lesson identifies owner, borrower, scope, and valid redesign
- **AND** does not bypass the model with unsafe or lifetime extension

#### Scenario: Recoverable domain error occurs

- **WHEN** input is empty, non-finite, invalid, or otherwise outside the domain contract
- **THEN** Rust returns `Result<T, DomainError>` and the caller handles it with matching or `?`
- **AND** user input is not processed with `unwrap` or `expect`

#### Scenario: Rust domain is tested alone

- **WHEN** `cargo test --locked` runs before PyO3 integration
- **THEN** it covers happy and edge cases without importing Python or constructing Python objects

### Requirement: Mixed Python and Rust Package Architecture

The capstone SHALL separate the Rust domain, PyO3 binding, private native module, public Python package, reference implementation, typing, tests, benchmarks, and build artifacts.

#### Scenario: Domain remains Python-independent

- **WHEN** `domain.rs` is compiled/tested
- **THEN** it uses Rust domain types and does not import PyO3 or depend on interpreter state

#### Scenario: Package is built for development

- **WHEN** `maturin develop --locked` runs in the active venv
- **THEN** the mixed project installs `faststats_rs._native` and the public package imports successfully
- **AND** the build does not require the deprecated PyO3 `extension-module` Cargo feature

#### Scenario: Base module declares GIL requirement

- **WHEN** PyO3 0.29 initializes the capstone module
- **THEN** its `#[pymodule]` declaration sets `gil_used = true`
- **AND** the base artifact does not make PyO3's default free-threaded compatibility claim

#### Scenario: Consumer imports public API

- **WHEN** Python imports `faststats_rs`
- **THEN** `__init__.py` exposes documented names while `_native` remains private
- **AND** runtime API, `__all__`, docstrings, stubs, and defaults agree

#### Scenario: Native extension cannot load

- **WHEN** `_native` is absent or incompatible
- **THEN** the package reports whether it is unbuilt or binary-invalid
- **AND** does not silently replace a broken installed artifact with `_reference.py`

#### Scenario: Artifact import is verified

- **WHEN** a built wheel is tested
- **THEN** the test uses a fresh venv and cwd outside the repository
- **AND** cannot pass by importing the Python source tree

### Requirement: Typed Boundary and Ownership Semantics

The chapter SHALL document and test how primitives, strings, bytes, sequences, optionals, Rust values, and Python objects are copied, moved, borrowed, reference-counted, and bounded by PyO3 lifetimes.

#### Scenario: Python sequence becomes Rust data

- **WHEN** a Python sequence is passed to the batch API
- **THEN** elements are validated and converted into an owned `Vec<f64>`
- **AND** the chapter explicitly calls this a conversion/copy rather than zero-copy

#### Scenario: Strings bytes or optionals cross the boundary

- **WHEN** supported textual/binary/optional inputs are supplied
- **THEN** Unicode, bytes, absent value, and invalid type behavior match the documented mapping
- **AND** no borrowed view escapes the active `'py` lifetime

#### Scenario: Python object handle is used

- **WHEN** code uses `Python<'py>`, `Bound<'py,T>`, or `Py<T>`
- **THEN** the chapter states owner/reference-count/lifetime/thread access rules
- **AND** does not store a borrowed handle in a longer-lived Rust domain object

#### Scenario: Type extraction fails

- **WHEN** Python supplies an incompatible type, range, nested shape, or element
- **THEN** PyO3 raises the documented Python exception without partial domain mutation

#### Scenario: Zero-copy interop is requested

- **WHEN** NumPy, Arrow, or Python buffer borrowing is considered
- **THEN** the chapter explains the additional lifetime/layout contracts
- **AND** keeps the implementation outside the mandatory capstone instead of making an unsupported zero-copy claim

### Requirement: Incremental Faststats Rust Capstone

The chapter SHALL evolve one `faststats_rs` project from a Python reference and pure Rust domain to a typed, concurrent, measured, and packaged extension.

#### Scenario: Batch input belongs to the accepted numeric domain

- **WHEN** samples are supplied to `summarize`
- **THEN** it accepts 1 through 1,000,000 values that are exactly built-in `int` or `float`, excluding `bool`, `Fraction`, `Decimal`, NumPy scalars, and arbitrary `__float__` objects
- **AND** integers satisfy `abs(value)<=2**53`, converted values are finite with `abs(value)<=1e150`, and threshold is finite within `[0,1e150]`

#### Scenario: Summary is computed

- **WHEN** valid samples and threshold are supplied
- **THEN** Python and Rust return equivalent count, minimum, maximum, mean, anomaly count, and anomaly ratio
- **AND** both update mean in input order using `mean += (value - mean) / count` without fast-math, parallel reduction, or reordering

#### Scenario: Anomaly is classified

- **WHEN** the final input-order `Summary.mean` has been computed and a second pass evaluates `delta = abs(value - Summary.mean)` for each sample
- **THEN** it counts only when `delta > threshold` and it is not close to threshold under `rel_tol=1e-12, abs_tol=1e-12`
- **AND** equality and the tolerance band are excluded, ratio equals anomaly count divided by count, and tests include `[-3,-3,-1]` at threshold `0.5` to distinguish final-mean classification from streaming classification

#### Scenario: Numeric parity is evaluated

- **WHEN** native and reference floating results are compared
- **THEN** tests use `rel_tol=1e-12` and `abs_tol=1e-12`, while integer fields compare exactly

#### Scenario: Edge-case batch is supplied

- **WHEN** the batch has 0, 1, 1,000,000, or 1,000,001 items or exercises value/integer/threshold/tolerance boundaries
- **THEN** empty/over-limit/out-of-range/non-finite/invalid-threshold input raises `ValueError`, while rejected types raise `TypeError` without partial mutation
- **AND** valid single/negative/boundary/tolerance/maximum-size inputs follow the exact common result contract

#### Scenario: Immutable result is exposed

- **WHEN** Rust returns `Summary`
- **THEN** the Python-facing `#[pyclass(frozen)]` has typed readable properties and representation
- **AND** prevents unsupported mutation

#### Scenario: Stateful calculator is used

- **WHEN** the learner uses `OnlineStats`
- **THEN** `add`, `extend`, and `reset` preserve count/minimum/maximum/mean, with empty/reset values `0/None/None/None`
- **AND** values use the same exact type/range domain, total count never exceeds 1,000,000, and rejected type/range/finiteness/over-limit updates preserve the complete prior state
- **AND** methods remain attached/GIL-held, never detach, and do not claim safe concurrent mutation

#### Scenario: Learner completes the capstone

- **WHEN** all required routes are complete
- **THEN** the package includes domain, binding, facade, reference, classes, errors, typing, detach, dual-language tests, benchmark, version-specific wheel, and abi3 exercise
- **AND** the learner can explain owner/copy/lifetime/error/interpreter/ABI boundaries for each public operation

### Requirement: Error and Panic Contract

The chapter SHALL map recoverable Rust errors to stable Python exceptions, prevent panic as public control flow, and isolate any panic demonstration from the main interpreter.

#### Scenario: Domain error crosses into Python

- **WHEN** `DomainError` is returned
- **THEN** the binding converts it to the documented built-in or custom Python exception with useful non-sensitive context
- **AND** preserves the public error contract across reference/native implementations

#### Scenario: PyO3 API returns an error

- **WHEN** extraction, allocation, class construction, or Python API interaction fails
- **THEN** the binding propagates `PyResult` with `?` or explicit context
- **AND** does not discard or replace the active Python exception accidentally

#### Scenario: External input reaches unwrap or expect audit

- **WHEN** code review scans the binding/domain
- **THEN** no user-controlled value can trigger `unwrap`/`expect`
- **AND** any remaining use documents a local invariant or exists only in tests

#### Scenario: Panic is demonstrated

- **WHEN** the hero material explains `PanicException` or unwinding risk
- **THEN** the demonstration runs in a subprocess with expected exit/exception evidence
- **AND** the normal test runner and learner session are not terminated

#### Scenario: Panic across manual FFI is considered

- **WHEN** unwinding across an FFI boundary is discussed
- **THEN** the chapter identifies it as dangerous/undefined under incompatible ABIs
- **AND** does not implement manual extern C FFI in the capstone

### Requirement: Interpreter Attachment and Parallel Execution

The hero route SHALL teach and test interpreter attachment, `Python::detach`, Rust ownership across threads, and the limits of GIL/free-threaded claims.

#### Scenario: Long Rust computation detaches

- **WHEN** a CPU-bound batch operation is called
- **THEN** Python input is fully validated/converted to owned Rust data before `Python::detach`
- **AND** the detached closure returns only Rust-owned results/errors

#### Scenario: Detached closure is audited

- **WHEN** code inside `Python::detach` is reviewed
- **THEN** it contains no `Python<'py>`, `Bound<'py,T>`, borrowed Python reference, Python API call, or callback

#### Scenario: Two Python threads call Rust

- **WHEN** two Python threads invoke detached native work
- **THEN** both make progress and return correct results within a bounded timeout
- **AND** shared Rust state is immutable, thread-safe, isolated, or explicitly synchronized

#### Scenario: Detached concurrency is proved deterministically

- **WHEN** the concurrency acceptance test runs
- **THEN** a test-only Rust `Mutex`/`Condvar` rendezvous requires both detached closures to enter before either continues
- **AND** serial execution or an implementation retaining the GIL cannot pass merely by finishing before timeout

#### Scenario: Distribution artifact excludes test instrumentation

- **WHEN** the release sdist or either release wheel is inspected
- **THEN** the `test-hooks` feature is disabled and no rendezvous API, symbol, or hook-only source is included
- **AND** concurrency acceptance uses a separately built test target rather than altering the distributed module

#### Scenario: Python object must be accessed again

- **WHEN** a result or exception must become a Python object
- **THEN** execution is attached to the interpreter after the detached region
- **AND** performs the conversion on the correct thread state

#### Scenario: Free-threaded Python is considered

- **WHEN** Python 3.14+ free-threaded or an advanced PyO3 module declaration is discussed
- **THEN** the chapter requires audit/tests for Send/Sync, pyclass state, globals, reference counting, and dependencies
- **AND** keeps `gil_used = true` in the base; `gil_used = false` requires a separately built/audited/tested variant

### Requirement: Dual-Language Verification

The chapter SHALL verify the Rust domain, Python facade, PyO3 binding, parity, errors, classes, concurrency, typing, and installed artifacts with the most appropriate test layer.

#### Scenario: Rust domain changes

- **WHEN** Rust domain code changes
- **THEN** `cargo fmt --check`, clippy with warnings denied, and `cargo test --locked` validate style, lints, behavior, and errors

#### Scenario: Python contract changes

- **WHEN** facade, extraction, exception, class, or typing code changes
- **THEN** pytest covers public behavior and parity against the built native module
- **AND** pytest cache is disabled or placed outside the repository

#### Scenario: Typing contract changes

- **WHEN** the facade, classes, or stubs change
- **THEN** the clean-installed wheel passes `python -m mypy.stubtest faststats_rs` and a strict typed consumer
- **AND** any allowlist is narrow, explained, and versioned

#### Scenario: Concurrency test runs

- **WHEN** detach/thread behavior is tested
- **THEN** synchronization uses events/barriers/futures and bounded timeout rather than arbitrary sleeps as the primary mechanism

#### Scenario: Clean artifact test runs

- **WHEN** distribution artifacts are verified
- **THEN** a temporary sdist is unpacked and used to rebuild the wheel before a fresh temporary venv installs only the wheel/test needs and runs import/contract smoke outside the source tree
- **AND** `pip check` succeeds

#### Scenario: Repository hygiene is audited

- **WHEN** validation completes
- **THEN** an explicit filesystem scan finds no `.venv`, `target`, wheel, compiled library, Cargo temp, pytest/Python cache, or credential inside the chapter tree, including ignored files

### Requirement: Evidence-Based Rust Performance

The chapter SHALL teach performance measurement that includes extraction/copy, boundary calls, allocation, Rust computation, build profile, and batching without a required speedup.

#### Scenario: Benchmark begins

- **WHEN** Python and Rust paths are compared
- **THEN** their results are verified on identical deterministic data before timing
- **AND** release/debug profile is recorded

#### Scenario: Measurements are collected

- **WHEN** time samples are taken
- **THEN** warm-up, repeated samples, median/robust summary, and multiple input sizes are used
- **AND** hardware/software/toolchain context is reported

#### Scenario: Boundary overhead dominates

- **WHEN** small native calls are not faster
- **THEN** the chapter demonstrates batching or retaining Python
- **AND** does not hide results or impose a speedup threshold

#### Scenario: Parallel measurement is interpreted

- **WHEN** two detached calls run in parallel
- **THEN** correctness and wall-time behavior are discussed separately from single-call throughput
- **AND** no universal scaling claim is made

### Requirement: Packaging Stable ABI and Typing

The chapter SHALL build and inspect an sdist, rebuild version-specific and `abi3-py311` wheels from that distributed source, inspect compatibility tags, clean-install artifacts, provide stable manual typing, and bound free-threaded/`abi3t` claims.

#### Scenario: Source distribution is built

- **WHEN** the release sdist is created in a temporary output directory
- **THEN** it contains package metadata, license, README, Python facade, stubs, Rust sources, Cargo metadata, and required lockfiles
- **AND** excludes targets, caches, credentials, test hooks, built libraries, and other generated output

#### Scenario: Version-specific wheel is built

- **WHEN** `maturin build --release --locked` runs from the unpacked sdist
- **THEN** the wheel contains the mixed Python package, `_native`, `.pyi`, and `py.typed`
- **AND** its Python/ABI/platform tags reflect the actual target

#### Scenario: abi3 wheel is built

- **WHEN** the documented `abi3-py311` feature/build mode is enabled from the unpacked sdist
- **THEN** maturin produces the appropriate stable-ABI tag for GIL-enabled CPython >=3.11 on that platform
- **AND** compatible available interpreters clean-install and smoke-test it

#### Scenario: abi3 is interpreted

- **WHEN** the learner sees an `abi3` wheel
- **THEN** the chapter explains that stable Python ABI does not remove OS/architecture/platform requirements or all API limitations

#### Scenario: abi3t is considered

- **WHEN** PyO3/maturin support for `abi3t` and Python 3.15+ is discussed
- **THEN** it is marked hero/future/conditional and requires a compatible runtime plus separate build/tests
- **AND** is not claimed by the baseline Python 3.11 capstone, which remains `gil_used = true`

#### Scenario: Typing is consumed

- **WHEN** an editor/type checker reads the installed package
- **THEN** manual stubs and `py.typed` expose public signatures/classes/defaults consistently
- **AND** `python -m mypy.stubtest faststats_rs` plus a strict consumer verify them while experimental introspection remains optional

#### Scenario: Package publication is considered

- **WHEN** remote publication or multi-platform release is discussed
- **THEN** the chapter explains that a verified wheel matrix and release controls are required
- **AND** does not request tokens or upload artifacts

### Requirement: Pedagogical Practice and Assessment

The chapter SHALL provide complete educational scaffolding, progressive exercises, normalized mistakes, explained solutions, and a final rubric across both languages.

#### Scenario: Learner performs an exercise

- **WHEN** an exercise is introduced
- **THEN** it provides objective, TODOs, hints, expected observable result, happy path, and at least one edge case

#### Scenario: Compiler rejects learner code

- **WHEN** Rust emits an ownership/type/lifetime diagnostic
- **THEN** the lesson treats it as expected feedback, explains the relevant span/help, and offers a minimal idiomatic correction

#### Scenario: Build error occurs

- **WHEN** maturin/Cargo/linker/import fails
- **THEN** common mistakes map the symptom to the correct layer and safe diagnostic command

#### Scenario: Learner reviews a solution

- **WHEN** a guided exercise is complete or blocked
- **THEN** the solution explains why it works, ownership/error implications, and alternatives rather than presenting only final code

#### Scenario: Final project is assessed

- **WHEN** the capstone is reviewed
- **THEN** a rubric covers correctness, Rust idioms, boundary safety, API design, errors, tests, concurrency, measurement, packaging, typing, and explanation

### Requirement: Multilingual Integration Scope and Hygiene

The course SHALL publish equivalent chapter 25 content in all five languages, update all six root indexes, link localized prerequisites, coordinate concurrent chapter changes, and preserve safety/scope/hygiene constraints.

#### Scenario: Reader discovers chapter 25

- **WHEN** a reader opens any root index after coordinated integration
- **THEN** chapter 25 appears before appendices and after lower-numbered chapters that are actually implemented
- **AND** links to matching language without creating dangling entries for pending changes

#### Scenario: Reader switches language

- **WHEN** another language is selected
- **THEN** the same routes, source refs, toolchain commands, code semantics, warnings, exercises, and rubric remain available
- **AND** Arabic uses the repository's outer `<div dir="rtl">` convention while code blocks remain readable LTR

#### Scenario: Reader uses accessible Markdown

- **WHEN** the chapter is rendered in any supported language
- **THEN** headings are hierarchical, links are descriptive, tables have simple headers, and meaningful visuals provide alt text plus an equivalent prose explanation
- **AND** instructions do not depend only on color, position, or icons while code and commands remain readable in RTL content

#### Scenario: Learner needs a prerequisite

- **WHEN** the chapter uses exceptions, modules, environments, testing, logging, or introspection
- **THEN** it links to chapters 14, 15, 16, 18, 20, or 22 in the current language
- **AND** chapters 23/24 are optional links only if present

#### Scenario: Unsafe or out-of-scope path is proposed

- **WHEN** unsafe, manual C ABI, arbitrary loader, embedding, async runtime, NumPy zero-copy, cross-compilation, mobile/WASM, or remote publication appears
- **THEN** the chapter marks it outside the mandatory change and does not add an unverified implementation

#### Scenario: Shared indexes have concurrent changes

- **WHEN** chapter 23, 24, and 25 changes are applied/rebased
- **THEN** the six indexes are reconciled serially and preserve numeric order plus appendices
- **AND** no implemented entry is lost and pending entries are not linked prematurely

#### Scenario: Final repository state is inspected

- **WHEN** the implementation is ready for review
- **THEN** only source, docs, lock/config, tests, stubs, and intended fixtures are present
- **AND** the root hygiene rule, or its temporary equivalence-tested fallback before root integration, confirms generated artifacts, ignored caches, venvs, targets, wheels, tokens, and secrets are absent
