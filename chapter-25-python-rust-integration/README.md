# Chapter 25 · Python and Rust: from first crate to a verified wheel

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

This chapter starts with zero Rust knowledge. You will first build a tiny Rust program, then a pure Rust statistics domain, and only then cross the Python boundary with PyO3. The final result is `faststats_rs`: a typed mixed package with deterministic tests, bounded parallel work, an sdist, a version-specific wheel, and an `abi3-py311` wheel.

All examples are original companion sources in [`examples/`](examples/). The complete verifier writes builds and environments to temporary directories; nothing is published and no credentials are used.

## Learning objectives and prerequisites

By the end you can:

- explain crate, compiler, extension module, application binary interface (ABI), sdist, and wheel in plain language;
- read basic Rust with variables, structs, `Vec<T>`, slices, ownership, borrowing, `Option`, and `Result`;
- keep a Rust domain independent from PyO3 and translate recoverable errors into Python exceptions;
- describe what is copied, moved, borrowed, or reference-counted at the Python/Rust boundary;
- design an exact bounded numeric contract before optimizing it;
- use `Python::detach` only with Rust-owned data and distinguish GIL release from free-threaded support;
- test Rust, Python, typing, concurrency, source distributions, wheels, and clean imports;
- interpret a benchmark without promising that Rust is always faster.

Required Python background: exceptions, modules, virtual environments, testing, logging, and introspection. Review [exceptions](../chapter-14-exceptions/README.md), [modules](../chapter-15-modulos/README.md), [environments](../chapter-16-entornos/README.md), [testing](../chapter-18-testing/README.md), [logging](../chapter-20-logging/README.md), and [introspection](../chapter-22-introspection/README.md) if needed. Chapters 23 and 24 are not prerequisites.

You need CPython 3.11+, Internet access for the initial Rust/crate/tool installation, a platform linker, and roughly 16 sessions of 45–60 minutes. The verified host for this implementation was Linux x86-64, CPython 3.13.11, Rust 1.97.0, PyO3 0.29.0, and maturin 1.14.1. Other platforms are instructions to validate, not claims of tested support.

## Route map

| Route | Time | Observable result | Completion check |
|---|---:|---|---|
| Preparation | 1–2 sessions | Toolchain report and first Rust test | `cargo test --locked` |
| Essential Rust | 4 sessions | Python-independent statistics domain | fmt, clippy, domain tests |
| Integration | 3 sessions | Python imports a private PyO3 extension | wheel installed outside source tree |
| Professional | 3–4 sessions | Classes, errors, typing, parity tests | pytest, stubtest, strict mypy |
| Hero | 3–4 sessions | Detached work and two inspected wheel modes | rendezvous, sdist rebuild, clean installs |

You may stop after any checkpoint. Hero material is not required to understand the essential route.

## 1. Why cross the language boundary?

Python is usually the best place to start: it is readable, has mature libraries, and lets us test ideas quickly. Native code adds a compiler, platform tooling, packaging, and another memory model. That cost is justified only after correctness is fixed and measurement identifies a useful boundary.

Our growing project summarizes up to one million numeric samples. Python owns the public experience; Rust owns a deliberately narrow compute domain. We keep a pure Python oracle so a fast wrong answer cannot pass.

**Predict:** which is likely faster: one native call with 100,000 values, or 100,000 native calls with one value each? The second case pays the boundary cost repeatedly. We will measure rather than guess.

**Checkpoint:** name one reason to retain Python: the workload is already fast enough, the native call is too small, an existing library solves it, or maintenance cost exceeds measured benefit.

## 2. Preparation: diagnose before building

Install Rust through `rustup`; install maturin as a released Python tool, not with `cargo install maturin` on the base route. Linux needs a C linker/build essentials, macOS needs Xcode command-line tools, and Windows normally needs the MSVC C++ build tools matching a 64-bit Python.

| System | Native prerequisite | First diagnostic |
|---|---|---|
| Linux | distro C build tools/linker | `cc --version` |
| macOS | Xcode command-line tools | `xcode-select -p` |
| Windows | matching MSVC Build Tools | run `cl` or `clang-cl` from a Developer shell |

