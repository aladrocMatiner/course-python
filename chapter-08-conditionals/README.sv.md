# Kapitel 8 · Villkor, ternära uttryck och logiskt tänkande

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Vi lär oss fatta beslut med `if/elif/else`, logiska operatorer, ternära uttryck och vanliga backend-valideringar. Du väljer väg utifrån API-data, komprimerar enkla värdeval till en rad och översätter verkliga regler till kod.

## Lärväg

1. **Mental kontext**: beslut binder samman data och handling.
2. **Grundläggande `if`**: syntax, indrag och booleska villkor.
3. **`elif`/`else`**: välj exakt en väg.
4. **`and`, `or`, `not`**: kombinera regler som i satslogik.
5. **Ternära uttryck**: korta beslut där bara ett värde ändras.
6. **Validering och tester** före resultat exponeras.

## Lärandemål

- Skriva tydliga `if/elif/else` som motsvarar verksamhetsregler.
- Kombinera jämförelser med `and`, `or` och `not` och förstå logiken.
- Använda läsbara ternära uttryck för enkla villkor.
- Förstå truthy och falsy värden.
- Skapa valideringsfunktioner och testa framgångs- och felvägar.

## Förkunskaper och frivilliga förhandsblickar

Du bör kunna [variabler och booleska värden](../chapter-02-variables/README.sv.md) samt grundläggande [samlingar](../chapter-03-lists/README.sv.md). Funktioner och pytest är frivilliga förhandsblickar: följ mönstren nu och studera sedan [kapitel 11](../chapter-11-functions/README.sv.md) och [kapitel 18](../chapter-18-testing/README.sv.md).

## Varför det spelar roll

API:er, formulär och automationsskript måste tillåta eller neka åtkomst, räkna priser och välja meddelanden. Villkor är grunden för backend-logik. Tydliga villkor förebygger tysta fel och uttrycker regler utan tvetydighet.

### Miniäventyr

Det är ”välj ditt eget äventyr” i kod: dörr A ger en händelse och dörr B en annan. Med `if/else` bygger du interaktiva berättelser.

## Förutsäg före körning

Förutsäg vilken gren som körs för `amount = 120` före det första exemplet och ändra bara gränsvärdet på papper. Skriv det exakta villkor som gör varje gren nåbar innan du kör.

---

## 1. Mental modell: översätt regler till kod

Ett villkor är en vägdelning: ”om A händer, gör B, annars C”. Regeln uttrycks som ett booleskt villkor.

```python runnable
# payment.py
amount = 120

if amount > 100:
    print("Apply 10% discount")
else:
    print("No discount")
```

- Villkoret utvärderas till `True` eller `False`.
- Använd indrag på fyra mellanslag enligt PEP 8.

---

## 2. Kedjad if/elif/else

```python runnable
# shipping.py
weight = 3.2

if weight <= 1:
    rate = 5
elif weight <= 5:
    rate = 10
else:
    rate = 20

print(f"Rate: ${rate}")
```

- `elif` betyder att tidigare villkor var falska men detta är sant.
- Bara ett block körs.

### Truthy och falsy

```python runnable
user = ""  # empty string counts as False
if user:
    print("User present")
else:
    print("Missing user")
```

`0`, `""`, `[]`, `{}` och `None` är falsy; övriga värden är truthy. Det passar snabba formulärkontroller.

---

## 3. Logiska operatorer (`and`, `or`, `not`)

```python runnable
age = 20
country = "ES"

if age >= 18 and country == "ES":
    print("Can sign the contract")

if age < 18 or country != "ES":
    print("We need additional authorization")

if not country:
    print("You must provide a country")
```

- `and` kräver att båda villkoren är sanna.
- `or` är sant om minst ett villkor är sant.
- `not` vänder resultatet.

### Short-circuiting

Python slutar när resultatet redan är känt. `condicion and expensive_call()` anropar bara `expensive_call` om `condicion` är `True`. Kontrollera på så sätt förvillkor före dyrt arbete.

---

## 4. Ternärt uttryck: korta beslut

Använd ett ternärt uttryck när resultatet är ett enkelt värde.

```python runnable
# ternary.py
score = 75
status = "passed" if score >= 60 else "needs review"
print(status)
```

- Syntax: `value_if_true if condition else value_if_false`.
- Det passar korta tilldelningar och returer, inte lång logik.

### Exempel i endpoints

```python runnable
from time import time

def status_response(success: bool) -> dict:
    return {
        "status": "ok" if success else "error",
        "timestamp": time()
    }
```

---

## 5. Tänk som i satslogik

Regler kan beskrivas med sanningstabeller:

- `A and B` är sant bara när båda är sanna.
- `A or B` är falskt bara när båda är falska.
- `not A` vänder A.

### Förenkla uttryck

```python illustrative
# Before
if (not user_active) or (user_active and user_banned):
    block = True
else:
    block = False

# After (using logic)
block = (not user_active) or user_banned
```

De Morgans lagar minskar nästlade villkor:

- `not (A and B)` motsvarar `not A or not B`.
- `not (A or B)` motsvarar `not A and not B`.

Det förbättrar läsbarheten och minskar fel.

### Not: `match` / `case` (Python 3.10+)

Python 3.10 införde *structural pattern matching*, ett modernt alternativ till klassisk `switch/case`.

```python runnable
def order_status(order):
    match order:
        case {"status": "pending", "total": total} if total > 100:
            return "manual review due to high total"
        case {"status": "pending"}:
            return "queued"
        case {"status": "shipped"}:
            return "shipped"
        case _:
            return "unknown"
```

- `match` kan jämföra strukturer som dicts, tuples och objekt och använda guards som `if total > 100`.
- Det finns i Python 3.10 och senare; äldre versioner använder `if/elif/else`.

---

## 6. Validering och tester

```python runnable
# discounts.py
def calculate_discount(total, vip_customer):
    if total < 0:
        raise ValueError("total cannot be negative")
    if total >= 100 or vip_customer:
        return total * 0.1
    return 0
```

```python illustrative
# tests/test_discounts.py
import pytest
from discounts import calculate_discount

def test_discount_for_high_total():
    assert calculate_discount(150, vip_customer=False) == 15

def test_discount_for_vip_customer():
    assert calculate_discount(50, vip_customer=True) == 5

def test_no_discount():
    assert calculate_discount(50, vip_customer=False) == 0

def test_negative_total():
    with pytest.raises(ValueError):
        calculate_discount(-10, vip_customer=False)
```

Här finns tre happy paths och ett felfall. Testerna tvingar fram tydliga gränsvillkor.

---

## Vägledda övningar (med TODO)

1. **8-1 · Temperaturklassificering**

   ```python todo
   temperature = 27
   # TODO 1: print "Cold" if temp < 15, "Warm" if 15-25, "Hot" if >25
   # TODO 2: use a ternary to set a "hydrate" message when temperature > 30
   ```

   *Ledtråd*: kombinera `if/elif/else` med ett ternärt uttryck i en separat variabel.

2. **8-2 · Åtkomstkontroll**

   ```python todo
   user = {"active": True, "role": "editor"}
   # TODO 1: allow access if user is active AND role is admin OR editor
   # TODO 2: print "Needs review" if the role is not recognized
   # TODO 3: add a test confirming inactive users are blocked
   ```

   *Ledtråd*: använd `if user["active"] and user["role"] in {"admin", "editor"}`.

3. **8-3 · Logisk validering med De Morgan**

   ```python todo
   payload = {"email": "noor@example.com", "terms": True}
   # TODO 1: write a function is_valid(payload)
   # TODO 2: it must return False if email is missing OR terms is False
   # TODO 3: simplify the expression using `not` and sets
   ```

   *Ledtråd*: den direkta formen är `if not payload.get("email") or not payload.get("terms"):`.

---

## Vanliga misstag

- **Glömt indrag** ger `IndentationError`; använd fyra mellanslag per block.
- **Blanda `=` och `==`**: `=` tilldelar och `==` jämför.
- **Långa villkor utan parenteser** gör operatorprioritet oklar; gruppera blandad `and/or`.
- **Överanvända ternära uttryck**: byt till vanlig `if/else` när raden blir svårläst.

---

## Förklarade lösningar

1. **Temperatur**: `if temperature < 15: ... elif temperature <= 25: ... else: ...`, följt av `message = "hydrate" if temperature > 30 else ""`, visar båda stilarna.
2. **Åtkomst**: `if user["active"] and user["role"] in {...}` tillåter; ett `else` hanterar inaktiv och ett extra `elif` okänd roll. Testet bygger en inaktiv payload och förväntar blockering.
3. **Validering**: `return bool(payload.get("email")) and payload.get("terms")` är kompakt. För felmeddelandet används motsatsen: `if not payload.get("email") or not payload.get("terms"):`.

---

## Kontrollpunkt och självbedömning

Förklara truthy och falsy värden, short-circuiting, De Morgans transformation och när ett ternärt uttryck är tydligare än `if/else`. Testa sedan varje nåbar gren i en valideringsfunktion, inklusive exakt gräns.

- **Redo**: varje verksamhetsregel motsvarar en explicit gren och varje gren har ett motiverat test.
- **Nästan**: happy path fungerar men en gräns eller felväg är osäker.
- **Repetera**: gå tillbaka till avsnitt 1, 3 och 5 och bygg en liten sanningstabell.

## Sammanfattning

Du uttrycker regler med `if/elif/else`, kedjar villkor med logiska operatorer, använder ternära uttryck för enkla val och förenklar med satslogik. Reglerna är dessutom testade.

## Avslutande reflektion

Varje beslut i en applikation passerar ett villkor. Nu kan du skriva dem tydligt, minska komplexitet med formell logik och använda ternära uttryck när de förbättrar läsbarheten. Nästa kapitel använder loopar för att upprepa handlingar utifrån samma villkor.
