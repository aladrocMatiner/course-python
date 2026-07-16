# Architectural · Composition Root

## Pattern card

| Field | Value |
|---|---|
| Family | Architectural technique |
| Status | Executable |
| Route | Advanced |
| Prerequisites | Composition, constructor injection, module entry points |
| Time | 30–40 minutes |

You will place concrete construction in one outer function so that the
application logic receives collaborators but does not choose them.

## Start with the pressure

Dependency injection can still become confusing when every module constructs a
different executor, ID source, or output target. Ownership is scattered, tests
do not know which graph they received, and cleanup has no obvious home.

The pressure is dispersed wiring. A **composition root** is the one outer place
where concrete collaborators are selected, constructed, and connected.

## The technique in plain language

`build_application(write)` is the composition root in the companion. It knows
about `SequentialIds`, `DirectExecutor`, and `JobApplication`. The application
knows only the collaborators it receives. This is a location and ownership
rule, not a framework.

The simpler option is constructing two or three objects directly in a short
`main` function. That `main` can itself be the composition root; no separate
builder is required.

### Use it, avoid it, count its cost

- Use it when wiring starts to repeat or when resources need one lifetime owner.
- Avoid turning it into a service locator that application code consults while
  running.
- Its cost is one explicit bootstrap surface and configuration checks.
- Remove the helper function when a tiny `main` expresses the complete graph
  more clearly.

## Predict, run, observe

Predict which object owns the next identifier and whether the invalid payload
consumes one.

Run the verified companion:

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B "zz_Appendix C Software Design Patterns/architectural - Composition Root/example.py"
```

Expected output:

```text illustrative
completed:job-1:pack books
owned-output:['completed:job-1:pack books']
boundary:payload must be non-empty text
recovered:completed:job-2:pack pens
```

Read the [composition-root companion](example.py). Construction happens in
`build_application`; the invalid input fails inside `submit` before the owned
ID source advances.

## Normal, boundary, and recoverable behavior

- **Normal:** one root builds one coherent object graph and returns the entry
  application.
- **Boundary:** a non-callable output is rejected during construction; invalid
  job data is rejected before stateful collaborators are consumed.
- **Recoverable:** correct the input and continue with the same healthy graph,
  or discard a failed construction and build a fresh graph.

Common mistakes are importing the root from domain modules, keeping a global
container, or constructing a second hidden executor inside `submit`.

## Guided exercise

Create a second root named `build_test_application` that accepts an ID source
and executor explicitly but still returns `JobApplication`. Do not add a
`testing=True` branch to production logic.

**Hint:** roots may differ in concrete choices while the application contract
stays identical.

**Success criterion:** both roots create a usable application, all concrete
choices remain outside `submit`, and the test root produces stable output.

## Explained solution and decision record

The test root can receive or construct deterministic fakes and pass them into
the same `JobApplication` constructor. The application needs no environment
check because composition, not business logic, owns the choice.

```text illustrative
problem → concrete wiring and lifetime ownership are scattered
forces → one inspectable graph; application code must not choose infrastructure
simplest option → construct the small graph directly in main
chosen technique → one composition root when wiring repeats
cost → an explicit bootstrap API and configuration validation
expected failure → hidden construction bypasses injected collaborators
verification → production-like and deterministic test graph checks
when to remove it → a short main expresses the whole graph more clearly
```

## Checkpoint and navigation

Continue when you can mark the single construction boundary and prove that no
application method constructs its own infrastructure collaborator.

[Return to the Appendix C family catalogue](../README.md#family-index) ·
[Continue the Advanced ownership route](../README.md#advanced-route-make-ownership-explicit)
