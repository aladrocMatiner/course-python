# Capítulo 12 · Programación orientada a objetos: teoría y práctica

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Crearemos nuestras primeras clases en Python, empezando por el modelo mental de “objeto” y terminando con clases orientadas a backend (usuarios, órdenes, servicios). Cubriremos atributos, métodos, inicialización, herencia, composición, `dataclasses` y buenas prácticas. Este capítulo es más largo porque la OOP requiere calma y ejemplos variados.

## Orden pedagógico
1. **Modelo mental**: qué es un objeto y por qué existen.
2. **Sintaxis básica de clase**: atributos, `__init__`, métodos.
3. **Representaciones (`__repr__` / `__str__`)**.
4. **Métodos de clase y estáticos**.
5. **Herencia y composición**: cuándo usarlas.
6. **Encapsulación ligera y propiedades**.
7. **`dataclasses` para modelos ligeros**.
8. **Patrones de uso en backend**.
9. **Pruebas y ejercicios guiados**.

## Objetivos de aprendizaje
- Definir clases con atributos y métodos claros.
- Crear instancias, modificar su estado y representar objetos con texto amigable.
- Aplicar herencia/composición sin caer en jerarquías complicadas.
- Usar `@property`, métodos de clase y estáticos para reglas específicas.
- Incorporar `dataclasses` cuando necesites contenedores inmutables o comparables.

## Por qué importa
Los objetos permiten modelar entidades del mundo real y agrupar datos + comportamiento. En aplicaciones Django, los modelos, vistas y serializers son clases; comprender su base te permite extenderlos con seguridad.

### Mini aventura
Piensa en una clase como un personaje de videojuego: tiene estadísticas (vida, energía) y habilidades (saltar, atacar). Un objeto es “un personaje concreto” con sus valores. Así tu programa deja de ser solo números sueltos y se vuelve un mundo con cosas con sentido.

---

## 1. Modelo mental: objetos como “cosas con datos y acciones”
Piensa en una clase como un plano y en los objetos como instancias del plano. Por ejemplo, un `Usuario` tiene datos (`nombre`, `email`) y acciones (activar, enviar notificación).

```python
class Usuario:
    def __init__(self, nombre, email):
        self.nombre = nombre
        self.email = email
        self.activo = True

    def desactivar(self):
        self.activo = False
```

- `self` es la propia instancia.
- Los atributos se crean en `__init__`.

### Creando instancias
```python
ada = Usuario("Ada", "ada@example.com")
print(ada.nombre)
ada.desactivar()
print(ada.activo)  # False
```

---

## 2. Representar objetos (`__repr__` y `__str__`)

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

- `repr(obj)` muestra una cadena útil para debugging.
- `str(obj)` se usa en `print`.

---

## 3. Métodos de clase y estáticos

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

- `@classmethod` recibe `cls` (la clase) y puede acceder/modificar atributos de clase.
- `@staticmethod` no recibe `self` ni `cls`; funciona como helper dentro de la clase.

---

## 4. Herencia y composición
### Herencia
```python
class Notificacion:
    def enviar(self, mensaje):
        raise NotImplementedError

class EmailNotificacion(Notificacion):
    def enviar(self, mensaje):
        print(f"Email: {mensaje}")
```

- Usa herencia cuando todas las clases comparten una interfaz común.

### Composición
```python
class ServicioMensajes:
    def __init__(self, canal):
        self.canal = canal

    def enviar(self, mensaje):
        self.canal.enviar(mensaje)
```

- Composición = una clase utiliza otra internamente. Más flexible que herencia para mezclar comportamientos.

---

## 5. Encapsulación ligera y propiedades

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

- `_balance` indica “uso interno”.
- `@property` expone un getter/setter sin cambiar la sintaxis (`cuenta.balance = 100`).

---

## 6. `dataclasses` para modelos ligeros

```python
from dataclasses import dataclass

@dataclass
class Coordenada:
    lat: float
    lon: float
    etiqueta: str = ""
```

- Genera `__init__`, `__repr__`, comparaciones y más.
- Ideal para objetos inmutables si usas `frozen=True`.

---

## 7. Patrones backend
- **Modelos**: encapsulan datos + validaciones (`Usuario`, `Pedido`).
- **Servicios**: clases que orquestan múltiples pasos (`ServicioMensajes`).
- **Repositorios**: abstraen acceso a datos; permiten pasar funciones (callbacks) para transformar resultados.

