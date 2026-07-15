# Kapitel 7 · Köer och stackar med `collections.deque`

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Det här ska vi bygga

Du använder `collections.deque` för köer (FIFO), stackar (LIFO) och glidande fönster. Exemplen liknar uppgiftsköer, loggbuffertar och små rate limiters som senare kan användas i Django-tjänster eller automationsskript.

## Lärväg

1. **Påminnelse om listor**: varför `list.pop(0)` inte skalar.
2. **Importbrygga**: be den valda tolken om en modul ur standardbiblioteket och diagnostisera sökfel säkert.
3. **Möt `deque`**: skapande och grundoperationer.
4. **FIFO-kö**: `append` och `popleft`.
5. **LIFO-stack**: `append` och `pop` på samma struktur.
6. **Glidande fönster och rate limiting**: `maxlen` och tidsintervall.
7. **Validering och tester** av kapacitet och ordning.

## Lärandemål

- Skapa begränsade eller obegränsade `deque` och förstå fördelen mot listor.
- Skilja moduler från standardbiblioteket, lokala moduler och tredjepartsmoduler samt medvetet använda `import module`, `from module import name` och `python -m module`.
- Diagnostisera en saknad eller oavsiktligt skuggad modul utan att installera godtyckliga paket eller ändra Python.
- Implementera köer och stackar med O(1)-operationer i båda ändar.
- Bygga roterande buffertar med `maxlen`.
- Skapa glidande fönster för mätvärden eller request-begränsning.
- Testa ordning och invariants.

## Förkunskaper och vägar

[Listor](../chapter-03-lists/README.sv.md) och fil-/körkretsloppet i kapitel 1 är de enda förkunskapskraven. Importbryggan nedan lär ut det extra begreppet precis innan `deque` behöver det första gången.

- **Grundväg · 60–80 min:** avsnitt 1, hela importbryggan, avsnitt 2–4, det direkta `maxlen`-exemplet i avsnitt 5 och övningarna 7-import/7-0. Resultat: kör en lokal modul som använder standardbiblioteket på två sätt och följ FIFO-, LIFO- och begränsade bufferttillstånd med bara importer och `deque`-operationer. Inga villkor, funktioner, klasser, undantagshantering, paketinstallationer eller tester krävs.
- **Mellanväg · 25–35 min:** övning 7-2 efter [loopar](../chapter-10-loops/README.sv.md). Resultat: fyll en fast buffert och förklara vilket värde som kastas bort.
- **Frivillig professionell förhandsblick · 60–90 min:** klassen, rate limitern, avsnitt 6 och övning 7-1/7-3. Den förhandsvisar [villkor](../chapter-08-conditionals/README.sv.md), [funktioner](../chapter-11-functions/README.sv.md), [klasser](../chapter-12-oop/README.sv.md), [exceptions](../chapter-14-exceptions/README.sv.md) och [testning](../chapter-18-testing/README.sv.md). Kopiera de kompletta exemplen eller hoppa över dem; de krävs inte för grundkontrollen.

## Varför det spelar roll

Backend-system behandlar ofta händelser i ankomstordning eller sparar en historik med fast storlek. `deque` är effektivare än listor för detta och finns i standardbiblioteket.

### Miniäventyr

Tänk på kön i en nöjespark: den som kommer först åker först. Med `deque` läggs personer sist och hämtas först utan att alla andra måste flyttas.

## Förutsäg före körning

Rita deque-innehållet efter varje `append`, `popleft` och `pop` före de första operationerna. Förutsäg vilket element `deque(maxlen=3)` kastar bort när ett fjärde läggs till. Rate-limiter-förutsägelsen hör till den frivilliga professionella förhandsblicken.

---

## 1. Varför inte bara listor?

`list.pop(0)` måste flytta alla återstående element och är därför O(n). I uppgiftsköer och loggar blir det en flaskhals. `deque` är byggd för O(1)-insättning och borttagning i båda ändar.

---

## Importbrygga: moduler före `deque`

