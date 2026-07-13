# Kapitel 9 · Användarindata och säker validering

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Du samlar data från terminalen med `input()`, från kommandoradsargument och från enkla filer. Varje värde valideras och konverteras före användning. Samtalsliknande formulär och små konsolverktyg efterliknar vanliga backendflöden.

## Lärväg

1. **Mental modell**: all indata börjar som en sträng.
2. **Interaktiv `input()`** och följdfrågor.
3. **Konvertering och validering** med `int()`, `float()`, `strip()` och `ValueError`.
4. **Standardvärden och återförsök** med tydliga gränser.
5. **Kommandoradsargument** via `sys.argv` och `argparse`.
6. **Enkla filer**: öppna, läsa och kontrollera existens.
7. **Tester och vägledda övningar**.

## Lärandemål

- Läsa konsolindata och konvertera till rätt typ.
- Validera före användning och visa hjälpsamma felmeddelanden.
- Implementera säkra, begränsade återförsök.
- Läsa argument och grundläggande filer med standardbiblioteket.
- Testa rena funktioner som inte beror på konsolen.

## Förkunskaper och vägar

- **Förkunskap:** slutför kontrollpunkten i [kapitel 8](../chapter-08-conditionals/README.sv.md). Grundvägen använder strängar, konverteringar och villkor.
- **Grundväg · 40–55 min:** avsnitt 1–3 och övning 9-1. Resultat: normalisera text, konvertera ett heltal och återhämta dig från ogiltig indata.
- **Mellanväg · 30–40 min:** begränsade återförsök i avsnitt 4. Det är en **frivillig förhandsblick** på [loopar](../chapter-10-loops/README.sv.md), [funktioner](../chapter-11-functions/README.sv.md) och [undantag](../chapter-14-exceptions/README.sv.md); kopiera de kompletta hjälparna eller hoppa över dem.
- **Frivillig professionell väg · 45–60 min:** CLI, filer, CSV och tester. Den förhandsvisar [filer](../chapter-13-files/README.sv.md) och [pytest](../chapter-18-testing/README.sv.md). Inget här krävs för grundkontrollpunkten.

## Varför det spelar roll

Verkliga program tar emot data från människor och system. Blind tillit skapar fel och ibland sårbarheter. Validering förbereder dig för webbformulär, automation och professionella CLI-verktyg.

### Miniäventyr

Programmet är en vänlig robot. När den inte förstår ska den inte gissa, utan lugnt be om ett tydligare svar. Det är validering.

## Förutsäg före inläsning

Om någon skriver `14`, förutsäg värdet och typen från `input()` och sedan värdet och typen efter `int()`. Förutsäg också vad som händer med `fjorton`; kör konverteringsexemplet och identifiera återställningsmeddelandet i stället för att gissa.

---

## 1. Mental modell: allt kommer som text

`input()` returnerar alltid en sträng. Du bestämmer om den ska bli tal eller datum eller jämföras som text.

```python illustrative
name = input("What's your name? ")
print(f"Hello, {name}")
```

- En prompt hjälper användaren.
- Rensa extra whitespace med `.strip()` när konsekvens krävs.

---

## 2. Konvertering och felhantering

```python illustrative
raw_age = input("Age: ")
try:
    age = int(raw_age)
except ValueError:
    print("Age must be an integer.")
    age = None
```

- Fånga `ValueError` och förklara vad som var fel.
- Kapsla gärna mönstret i återanvändbara funktioner.

### Återanvändbar hjälpfunktion

```python illustrative
def ask_int(prompt, attempts=3):
    for _ in range(attempts):
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Please enter an integer.")
    raise RuntimeError("Too many attempts")
```

---

## 3. Standardvärden

```python illustrative
city = input("City (default Barcelona): ").strip() or "Barcelona"
print(city)
```

`value or "default"` väljer standardvärdet när strängen är tom.

---

## 4. Återförsök och kombinerad validering

```python illustrative
def ask_email():
    while True:
        email = input("Email: ").strip().lower()
        if "@" in email and "." in email:
            return email
        print("Invalid format. Try again.")
```

- `while True` med `return` passar upprepning tills formatet är giltigt.
- Längre skript behöver en tydlig exit, exempelvis maximalt antal försök.

---

## 5. Kommandoradsargument

```python illustrative
# cli_args.py
import sys

if len(sys.argv) < 2:
    print("Usage: python cli_args.py <file>")
    sys.exit(1)

path = sys.argv[1]
print(f"Processing {path}")
```

### Kort exempel med `argparse`

```python illustrative
import argparse

parser = argparse.ArgumentParser(description="Calculator")
parser.add_argument("operation", choices=["add", "subtract"])
parser.add_argument("a", type=int)
parser.add_argument("b", type=int)
args = parser.parse_args()

if args.operation == "add":
    print(args.a + args.b)
else:
    print(args.a - args.b)
```

`argparse` validerar indata och skapar hjälptext automatiskt.

---

## 6. Enkel filläsning

```python illustrative
from pathlib import Path

path = Path("data.txt")
if not path.exists():
    raise FileNotFoundError("data.txt not found")

content = path.read_text(encoding="utf-8")
print(content)
```