### Ejemplo
```python
class ServicioDescuentos:
    def __init__(self, calculo_descuento):
        self.calculo_descuento = calculo_descuento

    def procesar(self, pedido):
        descuento = self.calculo_descuento(pedido)
        pedido.total -= descuento
        return pedido
```

- `calculo_descuento` es una función; mezcla OOP con funciones de orden superior.

---

## 8. Serializar y deserializar objetos

Serializar significa convertir un objeto en una estructura (dict, JSON) para guardarlo o enviarlo. Deserializar es reconstruirlo desde esa estructura.

### Métodos `to_dict` y `from_dict`
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

- Perfecto para convertir instancias en payloads JSON o registros de base de datos.

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

- Maneja `json.JSONDecodeError` cuando los datos vienen de fuentes externas.

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

- `asdict` convierte recursivamente dataclasses en dicts listos para serializar.

### Deserialización segura
- Valida campos obligatorios antes de construir la instancia (`if "id" not in data: raise ValueError`).
- Convierte tipos explícitamente (`int(data["id"])`) si esperas números.
- Nunca confíes en la estructura externa sin verificarla.

---

## 9. Pruebas con objetos
Usa `pytest` para verificar comportamiento.

```python
# tests/test_usuario.py
from usuarios import Usuario

def test_usuario_se_desactiva():
    user = Usuario("Ana", "ana@example.com")
    user.desactivar()
    assert user.activo is False
```

Para poder ejecutar este test, crea un archivo `usuarios.py` y copia dentro la clase `Usuario` que aparece al inicio del capítulo.

- Comprueba estados antes/después.
- Para clases con dependencias, inyecta objetos “doble” (mocks simples) que implementen la misma interfaz.

---

## Ejercicios guiados (con TODOs)
1. **12-1 · Clase `Producto`**
   ```python
   class Producto:
       # TODO 1: define atributos nombre, precio, stock
       # TODO 2: agrega método vender(cantidad) que reste stock y valide disponibilidad
       # TODO 3: implementa __repr__ para debugging
   ```
   *Pista*: lanza `ValueError` si `cantidad` > `stock`.

2. **12-2 · Composición de servicios**
   ```python
   class EmailService:
       # TODO: implementa send(mensaje)
       pass

   class SMSService:
       # TODO: implementa send(mensaje)
       pass

   class NotificationCenter:
       # TODO 1: acepta una lista de servicios
       # TODO 2: implementa notify(mensaje)
   ```
   *Pista*: recorre cada servicio y llama `service.send(mensaje)`.

3. **12-3 · Dataclass inmutable**
   ```python
   from dataclasses import dataclass
   @dataclass(frozen=True)
   class Config:
       env: str
       debug: bool = False
   # TODO 1: muestra cómo crear una nueva config cambiando env
   # TODO 2: explica por qué frozen evita modificaciones accidentales
   ```

---

## Errores comunes
- Olvidar `self` como primer parámetro en métodos (provoca `TypeError`).
- Definir atributos fuera de `__init__` sin entender que son de clase.
- Crear jerarquías profundas cuando bastaba con composición.
- No documentar qué métodos deben implementar las subclases ⇒ `NotImplementedError` ausente.

---

## Explicación de soluciones
1. **Producto**: `vender` verifica stock, resta y devuelve el nuevo valor; `__repr__` ayuda a inspeccionar la instancia en logs.
2. **NotificationCenter**: recibe servicios que compartan `send()`. Composición permite agregar/quitar canales sin herencia múltiple.
3. **Config inmutable**: `dataclass(frozen=True)` bloquea reasignaciones; para “modificar” usa `replace(config, env="prod")` (requiere import). Esto protege configuraciones sensibles.

---

## Resumen
La OOP en Python te permite representar entidades reales con claridad, mezclar datos y comportamiento, y aplicar patrones como herencia, composición y propiedades. Con práctica, sabrás cuándo usar clases tradicionales o `dataclasses` según el caso.

## Reflexión final
Construir clases bien pensadas es un paso clave hacia proyectos más grandes. Tómate tu tiempo para practicar, escribir pruebas y mantener cada clase con una responsabilidad principal. En capítulos posteriores, estas piezas se combinarán para formar aplicaciones completas.
