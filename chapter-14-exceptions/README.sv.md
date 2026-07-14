# Kapitel 14 · Undantag: från nybörjare till hjälte

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Du lär dig Pythons exceptionsystem: upptäcka och hantera med `try/except`, höja egna undantag, skapa klasser och utforma robusta API:er som förklarar fel. Vi validerar input, omsluter riskabla anrop och städar resurser.

## Lärväg

1. **Mental modell**: undantag avbryter normalflödet.
2. **`try/except`** för kända fel.
3. **`else` och `finally`**.
4. **`raise`** egna fel.
5. **Egna exception-klasser**.
6. **Chaining** med `raise ... from ...`.
7. **Context managers och cleanup**.
8. **Tester och övningar**.

## Lärandemål

- Identifiera möjliga undantag och fånga selektivt.
- Styra sidoflöde och cleanup med `else` och `finally`.
- Skapa domänspecifika undantag.
- Kedja fel och bevara ursprunglig kontext.
- Testa funktioner som ska höja eller hantera fel.

## Varför det spelar roll

Ignorerade undantag ger tysta fel eller kryptiska meddelanden. Bra felhantering skapar förtroende och gör produktionsfelsökning enklare.

### Miniäventyr

Undantag liknar vägmärken och airbags: de varnar och skyddar när något går fel. Genom att läsa och svara på dem blir programmet säkrare.

## Förkunskaper
- Funktioner, villkor, klasser, filer och context managers från kapitel 8–13.
- En lokal miljö med CPython 3.11+; `pytest` behövs bara i testavsnittet.

## Förutsäg innan du kör
För den första `try/except`: förutsäg vilken rad som slutar köras, vilken handler som tar över och om programmet fortsätter efteråt. Kör sedan exemplet och förklara varje skillnad mellan din förutsägelse och det observerade kontrollflödet.

---

## 1. `try/except` från grunden

```python runnable
try:
    result = int("abc")
    print(result)
except ValueError:
    print("That was not a valid number")
```

- `except` körs bara när `ValueError` uppstår.
- Ett bart `except:` fångar även `KeyboardInterrupt` och `SystemExit`; undvik det. `except Exception:` fångar många programfel, så använd det bara vid en avsiktlig gräns och föredra specifika undantag.

### Fånga flera undantag

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

## 2. `else` och `finally`

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

- `else` körs bara utan undantag.
- `finally` körs alltid och passar anslutnings- och resursstädning.

---

## 3. Höja egna undantag (`raise`)

```python runnable
def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Denominator cannot be zero")
    return a / b
```

`raise` stoppar funktionen och propagerar felet. Välj standardundantag som `ValueError` eller `TypeError` när de beskriver problemet.

### `raise` utan argument

```python illustrative
try:
    divide(10, 0)
except ZeroDivisionError:
    raise  # re-raise the same exception
```

---

## 4. Egna exceptions

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

Arv från `Exception` eller relevant subclass skiljer domänfel. Håll hierarkin liten och beskrivande.

---

## 5. Kedja med `raise ... from ...`

```python illustrative
import json

class ConfigDecodeError(ConfigError):
    pass

try:
    config = json.loads(raw)
except json.JSONDecodeError as exc:
    raise ConfigDecodeError("Invalid config") from exc
```

`from exc` bevarar ursprunglig traceback för enklare felsökning.

---

## 6. Context managers och cleanup

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

En egen context manager garanterar cleanup även när ett fel händer inuti `with`.

---

## 7. Testa undantag

```python illustrative
import pytest

def test_divide_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

`pytest.raises` bekräftar rätt exception; `match="text"` kan kontrollera meddelandet.

---

## Vägledda övningar (med TODO)

1. **14-1 · Robust validator**

   ```python todo
   def validate_payload(data):
       # TODO 1: raise ValueError if "email" is missing
       # TODO 2: use try/except to normalize type errors
   ```

   *Ledtråd*: `if "email" not in data: raise ValueError(...)`.

2. **14-2 · Motståndskraftig CLI**

   ```python todo
   # TODO 1: process files, catch FileNotFoundError and show a friendly message
   # TODO 2: use `sys.exit(1)` when it’s critical
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

3. **14-3 · Eget undantag**

   ```python todo
   class InsufficientFunds(Exception):
       pass
   # TODO 1: implement withdraw(amount) that raises InsufficientFunds
   # TODO 2: handle the exception and print the remaining balance
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

---

## Vanliga misstag

- Fånga för generellt och dölja riktiga problemet.
- Inte använda `raise` igen när felet inte kan lösas.
- Utelämna `finally` och lämna resurser öppna.
- Höja vaga meddelanden utan kontext.

---

## Förklarade lösningar

1. **Validator**: `try: email = data["email"]` och `except KeyError as exc: raise ValueError("Missing email") from exc` ger vänlig kontext.
2. **CLI**: fånga `FileNotFoundError`, visa filen och avsluta med kod 1 så andra skript upptäcker felet.
3. **Eget undantag**: `withdraw` kontrollerar saldo och höjer `InsufficientFunds`; top-level fångar och informerar utan rå traceback.

---

## Sammanfattning

Du väljer vad som hanteras, propageras och kommuniceras. Egna undantag ger API:er domänbetydelse.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: resultatet uppfyller enhetens kontrakt.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: ett normalfall, ett gränsfall och en återhämtning testas.
- **Verifiering**: exempel och övningar körs i en ren miljö.
- **Förklaring**: du kan motivera besluten och deras risker.

## Avslutande reflektion

Att bli skicklig på exceptions är att förutse fel, utforma tydliga meddelanden och våga höja när regler bryts. Övning gör koden pålitligare och lättare att underhålla.
