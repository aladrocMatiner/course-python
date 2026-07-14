# Implementation review: descendant cleanup hardening

Date: 2026-07-14
Change: `harden-quality-runner-descendant-cleanup`
State: implementation complete; clean-checkout acceptance and archival pending

## Defect evidence

The previous delayed-writer test used a fixed 800 ms sleep. The production
cleanup could spend 150 ms waiting after direct-child exit and another 500 ms
offering `SIGTERM` before `SIGKILL`. Under scheduler contention, a detached
child that ignored `SIGTERM` could therefore write before cleanup completed.

The old implementation reproduced once in seven local focused runs, once in
30 isolated audit runs, and 10 times in 60 concurrent audit runs. Instrumented
runs observed the descendant PID; the defect was not missing adoption. The
problem was that the observed process remained runnable during the graceful
cleanup interval.

## Implemented correction

- A surviving owned descendant after direct-child exit now causes the existing
  infrastructure error immediately.
- Cleanup sends `SIGSTOP` to known owned PIDs before the next expensive process
  scan, repeatedly freezes newly discovered recursive or adopted descendants,
  and sends `SIGKILL` only after the frozen set stabilizes.
- Post-kill scans continue to stop and kill any newly observed target until
  three empty rounds or the bounded deadline. Lost observability retains the
  existing fail-closed known-PID fallback.
- The focused regression now uses a ready/PID/release handshake. Its detached
  child installs a `SIGTERM` handler that would write the forbidden marker, so
  a graceful running window fails deterministically. The test proves the PID
  is dead before release and then proves that no late write appears.
- A mocked fork-acquisition regression proves that a PID first seen on a later
  ownership scan receives `SIGSTOP` before the first `SIGKILL` and that cleanup
  does not deliver `SIGTERM`.

Normal successful checks are unchanged. The runner still describes bounded
trusted-repository execution on supported Linux subreaper/`/proc` hosts, not a
hostile-code sandbox.

## Working-tree verification

The following evidence passed against the implementation before the clean
checkout was created:

| Evidence | Result |
|---|---|
| Focused handshake, isolated audit | 30/30 passed |
| Focused handshake, four workers × 15 | 60/60 passed |
| Combined focused stress | 90/90 passed; no timeout, skip, residual process, or temporary directory |
| Runner module | 34 tests passed |
| Complete tooling discovery | 137 tests passed |
| Curriculum validator | 0 issues |
| Normal parity validator | Valid: 27 canonical units and 108 localized variants |
| Strict OpenSpec validation | All 12 current items passed |
| OpenSpec doctor | Healthy |
| Domain checks | `network:network-suite`, `cpp:boundaries`, `cpp:contract`, `rust:contract`, and `rust:distribution-boundary` passed |
| Hygiene | Whitespace and cache/artifact inspection passed |

The generic validator still reports exactly five unbaselined
`attribution.review_required` warnings, for `LICENSE`, the Chapter 3 canonical
lesson, the Chapter 23 certificate inventory, and the Chapter 24 and 25
canonical lessons. Those warnings belong to `add-book-quality-gates`; this
change neither suppresses nor resolves them. The seven-entry provenance
inventory and all linguistic, accessibility, bidi, pedagogical, and
publication decisions remain human review boundaries.

## Remaining closure evidence

Before archival, rerun the complete matrix from a clean checkout at the
committed implementation revision. The handoff profile must distinguish the
five expected provenance warnings from runner infrastructure failures, leave
the checkout unchanged, and preserve the two unrelated active changes with
their human tasks untouched. Record those results here, complete tasks 3.1 and
3.2, then let the OpenSpec archive workflow sync the delta into the main
capability.
