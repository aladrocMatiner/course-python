# Capítulo 22 · Introspección: modo detective en Python

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
En este capítulo aprenderás *introspección*: cómo mirar un valor y preguntarle “¿qué eres?” y “¿qué puedes hacer?”. Usaremos herramientas como `type()`, `isinstance()`, `dir()`, `help()`, `getattr()` y `callable()` para explorar con seguridad.

Luego construiremos una mini herramienta de “detective” llamada `describe(value)` y (bonus) aprenderás a inspeccionar los parámetros de una función con `inspect.signature()` para validar callbacks y escribir mejores tests.

## Orden pedagógico
1. **Detectar el tipo**: `type`, `isinstance` (y el caso `None`).
2. **Imprimir para depurar**: `str` vs `repr` (por qué `repr` ayuda tanto).
3. **Métodos vs atributos**: `callable` y la trampa de “me falta el `()`”.
4. **Explorar objetos desconocidos**: `dir`, `help` y docstrings.
5. **Acceso seguro**: `getattr`, `hasattr`, `vars` (y cuándo fallan).
6. **Mini‑proyecto**: `describe(value)` (resumen seguro de un objeto).
7. **Bonus**: `inspect.signature()` para validar parámetros + tests con pytest.

## Objetivos de aprendizaje
- Saber el tipo de un valor y comprobarlo de forma segura con `isinstance`.
- Usar `repr()` para depurar valores “misteriosos” y entender `str()` vs `repr()`.
- Evitar errores típicos como “olvidar los paréntesis” de un método.
- Explorar un objeto desconocido sin romper el programa.
- Leer atributos con seguridad y detectar capacidades (`callable`, `hasattr`).
- Construir y testear utilidades pequeñas que validan inputs y callbacks.

## Por qué importa
Cuando aprendes, te encuentras valores que aún no entiendes del todo: strings, listas, diccionarios, objetos de librerías… La introspección te da una forma segura de explorarlos.

En proyectos backend reales, los frameworks también usan introspección: “¿esto es callable?”, “¿acepta `request`?”, “¿tiene `.save()`?”, “¿qué campos existen?”. No hace falta magia: solo aprender lo básico, bien.

### Mini aventura: eres un detective de Python
Imagina que eres detective con una linterna:
- `type()` es tu **escáner de identidad** (“¿qué eres?”).
- `dir()` es tu **lista de herramientas** (“¿qué puedes hacer?”).
- `help()` y `__doc__` son el **manual** (“¿cómo funciona?”).
- `getattr()` es tu **pinza segura** (“dame ese atributo, o un valor por defecto”).

Es normal que al principio suene raro. Se aprende jugando con valores reales.

## Prerrequisitos
Capítulos previos recomendados: 2, 11, 12, 14 (و18 للقسم الإضافي).
Usa CPython 3.11+ en un entorno local desechable y mantén los datos, secretos y servicios fuera de sistemas reales.

---

## 1) La primera pregunta: ¿qué es esto?

### `type()` te dice el tipo exacto
```python runnable
value = 42
print(type(value))          # <class 'int'>
print(type(value).__name__) # int
```

### `isinstance()` suele ser más seguro
```python runnable
value = 42
print(isinstance(value, int))          # True
print(isinstance(value, (int, float))) # True (tuple means “any of these”)
```

¿Por qué “más seguro”? Porque funciona con **subclases**:

```python runnable
print(isinstance(True, int))  # True (bool is a kind of int in Python)
print(type(True) is int)      # False (exact type is bool)
```

### Caso especial: `None`
```python runnable
x = None
print(x is None)          # the standard way
print(type(x).__name__)   # NoneType
```

---

## 2) Imprimir para depurar: `str()` vs `repr()`
Para mostrar algo a una persona, `str()` está bien. Para depurar, `repr()` es tu mejor amiga porque intenta ser **sin ambigüedades**.

```python runnable
text = "hello\nworld"
print(text)        # prints two lines
print(repr(text))  # 'hello\nworld' (shows the \n)
```

### Objetos propios: por qué `repr` ayuda
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

Mucha gente se confunde aquí, y está bien: `print(u)` usa `str(u)`, pero las colecciones (como listas) suelen mostrar los elementos con `repr(...)`.

---

## 3) Atributos vs métodos (y la trampa del `()`)
Un **atributo** es un dato. Un **método** es algo que puedes llamar.

```python runnable
text = "hello"
print(text.upper)         # this is a method object
print(callable(text.upper))  # True
print(text.upper())       # HELLO
```

Error típico:
```python runnable
text = "hello"
shout = text.upper   # forgot () → shout is not a string
print(shout)         # <built-in method upper of str object at ...>
```

Si ves `<built-in method ...>`, significa que has cogido el método pero no lo has ejecutado.

---

## 4) Explorar un objeto desconocido: `dir()` + `help()`
### `dir(obj)` te da una lista de nombres
```python runnable
text = "hello"
names = [name for name in dir(text) if "upper" in name]
print(names)  # ['isupper', 'upper']
```

La lista puede ser larga. Es normal. ¡Filtra!

### `help(...)` y docstrings explican cómo usarlo
```python runnable
print(str.upper.__doc__)
```

