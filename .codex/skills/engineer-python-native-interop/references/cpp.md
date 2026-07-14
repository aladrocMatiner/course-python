# C++ interoperability workflow

## Toolchain and profiles

Record CPython ABI/architecture, compiler identity/version, C++ standard, CMake, build frontend/backend, pybind11, and build type. Configure Debug, Release, and requested sanitizer profiles in separate clean build directories; account for multi-config generators where the configuration is selected at build/test time.

Prove requested flags from generated compile/link commands or equivalent build evidence. A CMake option being true is not proof that a compiler accepted or used its flags. Report sanitizer outcomes separately:

- `passed`: supported flags were observed and the instrumented autonomous target ran cleanly;
- `failed`: configure/build/run or sanitizer diagnostics failed;
- `supported skip`: the chapter explicitly permits the detected compiler/platform limitation;
- `not run`: no instrumented execution occurred.

Never report the requested profile as passed when CMake silently omitted instrumentation.

## Boundary and lifetime

Keep Python headers and pybind11 out of the autonomous domain core. Centralize conversion and exception mapping in bindings.

Audit every returned reference/view and accepted callback for:

- native owner and destruction order;
- pybind11 return-value policy;
- `keep_alive`, holder, or `reference_internal` requirement;
- temporary/container reallocation invalidation;
- callback lifetime and interpreter shutdown;
- exception safety across the boundary.

Use deterministic owner counters, weak references, and safe test-only rendezvous. Do not teach deliberate segmentation faults inside Python; use an isolated native test and sanitizer evidence.

## GIL and concurrency

Validate and copy/own Python-derived data before `gil_scoped_release`. During the released region, access no Python object, buffer whose lifetime is not independently held, callback, or Python allocator. Reacquire before creating results or raising mapped Python exceptions.

Prove concurrent native entry with a bounded barrier/rendezvous. A speedup or sleep overlap alone is insufficient.

## Typing and artifacts

Keep Python facade, runtime extension, `.pyi`, and `py.typed` consistent. Run runtime boundary tests, a type checker, and `stubtest`; keep allowlists narrow, explained, and tied to unavoidable extension behavior.

Inspect wheel tags and native runtime dependencies with platform-appropriate tools. Fail a promised dependency audit when inspection cannot resolve a required library; do not reinterpret missing output as success. Confirm test-only extension targets/hooks are absent from sdists and release wheels.

## Repository commands

Use the Chapter 24 plugin for bounded contract evidence and its full verifier only where the declared toolchain/dependencies are provisioned. Keep all CMake trees, virtual environments, wheels, sdists, libraries, objects, logs, and core dumps under temporary storage. Record the exact host matrix; Linux evidence does not establish MSVC or macOS compatibility.
