# Chapter 5 · Sets, Uniqueness, and Membership

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll explore sets (`set` and `frozenset`) to deduplicate data, check membership, and combine collections using “math-like” operations. We’ll use examples focused on permissions, tags, and syncing data between sources.

## Learning path
1. **Core idea**: a collection with no duplicates.
2. **Create and query**: build from lists, set comprehensions, mutability.
3. **Main operations**: union, intersection, difference, subsets.
4. **Real cases**: permissions, tags, syncing between sources.
5. **`frozenset` and using sets as keys**: when you need immutability.
6. **Validation and tests**: making sure access/dedup rules hold.

## Learning objectives
- Build sets from other collections and remove duplicates.
- Check membership in O(1) on average using `in`.
- Apply set operations to compare and combine collections of data.
- Choose between `set` and `frozenset` depending on mutability needs.
- Write tests for happy paths and edge cases (empty sets, no intersections).

## Prerequisites and optional previews
You should be comfortable with [lists](../chapter-03-lists/README.md) and [dictionaries](../chapter-04-dictionaries/README.md). Functions, exceptions, and pytest appear here only as reusable patterns; study them fully in [Chapter 11](../chapter-11-functions/README.md), [Chapter 14](../chapter-14-exceptions/README.md), and [Chapter 18](../chapter-18-testing/README.md).

## Why it matters
When you manage emails, roles, or tags, duplicates create subtle bugs. Sets solve this with direct and efficient syntax. In backend work they’re great for permissions, detecting inconsistencies, and syncing data with other systems.

### Mini adventure
Imagine you collect trading cards and you don’t want duplicates. A `set` is that box where, if you try to put the same card again, the box says: “I already have it.” That’s the idea.

## Predict before running
Before the first example, predict the set’s contents and the membership result. Do not predict the raw iteration order: sets deliberately provide no stable display order, so the example sorts only for presentation.

---

## 1. Mental model: a no-duplicates collection

```python runnable
correos = ["noor@example.com", "frej@example.com", "noor@example.com"]
correos_unicos = set(correos)
print(sorted(correos_unicos))  # ['frej@example.com', 'noor@example.com']

print("noor@example.com" in correos_unicos)  # True
```

- Sets do not guarantee order. They focus on membership.
- Converting a list to a set is the easiest way to remove duplicates.

---

## 2. Creating sets and comprehensions

```python runnable
lenguajes = {"python", "go", "rust"}
otros = set(["python", "java"])  # desde iterable

cuadrados = {n**2 for n in range(5)}
print(sorted(cuadrados))
```

- Use `{}` with elements for set literals. An empty `{}` is a dictionary; use `set()` for an empty set.
- Set comprehensions work like list comprehensions but remove duplicates automatically.

---

## 3. Set operations

```python runnable
permisos_admin = {"view", "edit", "delete"}
permisos_editor = {"view", "edit"}
permisos_guest = {"view"}

union = permisos_admin | permisos_guest           # {'view', 'edit', 'delete'}
interseccion = permisos_admin & permisos_editor   # {'view', 'edit'}
solo_admin = permisos_admin - permisos_editor     # {'delete'}
simetrica = permisos_admin ^ permisos_editor      # {'delete'}

print(permisos_guest <= permisos_editor)  # True: guest es subconjunto de editor
```

- `|` union, `&` intersection, `-` difference, `^` symmetric difference.
- `<=`/`<` to check whether one set is a subset of another.

---

## 4. Practical cases

### Tag control
```python runnable
etiquetas_existentes = {"python", "django", "api"}
etiquetas_propuestas = {"python", "rest", "observability"}

nuevas = etiquetas_propuestas - etiquetas_existentes
print(f"Etiquetas a crear: {sorted(nuevas)}")
```

### Data synchronization
```python runnable
local_users = {"noor", "frej", "taha"}
remote_users = {"frej", "taha", "grace"}

missing = remote_users - local_users
inactive = local_users - remote_users
```

### Permission validation
```python runnable
def validate_permissions(assigned, allowed):
    extra = assigned - allowed
    if extra:
        raise ValueError(f"Invalid permissions: {extra}")
    return True
```

