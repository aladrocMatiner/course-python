# Kapitel 20 · Logging och konfiguration

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Vi använder Pythons standardbibliotek `logging` för att skriva loggar med nivåer (INFO/DEBUG/ERROR), och styr nivån med miljövariabler.

---

## Grundläggande logging
```python
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("Iniciando app")
logging.warning("API lenta")
```

---

## Nivå via miljövariabel
```python
import os
import logging

nivel = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=nivel)
```

---

## Sammanfattning
Logging är din “svarta låda” i produktion. Nästa kapitel: `asyncio`.