Y si quieres el manual completo:
```python runnable
help(str.upper)
```

---

## 5) Acceso seguro: `getattr()`, `hasattr()`, `vars()`

### `getattr(obj, "name", default)`
Perfecto cuando no sabes si existe el atributo:

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

### `vars(obj)` (o `obj.__dict__`) para objetos simples
```python illustrative
print(vars(p))  # {'name': 'Frej'}
```

Importante: `vars()` **no** funciona con todos los objetos. Si falla, es normal.

---

## Mini‑proyecto: `describe(value)` (resumen defensivo)
Vamos a escribir una función que devuelve un diccionario con pistas, sin romper el programa.

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

Esta herramienta ofrece pistas defensivas para valores ordinarios; `repr()` y las propiedades pueden ejecutar código del objeto, por lo que no promete seguridad frente a objetos hostiles.

---

## Bonus: validar parámetros de funciones con `inspect.signature()`
A veces aceptas una función (callback) y quieres asegurarte de que tiene los parámetros necesarios.

Por ejemplo, queremos un callback que pueda aceptar `user_id` y `payload`.

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

### Demostración rápida

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

### Tests pequeños con pytest

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

Aquí no solo comprobamos resultados: verificamos que el sistema rechaza pronto una función con una forma incorrecta y ofrece un error claro.

---

## Ejercicios guiados (con TODOs y pistas)

### 22-1 · Reporte de tipos (fácil)
Escribe una función que devuelva una lista de textos con el tipo de cada valor.

```python todo
def report_types(values):
    # TODO: return something like:
    # ["'hi' -> str", "3 -> int", "None -> NoneType"]
    pass
```
*Pista*: `type(x).__name__` y `repr(x)`.

---

### 22-2 · Llamar un método con seguridad (medio)
Escribe una función que llame un método **solo si existe y es callable**.

```python todo
def call_method(obj, method_name, *args, **kwargs):
    # TODO 1: fetch attribute with getattr(obj, method_name, None)
    # TODO 2: if not callable, raise TypeError with a friendly message
    # TODO 3: call and return the result
    pass
```
*Pista*: `callable(attr)`.

---

### 22-3 · Mejorar `describe(value)` (medio+)
Amplía `describe(value)` para incluir `has_items` y `first_item` cuando el valor se pueda indexar, además de `has_len` y `len`.

```python todo
def describe2(value):
    # TODO: start from describe(value)
    # TODO: if value supports indexing, store first_item safely
    pass
```
*Pista*: `value[0]` puede lanzar `TypeError` o `IndexError`.

---

### 22-4 · Validar callbacks (avanzado, bonus)
Implementa `require_named_params(fn, required_names)` con `inspect.signature()` y añade tests para el camino correcto, una función con `**kwargs` y parámetros ausentes que lancen `TypeError`.

*Pista*: reutiliza la idea de la sección Bonus y después prueba cada contrato por separado.

---

## Errores comunes (y cómo evitarlos)
- **Usar `type(x) == Tipo` para todo**: mejor `isinstance(x, Tipo)`.
- **Olvidar `()`**: `text.upper` es un método, `text.upper()` es el resultado.
- **Hacer `dir()` y agobiarte**: filtra por una palabra.
- **Usar `getattr(obj, "x")` sin default**: puede lanzar `AttributeError`.
- **Creer que `vars(obj)` siempre funciona**: no en muchos objetos built‑in.
- **Pasarte con introspección**: es genial para aprender/depurar, pero mejor diseñar interfaces claras.

---

## Soluciones explicadas (cortas)

### Solución 22-1
```python runnable
def report_types(values):
    result = []
    for v in values:
        result.append(f"{repr(v)} -> {type(v).__name__}")
    return result
```

### Solución 22-2
```python runnable
def call_method(obj, method_name, *args, **kwargs):
    attr = getattr(obj, method_name, None)
    if not callable(attr):
        raise TypeError(f"{type(obj).__name__} has no callable '{method_name}'")
    return attr(*args, **kwargs)
```

### Solución 22-3

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

La solución captura solo los dos fallos esperados: un valor que no permite indexación o una colección vacía. Otros errores siguen visibles para poder diagnosticarlos.

### Solución 22-4 (núcleo)

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

Primero se acepta `**kwargs`, porque puede recibir cualquier nombre. Si no existe, calculamos exactamente qué nombres faltan y los incluimos en un diagnóstico recuperable.

---

## Punto de control y rúbrica
- **Corrección**: el resultado cumple el contrato de la unidad.
- **Legibilidad**: nombres y responsabilidades se entienden a la primera.
- **Errores**: se prueban un caso válido, un límite y una recuperación.
- **Verificación**: los ejemplos y ejercicios se ejecutan en un entorno limpio.
- **Explicación**: puedes justificar las decisiones y sus riesgos.

## Reflexión final
Hoy has aprendido a “hacer preguntas” a los valores: qué son, qué pueden hacer y cómo usarlos con seguridad. Esto te ayuda muchísimo a depurar y a aprender librerías nuevas.

La próxima vez que veas un error tipo “object has no attribute…”, no te asustes: usa `type()`, `dir()`, `help()` y `getattr()` como un detective tranquilo.
