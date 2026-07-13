# Capítol 22 · Introspecció: mode detectiu en Python

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
En aquest capítol aprendràs què és la *introspecció*: mirar un valor i preguntar-li «Què ets?» i «Què pots fer?». Utilitzaràs eines com `type()`, `isinstance()`, `dir()`, `help()`, `getattr()` i `callable()` per explorar de manera segura.

Després construiràs una petita eina de detectiu anomenada `describe(value)`. Com a ampliació, aprendràs a inspeccionar els paràmetres d'una funció amb `inspect.signature()` per validar callbacks i escriure proves millors.

## Itinerari d'aprenentatge
1. **Detectar el tipus**: `type`, `isinstance` i el cas `None`.
2. **Mostrar amb claredat**: `str` i `repr`, i per què la depuració prefereix `repr`.
3. **Mètodes i atributs**: `callable` i la trampa dels parèntesis absents.
4. **Explorar objectes desconeguts**: `dir`, `help` i docstrings.
5. **Accés segur**: `getattr`, `hasattr`, `vars` i els casos en què fallen.
6. **Miniprojecte**: `describe(value)`, un resum segur d'un objecte.
7. **Ampliació**: `inspect.signature()` per validar paràmetres obligatoris i proves amb pytest.

## Objectius d'aprenentatge
- Identificar el tipus d'un valor i comprovar-lo de manera segura amb `isinstance`.
- Utilitzar `repr()` per depurar valors misteriosos i entendre la diferència entre `str()` i `repr()`.
- Evitar trampes habituals com fer referència a un mètode sense `()`.
- Explorar un objecte desconegut sense fer fallar el programa.
- Llegir atributs de manera segura i detectar capacitats amb `callable` i `hasattr`.
- Construir i provar utilitats petites que validin entrades i callbacks.

## Per què és important
Quan estàs aprenent, et trobes contínuament valors que encara no entens del tot: strings, llistes, diccionaris o objectes de llibreries. La introspecció et permet explorar-los de manera segura.

Als projectes backend reals, els frameworks també fan introspecció. Per exemple: «És callable?», «Accepta `request`?», «Té un mètode `.save()`?» o «Quins camps existeixen?». No cal ser cap mag; n'hi ha prou amb dominar les bases segures.

### Miniaventura: ets un detectiu de Python
Imagina que ets un detectiu amb una llanterna:
- `type()` és l'**escàner d'identitat**: «Què ets?».
- `dir()` és la **llista d'eines**: «Què pots fer?».
- `help()` i `__doc__` són el **manual**: «Com funciona?».
- `getattr()` és la **pinça segura**: «Dona'm aquest atribut o un valor per defecte».

És normal que al principi sembli estrany. Tothom n'aprèn jugant amb valors reals.

## Prerequisits
Capítols previs recomanats: 2, 11, 12, 14 (و18 للقسم الإضافي).
Usa CPython 3.11+ en un entorn local d’un sol ús i mantén les dades, els secrets i els serveis fora de sistemes reals.

---

## 1) La primera pregunta: què és això?

### `type()` indica el tipus exacte
```python runnable
value = 42
print(type(value))          # <class 'int'>
print(type(value).__name__) # int
```

### `isinstance()` sol ser la comprovació més segura
```python runnable
value = 42
print(isinstance(value, int))          # True
print(isinstance(value, (int, float))) # True (tuple means “any of these”)
```

Per què és més segura? Perquè també funciona amb **subclasses**:

```python runnable
print(isinstance(True, int))  # True (bool is a kind of int in Python)
print(type(True) is int)      # False (exact type is bool)
```

### Cas especial: `None`
```python runnable
x = None
print(x is None)          # the standard way
print(type(x).__name__)   # NoneType
```

---

## 2) Mostrar per depurar: `str()` i `repr()`
Quan mostres una cosa a la persona usuària, `str()` sol anar bé. Quan depures, `repr()` és molt útil perquè intenta evitar ambigüitats.

```python runnable
text = "hello\nworld"
print(text)        # prints two lines
print(repr(text))  # 'hello\nworld' (shows the \n)
```

### Objectes propis: per què ajuda `repr`
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

És habitual confondre's aquí. `print(u)` utilitza `str(u)`, però els contenidors, com les llistes, acostumen a mostrar els elements amb `repr(...)`.

---

## 3) Atributs i mètodes, i la trampa de `()`
Un **atribut** és una dada. Un **mètode** és una cosa que pots cridar.

```python runnable
text = "hello"
print(text.upper)         # this is a method object
print(callable(text.upper))  # True
print(text.upper())       # HELLO
```

Error habitual:
```python runnable
text = "hello"
shout = text.upper   # forgot () → shout is not a string
print(shout)         # <built-in method upper of str object at ...>
```

Si veus una cosa com `<built-in method ...>`, has agafat el mètode però no l'has cridat.

---

## 4) Explorar un objecte desconegut: `dir()` i `help()`
### `dir(obj)` dona una llista de noms
```python runnable
text = "hello"
names = [name for name in dir(text) if "upper" in name]
print(names)  # ['isupper', 'upper']
```

La llista pot ser molt llarga. És normal: filtra-la.

