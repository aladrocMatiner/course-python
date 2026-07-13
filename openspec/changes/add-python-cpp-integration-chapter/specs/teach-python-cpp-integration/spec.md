## ADDED Requirements

### Requirement: Progressive Python and C++ Learning Path

The course SHALL provide a chapter 24 that teaches Python–C++ integration from no prior C++ knowledge through essential, professional, advanced, and hero routes using CPython 3.11 or later and C++17.

#### Scenario: Learner has never used C++

- **WHEN** a learner starts with Python knowledge but no C++ or native-toolchain experience
- **THEN** the chapter explains compiler, linker, loader, types, functions, headers, references, `const`, `std::vector`, RAII, and exceptions before relying on them
- **AND** the first route ends with a small executable before building a Python extension

#### Scenario: Learner completes a route

- **WHEN** the learner reaches an essential, professional, advanced, or hero checkpoint
- **THEN** the route states its prerequisites, estimated multi-session duration, runnable outcome, and self-assessment
- **AND** distinguishes that checkpoint from completing the full chapter

#### Scenario: Learner studies a boundary concept

- **WHEN** a new integration concept is introduced
- **THEN** the subsection follows objective/context, minimal theory, predict, execute, observe, modify, and verify
- **AND** includes a happy path, edge case, TODO, hint, common mistake, explained solution, and reflection

#### Scenario: Learner decides whether C++ is appropriate

- **WHEN** a workload can already be expressed in Python
- **THEN** the chapter asks for correctness and a measurable hypothesis before creating native code
- **AND** explains cases where pure Python, batching, another library, or no optimization is the better choice

### Requirement: Reproducible Native Toolchain

The chapter SHALL provide a preflight and build path for CPython 3.11+, a C++17 compiler, CMake 3.20+, pip >=25.3, pybind11 >=3.0.4,<4, scikit-build-core >=1.0.3,<2, declared build/test/type-check tools, isolated Python environments, and out-of-source builds.

#### Scenario: Supported toolchain is available

- **WHEN** the learner runs the preflight
- **THEN** it reports Python, interpreter architecture, compiler, C++ standard support, CMake, pip, pybind11, scikit-build-core, `build`, pytest, and mypy versions
- **AND** identifies the exact environment that subsequent commands will use

#### Scenario: Required component is missing

- **WHEN** Python, a compiler, CMake, headers, backend, or active venv is unavailable
- **THEN** the chapter identifies the missing layer and provides platform-specific next steps
- **AND** does not present a downstream linker or import workaround as the fix

#### Scenario: Build or import fails

- **WHEN** source compilation, linking, dynamic loading, or Python import fails
- **THEN** the lesson distinguishes the failing phase using the observed diagnostic
- **AND** provides a reversible diagnosis that preserves unrelated caches and files

#### Scenario: Clean rebuild is required

- **WHEN** stale native output is suspected
- **THEN** the learner removes only the documented build/temp/venv path and rebuilds from declared sources
- **AND** no command blindly deletes unrelated project or user data

#### Scenario: Initial setup requires network or privileges

- **WHEN** compiler or build dependencies are not already installed
- **THEN** the chapter explicitly marks which installation needs Internet or system permission
- **AND** does not promise an offline setup that the repository cannot provide

#### Scenario: Development tools are installed

- **WHEN** the verification environment is prepared
- **THEN** pytest, `build`, and mypy use the exact versions recorded in `requirements-dev.lock`
- **AND** pip >=25.3 uses `PIP_BUILD_CONSTRAINT` to pin pybind11 3.0.4 and scikit-build-core 1.0.3 inside every accepted isolated PEP 517 build and its log confirms them

### Requirement: Layered Native Extension Architecture

The capstone SHALL separate Python-independent C++ logic, binding code, private native module, public Python facade, type information, tests, benchmarks, and pure-Python reference behavior.

#### Scenario: C++ core is tested independently

- **WHEN** the native algorithm is built for CTest
- **THEN** it compiles and runs without including `Python.h`, pybind11 headers, or initializing Python
- **AND** its public inputs and outputs use C++ domain types

