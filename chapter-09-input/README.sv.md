# Kapitel 9 · Indata och säker validering

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Du lär dig läsa in data från `input()`, kommandoradsargument och enkla filer — och alltid validera och konvertera innan du använder värdena.

---

## Allt kommer som text
```python
nombre = input("¿Cómo te llamas? ")
print(f"Hola, {nombre}")
```

---

## Konvertering + felhantering
```python
raw_age = input("Edad: ")
try:
    edad = int(raw_age)
except ValueError:
    print("La edad debe ser un número entero.")
    edad = None
```

---

## Snabbt CLI‑exempel
```python
import sys

if len(sys.argv) < 2:
    print("Uso: python cli_args.py <archivo>")
    sys.exit(1)
```

---

## Testa “rena” funktioner
Istället för att testa `input()` direkt, gör en funktion som tar en sträng som argument och testa den.

---

## Sammanfattning
Säker indata gör dina program robusta. Nästa kapitel: loopar och hur man tänker på kostnad/komplexitet.
