# Capítol 12 · Programació orientada a objectes: teoria i pràctica

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Crearem les primeres classes en Python, començant pel model mental d’“objecte” i acabant amb classes orientades a backend (usuaris, comandes, serveis). Veurem atributs, mètodes, `__init__`, herència, composició, `dataclasses` i bones pràctiques. És un capítol llarg perquè la POO necessita calma i exemples variats.

## Ordre pedagògic
1. **Model mental**: què és un objecte i per què existeix.
2. **Sintaxi bàsica**: atributs, `__init__`, mètodes.
3. **Representacions (`__repr__` / `__str__`)**.
4. **Mètodes de classe i estàtics**.
5. **Herència i composició**.
6. **Encapsulació lleugera i propietats**.
7. **`dataclasses`**.
8. **Patrons en backend**.
9. **Proves i exercicis**.

## Objectius d’aprenentatge
- Definir classes amb atributs i mètodes clars.
- Crear instàncies, canviar estat i representar objectes en text.
- Aplicar herència/composició sense jerarquies complicades.
- Usar `@property`, mètodes de classe i estàtics.
- Usar `dataclasses` quan necessites models lleugers (i fins i tot immutables).

## Per què importa
Els objectes et permeten modelar entitats del món real i agrupar dades + comportament. A Django, models, vistes i serializers són classes: entendre la base t’ajuda a estendre-les amb seguretat.

### Mini aventura
Pensa en una classe com un personatge d’un videojoc: té estadístiques (vida) i habilitats (saltar). Un objecte és un personatge concret amb els seus valors.

---

## 1. Model mental: objectes = “coses amb dades i accions”
Una classe és un plànol; els objectes són instàncies del plànol.

```python
class Usuario:
    def __init__(self, nombre, email):
        self.nombre = nombre
        self.email = email
        self.activo = True

    def desactivar(self):
        self.activo = False
```

### Crear instàncies
```python
noor = Usuario("Noor", "noor@example.com")
print(noor.nombre)
noor.desactivar()
print(noor.activo)  # False
```

---

## 2. Representar objectes (`__repr__` i `__str__`)

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

- `repr(obj)` ajuda a depurar.
- `str(obj)` és el que veus amb `print`.

---

## 3. Mètodes de classe i estàtics

```python
class Sesion:
    activa = 0

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

- `@classmethod` rep `cls` i pot accedir a dades de classe.
- `@staticmethod` és un helper dins la classe.

---

## 4. Herència i composició

### Herència
```python
class Notificacion:
    def enviar(self, mensaje):
        raise NotImplementedError

class EmailNotificacion(Notificacion):
    def enviar(self, mensaje):
        print(f"Email: {mensaje}")
```

### Composició
```python
class ServicioMensajes:
    def __init__(self, canal):
        self.canal = canal

    def enviar(self, mensaje):
        self.canal.enviar(mensaje)
```

- La composició sol ser més flexible que l’herència.

---

## 5. Propietats i encapsulació lleugera

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

---

## 6. `dataclasses` per models lleugers

```python
from dataclasses import dataclass

@dataclass
class Coordenada:
    lat: float
    lon: float
    etiqueta: str = ""
```

- Pots fer-les immutables amb `frozen=True`.

---

## 7. Patrons backend
- **Models**: dades + validacions (`Usuario`, `Pedido`).
- **Serveis**: orquestren passos (`ServicioMensajes`).
- **Repositoris**: accés a dades; poden acceptar funcions per transformar resultats.

```python
class ServicioDescuentos:
    def __init__(self, calculo_descuento):
        self.calculo_descuento = calculo_descuento

    def procesar(self, pedido):
        descuento = self.calculo_descuento(pedido)
        pedido.total -= descuento
        return pedido
```

---

## 8. Serialitzar i deserialitzar objectes
Serialitzar és convertir un objecte a `dict`/JSON per desar o enviar. Deserialitzar és reconstruir-lo.

### `to_dict` i `from_dict`
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

### `dataclasses.asdict`
```python
from dataclasses import dataclass, asdict

@dataclass
class Configuracion:
    env: str
    debug: bool = False

conf = Configuracion("prod")
conf_dict = asdict(conf)
```

Consell: valida camps obligatoris abans de construir instàncies i no confiïs en estructures externes.

---

## 9. Proves amb objectes

```python
# tests/test_usuario.py
from usuarios import Usuario

def test_usuario_se_desactiva():
    user = Usuario("Noor", "ana@example.com")
    user.desactivar()
    assert user.activo is False
```

---

## Exercicis guiats (amb TODOs)
1. **12-1 · Classe `Producto`**
   ```python
   class Producto:
       # TODO 1: defineix nombre, precio, stock
       # TODO 2: vendre(cantidad) resta stock i valida disponibilitat
       # TODO 3: implementa __repr__
   ```

2. **12-2 · Composició de serveis**
   ```python
   class EmailService:
       # TODO: send(mensaje)
       pass

   class SMSService:
       # TODO: send(mensaje)
       pass

   class NotificationCenter:
       # TODO 1: rep una llista de serveis
       # TODO 2: notify(mensaje)
   ```

3. **12-3 · Dataclass immutable**
   ```python
   from dataclasses import dataclass
   @dataclass(frozen=True)
   class Config:
       env: str
       debug: bool = False
   ```

---

## Errors comuns
- Oblidar `self` en mètodes.
- Confondre atributs de classe i d’instància.
- Fer herències profundes quan la composició era suficient.

---

## Resum
La POO et permet representar entitats amb claredat i aplicar patrons com herència, composició i propietats. Amb pràctica, sabràs quan usar classes o `dataclasses`.

## Reflexió final
Pren-te el temps de practicar. Classes ben dissenyades i proves petites fan que els projectes grans siguin molt més fàcils de mantenir.
