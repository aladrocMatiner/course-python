# Architectural · Execution Port

## Pattern card

| Field | Value |
|---|---|
| Family | Architectural boundary |
| Status | Executable |
| Route | Advanced |
| Prerequisites | Composition, exceptions, Adapter, dependency injection |
| Time | 35–45 minutes |

You will define the smallest application-facing execution behavior and verify
that good, malformed, and temporarily unavailable implementations remain
visible at the boundary.

## Start with the pressure

The application needs to execute a job, but local, legacy, and remote
mechanisms have different details. If use-case code imports those details, a
change in transport or library changes the application policy too.

The pressure is dependency direction across a volatile boundary. An
**execution port** names what the application needs: an object with
`execute(job_id, payload)` that returns the application's `Result`.

## The boundary in plain language

A port is a small application-owned contract. An Adapter on the outside makes
a concrete mechanism satisfy it. Python's ordinary method behavior is enough
for this lesson; the application checks the operation at construction and the
result at runtime. `typing.Protocol` is a later optional tool, not a prerequisite.

The simpler alternative is an injected function. Prefer it when one operation
and no collaborator state make an object unnecessary.

### Use it, avoid it, count its cost

- Use it when application policy must remain stable across genuinely different
  execution mechanisms.
- Avoid a broad port that mirrors every method of an external library.
- Its cost is contract documentation, boundary validation, and one Adapter per
  mechanism.
- Remove it when only one stable, direct mechanism remains and the seam adds no
  useful test or ownership boundary.

## Predict, run, observe

Predict which layer rejects the dictionary from `BrokenAdapter`, and whether a
temporarily unavailable dependency should be reported as a completed result.

Run the verified companion:

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B "zz_Appendix C Software Design Patterns/architectural - Execution Port/example.py"
```

Expected output:

```text illustrative
job-1:completed
boundary:execution port returned an invalid result
recoverable:dependency is temporarily unavailable
fallback:job-3:completed
```

The [execution-port companion](example.py) keeps the port narrow. The
application validates identity and result type; each Adapter owns mechanism
details and failure reporting.

## Normal, boundary, and recoverable behavior

- **Normal:** `LocalExecutionAdapter` returns the `Result` for the requested
  identifier.
- **Boundary:** a dictionary that merely looks plausible is rejected, as is a
  `Result` for a different job.
- **Recoverable:** unavailability remains an explicit exception. This fake
  fails before accepting work, so the caller can use a documented local
  fallback. For a real dependency with an unknown outcome, fall back only when
  the operation is proven retry-safe or idempotent; otherwise surface the
  uncertainty. The port never invents success.

Common mistakes are designing the port from the external library inward,
returning `None` for every failure, or placing retries and transport parsing in
application policy without an owned boundary.

## Guided exercise

Add a fake Adapter that returns a `Result` with the wrong job identifier. Prove
that `JobApplication` rejects it before the caller receives a summary.

**Hint:** the existing result check has two independent conditions. Your test
should identify which contract invariant the fake violates.

**Success criterion:** normal execution remains green, wrong identity fails
closed, unavailability remains distinguishable, and the local fallback still
works for a new operation.

## Explained solution and decision record

The fake should return `Result("other-job", "completed")`. The application,
not each caller, compares that identity with the requested job and raises
`BoundaryError`. This protects correlation without coupling application code
to a concrete transport.

```text illustrative
problem → execution mechanisms leak into application policy
forces → stable dependency direction and validated result identity
simplest option → inject one execution function
chosen boundary → execution port plus outside Adapters when mechanisms vary
cost → contract and Adapter verification
expected failure → malformed or mismatched result is accepted
verification → healthy, invalid-result, unavailable, and fallback checks
when to remove it → one stable direct mechanism owns the whole operation
```

## Checkpoint and navigation

Continue when you can distinguish the application-owned port from its external
Adapters and keep the contract smaller than any concrete library API.

[Return to the Appendix C family catalogue](../README.md#family-index) ·
[Revisit the structural Adapter](<../structural - Adapter/README.md>) ·
[Continue the Advanced ownership route](../README.md#advanced-route-make-ownership-explicit)
