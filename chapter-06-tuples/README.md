# Chapter 6 · Tuples and Practical Immutability

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll see how tuples help represent lightweight records, multiple return values, and immutable keys. We’ll work with coordinates, function results, and small structures that should not change after they are created.

## Learning path
1. **Mental model**: the difference between lists and tuples.
2. **Create and access**: literals, `tuple()` and unpacking.
3. **Multiple returns**: functions that return more than one piece of information.
4. **Tuples as keys**: dictionaries that use tuples to index compound data.
5. **`namedtuple` (and lightweight “data objects”)** to improve readability.
6. **Validation and tests**: guaranteeing critical data can’t be modified.

## Learning objectives
- Create tuples to represent data that should not mutate.
- Unpack tuples into variables and use `_` for values you don’t need.
- Return multiple values from a function without creating full classes.
- Use tuples as dictionary keys or set elements.
- Write tests that confirm immutability and expected structure.

## Why it matters
In many APIs you need to group data briefly (coordinates, date ranges, status pairs). Tuples are lighter than lists and communicate “don’t change these values”, which prevents bugs in pipelines, caches, and compound keys.

### Mini adventure
A tuple is like writing a coordinate on a map with permanent ink. It helps you remember “this exact point”. If someone changes it by accident, the map breaks — so a tuple protects those values.

---

## 1. Mental model: list vs tuple

```python
punto_lista = [10, 20]
punto_tupla = (10, 20)

punto_lista[0] = 99      # ✔ se puede mutar
# punto_tupla[0] = 99    # ✘ TypeError: las tuplas son inmutables
```

- Use tuples when you want a clear “read-only” signal.
- Immutability lets tuples be dictionary keys or set elements.

---

## 2. Creating and unpacking

```python
coordenada = (41.40338, 2.17403)
latitud, longitud = coordenada
print(latitud, longitud)

horas = tuple(range(0, 24))
print(horas[:3])
```

```python
registro = ("Ada", "Lovelace", 1815)
nombre, apellido, _ = registro  # ignora el año con _
print(nombre, apellido)
```

- Unpacking improves readability and avoids “magic indexes”.
- Use `_` for values you intentionally ignore.

---

## 3. Returning multiple values

```python
def dividir_y_residuo(dividendo, divisor):
    if divisor == 0:
        raise ZeroDivisionError("Divisor no puede ser cero")
    return dividendo // divisor, dividendo % divisor

cociente, residuo = dividir_y_residuo(10, 3)
print(cociente, residuo)
```

- This is clearer than returning a dictionary when you only need an ordered pair.
- Document the return order to avoid confusion.

---

## 4. Tuples as dictionary keys

```python
coordenadas_ciudad = {
    (41.3874, 2.1686): "Barcelona",
    (40.4168, -3.7038): "Madrid",
}

print(coordenadas_ciudad.get((41.3874, 2.1686)))
```

```python
cache_respuestas = {}

parametros = ("/api/report", "POST", frozenset({("team", "analytics")}))
cache_respuestas[parametros] = {"status": 200, "body": "OK"}
```

- Pack meaningful arguments into tuples to create stable cache keys.
- Mixing tuples with `frozenset` lets you include parameters in any order without breaking the key.

---

## 5. `namedtuple` to add meaning

```python
from collections import namedtuple

Coordenada = namedtuple("Coordenada", ["lat", "lon"])
punto = Coordenada(lat=41.4, lon=2.17)
print(punto.lat)
```

- You get the benefits of tuples (immutable, lightweight) plus name-based access.
- Useful for returning self-documenting structures from functions or services.

---

## 6. Validation and tests

```python
# ranges.py
from typing import Tuple

Hora = Tuple[int, int]

def validar_intervalo(intervalo: Hora) -> bool:
    inicio, fin = intervalo
    if not (0 <= inicio < 24 and 0 <= fin < 24):
        raise ValueError("Horas fuera de rango")
    if inicio >= fin:
        raise ValueError("El inicio debe ser menor que el fin")
    return True
```

```python
# tests/test_ranges.py
import pytest
from ranges import validar_intervalo

def test_validar_intervalo_correcto():
    assert validar_intervalo((9, 17)) is True

def test_validar_intervalo_rechaza_valores_invalidos():
    with pytest.raises(ValueError):
        validar_intervalo((20, 8))
```

---

## Guided exercises (with TODOs)
1. **6-1 · Immutable coordinates**
   ```python
   ubicaciones = [
       ("HQ", (41.0, 2.0)),
       ("DataCenter", (40.4, -3.7)),
   ]
   # TODO 1: iterate and print name + lat/lon
   # TODO 2: try to modify a coordinate to see the exception
   # TODO 3: create a dict that uses coordinates as keys
   ```
   *Hint*: catch the exception and explain why immutability protects data.

2. **6-2 · Time ranges**
   ```python
   rangos = [(9, 12), (13, 17)]
   # TODO 1: write total_horas(rangos) that sums each interval
   # TODO 2: validate that no range is reversed
   # TODO 3: add a test for the reversed range
   ```
   *Hint*: reuse `validar_intervalo` or create a similar helper.

3. **6-3 · namedtuple for metrics**
   ```python
   from collections import namedtuple
   Punto = namedtuple("Punto", ["x", "y", "label"])
   muestras = [Punto(1, 2, "ok"), Punto(3, 5, "alert")]
   # TODO 1: count how many samples have label "alert"
   # TODO 2: convert each namedtuple into dict using _asdict()
   # TODO 3: create a test that confirms Punto is immutable
   ```
   *Hint*: `pytest.raises(AttributeError)` when trying to reassign `muestras[0].x`.

---

## Common mistakes
- **Forgetting the comma in single-item tuples**: `(42)` is an int; use `(42,)`.
- **Trying to modify a tuple**: it raises `TypeError`. Convert to a list if you truly need changes.
- **Not documenting return order**: causes subtle bugs when values are swapped.
- **Using giant tuples**: if you need many fields, consider dataclasses or a more expressive object.

---

## Explained solutions
1. **Immutable coordinates**: if you try `ubicaciones[0][1][0] = 0`, you’ll get `TypeError`. When you use coordinates as keys (`ciudades[ubicaciones[0][1]] = ...`), you guarantee the location can’t be corrupted.
2. **Time ranges**: `total_horas` sums `fin - inicio` after validating each tuple; a test with `(15, 10)` confirms validation works.
3. **namedtuple for metrics**: `_asdict()` converts each point into a dict for serialization; the test tries `muestras[0].x = 99` and expects `AttributeError`, proving immutability.

---

## Summary
Tuples let you package immutable data, return multiple values without complex classes, and build compound keys for caches or dictionaries. They’re ideal when you want lightweight structure and protection from accidental changes.

## Closing reflection
Now you can choose when to use tuples (or `namedtuple`) to communicate meaning and protect your data. Next we’ll continue with efficient queues, where `collections.deque` helps us model workflows and sliding windows.