The chapter pins Rust instead of saying “latest”:

```bash illustrative
rustup toolchain install 1.97.0 --profile minimal --component rustfmt --component clippy
python -m venv .venv
# Activate .venv with the command appropriate for your shell.
python -m pip install -r examples/faststats-rs/requirements-dev.lock
python -B tools/preflight.py --require-venv
```

The installation step may use the Internet. `requirements-dev.lock` contains exact direct pins for the Python verification tools, but it is not a resolver-generated, hash-locked transitive environment. `Cargo.lock` locks the Rust dependency graph, and `rust-toolchain.toml` selects Rust 1.97.0.

Preflight separates layers: Python/version/venv first, then rustup/toolchain, Cargo/host target, linker, and finally maturin. A missing linker is not a PyO3 error; an inactive venv is not a Rust error.

### Recoverable setup errors

- `rustup: command not found`: install from the official Rust installer, restart the shell, then run `rustup --version`.
- Rust 1.96 appears: run `rustup run 1.97.0 rustc --version`; do not weaken `rust-version`.
- maturin reports no virtual environment during `develop`: activate the venv or build a wheel instead.
- import works only from the source directory: test from a temporary foreign cwd; shadow imports can hide a broken installation.

**TODO:** run preflight and record Python, architecture, host target, rustc, Cargo, and maturin. **Hint:** `python -B tools/preflight.py --json` creates a copyable report without changing the repository.

## 3. First Rust program: values, functions, and tests

A crate is Rust's package/compilation unit. `Cargo.toml` is its manifest; Cargo resolves dependencies and runs the compiler and tests. Edition 2024 selects language idioms. `rust-version = "1.97.0"` declares the minimum supported Rust version (MSRV); the checked-in `rust-toolchain.toml` selects exactly 1.97.0 for these exercises.

```bash illustrative
cd examples/00-rust-survival
cargo check --locked
cargo run --locked
cargo test --locked
```

Expected program observation:

```text illustrative
workshop mean: 19.0
```

The companion library introduces a struct, borrowed slice, `Option`, enum, `Result`, and `?` in one bounded sensor-reading example.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/00-rust-survival/src/lib.rs" check="rust:contract" -->
```rust source-ref
pub fn average(values: &[f64]) -> Option<f64> { /* tested source */ }
pub fn parse_reading(text: &str) -> Result<Reading, ParseReadingError> { /* ... */ }
```

`Option<f64>` says an average may be absent for an empty slice. `Result<Reading, ParseReadingError>` says parsing can fail in known, recoverable ways. Neither needs a magic sentinel.

**Modify:** add a test for `"lab:NaN"`. **Hint:** parsing succeeds first, then `is_finite()` rejects the value. The explained solution is already represented by the `NonFiniteNumber` branch: validation happens after syntax conversion because “number-shaped” is not the whole domain.

## 4. Ownership and borrowing: read the compiler as feedback

Python variables refer to managed objects. Rust values also have an owner, and ordinary assignment may move ownership. The owner drops the value when its scope ends. A borrow (`&T`) temporarily lets code read without taking ownership; `&mut T` is an exclusive mutable borrow.

Before compiling the expected-error file, predict the failing line:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/00-rust-survival/lessons/ownership_move_error.rs" check="rust:contract" -->
```rust source-ref
let label = String::from("sensor-a");
let moved_label = label;
println!("{moved_label}");
println!("{label}"); // E0382: value used after move
```

The compiler points to the owner, move, and invalid reuse. It may suggest `.clone()`, but cloning has a cost and is not always the right design. Here the function only needs to read, so borrow:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/00-rust-survival/lessons/ownership_borrow_solution.rs" check="rust:contract" -->
```rust source-ref
fn print_label(label: &str) { println!("{label}"); }
// The caller retains its String and lends a &str twice.
```

Common mistake: adding clones until the compiler becomes quiet. A better question is “who should own this after the call?” Clone only when two independent owners are a deliberate trade-off.

