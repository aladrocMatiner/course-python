# Appendix A · Building CLI Tools with the Standard Library

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll design a console command inspired by real tools: it will accept subcommands, required options, and show automatic help. We’ll use `argparse`, `pathlib`, and `logging` so you can ship professional scripts without external dependencies.

## Learning path
1. **Reminder**: `sys.argv` and its limitations.
2. **Basic `argparse` structure**: description, positional and optional args.
3. **Subcommands (`add_subparsers`)**: multiple actions in one tool.
4. **Richer output**: formatting, exit codes, logging.
5. **Basic packaging**: entry point with `if __name__ == "__main__"`.
6. **Light testing**: `argparse` + `pytest` with `capsys`.

## Learning objectives
- Configure an `ArgumentParser` with required and optional arguments.
- Implement subcommands to group functionality.
- Read/write files with `Path` based on user arguments.
- Log messages and return appropriate exit codes.
- Test commands by simulating argv.

## Why it matters
Even though there are stronger frameworks, mastering the standard library avoids dependencies and lets you build internal tools, deploy scripts, and data utilities quickly.

### Mini adventure
A CLI is like a remote control for your program: instead of clicking, you type short commands. If the remote is well designed (help + clear options), anyone can use it without fear.

---

## 1. Basic `argparse`

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

- `nargs="*"` allows multiple tags.
- `parser.parse_args()` already validates and generates help.

### Generated help
```
python cli.py --help
```
It prints description, arguments, and usage automatically.

---

## 2. Subcommands

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

- `dest="comando"` tells you which subcommand was used.
- For `append=True` you can use `archivo.open("a")` or write manually (Python 3.11+ supports `append=True` in some `Path` helpers).

---

## 3. Logging and exit codes

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

- `sys.exit(0)` means success; any non‑zero code means error.

---

## 4. Good practices
- Keep logic in functions for testing and reuse.
- Use `Path` for paths; don’t concatenate strings.
- Add examples in `ArgumentParser(description=...)` and `epilog`.

### Recommended structure
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

- Lets you pass custom `argv` during tests.

---

## Guided exercises (with TODOs)
1. **A-1 · Expenses CLI**
   ```python
   # TODO 1: "add" subcommand with amount and description
   # TODO 2: "report" subcommand that shows the total
   # TODO 3: store data in CSV format using Path
   ```
   *Hint*: `Path("gastos.csv").open("a", newline="", encoding="utf-8")`.

2. **A-2 · Configurable logger**
   ```python
   # TODO 1: add --debug option that sets logging to DEBUG
   # TODO 2: print messages only if the level matches
   # TODO 3: try capsys in pytest
   ```
   *Hint*: `if args.debug: logging.getLogger().setLevel(logging.DEBUG)`.

---

## Common mistakes
- Forgetting `dest` or `required=True` for subparsers ⇒ the tool doesn’t know what to run.
- Not wrapping logic in `try/except` ⇒ raw tracebacks for expected errors.
- Using `print` for everything instead of logging ⇒ hard to filter.
- Not testing `argparse` with simulated arguments.

---

## Explained solutions
1. **Expenses CLI**: `subparsers.add_parser("add")` and `"report"`; write rows into `gastos.csv`. `report` reads and sums values.
2. **Configurable logger**: `parser.add_argument("--debug", action="store_true")`; when enabled, increase logger level and show detailed messages. `pytest` captures output with `capsys.readouterr()`.

---

## Summary
With `argparse`, `logging`, and `pathlib` you can create robust, self‑documenting console tools that are easy to test — without external frameworks.

## Closing reflection
When you master CLIs with the standard library, you gain autonomy to automate tasks and build professional utilities your teammates can run without installing anything else. These patterns show up again in deploy scripts and DevOps tools.
