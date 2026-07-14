---
name: verify-python-learning-assets
description: Verify executable Python educational content with bounded, reproducible evidence. Use when reviewing Markdown fences, runnable or expected-error examples, companion sources, stable outputs, cleanup behavior, or CPython-version claims in lessons and tutorials.
---

# Purpose

Verify what a Python lesson actually executes without turning illustrative prose into evidence. Produce a path-specific record that another maintainer can reproduce.

## Required preparation

1. Read the repository instructions, style guide, validator configuration, and the canonical lesson.
2. Identify the declared CPython versions, dependencies, working directory, inputs, expected output or diagnostic, and companion tests.
3. Read [the execution and fence contract](references/execution-contract.md) before classifying or running Markdown blocks.
4. Read [the evidence and recovery contract](references/evidence-and-recovery.md) when reporting a result or repairing a failure.

## Core workflow

1. Inventory every fenced block and every referenced companion source. Preserve source paths and line locations.
2. Classify each block as `runnable`, `expected-error`, `compile-only`, `source-ref`, `todo`, `illustrative`, or `output`. Do not infer execution from prose alone.
3. Run only trusted, standard-library, single-process Python in the generic path. Delegate networking, package installation, multiprocessing, native code, and external toolchains to an explicit companion verifier or domain plugin.
4. Execute eligible code with the declared interpreter using `-I -B`, no stdin, a minimal allowlisted environment, a disposable working directory, and hard time and output bounds.
5. Compare stable behavior: exit status plus meaningful output for success, or nonzero status plus a stable exception type/message signal for an expected failure.
6. Verify the recovery path after an expected error. Require an explanation of the correction and a successful bounded example.
7. Run the repository validator and the directly owning companion tests. Never convert an unavailable or unselected verifier into a pass.
8. Record interpreter/tool versions, repository-relative source, command, bound, exit status, comparison, cleanup, and any explicit unsupported result.

## Safety and truthfulness

- Treat repository snippets as trusted educational input, not hostile code; the runner is an accident guard, not a security sandbox.
- Keep fixtures read-only and copy only declared inputs into temporary storage.
- Terminate the whole child process group on timeout and reject surviving descendants.
- Redact credentials, personal data, absolute paths, and unsafe captured payloads from reports.
- Leave no cache, bytecode, virtual environment, generated artifact, or modified repository file.
- Report `not run`, `unsupported`, `failed`, or `passed` distinctly. Never call `illustrative`, `todo`, or unselected `source-ref` content executed.

## Handoff

Report the verified matrix, evidence paths, exact failed phase, and the smallest safe recovery. Escalate semantic teaching quality to `professor`, publication parity to `book-editor`, and domain behavior to the matching network, packaging, or native-interoperability skill.
