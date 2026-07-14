# Kapitel 12 · Objektorienterad programmering: teori och praktik

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Vi skapar våra första Python-klasser, från modellen av ett objekt till backendliknande användare, order och services. Kapitlet täcker attribut, metoder, initiering, arv, komposition, `dataclasses` och goda vanor. Det är medvetet långt: OOP behöver lugn och många exempel.

## Lärväg

1. **Mental modell**: objektets syfte.
2. **Grundsyntax**: attribut, `__init__` och metoder.
3. **Representation** med `__repr__` och `__str__`.
4. **Class methods och static methods**.
5. **Arv och komposition**.
6. **Lätt inkapsling och properties**.
7. **`dataclasses`** för lättviktiga modeller.
8. **Backendmönster**.
9. **Tester och övningar**.

## Lärandemål

- Definiera klasser med tydliga attribut och metoder.
- Skapa instanser, ändra tillstånd och representera objekt begripligt.
- Använda arv och komposition utan djupa hierarkier.
- Tillämpa `@property`, class methods och static methods för specifika regler.
- Använda `dataclasses` för lättviktiga värdebehållare och medvetet konfigurera likhet, ordning eller blockerad fälttilldelning.

## Förkunskaper och valfria förhandsblickar

Repetera [dictionaries](../chapter-04-dictionaries/README.sv.md) och [funktioner](../chapter-11-functions/README.sv.md) innan du börjar. Du ska kunna definiera en funktion, skicka argument, returnera ett värde och uppdatera en dictionary utan att mutera orelaterad data.

[Exceptions](../chapter-14-exceptions/README.sv.md) och [testning med pytest](../chapter-18-testing/README.sv.md) förekommer som valfria förhandsblickar. Vid första genomgången räcker det att känna igen att `raise` avvisar ogiltigt tillstånd och att `assert` kontrollerar ett förväntat resultat.

## Varför det spelar roll

Objekt modellerar entiteter och samlar data med beteende. I Django är models, views och serializers klasser; grunderna gör dem säkrare att utöka.

### Miniäventyr

En klass är mallen för en spelkaraktär med egenskaper och färdigheter. Ett objekt är en konkret karaktär med egna värden. Programmet blir en värld av meningsfulla saker i stället för lösa tal.

## Förutsäg först

Identifiera klassen, instansen, attributen och metoden före första körningen. Förutsäg tillståndet direkt efter konstruktion och efter ett metodanrop. Förutsägelser om `Cuenta`, properties och `frozen=True` hör till de frivilliga vägarna och krävs inte för grundkontrollen.

## Lärvägar

- **Grundväg · 70–100 min över två sessioner:** studera avsnitt 1–2, övning 12-0, dess återhämtning och grundkontrollen. Resultat: definiera en klass, skapa oberoende instanser, ändra tillstånd via en metod och implementera en användbar representation. Direkta anrop och utskrivet tillstånd är beviset; exceptions och pytest krävs inte.
- **Frivillig professionell väg · ungefär två sessioner till:** studera avsnitt 3–5 och 7–9 efter [exceptions](../chapter-14-exceptions/README.sv.md) och [testning](../chapter-18-testing/README.sv.md). Resultat: validera invariants, välj komposition eller arv, serialisera en gräns och ersätt ett beroende i ett test.
- **Frivillig avancerad väg · ungefär en session:** studera avsnitt 6 och anpassad serialisering i avsnitt 8. Resultat: förklara `eq`, `order`, `frozen`, `replace` och nästlad muterbarhet med observerade exempel.

---

## 1. Mental modell: objekt har data och handlingar

Klassen är ritningen, objekten dess instanser. En `Usuario` har data som `nombre`, `email` och handlingar som att avaktivera.

```python runnable
class Usuario:
    def __init__(self, nombre, email):
        self.nombre = nombre
        self.email = email
        self.activo = True

    def desactivar(self):
        self.activo = False
```