#### Scenario: Installed package is imported

- **WHEN** a consumer imports `faststats_cpp`
- **THEN** the public facade exposes the documented API while `_native` remains an implementation detail
- **AND** signatures, defaults, docstrings, `.pyi`, and `py.typed` agree

#### Scenario: Reference and native implementations are compared

- **WHEN** a shared valid or invalid input is evaluated
- **THEN** `_reference.py` and the native implementation follow the same documented semantics within the numeric tolerance
- **AND** tests verify results before performance measurement

#### Scenario: Native module cannot load

- **WHEN** `_native` is missing or binary-incompatible
- **THEN** the facade provides a diagnostic that distinguishes an unbuilt extension from a broken installed artifact
- **AND** does not silently hide the failure behind the Python reference implementation

#### Scenario: Import is tested outside the source tree

- **WHEN** the wheel is installed for artifact verification
- **THEN** import and smoke tests run from a temporary working directory outside the repository
- **AND** cannot pass by shadow-importing source files

### Requirement: Exact Faststats C++ Contract

The capstone SHALL implement a stable numeric contract shared by the Python reference and C++ implementation before optimization or benchmarking.

#### Scenario: Iterable batch input belongs to the accepted numeric domain

- **WHEN** samples are supplied through the iterable API
- **THEN** the API accepts 1 through 1,000,000 built-in `int`/`float` values only, excluding `bool`, `Fraction`, `Decimal`, NumPy scalars, and arbitrary `__float__` objects
- **AND** integers satisfy `abs(value)<=2**53`, converted values satisfy `abs(value)<=1e150`, and threshold is finite within `[0,1e150]`

#### Scenario: Batch summary is computed

- **WHEN** an accepted sequence or supported double buffer and threshold are supplied
- **THEN** the API returns immutable count, minimum, maximum, mean, anomaly count, and anomaly ratio
- **AND** both implementations compute mean in input order using `mean += (value - mean) / count` without fast-math

#### Scenario: Anomaly is classified

- **WHEN** the final input-order `Summary.mean` has been computed and a second pass evaluates `delta = abs(value - Summary.mean)` for each sample
- **THEN** it counts only if `delta > threshold` and it is not close to threshold under `rel_tol=1e-12, abs_tol=1e-12`
- **AND** equality or the tolerance band is not counted, and tests include `[-3,-3,-1]` at threshold `0.5` to distinguish final-mean classification from streaming classification

#### Scenario: Numeric results are compared

- **WHEN** reference and native floating-point fields are tested
- **THEN** tests use `rel_tol=1e-12` and `abs_tol=1e-12` unless a stricter exact integer comparison applies

#### Scenario: Invalid batch input is supplied

- **WHEN** the collection violates size/range/finiteness or threshold constraints
- **THEN** the API raises `ValueError`
- **AND** rejected types such as non-numeric, `bool`, `Fraction`, `Decimal`, NumPy scalars, or `__float__` objects raise `TypeError` without partial mutation

#### Scenario: Writable buffer is normalized

- **WHEN** a valid writable one-dimensional contiguous double buffer containing 1 through 1,000,000 finite values with `abs(value)<=1e150` is normalized
- **THEN** each value becomes `(value - minimum) / (maximum - minimum)`
- **AND** an all-equal buffer becomes all `0.0`

#### Scenario: Buffer numeric validation fails

- **WHEN** `summarize_buffer` or `normalize_in_place` receives zero or more than 1,000,000 values, a value outside `abs(value)<=1e150`, or data whose finiteness, format, shape, contiguity, alignment, or writable requirement fails
- **THEN** the complete buffer remains unchanged and the documented exception is raised

#### Scenario: Online statistics are updated

- **WHEN** valid built-in `int`/`float` values satisfying `abs(int)<=2**53` and finite `abs(value)<=1e150` are added or extended without taking the total above 1,000,000 samples
- **THEN** count, minimum, maximum, and mean update consistently
- **AND** empty/reset state exposes count 0 with minimum, maximum, and mean equal to `None`

#### Scenario: Online update is invalid

