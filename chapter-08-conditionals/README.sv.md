# Kapitel 8 · Villkor, ternary och logik

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Vi tränar beslutslogik i Python: `if/elif/else`, `and/or/not`, ternary‑operatorn och en kort not om `match/case` (Python 3.10+).

---

## `if/elif/else`
```python
peso = 3.2

if peso <= 1:
    tarifa = 5
elif peso <= 5:
    tarifa = 10
else:
    tarifa = 20
```

---

## Truthy / falsy
Tom sträng `""`, `0`, `[]`, `{}` och `None` räknas som falsy.

---

## Ternary
```python
score = 75
estado = "aprobado" if score >= 60 else "recuperación"
```

---

## `match/case` (Python 3.10+)
Python har inte klassisk “switch”, men har `match/case` från 3.10.

---

## Sammanfattning
Villkor är grunden för affärsregler. Nästa kapitel: indata (`input`) och säker validering.
