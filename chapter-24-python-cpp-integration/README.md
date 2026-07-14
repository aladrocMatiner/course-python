# Chapter 24: Python and C++ Integration — From Zero to Hero

English | [Español](README.es.md) | [Català](README.ca.md) | [Svenska](README.sv.md) | [العربية](README.ar.md)

This chapter teaches one boundary, not two unrelated languages: how Python owns a friendly API while C++ performs carefully delimited native work. You start without C++ experience, compile a small executable, build a first extension, and finish with the typed `faststats_cpp` package and a separate embedded-Python host.

The companion projects were verified on Linux with CPython 3.13.11, GCC 13.3.0, CMake 4.1.2, pip 25.3, pybind11 3.0.4, and scikit-build-core 1.0.3. The design targets CPython 3.11+, C++17, CMake 3.20+, GCC/Clang/MSVC, but this record is not a claim that every target was executed.

## Learning objectives and prerequisites

By the end you can:

- distinguish compiler, linker, loader, Python API/ABI, C++ ABI, and wheel tags;
- read the C++17 subset needed for a binding: values, references, `const`, vectors, classes, RAII, smart pointers, and exceptions;
- separate a Python-independent core, a thin pybind11 boundary, a private native module, and a typed public facade;
- reason explicitly about copies, borrowed memory, owners, lifetimes, the Global Interpreter Lock (GIL), callbacks, and threads;
- build an sdist and platform wheel, then prove the installed artifact from a clean environment;
- measure whether the boundary helps instead of assuming C++ is automatically faster;
- embed one trusted local Python strategy in a C++ host with controlled startup and teardown.

Required Python preparation: [functions](../chapter-11-functions/README.md), [object-oriented programming](../chapter-12-oop/README.md), [exceptions](../chapter-14-exceptions/README.md), [modules](../chapter-15-modulos/README.md), [environments](../chapter-16-entornos/README.md), [testing](../chapter-18-testing/README.md), [logging](../chapter-20-logging/README.md), and [introspection](../chapter-22-introspection/README.md). No prior C++ is required.

You need a local C++ compiler and may need Internet access or system permission to install it. All accepted build commands write into temporary directories; never paste a destructive cleanup command to compensate for a confusing build.

## Choose a route

| Route | Time | Runnable outcome | Completion check |
|---|---:|---|---|
| Essential | 4 sessions, 45–60 min each | executable plus `hello_cpp` extension | explain compile/link/load and rebuild after one edit |
| Professional | 5 sessions | typed `faststats_cpp` core, facade, errors, and ownership | native/reference contract and lifetime tests pass |
| Advanced | 5 sessions | safe buffers, callbacks, GIL-released owned work, wheel | concurrency and clean-install evidence pass |
| Hero | 3–4 sessions | sanitised core and embedded trusted strategy | state tested limits and decide when not to use C++ |

A route checkpoint is useful by itself; it is not the same as completing every later route.

## Glossary and boundary map

- **Compiler:** turns one C++ source file into machine-code object data.
- **Linker:** connects objects and libraries, resolving names between them.
- **Loader:** maps the final executable or shared library into a running process.
- **API:** source-level names and behaviours callers use.
- **ABI:** binary calling/layout contract. CPython ABI, C++ ABI, and platform libraries are separate constraints.
- **RAII:** Resource Acquisition Is Initialization; a C++ object's lifetime owns cleanup.
- **Borrow:** temporary access without ownership transfer.
- **GIL:** CPython lock required while touching Python objects or its C API.
- **Wheel:** installable archive whose tags describe Python, ABI, and platform compatibility.

```text illustrative
Python caller
  -> faststats_cpp public facade
  -> private _native binding (validate and convert)
  -> owned C++ values OR call-scoped borrowed buffer
  -> Python-independent faststats core
  -> Summary or translated exception
```

The facade is the public contract. `_native` is replaceable machinery. The core never includes `Python.h`. A borrowed buffer never enters the GIL-released path.

## Toolchain preflight

Create a disposable environment. The first installation can use the network; using the package manager for your compiler may require administrator permission.

