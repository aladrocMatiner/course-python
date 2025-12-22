# Chapter 13 · Files and Streams from Scratch

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
You’ll learn to work with text and binary files, use context managers (`with`), write logs, process streams in real time, and protect yourself from common problems (missing files, encodings, huge streams). We’ll build utilities that read configs, merge data, and generate reports without loading everything into memory.

## Learning path
1. **Mental model**: files as sequential streams.
2. **Open/close**: `open`, modes (`r`, `w`, `a`, `b`).
3. **Context managers (`with`)**: avoid resource leaks.
4. **Read and process line by line**.
5. **Write with buffering and logs**.
6. **Binary files (images, bytes)**.
7. **Standard streams (`sys.stdin`, `sys.stdout`)**.
8. **Tests and guided exercises**.

## Learning objectives
- Open files safely and choose the correct mode (read/write/append/binary).
- Process large files without loading them fully into memory.
- Write logs and reports with buffering.
- Read/write binary data with `rb`/`wb` and `bytes`.
- Use streams (`stdin`, `stdout`) for UNIX-style compositions.

## Why it matters
Every serious program reads or writes files: configs, logs, exports… Knowing how to handle streams correctly prevents data corruption and makes your scripts scale beyond classroom examples.

### Mini adventure
A file is like a notebook: if you open it properly, write carefully, and close it, your notes will be there tomorrow. If you leave it open or write on the wrong page, you can lose things. This chapter teaches you to be “organized” with your digital notebooks.

---

## 1. Opening text files

```python
archivo = open("notas.txt", mode="r", encoding="utf-8")
contenido = archivo.read()
archivo.close()
```

- `mode` tells Python how to open it: `r` (read), `w` (write, overwrite), `a` (append).
- Always close the file to free the handle (better: use `with`).

### Context manager
```python
with open("notas.txt", mode="r", encoding="utf-8") as fh:
    for linea in fh:
        print(linea.strip())
```

- `with` closes the file automatically, even if an exception happens.
- Iterating over `fh` reads line by line (doesn’t load everything in memory).

---

## 2. Writing files

```python
nuevas_notas = ["Aprender archivos", "Practicar streams"]
with open("notas.txt", mode="w", encoding="utf-8") as fh:
    for nota in nuevas_notas:
        fh.write(nota + "\n")
```

- `w` overwrites; use `a` if you want to add at the end.
- `fh.write` does not add a newline automatically.

### `pathlib.Path`
```python
from pathlib import Path
ruta = Path("reportes") / "hoy.txt"
ruta.parent.mkdir(parents=True, exist_ok=True)
ruta.write_text("Reporte generado", encoding="utf-8")
```

- `write_text` and `read_text` simplify quick operations.

---

## 3. Large files and buffering

```python
def contar_lineas(ruta):
    total = 0
    with open(ruta, encoding="utf-8") as fh:
        for _ in fh:
            total += 1
    return total
```

- Line-by-line processing avoids loading the whole file.

### Buffering control
```python
with open("log.txt", mode="a", buffering=1, encoding="utf-8") as log:
    log.write("[INFO] Inicio\n")
```

- `buffering=1` enables line buffering (flushes on `\n`).

---

## 4. Binary files

```python
with open("imagen.png", mode="rb") as fh:
    datos = fh.read()
print(len(datos))
```

```python
with open("copia.png", mode="wb") as destino:
    destino.write(datos)
```

- Use `rb`/`wb` for bytes; don’t set `encoding`.
- For huge files, read in chunks (`fh.read(4096)`).

### Binary streaming
```python
with open("entrada.dat", "rb") as origen, open("salida.dat", "wb") as destino:
    while chunk := origen.read(8192):
        destino.write(chunk)
```

---

## 5. JSON, CSV, and helpers

```python
import json
from pathlib import Path

ruta = Path("config.json")
data = json.loads(ruta.read_text())
data["debug"] = True
ruta.write_text(json.dumps(data, indent=2))
```

- `json.dumps`/`loads` convert between dicts and JSON.
- `indent=2` makes it readable.

```python
import csv
with open("usuarios.csv", newline="", encoding="utf-8") as fh:
    lector = csv.DictReader(fh)
    for fila in lector:
        print(fila["email"])
```

- `DictReader` creates dicts per row — great when you want columns by name.

---

## 6. Standard streams

```python
import sys

for linea in sys.stdin:
    sys.stdout.write(linea.upper())
```

- Enables compositions like `cat archivo.txt | python script.py`.
- Use `sys.stderr` for errors (`sys.stderr.write("Error\n")`).

---

## 7. Tests
Keep logic in functions that receive paths or file-like objects so testing is easy.

```python
def procesar_fichero(fh):
    return [linea.strip() for linea in fh]
```

```python
from io import StringIO

def test_procesar_fichero():
    fake = StringIO("uno\ndos\n")
    assert procesar_fichero(fake) == ["uno", "dos"]
```

- `StringIO` simulates a text file; `BytesIO` for binary.

---

## Guided exercises (with TODOs)
1. **13-1 · Log cleanup**
   ```python
   # TODO 1: read logs.txt line by line
   # TODO 2: drop lines containing "DEBUG"
   # TODO 3: write the result to logs_filtrados.txt
   ```
   *Hint*: use two context managers in one line: `with open(...) as origen, open(...) as destino:`.

2. **13-2 · Copy a big file**
   ```python
   # TODO 1: implement copiar(origen, destino) reading 4096-byte chunks
   # TODO 2: print progress every 1 MB using sys.stdout
   ```
   *Hint*: `tamano += len(chunk)` inside the loop.

3. **13-3 · Concat CLI**
   ```python
   # TODO 1: use argparse to accept multiple files and a destination
   # TODO 2: concatenate their content into one file
   # TODO 3: handle errors when a file does not exist
   ```
   *Hint*: `Path.exists()` + `try/except FileNotFoundError`.

---

## Common mistakes
- Forgetting to close files (avoid with `with`).
- Mixing text/binary modes (`r` vs `rb`) and getting encoding errors.
- Overwriting files by accident (`mode="w"`).
- Reading giant files with `.read()` and running out of memory.

---

## Explained solutions
1. **Log cleanup**: `if "DEBUG" not in linea` ⇒ `destination.write(linea)`; it’s streaming.
2. **Copy big file**: chunked reads keep memory stable; progress helps diagnose bottlenecks.
3. **Concat CLI**: `for ruta in args.archivos:` open one by one and write to destination; handle errors with clear messages.

---

## Summary
You now know the basics of reading/writing, when to use text vs binary modes, and how to process streams without exhausting resources. These patterns are the base of ETLs, reports, and CLI utilities.

## Closing reflection
Working with files and streams requires discipline: choose modes carefully, validate paths, and protect yourself from huge files. With practice you’ll build tools that safely process gigabytes of data.
