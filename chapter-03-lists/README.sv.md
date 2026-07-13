# Kapitel 3 · Introduktion till listor

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Du lär dig vad en lista är, hur varje element nås och hur listor ändras och sorteras utan vanliga misstag. Vi övar metoderna `append`, `insert`, `pop`, `remove` och `sort` och skriver små tester som säkrar funktionernas beteende.

## Lärväg

1. **Introduktion**: mental modell och varför hakparenteser (`[]`) spelar roll.
2. **Åtkomst**: index, `-1` för slutet och värden i meddelanden.
3. **Ändra, lägga till och ta bort**: rätt verktyg för varje behov.
4. **Ordna**: `sort`, `sorted`, `reverse`, `len` och kontroller.
5. **Undvika fel**: känna igen och förebygga `IndexError`.
6. **Tester och vägledda övningar** för säker listhantering.

## Lärandemål

- Definiera en lista och nå element med positiva och negativa index.
- Ändra, lägga till och ta bort element efter programmets behov.
- Ordna listor tillfälligt eller permanent och mäta längden.
- Förebygga `IndexError` med validering, `len()` och `-1`.
- I den frivilliga professionella vägen testa att listfunktioner inte skapar oönskade sidoeffekter.

## Förkunskaper och vägar

- **Förkunskap:** slutför kontrollpunkten i [kapitel 2](../chapter-02-variables/README.sv.md). Grundvägen använder variabler, strängar, tal och direkta anrop till `print`.
- **Grundväg · 55–70 min:** skapa, läsa, ändra, ta bort, sortera, mäta längd och göra övning 3-11. Resultat: underhåll en gäst- eller uppgiftslista och återhämta dig från ett ogiltigt index.
- **Mellanväg · 30–40 min:** gör övning 3-4 till 3-10 och förklara vilka operationer som ändrar originallistan.
- **Frivillig professionell förhandsblick · 40–50 min:** börja vid ”Små automatiserade tester” och fortsätt genom vägledda TODO. Den förhandsvisar [villkor](../chapter-08-conditionals/README.sv.md), [loopar](../chapter-10-loops/README.sv.md), [funktioner](../chapter-11-functions/README.sv.md), [undantag](../chapter-14-exceptions/README.sv.md) och [pytest](../chapter-18-testing/README.sv.md). Kopiera de kompletta exemplen eller hoppa direkt till ”Vanliga misstag”; de behövs inte för grundkontrollpunkten.

## Varför det spelar roll

Utan listor kan varje variabel hålla ett värde. Listor samlar kataloger, användare, order eller mätvärden i en ordnad, dynamisk behållare. Några få metoder och loopar kan sedan bearbeta hundratals eller tusentals element.

### Miniäventyr

En lista är som en ryggsäck med numrerade fickor. Du kan lägga in, ta ut, flytta och räkna saker. I kod slipper du skapa en variabel för varje liknande sak.

## Förutsäg före körning

Titta på den första listan `bicycles`. Förutsäg värdena vid index `0`, `-1` och `4` före körning. Kör först bara giltiga uppslag och använd sedan avsnittet om `IndexError` för att förklara och återhämta dig från den ogiltiga förutsägelsen.

---

## Vad är en lista?

En lista är en ordnad samling. Den skapas med `[]` och elementen skiljs med kommatecken.

```python runnable
# bicycles.py
bicycles = ["trek", "cannondale", "redline", "specialized"]
print(bicycles)
```

Utdata:

```text illustrative
['trek', 'cannondale', 'redline', 'specialized']
```

Python visar den bokstavliga representationen, men oftast vill du hämta ett element i taget.

### Nå element i en lista

Skriv positionens index inom hakparenteser:

```python illustrative
print(bicycles[0])
print(bicycles[0].title())
```

### Index börjar på 0

Första elementet har index `0`, andra `1` och fjärde `3`. Negativa index räknar bakifrån: `-1` är sist och `-2` näst sist.

### Använd enskilda listvärden

Element kan sättas in i f-strängar:

