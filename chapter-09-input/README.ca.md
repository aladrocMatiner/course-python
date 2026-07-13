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
- **Ruta essencial · 40–55 min:** seccions 1–3 i exercici 9-1. Resultat: normalitzar text, convertir un enter i recuperar-se d'una entrada invàlida.
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
nombre = input("¿Cómo te llamas? ")
print(f"Hola, {nombre}")
```

- El prompt ajuda a la persona usuària.
- Retalla espais amb `.strip()` si necessites consistència.

---

## 2. Conversió i gestió d’errors

```python illustrative
raw_age = input("Edad: ")
try:
    edad = int(raw_age)
except ValueError:
    print("La edad debe ser un número entero.")
    edad = None
```

- Captura `ValueError` per explicar què ha fallat.
- Pots encapsular-ho en funcions reutilitzables.

### Helper reutilitzable
```python illustrative
def pedir_entero(prompt, intentos=3):
    for _ in range(intentos):
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Debes escribir un número entero.")
    raise RuntimeError("Intentos agotados")
```

---

## 3. Valors per defecte

```python illustrative
ciudad = input("Ciudad (por defecto Barcelona): ").strip() or "Barcelona"
print(ciudad)
```

- `valor or "default"` usa el default si l’string queda buit.

---

## 4. Reintents i validacions combinades

```python illustrative
def pedir_email():
    while True:
        correo = input("Email: ").strip().lower()
        if "@" in correo and "." in correo:
            return correo
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

ruta = sys.argv[1]
print(f"Procesando {ruta}")
```

### `argparse` abreujat
```python illustrative
import argparse

parser = argparse.ArgumentParser(description="Calculadora")
parser.add_argument("operacion", choices=["suma", "resta"])
parser.add_argument("a", type=int)
parser.add_argument("b", type=int)
args = parser.parse_args()

if args.operacion == "suma":
    print(args.a + args.b)
else:
    print(args.a - args.b)
```

- `argparse` valida i genera ajuda automàticament.

---

## 6. Lectura simple de fitxers

```python illustrative
from pathlib import Path

ruta = Path("datos.txt")
if not ruta.exists():
    raise FileNotFoundError("datos.txt no encontrado")

contenido = ruta.read_text(encoding="utf-8")
print(contenido)
```

- Usa `Path` per rutes portables.
- Gestiona `FileNotFoundError` amb missatges clars.

---

## 7. Proves per funcions pures
En lloc de provar `input()` directament, separa la lògica i passa dades com a arguments.

```python runnable
# forms.py
def normalizar_nombre(nombre):
    limpio = nombre.strip().title()
    if not limpio:
        raise ValueError("Nombre vacío")
    return limpio
```

```python illustrative
# tests/test_forms.py
import pytest
from forms import normalizar_nombre

def test_normalizar_nombre_ok():
    assert normalizar_nombre("  noor ") == "Noor"

def test_normalizar_nombre_rechaza_vacio():
    with pytest.raises(ValueError):
        normalizar_nombre("   ")
```

---

## Exercicis guiats (amb TODOs)
1. **9-1 · Registre ràpid**
   ```python todo
   # TODO 1: demana nom i cognom, combina’ls amb title()
   # TODO 2: valida que cap sigui buit
   # TODO 3: imprimeix un missatge de benvinguda amb defaults si falten
   ```
   *Pista*: `.strip()` i `or "Invitada"`.

2. **9-2 · CLI de notes**
   ```python todo
   # TODO 1: usa argparse per acceptar --titulo i --mensaje
   # TODO 2: deriva una ruta confinada amb safe_note_path(titulo)
   # TODO 3: escriu en UTF-8 i rebutja sobreescriure una nota existent
   ```
   *Pista*: usa `parser.add_argument("--titulo", required=True)`.

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
1. **Registre ràpid**: neteja cada resultat d'`input()` amb `.strip()` i valida'l amb `if not valor:`. Un valor per defecte com `"Invitada"` evita interrompre el flux quan un camp opcional queda buit.
2. **CLI de notes**: `argparse` exigeix `--titulo` i `--mensaje`; `safe_note_path` manté el nom dins de `notes/`, rebutja un títol buit després de sanejar-lo i impedeix sobreescriure abans de `path.write_text(args.mensaje, encoding="utf-8")`.
3. **Importar CSV**: `Path(ruta).exists()` evita el fitxer absent; `csv.reader` conserva camps entre cometes i el comptador només augmenta per a files amb el nombre esperat de columnes.

---

## Checkpoint i autoavaluació
Demana un nom i una edat. Prediu els tipus inicials, normalitza el nom, converteix l'edat i recupera't d'una edat invàlida amb un missatge clar i reintents limitats. No guardis informació personal real: usa un nom fictici i descarta els valors en acabar.

Suma un punt per criteri:
- **Correcció:** l'entrada vàlida produeix el nom normalitzat i l'edat entera esperats.
- **Llegibilitat:** els prompts indiquen el format i les variables separen valors crus dels convertits.
- **Gestió de l'error:** l'entrada invàlida rep un missatge útil i els reintents són limitats.
- **Verificació:** proves entrada vàlida, buida i no numèrica i registres la branca observada.
- **Explicació:** expliques per què tots els valors d'`input()` comencen com a cadenes.

La ruta professional opcional afegeix dues comprovacions: els títols no escapen de `notes/` ni sobreescriuen i els camps CSV entre cometes romanen units.

---

## Resum
Has après patrons per llegir dades des de consola, arguments i fitxers, convertint i validant de manera segura. Ara pots fer scripts CLI sense por d’entrades “mal formades”.

## Reflexió final
Cada interacció depèn d’entrades fiables. Amb aquestes tècniques pots guiar l’usuari i reaccionar amb missatges clars. Al següent capítol aplicarem aquestes entrades en bucles i parlarem del cost d’executar-los.
