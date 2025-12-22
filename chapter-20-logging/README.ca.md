# Capítol 20 · Logging i configuració

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Implementarem logging amb la llibreria estàndard, configurarem nivells (INFO/DEBUG/ERROR), escriurem logs a fitxers i controlarem configuració amb fitxers i variables d’entorn. També veurem `logging.config.dictConfig`.

## Objectius d’aprenentatge
- Escriure logs amb diferents nivells.
- Configurar format i destí (consola i fitxer).
- Canviar el nivell segons entorn (dev/prod) sense tocar codi.
- Centralitzar configuració en un diccionari/fitxer.

---

## Configuració bàsica
```python
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("Iniciando app")
logging.warning("API lenta")
```

---

## Handlers (consola + fitxer)
```python
import logging

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

---

## Config per diccionari
```python
import logging.config
CONFIG = {
    "version": 1,
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "default", "level": "DEBUG"}},
    "formatters": {"default": {"format": "%(levelname)s %(name)s %(message)s"}},
    "loggers": {"app": {"handlers": ["console"], "level": "INFO"}},
}
logging.config.dictConfig(CONFIG)
```

---

## Resum
Amb logging tens una “caixa negra” per entendre què passa en producció. Si el configures bé, depurar és molt més fàcil.
