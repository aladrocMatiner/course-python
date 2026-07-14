# Capítulo 13 · Gestión de ficheros y streams desde cero

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

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

## Prerrequisitos
- Funciones, bucles, listas y fundamentos de `pathlib` de capítulos anteriores.
- Un entorno local con CPython 3.11+ y un directorio desechable para practicar.
- **Avance opcional**: el ejercicio 13-3 captura `FileNotFoundError`. Puedes copiar ahora el patrón mostrado; el [capítulo 14](../chapter-14-exceptions/README.es.md) enseña las excepciones en profundidad.

## Predice antes de ejecutar
Antes del primer ejemplo, predice qué cambia si falta el archivo y qué operación debe liberar el descriptor de archivo de todos modos. Después de ejecutar un ejemplo seguro en tu directorio desechable, compara el contenido observado y la limpieza con tu predicción antes de continuar.

---

## 1. Abrir archivos de texto

```python illustrative
archivo = open("notas.txt", mode="r", encoding="utf-8")
contenido = archivo.read()
archivo.close()
```

- `mode` indica cómo abrir: `r` (lectura), `w` (escritura, sobrescribe), `a` (append).
- Siempre cierra el archivo para liberar el descriptor (mejor usa `with`).

### Context manager
```python illustrative
with open("notas.txt", mode="r", encoding="utf-8") as fh:
    for linea in fh:
        print(linea.strip())
```

- `with` cierra el archivo automáticamente, incluso si ocurre una excepción.
- Iterar sobre `fh` lee línea a línea (no carga todo en memoria).

---

## 2. Escribir archivos

```python runnable
from pathlib import Path
from tempfile import TemporaryDirectory

nuevas_notas = ["Aprender archivos", "Practicar streams"]
with TemporaryDirectory() as temp_dir:
    ruta_notas = Path(temp_dir) / "notas.txt"
    with ruta_notas.open(mode="w", encoding="utf-8") as fh:
        for nota in nuevas_notas:
            fh.write(nota + "\n")
```

- `w` sobrescribe; usa `a` si deseas añadir al final.
- `fh.write` no añade salto de línea automáticamente.

### `pathlib.Path`
```python runnable
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as temp_dir:
    ruta = Path(temp_dir) / "reportes" / "hoy.txt"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("Reporte generado", encoding="utf-8")
```

- `write_text` y `read_text` simplifican operaciones rápidas.

---

## 3. Ficheros grandes y buffering

```python runnable
def contar_lineas(ruta):
    total = 0
    with open(ruta, encoding="utf-8") as fh:
        for _ in fh:
            total += 1
    return total
```

- Leer línea a línea evita cargar todo en memoria.

### Control de buffering
```python runnable
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as temp_dir:
    ruta_log = Path(temp_dir) / "log.txt"
    with ruta_log.open(mode="a", buffering=1, encoding="utf-8") as log:
        log.write("[INFO] Inicio\n")
```

- `buffering=1` activa line buffering (escribe cuando encuentra `\n`).

---

## 4. Archivos binarios

```python illustrative
with open("imagen.png", mode="rb") as fh:
    datos = fh.read()
print(len(datos))
```

```python illustrative
with open("copia.png", mode="wb") as destino:
    destino.write(datos)
```

- Usa `rb`/`wb` para bytes; no especifiques `encoding`.
- Procesa en bloques (`fh.read(4096)`) para archivos enormes.

### Streams binarios
```python illustrative
with open("entrada.dat", "rb") as origen, open("salida.dat", "wb") as destino:
    while chunk := origen.read(8192):
        destino.write(chunk)
```

---

## 5. JSON, CSV y helpers

```python illustrative
import json
from pathlib import Path

ruta = Path("config.json")
data = json.loads(ruta.read_text())
data["debug"] = True
ruta.write_text(json.dumps(data, indent=2))
```

