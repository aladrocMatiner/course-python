# Kapitel 15 · Moduler, packages och kodorganisation

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Du delar projekt i filer och kataloger, importerar funktioner och klasser, skapar återanvändbara packages och undviker cirkulära imports. En miniapp med `dominio`, `servicios` och `cli` visar kopplingarna.

## Lärväg

1. **Mental modell**: en `.py`-fil är en modul.
2. **Imports**: `import` och `from ... import ...`.
3. **Kataloger som packages**: `__init__.py` och relativa imports.
4. **Installerbar struktur `src/<package>`**.
5. **Undvika importcykler**.
6. **Entry point** med `if __name__ == "__main__"`.

## Lärandemål

- Organisera kod i sammanhängande moduler.
- Importera i stället för att duplicera logik.
- Skapa packages med `__init__.py` och förstå relativa imports.
- Upptäcka och reparera cirkulära imports.
- Förbereda en ren huvudmodul.
- Bygga, installera och importera ett package utanför källkatalogen.

## Varför det spelar roll

Riktiga projekt ryms inte i en fil. Separerade ansvar förenklar testning, återanvändning och samarbete.

### Miniäventyr

Ett spel byggs av team för figurer, nivåer och musik. Allt i en fil vore omöjligt att samarbeta kring. Moduler är husets ordnade rum.

### Öva kapitlet enkelt

1. Skapa `saludos.py` och `app.py` i samma katalog.
2. Kör `python app.py`.
3. Läs feltyp och radnummer om det inte fungerar; fel är normala under lärandet.

## Förkunskaper
- Funktioner, klasser, imports från standardbiblioteket och grundläggande navigering i terminalen.
- En lokal miljö med CPython 3.11+ och behörighet att skapa en tillfällig projektkatalog.

## Förutsäg innan du kör
Innan du importerar den första modulen: förutsäg vilken fil som tillhandahåller `hola` och vilken katalog Python måste kunna hitta. Kör exemplet, granska den importerade modulens sökväg och jämför den med din förutsägelse.

---

## 1. Grundläggande moduler

`saludos.py`:

```python runnable
def hola(nombre):
    return f"Hola {nombre}!"
```

`app.py`:

```python illustrative
import saludos
print(saludos.hola("Taha"))
```

Förväntad utdata:

```text illustrative
Hola Taha!
```

Byt snabbt ut `"Taha"` mot ditt namn och kör igen.

### `from ... import ...`

```python illustrative
from saludos import hola
print(hola("Frej"))
```

Undvik `import *`; annars blir ursprunget för namn oklart.

---

## 2. Packages

Struktur:

```text illustrative
mi_app/
    __init__.py
    dominio.py
    servicios.py
main.py
```

`mi_app/dominio.py`:

```python runnable
class Pedido:
    def __init__(self, id, total):
        self.id = id
        self.total = total
```

`mi_app/servicios.py`:

```python illustrative
from .dominio import Pedido

def procesar_pedido(pedido: Pedido):
    # Ejemplo: aplicar un descuento del 10%
    pedido.total = pedido.total * 0.9
    return pedido
```

`main.py`:

```python illustrative
from mi_app.dominio import Pedido
from mi_app.servicios import procesar_pedido

pedido = Pedido(1, 100)
pedido = procesar_pedido(pedido)
print(pedido.total)
```

Kör:

```bash illustrative
python main.py
```

Förväntad utdata:

```text illustrative
90.0
```

- `.` är en relativ import inom samma package.
- `__init__.py` kan vara tom och markerar katalogen som package.

---

## 3. Bonusnivå: installerbar `src`-layout (frivillig)

Nybörjare kan hoppa över detta. I en riktig `src`-layout är `src/` bara en behållare; det importerbara paketet ligger en nivå under. Här är paketet `mi_app`, så koden importerar `mi_app`, aldrig `src`.

```text illustrative
project/
├── pyproject.toml
├── src/
│   └── mi_app/
│       ├── __init__.py
│       ├── domain.py
│       └── cli.py
└── tests/
```

`pyproject.toml` låter byggbackend hitta packages under `src`:

```toml illustrative
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "course-mi-app"
version = "0.1.0"
requires-python = ">=3.11"

[tool.setuptools.packages.find]
where = ["src"]
```

### Bygg, installera och verifiera från en annan plats
Installera projektet i en ny virtuell miljö och byt avsiktligt arbetskatalog före import. Då visar du att Python använder den installerade distributionen och inte råkar importera checkouten:

```bash illustrative
# macOS/Linux (outside the checkout):
python -m venv /tmp/course-mi-app-venv
source /tmp/course-mi-app-venv/bin/activate
# Windows PowerShell alternative:
# python -m venv "$env:TEMP\course-mi-app-venv"
# & "$env:TEMP\course-mi-app-venv\Scripts\Activate.ps1"
# Run the remaining commands from project/
python -m pip install .
python -m unittest discover -s tests -v
python -c "import os, tempfile; os.chdir(tempfile.mkdtemp()); import mi_app; print(mi_app.__name__)"
```