```console illustrative
python -m venv /tmp/course-cpp-venv
source /tmp/course-cpp-venv/bin/activate       # POSIX
# .\course-cpp-venv\Scripts\Activate.ps1     # PowerShell alternative
python -m pip install -r chapter-24-python-cpp-integration/examples/faststats-cpp/requirements-dev.lock
python -B chapter-24-python-cpp-integration/tools/preflight.py
```

The preflight reports the exact interpreter, architecture, active environment, compiler, CMake, pip, pybind11, scikit-build-core, build, pytest, and mypy. If a layer is missing, fix that layer: a loader workaround cannot repair a missing compiler.

Platform next steps are deliberately separate from verification: on Ubuntu/Debian install the distribution's `build-essential` package; on macOS install Apple Command Line Tools with `xcode-select --install`; on Windows install Visual Studio Build Tools with the **Desktop development with C++** workload and use its Developer PowerShell. These actions may need network/admin approval. `requirements-dev.lock` records exact direct development-tool versions for the verified host, but it has no transitive graph or hashes and is not a hermetic cross-platform lock. Install it only inside the venv, use `constraints-build.txt` for isolated build inputs, rerun preflight, and claim support only for a platform you actually execute.

Accepted PEP 517 builds set `PIP_BUILD_CONSTRAINT` to `constraints-build.txt`. This keeps the isolated build environment on pybind11 3.0.4 and scikit-build-core 1.0.3. It is different from constraining packages installed into the runtime environment.

### Diagnose the phase, not the symptom

| Observation | Phase | First question | Reversible action |
|---|---|---|---|
| syntax or unknown type | compile | is the declaration/header visible? | inspect the first compiler diagnostic |
| unresolved symbol | link | was the defining object/library linked? | inspect target sources and link libraries |
| module exists but cannot import | load | do tags/dependencies match this interpreter? | test the installed wheel from a foreign cwd |
| Python `TypeError` | binding/API | did the value satisfy the documented contract? | reduce to one valid and one invalid call |

## Essential route: first C++ program

### Session 1 — values, functions, scope, and diagnostics

Prediction: in `ScoreReport report(std::vector<double>{6, 8, 10})`, who destroys the vector storage? The answer is the `ScoreReport` value: its vector member releases itself when the report leaves scope. That is RAII; there is no matching `free()` in learner code.

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/00-cpp-survival/src/main.cpp check=cpp:contract -->
```cpp source-ref
const course::ScoreReport report(std::vector<double>{6.0, 8.0, 10.0});
std::cout << report.label() << ": mean=" << report.mean() << '\n';
```

Build out of source:

```console illustrative
cmake -S chapter-24-python-cpp-integration/examples/00-cpp-survival -B /tmp/cpp-survival-build -DCMAKE_BUILD_TYPE=Debug
cmake --build /tmp/cpp-survival-build --config Debug
ctest --test-dir /tmp/cpp-survival-build --output-on-failure -C Debug
```

Happy path: output contains `practice batch: mean=8`. Edge case: constructing with an empty vector throws `std::invalid_argument`, which `main()` catches. Recoverable error: compile `expected_compile_error.cpp` separately and read the first missing-semicolon diagnostic; the file is deliberately excluded from CMake, so the normal build remains healthy.

**TODO:** change the three scores and predict the mean first. **Hint:** preserve `const` on the report and change only the vector values. **Solution:** the incremental expression `mean += (value - mean) / count` updates one owned `double`; no Python or heap-management concept is required yet.

Common mistake: editing a header but forgetting that the implementation lives in a namespace. Read the first diagnostic, verify the exact qualified name, then rebuild the temporary directory; do not delete unrelated caches.

### Session 2 — headers, references, vectors, classes, and exceptions

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/00-cpp-survival/include/score.hpp check=cpp:contract -->
```cpp source-ref
class ScoreReport {
public:
    explicit ScoreReport(std::vector<double> values);
    [[nodiscard]] double mean() const;
    [[nodiscard]] const std::string& label() const noexcept;
};
```

A header declares what other translation units may use. The source defines it. `const` after `mean()` promises not to mutate the report. `const std::string&` borrows the member without copying; it is safe only while the report is alive. `explicit` prevents surprising implicit construction. An exception represents a recoverable failure and is caught at an explicit boundary, never allowed to escape a destructor.

Checkpoint: explain, without code, the owner and lifetime of the label reference. If you cannot, return to the scope diagram before continuing.

