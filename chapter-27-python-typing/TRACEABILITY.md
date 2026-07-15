# Chapter 27 requirement traceability

This maintainer-facing record connects each learning objective to its canonical
teaching loop and executable evidence. It is not a replacement for the lesson
or for competent pedagogical, linguistic, accessibility, bidirectional,
provenance, or publication review.

## Objective-to-evidence map

- **O1 — Read and write annotations**
  - Teaching: `README.md`, “E1. Annotate a function you already understand”.
  - Practice/hint/solution: `total_units` TODO and explained solution.
  - Checkpoint: essential rubric items 1, 2, and 5.
  - Evidence: eligible canonical runnable blocks plus runtime companion import.
- **O2 — Model absence**
  - Teaching: “E2. Narrow `None` without losing a valid zero”.
  - Practice/hint/solution: `reorder_message` guided challenge.
  - Edge/recovery: `0` remains present; `None` follows a separate branch.
  - Evidence: runnable normal/zero/absence observations.
- **O3 — Validate a runtime boundary**
  - Teaching: “E3” and “E4”, followed by professional `parse_row` depth.
  - Practice/hint/solution: missing-quantity runtime-test modification.
  - Failure/recovery: wrong type, Boolean integer subclass, range rejection,
    corrected input, and non-mutation.
  - Evidence: `tests/test_typed_inventory.py`, `ParseRowTests` and
    `InventoryTests`.
- **O4 — Describe record shape**
  - Teaching: “P1. Give dictionary records a stable shape with `TypedDict`”.
  - Practice/hint/solution: missing-field test plus boundary explanation.
  - Checkpoint: professional rubric items 1, 5, and 6.
  - Evidence: `examples/typed_inventory.py`, `examples/checker_positive.py`,
    and expected `[typeddict-item]` in `checker_negative.py`.
- **O5 — Type behavior and reusable algorithms**
  - Teaching: P2 (`Callable`/`TypeVar`), P3 (`Protocol`), and P4 (`Self`).
  - Practice/hint/solution: `WarehousePrices` professional challenge.
  - Edge/recovery: one-shot iterator position, optional `0.0`, protocol method
    mismatch, rejected add, and subclass-preserving retry.
  - Evidence: `FirstMatchingTests`, `InventoryTests`, positive consumer, and
    corrected consumer.
- **O6 — Read static evidence honestly**
  - Teaching: optional A1–A3 route.
  - Practice/hint/solution: disposable correction of one negative fixture.
  - Failure/recovery: required negative categories `[arg-type]`,
    `[typeddict-item]`, and `[assignment]`, followed by corrected clean input.
  - Evidence: `tools/verify.py --checker` when the exact pin is provisioned.
- **O7 — Explain the evidence boundary**
  - Teaching: glossary flow, A3 verifier phases, and maintainer evidence section.
  - Practice/reflection: each route asks what its selected evidence did not prove.
  - Checkpoint: essential item 5, professional item 6, and all advanced items.
  - Evidence: separate runtime/checker status and explicit human-review gates.

## Canonical source contracts

- `examples/typed_inventory.py` owns `InventoryRow`, `PriceSource`,
  `parse_row`, `first_matching`, and `Inventory.add -> Self` behavior.
- `tests/test_typed_inventory.py` owns normal, inclusive-boundary, invalid,
  non-mutation, short-circuit, one-shot, copy, and subclass-identity evidence.
- `examples/checker_positive.py` owns the clean structural/generic/`Self`
  consumer.
- `examples/checker_negative.py` owns the expected non-zero static fixture; it
  is never part of the positive phase.
- `examples/checker_corrected.py` owns the recovery proof under the same strict
  checker options.
- `tools/verify.py` owns bounded selection, exact-pin preflight, temporary input
  copies, timeout/output/process cleanup, source-integrity comparison, and
  residue reporting.

Every learner-facing companion excerpt uses source-reference check
`learning:contract`. Generic book validation owns Markdown classification and
reference declaration; the explicit learning-bridges plugin owns companion
selection and must not install the checker implicitly.

## Reproducible commands

Runtime, always available with the declared standard-library interpreter:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --runtime
```

Static checker, only after the exact direct pin is already provisioned:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --checker
```

`requirements-dev.lock` records `mypy==2.2.0` as one exact direct tool pin. It
is not a resolver-generated transitive lock, has no hashes, and does not prove
cross-platform availability. Initial acquisition may require a configured
network index; neither verifier mode performs acquisition.

## Implementation evidence recorded on 2026-07-15

- Runtime mode: **passed** on Linux x86_64 with CPython 3.13.11; 11 tests;
  20-second and 64-KiB child bounds; cleanup passed.
- Checker mode: **passed** on the same Linux x86_64 host with CPython 3.13.11
  and `mypy==2.2.0`; the positive consumer was clean, the negative consumer
  produced `[arg-type]`, `[typeddict-item]`, and `[assignment]`, the corrected
  consumer was clean, and cleanup passed. The verifier did not install or
  acquire the checker.
- Repository scan after both selections: no chapter-local virtual environment,
  bytecode, `__pycache__`, or checker cache was created.

This observation proves one executed CPython runtime/checker target and the
declared pinned checker contract. It does not prove CPython 3.11/3.12 behavior,
another host, other mypy versions, teaching effectiveness,
translation parity, rendered accessibility, Arabic bidi, provenance, or release
approval.
