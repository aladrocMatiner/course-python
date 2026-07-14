# Kapitel 16 · Miljöer, beroenden och reproducerbara projekt

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Du skapar virtuella miljöer med `venv`, installerar beroenden med `pip`, skiljer mellan `pyproject.toml`, kravfiler, constraints, miljösnapshots och låsfiler samt läser miljövariabler för säker konfiguration. Miniprojektet installerar `requests` och använder `.env`.

## Lärväg

1. **Varför beroenden isoleras**.
2. **Skapa och aktivera `venv`**.
3. **Installera med `pip`**.
4. **Dokumentera beroenden korrekt**: deklarationer, direkta pins, constraints, snapshots och lås.
5. **Grundläggande `pyproject.toml`**.
6. **Environment variables och `.env`**.

## Lärandemål

- Skapa och aktivera miljöer på Windows, macOS och Linux.
- Installera bibliotek och dokumentera direkta beroenden medvetet.
- Använda `pip freeze` som en snapshot för en viss tolk och plattform, inte som resolver eller låsfil.
- Förklara vilket starkare underlag ett resolverat lås ger.
- Läsa känslig konfiguration från miljön.

## Varför det spelar roll

Utan isolering kan ett projekt förstöra ett annat. Kontrollerade beroenden är grunden för professionellt teamarbete.

### Miniäventyr

Varje virtuell miljö är en LEGO-låda med exakt rätt bitar för ett projekt. Blandas alla lådor blir bygget kaotiskt; `venv` håller dem åtskilda och reproducerbara.

## Förkunskaper
- Grundläggande terminalkommandon och moduler från kapitel 15.
- CPython 3.11+ med `venv` och `pip`; paketinstallation kräver nätverk, men övningen med miljövariabler är lokal.

## Förutsäg innan du kör
Innan du skapar miljön: förutsäg vilken interpreter `python -m pip` riktar sig mot före respektive efter aktivering. Verifiera båda sökvägarna och förklara sedan varför en oväntad sökväg är ett konfigurationsproblem, inte ett fel i paketet.

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
python -m pip install requests
python -c "import requests; print(requests.__version__)"
```

Varje miljö har eget `pip`.

### `requirements.txt`

```bash illustrative
python -m pip freeze > requirements.txt
git add requirements.txt
```

Återskapa snapshoten i en annan ren miljö med `python -m pip install -r requirements.txt`.

`pip freeze` rapporterar det som är installerat med kravfilssyntax. Det löser inte en ny miljö och skapar inget hermetiskt lås; resultatet kan skilja sig mellan Python-versioner och operativsystem.

### Fem poster med olika uppgifter

- **Projektdeklaration:** `[project].dependencies` anger direkta körberoenden, ofta som kompatibla intervall. Den lagrar inte hela den resolverade grafen.
- **Direkt pin:** `requests==X.Y.Z` fixerar en begärd version men säger i sig inget om alla transitiva beroenden.
- **Constraint:** en constraints-fil begränsar versioner när ett annat krav behöver dem; en post orsakar ingen installation. Exempel: `python -m pip install -c constraints.txt requests`.
- **Miljösnapshot:** `pip freeze` fångar paketen i aktuell tolk och plattform med kravfilsformat. Det är användbart underlag, men inte ett resolverresultat eller ett plattformsoberoende lås.
- **Resolverat lås:** ett låsverktyg lagrar hela resolutionen och dess giltighetsområde, ofta med hashvärden och miljömarkörer. Verifiera det exakta verktyget och målmatrisen innan du hävdar reproducerbarhet; dagens stöd för `pip lock` är experimentellt och utdata gäller aktuell Python-version och plattform.

---

## 3. Beroendedeklaration i `pyproject.toml` (frivilligt men modernt)

```toml illustrative
[project]
name = "mi-proyecto"
version = "0.1.0"
dependencies = [
  "requests>=2.31",
]
```

Det här deklarerar ett direkt kompatibelt krav i paketets metadata. Det är inte en fryst graf över transitiva beroenden. Verifiering av bygge och import från en annan katalog hör till det installerbara exemplet `src/<package>` i kapitel 15.

---

## 4. Environment variables

```python runnable
import os
API_KEY = os.environ.get("API_KEY", "dummy")
```

Lägg aldrig secrets i kodförrådet.

### `.env` med `python-dotenv`

```bash illustrative
python -m pip install python-dotenv
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
   # TODO 3: generate a requirements.txt environment snapshot
   ```
   *Ledtråd*: använd `python -m pip` så att installation och snapshot gäller den aktiva tolken; dokumentera också Python-version och plattform.

2. **16-2 · Konfigurerat skript**

   ```python todo
   # TODO 1: create config.py that loads variables from .env
   # TODO 2: use os.environ to read API_KEY
   ```
   *Ledtråd*: anropa `load_dotenv()` och ge ett tydligt fel om `API_KEY` saknas i stället för att tyst använda ett produktionsvärde.

3. **16-3 · Minimal pyproject**

   ```text todo
   # TODO 1: create pyproject.toml with basic dependencies
   # TODO 2: document in README how to install
   # TODO 3: explain why this declaration is not a lock file
   ```
   Detta är bonusnivå; för nybörjaren räcker `requirements.txt` väl.
   *Ledtråd*: håll tabellen `[project]` minimal och dokumentera de exakta kommandona för att skapa miljön och installera.

---

## Vanliga misstag

- Glömma aktivering före installation.
- Kalla en direkt pin eller en `pip freeze`-snapshot för ett plattformsoberoende lås.
- Förvänta sig att en constraint-post installerar ett paket av sig själv.
- Commita `.env` med secrets; använd `.gitignore`.

---

## Förklarade lösningar

1. **Miljö**: `python -m venv .venv` isolerar projektet och `python -m pip freeze > requirements.txt` dokumenterar en snapshot av miljön. Installera den i en ren miljö med angiven Python och plattform och verifiera importer; gör inte underlaget till ett påstående om hermetisk eller plattformsoberoende reproducerbarhet.
2. **Konfiguration**: `load_dotenv()` låter `os.environ` läsa lokala variabler.
3. **pyproject**: dokumentera det direkta beroendet och installationsstegen och ange att ett separat, resolvergenererat lås krävs för en fullständigt fryst graf.

---

## Sammanfattning

Du kan skapa miljöer, installera beroenden och hålla konfiguration säker i environment variables.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: en ny miljö med angiven Python och plattform installerar den valda beroendeposten.
- **Läsbarhet**: installationskommandon och stödd Python-version är dokumenterade.
- **Felhantering**: en saknad miljövariabel ger ett tydligt fel utan att avslöja hemligheter.
- **Verifiering**: återskapa miljön och importera varje direkt beroende.
- **Förklaring**: skilj mellan isolering, direkta pins, constraints, miljösnapshots, resolverade lås och lagring av hemligheter.

## Avslutande reflektion

Grunderna tar bort ”det fungerar på min dator”. Använd dem i varje nytt kodförråd.
