# Kapitel 17 · Lättviktig persistens: CSV/JSON och SQLite

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Vi kopplar program till grundläggande lagring: först strukturerad CSV/JSON, sedan SQLite som ingår i Python. Du läser och skriver poster, kapslar SQL i repositories och förbereder ORMs som Django.

## Lärväg

1. **Strukturerade filer**.
2. **CSV- och JSON-persistens**.
3. **SQLite med `sqlite3`**.
4. **Parametriserade inserts och queries**.
5. **En enkel repository-klass**.
6. **Minimigrationer** som skapar saknade tabeller.

## Lärandemål

- Spara och läsa CSV/JSON med grundvalidering.
- Ansluta till SQLite och köra säkra queries.
- Kapsla databasoperationer i repository.
- Mappa rows tillbaka till objekt.

## Varför det spelar roll

Även med ORM hjälper grunderna dig att förstå och felsöka lagret under.

### Miniäventyr

Persistens är programmets dagbok. CSV/JSON är enkla anteckningsböcker; SQLite lägger till välordnade tabeller och index så resan kan läsas senare.

## Förkunskaper
- Filer och JSON/CSV från kapitel 13, undantag från kapitel 14 samt klasser och dataclasses från kapitel 12.
- En lokal miljö med CPython 3.11+; `sqlite3` ingår i standardbiblioteket.

## Förutsäg innan du kör
Välj en order och förutsäg vilka typer som överlever en tur och retur genom CSV oförändrade och vilka värden som kommer tillbaka som text. När du har läst tillbaka raden jämför du varje fält med din förutsägelse innan du skapar ett objekt.

---

## 1. CSV-persistens

CSV liknar en tabell med kolumner och rader.

```python runnable
import csv

def guardar_pedidos(ruta, pedidos):
    with open(ruta, mode="w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "cliente", "total"])
        writer.writeheader()
        for pedido in pedidos:
            writer.writerow(pedido)
```

```python illustrative
with open("pedidos.csv", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    pedidos = list(reader)
print(pedidos)
```

Typisk utdata; allt från CSV blir text:

```text illustrative
[{'id': '1', 'cliente': 'Noor', 'total': '120'}]
```

Snabbutmaning: lägg till en order, spara och läs igen.

---

## 2. JSON

```python illustrative
import json
from pathlib import Path

ruta = Path("pedidos.json")
payload = json.loads(ruta.read_text())
payload.append({"id": 3, "total": 50})
ruta.write_text(json.dumps(payload, indent=2))
```

JSON passar konfiguration och små datamängder.

---

## 3. SQLite (`sqlite3`)

SQLite är en liten databas i en `.db`-fil, som en anteckningsbok med organiserade tabeller.

```python runnable
import sqlite3

conn = sqlite3.connect("pedidos.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY, cliente TEXT, total REAL)")
conn.commit()
conn.close()
```

- `connect` skapar filen om den saknas.
- `CREATE TABLE` skapar tabellen med rows och columns.

### Insert och query

```python illustrative
from contextlib import closing

with closing(sqlite3.connect("pedidos.db")) as conn:
    with conn:  # commits on success and rolls back on failure
        cur = conn.cursor()
        cur.execute("INSERT INTO pedidos(cliente, total) VALUES (?, ?)", ("Noor", 120))

with closing(sqlite3.connect("pedidos.db")) as conn:
    cur = conn.cursor()
    cur.execute("SELECT id, cliente, total FROM pedidos")
    filas = cur.fetchall()
```

- Använd `?`-parametrar mot SQL injection.
- Bygg aldrig SQL genom strängkonkatenering, inte ens under inlärning.

---

## 4. En enkel repository

```python runnable
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

```python illustrative
from contextlib import closing

with closing(sqlite3.connect("pedidos.db")) as conn:
    repo = PedidoRepo(conn)
    repo.crear("Frej", 90)
    print(repo.listar())
```

Kapsla SQL så övrig kod förblir ren.

---

## Vägledda övningar (med TODO)

1. **17-1 · CSV till objekt**

   ```python todo
   # TODO 1: read pedidos.csv and convert each row into a Pedido object
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

2. **17-2 · Grundläggande SQLite CRUD**

   ```python todo
   # TODO 1: implement update(id, total)
   # TODO 2: implement delete(id)
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

3. **17-3 · Service och repository**

   ```python todo
   # TODO 1: create PedidoService that uses PedidoRepo
   # TODO 2: add validation before inserting
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

---

## Vanliga misstag

- Glömma `conn.commit()` efter insert/update.
- Anta inte att `with conn:` stänger SQLite; det bekräftar eller återställer bara transaktionen. Anropa `close()` eller använd `contextlib.closing`.
- Bygga SQL med strängar och skapa injectionrisk.

---

## Förklarade lösningar

1. **CSV**: konvertera `id` med `int()` och `total` med `float()` innan `Pedido` skapas; avvisa saknade eller ogiltiga fält med `ValueError`.
2. **CRUD**: `UPDATE pedidos SET total=? WHERE id=?` och `DELETE FROM pedidos WHERE id=?`.
3. **Service/repo**: validering i service och persistens i repository, ett vanligt frameworkmönster.

---

## Sammanfattning

Du kan lagra och läsa strukturerade filer och SQLite och är redo för ORMs.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: resultatet uppfyller enhetens kontrakt.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: ett normalfall, ett gränsfall och en återhämtning testas.
- **Verifiering**: exempel och övningar körs i en ren miljö.
- **Förklaring**: du kan motivera besluten och deras risker.

## Avslutande reflektion

Persistensgrunder visar hur data rör sig och gör moderna verktyg lättare att felsöka.
