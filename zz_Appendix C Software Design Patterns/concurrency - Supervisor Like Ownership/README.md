# Supervisor-like ownership — comparison only

Canonical English lesson. Localized editions are not part of this implementation slice.

## At a glance

| Field | Contract |
|---|---|
| Family | Concurrency ownership comparison |
| Status | Cross-link and comparison only; no Supervisor implementation claim |
| Route | Network Crosswalk, after the `TaskGroup` ownership reading |
| Prerequisites | [Structured-concurrency cross-link](<../concurrency - Structured Concurrency with TaskGroup/README.md>) and Chapter 21 cleanup |
| Time | 20–30 minutes |
| Runtime | Read-only standard-library AST trace; authoring run on CPython 3.13.11 |
| Owner | [`chapter-21-async/structured_async.py`](../../chapter-21-async/structured_async.py) and its tests |
| Local companion | [`example.py`](example.py), import-safe and offline |

This lesson uses “Supervisor-like” only to compare responsibilities. Python's
Chapter 21 source owns `TaskGroup` lifetime, sibling cancellation, propagation,
and cleanup. It does **not** implement, name, or test a restart Supervisor.

## Pressure before the comparison

After learning structured concurrency, it is tempting to assume that an owner
also restarts failed children. That is a different policy. `TaskGroup` defines
a lifetime and failure boundary: one non-cancellation child failure cancels
unfinished siblings and is reported after cleanup. It does not decide whether
a child should restart, how often, with what backoff, or when repeated failure
should stop the application.

A **Supervisor-like comparison** asks which additional responsibilities a
restart owner would need. It is not evidence that such an owner exists. The
minimum questions are: which failures are eligible, what state is recreated,
how attempts and time are bounded, whether siblings restart, and how shutdown
overrides restart.

## The simplest option first

Use one `TaskGroup` and let failure propagate when the caller can decide what
happens next. Use a process/service manager when whole-process restart is the
actual operational policy. Often the correct answer is no restart at all:
clean up, report the cause, and let an outer owner choose.

### Consider an explicit restart owner only when

- a long-lived service has a defined recoverable child failure;
- recreated state and duplicate-effect safety are understood;
- restart count, backoff, total deadline, and shutdown precedence are bounded;
  and
- tests can prove that repeated failure stops rather than loops forever.

### Do not add one when

- ordinary propagation is sufficient;
- failure may indicate corrupted shared state;
- restart could duplicate an effect;
- a platform service manager already owns the policy; or
- “keep it alive” is the only stated requirement.

The cost is another state machine, attempt/deadline policy, recreated-resource
ownership, diagnostic history bounds, and shutdown races. Remove a custom
restart layer when failure should propagate or an external owner already has
the responsibility.

## Predict, trace, observe

Before running, predict whether Chapter 21 contains:

- `TaskGroup` scopes;
- child cleanup in `finally`; and
- any `restart`, `supervisor`, or restart-`backoff` policy signal.

Run `python -I -B "zz_Appendix C Software Design Patterns/concurrency - Supervisor Like Ownership/example.py"`
from the repository root. The companion parses the owner without importing or
executing it. It reports the three owned scopes and `worker` cleanup, then
prints `restart_policy=absent` and the comparison-only boundary.

Absence in this trace is intentionally narrow: the inspected Chapter 21 source
does not contain that policy. It is not a claim about every Python library,
framework, operating system, or future chapter revision.

## Normal, boundary, and recoverable decisions

**Normal decision:** related children complete inside one `TaskGroup`; the
owner returns their results after group exit. No restart state is needed.

**Boundary:** a child raises `ValueError`. Chapter 21 cancels and cleans the
unfinished sibling, handles the declared leaf at the group boundary, and
returns its evidence. Nothing in that flow schedules a replacement child.
Calling it a Supervisor would invent behavior.

**Recoverable decision:** timeout or child failure cleans up and propagates to
an outer owner. That outer owner may perform a later independent operation, or
an external process manager may restart the whole service under its own finite
policy. The local `TaskGroup` still must not leave a child behind.

If the owner source is unavailable or invalid, the trace raises a stable
`SourceTraceError`. Restore the owner and rerun instead of copying an outdated
implementation into this directory.

Common mistakes are treating cancellation as restart, retrying unsafe child
effects, implementing an infinite restart loop, rebuilding resources without
closing old ones, and claiming Supervisor from a `TaskGroup` keyword alone.

## Guided exercise

Decision scenario: a local telemetry parser fails because an input frame is
malformed. Choose among (a) restart the same parser task, (b) close that peer
and let the bounded owner continue, or (c) restart the whole service.

**Hint:** ask whether parser state can be trusted, who owns the peer, whether
the input will change on restart, and which existing Chapter 23 recovery
already handles malformed framing.

**Observable success criterion:** your decision names the owner, chosen action,
finite boundary, cleanup, verification, and removal threshold. It must not add
a restart loop merely to make the task appear resilient.

### Explained solution

For Chapter 23's fatal malformed framing, close the affected peer after bounded
diagnosis and keep the hub's owned service loop alive. Restarting the parser on
the same unsafe bytes cannot repair framing and may repeat the failure forever.
Whole-service restart is also disproportionate while the hub remains healthy.
Chapter 23 already owns peer-close behavior, so this appendix adds no new
implementation.

Decision record:

> child failure raises a restart question → safety, recreated state, finite
> attempts, shutdown precedence → propagate after `TaskGroup` cleanup → no
> custom Supervisor for this case → caller handles one visible failure → hidden
> loop or duplicate effect → ownership/cleanup trace plus owner tests → revisit
> only when a measured recoverable long-lived-child policy appears

## Checkpoint and navigation

You pass this comparison checkpoint when you can:

- separate task lifetime from restart policy;
- identify the additional bounds a restart owner would require;
- choose propagation or an external owner without treating that as a failure;
  and
- label Chapter 21 evidence separately from this reading interpretation.

Previous: [structured concurrency with `TaskGroup`](<../concurrency - Structured Concurrency with TaskGroup/README.md>).
Next: [Reactor-like Chapter 23 trace](<../network - Reactor/README.md>).
Return to the owning [Chapter 21 lesson](../../chapter-21-async/README.md#cancellation-and-cleanup)
for executable failure and cleanup evidence.

Safe stop: let the cleaned failure propagate to a visible outer owner.
