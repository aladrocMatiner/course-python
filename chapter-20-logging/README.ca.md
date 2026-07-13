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
Capítols previs recomanats: 13–16.
Usa CPython 3.11+ en un entorn local d’un sol ús i mantén les dades, els secrets i els serveis fora de sistemes reals.

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

### Carregar configuració JSON de manera segura
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

- És ideal per carregar la configuració des de JSON o YAML.

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
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

2. **20-2 · Handler de fitxer**
   ```python todo
   # TODO 1: write logs into app.log with rotation (use logging.handlers.RotatingFileHandler)
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

3. **20-3 · Configuració des de JSON amb la llibreria estàndard**
   ```python todo
   # TODO 1: save CONFIG into config.json
   # TODO 2: read the JSON with json.load and apply it with dictConfig
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

Nivell extra opcional: per fer el mateix amb YAML cal instal·lar `pyyaml`.

---

## Errors habituals
- Cridar `basicConfig` més d'una vegada; només la primera crida té efecte.
- Registrar dades sensibles, com tokens o contrasenyes.
- No incloure timestamps, cosa que dificulta reconstruir els esdeveniments.

---

## Solucions explicades
1. **Logger modular**: `logging.getLogger(__name__)` a cada fitxer ofereix control granular.
2. **Handler de fitxer**: `RotatingFileHandler` manté els fitxers en una mida raonable i crea còpies de seguretat.
3. **Configuració JSON**: obre `config.json` amb `with`, aplica `json.load` i `dictConfig`, i captura errors de fitxer/JSON per usar una configuració de consola coneguda.

---

## Resum
Ara pots controlar els nivells de logging i enviar missatges a diversos destins amb una configuració centralitzada.

## Punt de control i rúbrica
- **Correcció**: el resultat compleix el contracte de la unitat.
- **Llegibilitat**: els noms i les responsabilitats s’entenen a la primera.
- **Errors**: es proven un cas vàlid, un límit i una recuperació.
- **Verificació**: els exemples i els exercicis s’executen en un entorn net.
- **Explicació**: pots justificar les decisions i els riscos.

## Reflexió final
Aprendre a registrar esdeveniments et prepara per monitorar serveis reals. Comença amb una configuració senzilla i amplia-la a mesura que creixi el projecte.
