# Capítol 17 · Persistència lleugera: CSV/JSON i SQLite

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Connectarem els nostres programes a un emmagatzematge bàsic: primer a CSV i JSON estructurats i després a SQLite, que ja ve inclòs amb Python. Aprendràs a llegir i escriure registres, encapsular consultes en repositoris i preparar el terreny per a ORM com el de Django.

## Itinerari d'aprenentatge
1. **Recordatori ràpid: fitxers estructurats**.
2. **Persistència amb CSV i JSON**.
3. **Introducció a SQLite amb `sqlite3`**.
4. **Consultes parametritzades, insercions i lectures**.
5. **Una classe repositori senzilla**.
6. **Minimigracions: crear les taules si falten**.

## Objectius d'aprenentatge
- Desar i carregar dades CSV/JSON amb una validació bàsica.
- Connectar-se a SQLite amb `sqlite3` i executar consultes segures.
- Encapsular operacions de base de dades dins una classe repositori.
- Entendre com es tornen a convertir les files en objectes.

## Per què és important
Encara que aviat utilitzis ORM, conèixer aquests fonaments t'ajuda a depurar i entendre què passa per sota.

### Miniaventura
Desar dades és com escriure un diari: si ho fas de manera ordenada, podràs rellegir les històries anys després. CSV i JSON són llibretes simples per a notes ràpides; SQLite és una llibreta amb índexs i separadors. Conèixer-los permet que el programa «recordi» el seu viatge.

## Prerequisits
- Fitxers, JSON i CSV del capítol 13, excepcions del capítol 14 i classes/dataclasses del capítol 12.
- Un entorn local amb CPython 3.11+; `sqlite3` forma part de la biblioteca estàndard.

## Prediu abans d'executar
Tria una comanda i prediu quins tipus sobreviuen sense canvis a un cicle d'escriptura i lectura en CSV i quins valors tornen com a text. Després de tornar a llegir la fila, compara cada camp amb la predicció abans de construir un objecte.

---

## 1. Persistència amb CSV
Un CSV s'assembla a una taula en una llibreta: té columnes i files.

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

Sortida habitual; fixa't que tot allò que es llegeix del CSV arriba com a text:
```text illustrative
[{'id': '1', 'cliente': 'Noor', 'total': '120'}]
```

Repte ràpid: afegeix una altra comanda, desa-la i torna-la a llegir.

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

- JSON és molt útil per a configuracions o conjunts de dades petits.

---

## 3. SQLite (`sqlite3`)
SQLite és una base de dades petita que viu en un sol fitxer `.db`. Imagina una llibreta amb «taules», és a dir, pàgines molt ben organitzades.

```python runnable
import sqlite3

conn = sqlite3.connect("pedidos.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY, cliente TEXT, total REAL)")
conn.commit()
conn.close()
```

- `connect` crea el fitxer `.db` si no existeix.
- `CREATE TABLE` crea la taula si falta. Una taula té files i columnes, com un full de càlcul.

### Inserir i consultar
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

- Utilitza paràmetres `?` per evitar injecció SQL.
- Acostuma't des del principi a **no** concatenar strings per construir SQL.

---

## 4. Un repositori senzill

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

- Encapsula l'SQL perquè la resta del codi es mantingui net.

---

## Exercicis guiats (amb TODO)
1. **17-1 · De CSV a objectes**
   ```python todo
   # TODO 1: read pedidos.csv and convert each row into a Pedido object
   ```
   *Pista*: converteix `id` amb `int()` i `total` amb `float()` abans de construir `Pedido`.

2. **17-2 · CRUD bàsic amb SQLite**
   ```python todo
   # TODO 1: implement update(id, total)
   # TODO 2: implement delete(id)
   ```
   *Pista*: usa placeholders en totes dues sentències i comprova `cursor.rowcount` quan falti l'id.

3. **17-3 · Servei i repositori**
   ```python todo
   # TODO 1: create PedidoService that uses PedidoRepo
   # TODO 2: add validation before inserting
   ```
   *Pista*: rebutja els totals negatius al servei; deixa l'SQL i la propietat de la transacció al repositori.

---

## Errors habituals
- Oblidar `conn.commit()` després d'una inserció o actualització.
- Suposar que `with conn:` tanca SQLite: només confirma o reverteix la transacció. Crida `close()` o usa `contextlib.closing`.
- Construir SQL concatenant strings, cosa que crea risc d'injecció.

---

## Solucions explicades
1. **De CSV a objectes**: converteix `id` amb `int()` i `total` amb `float()` abans de construir `Pedido`; rebutja camps absents o invàlids amb `ValueError`.
2. **CRUD**: les consultes són `UPDATE pedidos SET total=? WHERE id=?` i `DELETE FROM pedidos WHERE id=?`.
3. **Servei i repositori**: mantén la validació al servei i la persistència al repositori, un patró habitual als frameworks.

---

## Resum
Ara pots desar i carregar dades de fitxers estructurats i SQLite, i estàs preparant el terreny per als ORM.

## Punt de control i rúbrica
- **Correcció**: els tipus sobreviuen als cicles d'escriptura i lectura de CSV/JSON i el CRUD usa paràmetres.
- **Llegibilitat**: la validació, la lògica de servei i la persistència romanen separades.
- **Gestió d'errors**: les files no vàlides reverteixen la transacció o es rebutgen sense escriptures parcials.
- **Verificació**: prova crear, llegir, actualitzar i eliminar, a més de registres absents i mal formats, en una base de dades temporal.
- **Explicació**: explica l'abast d'una transacció i per què tancar no és el mateix que confirmar amb `commit`.

## Reflexió final
Fins i tot amb eines modernes, entendre la persistència és valuós: t'ajuda a depurar i veure com es mouen les dades.
