# Bilaga A · Bygg CLI‑verktyg med standardbiblioteket

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
En liten kommandoradsapp med `argparse`: subkommandon, obligatoriska flaggor och automatisk hjälp. Vi använder också `pathlib` och `logging`.

---

## `argparse`‑exempel
```python
import argparse

parser = argparse.ArgumentParser(description="Gestor de notas")
parser.add_argument("titulo", help="Nombre del archivo de nota")
parser.add_argument("--mensaje", required=True)
parser.add_argument("--tags", nargs="*", default=[])
args = parser.parse_args()
```

---

## Sammanfattning
CLI‑verktyg är perfekta för automation. Med standardbiblioteket kan du bygga mycket utan extra beroenden.
