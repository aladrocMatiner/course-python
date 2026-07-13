# Kapitel 11 · Funktioner, ansvar och att skicka funktioner

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Vi går djupare i funktioner: definition, dokumentation, flera returvärden och funktioner som data. Du skickar funktioner som argument, lagrar dem i samlingar och bygger pipelines. Backendliknande validerare, serializers och hooks introducerar higher-order functions stegvis.

## Lärväg

1. **Repetition**: definition, argument och returvärden.
2. **Ett ansvar**: när en funktion bör delas.
3. **Standardvärden och keyword arguments**.
4. **First-class functions** i variabler och samlingar.
5. **Funktioner som argument**: callbacks, validatorer och filter.
6. **Funktioner som returnerar funktioner**, closures.
7. **Lätta decorators** som helhetsbild.
8. **Tester och goda vanor**.

## Lärandemål

- Skriva väl namngivna funktioner med kort dokumentation.
- Förstå positional, keyword och default arguments.
- Skicka funktioner och utforma utbyggbara API:er.
- Förstå closures och funktionsfabriker.
- Testa framgångs- och felvägar i higher-order functions.

## Förkunskaper och valfri förhandsblick

Du bör vara bekväm med [listor](../chapter-03-lists/README.sv.md), [dictionaries](../chapter-04-dictionaries/README.sv.md), [villkor](../chapter-08-conditionals/README.sv.md) och [loopar](../chapter-10-loops/README.sv.md). Repetera särskilt hur en samling itereras och hur ett resultat returneras när ett villkor uppfylls.

Avsnitt 7 ger en förhandsblick på [testning med pytest](../chapter-18-testing/README.sv.md). Det är valfritt vid första genomgången: läs tills vidare varje `assert` som ”det här resultatet måste motsvara det förväntade värdet”.

## Varför det spelar roll

Små tydliga funktioner minskar fel och ökar återanvändning. I backend gör validatorer och transformers som argument komponenter anpassningsbara utan kopierad kod.

### Miniäventyr

En funktion är ett recept. Ett tydligt recept kan upprepas utan att varje steg uppfinns igen och kan följas av någon annan. Bra recept sparar tid och förebygger misstag.

## Förutsäg först

Förutsäg utan att köra koden resultatet av `procesar_items(["noor", "frej"], str.upper)`. Förklara varför argumentet är `str.upper` och inte `str.upper()`. Förutsäg sedan om `[str.strip, str.upper]` ändrat till `[str.upper, str.strip]` ger ett annat pipeline-resultat för `"  hola  "`. Kontrollera varje förutsägelse och namnge värdet mellan stegen.

---

## 1. Definiera och dokumentera funktioner

```python runnable
def calcular_total(items):
    """Suma los precios en una lista de items."""
    total = 0
    for item in items:
        total += item
    return total
```

- Använd verb i namn, som `calcular_total`.
- En kort docstring beskriver beteende och förväntningar.

### Typer och flera returvärden

```python runnable
from typing import List, Tuple
def resumen_pedidos(pedidos: List[int]) -> Tuple[int, float]:
    cantidad = len(pedidos)
    total = sum(pedidos)
    promedio = total / cantidad if cantidad else 0
    return cantidad, promedio
```

---

## 2. Standardvärden och keyword arguments

```python runnable
def aplicar_descuento(total, porcentaje=0.1):
    return total * (1 - porcentaje)

print(aplicar_descuento(100))      # usa 10%
print(aplicar_descuento(100, 0.2)) # 20%
```

- Keywords gör anrop tydliga: `aplicar_descuento(total=100, porcentaje=0.15)`.
- Undvik muterbara standardvärden som listor och dictionaries.

---

## 3. Funktioner som first-class citizens

Funktioner kan lagras och skickas som andra värden.

```python runnable
def notificar_email(mensaje):
    print(f"Email: {mensaje}")

def notificar_sms(mensaje):
    print(f"SMS: {mensaje}")

canales = [notificar_email, notificar_sms]
for canal in canales:
    canal("Deploy completado")
```

- Funktionerna delar samma ”form”, alltså signatur.
- Mönstret används i hooks och event-system.

---

## 4. Skicka funktioner som argument

```python runnable
def procesar_items(items, transformacion):
    return [transformacion(item) for item in items]

procesar_items(["noor", "frej"], str.upper)  # ['NOOR', 'FREJ']
```

`transformacion` är en funktion, antingen inbyggd som `str.upper` eller egen. I riktiga projekt dokumenteras kontraktet exempelvis `Callable[[str], str]`.

### Anpassningsbara validatorer