Miljösökvägen ligger avsiktligt utanför checkouten; avaktivera och radera den efter övningen. `pip install .` använder PEP 517-isolering och kan behöva hämta `setuptools>=68` samt backendens rapporterade krav `wheel` från ett index eller en redan fylld cache. För ett offlinelabb ska du i förväg ordna granskade kompatibla wheels för båda byggindata. Använd `--no-build-isolation` bara när backend och dess byggkrav redan är installerade och versionerna är kontrollerade; den fallbacken bevisar inte ett isolerat bygge.

Importen ska skriva `mi_app`. En komplett kopia finns i [kapitel 15:s installerbara `src`-exempel](examples/src-layout/). Kontrollera annars `python -m pip --version`, installera om i rätt miljö och bekräfta `src/mi_app/__init__.py`. Lägg inte checkouten i `PYTHONPATH`; det döljer ett packagingfel.

Bokunderhållare kan köra `python -B chapter-15-modulos/examples/src-layout/tools/verify_artifact.py` från repositoryroten. Verifieraren bygger en tillfällig kopia med PEP 517, granskar wheelens innehåll och metadata, installerar exakt den wheelen i en andra miljö och kör `pip check`, den installerade entry pointen, testet och en import från en främmande katalog innan tillfälliga artefakter tas bort. I ett offlinelabb anger du `--wheelhouse SÖKVÄG` med granskade kompatibla distributioner av `setuptools>=68` och `wheel`; om någon av dem saknas är det ett prerequisitfel, inte ett lyckat isolerat bygge.

---

## 4. Undvika cirkulära imports

```python illustrative
# dominio.py
from servicios import descuentos  # ⚠️ if servicios imports dominio → cycle
```

Problemet är normalt när projekt växer. Flytta gemensam logik till en oberoende modul eller använd lokal import:

```python illustrative
def calcular(total):
    # Local import: only happens when the function is called
    from servicios.descuentos import aplicar_descuento
    return aplicar_descuento(total)
```

Här ligger `aplicar_descuento` exempelvis i `servicios/descuentos.py`.

---

## 5. Entry point

```python runnable
# cli.py
def main():
    print("Hola! Soy tu CLI")

if __name__ == "__main__":
    main()
```

Nu kan `python cli.py` köras, medan tester kan importera `main` utan automatisk körning.

---

## Vägledda övningar (med TODO)

1. **15-1 · Separera domain och services**

   ```python todo
   # TODO 1: create src/mi_app/dominio.py with class Producto
   # TODO 2: create src/mi_app/precios.py and use Producto
   # TODO 3: add pyproject.toml and install the distribution in a clean venv
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

   Extra: lägg `aplicar_descuento(porcentaje)` i `Producto`.
   Ledtråd: `src` är inte paketet; paketet är `mi_app`.

2. **15-2 · Modulär CLI**

   ```python todo
   # TODO 1: create src/mi_app/cli.py that imports functions from servicios
   # TODO 2: after installation, run python -m mi_app.cli to validate the import path
   ```

   Ledtråd: vid `ModuleNotFoundError`, kör från rätt katalog.

3. **15-3 · Reparera importcykel**

   ```python todo
   # TODO 1: create a small artificial cycle and fix it by moving functions to utils
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

   Edge case: testa import av båda modulerna efter reparationen.

---

## Vanliga misstag

- Fel relativ import som `from .. import` utan `__init__.py`.
- Duplicera i stället för att importera.
- Köra från olika kataloger och bryta paths; använd `python -m`.
- Lägga `__init__.py` direkt i `src/` och importera `src`; det riktiga paketet ska ligga under `src/<package>/` och installeras.

---

## Förklarade lösningar

1. **Domain/services**: lägg modulerna under `src/mi_app/`, konfigurera discovery i `pyproject.toml`, installera i en ny miljö och verifiera `import mi_app` från en tillfällig katalog.
2. **CLI**: `mi_app/cli.py` orkestrerar medan verksamhetslogik ligger i `servicios`. Kör `python -m mi_app.cli` efter installation för att prova paketets importsökväg; upplägget är fortsatt lätt att testa.
3. **Cykel**: gemensamma funktioner flyttas till `utils`, så beroenden och lager blir tydliga.

---

## Sammanfattning

Moduler och packages organiserar projekt. Du kan importera exakt vad som behövs och skapa rena entry points.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: distributionen installeras och det riktiga paketet importeras utanför projektroten.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: ett normalfall, ett gränsfall och en återhämtning testas.
- **Verifiering**: modulen och import från en annan arbetskatalog fungerar i en ny process.
- **Förklaring**: du kan motivera besluten och deras risker.

## Avslutande reflektion

Fråga alltid var logiken hör hemma. Tydliga moduler förbereder större projekt och ramverk som Django.
