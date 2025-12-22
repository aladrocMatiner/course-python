# Kapitel 17 · Lätt persistens: CSV/JSON och SQLite

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Vi sparar data i CSV/JSON och i en liten SQLite‑databas med `sqlite3`. Vi pratar också om säkra parametriserade frågor.

---

## CSV (idé)
```python
import csv

def guardar_pedidos(ruta, pedidos):
    with open(ruta, mode="w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "cliente", "total"])
        writer.writeheader()
        for pedido in pedidos:
            writer.writerow(pedido)
```

---

## SQLite (skapa tabell)
```python
import sqlite3

conn = sqlite3.connect("pedidos.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY, cliente TEXT, total REAL)")
conn.commit()
conn.close()
```

---

## Sammanfattning
Du kan nu spara och hämta data och förstå grunderna bakom ORMs. Nästa kapitel: testing med pytest.
