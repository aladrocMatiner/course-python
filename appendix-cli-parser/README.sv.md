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
- Funktioner, filer, undantag, moduler, loggning och grundläggande `pytest`-fixtures.
- En tillfällig lokal katalog; kommandotester ska använda `tmp_path` i stället för riktiga användarfiler.

## Förutsäg innan du kör
Innan du anropar den första parsern: förutsäg dess utdata och avslutsbeteende för giltiga argument, saknad obligatorisk indata och `--help`. Testa varje fall med tillfälliga data och jämför resultatet med din förutsägelse.

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

## 3. Ett stabilt kontrakt: `main(argv) -> int`

Håll parser, domänlogik och processavslut åtskilda. `argparse` höjer normalt `SystemExit` vid ogiltig syntax; den här lilla parsern omvandlar enbart användningsfel till ett värde som `main` kan mappa till kod `2`.

```python illustrative
import argparse
import sys
from pathlib import Path

class CliUsageError(ValueError):
    pass

class CourseArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise CliUsageError(message)

def build_parser():
    parser = CourseArgumentParser(prog="notes")
    subparsers = parser.add_subparsers(dest="command", required=True)
    show = subparsers.add_parser("show")
    show.add_argument("path", type=Path)
    return parser

def main(argv=None):
    try:
        args = build_parser().parse_args(argv)
    except CliUsageError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        return 2

    try:
        print(args.path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"note not found: {args.path}", file=sys.stderr)
        return 1
    except PermissionError:
        print(f"cannot read note: {args.path}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- `0` betyder framgång, `1` ett väntat fil- eller körfel och `2` felaktig kommandoanvändning.
- Fånga endast fel som kommandot kan förklara och återhämta sig från. Ett oväntat programmeringsfel ska behålla sin traceback för utvecklaren i stället för att förvandlas till ett vagt användarmeddelande.
- Den fullständiga [CLI-kontraktsmodulen](cli_contract.py) accepterar även injicerbara utdataflöden så att tester inte ändrar globalt processtillstånd.

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
    # Convert expected usage/domain failures into documented return codes.
    # Let unexpected programming errors remain visible.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

### Test av argv
```python illustrative
def test_build_parser_add():
    parser = build_parser()
    args = parser.parse_args(["add", "Learn argparse"])
    assert args.command == "add"
    assert args.text == "Learn argparse"
```

Egen `argv` kan nu skickas i tester. Kontrollera också att `main(giltig_argv) == 0`, att en saknad fil ger `1` och att ogiltig syntax ger `2`. Kör standardbibliotekets kompletterande testsvit från `appendix-cli-parser/` med `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

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
- `Exception` fångas runt hela kommandot, så programmeringsfel blir missvisande användarfel; fånga bara väntade användnings-, fil- och domänundantag.
- `print` för allt i stället för filtrerbar logging.
- Ingen testning med simulerade argument.

---

## Förklarade lösningar

1. **Utgifter**: skapa `add` och `report` och skriv CSV-rader. `main(argv)` returnerar `0` för giltig add/report, `1` för en väntat saknad eller oläsbar CSV och `2` för ogiltig syntax. Fånga bara `FileNotFoundError`, `PermissionError`, `csv.Error` och ditt eget domänfel där de kan förklaras.
2. **Logger**: aktivera `--debug` med `store_true` och kontrollera loggposter med `caplog`; använd `capsys` för `stdout` och `stderr`.

---

## Sammanfattning

`argparse`, `logging` och `pathlib` ger robusta, självdokumenterande och testbara konsolverktyg utan framework.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: resultatet uppfyller enhetens kontrakt.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: saknade filer och ogiltiga argument ger tydliga, stabila returkoder medan oväntade fel behåller sina tracebacks.
- **Verifiering**: simulera `argv`, kontrollera `0/1/2`, använd `tmp_path` och kontrollera loggar med `caplog`.
- **Förklaring**: skilj parserbeteende, domänlogik och terminalpresentation åt.

## Avslutande reflektion

Standardbibliotekets CLI:er ger autonomi för automation och verktyg som teamet kan köra utan fler installationer. Samma mönster finns i deploy- och DevOps-verktyg.
