# Chapter 4 · Dictionaries (Key–Value Data)

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
You’ll learn to model structured information using dictionaries (`dict`). We’ll work with user profiles, configuration objects, and JSON-like responses typical in backend work. You’ll practice creating, updating, merging, and validating dictionaries before exposing them as an API or storing them in a database.

## Learning path
1. **Mental model**: dictionaries as maps between keys and values.
2. **Create and access**: safe reading (`[]` vs `get`) and friendly formatting.
3. **Update and remove**: `.update`, `del`, `pop` and defaults.
4. **Iterate**: `keys`, `values`, `items`, dictionary comprehensions.
5. **Nested structures**: lists of dicts and dicts inside dicts.
6. **Validation and tests**: making sure payloads have required fields.

## Learning objectives
- Declare dictionaries to represent real entities (users, orders, configuration).
- Read and update keys safely (strict vs tolerant access).
- Iterate over dictionaries and build derived structures.
- Merge dictionaries and handle nested keys without losing consistency.
- Write tests that validate the presence/absence of required keys.

## Why it matters
Dictionaries are the foundation of JSON, the format modern APIs use to send data. Mastering `dict` means manipulating payloads, HTTP responses, parameters, and configuration objects without friction. It also prepares you for serializing and deserializing data between Python and other systems.

### Mini adventure
A dictionary is like your phone’s contacts: you search a name (key) and you get a piece of info (value). If you know how contacts work, you already get the idea. The magic: your program can find things “instantly” without scanning a whole list.

---

## 1. Mental model: dictionaries as maps
Think of a dictionary like a phone book: you look up a key (name) and retrieve a value (number).

```python
usuario = {
    "username": "ada",
    "email": "ada@example.com",
    "roles": ["admin", "editor"],
}

print(usuario["username"])  # acceso estricto
print(usuario.get("timezone", "UTC"))  # acceso tolerante con valor por defecto
```

- Keys must be immutable (strings, numbers, immutable tuples). Values can be any object.
- Use `get` when you aren’t sure a key exists; it avoids `KeyError` and lets you define sensible defaults.

---

## 2. Create, read, and normalize values

```python
perfil = {}
perfil["first_name"] = "Grace"
perfil["last_name"] = "Hopper"
perfil.setdefault("language", "Python")  # sólo asigna si no existe

nombre_completo = f"{perfil['first_name']} {perfil['last_name']}"
print(nombre_completo)
```

- `setdefault` avoids overwriting values that are already set.
- When building strings, make sure the keys exist or use `get` with defaults.

### Formatting function
```python
def formatear_perfil(data):
    first = data.get("first_name", "Desconocido")
    last = data.get("last_name", "")
    return f"{first} {last}".strip()
```

---

## 3. Update, merge, and clean dictionaries

```python
config_base = {"timeout": 5, "retries": 3}
config_usuario = {"timeout": 10, "region": "eu-west"}

config_final = config_base | config_usuario  # Python 3.9+: crea un nuevo dict
config_base.update({"logging": True})        # modifica en sitio

print(config_final)
print(config_base)
```

```python
feature_flags = {"beta": True, "legacy": False}
legacy = feature_flags.pop("legacy")  # devuelve el valor eliminado
print(legacy)

del feature_flags["beta"]
print(feature_flags)
```

- Use `|` or `|=` to merge configuration without writing loops.
- `pop` removes and returns a value (handy when moving data elsewhere).
- `del` removes without returning (perfect when you don’t need the removed value).

---

## 4. Iterating dictionaries and building derived data

```python
permisos = {"alice": "admin", "bob": "editor", "carol": "viewer"}

for usuario, rol in permisos.items():
    print(f"{usuario} → {rol}")

roles = {rol for rol in permisos.values()}  # set por comprensión
print(roles)

saludos = {user: f"Hola, {user.title()}" for user in permisos.keys()}
print(saludos)
```

- `items()` gives you key-value pairs.
- Dictionary comprehensions (`{key: value for ...}`) are a clean way to build new mappings.

---

## 5. Nested structures