En import ber **samma valda Python-tolk** som kör filen att hitta och läsa in en modul. En modul är oftast en `.py`-fil eller en modul som följer med Python. Du behöver skilja mellan tre källor:

- **standardbiblioteket** följer med den deklarerade Python-installationen; `collections` och `random` är exempel, så installera dem inte med `pip`;
- en **lokal modul** är din egen importerbara `.py`-fil, till exempel `queue_demo.py`; och
- ett **tredjepartspaket** installeras separat i en miljö. Kapitel 16 lär ut arbetsflödet; grundvägen behöver inget sådant paket.

Paketstruktur och återanvändbara offentliga API:er behandlas fullständigt i [kapitel 15](../chapter-15-modulos/README.sv.md). Här behöver vi bara tillräcklig importkunskap för att använda `deque` på ett ärligt sätt.

### Två importformer, två namnrymder

Förutsäg vilken stavning som skapar kön i vart och ett av de fullständiga exemplen:

```python runnable
import collections

queue = collections.deque(["A", "B"])
print(queue.popleft())
```

`import collections` binder modulnamnet, så åtkomsten kvalificeras som `collections.deque`. Jämför med:

```python runnable
from collections import deque

queue = deque(["A", "B"])
print(queue.popleft())
```

`from collections import deque` binder det valda offentliga namnet direkt. Båda exemplen skriver exakt `A`. En okvalificerad `deque(...)` är inte tillgänglig efter enbart `import collections`, eftersom formerna binder olika namn.

### Kör en lokal modul med den valda tolken

Spara följande som `queue_demo.py` i en egen tillfällig katalog:

```python runnable
from collections import deque

queue = deque(["A", "B"])
print(queue.popleft())
```

Från den katalogen kör vart och ett av följande skalkommandon filen en gång och ger samma rad:

```bash illustrative
python queue_demo.py
python -m queue_demo
```

Formen `-m` säger åt tolken att hitta den importerbara lokala modulen `queue_demo` från den aktuella importplatsen. Den innehåller inte `.py`. Exemplet med en enda fil introducerar ännu inte paketrelativa importer.

### Förutsäg och observera en saknad modul

Den här avsiktligt påhittade kursmodulen finns inte:

```python illustrative
import course_module_that_does_not_exist
```

Kapitlets körbara kontrakt kör importen i en isolerad underprocess. Den stabila kategorin är `ModuleNotFoundError`; hela det miljöberoende meddelandet ingår inte i kontraktet. Diagnostisera i denna ordning:

1. Kontrollera stavningen.
2. Avgör om namnet ska tillhöra standardbiblioteket, vara lokalt eller komma från tredje part.
3. För en lokal modul kontrollerar du filnamnet och skalets arbetskatalog.
4. Bara för ett känt tredjepartsberoende följer du senare projektets granskade installationsanvisningar i kapitel 16.

Försök inte lösa varje saknad import genom att installera ett paket med liknande namn från ett index.

### Skuggning: när din fil döljer den avsedda modulen

Pythons importsökning kan hitta en fil som du äger före den avsedda biblioteksmodulen. En fil eller katalog som heter `collections.py`, `typing.py` eller `random.py` i övningsmappen kan därför **skugga** modulen. Ett symptom kan vara en överraskande källsökväg eller ett meddelande om att den importerade modulen saknar det förväntade attributet.

Återhämtningen är lokal och reversibel:

1. Kontrollera den rapporterade modulsökvägen i en ny diagnostikprocess, till exempel `python -c "import collections; print(collections.__file__)"`.
2. Om sökvägen pekar på en konfliktfil som du skapade i den tillfälliga övningsmappen byter du bara namn på den filen till ett domännamn som `queue_notes.py`.
3. Avsluta den gamla REPL-miljön om den är öppen, starta en ny tolkprocess i avsedd katalog och kör `from collections import deque` igen.
4. Ta bara bort cachefiler som skapades i den tillfälliga övningsmappen om de finns kvar; radera eller redigera aldrig en fil i standardbiblioteket.

