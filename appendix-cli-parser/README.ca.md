# Apèndix A · Eines CLI amb la llibreria estàndard

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Dissenyarem una eina de consola amb subcomandes, opcions obligatòries i ajuda automàtica. Farem servir `argparse`, `pathlib` i `logging` per crear scripts professionals sense dependències externes.

## Objectius d’aprenentatge
- Configurar `ArgumentParser` amb arguments posicional i opcionals.
- Crear subcomandes amb `add_subparsers`.
- Llegir i escriure fitxers amb `Path`.
- Retornar codis de sortida i usar logging.
- Provar CLI simulant `argv`.

---

## Exemple bàsic (`argparse`)
```python
import argparse

parser = argparse.ArgumentParser(description="Gestor de notes")
parser.add_argument("titulo", help="Nom del fitxer de nota")
parser.add_argument("--mensaje", required=True)
parser.add_argument("--tags", nargs="*", default=[])
args = parser.parse_args()

print(args.titulo, args.mensaje, args.tags)
```

---

## Subcomandes
```python
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(prog="todos")
subparsers = parser.add_subparsers(dest="comando", required=True)

add_parser = subparsers.add_parser("add", help="Afegir tasca")
add_parser.add_argument("texto")

subparsers.add_parser("list", help="Llistar tasques")

args = parser.parse_args()
archivo = Path("todos.txt")

if args.comando == "add":
    with archivo.open("a", encoding="utf-8") as fh:
        fh.write(args.texto + "\n")
elif args.comando == "list":
    print(archivo.read_text())
```

---

## Resum
Amb `argparse` + `pathlib` + `logging` pots crear eines CLI robustes i fàcils d’usar. És un superpoder per automatitzar tasques.
