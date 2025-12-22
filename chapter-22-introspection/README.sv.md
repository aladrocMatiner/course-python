# Kapitel 22 · Introspektion: Python i detektivläge

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
I det här kapitlet lär du dig *introspektion*: hur du kan titta på ett värde och fråga “vad är du?” och “vad kan du göra?”. Du använder `type()`, `isinstance()`, `dir()`, `help()`, `getattr()` och `callable()` för att utforska säkert.

Sedan bygger du en liten “detektiv‑funktion” `describe(value)` och (bonus) ser du hur `inspect.signature()` kan kontrollera vilka parametrar en funktion har — användbart när du testar callbacks.

## Lärandemål
- Kolla typ med `type()` och kontrollera säkert med `isinstance()`.
- Förstå `str()` vs `repr()` (debugging gillar `repr`).
- Se skillnaden mellan attribut och metoder (`callable` + parenteser).
- Utforska okända objekt med `dir()` och `help()`.
- Läsa attribut säkert med `getattr()` och sammanfatta med `describe()`.

## Varför det spelar roll
När du programmerar kommer du ofta få “mystiska” värden (från input, filer, bibliotek). Introspektion hjälper dig att förstå dem utan att gissa.

---

## 1) Vad är det här?
```python
value = 42
print(type(value).__name__)          # int
print(isinstance(value, int))        # True
print(isinstance(value, (int, float)))  # True
```

`None`:
```python
x = None
print(x is None)
print(type(x).__name__)  # NoneType
```

---

## 2) Debug‑utskrift: `str()` vs `repr()`
```python
text = "hello\nworld"
print(text)
print(repr(text))
```

---

## 3) Attribut vs metod (och “glömde jag `()`?”)
```python
text = "hello"
print(text.upper)
print(callable(text.upper))
print(text.upper())
```

---

## 4) Utforska: `dir()` + `help()`
```python
text = "hello"
names = [name for name in dir(text) if "upper" in name]
print(names)
print(str.upper.__doc__)
help(str.upper)
```

---

## 5) Säker åtkomst: `getattr()` och `vars()`
```python
class Player:
    def __init__(self, name):
        self.name = name

p = Player("Frej")
print(getattr(p, "name", "<anonymous>"))
print(getattr(p, "nickname", "<anonymous>"))
print(vars(p))
```

---

## Mini‑projekt: `describe(value)`
```python
def describe(value):
    info = {
        "type": type(value).__name__,
        "repr": repr(value),
        "is_callable": callable(value),
    }
    try:
        info["len"] = len(value)
        info["has_len"] = True
    except TypeError:
        info["len"] = None
        info["has_len"] = False
    info["name_attr"] = getattr(value, "name", None)
    return info
```

---

## Bonus: kontrollera funktions‑parametrar (`inspect.signature()`)
```python
import inspect

def require_named_params(fn, required_names):
    sig = inspect.signature(fn)
    params = sig.parameters
    if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()):
        return
    missing = [name for name in required_names if name not in params]
    if missing:
        raise TypeError(f"{fn.__name__} must accept: {', '.join(missing)}")
```

---

## Övningar (TODO + tips)
1. Skriv `report_types(values)` med `type(x).__name__` och `repr(x)`.
2. Skriv `call_method(obj, method_name, ...)` med `getattr` + `callable`.
3. Uppgradera `describe` med `first_item` (fånga `TypeError` och `IndexError`).
4. Bonus: tester för `require_named_params` med pytest.

---

## Vanliga misstag
- `dir()` är lång: filtrera listan.
- `getattr(obj, "x")` utan default kan krascha.
- Glömda parenteser: `text.upper` vs `text.upper()`.

---

## Reflektion
Introspektion är din ficklampa när du lär dig och debuggar. Ställ frågor till värden med `type()`, `dir()` och `help()` — lugnt och steg för steg.

