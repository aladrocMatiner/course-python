# Chapter 14 · Exceptions: From Beginner to Hero

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
You’ll master Python’s exception system: spotting errors, handling them with `try/except`, raising your own exceptions, creating custom classes, and designing robust APIs that clearly explain what went wrong. We’ll practice professional patterns for validating input, wrapping risky calls, and cleaning up resources.

## Learning path
1. **Mental model**: exceptions interrupt the normal flow.
2. **Basic `try/except`**: catch known errors.
3. **`else` and `finally`**: supporting blocks.
4. **`raise`**: raise your own errors.
5. **Custom exceptions**: `class` that inherits from `Exception`.
6. **Exception chaining (`raise ... from ...`)**.
7. **Context managers and cleanup**.
8. **Tests and exercises**.

## Learning objectives
- Identify what exceptions can happen and catch them selectively.
- Use `else` and `finally` to control side flows and cleanup.
- Create and raise custom exceptions to describe domain errors.
- Chain exceptions so you keep the original context.
- Test functions that must raise or handle errors.

## Why it matters
Ignoring exceptions causes silent failures or cryptic messages. Good error handling gives confidence to your API and makes production debugging much easier.

### Mini adventure
Exceptions are like road signs and airbags: they’re not there to annoy you — they warn you and protect you when something goes wrong. If you learn to read them and respond, your program becomes much safer.

---

## 1. `try/except` from zero

```python
try:
    resultado = int("abc")
    print(resultado)
except ValueError:
    print("No era un número válido")
```

- The `except` block runs only if `ValueError` happens.
- If you don’t specify the exception you catch everything (`except Exception:`) — avoid that unless you have a very controlled reason.

### Catching multiple exceptions
```python
import json

try:
    with open("config.txt", encoding="utf-8") as archivo:
        datos = json.load(archivo)
except FileNotFoundError as exc:
    print("Archivo faltante", exc)
except json.JSONDecodeError as exc:
    print("JSON inválido", exc)
```

---

## 2. `else` and `finally`

```python
def leer_config():
    # Simple example: in real life you would read from a file/JSON
    return {"debug": True}

try:
    datos = leer_config()
except (FileNotFoundError, ValueError):
    datos = {}
else:
    print("Config cargada correctamente")
finally:
    print("Fin del proceso")
```

- `else` runs only if no exception happened.
- `finally` always runs (ideal for closing connections and freeing resources).

---

## 3. Raising your own exceptions (`raise`)

```python
def dividir(a, b):
    if b == 0:
        raise ZeroDivisionError("El denominador no puede ser cero")
    return a / b
```

- `raise` stops the function and propagates the error.
- Prefer standard exceptions when they describe the problem well (`ValueError`, `TypeError`).

### `raise` with no arguments
```python
try:
    dividir(10, 0)
except ZeroDivisionError:
    raise  # re-raise the same exception
```

---

## 4. Custom exceptions

```python
class ConfigError(Exception):
    """Errores relacionados con la configuración."""

class MissingConfig(ConfigError):
    pass
```

```python
def cargar_config(path):
    if not path.exists():
        raise MissingConfig(f"No existe {path}")
    # ...
```

- Inheriting from `Exception` (or a relevant subclass) lets you distinguish your domain errors.
- Keep hierarchies small and descriptive.

---

## 5. Chaining (`raise ... from ...`)

```python
import json

class ConfigDecodeError(ConfigError):
    pass

try:
    config = json.loads(raw)
except json.JSONDecodeError as exc:
    raise ConfigDecodeError("Config inválida") from exc
```

- `from exc` keeps the original traceback, which makes debugging easier.

---

## 6. Context managers and cleanup

```python
class TemporaryFile:
    def __enter__(self):
        self.fh = open("temp.txt", "w")
        return self.fh

    def __exit__(self, exc_type, exc, tb):
        self.fh.close()
        if exc_type:
            print("Ocurrió un error", exc)
            return False  # Propagate the exception
```

- Custom context managers ensure cleanup even if an error happens inside `with`.

---

## 7. Testing exceptions

```python
import pytest

def test_dividir_zero():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)
```

- `pytest.raises` confirms the right exception is raised.
- Use `match="text"` to check the error message.

---

## Guided exercises (with TODOs)
1. **14-1 · Robust validator**
   ```python
   def validar_payload(data):
       # TODO 1: raise ValueError if "email" is missing
       # TODO 2: use try/except to normalize type errors
   ```
   *Hint*: `if "email" not in data: raise ValueError(...)`.

2. **14-2 · Resilient CLI**
   ```python
   # TODO 1: process files, catch FileNotFoundError and show a friendly message
   # TODO 2: use `sys.exit(1)` when it’s critical
   ```

3. **14-3 · Custom exception**
   ```python
   class InsufficientFunds(Exception):
       pass
   # TODO 1: implement withdraw(amount) that raises InsufficientFunds
   # TODO 2: handle the exception and print the remaining balance
   ```

---

## Common mistakes
- Catching exceptions that are too generic and hiding the real problem.
- Not re‑raising (`raise`) when you can’t solve the error.
- Ignoring `finally` and leaving resources open.
- Raising exceptions with vague messages; always include context.

---

## Explained solutions
1. **Robust validator**: `try: email = data["email"]` and `except KeyError as exc: raise ValueError("Falta email") from exc`. Friendly messages make debugging easier.
2. **Resilient CLI**: `try/except FileNotFoundError` prints which file failed and exits with code 1 so other scripts can detect it.
3. **Custom exception**: `withdraw` checks balance and raises `InsufficientFunds`; the top-level `try/except` informs the user without dumping a raw traceback.

---

## Summary
Understanding and controlling exceptions helps you write solid code: you choose what to handle, what to propagate, and how to communicate problems. Custom exceptions add meaning to your APIs.

## Closing reflection
Being a “hero” with exceptions means anticipating failures, designing clear messages, and not being afraid to raise errors when rules aren’t met. Keep practicing in your projects and you’ll notice your code becomes more reliable and easier to maintain.