**Microcycle:** predict what a copied return would change, run the happy label test, then TODO return a value instead of a reference. Hint: compare the signatures and observe that the empty constructor remains the recoverable edge. The explained trade-off is one allocation/copy versus a lifetime dependency; reflect on which contract is easier to maintain.

### Session 3 — compiler, linker, loader

Source becomes object data during compilation; object data becomes an executable/shared library during linking; importing asks the operating-system loader to map that library. The same word “build” hides three different failure phases. Practice classifying one compile error, one deliberate missing-definition link error described in the exercise, and one import error from an uninstalled module.

**TODO:** temporarily remove `src/score.cpp` from the `score` target and predict the phase. **Hint:** the declaration remains visible. **Explained solution:** compilation succeeds, but linking cannot find `ScoreReport` definitions. Restore the target source immediately after observing the diagnostic.

Verify both the restored happy build and the missing-definition edge, then reflect: the first diagnostic identifies the earliest broken phase, while later messages are often consequences.

### Session 4 — first pybind11 extension

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/01-first-extension/src/bindings.cpp check=cpp:contract -->
```cpp source-ref
PYBIND11_MODULE(hello_cpp, module) {
    module.def("add", &add, py::arg("left"), py::arg("right"));
}
```

`PYBIND11_MODULE` defines the loader entry point. CMake builds it; scikit-build-core connects CMake to PEP 517; the wheel carries the result. Build/install from a temporary directory, then import from another temporary working directory. Importing beside the source can hide packaging defects.

Prediction: what happens for `hello_cpp.add("20", 22)`? pybind11 rejects the string with `TypeError`; it does not silently parse it. Modify the C++ sum to subtraction, rebuild, observe the test fail, then restore it. That edit→build→test loop is the essential-route outcome.

## Professional route: freeze the contract before optimizing

### Session 5 — Python oracle and exact domain

`_reference.py` is readable executable semantics, not a silent fallback. `summarize` accepts 1–1,000,000 exact built-in `int`/`float` values: no `bool`, subclasses, `Fraction`, `Decimal`, NumPy scalar, or arbitrary `__float__`. Integers satisfy `abs(x) <= 2**53`; converted values are finite with `abs(x) <= 1e150`; threshold is finite in `[0, 1e150]`.

Mean is computed in input order with `mean += (value - mean) / count`. A second pass compares every sample with the final mean. A delta counts only when it is greater than the threshold and not `isclose` to it at relative/absolute tolerance `1e-12`. Therefore `[-3, -3, -1]` at `0.5` has three anomalies; threshold equality is excluded.

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/faststats-cpp/python/faststats_cpp/_reference.py check=cpp:contract -->
```python source-ref
expected = summarize([-3, -3, -1], threshold=0.5)
assert expected.anomaly_count == 3
```

Happy path: mixed exact ints/floats. Edge: one sample and an all-equal batch. Recoverable errors: empty, non-finite, out-of-range, wrong exact type, or invalid threshold. Tests compare native/reference floats with `rel_tol=abs_tol=1e-12`.

**TODO:** add one boundary case to reference and native parameterized tests. **Hint:** change only one constraint at a time. The solution is to assert both the exception class and unchanged state where state exists; reflect on why an exact contract is more useful than “accepts numbers.”

### Session 6 — core, binding, facade, typing

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/faststats-cpp/cpp/include/faststats_cpp/core.hpp check=cpp:contract -->
```cpp source-ref
[[nodiscard]] Summary summarize(const double* values, std::size_t size,
                                double threshold);
void normalize_in_place(double* values, std::size_t size);
```

The core receives C++ domain values and is tested by CTest without Python. `bindings.cpp` checks Python-specific exact types and buffer metadata. `_native` remains private. `faststats_cpp/__init__.py` exposes the stable API, while `_native.pyi` and `py.typed` make consumers type-checkable.

An absent extension and a broken binary are different. The facade reports “not built” only for the exact missing private module; other loader failures remain visible. It never catches everything and substitutes `_reference.py`, because that would hide a damaged wheel.

**Microcycle:** predict which layer knows an invalid Python type, execute core CTest and facade pytest, then TODO change a public default in the stub only. Hint: strict typing and stubtest must catch the mismatch. Restore the shared default and reflect on why thin bindings reduce duplicated truth.

