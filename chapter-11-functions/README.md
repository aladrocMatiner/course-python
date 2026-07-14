# Chapter 11 · Functions, Responsibility, and Passing Functions

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll go deeper into functions: how to define them, document them, return multiple values, and treat functions as data. You’ll pass functions as arguments, store them in collections, and build small pipelines. The examples are backend-inspired (validation, serializers, hooks) and gradually introduce higher‑order functions.

## Learning path
1. **Review**: definition, arguments, return values.
2. **Single responsibility**: when to split into smaller functions.
3. **Default values and keyword arguments**.
4. **First-class functions**: store them in variables and collections.
5. **Functions as arguments**: callbacks, validators, custom filters.
6. **Functions returning functions** (closures).
7. **Light decorators** (conceptual intro).
8. **Tests and good practices**.

## Learning objectives
- Write well-named functions with short documentation.
- Understand positional args, keyword args, and default values.
- Pass functions as arguments and design extensible APIs.
- Understand closures and functions that return functions.
- Write tests for happy/error paths in higher‑order functions.

## Prerequisites and routes
You should be comfortable with [lists](../chapter-03-lists/README.md), [dictionaries](../chapter-04-dictionaries/README.md), [conditionals](../chapter-08-conditionals/README.md), and [loops](../chapter-10-loops/README.md). In particular, review iterating over a collection and returning a result after a condition is met.

- **Foundational route · 60–75 min:** the foundational section below, exercise 11-0, and the essential checkpoint. Outcome: define and call a function, use positional/keyword/default arguments, distinguish a returned value from implicit `None`, explain local scope, and recover from an invalid call. It requires no `Callable`, closure, decorator, pytest, or timing API.
- **Intermediate route · 35–45 min:** sections 1–2 after the foundational checkpoint. Outcome: document one responsibility, add Python 3.11 type hints, return multiple values, and use a safe optional default.
- **Optional advanced route · 75–110 min:** sections 3–7 and exercises 11-1 to 11-3. Outcome: build and explain a higher-order pipeline with callbacks, closures, and a light decorator. Section 7 previews [testing with pytest](../chapter-18-testing/README.md); copy it or skip it on a first pass.

## Why it matters
Smaller, clearer functions reduce errors and increase reuse. In backend work, passing functions as arguments (validators, transformers) lets you build customizable components without duplicating code.

### Mini adventure
A function is like a recipe: if you write it well, you can cook the dish whenever you want without rethinking every step. And if someone else reads it, they can cook it too. Good recipes save time and prevent accidents.

## Prediction warm-up
Without running code, predict `describir_tarea(" backup ")` and `describir_tarea(nombre="deploy", prioridad="high")` in the foundational example. Identify each argument, the default used, and the value returned to the caller. The earlier pipeline prediction belongs to the optional advanced route.

---

## Foundational route: calls, return values, scope, and safe defaults
A function call has a visible flow: arguments enter through parameters, the body runs, and `return` sends one value back to the caller. If execution reaches the end without `return`, Python returns `None`.

```python runnable
def describir_tarea(nombre, prioridad="normal"):
    etiqueta = nombre.strip()
    return f"{etiqueta}: {prioridad}"

print(describir_tarea(" backup "))
print(describir_tarea(nombre="deploy", prioridad="high"))
```

The first call is positional and uses the default. The second names both arguments. `etiqueta` is local: it exists only while that call runs.

```python runnable
def anunciar(mensaje):
    print(mensaje)

resultado = anunciar("ready")
print(resultado is None)
```

Printing is an effect; it is not a returned value. The final line observes the implicit `None`.

Use `None` as the sentinel for an optional list, then create the list inside the call. This avoids sharing one mutable default between calls:

```python runnable
def registrar(mensaje, historial=None):
    if historial is None:
        historial = []
    historial.append(mensaje)
    return historial

primero = registrar("start")
segundo = registrar("stop")
print(primero, segundo)
```

An invalid call is useful evidence. This block intentionally omits the required argument; the stable diagnostic signal is `TypeError`:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
def saludar(nombre):
    return f"Hola, {nombre}"

