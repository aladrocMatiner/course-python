# Chapter 20 · Logging and Configuration

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll implement logging with the standard library, configure levels (INFO, DEBUG, ERROR), write logs to files, and control configuration using files and environment variables. We’ll also use `logging.config.dictConfig` and store that configuration in a file (for example, JSON). As a bonus (optional), we’ll mention YAML.

## Learning path
1. **Why log?**
2. **Basic config (`logging.basicConfig`)**.
3. **Levels and named loggers**.
4. **Handlers/formatters (file + console)**.
5. **Load config from files (`dictConfig`)**.
6. **Connect logging to environment variables**.

## Learning objectives
- Emit logs with different levels for debugging and monitoring.
- Configure formatting and outputs (console, file).
- Change levels depending on environment (dev/prod).
- Centralize configuration in a file.

## Why it matters
Logs are your black box: they tell you what happened in production. Setting them up well early saves hours of debugging later.

### Mini adventure
Logs are like a detective’s notebook. If you write down each clue (time, place, urgency level), you can reconstruct the story the next day. Without that notebook, you rely on memory — and mysteries become impossible to solve.

## Prerequisites
- Files, exceptions, modules, JSON, and environment variables from Chapters 13–16.
- A disposable local directory so file handlers never write into an important project log.

---

## 1. Basic configuration

```python runnable
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("Iniciando app")
logging.warning("API lenta")
```

- `level` controls what messages are shown.
- `format` controls how they look.

### `print` vs `logging` (in one sentence)
- `print` is for “show something”.
- `logging` is for “leave clues” (filter by level, write to a file, etc.).

---

## 2. Named loggers

```python illustrative
logger = logging.getLogger("pedidos")
logger.setLevel(logging.DEBUG)
logger.debug("Detalle interno")
```

- Use one logger per module so you can filter selectively.

---

## 3. Handlers and files

```python illustrative
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
file_handler = logging.FileHandler("app.log")
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
console.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(console)
logger.addHandler(file_handler)
logger.info("Listo")
```

- You can send the same message to multiple destinations.

---

## 4. Dictionary configuration

```python runnable
import logging.config
CONFIG = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG",
        },
    },
    "formatters": {
        "default": {
            "format": "%(levelname)s %(name)s %(message)s"
        }
    },
    "loggers": {
        "app": {
            "handlers": ["console"],
            "level": "INFO",
        }
    }
}
logging.config.dictConfig(CONFIG)
logger = logging.getLogger("app")
logger.info("Configurado por dict")
```

- Great for loading from JSON/YAML.

### Load JSON configuration safely
```python illustrative
import json
import logging.config
from pathlib import Path

def apply_json_logging_config(path):
    try:
        with Path(path).open(encoding="utf-8") as fh:
            config = json.load(fh)
        logging.config.dictConfig(config)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(f"Invalid logging configuration: {path}") from exc
```

The caller can catch `RuntimeError`, report the bad path, and fall back to a small known-good console configuration.

### Bounded file rotation
```python illustrative
from logging.handlers import RotatingFileHandler

rotating = RotatingFileHandler(
    "app.log",
    maxBytes=1_000_000,
    backupCount=3,
    encoding="utf-8",
)
logger.addHandler(rotating)
```

`maxBytes` bounds each file and `backupCount` bounds the retained backups.

---

## 5. Configuration vs environments

```python illustrative
import os
nivel = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=nivel)
```

- Lets you increase/decrease verbosity without changing code.

Quick challenge: change `LOG_LEVEL` and notice how more/less messages appear.
```bash illustrative
# macOS/Linux
LOG_LEVEL=DEBUG python tu_script.py
# Windows PowerShell
$env:LOG_LEVEL="DEBUG"; python tu_script.py
```

---

## Guided exercises (with TODOs)
1. **20-1 · Modular logger**
   ```python todo
   # TODO 1: create one logger per module (dominio, servicios)
   # TODO 2: show different levels
   ```
   *Hint*: use `logging.getLogger(__name__)` and configure handlers once at the entry point.

2. **20-2 · File handler**
   ```python todo
   # TODO 1: write logs into app.log with rotation (use logging.handlers.RotatingFileHandler)
   ```
   *Hint*: start with `RotatingFileHandler("app.log", maxBytes=1_000_000, backupCount=3)`.

3. **20-3 · Config from JSON (standard library)**
   ```python todo
   # TODO 1: save CONFIG into config.json
   # TODO 2: read the JSON with json.load and apply it with dictConfig
   ```
   *Hint*: open the file with `with`, catch `JSONDecodeError`, and keep a console fallback.

Bonus level (optional): doing the same with YAML requires installing `pyyaml`.

---

## Common mistakes
- Calling `basicConfig` multiple times (only the first call has effect).
- Logging sensitive data (tokens, passwords).
- Missing timestamps: makes event reconstruction harder.

---

## Explained solutions
1. **Modular logger**: `logging.getLogger(__name__)` in each file gives granular control.
2. **File handler**: `RotatingFileHandler` keeps files manageable and creates backups.
3. **JSON config**: open `config.json` with a context manager, call `json.load`, and pass the dict to `dictConfig`. Catch file/JSON errors and apply a known-good console fallback.

---

## Summary
You can control logging levels and send logs to multiple destinations with centralized configuration.

## Checkpoint and rubric
- **Correctness**: levels, handlers, and formatters produce the intended records.
- **Readability**: logger names and configuration keys match module responsibilities.
- **Error handling**: invalid JSON falls back safely and logs never contain secrets.
- **Verification**: test console output and bounded rotation in a temporary directory.
- **Explanation**: explain why configuration belongs at the application boundary.

## Closing reflection
Learning to log prepares you to monitor real services. Start simple and expand as your project grows.
