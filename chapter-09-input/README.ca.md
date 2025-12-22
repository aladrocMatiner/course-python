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

## Per què importa
Els programes reals reben dades de persones o d’altres sistemes. Si confies cegament en l’entrada, apareixen bugs (o vulnerabilitats). Dominar lectura i validació et prepara per formularis web i eines CLI.

### Mini aventura
Imagina que el teu programa és un robot amable. Si li parles “rar”, es confon. La validació és ensenyar-li a dir: “no t’he entès, ho pots repetir d’una altra manera?”.

---

## 1. Model mental: tot arriba com a text
`input()` sempre retorna una cadena. Tu decideixes si la converteixes a número, data, etc.

```python
nombre = input("¿Cómo te llamas? ")
print(f"Hola, {nombre}")
```

- El prompt ajuda a la persona usuària.
- Retalla espais amb `.strip()` si necessites consistència.

---

## 2. Conversió i gestió d’errors

```python
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
```python
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

```python
ciudad = input("Ciudad (por defecto Barcelona): ").strip() or "Barcelona"
print(ciudad)
```

- `valor or "default"` usa el default si l’string queda buit.

---

## 4. Reintents i validacions combinades

```python
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

```python
# cli_args.py
import sys

if len(sys.argv) < 2:
    print("Uso: python cli_args.py <archivo>")
    sys.exit(1)

ruta = sys.argv[1]
print(f"Procesando {ruta}")
```

### `argparse` abreujat
```python
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

```python
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

```python
# forms.py
def normalizar_nombre(nombre):
    limpio = nombre.strip().title()
    if not limpio:
        raise ValueError("Nombre vacío")
    return limpio
```

```python
# tests/test_forms.py
import pytest
from forms import normalizar_nombre

def test_normalizar_nombre_ok():
    assert normalizar_nombre("  ada ") == "Ada"

def test_normalizar_nombre_rechaza_vacio():
    with pytest.raises(ValueError):
        normalizar_nombre("   ")
```

---

## Exercicis guiats (amb TODOs)
1. **9-1 · Registre ràpid**
   ```python
   # TODO 1: demana nom i cognom, combina’ls amb title()
   # TODO 2: valida que cap sigui buit
   # TODO 3: imprimeix un missatge de benvinguda amb defaults si falten
   ```
   *Pista*: `.strip()` i `or "Invitada"`.

2. **9-2 · CLI de notes**
   ```python
   # TODO 1: usa argparse per acceptar --titulo i --mensaje
   # TODO 2: desa la nota en un fitxer .txt amb Path.write_text()
   # TODO 3: gestiona errors si no es passa el títol
   ```

3. **9-3 · Importar CSV senzill**
   ```python
   # TODO 1: demana la ruta d’un CSV amb input()
   # TODO 2: comprova que existeix i llegeix-lo línia a línia
   # TODO 3: imprimeix quantes files vàlides has trobat
   ```

---

## Errors comuns
- Confiar en el format de l’entrada ⇒ captura `ValueError` i valida.
- No retallar espais ⇒ comparacions que fallen.
- Oblidar `sys.exit(1)` en CLIs quan falten arguments.
- Llegir fitxers sense verificar existència.

---

## Resum
Has après patrons per llegir dades des de consola, arguments i fitxers, convertint i validant de manera segura. Ara pots fer scripts CLI sense por d’entrades “mal formades”.

## Reflexió final
Cada interacció depèn d’entrades fiables. Amb aquestes tècniques pots guiar l’usuari i reaccionar amb missatges clars. Al següent capítol aplicarem aquestes entrades en bucles i parlarem del cost d’executar-los.
