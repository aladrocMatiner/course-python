# Capítol 17 · Persistència lleugera: CSV/JSON i SQLite

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Connectarem els programes a emmagatzematge bàsic: primer CSV/JSON estructurat i després SQLite (inclòs a Python). Veuràs com llegir/escriure registres, encapsular consultes en repositoris i preparar el terreny per a ORMs com Django.

## Objectius d’aprenentatge
- Guardar i recuperar dades en CSV/JSON amb validacions bàsiques.
- Connectar a SQLite amb `sqlite3` i fer consultes segures.
- Encapsular operacions en una classe repositori.
- Entendre com mapar files a objectes.

---

## 1. CSV

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

## 2. JSON

```python
import json
from pathlib import Path

ruta = Path("pedidos.json")
payload = json.loads(ruta.read_text())
payload.append({"id": 3, "total": 50})
ruta.write_text(json.dumps(payload, indent=2))
```

---

## 3. SQLite (`sqlite3`)

```python
import sqlite3

conn = sqlite3.connect("pedidos.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY, cliente TEXT, total REAL)")
conn.commit()
conn.close()
```

### Inserir i consultar (amb paràmetres)
```python
with sqlite3.connect("pedidos.db") as conn:
    cur = conn.cursor()
    cur.execute("INSERT INTO pedidos(cliente, total) VALUES (?, ?)", ("Ada", 120))
    conn.commit()
```

---

## 4. Repositori simple

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

---

## Errors comuns
- Oblidar `commit()`.
- No tancar connexions (usa `with`).
- Construir SQL concatenant strings.

---

## Resum
Ja pots persistir dades en fitxers estructurats i SQLite, i separar validacions (serveis) de persistència (repositoris).
