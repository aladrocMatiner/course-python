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
- Check membership in O(1) using `in`.
- Apply set operations to compare and combine collections of data.
- Choose between `set` and `frozenset` depending on mutability needs.
- Write tests for happy paths and edge cases (empty sets, no intersections).

## Why it matters
When you manage emails, roles, or tags, duplicates create subtle bugs. Sets solve this with direct and efficient syntax. In backend work they’re great for permissions, detecting inconsistencies, and syncing data with other systems.

### Mini adventure
Imagine you collect trading cards and you don’t want duplicates. A `set` is that box where, if you try to put the same card again, the box says: “I already have it.” That’s the idea.

---

## 1. Mental model: a no-duplicates collection

```python
correos = ["ada@example.com", "linus@example.com", "ada@example.com"]
correos_unicos = set(correos)
print(correos_unicos)  # {'ada@example.com', 'linus@example.com'}

print("ada@example.com" in correos_unicos)  # True
```

- Sets do not guarantee order. They focus on membership.
- Converting a list to a set is the easiest way to remove duplicates.

---

## 2. Creating sets and comprehensions

```python
lenguajes = {"python", "go", "rust"}
otros = set(["python", "java"])  # desde iterable

cuadrados = {n**2 for n in range(5)}
print(cuadrados)
```

- Use `{}` with elements for set literals. An empty `{}` is a dictionary; use `set()` for an empty set.
- Set comprehensions work like list comprehensions but remove duplicates automatically.

---

## 3. Set operations

```python
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
```python
etiquetas_existentes = {"python", "django", "api"}
etiquetas_propuestas = {"python", "rest", "observability"}

nuevas = etiquetas_propuestas - etiquetas_existentes
print(f"Etiquetas a crear: {nuevas}")
```

### Data synchronization
```python
usuarios_local = {"ada", "linus", "carol"}
usuarios_remoto = {"linus", "carol", "grace"}

faltantes = usuarios_remoto - usuarios_local
inactivos = usuarios_local - usuarios_remoto
```

### Permission validation
```python
def validar_permisos(asignados, permitidos):
    extra = asignados - permitidos
    if extra:
        raise ValueError(f"Permisos inválidos: {extra}")
    return True
```

---

## 5. `frozenset` and sets as keys
When you need an immutable set (for example, as a dictionary key), use `frozenset`.

```python
segmentos = {
    frozenset({"ios", "premium"}): "Campaña A",
    frozenset({"android", "free"}): "Campaña B",
}

consulta = frozenset({"premium", "ios"})
print(segmentos.get(consulta))
```

- A `frozenset` behaves like a set, except you can’t add/remove elements.
- Great for representing unique combinations of attributes.

---

## 6. Validation and tests

```python
# permissions.py
PERMISOS_VALIDOS = {"view", "edit", "delete"}

def normalizar_permisos(lista_permisos):
    if not isinstance(lista_permisos, (list, set, tuple)):
        raise TypeError("permisos debe ser iterable")
    permisos = set(lista_permisos)
    invalidos = permisos - PERMISOS_VALIDOS
    if invalidos:
        raise ValueError(f"Permisos invalidos: {invalidos}")
    return permisos
```

```python
# tests/test_permissions.py
import pytest
from permissions import normalizar_permisos

def test_normalizar_permisos_elimina_duplicados():
    resultado = normalizar_permisos(["view", "view", "edit"])
    assert resultado == {"view", "edit"}

def test_normalizar_permisos_rechaza_invalidos():
    with pytest.raises(ValueError):
        normalizar_permisos(["hack"])
```

---

## Guided exercises (with TODOs)
1. **5-1 · Unique tags**
   ```python
   etiquetas = ["api", "python", "api", "monitoring"]
   # TODO 1: convert to a set
   # TODO 2: ask the user for a new tag and add it if it doesn't exist
   # TODO 3: print how many unique tags there are
   ```
   *Hint*: use `if nueva not in etiquetas_set` before adding.

2. **5-2 · Skill intersection**
   ```python
   backend = {"python", "django", "postgres"}
   frontend = {"javascript", "react", "django"}
   # TODO 1: compute shared skills
   # TODO 2: compute backend-only skills
   # TODO 3: create a message explaining the result
   ```
   *Hint*: `backend & frontend` and `backend - frontend`.

3. **5-3 · Validate roles**
   ```python
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

## Summary
With sets you can deduplicate data, check membership, and combine collections using declarative operations. This simplifies permission management, tagging, and syncing in any backend system.

## Closing reflection
Now you can spot inconsistencies at a glance using set operations and validate whole catalogs before sending them to another layer. Next we’ll explore tuples to represent immutable records and multi-value returns from functions.