- **WHEN** an invalid, non-finite, out-of-range value is added/extended or an extension would take the total above 1,000,000 samples
- **THEN** the operation raises the documented exception and preserves the complete prior state

### Requirement: Pythonic Types Classes and Error Translation

The bindings SHALL expose typed functions, enums, a stateful class, keyword arguments, defaults, representations, callbacks, and stable Python exception behavior.

#### Scenario: Valid Python value crosses the boundary

- **WHEN** a documented number, iterable, enum, buffer, option, or class instance is supplied
- **THEN** pybind11 converts or borrows it according to an explicitly documented contract
- **AND** the lesson states whether a copy, move, reference, or allocation occurs

#### Scenario: Type range or shape is invalid

- **WHEN** input has the wrong Python type, numeric range, dimensionality, format, or mutability
- **THEN** the API raises the documented `TypeError`, `ValueError`, `OverflowError`, or domain exception
- **AND** no partial mutation or out-of-bounds access occurs

#### Scenario: C++ operation throws

- **WHEN** the core reports a recoverable domain error or throws a documented C++ exception
- **THEN** the binding translates it to a stable Python exception with useful non-sensitive context
- **AND** no C++ exception escapes through the CPython module boundary

#### Scenario: Python callback raises

- **WHEN** C++ invokes a Python callback that raises
- **THEN** the error remains associated with the active Python call and is re-raised to the Python caller
- **AND** C++ cleanup executes without replacing or discarding the original exception

#### Scenario: Destructor or noexcept path encounters a failure

- **WHEN** cleanup cannot complete normally
- **THEN** the design does not call Python from the destructor or let an exception escape a destructor/`noexcept` function
- **AND** reports failures at an earlier explicit operation where recovery is possible

### Requirement: Explicit Ownership and Lifetime Safety

The chapter SHALL teach and test value semantics, RAII, smart holders, return-value policies, borrowed references, keep-alive relationships, and deterministic native resource release.

#### Scenario: Python receives an owned value

- **WHEN** a function returns a value, moved object, unique object, or shared object
- **THEN** the binding identifies the owner and destroys the native resource exactly once
- **AND** the test does not depend on an undocumented exact CPython garbage-collection moment

#### Scenario: Python receives a borrowed child

- **WHEN** a child reference depends on a parent native object
- **THEN** the binding uses the correct explicit policy such as `reference_internal` or `keep_alive`
- **AND** a lifetime test proves the parent remains valid for the documented period

#### Scenario: Object participates in callbacks or virtual overrides

- **WHEN** a Python-derived object is retained by C++
- **THEN** the holder strategy keeps the associated Python object alive while C++ needs it
- **AND** releases the relationship when the native owner is destroyed

#### Scenario: Owning raw pointer is proposed

- **WHEN** a public binding would transfer or share ownership through a raw pointer
- **THEN** the implementation redesigns the API around values, RAII, `unique_ptr`, `shared_ptr`, or `py::smart_holder`
- **AND** does not rely on an ambiguous default return policy

#### Scenario: Potentially unsafe lifetime lesson is demonstrated

- **WHEN** the chapter explains use-after-free, double-free, or a wrong policy
- **THEN** it uses diagrams, counters, isolated C++ tests, or sanitizer evidence
- **AND** does not intentionally crash or corrupt the learner's Python interpreter

### Requirement: Safe Buffer Interoperability

The chapter SHALL contrast copied iterable conversion with validated, call-scoped buffer access using standard-library `array` and `memoryview`, with NumPy remaining optional.

#### Scenario: Generic iterable is processed

- **WHEN** the learner calls the convenient iterable API
- **THEN** the implementation validates elements and converts them into owned C++ storage
- **AND** the chapter explains the conversion/copy cost

#### Scenario: Compatible buffer is read

- **WHEN** a contiguous one-dimensional double buffer is passed to `summarize_buffer`
- **THEN** format, item size, shape, strides, alignment, and size are checked before reading
- **AND** the core processes the memory without an unnecessary element copy

#### Scenario: Compatible buffer is mutated

