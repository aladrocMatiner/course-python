---
name: python-packaging-release
description: Design and verify Python packaging and release lessons with artifact-backed evidence. Use for virtual environments, pyproject.toml, build isolation, requirements, constraints, locks, sdists, wheels, compatibility tags, clean installs, native runtime dependencies, or release claims.
---

# Purpose

Verify the artifact learners will install, not only the source checkout. Keep build, install, import, and release claims scoped to evidence.

## Required preparation

1. Read repository instructions, package manifests, build backend configuration, dependency inputs, tests, and the claimed interpreter/platform matrix.
2. Read [dependency evidence and terminology](references/dependency-evidence.md) before describing requirements, constraints, snapshots, locks, or reproducibility.
3. Read [artifact verification](references/artifact-verification.md) before building, inspecting, installing, or auditing a distribution.
4. Identify whether the package is pure Python or native and route native ABI/lifetime checks to `engineer-python-native-interop`.

## Core workflow

1. Start from a clean source tree and create all environments, build directories, caches, and artifact outputs in temporary storage.
2. Record the interpreter, build frontend/backend, installer, compiler when relevant, and the exact dependency input used.
3. Build with isolation enabled unless the lesson explicitly demonstrates another bounded case. Fail on missing or inconsistent metadata.
4. Build both source distribution and wheel when both are claimed. Inspect member paths, metadata, licenses/notices, package data, typing markers/stubs, native libraries, and compatibility tags.
5. Rebuild the wheel from the produced source distribution when reproducibility of the source artifact is claimed.
6. Install the artifact with dependencies handled according to the declared contract into a second clean environment.
7. Import and exercise the public API from a foreign working directory outside the source tree. Confirm the import resolves to the installed artifact.
8. Run normal, boundary, invalid, and recovery behavior plus typing and native dependency inspection when promised.
9. Report each phase independently: resolve, build, inspect, install, import, behavior, typing, and cleanup. Rebuild from clean state after a correction instead of accepting cached output.

## Claim and release boundaries

- Call a file a complete lock only when its resolver scope and transitive evidence justify that term. Direct pins, constraints, and `pip freeze` snapshots are not automatically portable or reproducible locks.
- Treat wheel tags as compatibility declarations, not proof that every tagged host was tested.
- Record only the platforms and toolchains actually executed. Keep other targets designed, intended, or unverified as appropriate.
- Never upload to an index, sign, attest, publish, or create a production release without separate explicit authorization.
- Leave no virtual environment, `build/`, `dist/`, wheel, sdist, cache, native output, credential, or generated metadata in the source tree.

## Handoff

Provide artifact names and digests, verified host/tool versions, inspection and foreign-import evidence, failed phase with recovery, and explicit unverified targets. Do not describe a source-tree test as installed-package evidence.
