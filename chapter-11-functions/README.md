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

## Prerequisites and optional preview
You should be comfortable with [lists](../chapter-03-lists/README.md), [dictionaries](../chapter-04-dictionaries/README.md), [conditionals](../chapter-08-conditionals/README.md), and [loops](../chapter-10-loops/README.md). In particular, review iterating over a collection and returning a result after a condition is met.

Section 7 previews [testing with pytest](../chapter-18-testing/README.md). It is optional on a first pass: for now, read each `assert` as “this result must equal the expected value.”

## Why it matters
Smaller, clearer functions reduce errors and increase reuse. In backend work, passing functions as arguments (validators, transformers) lets you build customizable components without duplicating code.

### Mini adventure
A function is like a recipe: if you write it well, you can cook the dish whenever you want without rethinking every step. And if someone else reads it, they can cook it too. Good recipes save time and prevent accidents.

## Prediction warm-up
Without running code, predict the result of `procesar_items(["noor", "frej"], str.upper)`. Explain why the argument is `str.upper` rather than `str.upper()`, then predict whether swapping `[str.strip, str.upper]` to `[str.upper, str.strip]` changes the pipeline’s result for `"  hola  "`. Verify each prediction and name the value passed between stages.

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
from typing import List, Tuple
def resumen_pedidos(pedidos: List[int]) -> Tuple[int, float]:
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
1. **Flexible converter**: `convertir(items, funcion)` loops and applies the function; first check `if not callable(funcion): raise TypeError`. It lets you combine built-ins with custom functions.
2. **Chained validators**: `run_validators` loops over validator functions; if one raises `ValueError`, it stops — similar to validation flow in Django serializers.
3. **Simple decorator**: `measure_time` wraps the original function, measures before/after, and prints the result. Great for seeing the impact of loops or pipelines.

---

## Checkpoint and rubric
Build `normalizar_registros(registros, transformadores)` so each dictionary passes through every transformer in order without mutating the input list. Reject a non-callable transformer with `TypeError`, and test an empty pipeline, two ordered stages, and the error path.

Score one point for each criterion: **contract** (inputs, output, and errors are explicit), **correctness** (stage order and all cases work), **responsibility** (the function stays focused), **verification** (tests cover success and failure), and **explanation** (you can distinguish passing a function from calling it). A score of 4/5 means you are ready for classes; otherwise revisit sections 3, 4, and 7.

---

## Summary
Functions are reusable blocks with clear responsibilities. When you treat them as data, you can build pipelines, configurable validators, and decorators that add behavior without duplicating logic.

## Closing reflection
Knowing how to define, combine, and pass functions lets you design flexible, expressive APIs. These skills are essential in frameworks like Django, where functions connect to form views, middleware, and signals.
