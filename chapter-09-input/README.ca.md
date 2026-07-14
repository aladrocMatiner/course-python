# Capítol 9 · Entrada de dades i validació segura

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Aprendràs a recollir dades des de la terminal (`input()`), des d’arguments de línia d’ordres i des de fitxers senzills, sempre validant i convertint abans d’usar els valors. Veureu exemples de “formularis conversacionals” i mini eines de consola.

## Ordre pedagògic
1. **Model mental**: tota entrada és un string; tu decideixes com convertir-la.
2. **`input()` interactiu**: preguntes bàsiques i encadenades.
3. **Conversió i validació**: `int()`, `float()`, `strip()` i `ValueError`.
4. **Defaults i reintents**: repetir fins a tenir una entrada vàlida.
5. **Arguments de CLI**: `sys.argv` i introducció a `argparse`.
6. **Lectura de fitxers**: obrir, llegir i comprovar existència.
7. **Proves i exercicis guiats**.

## Objectius d’aprenentatge
- Recollir entrades i convertir-les al tipus correcte.
- Validar abans d’usar, mostrant missatges útils quan falla.
- Implementar reintents segurs amb límits.
- Llegir arguments i fitxers amb la llibreria estàndard.
- Escriure proves per funcions “pures” (sense `input()`).

## Prerequisits i rutes
- **Prerequisit:** completa el checkpoint del [capítol 8](../chapter-08-conditionals/README.ca.md). La ruta essencial usa cadenes, conversions i condicionals.
- **Ruta essencial · 40–55 min:** secció 1, la subsecció essencial i l’exercici 9-0 següents, i després la secció 3. Resultat: normalitzar text, validar dígits, convertir un enter i recuperar-se d’una entrada invàlida amb condicionals directes. No exigeix excepcions, bucles, funcions ni pytest.
- **Ruta intermèdia · 30–40 min:** reintents limitats de la secció 4. És un **preview opcional** de [bucles](../chapter-10-loops/README.ca.md), [funcions](../chapter-11-functions/README.ca.md) i [excepcions](../chapter-14-exceptions/README.ca.md); copia els helpers complets o omet-los.
- **Ruta professional opcional · 45–60 min:** CLI, fitxers, CSV i tests. Anticipa [fitxers](../chapter-13-files/README.ca.md) i [pytest](../chapter-18-testing/README.ca.md). Res d'aquesta ruta és necessari per al checkpoint essencial.

## Per què importa
Els programes reals reben dades de persones o d’altres sistemes. Si confies cegament en l’entrada, apareixen bugs (o vulnerabilitats). Dominar lectura i validació et prepara per formularis web i eines CLI.

### Mini aventura
Imagina que el teu programa és un robot amable. Si li parles “rar”, es confon. La validació és ensenyar-li a dir: “no t’he entès, ho pots repetir d’una altra manera?”.

## Predicció abans de llegir entrada
Si algú escriu `14`, prediu el valor i tipus que retorna `input()` i després el valor i tipus després d'`int()`. Prediu també què passa amb `catorze`; executa l'exemple de conversió i identifica el missatge de recuperació en lloc d'endevinar.

---

## 1. Model mental: tot arriba com a text
`input()` sempre retorna una cadena. Tu decideixes si la converteixes a número, data, etc.

```python illustrative
name = input("¿Cómo te llamas? ")
print(f"Hola, {name}")
```

- El prompt ajuda a la persona usuària.
- Retalla espais amb `.strip()` si necessites consistència.

---

## 2. Conversió i gestió d’errors

### 9-0 · Conversió essencial sense excepcions

Comença amb una cadena fixa perquè l’exemple s’executi sense interacció. Substitueix-la per `input("Age: ")` només quan practiquis interactivament:

```python runnable
raw_age = "14".strip()

if raw_age.isdigit():
    age = int(raw_age)
    print(age)
else:
    print("Age must contain digits only")
```

Observa ara la branca de recuperació amb text invàlid; el programa manté el control en lloc de fallar:

```python runnable
raw_age = "fourteen".strip()

if raw_age.isdigit():
    age = int(raw_age)
    print(age)
else:
    print("Age must contain digits only")
```

Executa tots dos blocs i registra el valor i el tipus abans i després de convertir. L’ajudant amb `try`/`except` següent és un avançament opcional de les [excepcions](../chapter-14-exceptions/README.ca.md).

```python illustrative
raw_age = input("Edad: ")
try:
    age = int(raw_age)
except ValueError:
    print("L'edat ha de ser un nombre enter.")
    age = None
```

- Captura `ValueError` per explicar què ha fallat.
- Pots encapsular-ho en funcions reutilitzables.

### Helper reutilitzable
```python illustrative
def ask_int(prompt, attempts=3):
    for _ in range(attempts):
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Debes escribir un número entero.")
    raise RuntimeError("Intents esgotats")
```

---

## 3. Valors per defecte

```python illustrative
city = input("Ciudad (por defecto Barcelona): ").strip() or "Barcelona"
print(city)
```

- `valor or "default"` usa el default si l’string queda buit.

---

## 4. Reintents i validacions combinades

```python illustrative
def ask_email():
    while True:
        email = input("Email: ").strip().lower()
        if "@" in email and "." in email:
            return email
        print("Formato inválido. Intenta de nuevo.")
```