**Self-check:** identify owner, borrower, and scope in `average(values: &[f64])`. The caller owns the collection; `average` borrows a slice for the call; the borrow cannot outlive the caller's data.

## 5. Build the pure Rust domain before PyO3

The domain accepts already-converted `f64` values. It knows nothing about Python built-in types or the Global Interpreter Lock (GIL). This boundary lets `cargo test` catch numeric errors without a Python build.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/src/domain.rs" check="rust:contract" -->
```rust source-ref
pub const MAX_SAMPLES: usize = 1_000_000;
pub const MAX_ABS_VALUE: f64 = 1.0e150;
pub fn summarize(values: &[f64], threshold: f64)
    -> Result<SummaryData, DomainError> { /* tested implementation */ }
```

The order matters:

1. validate count, finiteness, value range, and threshold;
2. update `mean += (value - mean) / count` in input order;
3. make a second pass against the final mean;
4. count a delta only if it is greater than the threshold and outside the `1e-12` tolerance band.

For `[-3, -3, -1]` and threshold `0.5`, the final mean is `-7/3`; all three values are anomalies. A streaming decision would produce a different answer, which is why the contract states the second pass.

`OnlineStatsData.extend` clones the small state, validates and updates the clone, then commits it. An invalid extension leaves count/minimum/maximum/mean unchanged. This is transactional behavior, not database machinery.

**TODO:** add a domain test for a negative threshold. **Hint:** call `validate_threshold` before computing. **Solution:** expect `DomainError::InvalidThreshold`; do not clamp silently because that changes the caller's request.

## 6. First PyO3 extension

PyO3 generates the CPython extension boundary. `#[pyfunction]` describes callable functions and `#[pymodule]` initializes the module. The base module explicitly states `gil_used = true`; PyO3 0.29 must not accidentally advertise unaudited free-threaded compatibility.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/01-first-extension/src/lib.rs" check="rust:contract" -->
```rust source-ref
#[pyfunction]
fn double(value: i64) -> PyResult<i64> { /* checked multiplication */ }

#[pymodule(gil_used = true)]
fn first_pyo3_extension(module: &Bound<'_, PyModule>) -> PyResult<()> { /* ... */ }
```

Build in an active venv with `maturin develop --locked`, or prefer the verifier's temporary wheel workflow. `checked_mul` turns overflow into `ValueError`; a wrong Python type becomes `TypeError` during extraction.

```bash illustrative
cd examples/01-first-extension
maturin develop --locked
python -c "import first_pyo3_extension as m; print(m.double(21))"
```

Expected observation:

```text illustrative
42
```

Common mistake: adding the historical `pyo3/extension-module` feature because an old tutorial does. The maturin 1.14 route does not need it, so the tested manifests omit it.

## 7. Mixed package: private native module, public facade

`faststats_rs` uses two layers:

- `faststats_rs._native`: compiled implementation detail;
- `faststats_rs`: documented Python facade and stable typing surface.

`pyproject.toml` sets `python-source = "python"` and `module-name = "faststats_rs._native"`. Rust builds both `cdylib` for Python and `rlib` for Rust-side testing. `_reference.py` is a correctness oracle, never a silent fallback for a broken wheel.

If `_native` is absent, the facade says it is unbuilt. If a dependent library fails inside `_native`, that original import error is not disguised.

**Predict:** why test from outside this directory? Python puts the current directory on `sys.path`; a local folder can make an import look successful even when the wheel lacks files.

**Checkpoint:** draw the call path: caller → public facade → private native module → extraction → owned Rust vector → domain `Result` → Python class or exception.

## 8. Exact boundary types and PyO3 lifetimes

The public contract accepts only exact built-in `int` and `float`. `bool` is an `int` subclass in Python, but is rejected. So are `Fraction`, `Decimal`, numeric subclasses, NumPy scalars, and arbitrary `__float__` objects. Accepted integers satisfy `abs(value) <= 2**53`; converted floats are finite and `abs(value) <= 1e150`.

The binding checks the exact Python type before extracting. A sequence is iterated and copied into an owned `Vec<f64>`. That is not zero-copy. The simple copy gives Rust independent data for detached computation.

