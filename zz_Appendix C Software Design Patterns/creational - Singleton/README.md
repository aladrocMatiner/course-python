# Singleton

| Field | Value |
|---|---|
| Family | Creational |
| Status | Decision card with verified contrast |
| Route | Professional |
| Prerequisites | Object identity, modules, mutable state, tests |
| Estimated time | 25–35 minutes |

## Start with the pressure

Someone says, “there must be exactly one registry.” First ask what truly needs
one owner and for how long. A process-wide hidden instance is only one possible
lifetime. Explicit ownership in `main()` or a composition root often satisfies
the same requirement while keeping tests isolated.

## The basic idea

A Singleton makes one class instance globally reachable and prevents ordinary
construction of additional instances. Python modules already provide one
imported namespace per interpreter, but module state is still global state.
Neither mechanism explains who resets mutable data or how two tests stay
independent.

The companion intentionally demonstrates the sharing hazard, then recovers
with an explicitly constructed `Registry`. Its `module_owned_registry()` helper
is only a **singleton-like module accessor**: callers can still construct other
registries, so it does not enforce the “exactly one instance” invariant. This
card does not recommend adding a Singleton to the course project.

## Simpler option, fit, and cost

- **Simpler option:** construct one object in `main()` and pass it to users; for
  immutable constants, use a module constant.
- **Use it when:** identity must be process-wide, that invariant is enforced at
  the boundary, and explicit ownership cannot express it more safely.
- **Do not use it when:** “convenient access” is the real reason.
- **Cost:** hidden dependencies, shared mutable state, order-dependent tests,
  and unclear cleanup.

## Predict, run, observe

Predict which registry sees `job-b` and why the new explicit registry does not
inherit it. Run:

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  'zz_Appendix C Software Design Patterns/creational - Singleton/example.py'
```

```text illustrative
explicit-isolated=True
module-accessor-shared=True
boundary=duplicate name: job-b
recovery-explicit-owner=True
```

## Normal, boundary, and recoverable behavior

- Normal: two explicitly constructed registries do not share names.
- Boundary: two callers of `module_owned_registry()` receive the same mutable
  object, so a duplicate appears across caller boundaries. That shared accessor
  is a warning, not proof of an enforced Singleton.
- Recovery: create and pass a registry with a clear owner and lifetime.

Do not “fix” a flaky test by adding a public `reset_singleton()` hook. That
makes the hidden lifetime more complicated. Prefer removing the hidden owner.

## Guided exercise

Rewrite the imagined API `save_job(job)` so the registry is supplied by the
caller. Sketch only the function signature and one test arrangement.

**Hint:** `save_job(job, registry)` makes the dependency visible. Each test can
construct its own `Registry`.

**Success criterion:** two tests can run in either order without resetting a
module global, and production can still construct exactly one owned registry.

## Explained solution and decision record

Explicit injection separates “production currently creates one” from “the
program is structurally forbidden to create two.” The former is usually the
real requirement and is easier to verify.

```text illustrative
one production owner proposed → lifetime and test isolation matter
→ construct once and pass explicitly → no Singleton
→ cost avoided: hidden state and reset protocol
→ verify independent objects plus production wiring
→ revisit only if process-wide identity becomes an enforced domain invariant
```

## Checkpoint and navigation

Can you state the owner, lifetime, cleanup point, and test-reset story for the
shared resource? If any answer is hidden, keep explicit construction.

[Return to the Appendix C catalogue](../README.md#family-index) ·
[Continue the Professional route](../README.md#professional-route-cross-cutting-behavior-and-notifications)