### Session 7 — classes and transactional errors

`OnlineStats.add`, `extend`, and `reset` expose `count`, `minimum`, `maximum`, and `mean`. Empty/reset values are `0, None, None, None`. The total is capped at 1,000,000. `extend` validates every value and capacity before applying any change, so a bad final element preserves the complete previous state.

Prediction: after `[1, 2]`, what should `extend([3, inf])` leave behind? Exactly `(2, 1, 2, 1.5)`. This is stronger than “an exception occurs”; it is a transactional error contract.

The C++ domain exception is translated to `FaststatsError`; normal type/range/layout failures use `TypeError` or `ValueError`. A Python callback exception is re-raised to the active caller after C++ RAII cleanup. No exception crosses `main()`, a destructor, or `noexcept`.

**TODO:** extend valid values, then append one invalid value and compare state before/after. **Hint:** validate into temporary owned storage first. The happy extension commits; the edge is empty extension; the failure rolls back completely. Reflect on whether callers could safely retry a partially applied operation.

### Session 8 — ownership, policies, and smart holders

| Boundary | Owner | Borrower duration | Binding evidence |
|---|---|---|---|
| returned `Summary` | Python wrapper owns a value | none | read-only properties |
| `Dataset.metadata` | parent `Dataset` | child reference | `reference_internal` test |
| `BorrowingView(dataset)` | caller/keep-alive relation | view lifetime | `keep_alive<1,2>` test |
| `TrackedResource` | unique smart holder | ownership can transfer | live counter returns to baseline |

`py::smart_holder` supports explicit smart-pointer relationships and Python-derived trampoline objects. It does not excuse an ambiguous raw owning pointer. `ObserverRunner` retains a Python-derived `ProgressObserver`; its destructor never calls Python. A callback failure remains the original Python exception.

**TODO:** draw owner arrows before reading `test_ownership_callbacks.py`. **Hint:** arrows start at the object that controls destruction. **Solution:** `reference_internal` ties a returned child to the parent; `keep_alive` ties constructor patient to nurse; `consume_resource` moves unique ownership into C++ and releases it once.

Professional checkpoint: run Debug and Release contract tests and explain every public operation's input domain, error type, and owner.

## Advanced route: buffers, GIL, measurement, and wheels

### Session 9 — copied iterables versus borrowed buffers

`summarize(iterable)` validates and copies into `std::vector<double>`: convenient and safe, but conversion costs time and allocation. `summarize_buffer` borrows a one-dimensional, native-`double`, aligned, positive-stride contiguous buffer. `normalize_in_place` additionally requires writable memory.

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/faststats-cpp/tests/test_buffers.py check=cpp:contract -->
```python source-ref
values = array("d", [2.0, 4.0, 6.0])
faststats_cpp.normalize_in_place(values)
assert values.tolist() == [0.0, 0.5, 1.0]
```

Both buffer APIs keep the GIL throughout the borrow and forbid caller mutation at the same time. No pointer is retained after return. The full numeric/layout validation happens before mutation; a NaN, empty, oversized, read-only, strided, multidimensional, wrong-format, or misaligned buffer is rejected without partial changes. Equal values become all `0.0`.

NumPy is an optional next step, not a dependency here; `array('d')` and `memoryview` expose the protocol with the standard library.

**TODO:** pass a read-only and a strided `memoryview` before reading the solution test. **Hint:** inspect format, dimensionality, stride and writable before dereferencing. Valid contiguous data is the happy path; constant data is the edge; incompatible layout is the recoverable error. Reflect on when a documented copy is safer than zero-copy.

### Session 10 — callbacks, GIL, and deterministic concurrency

Python objects require the GIL. `summarize_many` first validates/copies while holding it, then wraps only core work on owned C++ storage in `py::gil_scoped_release`. Result creation and exception translation happen after reacquisition. Borrowed buffers and callbacks never enter that region.

The concurrency test does not trust a sleep. A separate `_faststats_test` CMake target, compiled only with `FASTSTATS_TEST_HOOKS`, uses a C++ mutex/condition-variable rendezvous: two calls must enter the released native region before either continues. A serial or GIL-held implementation times out. The wheel neither compiles nor exposes that hook.

