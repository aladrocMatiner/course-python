# Apéndice A · Creación de herramientas CLI con la librería estándar

## Qué vamos a construir
Diseñaremos un comando de consola inspirado en herramientas reales: aceptará subcomandos, opciones obligatorias y mostrará ayuda automática. Usaremos `argparse`, `pathlib` y `logging` para que puedas empaquetar scripts profesionales sin dependencias externas.

## Orden pedagógico
1. **Recordatorio**: `sys.argv` y su limitación.
2. **Estructura básica con `argparse`**: descripción, argumentos posicionales y opcionales.
3. **Subcomandos (`add_subparsers`)**: múltiples acciones en una sola herramienta.
4. **Salida rica**: formateo, códigos de retorno, logging.
5. **Empaquetado básico**: punto de entrada en `if __name__ == "__main__"`.
6. **Pruebas ligeras**: `argparse` + `pytest` con `capsys`.

## Objetivos de aprendizaje
- configurar `ArgumentParser` con argumentos obligatorios y opcionales.
- Implementar subcomandos para agrupar funcionalidades.
- Leer/escribir archivos con `Path` según argumentos del usuario.
- Registrar mensajes y códigos de salida apropiados.
- Probar comandos simulando argumentos.

## Por qué importa
Aunque existirán frameworks más potentes, dominar la librería estándar evita dependencias y te permite crear herramientas internas, scripts de despliegue o utilidades de datos rápidamente.

### Mini aventura
Una CLI es como un mando a distancia para tu programa: en lugar de hacer clics, escribes comandos cortos. Si el mando está bien diseñado (con ayuda y opciones claras), cualquiera puede usarlo sin miedo.

---

## 1. `argparse` básico

```python
# cli.py
import argparse

parser = argparse.ArgumentParser(description="Gestor de notas")
parser.add_argument("titulo", help="Nombre del archivo de nota")
parser.add_argument("--mensaje", required=True)
parser.add_argument("--tags", nargs="*", default=[])
args = parser.parse_args()

print(args.titulo, args.mensaje, args.tags)
```

- `nargs="*"` permite múltiples tags.
- `parser.parse_args()` ya valida tipos y muestra ayuda.

### Ayuda generada
```
python cli.py --help
```
Produce descripción, argumentos y ejemplos automáticamente.

---

## 2. Subcomandos

```python
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(prog="todos")
subparsers = parser.add_subparsers(dest="comando", required=True)

add_parser = subparsers.add_parser("add", help="Añadir tarea")
add_parser.add_argument("texto")

list_parser = subparsers.add_parser("list", help="Listar tareas")

args = parser.parse_args()
archivo = Path("todos.txt")

if args.comando == "add":
    with archivo.open("a", encoding="utf-8") as fh:
        fh.write(args.texto + "\n")
elif args.comando == "list":
    print(archivo.read_text())
```

- `dest="comando"` indica qué subparsers se activó.
- Para `append=True` usa `archivo.open("a")` o `write_text` manualmente (Python 3.11+ soporta `append=True`).

---

## 3. Logging y códigos de salida

```python
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

try:
    # lógica
    logging.info("Nota guardada")
except Exception as exc:
    logging.error("Fallo: %s", exc)
    sys.exit(1)
```

- `sys.exit(0)` indica éxito; cualquier valor distinto implica error.

---

## 4. Buenas prácticas
- Mantén la lógica en funciones para facilitar pruebas y reutilización.
- Usa `Path` para rutas; evita concatenar strings.
- Documenta ejemplos en el `ArgumentParser(description=...)` y `epilog`.

### Estructura recomendada
```python
def build_parser():
    parser = argparse.ArgumentParser(...)
    # configurar
    return parser

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    # lógica

if __name__ == "__main__":
    main()
```

- Permite pasar `argv` personalizados durante pruebas.

---

## Ejercicios guiados (con TODOs)
1. **A-1 · CLI de gastos**
   ```python
   # TODO 1: subcomando "add" con monto y descripción
   # TODO 2: subcomando "report" que muestre el total
   # TODO 3: guarda datos en formato CSV usando Path
   ```
   *Pista*: Usa `Path("gastos.csv").open("a", newline="", encoding="utf-8")`.

2. **A-2 · Logger configurable**
   ```python
   # TODO 1: agrega opción --debug que cambie logging a DEBUG
   # TODO 2: imprime mensajes solo si el nivel corresponde
   # TODO 3: ensaya con capsys en pytest
   ```
   *Pista*: `if args.debug: logging.getLogger().setLevel(logging.DEBUG)`.

---

## Errores comunes
- Olvidar `dest` o `required=True` en subparsers ⇒ el comando no sabe qué ejecutar.
- No envolver la lógica en `try/except` ⇒ trazas crudas para errores esperados.
- Usar `print` para todo en lugar de logging ⇒ difícil de filtrar.
- No testear `argparse` con argumentos simulados.

---

## Explicación de soluciones
1. **CLI de gastos**: `subparsers.add_parser("add")` y `("report")`; `Path("gastos.csv").write_text`/`read_text` acumula entradas. `report` resume sumando cada fila.
2. **Logger configurable**: `parser.add_argument("--debug", action="store_true")`; si está activo, se sube el nivel del logger y se muestran mensajes detallados. `pytest` captura salidas con `capsys.readouterr()`.

---

## Resumen
Con `argparse`, `logging` y `pathlib` puedes crear herramientas de consola robustas, autodescriptivas y fáciles de probar, sin depender de frameworks externos.

## Reflexión final
Al dominar CLIs con la librería estándar obtienes autonomía para automatizar tareas y construir utilidades profesionales que tus compañeras/os pueden ejecutar sin instalar nada más. Estos mismos patrones se reutilizan en scripts de despliegue y herramientas DevOps.