- `self` är instansen.
- Attribut skapas normalt i `__init__`.

### Skapa instanser

```python illustrative
noor = Usuario("Noor", "noor@example.com")
print(noor.nombre)
noor.desactivar()
print(noor.activo)  # False
```

---

## 2. Representera objekt (`__repr__` och `__str__`)

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

- `repr(obj)` är avsedd för felsökning.
- `str(obj)` används av `print`.

---

## 3. Class methods och static methods

```python runnable
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

- `@classmethod` tar emot `cls` och kan läsa eller ändra klassattribut.
- `@staticmethod` tar varken `self` eller `cls`; det är en hjälpfunktion i klassens namespace.

---

## 4. Arv och komposition

### Arv

```python runnable
class Notificacion:
    def enviar(self, mensaje):
        raise NotImplementedError

class EmailNotificacion(Notificacion):
    def enviar(self, mensaje):
        print(f"Email: {mensaje}")
```

Använd arv när klasser delar ett gemensamt interface.

### Komposition

```python runnable
class ServicioMensajes:
    def __init__(self, canal):
        self.canal = canal

    def enviar(self, mensaje):
        self.canal.enviar(mensaje)
```

Komposition betyder att en klass använder en annan internt och är ofta flexiblare för att blanda beteenden.

---

## 5. Lätt inkapsling och properties

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

- `__balance` använder *name mangling* för att minska oavsiktliga direkta skrivningar; det är ingen säkerhetsgräns. Både normal konstruktion och tilldelning passerar den validerande propertyn.
- `@property` exponerar getter/setter utan ändrad anropssyntax: `cuenta.balance = 100`.

---

## 6. `dataclasses` för lättviktiga modeller

```python runnable
from dataclasses import dataclass

@dataclass
class Coordenada:
    lat: float
    lon: float
    etiqueta: str = ""
```

- Som standard genererar `@dataclass` `__init__`, `__repr__` och likhet (`eq=True`). Ordningsmetoder kräver `order=True`, och de deltagande fälten måste stödja jämförelserna.
- `frozen=True` blockerar vanlig omtilldelning av fält men ger inte djup oföränderlighet: ett muterbart värde i ett fält kan fortfarande ändras.

---

## 7. Backendmönster

- **Models** håller data och validering, som `Usuario` och `Pedido`.
- **Services** orkestrerar steg, som `ServicioMensajes`.
- **Repositories** abstraherar dataåtkomst och kan ta transformerande callbacks.

### Exempel

```python runnable
class ServicioDescuentos:
    def __init__(self, calculo_descuento):
        self.calculo_descuento = calculo_descuento

    def procesar(self, pedido):
        descuento = self.calculo_descuento(pedido)
        pedido.total -= descuento
        return pedido
```

`calculo_descuento` blandar OOP med higher-order functions från föregående kapitel.

---

## 8. Serialisera och deserialisera objekt

Serialisering gör ett objekt till dict eller JSON för lagring eller överföring. Deserialisering bygger tillbaka objektet.

### `to_dict` och `from_dict`

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
pedido = Pedido(1, 120, ["libro", "cuaderno"])
payload = pedido.to_dict()
pedido_recuperado = Pedido.from_dict(payload)
```

Mönstret gör instanser till JSON-payloads eller databasposter.

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

Hantera `json.JSONDecodeError` när data kommer utifrån.

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

`asdict` konverterar dataclasses rekursivt till serialiserbara dictionaries.

### Säker deserialisering

- Validera obligatoriska fält före konstruktion: `if "id" not in data: raise ValueError`.
- Konvertera typer uttryckligen, exempelvis `int(data["id"])`.
- Lita aldrig på externa strukturer utan kontroll.

---

## 9. Testa objekt

Använd `pytest` för beteende.

```python illustrative
# tests/test_usuario.py
from usuarios import Usuario

def test_usuario_se_desactiva():
    user = Usuario("Noor", "ana@example.com")
    user.desactivar()
    assert user.activo is False
```