Det reparerade köexemplet skriver åter `A`. Omstarten är viktig eftersom en process som körs kan behålla moduler som redan har importerats.

### Guidad import-TODO, ledtråd och förklarad lösning

```python todo
# queue_demo.py
# TODO 1: import the standard-library deque name from collections.
# TODO 2: create a deque containing "A" and "B".
# TODO 3: remove and print the oldest value.
# TODO 4: run this file as a path and then with `python -m queue_demo`.
```

**Ledtråd:** den direkta formen börjar med `from collections import ...`; `popleft()` tar bort från ankomständen. Filnamnet hör hemma i sökvägskommandot, men suffixet `.py` utelämnas efter `-m`.

```python runnable
from collections import deque

queue = deque(["A", "B"])
print(queue.popleft())
```

```text output
A
```

Importbryggan är klar när båda skalkommandona ger denna rad, du observerar och klassificerar den påhittade modulens förväntade fel och du kan förklara varför det är säkrare att byta namn på en egen skuggfil än att ändra Python-installationen.

Ge en poäng för **rätt direktimport**, **rätt förklaring av den kvalificerade formen**, **båda lokala körformerna**, **återhämtning från saknad/skuggad modul** och **identifiering av `collections` som standardbibliotek**. 5/5 slutför bryggan; kapitel 15 behåller den senare fördjupningen.

---

## 2. Skapande och grundoperationer

```python runnable
from collections import deque

queue = deque(["task-1", "task-2"])
queue.append("task-3")
print(queue)

last = queue.pop()
print(f"Last removed: {last}")
```

- `deque()` utan argument skapar en tom struktur.
- `maxlen` begränsar den största storleken.

---

## 3. FIFO-kö (först in, först ut)

```python runnable
from collections import deque

queue = deque(["ticket-a", "ticket-b"])
queue.append("ticket-c")
first = queue.popleft()
print(first)
print(list(queue))
```

`append` lägger till vid ankomständen och `popleft` tar bort det äldsta elementet. Det är hela den grundläggande FIFO-modellen.

### Frivillig förhandsblick: lägg kön i en klass

```python runnable
from collections import deque

class SupportQueue:
    def __init__(self):
        self._queue = deque()

    def enqueue(self, ticket):
        self._queue.append(ticket)

    def handle_next(self):
        if not self._queue:
            return None
        return self._queue.popleft()  # O(1)

    def pending(self):
        return list(self._queue)
```

- `append` och `popleft` bevarar ankomstordningen.
- `list(self._queue)` gör tillståndet enkelt att visa i UI eller loggar.

---

## 4. LIFO-stack med samma struktur

```python runnable
from collections import deque

stack = deque()
stack.append("deploy")
stack.append("rollback")

last = stack.pop()
print(last)
```

En gemensam struktur gör det möjligt att byta beteende utan att byta typ.

---

## 5. Glidande fönster, `maxlen` och rate limiting

```python runnable
from collections import deque

logs = deque(["start", "connect", "query"], maxlen=3)
logs.append("disconnect")
print(list(logs))  # ['connect', 'query', 'disconnect']
```

Det fjärde tillägget kastar bort det äldsta värdet. Den direkta begränsade bufferten ingår i grundvägen.

### Frivillig professionell förhandsblick: tidsbaserad rate limiter

```python runnable
from collections import deque
from time import monotonic

class RateLimiter:
    def __init__(self, max_requests, window_seconds, clock=monotonic):
        if isinstance(max_requests, bool) or not isinstance(max_requests, int) or max_requests <= 0:
            raise ValueError("max_requests must be a positive integer")
        if isinstance(window_seconds, bool) or not isinstance(window_seconds, (int, float)) or window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        if not callable(clock):
            raise TypeError("clock must be callable")
        self.window = float(window_seconds)
        self.max_requests = max_requests
        self.timestamps = deque()
        self._clock = clock

    def allow(self):
        now = self._clock()
        cutoff = now - self.window
        while self.timestamps and self.timestamps[0] <= cutoff:
            self.timestamps.popleft()
        if len(self.timestamps) >= self.max_requests:
            return False
        self.timestamps.append(now)
        return True

ticks = iter([0.0, 1.0, 2.0, 10.0])
limiter = RateLimiter(2, 10, clock=lambda: next(ticks))
assert [limiter.allow() for _ in range(4)] == [True, True, False, True]
```

