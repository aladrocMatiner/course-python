# Chapter 17 · Lightweight Persistence: CSV/JSON and SQLite

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll connect our programs to basic storage: first structured CSV/JSON, then SQLite (built into Python). You’ll learn to read/write records, encapsulate queries in repositories, and prepare the ground for ORMs like Django.

## Learning path
1. **Quick reminder: structured files**.
2. **Persistence with CSV/JSON**.
3. **SQLite intro (`sqlite3`)**.
4. **Parameterized queries, inserts, reads**.
5. **Simple repository class**.
6. **Mini “migrations” (create tables if missing)**.

## Learning objectives
- Save and load data in CSV/JSON with basic validation.
- Connect to SQLite with `sqlite3` and run safe queries.
- Encapsulate database operations inside a repository class.
- Understand how to map rows back into objects.

## Why it matters
Even if you’ll soon use ORMs, knowing the basics helps you debug and understand what happens underneath.

### Mini adventure
Saving data is like keeping a diary: if you write it neatly, you can re-read your stories years later. With CSV/JSON you get simple notebooks for quick notes; with SQLite you get a notebook with indexes and separators. Knowing both helps your program “remember” its journey.

---

## 1. CSV persistence
A CSV is like a table in a notebook: columns and rows.

```python
import csv

def guardar_pedidos(ruta, pedidos):
    with open(ruta, mode="w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "cliente", "total"])
        writer.writeheader()
        for pedido in pedidos:
            writer.writerow(pedido)
```

```python
with open("pedidos.csv", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    pedidos = list(reader)
print(pedidos)
```

Typical output (note: everything read from CSV arrives as text):
```
[{'id': '1', 'cliente': 'Noor', 'total': '120'}]
```

Quick challenge: add one more order and save/read again.

---

## 2. JSON

```python
import json
from pathlib import Path

ruta = Path("pedidos.json")
payload = json.loads(ruta.read_text())
payload.append({"id": 3, "total": 50})
ruta.write_text(json.dumps(payload, indent=2))
```

- JSON is great for configuration or small data sets.

---

## 3. SQLite (`sqlite3`)
SQLite is a small database that lives in a single file (`.db`). Think of it as a notebook with very organized “tables” (pages).

```python
import sqlite3

conn = sqlite3.connect("pedidos.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY, cliente TEXT, total REAL)")
conn.commit()
conn.close()
```

- `connect` creates the `.db` file if it doesn’t exist.
- `CREATE TABLE` creates a table (if missing). A table is like a spreadsheet: rows and columns.

### Insert and query
```python
with sqlite3.connect("pedidos.db") as conn:
    cur = conn.cursor()
    cur.execute("INSERT INTO pedidos(cliente, total) VALUES (?, ?)", ("Noor", 120))
    conn.commit()

with sqlite3.connect("pedidos.db") as conn:
    cur = conn.cursor()
    cur.execute("SELECT id, cliente, total FROM pedidos")
    filas = cur.fetchall()
```

- Use `?` parameters to avoid SQL injection.
- Even while learning, build the habit of **not** concatenating strings to build SQL.

---

## 4. A simple repository

```python
class PedidoRepo:
    def __init__(self, conexion):
        self.conn = conexion

    def crear(self, cliente, total):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO pedidos(cliente, total) VALUES (?, ?)", (cliente, total))
        self.conn.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, cliente, total FROM pedidos")
        return cur.fetchall()
```

```python
with sqlite3.connect("pedidos.db") as conn:
    repo = PedidoRepo(conn)
    repo.crear("Frej", 90)
    print(repo.listar())
```

- Encapsulate SQL so the rest of your code stays clean.

---

## Guided exercises (with TODOs)
1. **17-1 · CSV to objects**
   ```python
   # TODO 1: read pedidos.csv and convert each row into a Pedido object
   ```

2. **17-2 · Basic SQLite CRUD**
   ```python
   # TODO 1: implement update(id, total)
   # TODO 2: implement delete(id)
   ```

3. **17-3 · Service + repository**
   ```python
   # TODO 1: create PedidoService that uses PedidoRepo
   # TODO 2: add validation before inserting
   ```

---

## Common mistakes
- Forgetting `conn.commit()` after inserts/updates.
- Not closing connections (use `with`).
- Building SQL by string concatenation (injection risk).

---

## Explained solutions
1. **CSV to objects**: use `csv.DictReader` and `Pedido(**fila)` if you use dataclasses.
2. **CRUD**: `UPDATE pedidos SET total=? WHERE id=?`; `DELETE FROM pedidos WHERE id=?`.
3. **Service + repo**: keep validation in the service, persistence in the repo — a common framework pattern.

---

## Summary
You can now save and load data from structured files and SQLite, preparing the ground for ORMs.

## Closing reflection
Even with modern tools, persistence fundamentals are valuable: they help you debug and understand how data moves.