---

## 5. `frozenset` and sets as keys
When you need an immutable set (for example, as a dictionary key), use `frozenset`.

```python runnable
segments = {
    frozenset({"ios", "premium"}): "Campaign A",
    frozenset({"android", "free"}): "Campaign B",
}

query = frozenset({"premium", "ios"})
print(segments.get(query))
```

- A `frozenset` behaves like a set, except you can’t add/remove elements.
- Great for representing unique combinations of attributes.

---

## 6. Validation and tests

```python runnable
# permissions.py
VALID_PERMISSIONS = {"view", "edit", "delete"}

def normalize_permissions(permission_list):
    if not isinstance(permission_list, (list, set, tuple)):
        raise TypeError("permissions must be iterable")
    permissions = set(permission_list)
    invalid = permissions - VALID_PERMISSIONS
    if invalid:
        raise ValueError(f"Invalid permissions: {invalid}")
    return permissions
```

```python illustrative
# tests/test_permissions.py
import pytest
from permissions import normalize_permissions

def test_normalize_permissions_deduplicates():
    result = normalize_permissions(["view", "view", "edit"])
    assert result == {"view", "edit"}

def test_normalize_permissions_rejects_invalid():
    with pytest.raises(ValueError):
        normalize_permissions(["hack"])
```

---

## Guided exercises (with TODOs)
1. **5-1 · Unique tags**
   ```python todo
   etiquetas = ["api", "python", "api", "monitoring"]
   # TODO 1: convert to a set
   # TODO 2: ask the user for a new tag and add it if it doesn't exist
   # TODO 3: print how many unique tags there are
   ```
   *Hint*: use `if nueva not in etiquetas_set` before adding.

2. **5-2 · Skill intersection**
   ```python todo
   backend = {"python", "django", "postgres"}
   frontend = {"javascript", "react", "django"}
   # TODO 1: compute shared skills
   # TODO 2: compute backend-only skills
   # TODO 3: create a message explaining the result
   ```
   *Hint*: `backend & frontend` and `backend - frontend`.

3. **5-3 · Validate roles**
   ```python todo
   roles_permitidos = {"admin", "editor", "viewer"}
   asignados = {"admin", "auditor"}
   # TODO 1: write check_roles(asignados, permitidos)
   # TODO 2: the function must raise ValueError if it finds roles outside the catalog
   # TODO 3: add a test confirming empty sets are valid
   ```
   *Hint*: reuse `extra = asignados - permitidos` and `pytest.raises`.

---

## Common mistakes
- **Trying to index a set**: sets have no order or positions. Convert to a list if you need indexes.
- **Expecting deterministic order**: set order can change between runs. Don’t use sets for UI output without converting.
- **Forgetting `{}` is a dict**: use `set()` to create an empty set.
- **Comparing references instead of contents**: use set operations to detect differences declaratively.

---

## Explained solutions
1. **Unique tags**: `etiquetas_unicas = set(etiquetas)` removes duplicates; count with `len(etiquetas_unicas)`.
2. **Skill intersection**: `compartidas = backend & frontend` and `solo_backend = backend - frontend`; explain results with an f-string.
3. **Validate roles**: compute `extra = asignados - permitidos` and raise `ValueError` if it’s not empty; add a test that `check_roles(set(), permitidos)` returns `True`.

---

## Checkpoint and self-assessment
Without running code, explain why membership is O(1) on average, when `frozenset` is required, and what each of `|`, `&`, and `-` returns. Then solve one exercise and test a normal case plus an empty-set edge case.

- **Ready**: you can choose the right set operation, avoid relying on order, and justify both tests.
- **Almost**: the code works, but you still need notes to choose an operation or edge case.
- **Review**: revisit sections 1, 3, and 5, then retry with different sample data.

## Summary
With sets you can deduplicate data, check membership, and combine collections using declarative operations. This simplifies permission management, tagging, and syncing in any backend system.

## Closing reflection
Now you can spot inconsistencies at a glance using set operations and validate whole catalogs before sending them to another layer. Next we’ll explore tuples to represent immutable records and multi-value returns from functions.
