## 1. Deterministic regression

- [x] 1.1 Replace the timing-dependent detached-writer fixture with a ready/PID/release handshake.
  - **Objective:** Test post-result liveness and write prevention without relying on scheduler timing near the cleanup deadline.
  - **Deliverables:** Updated focused regression in `tools/tests/test_run_quality.py` that waits for child readiness, records its PID, releases only after `run_child` returns, and checks PID death plus absence of the late write.
  - **Validation:** The fixture observes a real `setsid()` descendant whose `SIGTERM` handler exposes a graceful running window; it cannot pass with a merely stopped live PID and cleans only its temporary directory.
  - **Risk:** A handshake that never becomes ready could hang; every wait must have a short monotonic deadline and fail with a precise assertion.
  - **Scope:** S.

## 2. Freeze-first containment

- [x] 2.1 Fail immediately when an owned descendant is observed after direct-child exit.
  - **Objective:** Remove the unnecessary running interval before infrastructure cleanup starts.
  - **Deliverables:** Monitor transition in `tools/run_quality.py` that preserves the no-owned adoption/EOF quiescence check while treating a non-empty owned set as the existing surviving-descendant error.
  - **Validation:** Success, ordinary exit-1, crash, timeout, overflow, and detached-child outcomes retain their documented result/exit semantics.
  - **Scope:** S.

- [x] 2.2 Freeze, rescan, terminate, and reap the observed owned tree within the existing bound.
  - **Objective:** Prevent an already observed descendant that ignores `SIGTERM` from running through a graceful cleanup window.
  - **Deliverables:** Bounded stop-first ownership stabilization and post-kill reaping in `_terminate_owned_tree`, reusing the existing lost-observability fallback and baseline-child ownership rules.
  - **Validation:** Recursive/adopted descendants are stopped before termination; new observed forks are included; permission, `/proc`, or convergence failures remain explicit infrastructure errors; no CLI/schema/report change.
  - **Risk:** Abrupt failure cleanup is less graceful; apply it only after infrastructure evidence is already invalid and never to a successful check.
  - **Scope:** M.

## 3. Verification and closure

- [ ] 3.1 Stress the focused contract and run the complete quality-tooling matrix from a clean checkout.
  - **Objective:** Prove the race is closed without regressing other process, output, snapshot, plugin, parity, or report behavior.
  - **Deliverables:** Repeated isolated handshake runs, a bounded concurrent-load run, runner-module tests, full tools discovery, curriculum/parity checks, generic/plugin evidence, and artifact/status inspection.
  - **Validation:** All 137+ tooling tests pass repeatedly; domain check IDs remain positive; the generic aggregate retains exactly its independently owned provenance warnings; no late writer, process, cache, or source mutation remains.
  - **Scope:** M.

- [ ] 3.2 Validate the OpenSpec correction and prepare it for truthful archival.
  - **Objective:** Keep the delta, implementation evidence, and archive handoff coherent without marking the workflow action itself complete in advance.
  - **Deliverables:** Strict change/all validation, doctor, whitespace check, completed implementation tasks, and an archive-ready `deterministic-quality-evidence` delta.
  - **Validation:** OpenSpec strict/doctor pass; archival can sync only this change while `add-book-quality-gates` and `restore-multilingual-content-parity` remain active with all human tasks unchanged.
  - **Scope:** S.