PyO3 lifetime vocabulary:

- `Python<'py>` proves the current thread is attached for `'py`;
- `Bound<'py, T>` is a Python object handle bound to that attachment;
- `Py<T>` owns a reference-counted Python handle but still needs correct attachment to access Python.

No borrowed Python reference is stored in `domain.rs` or moved into detached work. The small `describe_payload` API separately tests Unicode, bytes, and `Option<&str>` conversion without extending a borrow.

**Optional preview:** zero-copy NumPy, Arrow, and buffer views require layout, lifetime, aliasing, and mutation contracts. They are valuable later, but outside this capstone.

## 9. The exact `faststats_rs` contract

`summarize(samples, *, threshold)` requires 1–1,000,000 values. Threshold is an exact built-in number, finite, and in `[0, 1e150]`. It returns frozen `Summary(count, minimum, maximum, mean, anomaly_count, anomaly_ratio)`.

Boundary behavior is part of the API:

- empty, 1,000,001 items, non-finite, out-of-range, oversized integer, or invalid threshold → `ValueError`;
- rejected Python type → `TypeError`;
- one value → ratio `0.0` at any valid non-negative threshold;
- equality or tolerance-closeness to threshold → not anomalous;
- integer fields compare exactly; floating fields use `rel_tol=abs_tol=1e-12` in parity tests.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/tests/test_parity.py" check="rust:contract" -->
```python source-ref
def assert_equivalent(samples, threshold):
    """The companion test compares reference and native fields."""
```

**Exercise:** predict the exception for `[True]`, `[2**53 + 1]`, and `[float("nan")]`. **Hint:** type validation happens before numeric range validation. **Solution:** `True` gives `TypeError`; the other two are accepted types but invalid values, so they give `ValueError`.

## 10. Pythonic classes and transactional state

`Summary` is `#[pyclass(frozen)]`: Python can read properties but cannot assign a new mean. `OnlineStats` is mutable and offers `add`, `extend`, `reset`, and four properties. Empty/reset state is exactly `0, None, None, None`.

All `OnlineStats` methods remain interpreter-attached and never call `Python::detach`. The class is not presented as a concurrent mutation primitive. PyO3 runtime borrow checks help enforce one mutable access, but application-level concurrent design still needs an explicit owner or synchronization.

The maximum total count is one million. `extend([4, bad, 5])` first converts the whole candidate batch; if any value fails, the old state remains intact.

Common mistake: mutate count as each Python element is extracted. If element 200 fails, state becomes partial. The tested design extracts and validates before committing.

## 11. Errors and panic boundaries

Expected input errors travel as `Result<T, DomainError>` in Rust and as documented `TypeError`/`ValueError` in Python. PyO3 operations return `PyResult<T>` and use `?` to preserve the active Python exception.

`unwrap` and `expect` are forbidden on user-controlled values. The two `expect` calls in the survival executable protect literal invariants written in that file; tests and review make that distinction visible. Panic is a bug/emergency signal, not normal validation. This chapter does not intentionally panic inside the learner's interpreter or implement manual `extern "C"` FFI.

**Recover:** if you see `PanicException`, isolate a minimal reproduction in a subprocess, inspect the Rust invariant, and convert expected failure into `Result`; do not catch panic as ordinary business logic.

## 12. Dual-language tests and typing

Each layer protects a different risk:

- `cargo fmt --check`: stable formatting;
- clippy with `-D warnings`: suspicious Rust patterns;
- `cargo test --locked`: domain behavior without Python;
- pytest: facade, extraction, parity, errors, classes, threads, and native import;
- `python -m mypy.stubtest faststats_rs`: installed runtime agrees with stubs;
- `python -m mypy --strict tests/typing_consumer.py`: a consumer receives useful types.

Manual `_native.pyi` and `py.typed` are the stable contract. PyO3 experimental introspection can be explored, but it does not replace checked-in reviewed stubs.

Tests disable pytest cache and run against a built extension. Count targets are not coverage claims: each assertion states a behavior or risk.

