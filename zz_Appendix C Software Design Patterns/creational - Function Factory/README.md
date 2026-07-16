# Function Factory

| Field | Value |
|---|---|
| Family | Creational |
| Status | Executable pattern |
| Route | Essential |
| Prerequisites | Functions as values, dictionaries, exceptions, modules |
| Estimated time | 25–35 minutes |

## Start with the pressure

Two callers must select the same executor by a configuration name. Each caller
currently repeats a conditional and may forget to reject an unknown name before
doing work. The pressure is **centralized, validated construction**. It is not
“we should use a Factory.”

## The basic idea

A function Factory is an ordinary function that validates a selection and
constructs a product. Here every valid call creates a new `PayloadExecutor`
whose transformation is a small closure. There is no need for a class hierarchy
merely to choose how that product is configured.

Start with a direct constructor or a small mapping. Add the Factory when several
callers need the same names, validation, or construction policy.

## Simpler option, fit, and cost

- **Simpler option:** call one constructor directly, or look up a callable in a
  local dictionary.
- **Use it when:** selection names form a shared boundary and invalid choices
  must fail consistently.
- **Do not use it when:** there is one implementation or one local caller.
- **Cost:** another name to learn, an indirect call, and a registry that must be
  kept honest.

## Predict, run, observe

Before running, predict which line proves that validation happens before an
executor is returned. Then run the import-safe companion from the repository
root:

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  'zz_Appendix C Software Design Patterns/creational - Function Factory/example.py'
```

Meaningful output:

```text illustrative
fresh-product=True
normal=mixed
variation=MIXED
name-boundary=executor name must be non-empty text
boundary=unknown executor: missing
recovery=safe
```

The identity check proves that two constructions do not share one product. The
two name boundaries distinguish an invalid name type from valid text that is
not registered. Recovery uses a known selection without repairing hidden global
state.

## Normal, boundary, and recoverable behavior

- Normal: `direct` constructs a fresh product that preserves the payload.
- Boundary: non-text or empty input raises `InvalidExecutorName`; `missing`
  raises `UnknownExecutor`, chained from the failed lookup.
- Recovery: choose a supported name and retry construction; no partial object
  was published.

A common mistake is to silently fall back to a default. That hides configuration
errors. Another is to return one mutable process-global object; construction
choice and lifetime ownership are different decisions.

## Guided exercise

Add a `lowercase` selection. First write the failing observation you expect,
then add the smallest builder entry.

**Hint:** add one builder that constructs `PayloadExecutor` with a lowercase
closure; do not add a product subclass.

**Success criterion:** `build_executor("lowercase").execute("MiXeD")` returns
`mixed`, two constructions have different identities, and an unknown name still
raises `UnknownExecutor`.

## Explained solution and decision record

The solution changes only the registry because selection and execution already
have separate responsibilities. The Factory remains useful while several
callers share validated names. If the program returns to one fixed executor,
replace it with a direct reference.

```text illustrative
repeated validated selection → shared names and consistent failure
→ direct constructor or mapping → function Factory
→ cost: indirection and registry maintenance
→ verify valid, unknown, and recovery cases
→ remove when only one fixed construction path remains
```

## Checkpoint and navigation

Can you explain why the Factory constructs a collaborator instead of executing
the job? Can you prove two calls create separate products and reject an invalid
selection without partial state? If so, the checkpoint is complete.

[Return to the Appendix C catalogue](../README.md#family-index) ·
[Continue the Essential route](../README.md#essential-route-earn-the-first-three-seams)
