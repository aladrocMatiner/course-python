# Chapter 27 · Gradual Typing and Static Analysis

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we are going to build

Python lets you add type information gradually. You can annotate one useful
boundary today without rewriting the whole program. Annotations help a reader,
an editor, or a static checker reason about values before execution. They do
not automatically inspect or reject values at runtime.

We will grow one small, synthetic inventory example in three calm stages:

1. **Essential:** annotate functions and collections, represent absence with
   `None`, narrow a union, and keep runtime validation explicit.
2. **Professional:** give dictionary records a shape with `TypedDict`, accept
   behavior structurally with `Protocol`, pass typed callables, preserve a
   generic result type, and use `Self` for a fluent method.
3. **Optional checker route:** compare a valid consumer with a deliberately
   invalid one, recognize stable error categories, repair the contract, and run
   a bounded verifier when the exact checker pin is already provisioned.

The executable authority is
[`examples/typed_inventory.py`](examples/typed_inventory.py). Runtime tests and
checker fixtures use only synthetic SKUs and quantities. They do not use a
network, database, credential, personal record, package index, or learner file.

## Learning objectives

By the end of the route you choose, you will be able to:

- **O1 — Read and write annotations:** annotate parameters, return values, and
  concrete collections without claiming that annotations execute validation.
- **O2 — Model absence:** use `T | None`, preserve valid false values such as
  quantity `0`, and narrow absence with `is None`.
- **O3 — Validate a runtime boundary:** accept an `object`, check its real
  type and domain bounds, reject `bool` where an exact integer is required,
  and recover without partial mutation.
- **O4 — Describe record shape:** use `TypedDict` for the stable keys and value
  types of a dictionary already inside the typed core.
- **O5 — Type behavior and reusable algorithms:** use `Callable`, structural
  `Protocol`, `TypeVar`, and `Self` where each tool makes a real contract clearer.
- **O6 — Read static evidence honestly:** separate checker diagnostics from
  Python exceptions, rely on stable categories rather than full wording, and
  correct an invalid consumer to a clean result.
- **O7 — Explain the evidence boundary:** state what runtime tests, a checker,
  and human review each do—and what none of them proves alone.

The [traceability record](TRACEABILITY.md) maps these objectives to teaching,
practice, solutions, source references, tests, and checkpoints.

## Prerequisites and route map

Before starting, complete the foundational checkpoints in:

- [Chapter 11: Functions](../chapter-11-functions/README.md), for parameters,
  return values, and `None`;
- [Chapter 15: Modules](../chapter-15-modulos/README.md), for imports and public
  module boundaries;
- [Chapter 18: Testing](../chapter-18-testing/README.md), for observable normal
  and failure contracts; and
- [Chapter 22: Introspection](../chapter-22-introspection/README.md), for the
  difference between an object's runtime behavior and information tools inspect.

The numerical position after Chapter 26 does not make networking, C++, or Rust
a prerequisite.

- **Essential route · 2 sessions of 45–60 minutes.** Read E1–E4, complete the
  essential challenge, and score its rubric. Outcome: a typed lookup plus an
  explicitly validated integer boundary. Completion: at least 4/5 points,
  including the static-versus-runtime distinction and `None` recovery. Safe
  stopping point: use these annotations in ordinary Python and continue without
  installing a checker.
- **Professional route · 2 sessions of 50–70 minutes.** Complete the essential
  checkpoint, then P1–P4 and the professional challenge. Outcome: extend the
  tested inventory contract with typed rows, a generic search, a structural
  price source, and subclass-preserving fluent calls. Completion: at least 5/6
  points, including runtime-boundary preservation. Safe stopping point: you can
  consume typed library interfaces without running the optional checker route.
- **Optional checker route · 1 session of 45–60 minutes.** Complete the
  professional checkpoint and use an isolated environment where the exact
  direct tool pin has already been installed deliberately. Outcome: explain
  three diagnostic categories, observe an expected non-zero fixture, and prove
  its corrected counterpart clean. Completion: runtime passes, positive passes,
  negative fails for all declared categories, corrected passes, and cleanup
  passes. A missing or different checker is a prerequisite-missing result, not
  a failed learner checkpoint and never a pass.

Returning learner? Explain why `def echo(value: str) -> str:` does not stop a
runtime call from receiving `7`. Then explain why `if value is None` keeps a
valid `0`. If both are clear, start at the professional route. If you can also
explain structural subtyping and why `list[Dog]` is not automatically a
`list[Animal]`, use the professional checkpoint as a quick audit before the
optional checker route.

