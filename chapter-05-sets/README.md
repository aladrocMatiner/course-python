# Chapter 5 · Sets, Uniqueness, and Membership

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll explore sets (`set` and `frozenset`) to deduplicate data, check membership, and combine collections using “math-like” operations. We’ll use examples focused on permissions, tags, and syncing data between sources.

## Learning path

- **Essential · 40–55 minutes.** Prerequisites: Chapters 3–4. Read Sections 1 and 3, then complete Exercise 5-0. Outcome: deduplicate direct data, check membership, and compare sets with `|`, `&`, and `-`. Evidence: the explained solution covers a normal case, an empty-set boundary, the intentional indexing error, and a successful recovery. You are finished when you can explain why a set has no position `0`; continue to Chapter 6 or stop safely here.
- **Intermediate · 45–60 minutes.** Prerequisites: the essential checkpoint and [Chapter 10](../chapter-10-loops/README.md). Study Section 2, the tag and synchronization examples in Section 4, and Section 5; complete Exercises 5-1 and 5-2. Outcome: create sets with a comprehension and choose `frozenset` for a hashable group. Evidence: rerun both exercises with an empty input. This route is optional before Chapter 6.
- **Optional professional preview · 45–60 minutes.** Prerequisites: the intermediate route plus [functions](../chapter-11-functions/README.md), [exceptions](../chapter-14-exceptions/README.md), and [testing](../chapter-18-testing/README.md). Study permission validation, Section 6, and Exercise 5-3. Outcome: validate a permission catalog with a function, a deliberate exception, and pytest evidence. This preview is skippable and does not block the next essential chapter.

## Learning objectives
- Build sets from other collections and remove duplicates.
- Check membership in O(1) on average using `in`.
- Apply set operations to compare and combine collections of data.
- Choose between `set` and `frozenset` depending on mutability needs.
- Write tests for happy paths and edge cases (empty sets, no intersections).

## Prerequisites and optional previews
You should be comfortable with [lists](../chapter-03-lists/README.md) and [dictionaries](../chapter-04-dictionaries/README.md). The essential route uses direct set values and familiar built-ins; it requires no function definitions, exception handling, typing, or pytest. Set comprehensions, functions, exceptions, and tests are optional previews linked from the routes above.

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

**Optional intermediate preview:** this section uses `range` and a set comprehension, which [Chapter 10](../chapter-10-loops/README.md) teaches in sequence. Essential learners can skip directly to Section 3.

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

**Optional professional preview:** this example defines a function and raises an exception. Skip it on the essential route; Chapters [11](../chapter-11-functions/README.md) and [14](../chapter-14-exceptions/README.md) teach those tools first.

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

This is intermediate depth. It is useful, but it is not required by the essential checkpoint.

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

**Optional professional preview:** this section combines functions, exceptions, type checks, and pytest. Complete Chapters [11](../chapter-11-functions/README.md), [14](../chapter-14-exceptions/README.md), and [18](../chapter-18-testing/README.md) first, or copy the pattern without treating it as required work.

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
1. **5-0 · Essential membership map**

   Predict the four printed results before writing code. The empty set is the boundary case.

   ```python todo
   skills = ["python", "python", "git"]
   required = {"python", "sql"}
   # TODO 1: create unique_skills from skills
   # TODO 2: print membership for "python"
   # TODO 3: print the shared and missing sets in sorted order
   # TODO 4: print the size of an empty set
   ```

   *Hint*: use `set(skills)`, `&`, `-`, `sorted(...)`, and `len(set())`. No loop or function definition is needed.

2. **5-1 · Unique tags** *(intermediate)*
   ```python todo
   etiquetas = ["api", "python", "api", "monitoring"]
   # TODO 1: convert to a set
   # TODO 2: ask the user for a new tag and add it if it doesn't exist
   # TODO 3: print how many unique tags there are
   ```
   *Hint*: use `if nueva not in etiquetas_set` before adding.

3. **5-2 · Skill intersection** *(intermediate)*
   ```python todo
   backend = {"python", "django", "postgres"}
   frontend = {"javascript", "react", "django"}
   # TODO 1: compute shared skills
   # TODO 2: compute backend-only skills
   # TODO 3: create a message explaining the result
   ```
   *Hint*: `backend & frontend` and `backend - frontend`.

4. **5-3 · Validate roles** *(optional professional preview)*
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

### Essential solution 5-0

First convert the list once. Intersection keeps values present in both sets; difference keeps requirements that are still missing. `set()` supplies the empty boundary without introducing a special case.

```python runnable
skills = ["python", "python", "git"]
unique_skills = set(skills)
required = {"python", "sql"}

print(sorted(unique_skills))
print("python" in unique_skills)
print(sorted(unique_skills & required))
print(sorted(required - unique_skills))
print(len(set()))
```

Observe `['git', 'python']`, `True`, `['python']`, `['sql']`, and `0`, in that order. The duplicate disappears and the empty set remains a valid input.

A set has no stable positions. This block intentionally indexes one, so the stable diagnostic signal is `TypeError`:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
languages = {"python", "rust"}
print(languages[0])
```

Recover by asking about membership or sorting only for presentation:

```python runnable
languages = {"python", "rust"}
print("python" in languages)
print(sorted(languages))
```

The recovery prints `True` and `['python', 'rust']`; it does not pretend that the set itself gained an order.

### Optional-route solution notes

1. **Unique tags**: `etiquetas_unicas = set(etiquetas)` removes duplicates; count with `len(etiquetas_unicas)`.
2. **Skill intersection**: `compartidas = backend & frontend` and `solo_backend = backend - frontend`; explain results with an f-string.
3. **Validate roles**: compute `extra = asignados - permitidos` and raise `ValueError` if it’s not empty; add a test that `check_roles(set(), permitidos)` returns `True`.

---

## Checkpoint and self-assessment
Complete Exercise 5-0, predict before each run, and compare the observed normal, empty, error, and recovery cases with the solution. Then explain aloud why `languages[0]` fails while `"python" in languages` is meaningful.

- **Correctness:** duplicates disappear; membership, intersection, difference, and the empty boundary match the stated observations.
- **Readability:** names describe the two sets, and sorting is used only for display.
- **Error handling:** you identify `TypeError` as the stable signal and recover without indexing or relying on iteration order.
- **Verification:** you actually run the normal, boundary, expected-error, and recovery blocks with CPython 3.11+.
- **Explanation:** in your own words, distinguish membership from position and explain one operation.

**Advance when all five points are true.** Continue to Chapter 6; the intermediate and professional routes above remain optional. If one point is missing, revisit Sections 1 and 3 and rerun 5-0 with `skills = []`.

## Summary
With sets you can deduplicate data, check membership, and combine collections using declarative operations. This simplifies permission management, tagging, and syncing in any backend system.

## Closing reflection
Now you can spot inconsistencies at a glance using set operations and validate whole catalogs before sending them to another layer. Next we’ll explore tuples to represent immutable records and multi-value returns from functions.