- Ta bort tidpunkter vid eller före gränsen; det aktiva intervallet är `(nu - fönster, nu]`.
- Avvisa när `len(self.timestamps) >= max_requests`; den injicerbara monotona klockan gör gränstestet deterministiskt.
- Den injicerade klockan måste vara anropsbar och ge icke-minskande tal, precis som `monotonic()`.

### Cirkulära buffertar med `maxlen`

```python illustrative
logs = deque(maxlen=3)
for event in ["start", "connect", "query", "disconnect"]:
    logs.append(event)
print(list(logs))  # only keeps the last 3 events
```

---

## 6. Validering och tester

```python runnable
# queues.py
from collections import deque

class BoundedQueue:
    def __init__(self, maxlen):
        if maxlen <= 0:
            raise ValueError("maxlen must be positive")
        self._data = deque(maxlen=maxlen)

    def push(self, value):
        if len(self._data) == self._data.maxlen:
            raise OverflowError("Queue full")
        self._data.append(value)

    def pop(self):
        if not self._data:
            raise IndexError("Queue empty")
        return self._data.popleft()
```

```python illustrative
# tests/test_queues.py
import pytest
from queues import BoundedQueue

def test_bounded_queue_keeps_order():
    queue = BoundedQueue(maxlen=2)
    queue.push("a")
    queue.push("b")
    assert queue.pop() == "a"

def test_bounded_queue_respects_maxlen():
    queue = BoundedQueue(maxlen=1)
    queue.push("a")
    with pytest.raises(OverflowError):
        queue.push("b")
```

---

## Vägledda övningar (med TODO)

0. **7-import · Importera och kör `queue_demo`**

   Slutför import-TODO:n ovan, kör båda dokumenterade skalformerna och förklara varför `collections` inte behöver installeras separat. Förvara alla filer i en egen tillfällig katalog.

   *Ledtråd*: efter de två lyckade körningarna använder du blocket med den avsiktligt saknade modulen för att öva diagnostik; installera den inte.

0. **7-0 · Grundläggande köspårning**
   ```python todo
   from collections import deque
   tickets = deque(["A", "B"])
   # TODO 1: lägg till "C" och ta bort den äldsta biljetten med popleft
   # TODO 2: använd en annan deque som stack och ta bort det nyaste med pop
   # TODO 3: skapa deque(["one", "two"], maxlen=2), lägg till "three" och förutsäg resultatet
   ```
   *Tips*: rita båda ändarna efter varje operation; inget `if`, ingen funktion, klass eller test behövs.

De återstående övningarna är frivilliga förhandsblickar som använder senare kapitel.

1. **7-1 · E-postkö**

   ```python todo
   from collections import deque
   emails = deque()
   # TODO 1: add three fake emails
   # TODO 2: write send_next(queue) that does popleft and returns the email
   # TODO 3: handle empty queue by returning None
   ```

   *Ledtråd*: använd `SupportQueue` som förebild.

2. **7-2 · Begränsad loggbuffert**

   ```python todo
   from collections import deque
   logs = deque(maxlen=5)
   events = ["start", "init", "load", "ready", "request", "error"]
   # TODO 1: append each event to the deque
   # TODO 2: print only the events that stayed in the buffer
   # TODO 3: explain why maxlen prevents using more memory
   ```

   *Ledtråd*: konvertera till lista för att visa slutbufferten.

