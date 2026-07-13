# Apéndice A · Creación de herramientas CLI con la librería estándar

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

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
- Configurar `ArgumentParser` con argumentos obligatorios y opcionales.
- Implementar subcomandos para agrupar funcionalidades.
- Leer/escribir archivos con `Path` según argumentos del usuario.
- Registrar mensajes y códigos de salida apropiados.
- Probar comandos simulando argumentos.

## Por qué importa
Aunque existirán frameworks más potentes, dominar la librería estándar evita dependencias y te permite crear herramientas internas, scripts de despliegue o utilidades de datos rápidamente.

### Mini aventura
Una CLI es como un mando a distancia para tu programa: en lugar de hacer clics, escribes comandos cortos. Si el mando está bien diseñado (con ayuda y opciones claras), cualquiera puede usarlo sin miedo.

## Prerrequisitos
Capítulos previos recomendados: 9, 11, 13–16, 18.
Usa CPython 3.11+ en un entorno local desechable y mantén los datos, secretos y servicios fuera de sistemas reales.

---

## 1. `argparse` básico

```python illustrative
# cli.py
import argparse

parser = argparse.ArgumentParser(description="Notes manager")
parser.add_argument("title", help="Note file name")
parser.add_argument("--message", required=True)
parser.add_argument("--tags", nargs="*", default=[])
args = parser.parse_args()

print(args.title, args.message, args.tags)
```

- `nargs="*"` permite múltiples tags.
- `parser.parse_args()` ya valida los argumentos y genera la ayuda.

### Ayuda generada
```text illustrative
python cli.py --help
```
Produce la descripción, los argumentos y el modo de uso automáticamente.

---

## 2. Subcomandos

```python illustrative
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(prog="todos")
subparsers = parser.add_subparsers(dest="command", required=True)

add_parser = subparsers.add_parser("add", help="Add task")
add_parser.add_argument("text")

list_parser = subparsers.add_parser("list", help="List tasks")

args = parser.parse_args()
file_path = Path("todos.txt")

if args.command == "add":
    with file_path.open("a", encoding="utf-8") as fh:
        fh.write(args.text + "\n")
elif args.command == "list":
    if file_path.exists():
        print(file_path.read_text(encoding="utf-8"))
    else:
        print("No tasks yet.")
```

- `dest="comando"` indica qué subcomando se activó.
- Para añadir contenido al final, usa `archivo.open("a", encoding="utf-8")` como en el ejemplo anterior. `Path.write_text()` reemplaza el archivo y no acepta un argumento `append=True`.

---

## 3. Logging y códigos de salida

```python runnable
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

try:
    # logic
    logging.info("Note saved")
except Exception as exc:
    logging.error("Failure: %s", exc)
    sys.exit(1)
```

- `sys.exit(0)` indica éxito; cualquier valor distinto implica error.

---

## 4. Buenas prácticas
- Mantén la lógica en funciones para facilitar pruebas y reutilización.
- Usa `Path` para rutas; evita concatenar strings.
- Documenta ejemplos en el `ArgumentParser(description=...)` y `epilog`.

### Estructura recomendada
```python illustrative
def build_parser():
    parser = argparse.ArgumentParser(...)
    # configure
    return parser

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    # logic

if __name__ == "__main__":
    main()
```

### Prueba de argv
```python illustrative
def test_build_parser_add():
    parser = build_parser()
    args = parser.parse_args(["add", "Learn argparse"])
    assert args.command == "add"
    assert args.text == "Learn argparse"
```

- Permite pasar `argv` personalizados durante pruebas.

---

## Ejercicios guiados (con TODOs)
1. **A-1 · CLI de gastos**
   ```python todo
   # TODO 1: "add" subcommand with amount and description
   # TODO 2: "report" subcommand that shows the total
   # TODO 3: store data in CSV format using Path
   ```
   *Pista*: Usa `Path("gastos.csv").open("a", newline="", encoding="utf-8")`.

2. **A-2 · Logger configurable**
   ```python todo
   # TODO 1: add --debug option that sets logging to DEBUG
   # TODO 2: print messages only if the level matches
   # TODO 3: try capsys in pytest
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
1. **CLI de gastos**: `subparsers.add_parser("add")` y `subparsers.add_parser("report")`; abre `Path("gastos.csv")` en modo `"a"` para añadir filas sin sobrescribir las existentes. `report` lee y suma sus valores.
2. **Logger configurable**: activa `--debug` con `store_true` y comprueba registros con `caplog`; reserva `capsys` para `stdout` y `stderr`.

---

## Resumen
Con `argparse`, `logging` y `pathlib` puedes crear herramientas de consola robustas, autodescriptivas y fáciles de probar, sin depender de frameworks externos.

## Punto de control y rúbrica
- **Corrección**: el resultado cumple el contrato de la unidad.
- **Legibilidad**: nombres y responsabilidades se entienden a la primera.
- **Errores**: se prueban un caso válido, un límite y una recuperación.
- **Verificación**: los ejemplos y ejercicios se ejecutan en un entorno limpio.
- **Explicación**: puedes justificar las decisiones y sus riesgos.

## Reflexión final
Al dominar CLIs con la librería estándar obtienes autonomía para automatizar tareas y construir utilidades profesionales que tus compañeras/os pueden ejecutar sin instalar nada más. Estos mismos patrones se reutilizan en scripts de despliegue y herramientas DevOps.
