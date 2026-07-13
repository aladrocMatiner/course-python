# Chapter 15 · Modules, Packages, and Code Organization

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
You’ll learn to split a project into files and folders, import functions/classes, create reusable packages, and avoid circular imports. We’ll simulate a mini app with `dominio`, `servicios`, and `cli` modules so you see how they connect.

## Learning path
1. **Mental model**: one `.py` file = one module.
2. **Basic imports**: `import`, `from ... import ...`.
3. **Folders as packages**: `__init__.py`, relative imports, `PYTHONPATH`.
4. **Recommended project structure**.
5. **Avoiding import cycles**.
6. **Light packaging** (`if __name__ == "__main__"`).

## Learning objectives
- Organize code into coherent modules.
- Import functions and classes from other files instead of duplicating logic.
- Create packages with `__init__.py` and understand relative imports.
- Detect and fix circular imports.
- Prepare a clean “main entry point” module.

## Why it matters
Real projects don’t fit in a single file. Separating responsibilities makes testing, reuse, and collaboration easier.

### Mini adventure
Imagine your favorite game is built by different teams: characters, levels, music. If everything were in one file, collaboration would be impossible. Modules are like tidy rooms in a house — everyone knows where their work belongs, and it’s easy to find later.

### How to practice this chapter (super simple)
1. Create two files: `saludos.py` and `app.py` (in the same folder).
2. Run `python app.py`.
3. If you get an error, read the error name and the line number — it’s normal while learning.

## Prerequisites
- Functions, classes, imports from the standard library, and basic terminal navigation.
- A local CPython 3.11+ environment and permission to create a disposable project folder.

---

## 1. Basic modules
`saludos.py`
```python runnable
def hola(nombre):
    return f"Hola {nombre}!"
```

`app.py`
```python illustrative
import saludos
print(saludos.hola("Taha"))
```

Expected output:
```text illustrative
Hola Taha!
```

Quick challenge: replace `"Taha"` with your name and run again.

### `from ... import ...`
```python illustrative
from saludos import hola
print(hola("Frej"))
```

- Avoid `import *` — it makes it hard to know what comes from where.

---

## 2. Packages
Structure:
```text illustrative
mi_app/
    __init__.py
    dominio.py
    servicios.py
main.py
```

`mi_app/dominio.py`
```python runnable
class Pedido:
    def __init__(self, id, total):
        self.id = id
        self.total = total
```

`mi_app/servicios.py`
```python illustrative
from .dominio import Pedido

def procesar_pedido(pedido: Pedido):
    # Ejemplo: aplicar un descuento del 10%
    pedido.total = pedido.total * 0.9
    return pedido
```

`main.py`
```python illustrative
from mi_app.dominio import Pedido
from mi_app.servicios import procesar_pedido

pedido = Pedido(1, 100)
pedido = procesar_pedido(pedido)
print(pedido.total)
```

Run:
```bash illustrative
python main.py
```

Expected output:
```text illustrative
90.0
```

- `.` means a relative import (same package).
- `__init__.py` can be empty; it tells Python “this folder is a package”.

---

## 3. Bonus level: a more professional structure (optional)
If you’re just starting, you can skip this section. But if you want to work “like a real project”, this structure helps a lot:

```text illustrative
project/
├── src/
│   ├── __init__.py
│   ├── dominio/
│   │   ├── __init__.py
│   │   └── pedidos.py
│   ├── servicios/
│   │   ├── __init__.py
│   │   └── descuentos.py
│   └── cli.py
└── tests/
```

- `src/` contains the code; `tests/` keeps tests separate.
- Because this teaching layout makes `src` the package, use imports such as `from src.dominio.pedidos import Pedido`.

### Run from the project root
When you use packages, run from the project root folder. A common trick is:

```bash illustrative
python -m src.cli
```

That means: “run `cli.py` as part of the `src` package”, which makes imports work more reliably.

### Verify the package contract
Verify the package contract before adding more code:

```bash illustrative
python -c "from src.dominio.pedidos import Pedido; print(Pedido.__name__)"
```

The command must print `Pedido`. If it raises `ModuleNotFoundError`, check that you are at `project/` and that both `__init__.py` files exist.

---

## 4. Avoiding circular imports

```python illustrative
# dominio.py
from servicios import descuentos  # ⚠️ if servicios imports dominio → cycle
```

If this happens, it’s not “your fault”: it’s a normal problem when projects grow.

Solutions:
- Move shared logic into an independent module.
- Use local imports inside functions to break the cycle:
```python illustrative
def calcular(total):
    # Local import: only happens when the function is called
    from servicios.descuentos import aplicar_descuento
    return aplicar_descuento(total)
```
(The idea is that `aplicar_descuento` lives in something like `servicios/descuentos.py`.)

---

## 5. Entry point

```python runnable
# cli.py
def main():
    print("Hola! Soy tu CLI")

if __name__ == "__main__":
    main()
```

- Lets you run `python cli.py` or import `main` in tests without executing automatically.

---

## Guided exercises (with TODOs)
1. **15-1 · Separate domain and services**
   ```python todo
   # TODO 1: create dominio/productos.py with class Producto
   # TODO 2: create servicios/precios.py and use Producto
   ```
   Extra: add a method `aplicar_descuento(porcentaje)` in `Producto`.
   Hint: make each package explicit with `__init__.py` and import domain objects in only one direction.

2. **15-2 · Modular CLI**
   ```python todo
   # TODO 1: create cli.py that imports functions from servicios
   # TODO 2: run python -m cli to validate the import path
   ```
   Hint: if you get `ModuleNotFoundError`, make sure you run from the correct folder.

3. **15-3 · Fix an import cycle**
   ```python todo
   # TODO 1: create a small artificial cycle and fix it by moving functions to utils
   ```
   Edge case: write a test that imports both modules to confirm there is no cycle anymore.
   Hint: move the smallest shared dependency to `utils.py`, then start a fresh Python process for the import test.

---

## Common mistakes
- Wrong relative imports (`from .. import` without `__init__.py`).
- Duplicating code across modules instead of importing it.
- Running from different directories and breaking paths (use `python -m`).

---

## Explained solutions
1. **Domain vs services**: each area gets its own module; services import domain to avoid mixing responsibilities.
2. **Modular CLI**: `cli.py` only orchestrates; business logic lives in `servicios`. Easier to test.
3. **Fix cycle**: moving shared functions into `utils` removes circular dependencies and clarifies layers.

---

## Summary
Splitting code into modules and packages keeps your project organized. You can now import only what you need and create clean entry points.

## Checkpoint and rubric
- **Correctness**: the package imports from the project root and has one working entry point.
- **Readability**: module names reflect one responsibility each.
- **Error handling**: import failures include a reproducible command and recovery check.
- **Verification**: run the module and the fresh-process import test.
- **Explanation**: describe why dependency direction prevents cycles.

## Closing reflection
Always ask: “Where should this piece of logic live?” Clear modules prepare you for bigger projects and frameworks like Django.