```python illustrative
message = f"My first bicycle was a {bicycles[0].title()}."
print(message)
```

Exempel med personer:

```python runnable
names = ["Noor", "Frej", "Taha"]
print(names[0])
print(f"Hello, {names[1]}!")
```

### Prova själv (3-1 till 3-3)

1. **3-1 · Namn**: skapa `names` med vänner och skriv ut varje namn.
2. **3-2 · Hälsningar**: återanvänd listan och skriv en personlig hälsning till var och en.
3. **3-3 · Egen lista**: lista favorittransporter och skapa meningar som ”I would like to own a …”.

---

## Ändra, lägga till och ta bort element

Listor är dynamiska och kan ändras medan programmet körs.

### Ändra element

```python runnable
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles)

motorcycles[0] = 'ducati'
print(motorcycles)
```

### Lägga till sist

```python illustrative
motorcycles.append('ducati')
print(motorcycles)

# Build from scratch
teams = []
teams.append('frontend')
teams.append('backend')
print(teams)
```

### Infoga element

```python illustrative
motorcycles.insert(0, 'victory')
print(motorcycles)
```

### Ta bort element

- `del lista[i]` tar bort via position och returnerar inget.
- `pop()` tar bort och returnerar sista elementet eller ett angivet index.
- `remove(valor)` tar bort första elementet som är lika med värdet.

```python runnable
motorcycles = ['honda', 'yamaha', 'suzuki', 'ducati']

last = motorcycles.pop()
print(f"Last: {last}")

first = motorcycles.pop(0)
print(f"First: {first}")

motorcycles.remove('yamaha')
print(motorcycles)
```

> Obs: `remove` tar bara bort första träffen. Senare använder vi loopar för att ta bort alla.

### Prova själv (3-4 till 3-7)

1. **3-4 · Gästlista**: skapa gäster och personliga inbjudningar.
2. **3-5 · Ändrad gästlista**: ersätt någon som inte kan komma och skriv ut igen.
3. **3-6 · Fler gäster**: använd `insert` och `append` för tre nya personer.
4. **3-7 · Mindre gästlista**: minska till två med `pop`, tacka de borttagna och radera resten med `del`.

---

## Ordna en lista

Data kommer ofta i oväntad ordning. Ibland vill du visa den sorterad utan att förstöra originalet.

### Sortera permanent med `sort()`

```python runnable
cars = ['bmw', 'audi', 'toyota', 'subaru']
cars.sort()
print(cars)  # ['audi', 'bmw', 'subaru', 'toyota']
```

`cars.sort(reverse=True)` sorterar omvänt och ändrar listan på plats.

### Sortera tillfälligt med `sorted()`

```python illustrative
print(sorted(cars))          # sorted copy
print(sorted(cars, reverse=True))
print(cars)                  # the original list did not change
```

### Vänd aktuell ordning

```python illustrative
cars.reverse()
print(cars)
```

`reverse()` vänder ordningen men ”sorterar baklänges” inte. Ett nytt anrop återställer den.

### Hitta listans längd

```python illustrative
print(len(cars))
```

Längden hjälper dig att validera index och visa antalet gäster eller poster.

### Prova själv (3-8 till 3-10)

1. **3-8 · Se världen**: öva `sorted`, `reverse`, `sort` och `len` på resmål utan att tappa originalordningen.
2. **3-9 · Middagsgäster**: skriv antalet inbjudna med `len()`.
3. **3-10 · Alla funktioner**: välj en lista och använd varje metod minst en gång.

---

## Undvika `IndexError`

Felet uppstår när ett index ligger utanför listan:

```python illustrative
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles[3])  # IndexError
```

Förebygg det så här:

- Kontrollera längden, exempelvis `if len(motorcycles) > 2:`.
- Använd `-1` för sista elementet i stället för att anta storlek.
- Iterera över en kopia om element tas bort: `for item in items[:]`.
- Validera index som kommer utifrån:

  ```python illustrative
  def get_item(items, index):
      if not 0 <= index < len(items):
          raise IndexError("index out of range")
      return items[index]
  ```

