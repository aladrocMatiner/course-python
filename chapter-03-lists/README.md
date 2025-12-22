# Chapter 3 · Introducing Lists

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
In this chapter you’ll learn what a list is, how to access each element, and how to change, sort, and protect your code from common mistakes. We’ll practice the essential methods (`append`, `insert`, `pop`, `remove`, `sort`) and write tiny tests to guarantee our functions behave the way we expect.

## Learning path
1. **Intro**: a mental model of a list and why square brackets (`[]`) matter.
2. **Access and use**: indexes, `-1` for the end, and reusing values in messages.
3. **Modify/add/remove**: `append`, `insert`, `del`, `pop`, `remove` and when to choose each.
4. **Organize**: `sort`, `sorted`, `reverse`, `len` and quick checks.
5. **Avoid errors**: spotting `IndexError` and preventing it.
6. **Tests and guided exercises** to make list work safe.

## Learning objectives
- Define a list and access elements by position, including negative indexes.
- Modify existing items and add/remove items depending on your program’s needs.
- Reorder lists temporarily or permanently and measure their length.
- Avoid `IndexError` by validating indexes and using `len()` and `-1` correctly.
- Write small tests that confirm list functions don’t create unwanted side effects.

## Why it matters
Without lists, you can only hold one value per variable. Lists let you store catalogs, users, orders, or readings in one ordered, dynamic container. Mastering these patterns opens the door to processing hundreds or thousands of elements with just a few methods and loops.

### Mini adventure
Think of a list like a backpack with numbered pockets. You can put things in, take them out, move them around, and count how many you have. When you program, that backpack lets you carry “many similar things” without going crazy creating one variable per item.

---

## What is a list?
A list is an ordered collection of items. In Python you create it with square brackets `[]`, and items are separated with commas.

```python
# bicycles.py
bicycles = ["trek", "cannondale", "redline", "specialized"]
print(bicycles)
```

Output:
```
['trek', 'cannondale', 'redline', 'specialized']
```
Python prints the literal representation, but usually you want to access each item.

### Accessing elements in a list
Use the index (position) inside brackets to get one element:

```python
print(bicycles[0])
print(bicycles[0].title())
```

### Indexes start at 0
The first element is index `0`, the second is `1`, etc. The fourth element is `bicycles[3]`. Negative indexes count from the end (`-1` is last, `-2` is second-to-last).

### Using individual values from a list
You can place list items inside messages using f-strings:

```python
message = f"Mi primera bicicleta fue una {bicycles[0].title()}."
print(message)
```

### Try it yourself (3-1 to 3-3)
1. **3-1 · Names**: create a `names` list with friends and print each name one by one.
2. **3-2 · Greetings**: reuse the list but print a personalized greeting for each person.
3. **3-3 · Your own list**: create a list of your favorite transport and generate sentences like “I would like to own a …”.

---

## Modifying, adding, and removing elements
Lists are dynamic: you can change them as your program runs.

### Modifying elements in a list
```python
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles)

motorcycles[0] = 'ducati'
print(motorcycles)
```

### Appending elements
```python
motorcycles.append('ducati')
print(motorcycles)

# Build from scratch
equipos = []
equipos.append('frontend')
equipos.append('backend')
print(equipos)
```

### Inserting elements
```python
motorcycles.insert(0, 'victory')
print(motorcycles)
```

### Removing elements
- `del lista[i]` removes by position (does not return the value).
- `pop()` removes and returns the last item (or an optional index).
- `remove(valor)` finds and removes the first item equal to `valor`.

```python
motorcycles = ['honda', 'yamaha', 'suzuki', 'ducati']

ultimo = motorcycles.pop()
print(f"Último: {ultimo}")

primero = motorcycles.pop(0)
print(f"Primero: {primero}")

motorcycles.remove('yamaha')
print(motorcycles)
```

> Note: `remove` only deletes the first match. If you need to remove all of them, you’ll use loops later.

### Try it yourself (3-4 to 3-7)
1. **3-4 · Guest List**: make a list of guests and print personalized invitations.
2. **3-5 · Changing Guest List**: replace a guest who can’t come and reprint invitations.
3. **3-6 · More Guests**: announce a bigger table; use `insert` and `append` to add three more people.
4. **3-7 · Shrinking Guest List**: reduce to two people using `pop`; thank them and delete the rest with `del`.

