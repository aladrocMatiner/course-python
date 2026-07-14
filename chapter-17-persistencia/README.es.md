# Capítulo 17 · Persistencia ligera: archivos estructurados y SQLite

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Conectaremos nuestros programas a almacenamiento básico: primero CSV/JSON estructurados y luego una base SQLite integrada en Python. Verás cómo leer/escribir registros, encapsular consultas en repositorios y preparar el terreno para ORMs como Django.

## Orden pedagógico
1. **Recordatorio de archivos estructurados**.
2. **Persistencia en CSV/JSON**.
3. **Introducción a SQLite (`sqlite3`)**.
4. **Consultas parametrizadas, inserciones y lecturas**.
5. **Repositorio simple (clase)**.
6. **Migraciones mínimas (crear tablas si no existen)**.

## Objetivos de aprendizaje
- Guardar y recuperar datos en CSV/JSON con validaciones básicas.
- Conectar a SQLite usando `sqlite3` y ejecutar consultas seguras.
- Encapsular operaciones de base de datos en una clase repositorio.
- Entender cómo mapear filas a objetos.

## Por qué importa
Aunque pronto usarás ORMs, conocer los fundamentos te ayuda a depurar y comprender qué ocurre debajo.

### Mini aventura
Guardar datos es como llevar un diario: si lo escribes ordenadamente podrás releer tus historias años después. Con CSV/JSON tienes cuadernos sencillos para notas rápidas; con SQLite consigues una libreta con índices y separadores. Saber usarlos te ayuda a no perder ningún recuerdo del viaje que narra tu programa.

## Prerrequisitos
- Archivos, JSON y CSV del capítulo 13, excepciones del capítulo 14 y clases/dataclasses del capítulo 12.
- Un entorno local con CPython 3.11+; `sqlite3` forma parte de la biblioteca estándar.

## Predice antes de ejecutar
Elige un pedido y predice qué tipos sobreviven sin cambios a un ciclo de escritura y lectura en CSV y qué valores regresan como texto. Después de volver a leer la fila, compara cada campo con tu predicción antes de construir un objeto.

---

## 1. Persistencia en CSV
Un CSV es como una tabla en un cuaderno: columnas y filas.

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

Salida típica (ojo: todo lo leído del CSV llega como texto):
```text illustrative
[{'id': '1', 'cliente': 'Noor', 'total': '120'}]
```

Reto rápido: agrega un pedido más y vuelve a guardar/leer.

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

- JSON es perfecto para configuraciones o datos pequeños.

---

## 3. SQLite (`sqlite3`)
SQLite es una base de datos pequeña que vive en un solo archivo (`.db`). Piensa en ella como una libreta con “tablas” (páginas) muy ordenadas.

```python runnable
import sqlite3

conn = sqlite3.connect("pedidos.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY, cliente TEXT, total REAL)")
conn.commit()
conn.close()
```

- `connect` crea el archivo `.db` si no existe.
- `CREATE TABLE` crea una tabla (si no existe). Una tabla es como un Excel: filas y columnas.

### Insertar y consultar
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

- Usa parámetros `?` para evitar SQL injection.
- Aunque estés aprendiendo, acostúmbrate desde el principio a **no** concatenar strings para crear SQL.

---

## 4. Repositorio simple

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

- Encapsula la lógica de SQL para mantener el resto del código limpio.

---

## Ejercicios guiados (con TODOs)
1. **17-1 · CSV a objetos**
   ```python todo
   # TODO 1: read pedidos.csv and convert each row into a Pedido object
   ```
   *Pista*: convierte `id` con `int()` y `total` con `float()` antes de construir `Pedido`.

2. **17-2 · CRUD básico SQLite**
   ```python todo
   # TODO 1: implement update(id, total)
   # TODO 2: implement delete(id)
   ```
   *Pista*: usa placeholders en ambas sentencias y comprueba `cursor.rowcount` cuando falte el id.

3. **17-3 · Servicio + repositorio**
   ```python todo
   # TODO 1: create PedidoService that uses PedidoRepo
   # TODO 2: add validation before inserting
   ```
   *Pista*: rechaza los totales negativos en el servicio; deja el SQL y la propiedad de la transacción en el repositorio.

---

## Errores comunes
- Olvidar `conn.commit()` tras inserciones o actualizaciones.
- Suponer que `with conn:` cierra SQLite: solo confirma o revierte la transacción. Llama a `close()` o usa `contextlib.closing`.
- Construir SQL concatenando strings (riesgo de inyección).

---

## Explicación de soluciones
1. **CSV a objetos**: convierte `id` con `int()` y `total` con `float()` antes de construir `Pedido`; rechaza campos ausentes o inválidos con `ValueError`.
2. **CRUD**: `UPDATE pedidos SET total=? WHERE id=?`; `DELETE FROM pedidos WHERE id=?`.
3. **Servicio + repo**: separa validaciones (servicio) de persistencia (repo) para replicar patrones de frameworks.

---

## Resumen
Ya puedes guardar y recuperar datos de archivos estructurados y SQLite, preparando el terreno para ORMs.

## Punto de control y rúbrica
- **Corrección**: los tipos sobreviven a los ciclos de escritura y lectura de CSV/JSON y el CRUD usa parámetros.
- **Legibilidad**: la validación, la lógica de servicio y la persistencia permanecen separadas.
- **Manejo de errores**: las filas inválidas revierten la transacción o se rechazan sin escrituras parciales.
- **Verificación**: prueba crear, leer, actualizar y eliminar, además de registros ausentes y mal formados, en una base de datos temporal.
- **Explicación**: explica el alcance de una transacción y por qué cerrar no es lo mismo que confirmar con `commit`.

## Reflexión final
Incluso con herramientas modernas, los fundamentos de persistencia son valiosos: te ayudan a depurar y entender cómo viajan los datos.