## 13. `Python::detach` and deterministic concurrency

The binding extracts and validates while attached, then moves `Vec<f64>` and numeric configuration into:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/src/lib.rs" check="rust:contract" -->
```rust source-ref
let result = py.detach(move || domain::summarize(&values, threshold));
```

Inside that closure there is no `Python<'py>`, `Bound`, Python callback, or borrowed Python data. It returns a Rust-owned result. Only afterwards does attached code create `Summary` or an exception.

A timeout alone does not prove parallel entry. The acceptance-only `test-hooks` build uses a Rust `Mutex`/`Condvar` rendezvous: both detached calls must enter before either continues. A serial or GIL-held implementation cannot pass. If its one-second deadline expires, the binding reports a dedicated `RuntimeError` instead of misclassifying the failure as invalid input. The feature is off by default; `src/test_hooks.rs` is absent from the sdist, and release wheels expose no hook API or symbol.

`gil_used = true` remains on the base module. Releasing the GIL around one safe region does not mean every class, global, dependency, and reference-counting path is audited for free-threaded Python.

## 14. Benchmark honestly: boundary, copy, and batching

The benchmark first compares every public result field (`count`, `minimum`, `maximum`, `mean`, `anomaly_count`, and `anomaly_ratio`) plus representative `TypeError`/`ValueError` behavior against the Python oracle. Only then does it record release profile and host, warm both paths, collect repeated samples, and report medians for several sizes. Sequence→`Vec` copy is included.

```bash illustrative
python benchmarks/benchmark.py
```

Small inputs may be slower in Rust because conversion and the call dominate. That is useful information. Batch larger work, keep it in Python, or use an existing vectorized library. There is no required speedup.

**TODO:** add `n=100` without removing other sizes. **Hint:** compare medians, not a single run. Explain changes in workload and noise; do not report one machine as universal performance.

## 15. Distribution: sdist first, then two wheel modes

A source distribution contains material needed to rebuild: metadata, license notice, README, Python facade/stubs, Rust sources, Cargo metadata and `Cargo.lock`, the pinned toolchain, and the direct Python development-tool pins. It excludes `target`, caches, built libraries, and test rendezvous source.

The verifier builds the sdist in a temporary directory, unpacks it, and builds the wheels from that unpacked source—not from the richer working tree. Each wheel is inspected and installed into a fresh venv from a foreign cwd.

The version-specific filename records current Python ABI and platform, for example `cp313-cp313-manylinux_..._x86_64`. The exact tag is evidence from the current host, not a promise for macOS or Windows.

The hero build enables `abi3-py311` and expects `cp311-abi3-<platform>`. Stable Python ABI can cover compatible GIL-enabled CPython versions from 3.11 onward, but it does not remove OS, architecture, external library, or API limitations.

`abi3t` is a future/conditional PyO3/maturin path requiring Python 3.15+ and a separate free-threaded audit. The base wheel does not claim it.

## 16. One-command verification

From the chapter directory:

```bash illustrative
python -B examples/faststats-rs/tools/verify.py
```

It uses temporary `CARGO_TARGET_DIR`, wheel outputs, venvs, and working directories. It verifies Rust 1.97.0, fmt, clippy, Cargo tests, the expected ownership compiler error and solution, first extension, test-hook wheel, release sdist, version-specific and abi3 wheels, pytest, typing, benchmark smoke, clean imports, tags/content, and chapter hygiene.

The root book gate additionally calls the Rust-only adapter:

```bash illustrative
python -B ../tools/validate_book.py --plugin chapter-25-python-rust-integration/tools/bookcheck_plugin.py
```

The plugin checks Rust/PyO3/source contracts only. The root owns generic Markdown, selectors, links, RTL, accessibility, snippet classifications, and repository hygiene.

## 17. Guided capstone modifications

### Exercise A: add a boundary case

Objective: protect the exact integer contract. Add tests for `-(2**53)` and `-(2**53)-1`.

- TODO: add the values to parity tests.
- Hint: the first is accepted; the second raises `ValueError`.
- Success: reference/native agree and existing tests still pass.
- Why: a conversion boundary without a tested edge drifts easily.

