# Kapitel 20 · Logging och konfiguration

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Vi implementerar logging med standardbiblioteket, nivåerna INFO/DEBUG/ERROR, filer och konfiguration via filer och miljö. Vi använder `logging.config.dictConfig` med exempelvis JSON och nämner YAML som frivillig bonus.

## Lärväg

1. **Varför logga?**
2. **`logging.basicConfig`**.
3. **Nivåer och namngivna loggers**.
4. **Handlers och formatters** för fil och konsol.
5. **`dictConfig` från filer**.
6. **Logging via environment variables**.

## Lärandemål

- Skicka loggar på olika nivåer för felsökning och övervakning.
- Konfigurera format och destinationer.
- Växla nivå mellan dev/prod.
- Centralisera konfiguration i fil.

## Varför det spelar roll

Loggar är tjänstens svarta låda och berättar vad som hände i produktion. Tidig god konfiguration sparar felsökningstid.

### Miniäventyr

Loggen är detektivens anteckningsbok. Tid, plats och allvar låter dig återskapa historien nästa dag.

## Förkunskaper
Rekommenderade tidigare kapitel: 13–16.
Använd CPython 3.11+ i en tillfällig lokal miljö och håll data, hemligheter och tjänster borta från verkliga system.

---

## 1. Grundkonfiguration

```python runnable
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("Iniciando app")
logging.warning("API lenta")
```

- `level` styr synliga meddelanden.
- `format` styr utseendet.

### `print` kontra `logging` på en rad

`print` visar något; `logging` lämnar filtrerbara ledtrådar som kan skrivas till fil.

---

## 2. Namngivna loggers

```python illustrative
logger = logging.getLogger("pedidos")
logger.setLevel(logging.DEBUG)
logger.debug("Detalle interno")
```

En logger per modul kan filtreras selektivt.

---

## 3. Handlers och filer

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

Samma meddelande kan gå till flera destinationer.

---

## 4. Dictionary-konfiguration

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

### Läs JSON-konfiguration säkert
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

### Begränsad filrotation
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

Formatet passar laddning från JSON eller YAML.

---

## 5. Konfiguration mellan miljöer

```python illustrative
import os
nivel = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=nivel)
```

Verbosity kan ändras utan kodändring. Ändra `LOG_LEVEL` och observera filtreringen:

```bash illustrative
# macOS/Linux
LOG_LEVEL=DEBUG python tu_script.py
# Windows PowerShell
$env:LOG_LEVEL="DEBUG"; python tu_script.py
```

---

## Vägledda övningar (med TODO)

1. **20-1 · Modulär logger**

   ```python todo
   # TODO 1: create one logger per module (dominio, servicios)
   # TODO 2: show different levels
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

2. **20-2 · File handler**

   ```python todo
   # TODO 1: write logs into app.log with rotation (use logging.handlers.RotatingFileHandler)
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

3. **20-3 · JSON-konfiguration**

   ```python todo
   # TODO 1: save CONFIG into config.json
   # TODO 2: read the JSON with json.load and apply it with dictConfig
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

Bonus: YAML kräver installation av `pyyaml`.

---

## Vanliga misstag

- Anropa `basicConfig` flera gånger; bara första får effekt.
- Logga tokens eller lösenord.
- Utelämna timestamps och försvåra händelserekonstruktion.

---

## Förklarade lösningar

1. **Modulär logger**: `logging.getLogger(__name__)` i varje fil ger detaljstyrning.
2. **Fil**: `RotatingFileHandler` begränsar filer och skapar backups.
3. **JSON**: öppna `config.json` med `with`, använd `json.load` och `dictConfig`, och fånga fil-/JSON-fel för att välja en känd konsolkonfiguration.

---

## Sammanfattning

Du styr nivåer och destinationer med central konfiguration.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: resultatet uppfyller enhetens kontrakt.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: ett normalfall, ett gränsfall och en återhämtning testas.
- **Verifiering**: exempel och övningar körs i en ren miljö.
- **Förklaring**: du kan motivera besluten och deras risker.

## Avslutande reflektion

Logging förbereder övervakning av riktiga tjänster. Börja enkelt och bygg ut när projektet växer.
