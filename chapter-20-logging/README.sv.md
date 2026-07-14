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
- Filer, undantag, moduler, JSON och miljövariabler från kapitel 13–16.
- En tillfällig lokal katalog så att file handlers aldrig skriver till en viktig projektlogg.

## Förutsäg innan du kör
Före det första loggningsexemplet: förutsäg vilka meddelanden som passerar den konfigurerade nivån och vilket mål som tar emot dem. Kör exemplet, jämför de observerade posterna med din förutsägelse och identifiera den konfiguration som förklarar varje skillnad.

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

Den här literalen är applikationsägd konfiguration. `dictConfig` kan slå upp importerbara klasser och den särskilda fabriksnyckeln `"()"`; skicka därför aldrig en godtycklig ordlista från en begäran, hämtning eller elevstyrd fil direkt till funktionen.

### Läs ett tillåtet applikationsägt JSON-värde
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

Filen innehåller endast `{"level": "INFO"}`. Koden validerar det lilla schemat och bygger hela konfigurationen själv. Applikationsgränsen fångar väntade `OSError`, `JSONDecodeError` eller `ValueError`, rapporterar den applikationsägda sökvägen och använder en känd konsolkonfiguration. Om konfigurationen kommer från en opålitlig part ska den nekas, eller endast uttryckligen tillåtna primitiva värden kopieras till en konfiguration som du själv bygger; vidarebefordra aldrig fält för `class`, `()`, handler, formatter eller filter.

De kompletterande [testerna för betrodd logging-konfiguration](trusted_logging.py) visar att en tillåten nivå fungerar och att ordlistor med fabriks- eller handlerfält avvisas. Kör från `chapter-20-logging/` med `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

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

3. **20-3 · Betrodda inställningar från JSON**

   ```python todo
   # TODO 1: save only {"level": "INFO"} in an application-owned config.json
   # TODO 2: validate the allowlisted schema
   # TODO 3: construct the full dict in code and apply it with dictConfig
   ```
   *Ledtråd*: avvisa extra nycklar, särskilt `"()"` och `"class"`; fånga väntade fil-, JSON- och värdefel vid applikationsgränsen och behåll en känd konsolkonfiguration.

Bonus: YAML kräver installation av `pyyaml`.

---

## Vanliga misstag

- Anropa `basicConfig` flera gånger; bara första får effekt.
- Logga tokens eller lösenord.
- Utelämna timestamps och försvåra händelserekonstruktion.
- Behandla godtycklig JSON som ofarlig datakonfiguration: `dictConfig` kan slå upp klasser och fabriker, så indata måste vara betrodd eller reduceras genom en strikt tillåtelselista.

---

## Förklarade lösningar

1. **Modulär logger**: `logging.getLogger(__name__)` i varje fil ger detaljstyrning.
2. **Fil**: `RotatingFileHandler` begränsar filer och skapar backups.
3. **Betrodda JSON-inställningar**: läs den applikationsägda filen, kräv exakt en tillåten `level`, bygg den kända handler-/formatter-ordlistan i kod och anropa först därefter `dictConfig`. Avvisa opålitliga handler-, klass-, filter- och fabriksfält; fånga väntade fil-, JSON- och värdefel och använd en känd konsolkonfiguration.

---

## Sammanfattning

Du styr nivåer och destinationer med central konfiguration.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: resultatet uppfyller enhetens kontrakt.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: ogiltig JSON eller en otillåten nyckel ger säker fallback, opålitliga ordlistor når aldrig `dictConfig` och loggar innehåller inga hemligheter.
- **Verifiering**: testa konsolutdata, avvisade fabriksfält och begränsad rotation i en tillfällig katalog.
- **Förklaring**: förklara varför konfiguration hör hemma vid applikationsgränsen och varför `dictConfig`-indata är en förtroendegräns, inte harmlösa användardata.

## Avslutande reflektion

Logging förbereder övervakning av riktiga tjänster. Börja enkelt och bygg ut när projektet växer.
