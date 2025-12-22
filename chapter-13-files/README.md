# Capítulo 13 · Gestión de ficheros y streams desde cero

## Qué vamos a construir
Aprenderás a trabajar con archivos de texto y binarios, usar context managers (`with`), escribir logs, procesar streams en tiempo real y protegerte contra errores comunes (archivos inexistentes, codificaciones, streams grandes). Construiremos utilidades que leen configuraciones, fusionan datos y generan reportes sin cargar toda la información en memoria.

## Orden pedagógico
1. **Modelo mental**: archivos como streams secuenciales.
2. **Abrir y cerrar archivos**: `open`, modos (`r`, `w`, `a`, `b`).
3. **Context managers (`with`)**: evitar fugas de recursos.
4. **Leer y procesar línea a línea**.
5. **Escribir con buffering y logs**.
6. **Trabajar con binarios (imágenes, bytes)**.
7. **Streams estándar (`sys.stdin`, `sys.stdout`)**.
8. **Pruebas y ejercicios guiados**.

## Objetivos de aprendizaje
- Abrir archivos de forma segura y elegir el modo adecuado (lectura, escritura, append, binario).
- Procesar ficheros grandes sin cargarlos enteros en memoria.
- Escribir logs y reportes aplicando buffering.
- Leer/escribir binarios con `rb`/`wb` y `bytes`.
- Usar streams (`stdin`, `stdout`) para composiciones tipo UNIX.

## Por qué importa
Todo programa serio lee o escribe datos en archivos: configuraciones, logs, exportaciones… Saber manejar streams correctamente evita corrupciones de datos y asegura que tus scripts escalen más allá de ejemplos académicos.

### Mini aventura
Un archivo es como un cuaderno: si lo abres bien, escribes con cuidado y lo cierras, tus notas quedan guardadas para mañana. Si lo dejas abierto o escribes en la página equivocada, puedes perder cosas. En este capítulo aprendes a ser una persona “ordenada” con tus cuadernos digitales.

---

## 1. Abrir archivos de texto

```python
archivo = open("notas.txt", mode="r", encoding="utf-8")
contenido = archivo.read()
archivo.close()
```

- `mode` indica cómo abrir: `r` (lectura), `w` (escritura, sobrescribe), `a` (append).
- Siempre cierra el archivo para liberar el descriptor (mejor usa `with`).

### Context manager
```python
with open("notas.txt", mode="r", encoding="utf-8") as fh:
    for linea in fh:
        print(linea.strip())
```

- `with` cierra el archivo automáticamente, incluso si ocurre una excepción.
- Iterar sobre `fh` lee línea a línea (no carga todo en memoria).

---

## 2. Escribir archivos

```python
nuevas_notas = ["Aprender archivos", "Practicar streams"]
with open("notas.txt", mode="w", encoding="utf-8") as fh:
    for nota in nuevas_notas:
        fh.write(nota + "\n")
```

- `w` sobrescribe; usa `a` si deseas añadir al final.
- `fh.write` no añade salto de línea automáticamente.

### `pathlib.Path`
```python
from pathlib import Path
ruta = Path("reportes") / "hoy.txt"
ruta.parent.mkdir(parents=True, exist_ok=True)
ruta.write_text("Reporte generado", encoding="utf-8")
```

- `write_text` y `read_text` simplifican operaciones rápidas.

---

## 3. Ficheros grandes y buffering

```python
def contar_lineas(ruta):
    total = 0
    with open(ruta, encoding="utf-8") as fh:
        for _ in fh:
            total += 1
    return total
```

- Leer línea a línea evita cargar todo en memoria.

### Control de buffering
```python
with open("log.txt", mode="a", buffering=1, encoding="utf-8") as log:
    log.write("[INFO] Inicio\n")
```

- `buffering=1` activa line buffering (escribe cuando encuentra `\n`).

---

## 4. Archivos binarios

