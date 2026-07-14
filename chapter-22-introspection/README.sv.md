# Kapitel 22 · Introspektion: Python-detectivläge

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Du lär dig *introspektion*: att fråga ett värde ”vad är du?” och ”vad kan du göra?”. `type()`, `isinstance()`, `dir()`, `help()`, `getattr()` och `callable()` utforskar säkert.

Sedan bygger du detective-verktyget `describe(value)` och, som bonus, granskar funktionsparametrar med `inspect.signature()` för callback-validering och bättre tester.

## Lärväg

1. **Typ**: `type`, `isinstance` och `None`.
2. **Tydlig utskrift**: `str` kontra `repr`.
3. **Metod eller attribut** och glömda parenteser.
4. **Okända objekt** med `dir`, `help`, docstrings.
5. **Säker åtkomst** med `getattr`, `hasattr`, `vars`.
6. **Miniprojektet `describe(value)`**.
7. **Bonus**: `inspect.signature()` och pytest.

## Lärandemål

- Identifiera typer och kontrollera flexibelt med `isinstance`.
- Använda `repr()` vid felsökning och skilja från `str()`.
- Undvika att glömma `()` på metoder.
- Utforska vanliga inbyggda objekt och kursobjekt samtidigt som du känner igen hooks som kan köra kod.
- Läsa attribut defensivt och upptäcka förmågor utan att behandla opålitliga objekt som passiva data.
- Bygga och testa verktyg som validerar input och callbacks.

## Varför det spelar roll

Som ny möter du ständigt okända strängar, listor, dictionaries och biblioteksobjekt. Introspektion gör dem utforskbara. Frameworks frågar också om något är callable, tar emot `request`, har `.save()` eller vilka fält som finns.

### Miniäventyr: du är Python-detective

- `type()` är ID-skannern.
- `dir()` listar verktygslådan.
- `help()` och `__doc__` är manualen.
- `getattr()` hämtar säkert eller ger standardvärde.

Det är normalt om det känns märkligt; programmerare lär sig genom riktiga värden.

## Förkunskaper
- Typer, funktioner, klasser, undantag och anropsbara argument från kapitel 2, 11, 12 och 14.
- `pytest` från kapitel 18 behövs bara för bonustesterna av callbacks.

## Förutsäg innan du kör
Välj ett vanligt värde och förutsäg vad `type()`, `repr()` och ett säkert anrop till `getattr()` kommer att visa. Gör exakt de observationerna, jämför dem med din förutsägelse och kom ihåg att introspection hooks på obetrodda objekt kan köra kod.

---

## 1) Första frågan: vad är detta?

### `type()` ger exakt typ

```python runnable
value = 42
print(type(value))          # <class 'int'>
print(type(value).__name__) # int
```

### `isinstance()` är oftast säkrare

```python runnable
value = 42
print(isinstance(value, int))          # True
print(isinstance(value, (int, float))) # True (tuple means “any of these”)
```

Det fungerar även för subclasses:

```python runnable
print(isinstance(True, int))  # True (bool is a kind of int in Python)
print(type(True) is int)      # False (exact type is bool)
```

### Specialfallet `None`

```python runnable
x = None
print(x is None)          # the standard way
print(type(x).__name__)   # NoneType
```

---

## 2) Felsökningsutskrift: `str()` mot `repr()`

`str()` passar användare; `repr()` försöker vara entydig för felsökning.

```python runnable
text = "hello\nworld"
print(text)        # prints two lines
print(repr(text))  # 'hello\nworld' (shows the \n)
```

### Egna objekt: därför hjälper `repr`

```python runnable
class User:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"User({self.name})"

    def __repr__(self):
        return f"User(name={self.name!r})"  # !r uses repr()

u = User("Noor")
print(u)       # User(Noor)
print([u])     # [User(name='Noor')]
print(f"{u!r}")  # User(name='Noor')
```

Förvirringen är normal: `print(u)` använder `str`, men listor visar element via `repr`.

---

## 3) Attribut eller metod och fällan utan `()`

Ett **attribut** är data; en **metod** kan anropas.

```python runnable
text = "hello"
print(text.upper)         # this is a method object
print(callable(text.upper))  # True
print(text.upper())       # HELLO
```

Vanligt misstag:

```python runnable
text = "hello"
shout = text.upper   # forgot () → shout is not a string
print(shout)         # <built-in method upper of str object at ...>
```

`<built-in method ...>` betyder att metoden hämtades men inte anropades.

---

## 4) Utforska okänt objekt med `dir()` och `help()`

### `dir(obj)` ger namn

```python runnable
text = "hello"
names = [name for name in dir(text) if "upper" in name]
print(names)  # ['isupper', 'upper']
```