Skapa `usuarios.py` och kopiera kapitlets `Usuario` för att köra testet.

- Kontrollera tillstånd före och efter.
- Injicera enkla test doubles med samma interface för beroenden.

---

## Grundövning och återhämtning

### 12-0 · Två oberoende räknare

Förutsäg båda representationerna, kör blocket och förklara varför en ändring av `first` inte ändrar `second`:

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

Nästa klass utelämnar avsiktligt `self`; metodanropet ger förväntad `TypeError`:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
class Counter:
    def increment():
        pass


counter = Counter()
counter.increment()
```

Återhämta dig genom att ta emot instansen uttryckligen och observera det ändrade tillståndet:

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

De två utskrivna tillstånden och återhämtningsutskriften är grundbeviset. Stanna före arv, properties, dataclasses, serialisering och pytest.

## Vägledda övningar (med TODO)

1. **12-1 · Klassen `Producto`**

   ```python todo
   class Producto:
       # TODO 1: define attributes nombre, precio, stock
       # TODO 2: add vender(cantidad) that subtracts stock and validates availability
       # TODO 3: implement __repr__ for debugging
   ```

   *Ledtråd*: höj `ValueError` om `cantidad > stock`.

2. **12-2 · Komposition av services**

   ```python todo
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

   *Ledtråd*: loopa över services och anropa `service.send(mensaje)`.

3. **12-3 · Oföränderlig dataclass**

   ```python todo
   from dataclasses import dataclass, replace
   @dataclass(frozen=True)
   class Config:
       env: str
       debug: bool = False
   # TODO 1: show how to create a new config changing env
   # TODO 2: explain why frozen prevents accidental modifications
   ```

---

## Vanliga misstag

- Glömma `self` först i metoder och få `TypeError`.
- Definiera attribut utanför `__init__` utan att inse att de blir klassattribut.
- Bygga djupt arv när komposition räcker.
- Inte dokumentera vad subclasses måste implementera, så `NotImplementedError` saknas.

---

## Förklarade lösningar

1. **Producto**: `vender` kontrollerar lager, minskar och returnerar nytt värde; `__repr__` hjälper logginspektion.
2. **NotificationCenter**: tar services med gemensam `send()`. Komposition låter kanaler läggas till utan multipelt arv.
3. **Fryst Config**: `dataclass(frozen=True)` blockerar vanlig fälttilldelning. Eftersom `replace` importeras ovan skapar `nueva = replace(config, env="prod")` en ändrad kopia. Det minskar oavsiktlig omtilldelning men djupfryser inte muterbara fältvärden.

---

## Kontrollpunkt och bedömningsmatris

Bygg en `Counter`-klass med startvärde, en metod som ändrar tillstånd och en läsbar `__repr__`. Skapa två instanser, ändra bara en, skriv båda och återskapa och rätta `TypeError` från saknad `self`. Använd direkta anrop; exceptions och pytest krävs inte.

Ge en poäng per kriterium: **konstruktion** (båda starttillstånd är rätt), **oberoende** (instanser delar inte tillstånd), **beteende** (metoden ändrar bara mottagaren), **representation** (utskrivet tillstånd är entydigt) och **återhämtning** (förväntat fel följs av fungerande kod). 4/5 betyder att du kan fortsätta; annars repetera avsnitt 1–2 och 12-0. Invarianter, arv/komposition, dataclasses, serialisering och pytest är senare eller valfria bevis.

---

## Sammanfattning

OOP representerar entiteter, grupperar data och beteende och ger arv, komposition och properties. Med övning väljer du klass eller `dataclass` efter behov.

## Avslutande reflektion

Välformade klasser är ett steg mot större projekt. Öva lugnt, testa och ge varje klass ett fokuserat ansvar. Senare kombineras delarna till hela applikationer.