- `while True` + `return` és útil quan cal repetir fins a un format vàlid.
- En scripts llargs, posa un límit d’intents.

---

## 5. Arguments de línia de comandes

```python illustrative
# cli_args.py
import sys

if len(sys.argv) < 2:
    print("Uso: python cli_args.py <archivo>")
    sys.exit(1)

path = sys.argv[1]
print(f"Procesando {path}")
```

### `argparse` abreujat
```python illustrative
import argparse

parser = argparse.ArgumentParser(description="Calculadora")
parser.add_argument("operacion", choices=["suma", "resta"])
parser.add_argument("a", type=int)
parser.add_argument("b", type=int)
args = parser.parse_args()

if args.operation == "suma":
    print(args.a + args.b)
else:
    print(args.a - args.b)
```

- `argparse` valida i genera ajuda automàticament.

---

## 6. Lectura simple de fitxers

```python illustrative
from pathlib import Path

path = Path("datos.txt")
if not path.exists():
    raise FileNotFoundError("datos.txt no encontrado")

content = path.read_text(encoding="utf-8")
print(content)
```

- Usa `Path` per rutes portables.
- Gestiona `FileNotFoundError` amb missatges clars.

---

## 7. Proves per funcions pures
En lloc de provar `input()` directament, separa la lògica i passa dades com a arguments.

```python runnable
# forms.py
def normalize_name(name):
    clean = name.strip().title()
    if not clean:
        raise ValueError("Nombre vacío")
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

## Exercicis guiats (amb TODOs)
1. **9-1 · Registre ràpid**
   ```python todo
   # TODO 1: demana nom i cognom, combina’ls amb title()
   # TODO 2: valida que cap sigui buit
   # TODO 3: imprimeix un missatge de benvinguda amb defaults si falten
   ```
   *Pista*: `.strip()` i `or "Convidada"`.

2. **9-2 · CLI de notes**
   ```python todo
   # TODO 1: usa argparse per acceptar --title i --message
   # TODO 2: deriva una ruta confinada amb safe_note_path(title)
   # TODO 3: escriu en UTF-8 i rebutja sobreescriure una nota existent
   ```
   *Pista*: usa `parser.add_argument("--title", required=True)`.

   Usa aquest helper per impedir que el títol injecti `/`, `\\` o `..` a la ruta de sortida:
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

3. **9-3 · Importar CSV senzill**
   ```python todo
   import csv
   # TODO 1: demana la ruta d’un CSV amb input()
   # TODO 2: obre amb newline="" i encoding="utf-8"
   # TODO 3: compta files vàlides amb csv.reader
   ```
   *Pista*: passa el fitxer obert a `csv.reader`; a diferència de `split(",")`, conserva les comes entre cometes.

---

## Errors comuns
- Confiar en el format de l’entrada ⇒ captura `ValueError` i valida.
- No retallar espais ⇒ comparacions que fallen.
- Oblidar `sys.exit(1)` en CLIs quan falten arguments.
- Llegir fitxers sense verificar existència.
- Derivar una ruta directament del títol pot permetre traversal o sobreescriptura accidental; confina i saneja primer el nom.
- Processar CSV amb `split(",")` trenca les comes entre cometes; usa el mòdul `csv`.

---

## Solucions explicades
1. **Registre ràpid**: neteja cada resultat d'`input()` amb `.strip()` i valida'l amb `if not value:`. Un valor per defecte com `"Convidada"` evita interrompre el flux quan un camp opcional queda buit.
2. **CLI de notes**: `argparse` exigeix `--title` i `--message`; `safe_note_path` manté el nom dins de `notes/`, rebutja un títol buit després de sanejar-lo i impedeix sobreescriure abans de `path.write_text(args.message, encoding="utf-8")`.
3. **Importar CSV**: `Path(path).exists()` evita el fitxer absent; `csv.reader` conserva camps entre cometes i el comptador només augmenta per a files amb el nombre esperat de columnes.

---

## Checkpoint i autoavaluació
Usa cadenes fixes i fictícies per simular nom i edat. Prediu-ne els tipus, normalitza el nom, valida l’edat amb `.isdigit()` i converteix només dins la branca vàlida. Executa una vegada amb dígits i una altra amb text no numèric; aquesta última ha de mostrar recuperació sense fallar. No usis bucles, funcions, excepcions ni frameworks de proves.

Suma un punt per criteri: **correcció** (el text vàlid es converteix en l’enter esperat), **normalització** (elimines espais exteriors), **límit** (buit i no numèric van a la branca invàlida), **recuperació** (el missatge indica el format) i **evidència** (registres tipus predits i sortides). Amb 4/5 pots continuar; si no, repeteix 9-0. Reintents, excepcions, CLI/fitxers i pytest pertanyen a rutes posteriors.

---

## Resum
Has après patrons per llegir dades des de consola, arguments i fitxers, convertint i validant de manera segura. Ara pots fer scripts CLI sense por d’entrades “mal formades”.

## Reflexió final
Cada interacció depèn d’entrades fiables. Amb aquestes tècniques pots guiar l’usuari i reaccionar amb missatges clars. Al següent capítol aplicarem aquestes entrades en bucles i parlarem del cost d’executar-los.