```python
usuarios = {
    "ada": {"email": "ada@example.com", "active": True},
    "linus": {"email": "linus@example.com", "active": False},
}

for username, detalle in usuarios.items():
    estado = "activo" if detalle.get("active") else "inactivo"
    print(f"{username}: {estado}")
```

```python
# Diccionarios dentro de listas
api_response = {
    "results": [
        {"id": 1, "status": "ok"},
        {"id": 2, "status": "failed", "error": "timeout"},
    ],
    "meta": {"count": 2}
}

fallidos = [item for item in api_response["results"] if item["status"] != "ok"]
print(fallidos)
```

- Always validate that keys exist before indexing; external APIs can omit them.
- For deeper structures, consider helper functions that encapsulate nested access.

---

## 6. Validation and tests

```python
# profiles.py
def validar_perfil(datos):
    campos_requeridos = {"username", "email"}
    faltantes = campos_requeridos - datos.keys()
    if faltantes:
        raise ValueError(f"Faltan campos: {sorted(faltantes)}")
    if "@" not in datos["email"]:
        raise ValueError("Email inválido")
    return True
```

```python
# tests/test_profiles.py
import pytest
from profiles import validar_perfil

def test_validar_perfil_exitoso():
    payload = {"username": "ada", "email": "ada@example.com"}
    assert validar_perfil(payload) is True

def test_validar_perfil_detecta_campos_faltantes():
    with pytest.raises(ValueError) as exc:
        validar_perfil({"username": "ada"})
    assert "email" in str(exc.value)
```

Tests guarantee a dictionary has the minimum required fields before it enters a view or serializer.

---

## Guided exercises (with TODOs)
1. **4-1 · Public profile**
   ```python
   perfil = {"username": "alba", "skills": ["python", "django"]}
   # TODO 1: add first_name and last_name fields
   # TODO 2: print a formatted message using get with defaults
   # TODO 3: add a "links" field that is another dict (github, linkedin)
   ```
   *Hint*: use `setdefault` to avoid overwriting existing data.

2. **4-2 · Merged configuration**
   ```python
   default = {"timeout": 5, "cache": True}
   user = {"timeout": 10, "debug": False}
   # TODO 1: create merge_config(base, custom) -> dict
   # TODO 2: make sure base is not modified (use a copy)
   # TODO 3: write a test that confirms base stays the same after merge
   ```
   *Hint*: use `base | custom` or `copy()` + `update()`.

3. **4-3 · Field audit**
   ```python
   registro = {"id": 1, "status": "ok", "duration_ms": 120}
   # TODO 1: write requires_fields(registro, campos_obligatorios)
   # TODO 2: the function must return a tuple (valid, missing)
   # TODO 3: add a test that confirms optional extra fields are allowed
   ```
   *Hint*: reuse set operations (`campos_obligatorios - registro.keys()`).

---

## Common mistakes
- **Assuming a key exists** ⇒ `KeyError`. Use `get` or validate first.
- **Mutating the same dict in multiple places** ⇒ side effects. Make copies (`dict.copy()`, `|`).
- **Mixing up lists and dicts** ⇒ indexing with numbers when you actually have a `dict`, or vice versa.
- **Not normalizing keys** ⇒ inconsistent casing creates duplicates.

---

## Explained solutions
1. **Public profile**: `perfil.setdefault("first_name", "")` fills data without losing what you already have; build messages with `perfil.get("first_name", "Desconocida")` to avoid errors.
2. **Merged config**: build `merged = base | custom` (or `merged = base.copy(); merged.update(custom)`) and test that `base` keeps its original value.
3. **Field audit**: `missing = required - registro.keys()` (and optionally `extra = registro.keys() - required`) gives a clear view of what’s missing/extra for better error messages.

---

## Summary
You practiced declaring, reading, merging, and validating dictionaries, iterating them, and handling nested structures. You know when to use `[]` vs `get`, how to move keys with `pop`, and how to check a payload is complete before processing it.

## Closing reflection
Every API you build relies on dictionaries to represent data. Now you can structure them carefully, protect yourself from missing keys, and write tests to prevent regressions. Next, we’ll study `set`, perfect for deduplicating and reasoning about membership when collections grow.