- **WHEN** a writable supported buffer is passed to `normalize_in_place`
- **THEN** the binding validates writable and the full layout before any mutation
- **AND** either completes the documented transformation or leaves the input unchanged on validation failure

#### Scenario: Incompatible buffer is supplied

- **WHEN** the buffer is read-only, non-contiguous, strided, misaligned, wrong-format, multidimensional, empty where forbidden, or otherwise unsupported
- **THEN** the API rejects it safely or explicitly takes a documented copy
- **AND** never reads or writes beyond the validated region

#### Scenario: Buffer call returns

- **WHEN** native processing finishes or raises
- **THEN** no pointer/reference into the Python-owned buffer is retained by C++
- **AND** cleanup follows normal RAII paths

#### Scenario: Borrowed buffer is processed

- **WHEN** `summarize_buffer` or `normalize_in_place` operates on Python-owned memory
- **THEN** the binding holds the GIL for the complete borrowed-memory operation and forbids concurrent caller mutation
- **AND** the borrowed pointer is never used by the GIL-released concurrency path

### Requirement: Correct GIL Threading and Callback Boundaries

The chapter SHALL explain and test GIL ownership, native work regions, callback acquisition, shared C++ state, exception recovery, and the limits of free-threaded/subinterpreter claims.

#### Scenario: Long pure-C++ operation runs

- **WHEN** input validation and conversion have produced C++-owned/copied data
- **THEN** the binding may release the GIL only around code that does not access Python
- **AND** reacquires it before creating Python results or exceptions

#### Scenario: Native code calls Python

- **WHEN** a callback, override, or Python object must be accessed
- **THEN** the executing thread owns/acquires the GIL before the access
- **AND** no callback runs inside an unguarded GIL-released region

#### Scenario: Two Python threads invoke native work

- **WHEN** two calls execute the long native operation concurrently
- **THEN** both make progress within a bounded timeout
- **AND** shared C++ state is immutable, isolated, or protected by a documented synchronization primitive

#### Scenario: Concurrent entry is proved deterministically

- **WHEN** the concurrency acceptance test runs
- **THEN** a C++17 test-only rendezvous implemented with mutex/condition-variable requires two native calls to enter before either proceeds
- **AND** a serial or GIL-held implementation cannot satisfy the test merely by completing before a timeout

#### Scenario: Test rendezvous is excluded from distribution

- **WHEN** the Release extension/wheel is built
- **THEN** `FASTSTATS_TEST_HOOKS` is disabled and the test-only hook is not compiled or exposed
- **AND** artifact smoke verifies the hook is absent from the installed module API

#### Scenario: Native exception occurs while GIL is released

- **WHEN** C++ work fails in the released region
- **THEN** native cleanup completes and the GIL is reacquired before translating the error
- **AND** the Python caller receives the documented exception

#### Scenario: Free-threaded or subinterpreter support is considered

- **WHEN** the hero route discusses these runtimes
- **THEN** it requires an audit of global state, allocators, holders, callbacks, locks, and module lifecycle
- **AND** the base capstone does not declare support or use compatibility tags without tests on the target runtime

### Requirement: Evidence-Based Native Performance

The chapter SHALL teach measurement that separates algorithmic work, conversion cost, call overhead, allocation, build profile, and native execution without a fixed speedup promise.

#### Scenario: Optimization begins

- **WHEN** the learner proposes moving code to C++
- **THEN** a correct Python reference, representative workload, and measurable hypothesis exist first

#### Scenario: Implementations are benchmarked

- **WHEN** Python and native paths are timed
- **THEN** they receive identical deterministic data and their results are checked before each measurement group
- **AND** the build profile and software/hardware context are recorded

#### Scenario: Timing is summarized

- **WHEN** benchmark results are reported
- **THEN** the benchmark uses warm-up, multiple samples, a robust summary such as median, and multiple input sizes
- **AND** separates or discusses conversion and call overhead

#### Scenario: Boundary work is too small

- **WHEN** the native path is equal to or slower than Python for a small operation
- **THEN** the lesson explains batching/granularity or retaining Python
- **AND** does not hide the result or require a universal speedup threshold

