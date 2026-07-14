# Chapter 16 · Environments, Dependencies, and Reproducible Projects

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
You’ll set up virtual environments (`venv`), install dependencies with `pip`, distinguish `pyproject.toml`, requirements, constraints, snapshots, and lock files, and learn how to load environment variables for safe configuration. We’ll practice with a mini project that installs `requests` and uses a `.env` file.

## Learning path
1. **Why isolate dependencies**.
2. **Create and activate `venv`**.
3. **Install packages with `pip`**.
4. **Record dependencies accurately**: declarations, pins, constraints, snapshots, and locks.
5. **Basic `pyproject.toml`**.
6. **Environment variables (`os.environ`) and `.env`**.

## Learning objectives
- Create and activate virtual environments on Windows/macOS/Linux.
- Install libraries and record direct dependencies deliberately.
- Use `pip freeze` as an interpreter/platform-specific environment snapshot, not as a resolver or lock file.
- Explain what stronger evidence a resolved lock provides.
- Load sensitive configuration from environment variables.

## Why it matters
Without isolated environments, one project can break another. Controlled dependencies are the foundation of professional teamwork.

### Mini adventure
Think of each virtual environment as a LEGO box with the exact pieces for one project. If you mix all the pieces from all sets, building anything becomes chaos. With `venv` you keep each set separate and you can always rebuild the model without losing parts.

## Prerequisites
- Basic terminal commands and modules from Chapter 15.
- CPython 3.11+ with `venv` and `pip`; package installation requires network access, but environment-variable practice is local.

## Predict before you run
Before creating the environment, predict which interpreter `python -m pip` will target before and after activation. Verify both paths, then explain why an unexpected path is a setup problem rather than a package bug.

---

## 1. Create and activate `venv`

```bash illustrative
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

- `(.venv)` will appear in your terminal to show you’re inside the environment.
- Use `deactivate` to exit.

If you’re confused about which `pip` you’re using, this trick always works:
```bash illustrative
python -m pip install requests
```
It guarantees you install into the Python you’re running.

---

## 2. Installing packages

```bash illustrative
python -m pip install requests
python -c "import requests; print(requests.__version__)"
```

- Each environment has its own `pip`.

### `requirements.txt`
```bash illustrative
python -m pip freeze > requirements.txt
git add requirements.txt
```

- To recreate the snapshot in another clean environment: `python -m pip install -r requirements.txt`.
- `pip freeze` reports what is installed in requirements-file syntax. It does not resolve a new environment or create a hermetic lock, and the result can differ across Python versions and operating systems.

### Five records with different jobs
- **Project declaration:** `[project].dependencies` states direct runtime requirements, often as compatible ranges. It does not record the complete resolved graph.
- **Direct pin:** `requests==X.Y.Z` fixes one requested version, but says nothing by itself about every transitive dependency.
- **Constraint:** a constraints file limits versions if another requirement needs them; an entry does not cause installation. Example: `python -m pip install -c constraints.txt requests`.
- **Environment snapshot:** `pip freeze` captures the packages installed in the current interpreter and platform in requirements format. It is useful evidence, but it is not a solver result or cross-platform lock.
- **Resolved lock:** a lock-capable tool records the complete resolution and its validity scope, often including hashes and environment markers. Verify that exact tool and target matrix before claiming reproducibility; current `pip lock` support is experimental and its output is scoped to the current Python version and platform.

---

## 3. `pyproject.toml` dependency declaration (optional but modern)

```toml illustrative
[project]
name = "mi-proyecto"
version = "0.1.0"
dependencies = [
  "requests>=2.31",
]
```

- This declares a direct compatible requirement for package metadata. It is not a frozen transitive dependency graph. Build and foreign-directory import verification belong to the installable `src/<package>` example in Chapter 15.

---

## 4. Environment variables

```python runnable
import os
API_KEY = os.environ.get("API_KEY", "dummy")
```

- Don’t commit secrets into your repo.

### `.env` with `python-dotenv`
```bash illustrative
python -m pip install python-dotenv
```

```python illustrative
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.environ["API_KEY"]
```

- Create a `.env` with `API_KEY=value` and add it to `.gitignore`.

Typical `.gitignore`:
```gitignore illustrative
.venv/
.env
__pycache__/
```

---

## Guided exercises (with TODOs)
1. **16-1 · Prepare the environment**
   ```bash todo
   # TODO 1: create .venv and activate it
   # TODO 2: install requests and python-dotenv
   # TODO 3: generate a requirements.txt environment snapshot
   ```
   *Hint*: use `python -m pip` so installation and freezing target the active interpreter, then record its Python and platform scope.

2. **16-2 · Configured script**
   ```python todo
   # TODO 1: create config.py that loads variables from .env
   # TODO 2: use os.environ to read API_KEY
   ```
   *Hint*: call `load_dotenv()`, then fail with a clear message if `API_KEY` is absent instead of silently using a production fallback.

3. **16-3 · Minimal pyproject**
   ```text todo
   # TODO 1: create pyproject.toml with basic dependencies
   # TODO 2: document in README how to install
   # TODO 3: explain why this declaration is not a lock file
   ```
   Note: this is “bonus level”. If you’re starting out, `requirements.txt` is already great.
   *Hint*: keep the `[project]` table minimal and document the exact environment creation and install commands.

---

## Common mistakes
- Forgetting to activate the environment before installing packages.
- Calling one direct pin or a `pip freeze` snapshot a cross-platform lock.
- Expecting a constraints entry to install a package by itself.
- Committing `.env` files with secrets (use `.gitignore`).

---

## Explained solutions
1. **Prepare the environment**: `python -m venv .venv` isolates the project and `python -m pip freeze > requirements.txt` records a snapshot of that environment. Reinstall it in a fresh environment on the declared Python/platform and verify imports; do not broaden that evidence into a hermetic or cross-platform claim.
2. **Configured script**: `load_dotenv()` lets `os.environ` read variables from local files.
3. **pyproject**: document the direct dependency and install instructions, then state that a separate resolver-generated lock is needed for a complete frozen graph.

---

## Summary
Now you know how to create environments, install dependencies, and keep configuration safe using environment variables.

## Checkpoint and rubric
- **Correctness**: a fresh environment on the declared Python/platform installs the selected dependency record.
- **Readability**: setup commands and supported Python version are documented.
- **Error handling**: a missing environment variable fails clearly without revealing secrets.
- **Verification**: recreate the environment and import every direct dependency.
- **Explanation**: distinguish isolation, direct pins, constraints, environment snapshots, resolved locks, and secret storage.

## Closing reflection
These basics let you share projects without “it works on my machine”. Use them every time you start a new repo.