```python runnable
from typing import Callable

def guardar_usuario(data, validador: Callable[[dict], None]):
    validador(data)
    print("Guardado", data)

def validar_email(data):
    if "@" not in data["email"]:
        raise ValueError("Invalid email")

payload = {"email": "noor@example.com"}
guardar_usuario(payload, validar_email)
```

---

## 5. Funktioner som returnerar funktioner (closures)

```python runnable
def crear_multiplicador(factor):
    def multiplicar(valor):
        return valor * factor
    return multiplicar

duplicar = crear_multiplicador(2)
print(duplicar(10))  # 20
```

`multiplicar` minns `factor` även sedan `crear_multiplicador` avslutats. Det ger konfigurerbart beteende som egna filter.

### Backendliknande exempel

```python runnable
def crear_validador_longitud(minimo):
    def validar(texto):
        if len(texto) < minimo:
            raise ValueError("Muy corto")
        return texto
    return validar

validar_usuario = crear_validador_longitud(3)
validar_usuario("api")  # OK
```

---

## 6. Lätta decorators (helhetsbild)

```python runnable
import functools

def loggear(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Ejecutando {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@loggear
def procesar():
    print("Procesando...")
```

- `@loggear` applicerar decorator-funktionen.
- `functools.wraps` bevarar ursprungligt namn och docstring.
- Decorators passar tvärgående ansvar som loggning och behörighet.

---

## 7. Testa higher-order functions

```python runnable
# pipelines.py
def aplicar_pipeline(valor, etapas):
    for etapa in etapas:
        valor = etapa(valor)
    return valor
```

```python illustrative
# tests/test_pipelines.py
from pipelines import aplicar_pipeline

def test_aplicar_pipeline():
    etapas = [str.strip, str.upper]
    resultado = aplicar_pipeline("  hola  ", etapas)
    assert resultado == "HOLA"
```

Testet visar att ordningen spelar roll och att varje steg appliceras.

---

## Vägledda övningar (med TODO)

1. **11-1 · Flexibel konverterare**

   ```python todo
   # TODO 1: create convertir(items, funcion)
   # TODO 2: pass str.upper, then a function that adds a prefix
   # TODO 3: validate it raises if funcion is not callable
   ```

   *Ledtråd*: `callable(funcion)` ger `True` eller `False`.

2. **11-2 · Kedjade validatorer**

   ```python todo
   def validar_no_vacio(texto):
       # TODO: raise ValueError if texto is empty
       pass

   def validar_minimo(texto):
       # TODO: raise ValueError if len(texto) is less than a minimum
       pass
   # TODO 1: create run_validators(texto, validadores)
   # TODO 2: stop at the first error and re-raise it
   # TODO 3: add pytest tests
   ```

3. **11-3 · Enkel decorator**

   ```python todo
   # TODO 1: write decorator measure_time(func)
   # TODO 2: print how long it took to run
   # TODO 3: use it on a loop-heavy function to demonstrate
   ```

   *Ledtråd*: mät med `time.perf_counter()`.

---

## Vanliga misstag

- Muterbara defaults som `def foo(items=[])`; använd `None` och skapa listan inuti.
- Glömma `return` i en transformerande funktion.
- Inte dokumentera callback-signaturen och få inkompatibla anrop.
- Återanvända closures utan att förstå vad de fångar.

---

## Förklarade lösningar

1. **Konverterare**: loopa och applicera funktionen efter `if not callable(funcion): raise TypeError`; både inbyggda och egna funktioner fungerar.
2. **Validatorer**: `run_validators` loopar tills en validator höjer `ValueError`, ungefär som Django serializers.
3. **Decorator**: `measure_time` omsluter funktionen, mäter före och efter och skriver tiden, användbart för loopar och pipelines.

---

## Kontrollpunkt och bedömningsmatris

Bygg `normalisera_poster(poster, transformerare)` så att varje dictionary passerar alla transformerare i ordning utan att indatalistan muteras. Avvisa en icke-anropbar transformerare med `TypeError`, och testa en tom pipeline, två ordnade steg och felvägen.

Ge en poäng per kriterium: **kontrakt** (indata, utdata och fel är tydliga), **korrekthet** (ordning och alla fall fungerar), **ansvar** (funktionen har ett fokuserat syfte), **verifiering** (tester täcker framgång och fel) och **förklaring** (du skiljer på att skicka en funktion och att anropa den). 4/5 betyder att du är redo för klasser; annars repeterar du avsnitt 3, 4 och 7.

---

## Sammanfattning

Funktioner är återanvändbara block med tydliga ansvar. Som data bygger de pipelines, anpassningsbara validatorer och decorators utan duplicering.

## Avslutande reflektion

Att definiera, kombinera och skicka funktioner ger flexibla API:er. Det är centralt i Django, där funktioner kopplas till views, middleware och signals.
