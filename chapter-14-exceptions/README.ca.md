# Capítol 14 · Excepcions: de principiant a heroïna/heroi

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Dominaràs el sistema d’excepcions de Python: detectar errors, gestionar-los amb `try/except`, llançar excepcions pròpies, crear classes personalitzades i dissenyar APIs robustes amb missatges clars. Practicarem patrons per validar entrades i netejar recursos.

## Ordre pedagògic
1. Model mental: les excepcions interrompen el flux normal.
2. `try/except` bàsic.
3. `else` i `finally`.
4. `raise`.
5. Excepcions personalitzades.
6. Encadenar (`raise ... from ...`).
7. Context managers.
8. Proves i exercicis.

## Objectius d’aprenentatge
- Capturar excepcions selectivament.
- Usar `else` i `finally` per controlar flux i neteja.
- Crear excepcions de domini.
- Encadenar excepcions sense perdre context.
- Provar funcions que han de llançar errors.

## Per què importa
Ignorar excepcions crea fallades silencioses o missatges críptics. Un bon maneig d’errors dona confiança i facilita depurar en producció.

### Mini aventura
Les excepcions són com senyals i airbags: t’avisen i et protegeixen quan alguna cosa va malament. Aprendre-les et fa el programa més segur.

## Prerequisits
Capítols previs recomanats: 8, 11, 12, 13.
Usa CPython 3.11+ en un entorn local d’un sol ús i mantén les dades, els secrets i els serveis fora de sistemes reals.

---

## 1. `try/except` des de zero

```python runnable
try:
    result = int("abc")
    print(result)
except ValueError:
    print("That was not a valid number")
```

- El bloc `except` només s'executa si es produeix `ValueError`.
- Un `except:` sense tipus captura fins i tot `KeyboardInterrupt` i `SystemExit`; evita’l. `except Exception:` captura molts errors d’aplicació, així que usa’l només en un límit deliberat i prefereix excepcions concretes.

### Capturar múltiples excepcions
```python runnable
import json

try:
    with open("config.txt", encoding="utf-8") as file:
        data = json.load(file)
except FileNotFoundError as exc:
    print("Missing file", exc)
except json.JSONDecodeError as exc:
    print("Invalid JSON", exc)
```

---

## 2. `else` i `finally`

```python runnable
def read_config():
    # Simple example: in real life you would read from a file/JSON
    return {"debug": True}

try:
    data = read_config()
except (FileNotFoundError, ValueError):
    data = {}
else:
    print("Config loaded successfully")
finally:
    print("End of process")
```

- `else` només s'executa quan no hi ha hagut cap excepció.
- `finally` s'executa sempre; és adequat per tancar connexions i alliberar recursos.

---

## 3. Llançar excepcions (`raise`)

```python runnable
def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Denominator cannot be zero")
    return a / b
```

- `raise` atura la funció i propaga l'error.
- Prefereix excepcions estàndard com `ValueError` o `TypeError` quan descriguin bé el problema.

### `raise` sense arguments
```python illustrative
try:
    divide(10, 0)
except ZeroDivisionError:
    raise  # re-raise the same exception
```

---

## 4. Excepcions personalitzades

```python runnable
class ConfigError(Exception):
    """Errors related to configuration."""

class MissingConfig(ConfigError):
    pass
```

```python runnable
def load_config(path):
    if not path.exists():
        raise MissingConfig(f"Missing {path}")
    # ...
```

- Heretar d'`Exception`, o d'una subclasse adequada, permet distingir els errors del domini.
- Mantén les jerarquies petites i descriptives.

---

## 5. Encadenament (`raise ... from ...`)

```python illustrative
import json

class ConfigDecodeError(ConfigError):
    pass

try:
    config = json.loads(raw)
except json.JSONDecodeError as exc:
    raise ConfigDecodeError("Invalid config") from exc
```

`from exc` conserva el traceback original i facilita la depuració.

---

## 6. Context managers i neteja

```python runnable
class TemporaryFile:
    def __enter__(self):
        self.fh = open("temp.txt", "w")
        return self.fh

    def __exit__(self, exc_type, exc, tb):
        self.fh.close()
        if exc_type:
            print("An error occurred", exc)
            return False  # Propagate the exception
```

Un context manager propi garanteix la neteja encara que es produeixi un error dins del bloc `with`.

---

## 7. Proves amb excepcions

```python illustrative
import pytest

def test_divide_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

- `pytest.raises` comprova que es llanci l'excepció esperada.
- Usa `match="text"` si també vols verificar el missatge.

---

## Exercicis guiats (amb TODOs)
1. **14-1 · Validador robust**
   ```python todo
   def validate_payload(data):
       # TODO 1: raise ValueError if "email" is missing
       # TODO 2: use try/except to normalize type errors
   ```
   *Pista*: `if "email" not in data: raise ValueError(...)`.

2. **14-2 · CLI resistent**
   ```python todo
   # TODO 1: process files, catch FileNotFoundError and show a friendly message
   # TODO 2: use `sys.exit(1)` when it’s critical
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

3. **14-3 · Excepció personalitzada**
   ```python todo
   class InsufficientFunds(Exception):
       pass
   # TODO 1: implement withdraw(amount) that raises InsufficientFunds
   # TODO 2: handle the exception and print the remaining balance
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

---

## Errors comuns
- Capturar excepcions massa genèriques i amagar el problema real.
- No tornar a llançar l'excepció amb `raise` quan no la pots resoldre.
- Ignorar `finally` i deixar recursos oberts.
- Llançar excepcions amb missatges imprecisos; inclou-hi sempre el context útil.

---

## Solucions explicades
1. **Validador robust**: `try: email = data["email"]` i `except KeyError as exc: raise ValueError("Falta email") from exc` converteix un detall d'implementació en un error útil sense perdre'n la causa.
2. **CLI resistent**: un `try/except FileNotFoundError` indica quin fitxer ha fallat i acaba amb codi 1 perquè altres programes puguin detectar l'error.
3. **Excepció personalitzada**: `withdraw` comprova el saldo i llança `InsufficientFunds` si no n'hi ha prou. El `try/except` del nivell superior informa la persona usuària sense mostrar un traceback cru.

---

## Resum
Controlar excepcions et permet escriure codi sòlid: decideixes què gestiones, què propagues i com ho expliques. Les excepcions personalitzades donen semàntica a la teva API.

## Punt de control i rúbrica
- **Correcció**: el resultat compleix el contracte de la unitat.
- **Llegibilitat**: els noms i les responsabilitats s’entenen a la primera.
- **Errors**: es proven un cas vàlid, un límit i una recuperació.
- **Verificació**: els exemples i els exercicis s’executen en un entorn net.
- **Explicació**: pots justificar les decisions i els riscos.

## Reflexió final
Ser “heroïna/heroi” amb excepcions és anticipar fallades, escriure missatges clars i no tenir por de llançar errors quan una regla no es compleix.