### `help(...)` i les docstrings expliquen com s'utilitza
```python runnable
print(str.upper.__doc__)
```

Si vols el manual complet:
```python runnable
help(str.upper)
```

---

## 5) Accés segur: `getattr()`, `hasattr()` i `vars()`

### `getattr(obj, "name", default)`
És ideal quan no saps si l'atribut existeix:

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

### `vars(obj)`, o `obj.__dict__`, per a objectes senzills
```python illustrative
print(vars(p))  # {'name': 'Frej'}
```

Important: `vars()` **no** funciona amb tots els objectes. Si falla, és normal; alguns objectes desen les dades d'una altra manera.

---

## Miniprojecte: `describe(value)`, un resum defensiu
Escriurem una funció petita que retorna un diccionari descriptiu sense fer fallar el programa.

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

Aquesta eina ofereix pistes defensives per a valors ordinaris; `repr()` i les propietats poden executar codi de l’objecte, així que no promet seguretat davant d’objectes hostils.

---

## Ampliació: validar paràmetres amb `inspect.signature()`
De vegades acceptes una funció, és a dir, un callback, i vols comprovar que tingui els paràmetres necessaris.

Suposa que vols un callback que accepti `user_id` i `payload`.

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

### Demostració ràpida
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

### Proves petites amb pytest
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

Aquest és un ús real de testing: no només proves resultats, sinó que el sistema rebutgi aviat una funció amb la forma incorrecta i mostri un error clar.

---

## Exercicis guiats amb TODO i pistes

### 22-1 · Informe de tipus (fàcil)
Escriu una funció que retorni una llista de strings amb el tipus de cada valor.

```python todo
def report_types(values):
    # TODO: return something like:
    # ["'hi' -> str", "3 -> int", "None -> NoneType"]
    pass
```

*Pista*: utilitza `type(x).__name__` i `repr(x)`.

---

### 22-2 · Cridar un mètode de manera segura (mitjà)
Escriu una funció que cridi un mètode **només si existeix i és callable**.

```python todo
def call_method(obj, method_name, *args, **kwargs):
    # TODO 1: fetch attribute with getattr(obj, method_name, None)
    # TODO 2: if not callable, raise TypeError with a friendly message
    # TODO 3: call and return the result
    pass
```

*Pista*: `callable(attr)` és el teu aliat.

---

### 22-3 · Millorar `describe(value)` (mitjà+)
Amplia `describe(value)` perquè inclogui:
- `has_len` i `len`, que ja hem fet;
- `has_items` i `first_item`, si permet accés per índex.

```python todo
def describe2(value):
    # TODO: start from describe(value)
    # TODO: if value supports indexing, store first_item safely
    pass
```

*Pista*: accedir a `value[0]` pot llançar `TypeError` o `IndexError`. Captura totes dues excepcions.

---

### 22-4 · Validar callbacks (avançat i opcional)
Implementa `require_named_params(fn, required_names)` amb `inspect.signature`.
Afegeix proves per a:
- happy path;
- una funció amb `**kwargs`;
- paràmetres absents que llancen `TypeError`.

*Pista*: mira la secció d'ampliació, copia'n la idea i després prova-la.

---

## Errors habituals i com evitar-los
- **Utilitzar `type(x) == SomeType` a tot arreu**: prefereix `isinstance(x, SomeType)` per tenir flexibilitat.
- **Oblidar `()`**: `text.upper` és un mètode; `text.upper()` és el resultat.
- **Cridar `dir()` i sentir-se desbordat**: filtra la llista cercant una paraula.
- **Fer `getattr(obj, "x")` sense default**: llança `AttributeError` si no existeix.
- **Suposar que `vars(obj)` sempre funciona**: molts built-ins no ho admeten, i és normal.
- **Abusar de la introspecció**: és excel·lent per aprendre i depurar, però al codi real és millor dissenyar interfícies clares.

---

## Solucions explicades, breus i clares

### Solució 22-1
```python runnable
def report_types(values):
    result = []
    for v in values:
        result.append(f"{repr(v)} -> {type(v).__name__}")
    return result
```

### Solució 22-2
```python runnable
def call_method(obj, method_name, *args, **kwargs):
    attr = getattr(obj, method_name, None)
    if not callable(attr):
        raise TypeError(f"{type(obj).__name__} has no callable '{method_name}'")
    return attr(*args, **kwargs)
```

### Solució 22-3
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

### Solució 22-4 (nucli)
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

## Punt de control i rúbrica
- **Correcció**: el resultat compleix el contracte de la unitat.
- **Llegibilitat**: els noms i les responsabilitats s’entenen a la primera.
- **Errors**: es proven un cas vàlid, un límit i una recuperació.
- **Verificació**: els exemples i els exercicis s’executen en un entorn net.
- **Explicació**: pots justificar les decisions i els riscos.

## Reflexió final
Avui has après a *fer preguntes a Python* sobre els valors: què són, què poden fer i com utilitzar-los amb seguretat. És un superpoder per depurar i aprendre llibreries noves.

La pròxima vegada que vegis un error com «object has no attribute...», no t'espantis. Utilitza `type()`, `dir()`, `help()` i `getattr()` com un detectiu tranquil. Ho pots resoldre.