- Vid `IndexError`, skriv ut listan eller `len(items)` och kontrollera verkligt tillstånd.

### Prova själv (3-11)

Framkalla avsiktligt `IndexError` genom att ändra ett giltigt index. Läs diagnostiken och reparera indexet. Det tränar ett tryggt felsökningsflöde.

---

## Små automatiserade tester

**Frivillig förhandsblick:** följande avsnitt använder `def`, `if`, `raise`, loopar, comprehensions, importer och `pytest`. Minimiidén är att en funktion namnger återanvändbart arbete och att ett test anropar den med känd indata. Kopiera varje komplett fil eller vänta med vägen till de länkade kapitlen; installera inte `pytest` från en orelaterad källa.

```python illustrative
# lists_utils.py
def prioritize_task(tasks, new_task):
    if not isinstance(tasks, list):
        raise TypeError("tasks must be a list")
    copy = tasks[:]
    copy.insert(0, new_task)
    return copy

# tests/test_lists_utils.py
import pytest
from lists_utils import prioritize_task

def test_prioritize_task_adds_to_front():
    original = ["document", "refactor"]
    result = prioritize_task(original, "set up CI")
    assert result[0] == "set up CI"
    assert original[0] == "document"  # the copy protects the original list

def test_prioritize_task_rejects_non_lists():
    with pytest.raises(TypeError):
        prioritize_task("not-a-list", "something")
```

---

## Progressiva exempel ur praktiska perspektiv

Exemplen ökar svårigheten och visar listor i backend-liknande situationer.

### Exempel 1 · Interaktiv checklista

```python runnable
checklist = ["Create virtualenv", "Install dependencies", "Run tests"]

for step in checklist:
    print(f"- [ ] {step}")

print(f"The checklist has {len(checklist)} steps.")
last = checklist.pop()              # Get the last step
print(f"Last completed step: {last}")
checklist.append("Publish release")  # Add a new task at the end
```

- Du övar direkt åtkomst, `len()`, `pop` och `append`.
- Mönstret passar CLI-skript där stegen förändras under körning.

### Exempel 2 · Supportkö (lista som kö)

```python runnable
ticket_queue = ["BUG-101", "BUG-102", "BUG-103"]

def handle_ticket(queue):
    if not queue:
        return None
    return queue.pop(0)  # pop(0) simulates a FIFO queue

def register_ticket(queue, ticket):
    queue.append(ticket)

current_ticket = handle_ticket(ticket_queue)
print(f"Handling: {current_ticket}")
register_ticket(ticket_queue, "BUG-200")
print(f"Pending: {ticket_queue}")
```

- `pop(0)` kostar mer men visar FIFO tydligt. Senare byter vi till `collections.deque`.
- Funktionerna kan senare kopplas till en Django-vy eller webhook, även om lagring ännu saknas.

### Exempel 3 · Normalisera mätvärden (validering och tester)

```python runnable
# normalizer.py
def normalize_readings(readings, *, max_limit):
    if not isinstance(readings, list):
        raise TypeError("readings must be a list")
    if not all(isinstance(value, (int, float)) for value in readings):
        raise ValueError("all readings must be numeric")
    if not readings:
        return {"average": 0, "out_of_range": [], "top3": []}

    out_of_range = [value for value in readings if value > max_limit]
    average = sum(readings) / len(readings)
    top3 = sorted(readings, reverse=True)[:3]
    return {"average": average, "out_of_range": out_of_range, "top3": top3}
```

```python illustrative
# tests/test_normalizer.py
import pytest

from normalizer import normalize_readings

def test_normalize_readings_detects_outliers():
    data = [19.2, 20.1, 22.5, 18.0]
    result = normalize_readings(data, max_limit=20)
    assert result["out_of_range"] == [22.5]
    assert result["top3"][0] == 22.5

def test_normalize_readings_validates_types():
    with pytest.raises(ValueError):
        normalize_readings([10, "not-num"], max_limit=50)

def test_normalize_readings_empty_keeps_schema():
    result = normalize_readings([], max_limit=20)
    assert result == {"average": 0, "out_of_range": [], "top3": []}
```