- `Path` ger portabel sökvägshantering.
- Fånga `FileNotFoundError` för ett tydligt meddelande.

---

## 7. Testa rena funktioner

Kapsla logiken och skicka in data som argument i stället för att testa `input()` direkt. Då kan `pytest` köras utan konsolberoende.

```python runnable
# forms.py
def normalize_name(name):
    clean = name.strip().title()
    if not clean:
        raise ValueError("Name cannot be empty")
    return clean
```

```python illustrative
# tests/test_forms.py
import pytest
from forms import normalize_name

def test_normalize_name_ok():
    assert normalize_name("  noor ") == "Noor"

def test_normalize_name_rejects_empty():
    with pytest.raises(ValueError):
        normalize_name("   ")
```

---

## Vägledda övningar (med TODO)

1. **9-1 · Snabb registrering**

   ```python todo
   # TODO 1: ask for first name and last name, combine them with title()
   # TODO 2: validate that neither is empty
   # TODO 3: print a welcome message with defaults if something is missing
   ```

   *Ledtråd*: använd `.strip()` och `or "Guest"`.

2. **9-2 · Antecknings-CLI**

   ```python todo
   # TODO 1: use argparse to accept --title and --message
   # TODO 2: derive a confined path with safe_note_path(title)
   # TODO 3: write with UTF-8 and refuse to overwrite an existing note
   ```

   *Ledtråd*: `parser.add_argument("--title", required=True)`.

   Använd hjälparen så att titeln inte kan injicera `/`, `\\` eller `..` i utdatasökvägen:
   ```python illustrative
   from pathlib import Path

   def safe_note_path(title, root=Path("notes")):
       safe_stem = "".join(
           char for char in title.strip()
           if char.isalnum() or char in ("-", "_")
       )
       if not safe_stem:
           raise ValueError("title must contain a letter or number")
       root.mkdir(parents=True, exist_ok=True)
       path = root / f"{safe_stem}.txt"
       if path.exists():
           raise FileExistsError(f"refusing to overwrite {path}")
       return path
   ```

3. **9-3 · Importera enkel CSV**

   ```python todo
   import csv
   # TODO 1: ask for a CSV path using input()
   # TODO 2: open with newline="" and encoding="utf-8"
   # TODO 3: count valid rows with csv.reader
   ```

   *Ledtråd*: skicka den öppna filen till `csv.reader`; till skillnad från `split(",")` hanterar den citerade kommatecken.

---

## Vanliga misstag

- Lita blint på format: fånga `ValueError` och validera uttryckligen.
- Inte rensa whitespace: likadana strängar jämförs olika.
- Glömma `sys.exit(1)` vid saknade CLI-argument: programmet fortsätter i fel tillstånd.
- Läsa utan existenskontroll: oväntat `FileNotFoundError`.
- Härleda sökvägen direkt från titeln: traversal eller oavsiktlig överskrivning; begränsa och rensa filnamnet först.
- Tolka CSV med `split(",")`: citerade kommatecken blir falska kolumner; använd modulen `csv`.

---

## Förklarade lösningar

1. **Registrering**: rensa varje `input()`, kontrollera `if not value:` och använd `"Guest"` för ett säkert standardflöde.
2. **Antecknings-CLI**: `argparse` kräver `--title` och `--message`; `safe_note_path` håller namnet inom `notes/`, avvisar en tom rensad titel och vägrar överskrivning före `path.write_text(args.message, encoding="utf-8")`.
3. **CSV**: `Path(path).exists()` förebygger saknad fil; `csv.reader` bevarar citerade fält och räknaren ökar bara för rader med förväntat antal kolumner.

---

## Kontrollpunkt och självbedömning

Fråga efter ett namn och en ålder. Förutsäg deras ursprungliga typer, normalisera namnet, konvertera åldern och återhämta dig från en ogiltig ålder med ett tydligt meddelande och begränsade återförsök. Lagra inga verkliga personuppgifter; använd ett påhittat namn och kasta värdena när programmet avslutas.

Ge dig en poäng per kriterium:
- **Korrekthet:** giltig indata ger förväntat normaliserat namn och heltalsålder.
- **Läsbarhet:** frågorna anger formatet och variabler skiljer råa från konverterade värden.
- **Felhantering:** ogiltig indata får ett användbart meddelande och antalet försök är begränsat.
- **Verifiering:** du provar giltig, tom och icke-numerisk indata och noterar den observerade grenen.
- **Förklaring:** du förklarar varför alla värden från `input()` börjar som strängar.

Den frivilliga professionella vägen lägger till två kontroller: titlar kan inte lämna `notes/` eller skriva över filer, och citerade CSV-fält hålls samman.

---

## Sammanfattning

Du kan läsa data från konsol, CLI och filer, konvertera säkert och validera varje steg. Nu kan du bygga interaktiva assistenter och CLI-skript som hanterar stökig indata lugnt.

## Avslutande reflektion

Tillförlitlig indata ligger bakom all interaktion. Du kan vägleda, förutse fel och svara begripligt. Nästa kapitel placerar indatan i loopar och introducerar prestandakostnad.
