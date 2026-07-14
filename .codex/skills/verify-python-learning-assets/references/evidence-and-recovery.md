# Evidence and recovery contract

## Result states

Use only evidence-backed states:

- `passed`: the declared command ran and every stated comparison and cleanup assertion passed;
- `failed`: execution ran but a behavior, diagnostic, cleanup, or mutation assertion failed;
- `unsupported`: the contract explicitly permits the detected interpreter/platform/tool limitation;
- `prerequisite missing`: required tooling is absent and the contract does not define a supported skip;
- `not run`: execution was not selected or no eligible verifier exists.

Never merge these states into a generic success.

## Stable comparisons

Prefer exact values, structured objects, exit codes, exception classes, invariant substrings, and explicit cleanup state. Avoid timestamps, absolute temporary paths, random ports, wall-clock performance thresholds, hash iteration order, locale-specific system errors, and full native tracebacks as golden output.

For a multi-version claim, run every declared version or narrow the claim to the versions actually executed. Distinguish Python language guarantees from CPython implementation behavior.

## Recovery loop

1. Preserve a bounded diagnostic with secret and absolute-path redaction.
2. Identify whether failure belongs to setup, parse/compile, execution, assertion, timeout, output bound, surviving process, source mutation, or cleanup.
3. Correct the smallest source or prose contract.
4. discard temporary outputs and rerun from a clean working directory;
5. rerun both the failing case and its happy/recovery neighbor;
6. report any matrix target that remains unexecuted.

Do not update expected output to match a bug, weaken a stable diagnostic until any error passes, or reuse state produced before the correction.

## Evidence handoff

Provide a compact table or list with source, interpreter, classification/check, command, result state, meaningful observation, and cleanup. State explicitly what was not proven: teaching quality, translation naturalness, security isolation, unexecuted toolchains, or broad platform compatibility.