### Exercise B: preserve transactionality

Objective: make partial mutation observable. Extend an `OnlineStats` containing `[1, 2]` with `[3, float("inf"), 4]`.

- TODO: snapshot all four properties before the call.
- Hint: assert the exception and the complete snapshot afterwards.
- Solution: `tests/test_classes.py` uses the same arrange/fail/compare pattern for several invalid types.

### Exercise C: decide against Rust

Objective: practice engineering judgment. Choose a small workload from your project and write a decision note.

- Measure current Python behavior.
- Identify whether calls can be batched.
- Include build/release/maintenance cost.
- Accept “keep Python” as a successful result when evidence supports it.

## 18. Common mistakes by layer

- **Rust compiler:** ownership error → identify move/borrow/scope before cloning.
- **Cargo:** lock mismatch → run the documented update deliberately, inspect `Cargo.lock`, rerun all suites.
- **Linker:** missing system tool → install platform build tools; changing Python code cannot fix it.
- **maturin:** inactive venv → activate it or build/install a wheel.
- **Import:** local source shadows install → change cwd and inspect `module.__file__`.
- **PyO3 extraction:** permissive conversion accepts too much → check exact Python type first.
- **GIL:** detach closure touches Python → extract owned values before detach, convert result after.
- **Packaging:** working tree builds but sdist fails → always rebuild from unpacked sdist.
- **Performance:** one fast run becomes a claim → verify equality, warm up, repeat, report context.

Errors are evidence about a layer, not a verdict about the learner. Diagnose the lowest failing layer before changing higher-level code.

## 19. Route checkpoints and rubric

At each route, explain your result aloud or in notes:

- Preparation: identify active Python/Rust/target and recover from one setup error.
- Essential: explain who owns a `String`, why a slice is borrowed, and how `Result` carries failure.
- Integration: trace one call across facade, PyO3, owned data, domain, and exception/result.
- Professional: demonstrate parity, transactional state, typing, and clean installed import.
- Hero: explain detached closure safety, rendezvous proof, benchmark limits, and wheel tags.

Final rubric, scored 0–2 each: correctness; idiomatic ownership; boundary safety; API clarity; error recovery; Rust/Python tests; deterministic concurrency; honest measurement; packaging/typing evidence; and your explanation. A complete capstone has no category at 0 and at least 16/20.

## 20. Glossary and reflection

- **crate:** Rust compilation/package unit.
- **ownership:** rule defining which value is responsible for releasing a resource.
- **borrow:** temporary access without taking ownership.
- **PyO3:** Rust bindings and macros for CPython integration.
- **GIL:** lock used by ordinary CPython builds to protect interpreter access.
- **ABI:** binary-level agreement between compiled components.
- **sdist:** source archive used to rebuild a package.
- **wheel:** built Python distribution tagged for compatible runtimes/platforms.
- **abi3:** CPython stable ABI mode with a minimum Python version and platform-specific wheel.

Reflection: where is the narrowest useful native boundary in `faststats_rs`? Which complexity would appear if we borrowed a mutable NumPy buffer or stored Python handles in global Rust state? If you cannot state the owner, lifetime, error path, test, and artifact compatibility, the boundary is not ready.

## Verified references

- [Official Rust installation](https://rust-lang.org/tools/install/)
- [The Rust Book: ownership](https://doc.rust-lang.org/stable/book/ch04-01-what-is-ownership.html)
- [The Rust Book: error handling](https://doc.rust-lang.org/stable/book/ch09-00-error-handling.html)
- [PyO3 0.29 guide](https://pyo3.rs/v0.29.0/)
- [PyO3 parallelism and `Python::detach`](https://pyo3.rs/main/parallelism)
- [maturin mixed-project layout](https://www.maturin.rs/project_layout.html)
- [maturin bindings and stable ABI](https://www.maturin.rs/bindings.html)

Version-sensitive material was checked on 2026-07-13 and is pinned in the companion assets. Re-run the full verifier before changing a pin.