saludar()
```

Recover by matching the call to the signature and rerun it:

```python runnable
def saludar(nombre):
    return f"Hola, {nombre}"

print(saludar("Noor"))
```

Verify foundations with direct calls and printed values. Automated tests arrive in Chapter 18; they are not a hidden prerequisite here.

---

## 1. Defining and documenting functions

```python runnable
def calcular_total(items):
    """Suma los precios en una lista de items."""
    total = 0
    for item in items:
        total += item
    return total
```

- Use verb names (`calcular_total`).
- A short docstring explains what it does and what it expects.

### Types and multiple returns
```python runnable
def resumen_pedidos(pedidos: list[int]) -> tuple[int, float]:
    cantidad = len(pedidos)
    total = sum(pedidos)
    promedio = total / cantidad if cantidad else 0
    return cantidad, promedio
```

---

## 2. Default values and keyword arguments

```python runnable
def aplicar_descuento(total, porcentaje=0.1):
    return total * (1 - porcentaje)

print(aplicar_descuento(100))      # usa 10%
print(aplicar_descuento(100, 0.2)) # 20%
```

- Use keywords for clarity: `aplicar_descuento(total=100, porcentaje=0.15)`.
- Avoid mutable defaults (lists, dicts).

---

## 3. Functions as first-class citizens
Functions can be stored and passed like any other value.

```python runnable
def notificar_email(mensaje):
    print(f"Email: {mensaje}")

def notificar_sms(mensaje):
    print(f"SMS: {mensaje}")

canales = [notificar_email, notificar_sms]
for canal in canales:
    canal("Deploy completado")
```

- Each function shares the same “shape” (same signature).
- This pattern appears in hooks and event systems.

---

## 4. Passing functions as arguments

```python runnable
def procesar_items(items, transformacion):
    return [transformacion(item) for item in items]

procesar_items(["noor", "frej"], str.upper)  # ['NOOR', 'FREJ']
```

- `transformacion` is a function. You can pass built-ins (`str.upper`) or your own functions.
- Document what you expect (`Callable[[str], str]`) in real projects.

### Customizable validators
```python runnable
from typing import Callable

def guardar_usuario(data, validador: Callable[[dict], None]):
    validador(data)
    print("Guardado", data)

def validar_email(data):
    if "@" not in data["email"]:
        raise ValueError("Invalid email")

payload = {"email": "noor@example.com"}
guardar_usuario(payload, validar_email)
```

---

## 5. Functions that return functions (closures)

```python runnable
def crear_multiplicador(factor):
    def multiplicar(valor):
        return valor * factor
    return multiplicar

duplicar = crear_multiplicador(2)
print(duplicar(10))  # 20
```

- `multiplicar` “remembers” `factor` even after `crear_multiplicador` ends.
- Useful for configurable behavior (for example, creating custom filters).

### Backend-style example
```python runnable
def crear_validador_longitud(minimo):
    def validar(texto):
        if len(texto) < minimo:
            raise ValueError("Muy corto")
        return texto
    return validar

validar_usuario = crear_validador_longitud(3)
validar_usuario("api")  # OK
```

---

## 6. Light decorators (big picture)

```python runnable
import functools

