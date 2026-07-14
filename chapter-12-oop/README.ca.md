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
- Usar `dataclasses` per a contenidors lleugers de valors i configurar deliberadament la igualtat, l’ordre o el bloqueig de reassignacions.

## Prerequisits i anticipacions opcionals
Abans de començar, repassa els [diccionaris](../chapter-04-dictionaries/README.ca.md) i les [funcions](../chapter-11-functions/README.ca.md). Has de poder definir una funció, passar arguments, retornar un valor i actualitzar un diccionari sense modificar dades no relacionades.

Les [excepcions](../chapter-14-exceptions/README.ca.md) i les [proves amb pytest](../chapter-18-testing/README.ca.md) apareixen com a anticipacions opcionals. En una primera lectura només cal reconèixer que `raise` rebutja un estat invàlid i que `assert` comprova un resultat esperat.

## Per què importa
Els objectes et permeten modelar entitats del món real i agrupar dades + comportament. A Django, models, vistes i serializers són classes: entendre la base t’ajuda a estendre-les amb seguretat.

### Mini aventura
Pensa en una classe com un personatge d’un videojoc: té estadístiques (vida) i habilitats (saltar). Un objecte és un personatge concret amb els seus valors.

## Predicció inicial
Abans d’executar el primer exemple, identifica la classe, la instància, els atributs i el mètode. Prediu l’estat just després de construir-la i després d’una crida. Les prediccions sobre `Cuenta`, propietats i `frozen=True` pertanyen a les rutes opcionals i no calen per al punt essencial.

## Rutes d’aprenentatge
- **Ruta essencial · 70–100 min en dues sessions:** estudia les seccions 1–2, l’exercici 12-0, la recuperació i el punt essencial. Resultat: definir una classe, construir instàncies independents, canviar estat amb un mètode i implementar una representació útil. Les crides directes i l’estat imprès són l’evidència; no exigeix excepcions ni pytest.
- **Ruta professional opcional · unes dues sessions més:** estudia les seccions 3–5 i 7–9 després d’[excepcions](../chapter-14-exceptions/README.ca.md) i [proves](../chapter-18-testing/README.ca.md). Resultat: validar invariants, triar composició o herència, serialitzar un límit i substituir una dependència en una prova.
- **Ruta avançada opcional · una sessió aproximada:** estudia la secció 6 i la serialització personalitzada de la secció 8. Resultat: explicar `eq`, `order`, `frozen`, `replace` i mutabilitat anidada amb exemples observats.

---

## 1. Model mental: objectes = “coses amb dades i accions”
Una classe és un plànol; els objectes són instàncies del plànol. Per exemple, un `Usuario` conté dades (`nombre`, `email`) i accions (desactivar, notificar).

```python runnable
class Usuario:
    def __init__(self, nombre, email):
        self.nombre = nombre
        self.email = email
        self.activo = True

    def desactivar(self):
        self.activo = False
```

- `self` és la instància mateixa.
- Normalment crees els atributs a `__init__`.

### Crear instàncies
```python illustrative
noor = Usuario("Noor", "noor@example.com")
print(noor.nombre)
noor.desactivar()
print(noor.activo)  # False
```

---

## 2. Representar objectes (`__repr__` i `__str__`)

```python runnable
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

```python runnable
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
```python runnable
class Notificacion:
    def enviar(self, mensaje):
        raise NotImplementedError

class EmailNotificacion(Notificacion):
    def enviar(self, mensaje):
        print(f"Email: {mensaje}")
```

- Usa l'herència quan les classes comparteixen una interfície comuna.

### Composició
```python runnable
class ServicioMensajes:
    def __init__(self, canal):
        self.canal = canal

    def enviar(self, mensaje):
        self.canal.enviar(mensaje)
```

- La composició vol dir que una classe n'usa una altra internament. Sol ser més flexible que l'herència per combinar comportaments.

---

## 5. Propietats i encapsulació lleugera

```python runnable
class Cuenta:
    def __init__(self, balance):
        self.balance = balance

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, valor):
        if valor < 0:
            raise ValueError("Balance negativo no permitido")
        self.__balance = valor
```

- `__balance` usa *name mangling* per reduir escriptures directes accidentals; no és una frontera de seguretat. Tant la construcció normal com l’assignació passen per la propietat que valida.
- `@property` exposa lectura i escriptura controlades sense canviar la sintaxi de crida: `cuenta.balance = 100`.

---

## 6. `dataclasses` per models lleugers

```python runnable
from dataclasses import dataclass

@dataclass
class Coordenada:
    lat: float
    lon: float
    etiqueta: str = ""
```

- Per defecte, `@dataclass` genera `__init__`, `__repr__` i igualtat (`eq=True`). Els mètodes d’ordre requereixen `order=True` i que els camps participants admetin aquestes comparacions.
- `frozen=True` bloqueja la reassignació normal de camps, però no aporta immutabilitat profunda: un valor mutable desat en un camp encara pot canviar.

---

## 7. Patrons backend
- **Models**: dades + validacions (`Usuario`, `Pedido`).
- **Serveis**: orquestren passos (`ServicioMensajes`).
- **Repositoris**: accés a dades; poden acceptar funcions per transformar resultats.

### Exemple
```python runnable
class ServicioDescuentos:
    def __init__(self, calculo_descuento):
        self.calculo_descuento = calculo_descuento

    def procesar(self, pedido):
        descuento = self.calculo_descuento(pedido)
        pedido.total -= descuento
        return pedido
```

`calculo_descuento` és una funció: l'exemple combina POO amb funcions d'ordre superior.

---