## A small glossary

- **Annotation:** type information attached to a name, parameter, or return
  position. It is metadata; Python does not turn it into a validator by default.
- **Static checker:** a separate tool that analyzes source without using each
  value from a live execution.
- **Runtime validation:** executable checks such as `isinstance`, exact-type
  checks, range checks, and explicit exceptions.
- **Union:** a value that may have one of several declared types. `int | None`
  means an integer or absence.
- **Narrowing:** evidence that lets a checker and reader reduce a union inside
  one branch, such as `value is None`.
- **Structural typing:** accepting an object because it has the required method
  shape, not because it inherits from a named base class.
- **Generic:** code whose input and output relationship is expressed using a
  type variable rather than one fixed data type.
- **Escape hatch:** `Any`, `cast`, or an ignore that asks the checker to trust
  code it cannot prove. Escape hatches require a narrow, explained boundary.

The complete flow, in prose, is: a developer writes source and annotations; a
checker may analyze those annotations before a run; the interpreter executes
the source; explicit runtime checks inspect live boundary values; tests observe
selected executions. No arrow, color, or diagram position is needed to
distinguish those four responsibilities.

## Essential route: useful information without false enforcement

### E1. Annotate a function you already understand

Objective: communicate the type of each input and the returned result while
preserving familiar function behavior.

Read this signature from left to right: `sku` is expected to be a string,
`stock` maps strings to integers, and the function returns either an integer or
`None`. Before running it, predict both lines. In particular, decide whether a
stored quantity of `0` means “missing.”

```python runnable
def find_quantity(sku: str, stock: dict[str, int]) -> int | None:
    return stock.get(sku)


quantities = {"PART-7": 0, "PART-8": 4}
print(find_quantity("PART-7", quantities))
print(find_quantity("UNKNOWN", quantities))
```

```text output
0
None
```

The annotation does not change `dict.get`. The runtime behavior still comes
from the function body. The return annotation makes the two outcomes visible
before someone reads every call site.

Typed collections describe their members:

- `list[str]` is a list whose values are strings;
- `dict[str, int]` maps string keys to integer values; and
- `tuple[str, int]` is a two-position tuple with a string then an integer.

Prefer the concrete type that expresses the real operation. Do not add a type
merely because it looks more advanced.

**Modify — O1 TODO:** Add parameter and return annotations without changing
the body or output.

```python todo
def total_units(quantities):
    return sum(quantities)


print(total_units([2, 3, 5]))
```

**Hint:** the input is one concrete list of integers and `sum` returns an
integer for this domain. Start with `list[int]`; generic iterable depth belongs
to the professional route.

**Explained solution:** `def total_units(quantities: list[int]) -> int:` tells
the truth about this exercise's accepted collection. The body stays
`return sum(quantities)`, so output remains `10`. An annotation is most useful
when it preserves and clarifies an already chosen contract.

### E2. Narrow `None` without losing a valid zero

Objective: distinguish absence from a false but present value.

When a value has type `int | None`, check `is None` first. In the other branch,
the value has been narrowed to `int`. Predict the output for `0` and `None`:

```python runnable
def quantity_label(quantity: int | None) -> str:
    if quantity is None:
        return "unknown"
    return f"{quantity} units"


print(quantity_label(0))
print(quantity_label(None))
```

```text output
0 units
unknown
```

The tempting `if not quantity:` would merge `0` with absence and change the
inventory contract. Truthiness can be useful, but it is not a replacement for
an explicit absence decision.

**Edge case:** an empty collection, empty string, `False`, and `0` are all false
in Boolean contexts, but none is the `None` sentinel. Ask “is this absent?” and
“is this empty or zero?” as separate domain questions.

### E3. Observe that annotations do not run validation

Objective: separate metadata, operations, and explicit validation.

This function claims strings, but its body simply returns the object it
receives. Python stores the annotations and executes the body; it does not add
a hidden type check. Predict what this deliberately bad call prints:

```python runnable
def echo_label(label: str) -> str:
    return label


print(echo_label(7))
```

```text output
7
```

This successful process is **not** proof that the call satisfies the declared
contract. A static checker can report the mismatch. Runtime can also fail later
when an operation needs the promised behavior:

<!-- bookcheck: expect-error=TypeError timeout=5 -->
```python expected-error
def add_one(quantity: int) -> int:
    return quantity + 1


print(add_one("2"))
```

The stable signal is `TypeError`; complete traceback wording can change. The
failure comes from trying to add a string and integer, not from the annotation.

**Recovery:** give the function a real integer. This successful neighbor proves
the correction reaches the intended operation:

```python runnable
def add_one(quantity: int) -> int:
    return quantity + 1


print(add_one(2))
```

```text output
3
```

Common mistake: saying “Python checked the type” because a wrong value happened
to trigger an exception. The operation rejected that particular value. A
different body might accept it accidentally, as `echo_label` did.

### E4. Validate the boundary, then trust the typed core

Objective: turn an unknown runtime value into a validated integer or a clear
recoverable error.

At a file, command, HTTP, or loosely shaped mapping boundary, the honest input
type may be `object`. First check the runtime type, then the domain range. An
exact type check is deliberate here because `bool` subclasses `int`, while an
inventory quantity must not accept `True` as one unit.

```python runnable
def parse_quantity(value: object) -> int:
    if type(value) is not int:
        raise TypeError("quantity must be a built-in int, not bool")
    if not 0 <= value <= 1_000_000:
        raise ValueError("quantity must be between 0 and 1000000")
    return value


print(parse_quantity(0))
print(parse_quantity(1_000_000))
```

```text output
0
1000000
```

Predict the exception category before running this boundary failure:

<!-- bookcheck: expect-error=TypeError timeout=5 -->
```python expected-error
def parse_quantity(value: object) -> int:
    if type(value) is not int:
        raise TypeError("quantity must be a built-in int, not bool")
    if not 0 <= value <= 1_000_000:
        raise ValueError("quantity must be between 0 and 1000000")
    return value


print(parse_quantity(True))
```

**Recovery:** replace `True` with the intended integer, rerun, and keep the
original external value unchanged until validation succeeds. Validation should
happen before appending to a collection or updating any other state.

### Essential guided challenge

Build `reorder_message`. It receives the optional result of `find_quantity`.
It must distinguish unknown, zero, and a positive quantity.

```python todo
def reorder_message(quantity: int | None) -> str:
    # TODO 1: return "unknown SKU" only for None
    # TODO 2: return "reorder now" for zero
    # TODO 3: otherwise return "stock: N"
    ...


print(reorder_message(None))
print(reorder_message(0))
print(reorder_message(4))
```

**Hint:** narrow with `is None` first. After that branch, `quantity` is an
integer, so compare it with `0`.

**Explained solution:** the order of questions preserves the domain. First ask
whether the value is absent, then ask whether the present integer is zero.

```python runnable
def reorder_message(quantity: int | None) -> str:
    if quantity is None:
        return "unknown SKU"
    if quantity == 0:
        return "reorder now"
    return f"stock: {quantity}"


print(reorder_message(None))
print(reorder_message(0))
print(reorder_message(4))
```

```text output
unknown SKU
reorder now
stock: 4
```

### Essential checkpoint and rubric

Score 0 or 1 point for each item:

1. **Correctness:** normal, zero, and absent cases produce the stated result.
2. **Annotation clarity:** parameters and returns express the real contract.
3. **Runtime boundary:** invalid `bool`, wrong type, and out-of-range values are
   rejected before mutation.
4. **Recovery:** you can explain and demonstrate one corrected rerun.
5. **Explanation:** you can say why an annotation, a checker, an operation, and
   explicit validation are different.

Completion requires at least 4/5 and must include points 3 and 5. Stop here if
you want: you can add useful annotations without installing any third-party
tool. Reflection: which boundary in one of your programs receives values that
annotations alone cannot make safe?

## Professional route: shape, behavior, and relationships

### P1. Give dictionary records a stable shape with `TypedDict`

Objective: describe known keys while remembering that the runtime object is
still an ordinary dictionary.

The companion's normalized record has exactly the two fields used by this
lesson:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
class InventoryRow(TypedDict):
    """A normalized inventory record used inside the typed core."""

    sku: str
    quantity: int
```

`TypedDict` helps static tools check field names and values. It does not wrap
the dictionary or reject a bad runtime mapping. The explicit boundary remains
`parse_row`:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
def parse_row(raw: Mapping[str, object]) -> InventoryRow:
    """Validate and normalize one untrusted mapping without mutating it.

    ``sku`` must be a string whose stripped form contains 1 through 32
    characters.  ``quantity`` must be a built-in ``int`` (never ``bool``) in
    the inclusive range 0 through 1,000,000.
    """
```

