"""Allowlisted logging configuration for Chapter 20."""

import json
import logging
import logging.config
from pathlib import Path


ALLOWED_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def build_logging_config(settings: object) -> dict[str, object]:
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
        "formatters": {"default": {"format": "%(levelname)s %(name)s %(message)s"}},
        "root": {"handlers": ["console"], "level": level},
    }


def apply_trusted_json_logging_config(path: str | Path) -> None:
    with Path(path).open(encoding="utf-8") as stream:
        settings = json.load(stream)
    logging.config.dictConfig(build_logging_config(settings))