Common mistake: release the GIL around a `py::object` because the operation “looks slow.” Correct sequence: validate/convert → own data → release → pure C++ → reacquire → create Python result.

**TODO:** temporarily remove `gil_scoped_release` only in the test target and predict the rendezvous outcome. **Hint:** the two Python threads cannot both cross the gate. Restore it after the bounded failure; the happy path proves simultaneous native entry, while timeout is the recoverable diagnostic. Reflect on why a fixed sleep would prove less.

### Session 11 — honest benchmarks

The benchmark checks parity before each group, warms up, takes multiple samples, reports the median, records profile/software/platform, and uses sizes 1, 10, 1,000, and 100,000. A one-element native call may lose because crossing and conversion dominate. That is a useful result, not a failed lesson.

```console illustrative
python chapter-24-python-cpp-integration/examples/faststats-cpp/benchmarks/benchmark.py --profile release --repeats 7
```

**TODO:** write a hypothesis for the crossover size, then measure. **Hint:** compare batching, not just language labels. **Solution:** retain Python when work is small or already delegated to an optimized library; use C++ only after correctness and representative measurement.

### Session 12 — sdist, wheel, tags, and clean install

`verify_artifacts.py` builds an sdist in a temporary directory, inspects it, unpacks it, rebuilds the wheel from that distributed source, and installs it into a fresh venv with a foreign cwd. It runs `pip check`, smoke, `mypy.stubtest`, a strict typed consumer, negative type checks for three native-only constructors, and verifies the test hook is absent. On supported hosts it parses the dependency inspector and fails when `ldd` reports `not found`; merely printing inspector output is not a pass.

Wheel tags encode Python, ABI, and platform. They do not encode the compiler version, libstdc++/C++ ABI, or every shared library; those are audited separately with local platform tools. Never rename a wheel to `abi3`: Limited API, CPython ABI, C++ ABI, and platform dependencies are different promises.

Advanced checkpoint: explain why “works from the source directory” is weaker than “wheel rebuilt from sdist works in a clean venv.”

**TODO:** inspect the generated wheel name and list what it does not promise. **Hint:** separate Python/ABI/platform tags from compiler, C++ ABI and shared libraries. A clean install is the happy path; a foreign interpreter is the compatibility edge; a loader error must remain visible. Reflect before describing any wheel as portable.

## Hero route: debugging, embedding, and runtime limits

### Session 13 — Debug, warnings, and sanitizers

Debug preserves symbols; Release represents the distributable profile. Project code compiles with high warnings as errors. On GCC/Clang, `FASTSTATS_ENABLE_SANITIZERS=ON` adds AddressSanitizer and UndefinedBehaviorSanitizer only to the autonomous core/tests, not indiscriminately inside CPython. Unsupported toolchains report a skip.

Do not teach a segfault as an interactive Python exercise. Explain use-after-free with owner diagrams, counters, C++ tests, and sanitizer evidence. Reconfigure a new temporary build directory so returning to the normal profile is reversible.

**TODO:** run the sanitized core where supported and locate the profile-specific flags. **Hint:** they belong only to autonomous targets. CMake writes capability evidence; the verifier reports success only when it reads `enabled:<compiler>`, otherwise it emits an explicit unsupported-compiler skip. A sanitizer report is a recoverable investigation, not permission to continue. Reflect on the smallest safe reproducer.

### Session 14 — embed one trusted strategy

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/embed-python/src/main.cpp check=cpp:contract -->
```cpp source-ref
py::scoped_interpreter interpreter;
py::module_ strategy = py::module_::import("trusted_strategy");
py::object result = strategy.attr("evaluate")(values);
```

The separate host requires `--strategy-dir`. It canonicalizes that trusted local directory, replaces `sys.path` with the controlled path, imports the fixed `trusted_strategy` name, passes a typed list, requires an exact float result, and maps missing/raised/invalid cases to documented non-zero exits. Tests run from a foreign cwd containing a malicious same-name decoy, which must not win.

All Python handles die before `py::scoped_interpreter`. The host catches Python and C++ exceptions at `main()`'s upper boundary. It never evaluates user text or loads an untrusted module: embedded Python has the host process permissions.