3. **7-3 · Glidande fönster för mätvärden**

   ```python todo
   from collections import deque
   measurements = deque(maxlen=3)
   # TODO 1: write add_measurement(value) that appends and returns the current average
   # TODO 2: compute the average only with the values in the current window
   # TODO 3: add a test confirming the window never exceeds maxlen
   ```

   *Ledtråd*: beräkna `sum(measurements)/len(measurements)` efter tillägg.

---

## Vanliga misstag

- **Listor för intensiva köer** blir långsamma; byt till `deque` vid återkommande `pop(0)` eller `insert(0)`.
- **Gamla element tas inte bort**, så tidsfönstret växer utan gräns; rensa med en `while` som i `RateLimiter`.
- **Anta att `maxlen` höjer fel**: normalt kastas element i andra änden. Kontrollera `len` före `append` om full kö ska ge fel.
- **Dela samma `deque` mellan trådar utan lås**: använd lås eller en trådsäker `queue.Queue` vid concurrency.
- **Installera `collections` från ett paketindex**: det ingår redan i Pythons standardbibliotek; kontrollera i stället den valda tolken.
- **Kalla en lokal fil `collections.py` eller `typing.py`**: den kan skugga den avsedda modulen; byt bara namn på din lokala kod och starta om processen.
- **Skriva `python -m queue_demo.py`**: modulläget använder det importerbara namnet `queue_demo` utan filsuffixet.

---

## Förklarade lösningar

### Grundlösning 7-0 och återhämtning
`append` ändrar höger ände, `popleft` vänster ände, `pop` höger ände och `maxlen` kastar bort från motsatt ände.

```python runnable
from collections import deque
tickets = deque(["A", "B"])
tickets.append("C")
print(tickets.popleft())
stack = deque(["draft", "publish"])
print(stack.pop())
bounded = deque(["one", "two"], maxlen=2)
bounded.append("three")
print(list(bounded))
```

Ett extra `popleft` på en tom deque misslyckas med den stabila signalen `IndexError`:

<!-- bookcheck: expect-error="IndexError" -->
```python expected-error
from collections import deque
deque().popleft()
```

Återhämta genom att kontrollera den ritade eller utskrivna längden och bara köra en giltig borttagning:

```python runnable
from collections import deque
tickets = deque(["A"])
print(tickets.popleft())
```

1. **E-postkö**: `send_next` använder `popleft()` och returnerar `None` när kön är tom, så funktionen blir idempotent och höjer inte fel.
2. **Loggbuffert**: `logs.append(event)` för varje händelse behåller de fem senaste; `list(logs)` visar resultatet.
3. **Mätfönster**: efter varje värde beräknas `sum(measurements) / len(measurements)`; testet bekräftar att längden är 3 även efter många tillägg.

---

## Kontrollpunkt och självbedömning

Slutför 7-import och 7-0. Kör `queue_demo.py` både som sökväg och med `-m`, klassificera den dokumenterade `ModuleNotFoundError`, förklara återhämtningen från skuggning, förutsäg varje borttaget eller kasserat värde, observera medvetet `IndexError` för en tom deque och kör återhämtningsfallet. Rate limitern och dess tidsgräns hör till den frivilliga professionella förhandsblicken.

Ge en poäng för **rätt import/körning**, **korrekt FIFO**, **korrekt LIFO**, **`maxlen`-gräns** och **båda återhämtningsförklaringarna**. 5/5 slutför grundvägen; annars går du tillbaka till importbryggan eller avsnitt 2–5 och upprepar bara den observation som saknas.

## Sammanfattning

`collections.deque` ger en effektiv standardbibliotekslösning för köer, stackar och glidande fönster. Du vet nu hur den löses av den valda tolken, när den är bättre än listor, hur `maxlen` fungerar och hur beteendet testas.

## Avslutande reflektion

Vilken diagnostikfråga ställer du först vid en saknad import: stavning, modulens källa, arbetskatalog eller installation? Förklara varför svaret beror på om modulen hör till standardbiblioteket, är lokal eller kommer från tredje part. Med robusta köer kan du bygga rate limiters, buffertar och händelseprocessorer utan att tappa en begriplig och reparerbar modulupplösning.
