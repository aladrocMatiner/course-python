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

---

## 1) La primera pregunta: ¿qué es esto?

### `type()` te dice el tipo exacto
```python
value = 42
print(type(value))          # <class 'int'>
print(type(value).__name__) # int
```

### `isinstance()` suele ser más seguro
```python
value = 42
print(isinstance(value, int))          # True
print(isinstance(value, (int, float))) # True (tupla = “cualquiera de estos”)
```

¿Por qué “más seguro”? Porque funciona con **subclases**:

```python
print(isinstance(True, int))  # True (bool es un tipo especial relacionado con int)
print(type(True) is int)      # False
```

### Caso especial: `None`
```python
x = None
print(x is None)          # forma estándar
print(type(x).__name__)   # NoneType
```

---

## 2) Imprimir para depurar: `str()` vs `repr()`
Para mostrar algo a una persona, `str()` está bien. Para depurar, `repr()` es tu mejor amiga porque intenta ser **sin ambigüedades**.

```python
text = "hello\nworld"
print(text)        # imprime dos líneas
print(repr(text))  # 'hello\nworld' (muestra el \n)
```

### Objetos propios: por qué `repr` ayuda
```python
class User:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"User({self.name})"

    def __repr__(self):
        return f"User(name={self.name!r})"  # !r usa repr()

u = User("Noor")
print(u)       # User(Noor)
print([u])     # [User(name='Noor')]
print(f"{u!r}")  # User(name='Noor')
```

Mucha gente se confunde aquí, y está bien: `print(u)` usa `str(u)`, pero las colecciones (como listas) suelen mostrar los elementos con `repr(...)`.

---

## 3) Atributos vs métodos (y la trampa del `()`)
Un **atributo** es un dato. Un **método** es algo que puedes llamar.

```python
text = "hello"
print(text.upper)            # esto es un método
print(callable(text.upper))  # True
print(text.upper())          # HELLO
```

Error típico:
```python
text = "hello"
shout = text.upper   # olvidaste () → shout no es un string
print(shout)         # <built-in method upper of str object at ...>
```

Si ves `<built-in method ...>`, significa que has cogido el método pero no lo has ejecutado.

---

## 4) Explorar un objeto desconocido: `dir()` + `help()`
### `dir(obj)` te da una lista de nombres
```python
text = "hello"
names = [name for name in dir(text) if "upper" in name]
print(names)  # ['isupper', 'upper']
```

La lista puede ser larga. Es normal. ¡Filtra!

### `help(...)` y docstrings explican cómo usarlo
```python
print(str.upper.__doc__)
```

Y si quieres el manual completo:
```python
help(str.upper)
```

---

## 5) Acceso seguro: `getattr()`, `hasattr()`, `vars()`

### `getattr(obj, "name", default)`
Perfecto cuando no sabes si existe el atributo:

```python
class Player:
    def __init__(self, name):
        self.name = name

p = Player("Frej")
print(getattr(p, "name", "<anonymous>"))      # Frej
print(getattr(p, "nickname", "<anonymous>")) # <anonymous>
```

### `hasattr(obj, "name")`
```python
print(hasattr(p, "name"))     # True
print(hasattr(p, "nickname")) # False
```

### `vars(obj)` (o `obj.__dict__`) para objetos simples
```python
print(vars(p))  # {'name': 'Frej'}
```

Importante: `vars()` **no** funciona con todos los objetos. Si falla, es normal.

---

## Mini‑proyecto: `describe(value)` (resumen seguro)
Vamos a escribir una función que devuelve un diccionario con pistas, sin romper el programa.

```python
def describe(value):
    info = {
        "type": type(value).__name__,
        "repr": repr(value),
        "is_callable": callable(value),
    }

    # ¿Tiene longitud?
    try:
        info["len"] = len(value)
        info["has_len"] = True
    except TypeError:
        info["len"] = None
        info["has_len"] = False

    # ¿Tiene atributo "name"?
    info["name_attr"] = getattr(value, "name", None)
    return info
```

---

## Bonus: validar parámetros de funciones con `inspect.signature()`
A veces aceptas una función (callback) y quieres asegurarte de que tiene los parámetros necesarios.

```python
import inspect

def require_named_params(fn, required_names):
    sig = inspect.signature(fn)
    params = sig.parameters

    # Si tiene **kwargs, puede aceptar cualquier argumento con nombre.
    if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()):
        return

    missing = [name for name in required_names if name not in params]
    if missing:
        raise TypeError(f"{fn.__name__} must accept: {', '.join(missing)}")
```

Esto es muy útil para testear: no solo pruebas “salidas”, también pruebas que tu sistema rechaza callbacks con forma incorrecta.

---

## Ejercicios guiados (con TODOs y pistas)

### 22-1 · Reporte de tipos (fácil)
```python
def report_types(values):
    # TODO: devuelve algo como:
    # ["'hi' -> str", "3 -> int", "None -> NoneType"]
    pass
```
*Pista*: `type(x).__name__` y `repr(x)`.

### 22-2 · Llamar un método con seguridad (medio)
```python
def call_method(obj, method_name, *args, **kwargs):
    # TODO 1: obtener el atributo con getattr(obj, method_name, None)
    # TODO 2: si no es callable, lanzar TypeError con mensaje claro
    # TODO 3: llamar y devolver el resultado
    pass
```
*Pista*: `callable(attr)`.

### 22-3 · Mejorar `describe(value)` (medio+)
```python
def describe2(value):
    # TODO: empieza desde describe(value)
    # TODO: si soporta indexado, guarda first_item con seguridad
    pass
```
*Pista*: `value[0]` puede lanzar `TypeError` o `IndexError`.

### 22-4 · Validar callbacks (avanzado, bonus)
Implementa `require_named_params(fn, required_names)` con `inspect.signature()` y añade tests.

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
```python
def report_types(values):
    result = []
    for v in values:
        result.append(f"{repr(v)} -> {type(v).__name__}")
    return result
```

### Solución 22-2
```python
def call_method(obj, method_name, *args, **kwargs):
    attr = getattr(obj, method_name, None)
    if not callable(attr):
        raise TypeError(f"{type(obj).__name__} has no callable '{method_name}'")
    return attr(*args, **kwargs)
```

---

## Reflexión final
Hoy has aprendido a “hacer preguntas” a los valores: qué son, qué pueden hacer y cómo usarlos con seguridad. Esto te ayuda muchísimo a depurar y a aprender librerías nuevas.

La próxima vez que veas un error tipo “object has no attribute…”, no te asustes: usa `type()`, `dir()`, `help()` y `getattr()` como un detective tranquilo.

