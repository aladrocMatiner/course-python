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
- Funcions, fitxers, excepcions, mòduls, logging i fixtures bàsics de pytest.
- Un directori local d'un sol ús; les proves d'ordres han d'usar `tmp_path` en lloc de fitxers reals de la persona usuària.

## Prediu abans d'executar
Abans d'invocar el primer parser, prediu-ne la sortida i el comportament de terminació amb arguments vàlids, si falta l'entrada obligatòria i amb `--help`. Prova cada cas amb dades d'un sol ús i compara el resultat amb la predicció.

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

## 3. Un contracte estable `main(argv) -> int`

Separa el parser, la lògica de domini i la sortida del procés. Normalment `argparse` llança `SystemExit` quan la sintaxi no és vàlida; aquest parser petit converteix només els errors d'ús en un valor que `main` pot assignar al codi `2`.

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

- `0` significa èxit, `1` un error esperat de fitxer o execució i `2` un ús incorrecte de l'ordre.
- Captura només els errors que l'ordre pugui explicar i dels quals es pugui recuperar. Un error de programació inesperat ha de conservar el traceback per a qui desenvolupa, en comptes de convertir-se en un missatge vague.
- El [mòdul complementari del contracte CLI](cli_contract.py) també accepta fluxos de sortida injectables perquè les proves no modifiquin l'estat global del procés.

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
    # Convert expected usage/domain failures into documented return codes.
    # Let unexpected programming errors remain visible.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

### Prova d’argv
```python illustrative
def test_build_parser_add():
    parser = build_parser()
    args = parser.parse_args(["add", "Learn argparse"])
    assert args.command == "add"
    assert args.text == "Learn argparse"
```

- Això permet passar un `argv` propi durant les proves. Comprova també que `main(argv_vàlid) == 0`, que un fitxer absent retorna `1` i que una sintaxi invàlida retorna `2`. Des d'`appendix-cli-parser/`, executa la suite complementària de la biblioteca estàndard amb `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

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
- Capturar `Exception` al voltant de tota l'ordre converteix defectes de programació en errors enganyosos; captura només excepcions esperades d'ús, fitxer i domini.
- Utilitzar `print` per a tot en lloc de logging i no poder filtrar.
- No provar `argparse` amb arguments simulats.

---

## Solucions explicades
1. **CLI de despeses**: crea `subparsers.add_parser("add")` i `"report"`; escriu files a `expenses.csv`. `main(argv)` retorna `0` per a un `add` o `report` vàlid, `1` per a un CSV esperat absent o il·legible i `2` per a sintaxi invàlida. Captura només `FileNotFoundError`, `PermissionError`, `csv.Error` i el teu error de domini allà on els puguis explicar.
2. **Logger configurable**: activa `--debug` amb `store_true` i comprova registres amb `caplog`; reserva `capsys` per a `stdout` i `stderr`.

---

## Resum
Amb `argparse`, `logging` i `pathlib` pots crear eines de consola robustes, autodocumentades i fàcils de provar, sense frameworks externs.

## Punt de control i rúbrica
- **Correcció**: les opcions obligatòries, les subordres i els codis de sortida corresponen al contracte de l'ordre.
- **Llegibilitat**: el text d'ajuda i els noms de les ordres n'expliquen el propòsit.
- **Errors**: els fitxers absents i els arguments invàlids produeixen codis de retorn estables i clars, mentre els defectes inesperats conserven els tracebacks.
- **Verificació**: simula `argv`, comprova `0/1/2`, usa `tmp_path` i verifica els logs amb `caplog`.
- **Explicació**: distingeix el comportament del parser, la lògica de domini i la presentació al terminal.

## Reflexió final
Dominar les CLI amb la llibreria estàndard et dona autonomia per automatitzar tasques i crear utilitats professionals que l'equip pot executar sense instal·lar res més. Aquests patrons reapareixen als scripts de desplegament i a les eines DevOps.
