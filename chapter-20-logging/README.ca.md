# Capítol 20 · Logging i configuració

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Implementarem logging amb la llibreria estàndard, configurarem nivells com INFO, DEBUG i ERROR, escriurem logs en fitxers i controlarem la configuració amb fitxers i variables d'entorn. També utilitzarem `logging.config.dictConfig` i desarem aquesta configuració en un fitxer, per exemple JSON. Com a ampliació opcional, mencionarem YAML.

## Itinerari d'aprenentatge
1. **Per què fem logging?**
2. **Configuració bàsica amb `logging.basicConfig`**.
3. **Nivells i loggers amb nom**.
4. **Handlers i formatters: fitxer i consola**.
5. **Carregar configuració des de fitxers amb `dictConfig`**.
6. **Connectar el logging amb variables d'entorn**.

## Objectius d'aprenentatge
- Emetre logs de nivells diferents per depurar i monitorar.
- Configurar el format i els destins, com la consola i un fitxer.
- Canviar els nivells segons l'entorn de desenvolupament o producció.
- Centralitzar la configuració en un fitxer.

## Per què és important
Els logs són la caixa negra del programa: expliquen què ha passat a producció. Configurar-los bé des del principi estalvia hores de depuració.

### Miniaventura
Els logs són com la llibreta d'un detectiu. Si anotes cada pista, amb hora, lloc i urgència, pots reconstruir la història l'endemà. Sense llibreta només tens la memòria, i els misteris es tornen impossibles de resoldre.

## Prerequisits
- Fitxers, excepcions, mòduls, JSON i variables d'entorn dels capítols 13–16.
- Un directori local d'un sol ús perquè els gestors de fitxer no escriguin mai en un registre important del projecte.

## Prediu abans d'executar
Abans del primer exemple de logging, prediu quins missatges superen el nivell configurat i quin destí els rep. Executa'l, compara els registres observats amb la predicció i identifica la configuració responsable de qualsevol diferència.

---

## 1. Configuració bàsica

```python runnable
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("Iniciando app")
logging.warning("API lenta")
```

- `level` controla quins missatges es mostren.
- `format` controla com es presenten.

### `print` i `logging` en una frase
- `print` serveix per «mostrar una cosa».
- `logging` serveix per «deixar pistes», filtrar per nivell o escriure en un fitxer.

---

## 2. Loggers amb nom

```python illustrative
logger = logging.getLogger("pedidos")
logger.setLevel(logging.DEBUG)
logger.debug("Detalle interno")
```

- Utilitza un logger per mòdul per poder filtrar-los de manera selectiva.

---

## 3. Handlers i fitxers

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

- Pots enviar el mateix missatge a diversos destins.

---

## 4. Configuració amb diccionari

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

Aquest literal és configuració propietat de l'aplicació. `dictConfig` pot resoldre classes importables i la clau especial de fàbrica `"()"`, de manera que no li has de passar mai directament un diccionari arbitrari procedent d'una petició, baixada o fitxer controlat per qui aprèn.

### Carregar un ajust JSON de l'aplicació mitjançant una llista permesa
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

El fitxer conté només `{"level": "INFO"}`. El codi valida aquest esquema mínim i construeix tot el diccionari. Al límit de l'aplicació es capturen els `OSError`, `JSONDecodeError` o `ValueError` esperats, s'informa de la ruta propietat de l'aplicació i s'aplica una configuració de consola coneguda. Si la configuració prové d'una part no fiable, rebutja-la o copia només valors primitius explícitament permesos en una configuració construïda per tu; no reenviïs mai camps `class`, `()`, handler, formatter o filter.

Les [proves complementàries de configuració de logging fiable](trusted_logging.py) demostren que un nivell permès funciona i que es rebutgen diccionaris amb camps de fàbrica o handlers. Des de `chapter-20-logging/`, executa `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

### Rotació acotada de fitxers
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

`maxBytes` limita la mida de cada fitxer i `backupCount` limita les còpies de seguretat conservades.

---

## 5. Configuració segons l'entorn

```python illustrative
import os
nivel = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=nivel)
```

- Permet augmentar o reduir el detall sense modificar el codi.

Repte ràpid: canvia `LOG_LEVEL` i observa com apareixen més o menys missatges.
```bash illustrative
# macOS/Linux
LOG_LEVEL=DEBUG python tu_script.py
# Windows PowerShell
$env:LOG_LEVEL="DEBUG"; python tu_script.py
```

---

## Exercicis guiats (amb TODO)
1. **20-1 · Logger modular**
   ```python todo
   # TODO 1: create one logger per module (dominio, servicios)
   # TODO 2: show different levels
   ```
   *Pista*: usa `logging.getLogger(__name__)` i configura els handlers una sola vegada al punt d'entrada.

2. **20-2 · Handler de fitxer**
   ```python todo
   # TODO 1: write logs into app.log with rotation (use logging.handlers.RotatingFileHandler)
   ```
   *Pista*: comença amb `RotatingFileHandler("app.log", maxBytes=1_000_000, backupCount=3)`.

3. **20-3 · Ajustos fiables des de JSON amb la llibreria estàndard**
   ```python todo
   # TODO 1: save only {"level": "INFO"} in an application-owned config.json
   # TODO 2: validate the allowlisted schema
   # TODO 3: construct the full dict in code and apply it with dictConfig
   ```
   *Pista*: rebutja claus addicionals, especialment `"()"` i `"class"`; captura els errors esperats de fitxer, JSON o valor al límit de l'aplicació i conserva una configuració de consola coneguda.

Nivell extra opcional: per fer el mateix amb YAML cal instal·lar `pyyaml`.

---

## Errors habituals
- Cridar `basicConfig` més d'una vegada; només la primera crida té efecte.
- Registrar dades sensibles, com tokens o contrasenyes.
- No incloure timestamps, cosa que dificulta reconstruir els esdeveniments.
- Tractar JSON arbitrari com a configuració de dades innòcua: `dictConfig` pot resoldre classes i fàbriques, per tant l'entrada ha de ser fiable o reduïda amb una llista permesa estricta.

---

## Solucions explicades
1. **Logger modular**: `logging.getLogger(__name__)` a cada fitxer ofereix control granular.
2. **Handler de fitxer**: `RotatingFileHandler` manté els fitxers en una mida raonable i crea còpies de seguretat.
3. **Ajustos JSON fiables**: carrega el fitxer de l'aplicació, exigeix exactament un `level` permès, construeix en codi el diccionari conegut de handler i formatter i només llavors crida `dictConfig`. Rebutja camps no fiables de handler, classe, filtre i fàbrica; captura els errors esperats de fitxer, JSON o valor i aplica una configuració de consola coneguda.

---

## Resum
Ara pots controlar els nivells de logging i enviar missatges a diversos destins amb una configuració centralitzada.

## Punt de control i rúbrica
- **Correcció**: els nivells, gestors i formatadors produeixen els registres previstos.
- **Llegibilitat**: els noms de logger i les claus de configuració corresponen a les responsabilitats dels mòduls.
- **Errors**: JSON invàlid o una clau no permesa activa un fallback segur, cap diccionari no fiable arriba a `dictConfig` i els logs mai contenen secrets.
- **Verificació**: prova la sortida de consola, el rebuig de camps de fàbrica i la rotació acotada en un directori temporal.
- **Explicació**: explica per què la configuració pertany al límit de l'aplicació i per què l'entrada de `dictConfig` és un límit de confiança, no simples dades d'usuari.

## Reflexió final
Aprendre a registrar esdeveniments et prepara per monitorar serveis reals. Comença amb una configuració senzilla i amplia-la a mesura que creixi el projecte.