The tested contract strips and uppercases an SKU, accepts 1–32 normalized
characters, and accepts an exact integer quantity from 0 through 1,000,000.
Missing or wrong-typed fields raise `TypeError`; empty/oversized SKUs and
out-of-range quantities raise `ValueError`. The input mapping is unchanged in
every case.

Run the standard-library evidence from the repository root:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --runtime
```

Happy input `{"sku": "  part-7 ", "quantity": 0}` becomes
`{"sku": "PART-7", "quantity": 0}`. The upper boundary—32 characters and
1,000,000 units—is accepted. A 33-character SKU, `-1`, `1_000_001`, or Boolean
quantity is rejected before any inventory row is added.

**Modify — O3/O4 TODO:** add a runtime test for a missing `quantity`. Predict
the exception category and copy the input before the call. **Hint:** a missing
required field is a shape/type error in this teaching contract. **Solution:**
assert `TypeError`, then assert the mapping still equals the copy. Do not weaken
the static field to optional merely to silence a real boundary requirement.

### P2. Express a callback relationship with `Callable` and `TypeVar`

Objective: preserve the element type while accepting one predicate operation.

`Callable[[T], bool]` reads “a callable receiving one `T` and returning a
Boolean.” The same `T` in the result says the function returns an element of
the input type, or `None`:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
def first_matching(items: Iterable[T], predicate: Callable[[T], bool]) -> T | None:
    """Return the first matching item, or ``None`` after finite exhaustion."""

    for item in items:
        if predicate(item):
            return item
    return None
```

The function stops on the first match. Empty or unmatched finite input returns
`None`. If the input is a one-shot iterator, its position remains after the
matched element; typing does not rewind it.

**Predict:** for generator values `1, 2, 3, 4` and predicate `value == 3`, how
many predicate calls occur, and what does the next direct `next` return? The
tests observe three predicate calls and then value `4`.

**Modify — O5 TODO:** use `first_matching` to locate the first row with quantity
`0`. **Hint:** the callback parameter is one `InventoryRow`, so access
`row["quantity"]`. The explained solution returns `InventoryRow | None`; narrow
with `is None` before reading `row["sku"]`.

Common mistake: replacing `T` with `object`. That would lose the useful
relationship between input elements and the returned match. A type variable is
not “any value with no checking”; it connects positions in one call.

### P3. Accept behavior structurally with `Protocol`

Objective: depend on one method shape without forcing inheritance.

The inventory needs a source that may or may not know a price:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
class PriceSource(Protocol):
    """Anything with this method shape can supply an optional unit price."""

    def unit_price(self, sku: str) -> float | None:
        """Return the unit price, or ``None`` when the SKU is unknown."""
```

A class need not inherit from `PriceSource`. If its method accepts `str` and
returns `float | None`, a static checker can accept it structurally:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_positive.py check=learning:contract -->
```python source-ref
class Catalogue:
    def unit_price(self, sku: str) -> float | None:
        return {"PART-7": 2.5}.get(sku)
```

This is a static relationship. The base protocol is not marked
`runtime_checkable`, and even a runtime shape check would not prove that every
future return value respects the annotation. Tests and boundary validation
still own runtime behavior.

**Edge case:** price `0.0` is present and must not be confused with `None`.
**Recoverable mismatch:** if an implementation accepts `int` SKUs and returns
`str`, correct its public method signature and behavior; do not add inheritance
or `cast` merely to suppress the checker.

### P4. Preserve the fluent instance type with `Self`

Objective: state that a fluent method returns the exact receiving type,
including subclasses.

The companion validates and copies a row before mutation, then returns the
same instance:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
    def add(self, row: InventoryRow) -> Self:
        """Validate, copy, and append ``row``; return this exact instance."""

        normalized = parse_row(row)
        self._rows.append(normalized)
        return self
```

`Self` is more precise than writing `Inventory`: calling inherited `add` on a
`LabelledInventory` remains typed as `LabelledInventory`. At runtime, the test
also proves identity with `is`; it does not only trust the annotation.

**Failure and recovery:** adding a Boolean quantity raises before append. The
previous tuple of rows remains equal. Correct the input and call `add` again;
the same instance receives one normalized copy. Mutating either the caller's
original dictionary or a dictionary returned by `.rows` does not change stored
state.

