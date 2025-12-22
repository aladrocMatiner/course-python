# Kapitel 2 · Variabler och enkla datatyper

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Du lär dig grunderna: vad som händer när du kör en `.py`‑fil, hur variabler fungerar, hur du jobbar med strängar och tal, och hur du skriver bra kommentarer. Vi tittar också på hur du kan se vilken typ en variabel har, och hur du kan testa att en funktion får rätt data.

## Mål
- Förstå att variabler är “etiketter” som pekar på värden.
- Lära dig `str`, `int`, `float` och vanliga strängmetoder.
- Kolla typer med `type()` och `isinstance()`.
- Skriva små tester med `pytest`.

---

## 1. Vad händer när du kör `hello_world.py`?
```python
# hello_world.py
print("Hello Python world!")
```

---

## 2. Variabler som etiketter
```python
message = "Hello Python world!"
print(message)

message = "Hello Python Crash Course world!"
print(message)
```

---

## 3. Kolla typen på en variabel
```python
username = "ada"
age = 28
temperature = 20.5

print(type(username))          # <class 'str'>
print(type(age))               # <class 'int'>
print(isinstance(age, int))    # True
print(isinstance(temperature, float))  # True
print(isinstance(age, (int, float)))   # True
```

---

## 4. Validera argument i en funktion
```python
def calcular_area_rectangulo(base, altura):
    if not isinstance(base, (int, float)):
        raise TypeError("base debe ser numérica")
    if not isinstance(altura, (int, float)):
        raise TypeError("altura debe ser numérica")
    if base <= 0 or altura <= 0:
        raise ValueError("las dimensiones deben ser positivas")

    return base * altura
```

---

## 5. Testa med pytest
```python
# tests/test_rectangulos.py
import pytest
from area import calcular_area_rectangulo

def test_calcular_area_rectangulo_valores_validos():
    assert calcular_area_rectangulo(3, 4) == 12

def test_calcular_area_rectangulo_rechaza_strings():
    with pytest.raises(TypeError):
        calcular_area_rectangulo("10", 5)

def test_calcular_area_rectangulo_rechaza_negativos():
    with pytest.raises(ValueError):
        calcular_area_rectangulo(-1, 2)
```

---

## Strängar (strings) i korthet
```python
name = "ada lovelace"
print(name.title())
print(name.upper())
print(name.lower())
```

```python
first_name = "ada"
last_name = "lovelace"
full_name = f"{first_name} {last_name}"
print(f"Hello, {full_name.title()}!")
```

---

## Sammanfattning
Nu kan du använda variabler tryggt, jobba med strängar och tal, kolla typer och skriva små tester. Nästa kapitel: listor.