Listan är lång; filtrera den.

### `help(...)` och docstrings förklarar användning

```python runnable
print(str.upper.__doc__)
```

Hela manualen:

```python runnable
help(str.upper)
```

---

## 5) Säker åtkomst: `getattr()`, `hasattr()`, `vars()`

### `getattr(obj, "name", default)`

Använd när attributet kanske saknas:

```python runnable
class Player:
    def __init__(self, name):
        self.name = name

p = Player("Frej")
print(getattr(p, "name", "<anonymous>"))     # Frej
print(getattr(p, "nickname", "<anonymous>")) # <anonymous>
```

### `hasattr(obj, "name")`

```python illustrative
print(hasattr(p, "name"))     # True
print(hasattr(p, "nickname")) # False
```

`hasattr` gör internt ett attributuppslag. Det kan alltså köra samma property- eller descriptorkod som `getattr`; det är ingen biverkningsfri säkerhetskontroll.

### `vars(obj)` eller `obj.__dict__`

```python illustrative
print(vars(p))  # {'name': 'Frej'}
```

`vars()` fungerar inte på alla objekt; vissa lagrar data annorlunda och det är normalt.

### Introspektion kan köra hooks

Pythonobjekt kan anpassa `__repr__`, `__len__`, `__dir__`, `__getattribute__`, descriptors och properties. Därför kan `repr`, `len`, `dir`, `vars`, `getattr` och `hasattr` köra användarkod, ge biverkningar, höja fel, blockera eller förbruka resurser. Använd verktygen på objekt du litar på i den aktuella processen; beskriv inte ett fientligt pluginvärde som ”säkert”.

`inspect.getattr_static` kan granska ett attribut utan att anropa det vanliga descriptor-/property-uppslaget, men returnerar själva descriptorn i stället för dess beräknade värde:

```python runnable
import inspect

class Probe:
    calls = 0

    @property
    def status(self):
        type(self).calls += 1
        return "ready"

probe = Probe()
descriptor = inspect.getattr_static(probe, "status")
print(type(descriptor).__name__, Probe.calls)  # property 0
print(getattr(probe, "status"), Probe.calls)   # ready 1
```

Statiskt uppslag begränsar en risk; det gör inte senare anrop till det returnerade objektet säkra och skapar ingen tids- eller resurssandbox runt godtycklig kod.

---

## Miniprojekt: `describe(value)` ger en defensiv sammanfattning

```python runnable
def describe(value):
    info = {
        "type": type(value).__name__,
        "repr": repr(value),
        "is_callable": callable(value),
    }

    # Does it have a length?
    try:
        info["len"] = len(value)
        info["has_len"] = True
    except TypeError:
        info["len"] = None
        info["has_len"] = False

    # Does it have a "name" attribute?
    info["name_attr"] = getattr(value, "name", None)
    return info

print(describe("hello"))
print(describe([1, 2, 3]))

class Box:
    def __init__(self, name):
        self.name = name
print(describe(Box("Taha")))
```

Verktyget ger defensiva ledtrådar för vanliga värden; `repr()` och egenskaper kan köra objektkod, så det lovar inte säkerhet för fientliga objekt.

---

## Bonus: validera funktionsparametrar med `inspect.signature()`

Anta att en callback måste acceptera `user_id` och `payload`.

```python runnable
import inspect

def require_named_params(fn, required_names):
    sig = inspect.signature(fn)
    probe = {name: object() for name in required_names}
    try:
        sig.bind(**probe)
    except TypeError as exc:
        raise TypeError(
            f"{fn.__name__} must accept these named arguments: {', '.join(required_names)}"
        ) from exc
```

### Snabb demonstration

```python illustrative
def ok(user_id, payload):
    return (user_id, payload)

def flexible(**kwargs):
    return kwargs

def bad(user_id):
    return user_id

def positional_only(user_id, payload, /):
    return (user_id, payload)

require_named_params(ok, ["user_id", "payload"])        # OK
require_named_params(flexible, ["user_id", "payload"])  # OK (**kwargs)
require_named_params(bad, ["user_id", "payload"])       # raises TypeError
require_named_params(positional_only, ["user_id", "payload"])  # raises TypeError
```

### Små pytest-tester

```python illustrative
# tests/test_introspection.py
import pytest
from chapter_22 import require_named_params

def ok(user_id, payload):
    return (user_id, payload)

def flexible(**kwargs):
    return kwargs

def bad(user_id):
    return user_id

def positional_only(user_id, payload, /):
    return (user_id, payload)

def test_require_named_params_ok():
    require_named_params(ok, ["user_id", "payload"])

def test_require_named_params_kwargs_ok():
    require_named_params(flexible, ["user_id", "payload"])

def test_require_named_params_raises():
    with pytest.raises(TypeError):
        require_named_params(bad, ["user_id", "payload"])

def test_require_named_params_rejects_positional_only():
    with pytest.raises(TypeError):
        require_named_params(positional_only, ["user_id", "payload"])
```