```python
with open("imagen.png", mode="rb") as fh:
    datos = fh.read()
print(len(datos))
```

```python
with open("copia.png", mode="wb") as destino:
    destino.write(datos)
```

- Usa `rb`/`wb` para bytes; no especifiques `encoding`.
- Procesa en bloques (`fh.read(4096)`) para archivos enormes.

### Streams binarios
```python
with open("entrada.dat", "rb") as origen, open("salida.dat", "wb") as destino:
    while chunk := origen.read(8192):
        destino.write(chunk)
```

---

## 5. JSON, CSV y helpers

```python
import json
from pathlib import Path

ruta = Path("config.json")
data = json.loads(ruta.read_text())
data["debug"] = True
ruta.write_text(json.dumps(data, indent=2))
```

- `json.dumps`/`loads` convierten entre dicts y JSON.
- Usa `indent=2` para hacerlo legible.

```python
import csv
with open("usuarios.csv", newline="", encoding="utf-8") as fh:
    lector = csv.DictReader(fh)
    for fila in lector:
        print(fila["email"])
```

- `DictReader` crea dicts por fila; ideal para tratar columnas por nombre.

---

## 6. Streams estándar

```python
import sys

for linea in sys.stdin:
    sys.stdout.write(linea.upper())
```

- Permite composiciones tipo `cat archivo.txt | python script.py`.
- Usa `sys.stderr` para errores (`sys.stderr.write("Error\n")`).

---

## 7. Pruebas
Aísla la lógica en funciones que reciban rutas o file-like objects para facilitar pruebas.

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

- `StringIO` simula un archivo de texto; `BytesIO` para binarios.

---

## Ejercicios guiados (con TODOs)
1. **13-1 · Limpieza de logs**
   ```python
   # TODO 1: lee logs.txt línea a línea
   # TODO 2: descarta líneas que contengan "DEBUG"
   # TODO 3: escribe el resultado en logs_filtrados.txt
   ```
   *Hint*: usa dos context managers en la misma línea `with open(...) as origen, open(...) as destino:`.

2. **13-2 · Copiar archivo grande**
   ```python
   # TODO 1: implementa copiar(origen, destino) leyendo bloques de 4096 bytes
   # TODO 2: imprime progreso cada 1 MB usando sys.stdout
   ```
   *Hint*: `tamano += len(chunk)` dentro del bucle.

3. **13-3 · CLI de concat**
   ```python
   # TODO 1: usa argparse para aceptar múltiples archivos y destino
   # TODO 2: concatena su contenido en un solo arquivo
   # TODO 3: maneja errores cuando un archivo no existe
   ```
   *Hint*: `Path.exists()` + `try/except FileNotFoundError`.

---

## Errores comunes
- Olvidar cerrar archivos (evítalo con `with`).
- Mezclar modos (`r` vs `rb`) y obtener errores de codificación.
- Sobrescribir archivos sin confirmar (`mode="w"`).
- Leer archivos gigantes con `.read()` y agotar la memoria.

---

## Explicación de soluciones
1. **Limpieza de logs**: `if "DEBUG" not in linea` ⇒ `destination.write(linea)`; se procesa en streaming.
2. **Copiar archivo grande**: leer bloques y escribirlos conserva memoria; el progreso ayuda a diagnosticar cuellos de botella.
3. **CLI de concat**: `for ruta in args.archivos:` abre uno a uno y escribe en destino; maneja errores con mensajes claros.

---

## Resumen
Dominas las operaciones básicas de lectura/escritura, sabes cuándo usar modos de texto o binario, y entiendes cómo procesar streams sin agotar recursos. Estos patrones son la base de ETLs, reportes y utilidades de línea de comandos.

## Reflexión final
Trabajar con archivos y streams requiere disciplina: elegir bien el modo, validar rutas y protegerte contra archivos enormes. Con práctica podrás crear herramientas que procesen gigabytes de datos de manera segura.