### Professional guided challenge

Create a `WarehousePrices` class with `unit_price(sku: str) -> float | None`,
then find the first zero-quantity row and ask for its price.

```python todo
from typing import assert_type

# TODO 1: implement WarehousePrices without inheriting PriceSource
# TODO 2: find the first zero-quantity InventoryRow
# TODO 3: narrow the optional row and optional price with `is None`
# TODO 4: add the row to a subclass of Inventory and preserve the subclass type
```

**Hint:** a structural protocol cares about the public method shape. Keep the
two absence decisions separate: no matching row and no price are different
domain outcomes.

**Explained solution:** `WarehousePrices.unit_price` accepts `str` and returns
the result of a `dict[str, float].get`, so it satisfies `PriceSource` without
inheritance. `first_matching` preserves `InventoryRow` as its `T`. After each
`is None` branch, the remaining value is narrowed. `Self` preserves the
inventory subclass through `add`. Runtime tests remain necessary for input
bounds, non-mutation, and object identity.

### Professional checkpoint and rubric

Score 0 or 1 point for each item:

1. `TypedDict` fields match the normalized runtime contract.
2. `Callable` and `TypeVar` preserve the callback and return relationship.
3. A structural `Protocol` implementation works without forced inheritance.
4. `Self` preserves both the static subclass and runtime object identity.
5. Invalid boundary input leaves all existing rows unchanged.
6. Your explanation separates static shape from runtime behavior.

Completion requires at least 5/6 and must include points 5 and 6. You may stop
here with a fully runnable, tested companion. Reflection: which interface in a
larger project needs a behavior contract, and which incoming boundary still
needs executable validation?

## Optional advanced route: checker evidence and recovery

### A1. Provision the declared tool deliberately

The runtime route uses only the standard library. The checker route declares
one exact direct development-tool pin in `requirements-dev.lock`:
`mypy==2.2.0`. Despite its filename, this file is **not** a resolver-generated,
hash-complete, transitive, cross-platform lock. It records one direct tool pin
for the declared evidence contract.

If a maintainer deliberately prepares a disposable virtual environment outside
the repository, this installation command may need network/index access:

```text illustrative
python -m pip install -r chapter-27-python-typing/requirements-dev.lock
```

Installation is a separate setup action. The verifier never runs it, never
reaches an index, and never treats a global or differently versioned checker as
equivalent. Do not create `.venv` inside this chapter.

### A2. Compare positive, negative, and corrected consumers

The positive consumer checks typed rows, generic return inference, a structural
price source, and `Self`:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_positive.py check=learning:contract -->
```python source-ref
prices: PriceSource = Catalogue()
assert_type(prices.unit_price(row["sku"]), float | None)

inventory = LabelledInventory()
assert_type(inventory.add(row), LabelledInventory)
```

The negative consumer is deliberately invalid. Read it before running and
predict one category per mistake:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_negative.py check=learning:contract -->
```python source-ref
bad_row: InventoryRow = {"sku": "PART-7", "quantity": "many"}
Inventory().add("not an inventory row")


class BrokenPrices:
    def unit_price(self, sku: int) -> str:
        return str(sku)


prices: PriceSource = BrokenPrices()
```

The stable acceptance categories are:

- `[typeddict-item]` for the wrong value in a declared `TypedDict` field;
- `[arg-type]` for the incompatible `Inventory.add` argument; and
- `[assignment]` for assigning a method-incompatible class to `PriceSource`.

Complete wording, source prefixes, notes, colors, and caret formatting are not
golden output. The verifier requires a non-zero result and all three category
tokens.

The corrected consumer fixes the contracts instead of hiding them:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_corrected.py check=learning:contract -->
```python source-ref
row: InventoryRow = {"sku": "PART-7", "quantity": 3}
inventory = Inventory().add(row)
assert_type(inventory, Inventory)


class FixedPrices:
    def unit_price(self, sku: str) -> float | None:
        return 1.25 if sku == "PART-7" else None
```

Common mistake: adding unbounded `Any`, a plain `# type: ignore`, or a `cast`
that changes no runtime behavior. First correct the value, signature, or
boundary. When a real external limitation requires an escape hatch, constrain
it to the smallest expression, use a code-specific ignore where supported, and
record why runtime evidence covers the gap.