**TODO:** run good, raising and invalid-result strategies from the decoy cwd. **Hint:** the fixed module must come from the canonical strategy directory. Success is the happy path; missing callable/result type are edges; Python exception maps to a non-zero exit. Reflect on why arbitrary `eval` would change the threat model.

### Session 15 — free-threading and subinterpreters are future audits

The base module does not use `mod_gil_not_used()` and does not claim free-threaded or subinterpreter safety. Before such a claim, audit global/static state, allocators, holders/trampolines, callbacks, locks, module initialization, interpreter-local data, teardown, and a target-runtime test matrix. A compatibility tag is not evidence.

Alternatives remain valid: Cython for Python-like compiled code, nanobind for another modern binding design, SWIG for interface generation, `ctypes` for a stable C ABI, and the raw C API for maximum control. They are decision options, not parallel tutorials here. GPU, SIMD, OpenMP, cross-compilation, mobile/WASM, production publishing, and a large external library are outside this chapter.

**TODO:** write a proposed support matrix without changing code. **Hint:** include runtime, interpreter count, callbacks, global state and teardown. The base GIL build is the happy tested path; free-threaded/subinterpreter configurations are unverified edges. The solution is a new evidence-backed change, not a tag; reflect on the cost of every compatibility promise.

## Capstone verification

Run from the repository root. It creates its venv/builds/wheels in temporary directories and can require network access for the initial pinned direct-tool installation.

```console illustrative
python -B chapter-24-python-cpp-integration/tools/verify_all.py
python -B tools/validate_book.py --plugin chapter-24-python-cpp-integration/tools/bookcheck_plugin.py
```

The verifier covers survival, first extension, core CTest, Debug/Release pytest, deterministic concurrency, sanitizers when supported, sdist→wheel, typing, shared-library inspection, and embedding success/failures. An explicit hygiene scan must still find no venv, build, dist, archive, native library, object, or cache in the chapter tree, including ignored paths.

## Exercises, hints, and explained solutions

1. **Essential:** add `range()` to `ScoreReport`. Predict the result for negative values. Hint: compute min/max in one pass. Solution principle: keep ownership inside the class and test empty input before indexing.
2. **Professional:** add a read-only `variance` field first to `_reference.py`. Hint: freeze semantics and error behaviour before binding. Solution principle: extend reference, core, binding, stub, CTest, pytest, then docs—in that order.
3. **Advanced:** compare iterable and buffer calls for 100,000 doubles. Hint: verify equal summaries before timing. Solution principle: attribute differences to conversion/copy/boundary, not “Python versus C++” as a single cause.
4. **Hero:** propose free-threaded support without implementing it. Hint: list every global and Python-touching path. Solution principle: define an explicit runtime matrix and deterministic tests before adding a compatibility declaration.

## Self-assessment rubric

| Area | Ready | Needs another pass | Evidence |
|---|---|---|---|
| Correctness/API | contract and transactional failures match | results only look plausible | CTest plus native/reference pytest |
| Ownership/safety | every owner, borrow, GIL region is explainable | relies on default policy guesses | lifetime, buffer, callback, rendezvous tests |
| Verification | Debug/Release and artifacts run in temporary paths | imports beside source | verifier logs and clean venv |
| Engineering judgement | measurement and compatibility limits are stated | promises universal speed/portability | benchmark context and tag/dependency audit |

Final reflection: which boundary in your capstone deserves the most suspicion, and what evidence would make you trust it? If the answer is only “it compiled,” choose one invalid input, one lifetime, or one packaging scenario and strengthen the test.

## Sources and attribution

All lesson prose and exercises are original for this repository. Technical references: [Python extending and embedding](https://docs.python.org/3/extending/index.html), [pybind11 build systems](https://pybind11.readthedocs.io/en/stable/compiling.html), [pybind11 call policies](https://pybind11.readthedocs.io/en/stable/advanced/functions.html), [pybind11 smart holders](https://pybind11.readthedocs.io/en/stable/advanced/smart_ptrs.html), [scikit-build-core guide](https://scikit-build-core.readthedocs.io/en/stable/guide/getting_started.html), and [CMake FindPython](https://cmake.org/cmake/help/latest/module/FindPython.html).