- `json.dumps`/`loads` convierten entre dicts y JSON.
- Usa `indent=2` para hacerlo legible.

```python illustrative
import csv
with open("usuarios.csv", newline="", encoding="utf-8") as fh:
    lector = csv.DictReader(fh)
    for fila in lector:
        print(fila["email"])
```

- `DictReader` crea dicts por fila; ideal para tratar columnas por nombre.

---

## 6. Streams estándar

```python runnable
import sys

for linea in sys.stdin:
    sys.stdout.write(linea.upper())
```

- Permite composiciones tipo `cat archivo.txt | python script.py`.
- Usa `sys.stderr` para errores (`sys.stderr.write("Error\n")`).

---

## 7. Pruebas
Aísla la lógica en funciones que reciban rutas o file-like objects para facilitar pruebas.

```python runnable
def procesar_fichero(fh):
    return [linea.strip() for linea in fh]
```

```python runnable
from io import StringIO

def test_procesar_fichero():
    fake = StringIO("uno\ndos\n")
    assert procesar_fichero(fake) == ["uno", "dos"]
```

- `StringIO` simula un archivo de texto; `BytesIO` para binarios.

---

## Ejercicios guiados (con TODOs)
1. **13-1 · Limpieza de logs**
   ```python todo
   # TODO 1: read logs.txt line by line
   # TODO 2: drop lines containing "DEBUG"
   # TODO 3: write the result to logs_filtrados.txt
   ```
   *Pista*: usa dos context managers en la misma línea `with open(...) as origen, open(...) as destino:`.

2. **13-2 · Copiar archivo grande**
   ```python todo
   # TODO 1: implement copiar(origen, destino) reading 4096-byte chunks
   # TODO 2: print progress every 1 MB using sys.stdout
   ```
   *Pista*: `tamano += len(chunk)` dentro del bucle.

3. **13-3 · CLI de concat**
   ```python todo
   # TODO 1: use argparse to accept multiple files and a destination
   # TODO 2: concatenate their content into one file
   # TODO 3: handle errors when a file does not exist
   ```
   *Pista*: `Path.exists()` + `try/except FileNotFoundError`.

---

## Errores comunes
- Olvidar cerrar archivos (evítalo con `with`).
- Mezclar modos (`r` vs `rb`) y obtener errores de codificación.
- Sobrescribir archivos por accidente (`mode="w"`); practica en un directorio temporal antes de elegir un destino real.
- Leer archivos gigantes con `.read()` y agotar la memoria.

---

## Explicación de soluciones
1. **Limpieza de logs**: `if "DEBUG" not in linea` ⇒ `destino.write(linea)`; se procesa en streaming.
2. **Copiar archivo grande**: leer bloques y escribirlos conserva memoria; el progreso ayuda a diagnosticar cuellos de botella.
3. **CLI de concat**: `for ruta in args.archivos:` abre uno a uno y escribe en destino; maneja errores con mensajes claros.

---

## Resumen
Dominas las operaciones básicas de lectura/escritura, sabes cuándo usar modos de texto o binario, y entiendes cómo procesar streams sin agotar recursos. Estos patrones son la base de ETLs, reportes y utilidades de línea de comandos.

## Punto de control y rúbrica
- **Corrección**: los modos de texto y binario corresponden a los datos y el streaming conserva el contenido.
- **Legibilidad**: las rutas y las responsabilidades de los archivos tienen nombres claros.
- **Manejo de errores**: los archivos ausentes y los destinos inválidos tienen una vía de recuperación.
- **Verificación**: ejecuta los ejercicios en un directorio temporal y prueba entradas vacías y de varias líneas.
- **Explicación**: explica por qué `with` y las lecturas por bloques protegen los recursos.

## Reflexión final
Trabajar con archivos y streams requiere disciplina: elegir bien el modo, validar rutas y protegerte contra archivos enormes. Con práctica podrás crear herramientas que procesen gigabytes de datos de manera segura.
