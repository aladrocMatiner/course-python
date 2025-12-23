# Chapter 12 · Object-Oriented Programming: Theory and Practice

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll create our first classes in Python, starting from the mental model of an “object” and ending with backend‑flavored classes (users, orders, services). We’ll cover attributes, methods, initialization, inheritance, composition, `dataclasses`, and good practices. This chapter is longer on purpose: OOP needs calm and lots of examples.

## Learning path
1. **Mental model**: what an object is and why it exists.
2. **Basic class syntax**: attributes, `__init__`, methods.
3. **Representations (`__repr__` / `__str__`)**.
4. **Class methods and static methods**.
5. **Inheritance and composition**: when to use each.
6. **Light encapsulation and properties**.
7. **`dataclasses` for lightweight models**.
8. **Backend usage patterns**.
9. **Tests and guided exercises**.

## Learning objectives
- Define classes with clear attributes and methods.
- Create instances, change state, and represent objects with friendly text.
- Use inheritance/composition without building complex hierarchies.
- Use `@property`, class methods, and static methods for specific rules.
- Use `dataclasses` when you need immutable or comparable containers.

## Why it matters
Objects let you model real-world entities and group data + behavior. In Django apps, models, views, and serializers are classes — understanding the basics helps you extend them safely.

### Mini adventure
Think of a class like a video‑game character template: it has stats (health, energy) and skills (jump, attack). An object is one concrete character with its own values. Your program stops being loose numbers and becomes a world of meaningful things.

---

## 1. Mental model: objects as “things with data and actions”
Think of a class as a blueprint and objects as instances of that blueprint. For example, a `Usuario` has data (`nombre`, `email`) and actions (deactivate, notify).

```python
class Usuario:
    def __init__(self, nombre, email):
        self.nombre = nombre
        self.email = email
        self.activo = True

    def desactivar(self):
        self.activo = False
```

- `self` is the instance itself.
- You usually create attributes in `__init__`.

### Creating instances
```python
noor = Usuario("Noor", "noor@example.com")
print(noor.nombre)
noor.desactivar()
print(noor.activo)  # False
```

---

## 2. Representing objects (`__repr__` and `__str__`)

```python
class Ticket:
    def __init__(self, id, estado):
        self.id = id
        self.estado = estado

    def __repr__(self):
        return f"Ticket(id={self.id!r}, estado={self.estado!r})"

    def __str__(self):
        return f"Ticket #{self.id} ({self.estado})"
```

- `repr(obj)` is a debugging-friendly representation.
- `str(obj)` is what `print` uses.

---

## 3. Class methods and static methods

```python
class Sesion:
    activa = 0  # atributo de clase

    def __init__(self, usuario):
        self.usuario = usuario
        Sesion.activa += 1

    @classmethod
    def creadas(cls):
        return cls.activa

    @staticmethod
    def formato_id(value):
        return f"SES-{value}"
```

- `@classmethod` receives `cls` (the class) and can read/modify class attributes.
- `@staticmethod` receives neither `self` nor `cls`; it’s a helper that lives inside the class namespace.

---

## 4. Inheritance and composition

### Inheritance
```python
class Notificacion:
    def enviar(self, mensaje):
        raise NotImplementedError

class EmailNotificacion(Notificacion):
    def enviar(self, mensaje):
        print(f"Email: {mensaje}")
```

- Use inheritance when classes share a common interface.

### Composition
```python
class ServicioMensajes:
    def __init__(self, canal):
        self.canal = canal

    def enviar(self, mensaje):
        self.canal.enviar(mensaje)
```

- Composition means one class uses another internally. It’s more flexible than inheritance for mixing behaviors.

---

## 5. Light encapsulation and properties

```python
class Cuenta:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, valor):
        if valor < 0:
            raise ValueError("Balance negativo no permitido")
        self._balance = valor
```

- `_balance` signals “internal use”.
- `@property` exposes getter/setter without changing the calling syntax (`cuenta.balance = 100`).

---

## 6. `dataclasses` for lightweight models

```python
from dataclasses import dataclass

@dataclass
class Coordenada:
    lat: float
    lon: float
    etiqueta: str = ""
```

- Generates `__init__`, `__repr__`, comparisons, and more.
- Great for immutable objects with `frozen=True`.

---

## 7. Backend patterns
- **Models**: hold data + validations (`Usuario`, `Pedido`).
- **Services**: orchestrate multiple steps (`ServicioMensajes`).
- **Repositories**: abstract data access; you can pass functions (callbacks) to transform results.