def loggear(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Ejecutando {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@loggear
def procesar():
    print("Procesando...")
```

- `@loggear` applies the decorator function.
- `functools.wraps` keeps the original name and docstring.
- Use decorators for cross-cutting concerns (logging, permissions).

---

## 7. Testing higher‑order functions

```python runnable
# pipelines.py
def aplicar_pipeline(valor, etapas):
    for etapa in etapas:
        valor = etapa(valor)
    return valor
```

```python illustrative
# tests/test_pipelines.py
from pipelines import aplicar_pipeline

def test_aplicar_pipeline():
    etapas = [str.strip, str.upper]
    resultado = aplicar_pipeline("  hola  ", etapas)
    assert resultado == "HOLA"
```

- Tests confirm order matters and every step is applied.

---

## Guided exercises (with TODOs)
0. **11-0 · Foundational label function**
   ```python todo
   def crear_etiqueta(nombre, prefijo="user"):
       # TODO 1: strip surrounding whitespace from nombre into a local variable
       # TODO 2: return "prefijo:nombre_limpio"
       pass

   # TODO 3: call it once positionally and once with keyword arguments
   # TODO 4: print both returned values and try the empty-string boundary
   ```
   *Hint*: the essential success condition is observable with `print`; no callback, closure, decorator, pytest, or timer is needed.

Exercises 11-1 to 11-3 belong to the optional advanced route.

1. **11-1 · Flexible converter**
   ```python todo
   # TODO 1: create convertir(items, funcion)
   # TODO 2: pass str.upper, then a function that adds a prefix
   # TODO 3: validate it raises if funcion is not callable
   ```
   *Hint*: `callable(funcion)` returns True/False.

2. **11-2 · Chained validators**
   ```python todo
   def validar_no_vacio(texto):
       # TODO: raise ValueError if texto is empty
       pass

   def validar_minimo(texto):
       # TODO: raise ValueError if len(texto) is less than a minimum
       pass
   # TODO 1: create run_validators(texto, validadores)
   # TODO 2: stop at the first error and re-raise it
   # TODO 3: add pytest tests
   ```

3. **11-3 · Simple decorator**
   ```python todo
   # TODO 1: write decorator measure_time(func)
   # TODO 2: print how long it took to run
   # TODO 3: use it on a loop-heavy function to demonstrate
   ```
   *Hint*: `time.perf_counter()` for timing.

---

## Common mistakes
- Using mutable defaults (`def foo(items=[])`). Better: use `None` and create the list inside.
- Forgetting `return` in functions that transform data.
- Not documenting expected function signatures when passing callbacks ⇒ incompatible calls.
- Reusing closures without understanding what they capture ⇒ surprising values.

---

## Explained solutions
### Foundational solution 11-0
The local `nombre_limpio` belongs to one call, the default is used only when `prefijo` is omitted, and the caller receives the string after `return`.

```python runnable
def crear_etiqueta(nombre, prefijo="user"):
    nombre_limpio = nombre.strip()
    return f"{prefijo}:{nombre_limpio}"

print(crear_etiqueta(" Noor "))
print(crear_etiqueta(nombre="Frej", prefijo="admin"))
print(crear_etiqueta(""))
```

The empty string is a boundary, not a hidden crash. A program that must reject it can add that policy later; this exercise checks call and return mechanics first. The invalid-call `TypeError` and successful recovery are executed in the foundational section above.

1. **Flexible converter**: `convertir(items, funcion)` loops and applies the function; first check `if not callable(funcion): raise TypeError`. It lets you combine built-ins with custom functions.
2. **Chained validators**: `run_validators` loops over validator functions; if one raises `ValueError`, it stops — similar to validation flow in Django serializers.
3. **Simple decorator**: `measure_time` wraps the original function, measures before/after, and prints the result. Great for seeing the impact of loops or pipelines.

---

## Checkpoint and rubric
Build `crear_etiqueta(nombre, prefijo="user")`, call it positionally and with keywords, and verify normal, empty-name, and missing-argument behavior. Add a separate `mostrar(mensaje)` with no `return` and explain why its caller observes `None`. Do not use callbacks, closures, decorators, pytest, or a timing API.

Score one point for **signature and calls**, **correct returned values**, **safe default**, **documented `TypeError` recovery**, and **explanation of local scope versus implicit `None`**. A score of 4/5 completes the foundational route and prepares you for the essential route in Chapter 12. The previous pipeline checkpoint is available as the optional advanced-route challenge.

---

## Summary
Functions are reusable blocks with clear responsibilities. When you treat them as data, you can build pipelines, configurable validators, and decorators that add behavior without duplicating logic.

## Closing reflection
Knowing how to define, combine, and pass functions lets you design flexible, expressive APIs. These skills are essential in frameworks like Django, where functions connect to form views, middleware, and signals.
