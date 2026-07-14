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

## Förkunskaper och vägar

Du bör vara bekväm med [listor](../chapter-03-lists/README.sv.md), [dictionaries](../chapter-04-dictionaries/README.sv.md), [villkor](../chapter-08-conditionals/README.sv.md) och [loopar](../chapter-10-loops/README.sv.md). Repetera särskilt hur en samling itereras och hur ett resultat returneras när ett villkor uppfylls.

- **Grundväg · 60–75 min:** grundavsnittet, övning 11-0 och den grundläggande kontrollpunkten. Resultat: definiera och anropa en funktion, använda positional/keyword/default arguments, skilja returvärde från implicit `None`, förklara lokalt scope och återhämta ett ogiltigt anrop. Inget `Callable`, closure, decorator, pytest eller tids-API krävs.
- **Mellanväg · 35–45 min:** avsnitt 1–2 efter grundkontrollen. Resultat: dokumentera ett ansvar, lägga till Python 3.11-typer, returnera flera värden och använda ett säkert valfritt standardvärde.
- **Frivillig avancerad väg · 75–110 min:** avsnitt 3–7 och övning 11-1 till 11-3. Resultat: bygg och förklara en higher-order-pipeline med callbacks, closures och en lätt decorator. Avsnitt 7 förhandsvisar [pytest-testning](../chapter-18-testing/README.sv.md); kopiera eller hoppa över det vid första genomgången.

## Varför det spelar roll

Små tydliga funktioner minskar fel och ökar återanvändning. I backend gör validatorer och transformers som argument komponenter anpassningsbara utan kopierad kod.

### Miniäventyr

En funktion är ett recept. Ett tydligt recept kan upprepas utan att varje steg uppfinns igen och kan följas av någon annan. Bra recept sparar tid och förebygger misstag.

## Förutsäg först

Förutsäg utan att köra `describir_tarea(" backup ")` och `describir_tarea(nombre="deploy", prioridad="high")` i grundexemplet. Identifiera argumenten, standardvärdet och värdet som återvänder till anroparen. Pipeline-förutsägelsen hör till den frivilliga avancerade vägen.

---

## Grundväg: anrop, returvärden, scope och säkra standardvärden
Ett funktionsanrop har ett synligt flöde: argument går in genom parametrar, kroppen körs och `return` skickar ett värde till anroparen. Om slutet nås utan `return` returnerar Python `None`.

```python runnable
def describir_tarea(nombre, prioridad="normal"):
    etiqueta = nombre.strip()
    return f"{etiqueta}: {prioridad}"

print(describir_tarea(" backup "))
print(describir_tarea(nombre="deploy", prioridad="high"))
```

Det första anropet är positional och använder standardvärdet. Det andra namnger båda argumenten. `etiqueta` är lokal och finns bara under anropet.

```python runnable
def anunciar(mensaje):
    print(mensaje)

resultado = anunciar("ready")
print(resultado is None)
```

Utskrift är en effekt, inte ett returvärde. Sista raden observerar implicit `None`.

Använd `None` som signal för en valfri lista och skapa listan inuti anropet så att ett muterbart standardvärde inte delas:

```python runnable
def registrar(mensaje, historial=None):
    if historial is None:
        historial = []
    historial.append(mensaje)
    return historial

primero = registrar("start")
segundo = registrar("stop")
print(primero, segundo)
```

Det här anropet utelämnar avsiktligt det obligatoriska argumentet; den stabila signalen är `TypeError`:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
def saludar(nombre):
    return f"Hola, {nombre}"

saludar()
```

Återhämta genom att matcha anropet mot signaturen och kör igen:

```python runnable
def saludar(nombre):
    return f"Hola, {nombre}"

print(saludar("Noor"))
```

Verifiera grunderna med direkta anrop och utskrivna värden. Automatiserade tester kommer i Kapitel 18 och är inget dolt förkunskapskrav här.

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
def resumen_pedidos(pedidos: list[int]) -> tuple[int, float]:
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

0. **11-0 · Grundläggande etikettfunktion**
   ```python todo
   def crear_etiqueta(nombre, prefijo="user"):
       # TODO 1: ta bort omgivande blanksteg från nombre i en lokal variabel
       # TODO 2: returnera "prefijo:nombre_limpio"
       pass

   # TODO 3: anropa en gång positionellt och en gång med namngivna argument
   # TODO 4: skriv ut båda returvärdena och prova gränsen tom sträng
   ```
   *Tips*: grundresultatet syns med `print`; inga callbacks, closures, decorators, pytest eller timers behövs.

Övning 11-1 till 11-3 hör till den frivilliga avancerade vägen.

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

### Grundlösning 11-0
Det lokala `nombre_limpio` tillhör ett anrop, standardvärdet används bara när `prefijo` utelämnas och anroparen får strängen efter `return`.

```python runnable
def crear_etiqueta(nombre, prefijo="user"):
    nombre_limpio = nombre.strip()
    return f"{prefijo}:{nombre_limpio}"

print(crear_etiqueta(" Noor "))
print(crear_etiqueta(nombre="Frej", prefijo="admin"))
print(crear_etiqueta(""))
```

Den tomma strängen är ett gränsfall, inte ett dolt fel. Ett program som måste avvisa den kan lägga till policyn senare; här kommer anrop och retur först. Det ogiltiga anropets `TypeError` och återhämtning körs i grundavsnittet.

1. **Konverterare**: loopa och applicera funktionen efter `if not callable(funcion): raise TypeError`; både inbyggda och egna funktioner fungerar.
2. **Validatorer**: `run_validators` loopar tills en validator höjer `ValueError`, ungefär som Django serializers.
3. **Decorator**: `measure_time` omsluter funktionen, mäter före och efter och skriver tiden, användbart för loopar och pipelines.

---

## Kontrollpunkt och bedömningsmatris

Bygg `crear_etiqueta(nombre, prefijo="user")`, anropa den positionellt och med namn och verifiera normalt namn, tomt namn och saknat argument. Lägg separat till `mostrar(mensaje)` utan `return` och förklara varför anroparen observerar `None`. Använd inga callbacks, closures, decorators, pytest eller timers.

Ge en poäng för **signatur och anrop**, **korrekta returvärden**, **säkert standardvärde**, **dokumenterad `TypeError`-återhämtning** och **förklaring av lokalt scope kontra implicit `None`**. 4/5 slutför grundvägen och förbereder Kapitel 12:s grundväg. Den tidigare pipeline-kontrollen finns kvar som frivillig avancerad utmaning.

---

## Sammanfattning

Funktioner är återanvändbara block med tydliga ansvar. Som data bygger de pipelines, anpassningsbara validatorer och decorators utan duplicering.

## Avslutande reflektion

Att definiera, kombinera och skicka funktioner ger flexibla API:er. Det är centralt i Django, där funktioner kopplas till views, middleware och signals.
