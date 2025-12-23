# Kapitel 3 · Listor

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Du lär dig vad en lista är, hur du hämtar element med index, och hur du lägger till, tar bort och sorterar. Vi gör också små tester så att våra funktioner beter sig som vi vill.

## Nyckelidéer
- Index börjar på 0.
- `-1` betyder “sista elementet”.
- Vanliga metoder: `append`, `insert`, `pop`, `remove`, `sort`.
- Undvik `IndexError` genom att kolla `len()`.

---

## Exempel: skapa och läsa en lista
```python
bicycles = ["trek", "cannondale", "redline", "specialized"]
print(bicycles[0])
print(bicycles[-1])
```

Exempel med personer:
```python
names = ["Noor", "Frej", "Taha"]
print(names[0])
print(f"Hej, {names[1]}!")
```

---

## Lägga till och ta bort
```python
motorcycles = ["honda", "yamaha", "suzuki"]
motorcycles.append("ducati")
motorcycles.insert(0, "victory")

last = motorcycles.pop()
motorcycles.remove("yamaha")
```

---

## Sortera
```python
cars = ["bmw", "audi", "toyota", "subaru"]
print(sorted(cars))
cars.sort(reverse=True)
```

---

## Mini‑test (idé)
```python
import pytest

def prioritize_task(tasks, new_task):
    if not isinstance(tasks, list):
        raise TypeError("tasks must be a list")
    copy = tasks[:]
    copy.insert(0, new_task)
    return copy

def test_prioritize_task():
    assert prioritize_task(["a", "b"], "x")[0] == "x"
```

---

## Sammanfattning
Listor hjälper dig hantera många värden i ordning. Nästa kapitel: dictionaries (nyckel‑värde).