- Exemplet kombinerar slicing (`[:3]`), sortering och tydlig validering före ett API.
- Testerna beskriver de intressanta fallen: avvikare och rätt felsignal.

---

## Vägledda övningar (med TODO)

1. **G3-1 · Dynamiska inbjudningar**

   ```python todo
   guests = ["Noor", "Frej", "Taha"]
   # TODO 1: print a personalized message for each guest
   # TODO 2: add two new people at the end using append
   # TODO 3: remove the second guest and print who won’t attend
   ```

   *Ledtråd*: `append`, `pop` och en `for`-loop räcker.

2. **G3-2 · Prislista**

   ```python todo
   prices = [12.5, 9.99, 3.5, 18.0]
   # TODO 1: compute the average with sum/len
   # TODO 2: create a list of prices with VAT (21%)
   # TODO 3: use slicing to show only the two highest prices
   ```

   *Ledtråd*: kombinera `sorted(prices)` och `[-2:]`.

3. **G3-3 · Sensorer och validering**

   ```python todo
   readings = [19.2, 20.1, 21.3, 18.9]
   # TODO 1: write function out_of_range(readings, limit)
   # TODO 2: add a test that confirms False when all are in range
   # TODO 3: test that it raises TypeError if readings is not a list
   ```

   *Ledtråd*: använd `any(value > limit for value in readings)` och testmönstret ovan.

---

## Vanliga misstag

- Börja räkna från 1 och få `IndexError`.
- Ändra listan under iteration utan att kopiera.
- Blanda ihop `append`, som lägger en lista som ett element, med `extend`.
- Ändra originalet med `sort()` när en sorterad kopia med `sorted()` behövdes.
- Glömma att `remove` bara tar bort första förekomsten.

---

## Förklarade lösningar till övningarna

1. **G3-1**: en `for`-loop skapar meddelanden, `append` lägger till och `pop(1)` returnerar personen som togs bort.
2. **G3-2**: medelvärdet är `sum(prices)/len(prices)`, momslistan `[price * 1.21 for price in prices]` och de två högsta `sorted(prices)[-2:]`.
3. **G3-3**: validera först med `isinstance(readings, list)` och använd sedan `any(value > limit for value in readings)`; tester täcker happy path och typfel.

---

## Kontrollpunkt och självbedömning

Skapa en lista med tre uppgifter. Förutsäg första och sista värdet, lägg till en uppgift, ta bort en annan, visa en sorterad kopia och bevisa att originalordningen är oförändrad. Begär sedan avsiktligt ett ogiltigt index, läs `IndexError` och återhämta dig genom att kontrollera `len()` före nästa försök.

Ge dig en poäng per kriterium:
- **Korrekthet:** åtkomst, tillägg, borttagning och sorterad kopia matchar dina förutsägelser.
- **Läsbarhet:** namnen visar vad listan innehåller och varje operation har ett tydligt syfte.
- **Felhantering:** du förklarar det ogiltiga indexet och återhämtar dig utan att gissa längden.
- **Verifiering:** du skriver ut original och härledd lista och identifierar vilken operation som ändrade data.
- **Förklaring:** du motiverar `pop`, `remove`, `sort` eller `sorted` i ett konkret fall.

Grundvägen är klar med 5/5. Den frivilliga vägen lägger till kontrollen att `normalize_readings([], max_limit=20)` behåller alla tre resultatnycklar, inklusive `top3`.

---

## Sammanfattning

Du har definierat listor, använt positiva och negativa index, satt värden i strängar, lagt till och tagit bort, sorterat tillfälligt eller permanent samt använt `len()` och `reverse()`. Du kan förebygga `IndexError` och testa operationerna.

## Avslutande reflektion

När du behärskar listor kan hela datamängder hanteras på några rader utan kopierad kod. Nästa kapitel introducerar dictionaries som parar ihop *nycklar* och *värden*, grunden för JSON och API:er.
