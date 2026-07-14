## Context

`tools/run_quality.py` supports execution only on Linux hosts where it can act
as a child subreaper and continuously reconstruct ownership from `/proc`. Once
the direct child exits, the monitor currently waits up to 150 ms for
quiescence. If a detached descendant remains, cleanup then allows a 500 ms
`SIGTERM` window before `SIGKILL`. The regression's writer wakes after 800 ms,
so scheduler jitter can let the write occur during cleanup. This reproduced in
an isolated loop as well as under a parallel clean-checkout matrix.

The runner is trusted-code fail-detection, not a hostile-code sandbox. It must
still meet the narrower published contract: after it observes an owned
descendant and reports an infrastructure error, that tree is terminated and
reaped without a delayed post-result repository write. Generic book findings,
domain checks, OpenSpec validation, and human review gates remain separate.

## Goals / Non-Goals

**Goals:**

- Stop observed owned processes before giving them another cleanup window.
- Detect an already observed post-parent descendant immediately.
- Close forks between observation and signaling through bounded repeated
  ownership scans.
- Prove cleanup with a deterministic process handshake rather than a sleep
  chosen near the implementation's timing budget.
- Preserve exit codes, result schemas, redaction, resource bounds, source
  snapshots, and unsupported-platform behavior.

**Non-Goals:**

- Prevent arbitrary writes while a selected trusted check is legitimately
  running or claim an OS security sandbox.
- Add a portable non-Linux fallback, cgroups, namespaces, privileges, or an
  external dependency.
- Change course content, localization evidence, provenance decisions, or any
  active human-review task.

## Decisions

### Fail immediately when an owned process survives the direct child

After `process.poll()` first reports direct-child exit, a non-empty owned set
is sufficient evidence of a surviving descendant. The monitor reports the
existing infrastructure error immediately. The short no-owned/output-EOF
quiescence window remains so `/proc` adoption and pipe closure cannot produce a
false pass.

Allowing a known descendant to run for the remainder of the 150 ms window was
rejected: it does not add evidence and increases the mutation window. Treating
only process-group members as owned remains rejected because `setsid()` escapes
that boundary.

### Freeze, rescan, then terminate and reap

Infrastructure cleanup repeatedly resolves the direct child, recursively
observed descendants, and children newly adopted by the subreaper outside the
pre-launch baseline. It sends `SIGSTOP` to the current owned set before another
scan. Once the stopped set is stable, it sends termination signals without
resuming an ignored handler, then continues freeze/kill/reap scans until three
empty rounds or the existing bounded cleanup deadline.

This order closes the ordinary fork race: a process that forks between a scan
and `SIGSTOP` is found on the next scan, while its stopped parent cannot fork
again. If `/proc` becomes unreliable, the existing fallback stops and kills
only previously observed PIDs and reports that unobserved cleanup cannot be
proved. Permission failures or non-convergence remain infrastructure errors.

Keeping a 500 ms graceful running window was rejected because a handler can
ignore `SIGTERM` and mutate during that interval. Merely shortening the sleep
or extending the fixture delay was rejected because both retain a
scheduler-dependent race.

### Use a ready/PID/release regression

The detached fixture writes a bounded ready file containing its PID, installs
a `SIGTERM` handler that exposes a graceful cleanup window by writing the
forbidden marker, and waits for a release marker. The direct child
does not exit until readiness exists. After `run_child` returns, the test proves
the PID is no longer live, creates the release marker, and confirms that no late
write appears. Focused repeated runs and a bounded parallel-load run exercise
the same contract.

A fixed `sleep(0.8)` was rejected because it tests relative scheduler timing,
not the post-result liveness invariant. The handshake files live only in the
test's temporary directory and are removed by its existing cleanup.

### Keep verification ownership unchanged

The tooling suite owns runner mechanics. The normal generic validator may
remain exit 1 because `add-book-quality-gates` deliberately exposes unresolved
human provenance entries; that result is not converted to a runner failure or
waiver. `restore-multilingual-content-parity` remains the owner of human parity
acceptance. No learner-facing Markdown or parity digest changes.

## Risks / Trade-offs

- **A stopped process is terminated less gracefully after infrastructure
  failure** → cleanup already represents incomplete/unsafe evidence; preserving
  the checkout and preventing a late descendant takes priority, and normal
  successful checks are untouched.
- **A fork occurs during the first observation/signal pass** → stop parents,
  rescan the recursive/adopted tree to stability, and keep post-kill scans
  bounded and fail-closed.
- **A PID exits or is reaped during cleanup** → existing `ProcessLookupError`,
  `waitpid(WNOHANG)`, ownership, and stable-empty handling remain idempotent.
- **A PID cannot be observed or signaled** → retain known PIDs, report lost
  observability/non-convergence, and never return pass.
- **The new test passes with a merely stopped survivor** → record the PID and
  assert it is no longer live before releasing the writer.

## Migration Plan

1. Add the deterministic regression and confirm it fails or flakes against the
   previous cleanup under repeated execution.
2. Implement immediate descendant failure and freeze-first bounded cleanup.
3. Run the focused test repeatedly, the runner module, all tooling tests, the
   clean-checkout matrix, strict OpenSpec, doctor, whitespace, and hygiene.
4. Sync and archive this delta only after all tasks and verification pass.

Rollback reverts the implementation and regression together. The CLI and data
formats require no migration.

## Open Questions

None. Stronger hostile-code containment or non-Linux execution would require a
separate capability and provisioned host evidence.
