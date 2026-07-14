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
- Funciones, archivos, excepciones, módulos, logging y fixtures básicos de pytest.
- Un directorio local desechable; las pruebas de comandos deben usar `tmp_path` en vez de archivos reales de la persona usuaria.

## Predice antes de ejecutar
Antes de invocar el primer parser, predice su salida y su comportamiento de terminación con argumentos válidos, si falta la entrada obligatoria y con `--help`. Prueba cada caso con datos desechables y compara el resultado con tu predicción.

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

## 3. Un contrato estable `main(argv) -> int`

Separa el parser, la lógica de dominio y la salida del proceso. Normalmente `argparse` lanza `SystemExit` cuando la sintaxis no es válida; este pequeño parser convierte solo los errores de uso en un valor que `main` puede mapear al código `2`.

```python illustrative
import argparse
import sys
from pathlib import Path

class CliUsageError(ValueError):
    pass

class CourseArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise CliUsageError(message)

def build_parser():
    parser = CourseArgumentParser(prog="notes")
    subparsers = parser.add_subparsers(dest="command", required=True)
    show = subparsers.add_parser("show")
    show.add_argument("path", type=Path)
    return parser

def main(argv=None):
    try:
        args = build_parser().parse_args(argv)
    except CliUsageError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        return 2

    try:
        print(args.path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"note not found: {args.path}", file=sys.stderr)
        return 1
    except PermissionError:
        print(f"cannot read note: {args.path}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- `0` significa éxito, `1` un fallo esperado de archivo o ejecución y `2` un uso incorrecto del comando.
- Captura solo los fallos que el comando pueda explicar y de los que pueda recuperarse. Un error de programación inesperado debe conservar su traceback para la persona que desarrolla, en vez de convertirse en un mensaje vago.
- El [módulo complementario del contrato CLI](cli_contract.py) también acepta flujos de salida inyectables para que las pruebas no modifiquen el estado global del proceso.

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
    # Convert expected usage/domain failures into documented return codes.
    # Let unexpected programming errors remain visible.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

### Prueba de argv
```python illustrative
def test_build_parser_add():
    parser = build_parser()
    args = parser.parse_args(["add", "Learn argparse"])
    assert args.command == "add"
    assert args.text == "Learn argparse"
```

- Permite pasar `argv` personalizados durante pruebas. Comprueba también que `main(argv_válido) == 0`, que un archivo ausente devuelve `1` y que una sintaxis inválida devuelve `2`. Desde `appendix-cli-parser/`, ejecuta la suite complementaria de la biblioteca estándar con `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

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
- Capturar `Exception` alrededor de todo el comando ⇒ los defectos de programación se convierten en errores engañosos para quien usa la herramienta; captura solo excepciones esperadas de uso, archivo y dominio.
- Usar `print` para todo en lugar de logging ⇒ difícil de filtrar.
- No testear `argparse` con argumentos simulados.

---

## Explicación de soluciones
1. **CLI de gastos**: `subparsers.add_parser("add")` y `subparsers.add_parser("report")`; abre `Path("gastos.csv")` en modo `"a"` para añadir filas sin sobrescribirlas. `main(argv)` devuelve `0` para `add` o `report` válidos, `1` para un CSV esperado ausente o ilegible y `2` para sintaxis inválida. Captura solo `FileNotFoundError`, `PermissionError`, `csv.Error` y tu error de dominio allí donde puedas explicarlos.
2. **Logger configurable**: activa `--debug` con `store_true` y comprueba registros con `caplog`; reserva `capsys` para `stdout` y `stderr`.

---

## Resumen
Con `argparse`, `logging` y `pathlib` puedes crear herramientas de consola robustas, autodescriptivas y fáciles de probar, sin depender de frameworks externos.

## Punto de control y rúbrica
- **Corrección**: las opciones obligatorias, los subcomandos y los códigos de salida corresponden al contrato del comando.
- **Legibilidad**: el texto de ayuda y los nombres de los comandos explican su propósito.
- **Errores**: los archivos ausentes y los argumentos inválidos producen códigos de retorno estables y claros, mientras los defectos inesperados conservan sus tracebacks.
- **Verificación**: simula `argv`, comprueba `0/1/2`, usa `tmp_path` y verifica los logs con `caplog`.
- **Explicación**: distingue el comportamiento del parser, la lógica de dominio y la presentación en terminal.

## Reflexión final
Al dominar CLIs con la librería estándar obtienes autonomía para automatizar tareas y construir utilidades profesionales que tus compañeras/os pueden ejecutar sin instalar nada más. Estos mismos patrones se reutilizan en scripts de despliegue y herramientas DevOps.