### Example
```python
class ServicioDescuentos:
    def __init__(self, calculo_descuento):
        self.calculo_descuento = calculo_descuento

    def procesar(self, pedido):
        descuento = self.calculo_descuento(pedido)
        pedido.total -= descuento
        return pedido
```

- `calculo_descuento` is a function: mixing OOP with higher‑order functions.

---

## 8. Serializing and deserializing objects
Serializing means turning an object into a structure (dict, JSON) so you can store it or send it. Deserializing is rebuilding the object from that structure.

### `to_dict` and `from_dict`
```python
class Pedido:
    def __init__(self, id, total, items):
        self.id = id
        self.total = total
        self.items = items

    def to_dict(self):
        return {
            "id": self.id,
            "total": self.total,
            "items": self.items,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            total=data["total"],
            items=data.get("items", []),
        )
```

```python
pedido = Pedido(1, 120, ["libro", "cuaderno"])
payload = pedido.to_dict()
pedido_recuperado = Pedido.from_dict(payload)
```

- Perfect for turning instances into JSON payloads or database records.

### JSON
```python
import json

class UsuarioJSON(Usuario):
    def to_json(self):
        return json.dumps({
            "nombre": self.nombre,
            "email": self.email,
        })

    @classmethod
    def from_json(cls, raw):
        data = json.loads(raw)
        return cls(data["nombre"], data["email"])
```

- Handle `json.JSONDecodeError` when data comes from external sources.

### `dataclasses.asdict`
```python
from dataclasses import dataclass, asdict

@dataclass
class Configuracion:
    env: str
    debug: bool = False

conf = Configuracion("prod")
conf_dict = asdict(conf)  # {'env': 'prod', 'debug': False}
```

- `asdict` converts dataclasses recursively into dicts ready to serialize.

### Safe deserialization
- Validate required fields before building the instance (`if "id" not in data: raise ValueError`).
- Convert types explicitly (`int(data["id"])`) when you expect numbers.
- Never trust external structures without checking them.

---

## 9. Testing objects
Use `pytest` to verify behavior.

```python
# tests/test_usuario.py
from usuarios import Usuario

def test_usuario_se_desactiva():
    user = Usuario("Noor", "ana@example.com")
    user.desactivar()
    assert user.activo is False
```

To run this test, create a `usuarios.py` file and copy the `Usuario` class from the start of this chapter.

- Check state before/after.
- For classes with dependencies, inject “test doubles” (simple mocks) that implement the same interface.

---

## Guided exercises (with TODOs)
1. **12-1 · `Producto` class**
   ```python
   class Producto:
       # TODO 1: define attributes nombre, precio, stock
       # TODO 2: add vender(cantidad) that subtracts stock and validates availability
       # TODO 3: implement __repr__ for debugging
   ```
   *Hint*: raise `ValueError` if `cantidad` > `stock`.

2. **12-2 · Service composition**
   ```python
   class EmailService:
       # TODO: implement send(mensaje)
       pass

   class SMSService:
       # TODO: implement send(mensaje)
       pass

   class NotificationCenter:
       # TODO 1: accept a list of services
       # TODO 2: implement notify(mensaje)
   ```
   *Hint*: loop over services and call `service.send(mensaje)`.

3. **12-3 · Immutable dataclass**
   ```python
   from dataclasses import dataclass
   @dataclass(frozen=True)
   class Config:
       env: str
       debug: bool = False
   # TODO 1: show how to create a new config changing env
   # TODO 2: explain why frozen prevents accidental modifications
   ```

---

## Common mistakes
- Forgetting `self` as the first parameter in methods (causes `TypeError`).
- Defining attributes outside `__init__` without realizing they become class attributes.
- Building deep inheritance trees when composition was enough.
- Not documenting what subclasses must implement ⇒ missing `NotImplementedError`.

---

## Explained solutions
1. **Producto**: `vender` checks stock, subtracts, and returns the new value; `__repr__` helps inspect instances in logs.
2. **NotificationCenter**: it receives services that share `send()`. Composition lets you add/remove channels without multiple inheritance.
3. **Immutable Config**: `dataclass(frozen=True)` blocks reassignment; to “change” values use `replace(config, env="prod")` (requires importing it). This protects sensitive configuration.

---

## Summary
OOP in Python helps you represent real entities clearly, group data + behavior, and apply patterns like inheritance, composition, and properties. With practice, you’ll know when to use classic classes vs `dataclasses`.

## Closing reflection
Building well‑designed classes is a key step toward larger projects. Take your time to practice, write tests, and keep each class focused on a single responsibility. In later chapters, these pieces will combine into complete applications.