## 8. Serialitzar i deserialitzar objectes
Serialitzar és convertir un objecte a `dict`/JSON per desar o enviar. Deserialitzar és reconstruir-lo.

### `to_dict` i `from_dict`
```python runnable
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

```python illustrative
pedido = Pedido(1, 120, ["llibre", "quadern"])
payload = pedido.to_dict()
pedido_recuperado = Pedido.from_dict(payload)
```

Aquest patró és útil per convertir instàncies en payloads JSON o registres de base de dades.

### JSON
```python illustrative
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

Captura `json.JSONDecodeError` quan el text provingui d'una font externa.

### `dataclasses.asdict`
```python runnable
from dataclasses import dataclass, asdict

@dataclass
class Configuracion:
    env: str
    debug: bool = False

conf = Configuracion("prod")
conf_dict = asdict(conf)  # {'env': 'prod', 'debug': False}
```

`asdict` converteix recursivament les dataclasses en diccionaris preparats per serialitzar.

### Deserialització segura
- Valida els camps obligatoris abans de construir la instància: `if "id" not in data: raise ValueError(...)`.
- Converteix els tipus explícitament, per exemple amb `int(data["id"])`, quan esperis nombres.
- No confiïs mai en estructures externes sense comprovar-les.

---

## 9. Proves amb objectes

```python illustrative
# tests/test_usuario.py
from usuarios import Usuario

def test_usuario_se_desactiva():
    user = Usuario("Noor", "ana@example.com")
    user.desactivar()
    assert user.activo is False
```

Per executar aquesta prova, crea un fitxer `usuarios.py` i copia-hi la classe `Usuario` de l'inici del capítol.

- Comprova l'estat abans i després de l'acció.
- Per a classes amb dependències, injecta dobles de prova senzills que implementin la mateixa interfície.

---

## Pràctica essencial i recuperació

### 12-0 · Dos comptadors independents

Prediu totes dues representacions, executa el bloc i explica per què canviar `first` no canvia `second`:

```python runnable
class Counter:
    def __init__(self, start=0):
        self.value = start

    def increment(self):
        self.value += 1

    def __repr__(self):
        return f"Counter(value={self.value})"


first = Counter()
second = Counter(10)
first.increment()
print(first)
print(second)
```

La classe següent omet `self` expressament; cridar-ne el mètode produeix el `TypeError` esperat:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
class Counter:
    def increment():
        pass


counter = Counter()
counter.increment()
```

Recupera’t acceptant la instància explícitament i observa l’estat canviat:

```python runnable
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1


counter = Counter()
counter.increment()
print(counter.value)
```

Els dos estats impresos i la sortida de recuperació són l’evidència essencial. Atura’t abans d’herència, properties, dataclasses, serialització i pytest.

## Exercicis guiats (amb TODOs)
1. **12-1 · Classe `Producto`**
   ```python todo
   class Producto:
       # TODO 1: defineix nombre, precio, stock
       # TODO 2: vendre(cantidad) resta stock i valida disponibilitat
       # TODO 3: implementa __repr__
   ```
   *Pista*: llança `ValueError` si `cantidad > stock`.

2. **12-2 · Composició de serveis**
   ```python todo
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
   *Pista*: recorre els serveis i crida `service.send(mensaje)`.

3. **12-3 · Dataclass immutable**
   ```python todo
   from dataclasses import dataclass, replace
   @dataclass(frozen=True)
   class Config:
       env: str
       debug: bool = False
   # TODO 1: mostra com crear una configuració nova canviant env
   # TODO 2: explica per què frozen evita modificacions accidentals
   ```

---

## Errors comuns
- Oblidar `self` en mètodes.
- Confondre atributs de classe i d’instància.
- Fer herències profundes quan la composició era suficient.
- No documentar què han d'implementar les subclasses: una classe base pot usar `NotImplementedError` per fer explícit el contracte.

---

## Solucions explicades
1. **Producto**: `vendre` comprova l'estoc, el redueix i retorna el valor nou. Si la quantitat supera la disponibilitat, llança `ValueError`; `__repr__` facilita inspeccionar la instància als logs.
2. **NotificationCenter**: rep serveis que comparteixen el mètode `send()`. La composició permet afegir o eliminar canals sense crear una jerarquia d'herència múltiple.
3. **Config congelada**: `dataclass(frozen=True)` bloqueja la reassignació normal de camps. Com que `replace` s’importa més amunt, `nueva = replace(config, env="prod")` crea una còpia modificada. Això redueix reassignacions accidentals, però no congela profundament els valors mutables dels camps.

---

## Punt de control i rúbrica
Crea una classe `Counter` amb valor inicial, un mètode que canviï estat i un `__repr__` llegible. Construeix dues instàncies, canvia’n només una, imprimeix totes dues i reprodueix i corregeix el `TypeError` per ometre `self`. Usa crides directes; no exigeix excepcions ni pytest.

Suma un punt per criteri: **construcció** (estats inicials correctes), **independència** (no comparteixen estat), **comportament** (el mètode canvia només el receptor), **representació** (estat imprès inequívoc) i **recuperació** (a l’error esperat el segueix codi funcional). Amb 4/5 pots continuar; si no, repeteix seccions 1–2 i 12-0. Invariants, herència/composició, dataclasses, serialització i pytest són evidència posterior o opcional.

---

## Resum
La POO et permet representar entitats amb claredat i aplicar patrons com herència, composició i propietats. Amb pràctica, sabràs quan usar classes o `dataclasses`.

## Reflexió final
Pren-te el temps de practicar. Classes ben dissenyades i proves petites fan que els projectes grans siguin molt més fàcils de mantenir.
