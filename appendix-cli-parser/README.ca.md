# Apèndix A · Construir eines CLI amb la llibreria estàndard

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Dissenyarem una ordre de consola inspirada en eines reals: acceptarà subordres, opcions obligatòries i mostrarà ajuda automàtica. Utilitzarem `argparse`, `pathlib` i `logging` perquè puguis distribuir scripts professionals sense dependències externes.

## Itinerari d'aprenentatge
1. **Recordatori: `sys.argv` i les seves limitacions**.
2. **Estructura bàsica d'`argparse`**: descripció, arguments posicionals i opcionals.
3. **Subordres amb `add_subparsers`**: diverses accions dins una eina.
4. **Sortida més rica**: format, codis de sortida i logging.
5. **Packaging bàsic**: punt d'entrada amb `if __name__ == "__main__"`.
6. **Proves lleugeres**: `argparse`, pytest i `capsys`.

## Objectius d'aprenentatge
- Configurar un `ArgumentParser` amb arguments obligatoris i opcionals.
- Implementar subordres per agrupar funcionalitat.
- Llegir i escriure fitxers amb `Path` a partir d'arguments de la persona usuària.
- Registrar missatges i retornar codis de sortida adequats.
- Provar ordres simulant `argv`.

## Per què és important
Encara que hi ha frameworks més potents, dominar la llibreria estàndard evita dependències i permet construir ràpidament eines internes, scripts de desplegament i utilitats de dades.

### Miniaventura
Una CLI és com el comandament a distància del programa: en lloc de fer clic, escrius ordres curtes. Si el comandament està ben dissenyat, amb ajuda i opcions clares, qualsevol persona el pot utilitzar sense por.

## Prerequisits
Capítols previs recomanats: 9, 11, 13–16, 18.
Usa CPython 3.11+ en un entorn local d’un sol ús i mantén les dades, els secrets i els serveis fora de sistemes reals.

---

## 1. `argparse` bàsic

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

- `nargs="*"` permet passar diverses etiquetes.
- `parser.parse_args()` ja valida els arguments i genera l'ajuda.

### Ajuda generada
```text illustrative
python cli.py --help
```
Mostra automàticament la descripció, els arguments i la forma d'ús.

---

## 2. Subordres

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

- `dest="command"` permet saber quin subordre s'ha utilitzat.
- Per afegir contingut, utilitza `file_path.open("a", encoding="utf-8")` com a l'exemple. `Path.write_text()` substitueix el fitxer i no accepta cap argument `append=True`.

---

## 3. Logging i codis de sortida

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

- `sys.exit(0)` significa èxit; qualsevol codi diferent de zero indica error.

---

## 4. Bones pràctiques
- Mantén la lògica dins funcions per poder-la provar i reutilitzar.
- Utilitza `Path` per a les rutes; no concatenis strings.
- Afegeix exemples amb `ArgumentParser(description=...)` i `epilog`.

### Estructura recomanada
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

### Prova d’argv
```python illustrative
def test_build_parser_add():
    parser = build_parser()
    args = parser.parse_args(["add", "Learn argparse"])
    assert args.command == "add"
    assert args.text == "Learn argparse"
```

- Això permet passar un `argv` propi durant les proves.

---

## Exercicis guiats (amb TODO)
1. **A-1 · CLI de despeses**
   ```python todo
   # TODO 1: "add" subcommand with amount and description
   # TODO 2: "report" subcommand that shows the total
   # TODO 3: store data in CSV format using Path
   ```
   *Pista*: `Path("expenses.csv").open("a", newline="", encoding="utf-8")`.

2. **A-2 · Logger configurable**
   ```python todo
   # TODO 1: add --debug option that sets logging to DEBUG
   # TODO 2: print messages only if the level matches
   # TODO 3: try capsys in pytest
   ```
   *Pista*: `if args.debug: logging.getLogger().setLevel(logging.DEBUG)`.

---

## Errors habituals
- Oblidar `dest` o `required=True` als subparsers, de manera que l'eina no sap què ha d'executar.
- No encapsular la lògica amb `try/except` i mostrar tracebacks crus per a errors esperables.
- Utilitzar `print` per a tot en lloc de logging i no poder filtrar.
- No provar `argparse` amb arguments simulats.

---

## Solucions explicades
1. **CLI de despeses**: crea `subparsers.add_parser("add")` i `"report"`; escriu files a `expenses.csv`. `report` llegeix i suma els valors.
2. **Logger configurable**: activa `--debug` amb `store_true` i comprova registres amb `caplog`; reserva `capsys` per a `stdout` i `stderr`.

---

## Resum
Amb `argparse`, `logging` i `pathlib` pots crear eines de consola robustes, autodocumentades i fàcils de provar, sense frameworks externs.

## Punt de control i rúbrica
- **Correcció**: el resultat compleix el contracte de la unitat.
- **Llegibilitat**: els noms i les responsabilitats s’entenen a la primera.
- **Errors**: es proven un cas vàlid, un límit i una recuperació.
- **Verificació**: els exemples i els exercicis s’executen en un entorn net.
- **Explicació**: pots justificar les decisions i els riscos.

## Reflexió final
Dominar les CLI amb la llibreria estàndard et dona autonomia per automatitzar tasques i crear utilitats professionals que l'equip pot executar sense instal·lar res més. Aquests patrons reapareixen als scripts de desplegament i a les eines DevOps.
