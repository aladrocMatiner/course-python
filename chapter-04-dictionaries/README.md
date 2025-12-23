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
user = {
    "username": "noor",
    "email": "noor@example.com",
    "roles": ["admin", "editor"],
}

print(user["username"])  # strict access
print(user.get("timezone", "UTC"))  # tolerant access with a default
```

- Keys must be immutable (strings, numbers, immutable tuples). Values can be any object.
- Use `get` when you aren’t sure a key exists; it avoids `KeyError` and lets you define sensible defaults.

---

## 2. Create, read, and normalize values

```python
profile = {}
profile["first_name"] = "Grace"
profile["last_name"] = "Hopper"
profile.setdefault("language", "Python")  # only sets if missing

full_name = f"{profile['first_name']} {profile['last_name']}"
print(full_name)
```

- `setdefault` avoids overwriting values that are already set.
- When building strings, make sure the keys exist or use `get` with defaults.

### Formatting function
```python
def format_profile(data):
    first = data.get("first_name", "Unknown")
    last = data.get("last_name", "")
    return f"{first} {last}".strip()
```

---

## 3. Update, merge, and clean dictionaries

```python
base_config = {"timeout": 5, "retries": 3}
user_config = {"timeout": 10, "region": "eu-west"}

final_config = base_config | user_config  # Python 3.9+: creates a new dict
base_config.update({"logging": True})      # modifies in place

print(final_config)
print(base_config)
```

```python
feature_flags = {"beta": True, "legacy": False}
legacy = feature_flags.pop("legacy")  # returns the removed value
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
permissions = {"alice": "admin", "bob": "editor", "taha": "viewer"}

for user, role in permissions.items():
    print(f"{user} → {role}")

roles = {role for role in permissions.values()}  # set comprehension
print(roles)

greetings = {user: f"Hello, {user.title()}" for user in permissions.keys()}
print(greetings)
```

- `items()` gives you key-value pairs.
- Dictionary comprehensions (`{key: value for ...}`) are a clean way to build new mappings.

---

## 5. Nested structures

```python
users = {
    "noor": {"email": "noor@example.com", "active": True},
    "frej": {"email": "frej@example.com", "active": False},
}

for username, details in users.items():
    status = "active" if details.get("active") else "inactive"
    print(f"{username}: {status}")
```

```python
# Dictionaries inside lists
api_response = {
    "results": [
        {"id": 1, "status": "ok"},
        {"id": 2, "status": "failed", "error": "timeout"},
    ],
    "meta": {"count": 2}
}

failed = [item for item in api_response["results"] if item["status"] != "ok"]
print(failed)
```

- Always validate that keys exist before indexing; external APIs can omit them.
- For deeper structures, consider helper functions that encapsulate nested access.

---

## 6. Validation and tests

```python
# profiles.py
def validate_profile(data):
    required_fields = {"username", "email"}
    missing = required_fields - data.keys()
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")
    if "@" not in data["email"]:
        raise ValueError("Invalid email")
    return True
```

```python
# tests/test_profiles.py
import pytest
from profiles import validate_profile

def test_validate_profile_success():
    payload = {"username": "noor", "email": "noor@example.com"}
    assert validate_profile(payload) is True

def test_validate_profile_detects_missing_fields():
    with pytest.raises(ValueError) as exc:
        validate_profile({"username": "noor"})
    assert "email" in str(exc.value)
```

Tests guarantee a dictionary has the minimum required fields before it enters a view or serializer.

---

## Guided exercises (with TODOs)
1. **4-1 · Public profile**
   ```python
   profile = {"username": "alba", "skills": ["python", "django"]}
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
   record = {"id": 1, "status": "ok", "duration_ms": 120}
   # TODO 1: write requires_fields(record, required_fields)
   # TODO 2: the function must return a tuple (valid, missing)
   # TODO 3: add a test that confirms optional extra fields are allowed
   ```
   *Hint*: reuse set operations (`required_fields - record.keys()`).

---

## Common mistakes
- **Assuming a key exists** ⇒ `KeyError`. Use `get` or validate first.
- **Mutating the same dict in multiple places** ⇒ side effects. Make copies (`dict.copy()`, `|`).
- **Mixing up lists and dicts** ⇒ indexing with numbers when you actually have a `dict`, or vice versa.
- **Not normalizing keys** ⇒ inconsistent casing creates duplicates.

---

## Explained solutions
1. **Public profile**: `profile.setdefault("first_name", "")` fills data without losing what you already have; build messages with `profile.get("first_name", "Unknown")` to avoid errors.
2. **Merged config**: build `merged = base | custom` (or `merged = base.copy(); merged.update(custom)`) and test that `base` keeps its original value.
3. **Field audit**: `missing = required - record.keys()` (and optionally `extra = record.keys() - required`) gives a clear view of what’s missing/extra for better error messages.

---

## Summary
You practiced declaring, reading, merging, and validating dictionaries, iterating them, and handling nested structures. You know when to use `[]` vs `get`, how to move keys with `pop`, and how to check a payload is complete before processing it.

## Closing reflection
Every API you build relies on dictionaries to represent data. Now you can structure them carefully, protect yourself from missing keys, and write tests to prevent regressions. Next, we’ll study `set`, perfect for deduplicating and reasoning about membership when collections grow.
