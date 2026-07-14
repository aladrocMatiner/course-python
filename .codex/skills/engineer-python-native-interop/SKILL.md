---
name: engineer-python-native-interop
description: Design, review, and verify Python native interoperability boundaries. Use for C++/CMake/pybind11 or Rust/Cargo/PyO3/maturin extensions, ownership and lifetime, GIL behavior, exception mapping, typing, ABI, native artifacts, sanitizers, and concurrency claims.
---

# Purpose

Verify Python/native boundaries from an autonomous domain core through an installed wheel. Keep shared evidence rules concise while preserving language-specific toolchain semantics.

## Select the domain reference

- For C++, CMake, or pybind11 work, read [the C++ interoperability workflow](references/cpp.md). Do not load the Rust reference unless Rust is also in scope.
- For Rust, Cargo, PyO3, or maturin work, read [the Rust interoperability workflow](references/rust.md). Do not load the C++ reference unless C++ is also in scope.
- For a comparison that changes both implementations, load both and report their evidence separately.

## Shared workflow

1. Read repository instructions, the chapter contract, manifests, companion verifiers, tests, stubs, and traceability evidence.
2. Record exact Python ABI, interpreter, compiler/linker, build frontend, binding library, platform, architecture, build profile, and requested optional capabilities.
3. Build in disposable directories from a clean configuration. Keep the domain core independently testable without Python dependencies.
4. Verify conversions at the boundary: accepted exact/coercible types, size/range limits, overflow, invalid data, native errors, and stable Python exception classes/messages.
5. Verify ownership and lifetime with deterministic tests. Make object owners, borrowed views, callbacks, and teardown order explicit.
6. Verify Global Interpreter Lock (GIL) behavior with an owned-data rule: touch no Python object while detached/released, reacquire before Python access, and prove concurrency with rendezvous coordination rather than sleeps.
7. Build and inspect source and wheel artifacts, typing surfaces, package contents, tags, runtime dependencies, test-hook exclusion, and clean import from a foreign working directory.
8. Compare Python and native results before measuring performance. Record profile, host, warmup, repetitions, sizes, and complete public result parity without promising universal speed.
9. Run the explicit domain plugin and available full verifier. Separate `passed`, `failed`, `supported skip`, `prerequisite missing`, and `not run`; unexecuted work never passes.
10. Remove build trees, virtual environments, Cargo/CMake output, wheels, sdists, native binaries, caches, core dumps, and temporary credentials from source.

## Failure recovery

Preserve a bounded actionable diagnostic, identify the exact configure/build/test/import/artifact phase, correct the smallest contract, and rerun from a clean configuration. Never reuse an artifact produced before the correction.

## Handoff

Report evidence per language, profile, ABI, and host. State lifetime/GIL assumptions, artifact findings, typing results, and every unsupported or unverified target explicitly.