### Requirement: Native Packaging ABI and Wheel Verification

The chapter SHALL build and inspect an sdist and platform wheel through PEP 517, explain Python/API/ABI/platform compatibility, and test installed artifacts outside the source tree.

#### Scenario: Sdist is built

- **WHEN** the source distribution is created
- **THEN** it contains Python sources, C++ sources, public headers, CMake configuration, typing files, metadata, and required documentation
- **AND** excludes build outputs, venvs, caches, wheels, and compiled libraries

#### Scenario: Sdist can rebuild the wheel

- **WHEN** the sdist is unpacked in a temporary directory
- **THEN** a wheel is built from that unpacked source and not from the original repository
- **AND** the rebuilt wheel passes the same clean-install checks

#### Scenario: Wheel is built

- **WHEN** the platform wheel is created
- **THEN** it contains the public facade, type information, and native module at the expected private package path
- **AND** its filename/content tags are generated by the build backend

#### Scenario: Wheel tags are inspected

- **WHEN** the learner reads the wheel filename
- **THEN** they identify the encoded Python, ABI, and platform tags and relate them to the interpreter, operating system, and architecture actually built
- **AND** separately record compiler version, C++ ABI, and shared-library dependencies because wheel tags do not encode them directly

#### Scenario: Stable ABI is discussed

- **WHEN** Limited API, Stable ABI, or `abi3` appears
- **THEN** the chapter distinguishes CPython API/ABI, C++ ABI, platform dependencies, and pybind11's actual support constraints
- **AND** does not manually rename or retag the wheel

#### Scenario: Wheel is clean-installed

- **WHEN** the wheel is installed in a fresh temporary venv with no source-tree cwd
- **THEN** import, typing/resource presence, contract smoke tests, and `pip check` succeed
- **AND** the test proves the wheel rather than an editable/source installation

#### Scenario: Typing artifact is verified

- **WHEN** the clean-installed package is checked
- **THEN** `python -m mypy.stubtest faststats_cpp` and a strict typed consumer validate public names, signatures, defaults, classes, and properties
- **AND** any allowlist is narrow, explained, and versioned

#### Scenario: Another target is desired

- **WHEN** the learner wants a different OS, architecture, Python ABI, or interpreter
- **THEN** the lesson explains that a matching build or verified wheel matrix is required
- **AND** does not describe the local wheel as universal

### Requirement: Embedded Python Host

The hero route SHALL provide a separate C++ executable that owns one CPython interpreter lifecycle and calls a trusted local Python strategy through typed inputs and validated outputs.

#### Scenario: Embedded host succeeds

- **WHEN** the host starts with the documented environment and strategy module
- **THEN** it initializes Python before creating Python objects, imports/calls the strategy, validates the result, and exits successfully
- **AND** destroys all Python handles before interpreter teardown

#### Scenario: Trusted strategy path is selected

- **WHEN** the host receives `--strategy-dir`
- **THEN** it canonicalizes the documented local asset directory and imports a fixed module name from that controlled path
- **AND** a same-named module in the current working directory is not selected

#### Scenario: Strategy is missing or raises

- **WHEN** import fails, the callable is missing, the callback raises, or the return type is invalid
- **THEN** the top-level C++ boundary captures and reports useful context
- **AND** returns a documented non-zero exit code without an uncaught C++ exception

#### Scenario: Untrusted code execution is proposed

- **WHEN** a learner considers evaluating arbitrary text or loading an untrusted module
- **THEN** the chapter explains that embedded Python executes with the host process permissions
- **AND** keeps arbitrary code execution outside the laboratory

### Requirement: Native Testing Debugging and Capstone

The chapter SHALL provide autonomous C++ tests, Python contract tests, deterministic concurrency tests, artifact tests, debugging guidance, optional sanitizer checks, and a complete `faststats_cpp` capstone.

#### Scenario: C++ algorithm changes

- **WHEN** the core is modified
- **THEN** CTest validates numeric behavior and error cases without importing Python
- **AND** its explicit check harness returns non-zero on failure in both Debug and Release rather than relying on `assert` under `NDEBUG`

