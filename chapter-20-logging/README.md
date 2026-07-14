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

## Predict before you run
Before the first logging example, predict which messages pass the configured level and which destination receives them. Run it, compare the observed records with your prediction, and identify the configuration responsible for any difference.

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

- This literal is application-owned configuration. `dictConfig` may resolve importable classes and the special `"()"` factory key, so never pass an arbitrary dictionary from a request, download, or learner-controlled file directly to it.

### Load an allowlisted application-owned JSON setting
```python illustrative
import json
import logging.config
from pathlib import Path

ALLOWED_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

def build_logging_config(settings):
    if not isinstance(settings, dict) or set(settings) != {"level"}:
        raise ValueError("logging settings must contain only 'level'")
    level = settings["level"]
    if not isinstance(level, str) or level not in ALLOWED_LEVELS:
        raise ValueError("unsupported logging level")
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": level,
            }
        },
        "formatters": {
            "default": {"format": "%(levelname)s %(name)s %(message)s"}
        },
        "root": {"handlers": ["console"], "level": level},
    }

def apply_application_logging_settings(path):
    with Path(path).open(encoding="utf-8") as fh:
        settings = json.load(fh)
    logging.config.dictConfig(build_logging_config(settings))
```

The bundled file contains only `{"level": "INFO"}`. The code validates that tiny schema and constructs the full dictionary itself. The application boundary catches expected `OSError`, `JSONDecodeError`, or `ValueError`, reports the bad application-owned path, and falls back to a known-good console configuration. If configuration comes from an untrusted party, refuse it or copy only explicitly allowlisted primitive values into a configuration you construct; never forward its `class`, `()`, handler, formatter, or filter fields.

The companion [trusted logging configuration tests](trusted_logging.py) prove that an allowed level works and dictionaries containing factory or handler fields are rejected. From `chapter-20-logging/`, run `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

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

3. **20-3 · Trusted settings from JSON (standard library)**
   ```python todo
   # TODO 1: save only {"level": "INFO"} in an application-owned config.json
   # TODO 2: validate the allowlisted schema
   # TODO 3: construct the full dict in code and apply it with dictConfig
   ```
   *Hint*: reject extra keys (especially `"()"` and `"class"`), catch expected file/JSON/value errors at the application boundary, and keep a known-good console fallback.

Bonus level (optional): doing the same with YAML requires installing `pyyaml`.

---

## Common mistakes
- Calling `basicConfig` multiple times (only the first call has effect).
- Logging sensitive data (tokens, passwords).
- Missing timestamps: makes event reconstruction harder.
- Treating arbitrary JSON as data-only configuration: `dictConfig` can resolve classes and factories, so its input must be trusted or reduced through a strict allowlist.

---

## Explained solutions
1. **Modular logger**: `logging.getLogger(__name__)` in each file gives granular control.
2. **File handler**: `RotatingFileHandler` keeps files manageable and creates backups.
3. **Trusted JSON settings**: load the application-owned file, require exactly one allowed `level`, build the known handler/formatter dictionary in code, and only then call `dictConfig`. Reject untrusted handler, class, filter, and factory fields; catch expected file/JSON/value errors and apply a known-good console fallback.

---

## Summary
You can control logging levels and send logs to multiple destinations with centralized configuration.

## Checkpoint and rubric
- **Correctness**: levels, handlers, and formatters produce the intended records.
- **Readability**: logger names and configuration keys match module responsibilities.
- **Error handling**: invalid JSON or a disallowed key falls back safely, untrusted dictionaries never reach `dictConfig`, and logs never contain secrets.
- **Verification**: test console output and bounded rotation in a temporary directory.
- **Explanation**: explain why configuration belongs at the application boundary and why `dictConfig` input is a trust boundary rather than harmless user data.

## Closing reflection
Learning to log prepares you to monitor real services. Start simple and expand as your project grows.
