# Implementation review: descendant cleanup hardening

Date: 2026-07-14
Change: `harden-quality-runner-descendant-cleanup`
State: implementation verified, main spec synchronized, and change archived

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

## Clean-checkout closure evidence

The committed implementation and atomic-handshake regression were verified
from a detached clean checkout at
`35783414b59fff2fb8ab605e48f1f8d7f216a90b`:

| Evidence | Result |
|---|---|
| Complete tooling discovery | 137/137 tests passed in 20.080 s |
| Atomic-handshake stress | 20/20 isolated and 40/40 across four workers passed; no failure, timeout, skip, process, or temporary residue |
| Curriculum and normal parity | 0 curriculum issues; valid 27-source/108-variant inventory |
| Generic validator | Exit 1 only for the exact five human provenance warnings listed above; no stale baseline or other diagnostic |
| Explicit domain plugins | All five expected network/C++/Rust check IDs produced positive evidence; each aggregate remained exit 1 only because of the same provenance warnings |
| Handoff profile | `tool-tests`, `curriculum`, `parity`, `openspec-strict`, and `whitespace` passed; the generic and three domain checks reported quality findings only |
| Runner infrastructure | No infrastructure error, timeout, blocked process, source mutation, or retained runner temporary |
| OpenSpec | Strict change and all-item validation passed 12/12; doctor reported a healthy root |
| Checkout hygiene | `git status --porcelain` empty, `git diff --check` passed, and no cache or generated artifact remained |

The handoff exit was 1, not 2: it truthfully preserved the independent human
provenance gate and produced no runner infrastructure failure. The two other
active changes remain unchanged at 21/24 and 4/50 completed tasks.

## Residual engineering boundary

Ownership is still represented by Linux PIDs reconstructed from `/proc` during
the runner's short bounded cleanup interval. An independently pinned process
identity, such as PID plus start time or a retained pidfd, could further harden
against an extreme PID-reuse event. No such event reproduced, this risk
predates the corrected graceful-running window, and trusted repository checks
remain the stated execution model. Stronger process-identity or hostile-code
containment therefore requires a separate proposal rather than an unsupported
claim in this change.

## Archive result

Tasks 3.1 and 3.2 had the required clean evidence before archival. The OpenSpec
workflow synchronized only `deterministic-quality-evidence` and archived this
change as `2026-07-14-harden-quality-runner-descendant-cleanup`. Post-archive
strict validation passed all 11 remaining items and doctor remained healthy.
`add-book-quality-gates` and `restore-multilingual-content-parity` remain active
with their human tasks untouched.