**Modify — O6 TODO:** copy one negative case into a disposable working file,
predict its category, correct the underlying contract, and rerun the same
checker configuration. **Hint:** do not edit the canonical negative fixture;
the verifier needs it as expected-failure evidence. **Solution:** the corrected
fixture demonstrates all three repairs while the runtime suite proves that the
typed core still works.

### A3. Run the bounded verifier

From the repository root, runtime verification is always selected explicitly:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --runtime
```

Checker verification is a separate selection:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --checker
```

The verifier:

1. snapshots the chapter source and rejects pre-existing caches/bytecode;
2. copies only the companion, tests, and three consumers to a temporary root;
3. uses the current interpreter with `-I -B`, no stdin, a minimal environment,
   a 20-second bound, a 64-KiB combined-output bound, and process-group cleanup;
4. runs runtime tests, or checks the exact `mypy==2.2.0` version;
5. in checker mode, requires positive clean, negative non-zero with all three
   stable categories, and corrected clean; and
6. deletes the temporary root, compares the chapter snapshot, scans for
   residue, and reports cleanup independently.

Exit status `0` means the selected contract and cleanup passed. Status `1`
means a selected behavior, bound, source-integrity, or cleanup check failed.
Status `2` means command usage or the exact checker prerequisite is missing.
Missing checker evidence must remain **prerequisite missing**; it cannot be
projected as pass.

The verifier limits accidents from trusted lesson sources; it is not a hostile
code sandbox. It proves only the selected interpreter/tool execution. It does
not prove all platforms, all Python versions, the naturalness of a translation,
teaching effectiveness, accessibility, package compatibility, or production
safety.

### Advanced checkpoint and rubric

Score 0 or 1 point for each item:

1. The exact provisioned checker version matches the direct pin.
2. Positive and corrected consumers are clean under the same strict options.
3. The negative consumer exits non-zero for all three stable categories.
4. Runtime tests still pass after the correction.
5. No broad `Any`, unqualified ignore, or evidence-only `cast` hides a defect.
6. Cleanup passes and no checker cache appears in the repository.

Completion requires all six points. If the pin is absent, keep this route
pending and retain the professional checkpoint. Reflection: what did the
checker find before execution, and what important runtime fact could it still
not prove?

## Common mistakes and calm recovery

- **“Annotated means validated.”** Revisit E3, identify the operation that
  actually ran, and put explicit validation at the incoming boundary.
- **Using `if not value` for `T | None`.** Revisit the `0` case and narrow with
  `is None` when absence is the question.
- **Annotating every value with the widest type.** Start from the real accepted
  contract; widen only when behavior truly accepts more.
- **Using `TypedDict` as a runtime parser.** Keep `parse_row` at the untrusted
  boundary and return the typed shape only after validation.
- **Forcing protocol inheritance.** Match the public method shape; inheritance
  is a separate design choice.
- **Silencing diagnostics.** Correct the smallest mismatch, then rerun its
  runtime neighbor and static check from a clean temporary root.
- **Calling a direct pin a universal lock.** Record the tool, version, host,
  Python target, acquisition assumptions, and actual run. Do not infer a
  transitive or cross-platform resolution.

## Maintainer verification and evidence boundary

All companion excerpts in this chapter use the registered source-reference
check `learning:contract`. The owning plugin may select that contract; generic
book validation checks Markdown and declared reference shape without silently
executing arbitrary companion files.

Run the narrow runtime evidence first:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --runtime
```

Run checker evidence only when `mypy==2.2.0` is already present in the selected
interpreter:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --checker
```

Do not install a checker as a hidden validation step. Record runtime and
checker outcomes independently. A passing checker does not replace runtime
tests; passing structure does not approve language fluency, pedagogy,
accessibility, bidirectional rendering, provenance, or publication.

## Closing reflection and next steps

Good typing makes a real boundary easier to understand. It does not make Python
less dynamic, and it does not remove the need to validate external values. Use
the smallest annotation that clarifies a relationship, then prove runtime
behavior at the boundary where mistakes matter.

For native package interfaces, continue independently to
[Chapter 24: Python and C++](../chapter-24-python-cpp-integration/README.md) or
[Chapter 25: Python and Rust](../chapter-25-python-rust-integration/README.md).
For a project that combines domain modeling, persistence, CLI, tests, logging,
and artifact verification, continue to
[Chapter 28: Professional Capstone](../chapter-28-professional-capstone/README.md).
