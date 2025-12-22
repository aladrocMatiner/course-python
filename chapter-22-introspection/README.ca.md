# Capítol 22 · Introspecció: mode detectiu en Python

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
En aquest capítol aprendràs *introspecció*: com mirar un valor i preguntar-li “què ets?” i “què pots fer?”. Farem servir eines com `type()`, `isinstance()`, `dir()`, `help()`, `getattr()` i `callable()` per explorar sense trencar res.

Després construirem una mini eina de “detectiu” anomenada `describe(value)` i (bonus) aprendràs a inspeccionar els paràmetres d’una funció amb `inspect.signature()` per validar callbacks i escriure millors proves.

## Ordre pedagògic
1. **Detectar el tipus**: `type`, `isinstance` (i el cas `None`).
2. **Imprimir per depurar**: `str` vs `repr`.
3. **Mètodes vs atributs**: `callable` i la trampa del `()`.
4. **Explorar objectes desconeguts**: `dir`, `help` i docstrings.
5. **Accés segur**: `getattr`, `hasattr`, `vars`.
6. **Mini‑projecte**: `describe(value)` (resum segur d’un objecte).
7. **Bonus**: `inspect.signature()` per validar paràmetres + proves amb pytest.

## Objectius d’aprenentatge
- Saber quin tipus té un valor i comprovar-ho amb `isinstance`.
- Fer servir `repr()` per depurar i entendre `str()` vs `repr()`.
- Evitar errors típics com “oblidar els parèntesis”.
- Explorar un objecte desconegut amb calma.
- Llegir atributs de forma segura (`getattr`) i detectar capacitats (`callable`).
- Construir i provar utilitats petites.

## Per què importa
Quan aprens, et trobaràs valors que encara no entens del tot. La introspecció et dona una manera segura de mirar-los i aprendre.

En backend real, els frameworks també fan introspecció: “això és callable?”, “accepta `request`?”, “té `.save()`?”. No cal màgia: només bases sòlides.

### Mini aventura: ets un detectiu de Python
- `type()` és l’**escàner d’identitat**.
- `dir()` és la **llista d’eines**.
- `help()` i `__doc__` són el **manual**.
- `getattr()` és la **pinça segura** (atribut o valor per defecte).

És normal que al principi no sigui obvi. Es practica jugant.

---

## 1) La primera pregunta: què és això?
```python
value = 42
print(type(value))
print(type(value).__name__)
print(isinstance(value, int))
print(isinstance(value, (int, float)))
```

Cas especial:
```python
x = None
print(x is None)
print(type(x).__name__)
```

---

## 2) Depurar: `str()` vs `repr()`
```python
text = "hello\nworld"
print(text)
print(repr(text))
```

---

## 3) Atributs vs mètodes
```python
text = "hello"
print(text.upper)
print(callable(text.upper))
print(text.upper())
```

---

## 4) Explorar: `dir()` + `help()`
```python
text = "hello"
names = [name for name in dir(text) if "upper" in name]
print(names)
print(str.upper.__doc__)
help(str.upper)
```

---

## 5) Accés segur: `getattr()`, `hasattr()`, `vars()`
```python
class Player:
    def __init__(self, name):
        self.name = name

p = Player("Frej")
print(getattr(p, "name", "<anonymous>"))
print(getattr(p, "nickname", "<anonymous>"))
print(hasattr(p, "name"))
print(vars(p))
```

---

## Mini‑projecte: `describe(value)`
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

## Bonus: validar paràmetres amb `inspect.signature()`
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

## Exercicis guiats (TODOs + pistes)
1. **22-1 · Report de tipus**: implementa `report_types(values)`.
2. **22-2 · Cridar un mètode amb seguretat**: implementa `call_method(...)`.
3. **22-3 · Millorar `describe`**: afegeix `first_item` de forma segura.
4. **22-4 · Validar callbacks (bonus)**: implementa `require_named_params` + proves.

---

## Errors comuns
- Oblidar `()` en un mètode.
- `dir()` és llarg: filtra.
- `getattr` sense default pot fallar.
- `vars()` no funciona amb tot.

---

## Reflexió final
La introspecció és com una llanterna per aprendre i depurar. Si tens dubtes, fes preguntes al valor amb `type()`, `dir()` i `help()` i avança pas a pas.

