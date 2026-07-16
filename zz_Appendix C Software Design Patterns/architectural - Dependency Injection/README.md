# Architectural · Dependency Injection

## Pattern card

| Field | Value |
|---|---|
| Family | Architectural technique |
| Status | Executable |
| Route | Advanced |
| Prerequisites | Callables, composition, exceptions, Professional checkpoint |
| Time | 35–45 minutes |

You will make identifiers, time, output, and execution controllable without a
framework or global monkey-patching.

## Start with the pressure

An application that creates its own random identifier, reads the real clock,
prints directly, and constructs its executor is difficult to predict. A test
must either accept unstable output or reach inside global state. The business
operation also becomes the owner of infrastructure lifetime by accident.

The pressure is uncontrollable collaboration. **Dependency injection** is the
small technique that supplies those collaborators from outside.

## The technique in plain language

A dependency is something this object needs to do its work. Injection means
the caller provides it, usually through a constructor argument. In Python a
dependency can be a function, bound method, or small object. The example uses
plain callables; it needs no container and no advanced type machinery.

The simpler alternative is direct construction inside `main` when the
dependency is deterministic, has no meaningful replacement, and has one clear
owner.

### Use it, avoid it, count its cost

- Use it for nondeterministic or external boundaries such as time, IDs, output,
  storage, and execution.
- Avoid injecting every pure helper or passing a dictionary of unnamed
  services through the whole program.
- Its cost is a larger construction signature and an explicit wiring decision.
- Remove an injection point when the variation disappears and direct ownership
  is clearer.

## Predict, run, observe

Predict the exact output timestamp and identifier. Then predict when the fake
ID source would become exhausted.

Run the verified companion from the repository root:

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B "zz_Appendix C Software Design Patterns/architectural - Dependency Injection/example.py"
```

Expected output:

```text illustrative
completed:job-1:pack books
output:12:00|job-1|completed:job-1:pack books
boundary:new_id must be callable
recovered:completed:job-2:pack pens
```

The [dependency-injection companion](example.py) validates collaborators once
at construction. `submit` then owns a visible order: validate, obtain an ID,
execute, read time, and write output.

## Normal, boundary, and recoverable behavior

- **Normal:** injected fakes produce stable output without reading host time or
  external state.
- **Boundary:** a non-callable dependency is rejected before a job begins; an
  empty payload is rejected before consuming an ID.
- **Recoverable:** construct a new application with a corrected collaborator
  and start a new operation. Do not mutate a half-configured object in place.

Common mistakes are hiding dependencies in module globals, injecting an
unstructured “service locator,” or using injection while still reading the real
clock inside the method.

## Guided exercise

Inject an executor that raises `RuntimeError("planned")`. Verify that no output
message is written for that failed call, then construct an application with a
healthy executor and complete a new job.

**Hint:** pass a short named function instead of adding a testing flag to
`JobApplication`.

**Success criterion:** the failure remains visible, output has no false success,
and recovery changes only construction code.

## Explained solution and decision record

The application should not catch an execution failure merely because the
dependency was injected. Injection changes ownership and replaceability, not
the failure policy. A failing function makes the negative path deterministic;
a second construction proves recovery without globals.

```text illustrative
problem → tests cannot control IDs, time, output, or execution
forces → deterministic evidence and explicit collaborator ownership
simplest option → direct construction for stable, single-owner helpers
chosen technique → constructor injection for volatile boundaries
cost → more explicit parameters and wiring
expected failure → hidden real dependency makes output unstable
verification → fixed normal, invalid dependency, failure, and recovery cases
when to remove it → a collaborator becomes pure, fixed, and directly owned
```

## Checkpoint and navigation

Continue when you can name which dependencies deserve a seam, which do not,
and why dependency injection is possible without a framework.

[Return to the Appendix C family catalogue](../README.md#family-index) ·
[Continue the Advanced ownership route](../README.md#advanced-route-make-ownership-explicit)
