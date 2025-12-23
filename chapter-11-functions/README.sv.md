# Kapitel 11 · Funktioner och funktioner som argument

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Vi går djupare i funktioner: tydliga namn, docstrings, default‑argument, och att funktioner i Python är “förstklassiga” (du kan skicka dem som argument, lägga dem i listor och bygga pipelines).

---

## Enkel funktion
```python
def calcular_total(items):
    """Suma los precios en una lista de items."""
    total = 0
    for item in items:
        total += item
    return total
```

---

## Funktion som argument
```python
def procesar_items(items, transformacion):
    return [transformacion(item) for item in items]

procesar_items(["noor", "frej"], str.upper)
```

---

## Funktion som returnerar funktion (closure)
```python
def crear_multiplicador(factor):
    def multiplicar(valor):
        return valor * factor
    return multiplicar
```

---

## Sammanfattning
Du kan bygga flexibla API:er genom att skicka funktioner. Nästa kapitel: objekt och klasser (OOP).