---

## Organizing a list
When data arrives in an unpredictable order, you often want to show it sorted without destroying the original order.

### Sorting permanently with `sort()`
```python
cars = ['bmw', 'audi', 'toyota', 'subaru']
cars.sort()
print(cars)  # ['audi', 'bmw', 'subaru', 'toyota']
```
`cars.sort(reverse=True)` reverses alphabetic order and modifies the list in place.

### Sorting temporarily with `sorted()`
```python
print(sorted(cars))          # sorted copy
print(sorted(cars, reverse=True))
print(cars)                  # the original list did not change
```

### Printing a list in reverse order
```python
cars.reverse()
print(cars)
```
`reverse()` flips the current order (it does not “sort backwards”), and you can undo it by calling it again.

### Finding the length of a list
```python
print(len(cars))
```
Length helps you validate indexes and show “how many items” you have (guests, remaining entries, etc.).

### Try it yourself (3-8 to 3-10)
1. **3-8 · Seeing the World**: create a list of places and practice `sorted`, `reverse`, `sort` and `len` without losing the original order.
2. **3-9 · Dinner Guests**: using exercises 3-4 to 3-7, print how many people you’re inviting with `len()`.
3. **3-10 · Every function**: pick any list (mountains, cities, etc.) and use each method from this chapter at least once.

---

## Avoiding `IndexError` when working with lists
The most common error is asking for an out-of-range index:

```python
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles[3])  # IndexError
```

Tips to prevent it:
- Check the length before accessing (`if len(motorcycles) > 2:`).
- Use `-1` for the last item and don’t assume the size.
- If you remove items while iterating, loop over a copy (`for item in lista[:]`).
- If your function receives an external index, validate it:
  ```python
  def obtener_elemento(lista, posicion):
      if not 0 <= posicion < len(lista):
          raise IndexError("posición fuera de rango")
      return lista[posicion]
  ```
- If you hit an `IndexError`, print the list (or `len(lista)`) to confirm its real state.

### Try it yourself (3-11)
Trigger an `IndexError` on purpose by changing a valid index to an invalid one, then fix it. You’ll understand Python’s debugging flow much better.

---

## Mini automated tests
```python
# lists_utils.py
def priorizar_tarea(tareas, nueva):
    if not isinstance(tareas, list):
        raise TypeError("tareas debe ser una lista")
    copia = tareas[:]
    copia.insert(0, nueva)
    return copia

# tests/test_lists_utils.py
import pytest
from lists_utils import priorizar_tarea

def test_priorizar_tarea_agrega_al_inicio():
    original = ["documentar", "refactorizar"]
    resultado = priorizar_tarea(original, "configurar CI")
    assert resultado[0] == "configurar CI"
    assert original[0] == "documentar"  # la copia protege la lista original

def test_priorizar_tarea_rechaza_no_listas():
    with pytest.raises(TypeError):
        priorizar_tarea("no-lista", "algo")
```

---

## Progressive examples: playing with interesting angles
These examples ramp up difficulty to show how lists behave in real backend-ish situations.

### Example 1 · Interactive checklist
```python
checklist = ["Crear entorno virtual", "Instalar dependencias", "Correr pruebas"]

for paso in checklist:
    print(f"- [ ] {paso}")

print(f"La checklist tiene {len(checklist)} pasos.")
ultimo = checklist.pop()            # Recuperamos el último paso
print(f"Último paso completado: {ultimo}")
checklist.append("Publicar release")  # Añade una nueva tarea al final
```
- You practice direct access, `len()`, and basic mutations (`pop`, `append`).
- Useful for CLI scripts where the steps change while the program runs.

### Example 2 · Support queue (list as queue)
```python
cola_tickets = ["BUG-101", "BUG-102", "BUG-103"]

def atender_ticket(cola):
    if not cola:
        return None
    return cola.pop(0)  # pop(0) simula una cola FIFO

def registrar_ticket(cola, ticket):
    cola.append(ticket)

ticket_actual = atender_ticket(cola_tickets)
print(f"Atendiendo: {ticket_actual}")
registrar_ticket(cola_tickets, "BUG-200")
print(f"Pendientes: {cola_tickets}")
```
- `pop(0)` has a higher cost, but it makes FIFO behavior clear; later you can swap in `collections.deque`.
- These methods are ready to plug into a Django view or a webhook without storage yet.

