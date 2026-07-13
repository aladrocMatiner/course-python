# Kapitel 16 · Miljöer, beroenden och reproducerbara projekt

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Du skapar virtuella miljöer med `venv`, installerar beroenden med `pip`, hanterar `requirements.txt` och `pyproject.toml` och läser environment variables för säker konfiguration. Miniprojektet installerar `requests` och använder `.env`.

## Lärväg

1. **Varför beroenden isoleras**.
2. **Skapa och aktivera `venv`**.
3. **Installera med `pip`**.
4. **Lås versioner i `requirements.txt`**.
5. **Grundläggande `pyproject.toml`**.
6. **Environment variables och `.env`**.

## Lärandemål

- Skapa och aktivera miljöer på Windows, macOS och Linux.
- Installera bibliotek och låsa versioner för reproduktion.
- Exportera och importera beroenden med `pip freeze`.
- Läsa känslig konfiguration från miljön.

## Varför det spelar roll

Utan isolering kan ett projekt förstöra ett annat. Kontrollerade beroenden är grunden för professionellt teamarbete.

### Miniäventyr

Varje virtuell miljö är en LEGO-låda med exakt rätt bitar för ett projekt. Blandas alla lådor blir bygget kaotiskt; `venv` håller dem åtskilda och reproducerbara.

## Förkunskaper
Rekommenderade tidigare kapitel: 15.
Använd CPython 3.11+ i en tillfällig lokal miljö och håll data, hemligheter och tjänster borta från verkliga system.

---

## 1. Skapa och aktivera `venv`

```bash illustrative
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

- `(.venv)` i prompten visar aktiv miljö.
- `deactivate` lämnar den.

Om du är osäker på vilket `pip` som används:

```bash illustrative
python -m pip install requests
```

Det installerar i den Python som faktiskt kör kommandot.

---

## 2. Installera packages

```bash illustrative
pip install requests
python -c "import requests; print(requests.__version__)"
```

Varje miljö har eget `pip`.

### `requirements.txt`

```bash illustrative
pip freeze > requirements.txt
git add requirements.txt
```

På en annan maskin körs `pip install -r requirements.txt`.

---

## 3. `pyproject.toml` (frivilligt men modernt)

```toml illustrative
[project]
name = "mi-proyecto"
version = "0.1.0"
dependencies = [
  "requests>=2.31",
]
```

Verktyg som `pip-tools`, `poetry` och `pdm` använder formatet.

---

## 4. Environment variables

```python runnable
import os
API_KEY = os.environ.get("API_KEY", "dummy")
```

Lägg aldrig secrets i kodförrådet.

### `.env` med `python-dotenv`

```bash illustrative
pip install python-dotenv
```

```python illustrative
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.environ["API_KEY"]
```

Skapa `.env` med `API_KEY=value` och lägg den i `.gitignore`.

Typisk `.gitignore`:

```gitignore illustrative
.venv/
.env
__pycache__/
```

---

## Vägledda övningar (med TODO)

1. **16-1 · Förbered miljön**

   ```bash todo
   # TODO 1: create .venv and activate it
   # TODO 2: install requests and python-dotenv
   # TODO 3: generate requirements.txt
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

2. **16-2 · Konfigurerat skript**

   ```python todo
   # TODO 1: create config.py that loads variables from .env
   # TODO 2: use os.environ to read API_KEY
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

3. **16-3 · Minimal pyproject**

   ```text todo
   # TODO 1: create pyproject.toml with basic dependencies
   # TODO 2: document in README how to install
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

   Detta är bonusnivå; för nybörjaren räcker `requirements.txt` väl.

---

## Vanliga misstag

- Glömma aktivering före installation.
- Inte versionshantera `requirements.txt`.
- Commita `.env` med secrets; använd `.gitignore`.

---

## Förklarade lösningar

1. **Miljö**: `python -m venv .venv` och `pip freeze > requirements.txt` gör projektet reproducerbart.
2. **Konfiguration**: `load_dotenv()` låter `os.environ` läsa lokala variabler.
3. **pyproject**: dokumenterade installationssteg ger teamet samma process.

---

## Sammanfattning

Du kan skapa miljöer, installera beroenden och hålla konfiguration säker i environment variables.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: resultatet uppfyller enhetens kontrakt.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: ett normalfall, ett gränsfall och en återhämtning testas.
- **Verifiering**: exempel och övningar körs i en ren miljö.
- **Förklaring**: du kan motivera besluten och deras risker.

## Avslutande reflektion

Grunderna tar bort ”det fungerar på min dator”. Använd dem i varje nytt kodförråd.
