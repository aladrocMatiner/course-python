# Kapitel 6 · Tuples och immutabilitet

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Tuples (`tuple`) är lätta, ordnade och (oftast) immutabla. De passar bra för koordinater, flera returvärden och som nycklar i dictionaries.

---

## Lista vs tuple
```python
punto_lista = [10, 20]
punto_tupla = (10, 20)

punto_lista[0] = 99
# punto_tupla[0] = 99  # TypeError
```

---

## Unpacking
```python
coordenada = (41.40338, 2.17403)
latitud, longitud = coordenada
```

---

## Flera returvärden
```python
def dividir_y_residuo(dividendo, divisor):
    if divisor == 0:
        raise ZeroDivisionError("Divisor no puede ser cero")
    return dividendo // divisor, dividendo % divisor
```

---

## Sammanfattning
Tuples signalerar “ändra inte” och gör det lätt att returnera flera värden. Nästa kapitel: köer och stackar med `deque`.