### Example 3 · Readings normalizer (validation + tests)
```python
def normalizar_lecturas(lecturas, *, limite_maximo):
    if not isinstance(lecturas, list):
        raise TypeError("lecturas debe ser lista")
    if not all(isinstance(valor, (int, float)) for valor in lecturas):
        raise ValueError("todas las lecturas deben ser numéricas")
    if not lecturas:
        return {"promedio": 0, "fuera_de_rango": []}

    fuera = [valor for valor in lecturas if valor > limite_maximo]
    promedio = sum(lecturas) / len(lecturas)
    top3 = sorted(lecturas, reverse=True)[:3]
    return {"promedio": promedio, "fuera_de_rango": fuera, "top3": top3}
```

```python
# tests/test_normalizador.py
import pytest
from normalizador import normalizar_lecturas

def test_normalizar_lecturas_detecta_excesos():
    datos = [19.2, 20.1, 22.5, 18.0]
    resultado = normalizar_lecturas(datos, limite_maximo=20)
    assert resultado["fuera_de_rango"] == [22.5]
    assert resultado["top3"][0] == 22.5

def test_normalizar_lecturas_valida_tipos():
    with pytest.raises(ValueError):
        normalizar_lecturas([10, "no-num"], limite_maximo=50)
```
- Combines slicing (`[:3]`), sorting, and strong validation before you put it behind an API.
- Notice how the tests describe the interesting angles: outliers and correct error signaling.

---

## Guided exercises (with TODOs)
1. **G3-1 · Dynamic invitations**
   ```python
   invitados = ["Ana", "Luis", "Marta"]
   # TODO 1: print a personalized message for each guest
   # TODO 2: add two new people at the end using append
   # TODO 3: remove the second guest and print who won’t attend
   ```
   *Hint*: `append`, `pop`, and a `for` loop are enough.

2. **G3-2 · Price list**
   ```python
   precios = [12.5, 9.99, 3.5, 18.0]
   # TODO 1: compute the average with sum/len
   # TODO 2: create a list of prices with VAT (21%)
   # TODO 3: use slicing to show only the two highest prices
   ```
   *Hint*: combine `sorted(precios)` and `[-2:]`.

3. **G3-3 · Sensors and validations**
   ```python
   lecturas = [19.2, 20.1, 21.3, 18.9]
   # TODO 1: write function fuera_de_rango(lecturas, limite)
   # TODO 2: add a test that confirms False when all are in range
   # TODO 3: test that it raises TypeError if lecturas is not a list
   ```
   *Hint*: use `any(valor > limite for valor in lecturas)` and the test pattern above.

---

## Common mistakes
- Starting to count from 1 and getting `IndexError`.
- Modifying a list while iterating without copying first.
- Confusing `append` (adds the list as a single element) with `extend`.
- Changing the original order with `sort()` when you needed a sorted copy (`sorted`).
- Forgetting that `remove` only removes the first occurrence.

---

## Explained solutions for the guided exercises
1. **G3-1**: generate messages with a `for` loop, `append` adds guests, and `pop(1)` returns who was removed so you can announce it.
2. **G3-2**: average is `sum(precios)/len(precios)`; VAT list is `[precio * 1.21 for precio in precios]`; top two come from `sorted(precios)[-2:]`.
3. **G3-3**: `any(valor > limite for valor in lecturas)` detects out-of-range values after `isinstance(lecturas, list)`; tests cover the happy path and type errors.

---

## Summary
In this chapter you defined lists, accessed elements with positive and negative indexes, reused values inside strings, modified the list in real time (add, insert, remove), sorted it permanently or temporarily, and used `len()` and `reverse()` to inspect it. You also learned how to avoid `IndexError` and even wrote tests to validate these operations.

## Closing reflection
Mastering lists means handling whole collections of data with just a few lines: you can add, remove, slice, sort, and validate information without duplicating code. In the next chapter we’ll move on to structures that pair *keys* with *values* (dictionaries), which is the foundation of JSON and APIs.