`chapter_22` är en verklig modul i [de importerbara hjälparna för kapitel 22](chapter_22.py), inte ett platshållarnamn. Kör från `chapter-22-introspection/` med `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`; testet importerar modulen, kontrollerar namngivna kontra endast positionella parametrar och visar att statiskt uppslag inte kör en property.

Här testas inte bara utdata utan att fel funktions-*form* avvisas tidigt och begripligt.

---

## Vägledda övningar med TODO och ledtrådar

### 22-1 · Typrapport (lätt)

Returnera strängar som beskriver varje värdes typ.

```python todo
def report_types(values):
    # TODO: return something like:
    # ["'hi' -> str", "3 -> int", "None -> NoneType"]
    pass
```

*Ledtråd*: `type(x).__name__` och `repr(x)`.

### 22-2 · Säker metodanropare (medel)

Anropa bara en metod som finns och är callable.

```python todo
def call_method(obj, method_name, *args, **kwargs):
    # TODO 1: fetch attribute with getattr(obj, method_name, None)
    # TODO 2: if not callable, raise TypeError with a friendly message
    # TODO 3: call and return the result
    pass
```

*Ledtråd*: `callable(attr)`.

### 22-3 · Bättre `describe(value)` (medel+)

Lägg till `has_items` och `first_item` när indexering stöds.

```python todo
def describe2(value):
    # TODO: start from describe(value)
    # TODO: if value supports indexing, store first_item safely
    pass
```

*Ledtråd*: `value[0]` kan ge `TypeError` eller `IndexError`; fånga båda.

### 22-4 · Callback-validering (avancerad bonus)

Implementera `require_named_params` med `inspect.signature` och testa happy path, `**kwargs` och saknade parametrar som ger `TypeError`.

*Ledtråd*: återanvänd bonussektionens idé och skriv sedan egna tester.

---

## Vanliga misstag och hur de undviks

- **`type(x) == SomeType` överallt**: föredra flexibla `isinstance`.
- **Glömda `()`**: `text.upper` är metoden och `text.upper()` resultatet.
- **Överväldigande `dir()`**: filtrera listan.
- **`getattr` utan default** höjer `AttributeError` när det saknas.
- **Anta att `vars()` alltid fungerar**: många built-ins fungerar annorlunda.
- **Anta att uppslag är passivt**: properties, descriptors, `__dir__` och andra hooks kan köra kod; använd `inspect.getattr_static` när du bara behöver den statiska attributdefinitionen.
- **Överanvända introspektion**: använd den för lärande/felsökning men föredra tydliga interfaces i design.

---

## Förklarade lösningar

### Lösning 22-1

```python runnable
def report_types(values):
    result = []
    for v in values:
        result.append(f"{repr(v)} -> {type(v).__name__}")
    return result
```

### Lösning 22-2

```python runnable
def call_method(obj, method_name, *args, **kwargs):
    attr = getattr(obj, method_name, None)
    if not callable(attr):
        raise TypeError(f"{type(obj).__name__} has no callable '{method_name}'")
    return attr(*args, **kwargs)
```

### Lösning 22-3

```python runnable
def describe2(value):
    info = describe(value)
    try:
        info["first_item"] = value[0]
        info["has_items"] = True
    except (TypeError, IndexError, KeyError):
        info["first_item"] = None
        info["has_items"] = False
    return info
```

### Lösning 22-4 (kärnan)

```python runnable
import inspect

def require_named_params(fn, required_names):
    sig = inspect.signature(fn)
    probe = {name: object() for name in required_names}
    try:
        sig.bind(**probe)
    except TypeError as exc:
        raise TypeError(
            f"{fn.__name__} must accept these named arguments: {', '.join(required_names)}"
        ) from exc
```

---

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: resultatet uppfyller enhetens kontrakt.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: påståenden är defensiva och lovar inte säkerhet för fientliga objekt, properties eller descriptors.
- **Verifiering**: testa listor, tomma sekvenser, dictionaries, callables, callbacks med endast positionella parametrar och en property med en observerbar hook.
- **Förklaring**: du kan motivera besluten och deras risker.

## Avslutande reflektion

Du kan fråga Python vad värden är, vad de kan och hur de används säkert. Nästa gång ”object has no attribute…” visas kan du lugnt använda `type()`, `dir()`, `help()` och `getattr()` som en detective.
