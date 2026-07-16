# Structural · Proxy

## Pattern card

| Field | Value |
|---|---|
| Family | Structural |
| Status | Decision-card; the code is a verified contrast, not required architecture |
| Route | Professional |
| Prerequisites | Functions, composition, exceptions, Essential checkpoint |
| Time | 20–30 minutes |

You will decide whether an access check deserves an object with the same
interface as the real reader, or whether one direct guard is clearer.

## Start with the pressure

Callers can read a document, but access must be checked before delegation.
When many callers must use the same interface and policy boundary, repeating
the check can drift. With one call site, however, an extra object may only hide
the rule.

The pressure is controlled access while preserving the real object's
interface. That is the reason to consider **Proxy**, not the mere presence of a
wrapper class.

## The pattern in plain language

A Proxy stands in for another object. It offers the same operation, performs a
control such as authorization or lazy access, and delegates only when allowed.
Unlike an Adapter, it does not translate to a different interface. Unlike the
Decorator in this appendix, its central purpose here is access control.

The simpler Python option is the `read_with_guard` function in the companion.
Prefer it while one visible call site owns the decision.

### Use it, avoid it, count its cost

- Consider it when several callers already depend on the same interface and
  must not bypass one access boundary.
- Avoid it when a direct conditional is obvious or when it creates the false
  impression that this toy check is production authorization.
- Its cost is hidden delegation, policy configuration, and interface-parity
  tests.
- Remove it when access control moves to one genuine outer boundary or only
  one direct call remains.

## Predict, run, observe

Predict whether `DocumentReader.read` runs for `guest`, and whether the caller
must change method names when switching between real reader and Proxy.

Run the verified contrast:

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B "zz_Appendix C Software Design Patterns/structural - Proxy/example.py"
```

Expected output:

```text illustrative
direct:safe local content
proxy:safe local content
direct-invalid:invalid_actor
direct-denied:access_denied
proxy-invalid:invalid_actor
proxy-denied:access_denied
missing:document_not_found
recovered:safe local content
```

The [Proxy decision-card source](example.py) deliberately includes both the
direct guard and `ReadProxy` in the executed contrast. Both call the same
boundary function, so invalid and denied actors have the same stable codes. It
uses invented identities and local data; it is not a security system.

## Normal, boundary, and recoverable behavior

- **Normal:** both the direct function and Proxy let `learner` receive the real
  reader's value.
- **Boundary:** both routes report `invalid_actor` for empty input and
  `access_denied` for `guest`, before delegation. The real reader translates a
  missing document to the stable `document_not_found` error.
- **Recoverable:** the caller supplies an allowed identity and repeats a new
  read; denial never mutates the document store.

Common mistakes are changing the method signature, placing business policy in
the real object and the Proxy at once, or treating a local allow-list example
as sufficient authentication.

## Guided decision exercise

Choose between `read_with_guard` and `ReadProxy` for (a) one command-line call
site and (b) four clients that already receive interchangeable readers.

**Hint:** count bypass opportunities and interface consumers, not lines of
code. Do not award the pattern points merely because it has a class name.

**Success criterion:** each choice states its pressure, cost, verification, and
removal condition; the one-call-site case remains simple.

## Explained solution and decision record

For one command-line call, the direct function keeps the guard visible. For
several interchangeable clients, a Proxy can centralize the boundary without
changing their `read(document_id, actor)` call. Both choices still require real
security design outside this teaching fake.

```text illustrative
problem → several clients might bypass the same access check
forces → preserve one reader interface and deny before delegation
simplest option → one direct guard function
chosen pattern → Proxy only when multiple interface consumers justify it
cost → hidden delegation and parity/security tests
expected failure → unauthorized work reaches the real reader
verification → allowed, denied, invalid-actor, and missing-document checks
when to remove it → one outer boundary owns all reads
```

## Checkpoint and navigation

You pass this card when you can contrast Proxy with Adapter and Decorator and
can defend the direct guard for the smaller case.

[Return to the Appendix C family catalogue](../README.md#family-index) ·
[Review the Professional decision cards](../README.md#professional-decision-cards)
