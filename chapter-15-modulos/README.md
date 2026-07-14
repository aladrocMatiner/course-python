# Chapter 15 · Modules, Packages, and Code Organization

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
You’ll learn to split a project into files and folders, import functions/classes, create reusable packages, and avoid circular imports. We’ll simulate a mini app with `dominio`, `servicios`, and `cli` modules so you see how they connect.

## Learning path
1. **Mental model**: one `.py` file = one module.
2. **Basic imports**: `import`, `from ... import ...`.
3. **Folders as packages**: `__init__.py` and relative imports.
4. **Installable `src/<package>` structure**.
5. **Avoiding import cycles**.
6. **Light packaging** (`if __name__ == "__main__"`).

## Learning objectives
- Organize code into coherent modules.
- Import functions and classes from other files instead of duplicating logic.
- Create packages with `__init__.py` and understand relative imports.
- Detect and fix circular imports.
- Prepare a clean “main entry point” module.
- Build, install, and import a package outside its source directory.

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

## Predict before you run
Before importing the first module, predict which file supplies `hola` and what directory Python must be able to find. After running the example, inspect the imported module path and compare it with your prediction.

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

## 3. Bonus level: an installable `src` layout (optional)
If you’re just starting, you can skip this section. In a real `src` layout, `src/` is only a container: the importable package must be one level below it. The package below is `mi_app`, so application code imports `mi_app`, never `src`.

```text illustrative
project/
├── pyproject.toml
├── src/
│   └── mi_app/
│       ├── __init__.py
│       ├── domain.py
│       └── cli.py
└── tests/
```

`pyproject.toml` tells the build backend to discover packages below `src`:

```toml illustrative
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "course-mi-app"
version = "0.1.0"
requires-python = ">=3.11"

[tool.setuptools.packages.find]
where = ["src"]
```

### Build, install, and verify from somewhere else
Create a fresh virtual environment, install the project, and deliberately change the process working directory before importing. That final step proves Python is using the installed distribution instead of accidentally importing from the checkout:

```bash illustrative
# macOS/Linux (outside the checkout):
python -m venv /tmp/course-mi-app-venv
source /tmp/course-mi-app-venv/bin/activate
# Windows PowerShell alternative:
# python -m venv "$env:TEMP\course-mi-app-venv"
# & "$env:TEMP\course-mi-app-venv\Scripts\Activate.ps1"
# Run the remaining commands from project/
python -m pip install .
python -m unittest discover -s tests -v
python -c "import os, tempfile; os.chdir(tempfile.mkdtemp()); import mi_app; print(mi_app.__name__)"
```

The environment path is deliberately outside the checkout; deactivate and delete it after the exercise. `pip install .` uses PEP 517 build isolation and may need to obtain `setuptools>=68` plus the backend-reported `wheel` requirement from an index or an already populated cache. For an offline lab, provision reviewed compatible wheels for both build inputs in advance. Use `--no-build-isolation` only when the backend and its build requirements are already installed and their versions have been checked; that fallback is not isolated-build evidence.

The import command must print `mi_app`. A complete companion project is available at [the Chapter 15 installable `src` example](examples/src-layout/). If the foreign-directory import raises `ModuleNotFoundError`, confirm the active interpreter with `python -m pip --version`, reinstall into that environment, and check that `src/mi_app/__init__.py` exists. Do not repair this by adding the checkout to `PYTHONPATH`, because that would hide a packaging error.

Maintainers can run `python -B chapter-15-modulos/examples/src-layout/tools/verify_artifact.py` from the repository root. The verifier builds a temporary copy with PEP 517, inspects the wheel contents and metadata, installs that exact wheel into a second environment, and runs `pip check`, the installed console entry point, the test, and a foreign-directory import before deleting its temporary artifacts. In an offline lab, pass `--wheelhouse PATH` containing reviewed compatible `setuptools>=68` and `wheel` distributions; failure to provision either input is a prerequisite failure, not a successful isolated build.

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
   # TODO 1: create src/mi_app/dominio.py with class Producto
   # TODO 2: create src/mi_app/precios.py and use Producto
   # TODO 3: add pyproject.toml and install the distribution in a clean venv
   ```
   Extra: add a method `aplicar_descuento(porcentaje)` in `Producto`.
   Hint: `src` is not the package; make `mi_app` explicit with `__init__.py` and import domain objects in only one direction.

2. **15-2 · Modular CLI**
   ```python todo
   # TODO 1: create src/mi_app/cli.py that imports functions from servicios
   # TODO 2: after installation, run python -m mi_app.cli to validate the import path
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
- Putting `__init__.py` directly under `src/` and importing `src`: the real package belongs under `src/<package>/` and should be installed.

---

## Explained solutions
1. **Domain vs services**: place both modules under `src/mi_app/`, configure package discovery in `pyproject.toml`, install in a fresh environment, and verify `import mi_app` after changing to a temporary directory. Services import domain to avoid mixing responsibilities.
2. **Modular CLI**: `mi_app/cli.py` only orchestrates; business logic lives in `servicios`. Running `python -m mi_app.cli` after installation exercises the package import path and remains easy to test.
3. **Fix cycle**: moving shared functions into `utils` removes circular dependencies and clarifies layers.

---

## Summary
Splitting code into modules and packages keeps your project organized. You can now import only what you need and create clean entry points.

## Checkpoint and rubric
- **Correctness**: the distribution installs cleanly and its real package imports outside the project root.
- **Readability**: module names reflect one responsibility each.
- **Error handling**: import failures include a reproducible command and recovery check.
- **Verification**: run the module and the fresh-process, foreign-working-directory import test.
- **Explanation**: describe why dependency direction prevents cycles.

## Closing reflection
Always ask: “Where should this piece of logic live?” Clear modules prepare you for bigger projects and frameworks like Django.
