## Why

The Linux quality runner can spend its full graceful `SIGTERM` window after it
has already detected a detached surviving descendant. A descendant that ignores
`SIGTERM` can therefore win a scheduler-dependent race and write into the
checkout before the later `SIGKILL`, contradicting the archived cleanup
contract and making its delayed-writer regression flaky.

## What Changes

- Freeze every currently observed owned process as soon as a surviving
  descendant or another infrastructure failure requires cleanup, then rescan
  the owned tree and terminate/reap it within the existing outer bound.
- Treat an observed descendant after direct-child exit as an immediate
  infrastructure error instead of allowing it to run through the quiescence
  window.
- Replace the wall-clock delayed-writer fixture with a deterministic
  ready/PID/release handshake that proves the detached PID is gone before the
  runner returns and cannot perform a post-return write.
- Stress the focused containment regression, rerun the complete tooling suite,
  and preserve all result, redaction, platform, and human-review boundaries.
- Make no CLI, matrix schema, report schema, platform-support, content, parity,
  provenance, or publication-status change.

### Goals

- Close the observed freeze/kill race without broadening the executor's trust
  claim beyond Linux subreaper plus `/proc` evidence.
- Make the regression deterministic under ordinary scheduler contention.
- Keep failures fail-closed and preserve the distinction between infrastructure
  errors and the active human provenance gate.

### Non-goals

- This is not a hostile-code sandbox and does not promise to prevent a child
  from writing while its selected check is legitimately running.
- It does not add Windows or macOS containment, relax time/output bounds, or
  resolve any human linguistic, accessibility, pedagogical, or provenance task.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deterministic-quality-evidence`: Require freeze-first cleanup once an owned
  detached descendant is observed, immediate fail-closed transition after the
  direct process exits, and deterministic proof that no owned PID survives the
  reported result.

## Impact

- **Affected code:** `tools/run_quality.py` and focused regressions in
  `tools/tests/test_run_quality.py`.
- **Affected specification:** a delta for the archived/main
  `deterministic-quality-evidence` capability.
- **Active-change coordination:** `add-book-quality-gates` continues to own the
  generic gate/provenance diagnostics and `restore-multilingual-content-parity`
  continues to own human parity acceptance; neither task state is changed.
- **Compatibility:** no public CLI, config, adapter, report, check ID, exit-code,
  or supported-platform contract changes.
- **Risks:** stopping the wrong process or missing a fork between observation
  and signaling. Cleanup remains restricted to the direct child, recursively
  observed descendants, and newly adopted children outside the pre-launch
  baseline; repeated observation closes the fork window and any lost
  observability still fails closed.
- **Migration:** none; the next runner invocation uses the tightened cleanup.
- **Rollback:** revert the production and regression bundle together; do not
  retain the timing-dependent fixture as evidence of reliable containment.
- **Definition of done:** the focused handshake regression passes repeatedly in
  isolation and under bounded concurrent load; all 136+ tooling tests pass from
  a clean checkout; the normal parity and OpenSpec gates validate; the generic
  gate still reports exactly its independently owned provenance blockers; no
  process, cache, or generated artifact remains; strict OpenSpec and whitespace
  checks pass.