#### Scenario: Binding contract changes

- **WHEN** conversion, API, ownership, buffer, callback, or GIL code changes
- **THEN** pytest tests public behavior, parity, errors, lifetime evidence, and concurrency with bounded timeouts
- **AND** pytest cache output is disabled or directed outside the repository

#### Scenario: Debug build is requested

- **WHEN** native behavior needs diagnosis
- **THEN** documented CMake options enable symbols and strict warnings for project code through reversible build-directory configuration
- **AND** commands distinguish compiler, debugger, loader, and Python traceback information

#### Scenario: Memory-safety audit runs

- **WHEN** GCC/Clang sanitizer support is available for the autonomous core
- **THEN** ASan/UBSan execute core tests and report cleanly
- **AND** unsupported compiler/runtime combinations produce an explained skip rather than unsafe flags

#### Scenario: Learner completes the capstone

- **WHEN** all required routes are complete
- **THEN** `faststats_cpp` provides public facade, reference, C++ core, thin binding, typed API, safe buffers, stateful class, errors, ownership, GIL-correct work, tests, benchmark, sdist, and wheel
- **AND** the learner can explain each boundary's owner, copy behavior, error contract, GIL state, and compatibility limits

#### Scenario: Repository hygiene is checked

- **WHEN** final validation completes
- **THEN** an explicit filesystem scan finds no `.venv`, build directory, dist directory, wheel, sdist, compiled library, object file, sanitizer output, or cache inside the chapter tree, including ignored files

#### Scenario: All learning assets are verified

- **WHEN** the top-level chapter verifier runs
- **THEN** it compiles/tests `00-cpp-survival`, builds/imports `01-first-extension`, runs faststats Debug/Release/artifact checks, and exercises `embed-python`
- **AND** each subcommand uses declared environment and temporary output paths

### Requirement: Multilingual Integration and Scope Control

The course SHALL publish equivalent chapter 24 content in all five course languages, update all six root indexes, link localized prerequisites, coordinate active chapter reservations, and preserve the defined scope.

#### Scenario: Reader discovers chapter 24

- **WHEN** a reader opens any root index after coordinated integration
- **THEN** chapter 24 appears before the appendices and after lower-numbered implemented chapters
- **AND** preserves chapter 23/25 entries only when they are implemented, without creating dangling links

#### Scenario: Reader switches language

- **WHEN** a reader selects another language in chapter 24
- **THEN** the same chapter, routes, source references, commands, code semantics, warnings, exercises, and rubric remain available
- **AND** Arabic uses the repository's outer `<div dir="rtl">` convention while code remains readable LTR

#### Scenario: Reader uses accessible Markdown

- **WHEN** the chapter is rendered in any supported language
- **THEN** headings are hierarchical, links are descriptive, tables have simple headers, and meaningful visuals provide alt text plus an equivalent prose explanation
- **AND** instructions do not depend only on color, position, or icons while code and commands remain readable in RTL content

#### Scenario: Learner needs a prerequisite

- **WHEN** the chapter relies on functions, OOP, exceptions, modules, environments, testing, logging, or introspection
- **THEN** it links to chapters 11, 12, 14, 15, 16, 18, 20, or 22 in the current language

#### Scenario: Alternative binding technology is mentioned

- **WHEN** Cython, SWIG, Boost.Python, nanobind, ctypes, or the raw C API appears
- **THEN** it is placed in a concise decision matrix or next-step reference
- **AND** is not developed as a parallel implementation path

#### Scenario: Out-of-scope target appears

- **WHEN** GPU, SIMD, OpenMP, cross-compilation, mobile/WASM, production free-threading, a large external library, or remote publication is considered
- **THEN** the chapter marks it outside this change and does not add an unverified implementation

#### Scenario: Shared indexes have concurrent changes

- **WHEN** chapter 23, 24, and 25 proposals are applied or rebased
- **THEN** the six root indexes are reconciled serially so no accepted entry is lost
- **AND** final navigation preserves numeric order for implemented chapters and the appendices
