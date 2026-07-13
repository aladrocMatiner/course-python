# Appendix A · Bygg CLI-verktyg med standardbiblioteket

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Vi utformar ett konsolkommando med subcommands, obligatoriska options och automatisk hjälp. `argparse`, `pathlib` och `logging` ger professionella skript utan externa beroenden.

## Lärväg

1. **`sys.argv` och begränsningar**.
2. **`argparse`** med beskrivning, positional och optional args.
3. **Subcommands** med `add_subparsers`.
4. **Formatering, exit codes och logging**.
5. **Entry point** med `if __name__ == "__main__"`.
6. **Lätta tester** med pytest och `capsys`.

## Lärandemål

- Konfigurera `ArgumentParser` med obligatoriska och frivilliga argument.
- Gruppera funktionalitet i subcommands.
- Läsa och skriva via `Path` från användarargument.
- Logga och returnera rätt exit code.
- Testa kommandon med simulerad argv.

## Varför det spelar roll

Standardbiblioteket räcker för interna verktyg, deployskript och dataverktyg utan beroenden.

### Miniäventyr

En CLI är programmets fjärrkontroll. Tydlig hjälp och options gör att andra kan använda den tryggt.

## Förkunskaper
Rekommenderade tidigare kapitel: 9, 11, 13–16, 18.
Använd CPython 3.11+ i en tillfällig lokal miljö och håll data, hemligheter och tjänster borta från verkliga system.

---

## 1. Grundläggande `argparse`

```python illustrative
# cli.py
import argparse

parser = argparse.ArgumentParser(description="Notes manager")
parser.add_argument("title", help="Note file name")
parser.add_argument("--message", required=True)
parser.add_argument("--tags", nargs="*", default=[])
args = parser.parse_args()

print(args.title, args.message, args.tags)
```

- `nargs="*"` tillåter flera taggar.
- `parse_args()` validerar och skapar hjälp.

### Genererad hjälp

```text illustrative
python cli.py --help
```

Beskrivning, argument och usage skrivs automatiskt.

---

## 2. Subcommands

```python illustrative
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(prog="todos")
subparsers = parser.add_subparsers(dest="command", required=True)

add_parser = subparsers.add_parser("add", help="Add task")
add_parser.add_argument("text")

list_parser = subparsers.add_parser("list", help="List tasks")

args = parser.parse_args()
file_path = Path("todos.txt")

if args.command == "add":
    with file_path.open("a", encoding="utf-8") as fh:
        fh.write(args.text + "\n")
elif args.command == "list":
    if file_path.exists():
        print(file_path.read_text(encoding="utf-8"))
    else:
        print("No tasks yet.")
```

- `dest="command"` visar valt subcommand.
- Append görs med `file_path.open("a", encoding="utf-8")`; `Path.write_text()` ersätter filen och har inget `append=True`.

---

## 3. Logging och exit codes

```python runnable
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

try:
    # logic
    logging.info("Note saved")
except Exception as exc:
    logging.error("Failure: %s", exc)
    sys.exit(1)
```

`sys.exit(0)` är framgång; övriga koder betyder fel.

---

## 4. Goda vanor

- Håll logik i funktioner för test och återanvändning.
- Använd `Path`; konkatenera inte sökvägssträngar.
- Lägg exempel i `ArgumentParser(description=...)` och `epilog`.

### Rekommenderad struktur

```python illustrative
def build_parser():
    parser = argparse.ArgumentParser(...)
    # configure
    return parser

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    # logic

if __name__ == "__main__":
    main()
```

### Test av argv
```python illustrative
def test_build_parser_add():
    parser = build_parser()
    args = parser.parse_args(["add", "Learn argparse"])
    assert args.command == "add"
    assert args.text == "Learn argparse"
```

Egen `argv` kan nu skickas i tester.

---

## Vägledda övningar (med TODO)

1. **A-1 · Utgifts-CLI**

   ```python todo
   # TODO 1: "add" subcommand with amount and description
   # TODO 2: "report" subcommand that shows the total
   # TODO 3: store data in CSV format using Path
   ```

   *Ledtråd*: `Path("expenses.csv").open("a", newline="", encoding="utf-8")`.

2. **A-2 · Konfigurerbar logger**

   ```python todo
   # TODO 1: add --debug option that sets logging to DEBUG
   # TODO 2: print messages only if the level matches
   # TODO 3: try capsys in pytest
   ```

   *Ledtråd*: `if args.debug: logging.getLogger().setLevel(logging.DEBUG)`.

---

## Vanliga misstag

- Saknat `dest` eller `required=True` för subparsers.
- Ingen `try/except`, så väntade fel ger rå traceback.
- `print` för allt i stället för filtrerbar logging.
- Ingen testning med simulerade argument.

---

## Förklarade lösningar

1. **Utgifter**: skapa `add` och `report`, skriv CSV-rader och summera dem i rapporten.
2. **Logger**: aktivera `--debug` med `store_true` och kontrollera loggposter med `caplog`; använd `capsys` för `stdout` och `stderr`.

---

## Sammanfattning

`argparse`, `logging` och `pathlib` ger robusta, självdokumenterande och testbara konsolverktyg utan framework.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: resultatet uppfyller enhetens kontrakt.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: ett normalfall, ett gränsfall och en återhämtning testas.
- **Verifiering**: exempel och övningar körs i en ren miljö.
- **Förklaring**: du kan motivera besluten och deras risker.

## Avslutande reflektion

Standardbibliotekets CLI:er ger autonomi för automation och verktyg som teamet kan köra utan fler installationer. Samma mönster finns i deploy- och DevOps-verktyg.
