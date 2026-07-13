# Kapitel 7 · Köer och stackar med `collections.deque`

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Du använder `collections.deque` för köer (FIFO), stackar (LIFO) och glidande fönster. Exemplen liknar uppgiftsköer, loggbuffertar och små rate limiters som senare kan användas i Django-tjänster eller automationsskript.

## Lärväg

1. **Påminnelse om listor**: varför `list.pop(0)` inte skalar.
2. **Möt `deque`**: skapande och grundoperationer.
3. **FIFO-kö**: `append` och `popleft`.
4. **LIFO-stack**: `append` och `pop` på samma struktur.
5. **Glidande fönster och rate limiting**: `maxlen` och tidsintervall.
6. **Validering och tester** av kapacitet och ordning.

## Lärandemål

- Skapa begränsade eller obegränsade `deque` och förstå fördelen mot listor.
- Implementera köer och stackar med O(1)-operationer i båda ändar.
- Bygga roterande buffertar med `maxlen`.
- Skapa glidande fönster för mätvärden eller request-begränsning.
- Testa ordning och invariants.

## Förkunskaper och frivilliga förhandsblickar

[Listor](../chapter-03-lists/README.sv.md) är det enda förkunskapskravet. Villkor, klasser, injicerade beroenden, exceptions och pytest är förhandsblickar; följ mönstren nu och studera sedan [villkor](../chapter-08-conditionals/README.sv.md), [funktioner](../chapter-11-functions/README.sv.md), [klasser](../chapter-12-oop/README.sv.md), [exceptions](../chapter-14-exceptions/README.sv.md) och [testning](../chapter-18-testing/README.sv.md).

## Varför det spelar roll

Backend-system behandlar ofta händelser i ankomstordning eller sparar en historik med fast storlek. `deque` är effektivare än listor för detta och finns i standardbiblioteket.

### Miniäventyr

Tänk på kön i en nöjespark: den som kommer först åker först. Med `deque` läggs personer sist och hämtas först utan att alla andra måste flyttas.

## Förutsäg före körning

Rita deque-innehållet efter varje `append`, `popleft` och `pop` före de första operationerna. För rate limitern: förutsäg `[True, True, False, True]` och förklara varför en tidpunkt exakt vid gränsen löper ut.

---

## 1. Varför inte bara listor?

`list.pop(0)` måste flytta alla återstående element och är därför O(n). I uppgiftsköer och loggar blir det en flaskhals. `deque` är byggd för O(1)-insättning och borttagning i båda ändar.

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

---

## Förklarade lösningar

1. **E-postkö**: `send_next` använder `popleft()` och returnerar `None` när kön är tom, så funktionen blir idempotent och höjer inte fel.
2. **Loggbuffert**: `logs.append(event)` för varje händelse behåller de fem senaste; `list(logs)` visar resultatet.
3. **Mätfönster**: efter varje värde beräknas `sum(measurements) / len(measurements)`; testet bekräftar att längden är 3 även efter många tillägg.

---

## Kontrollpunkt och självbedömning

Förklara FIFO mot LIFO, varför `pop(0)` är O(n), hur `maxlen` kastar värden och varför en rate limiter använder `monotonic()` i stället för väggklockan. Testa sedan kapacitet, tom indata och exakt tidsgräns.

- **Redo**: du bevarar ordningsinvariants och gör tidsberoende beteende deterministiskt.
- **Nästan**: operationerna fungerar men kapacitets- eller gränstest kräver stöd.
- **Repetera**: gå tillbaka till avsnitt 1, 3 och 5 och rita varje deque-tillstånd.

## Sammanfattning

`collections.deque` ger effektiva köer, stackar och glidande fönster. Du vet när den är bättre än listor, hur `maxlen` fungerar och hur beteendet testas.

## Avslutande reflektion

Robusta köer ger rate limiters, buffertar och händelseprocessorer som skalar bättre. Du har nu grunden för API:er, workers och observability-verktyg och en stark introduktion till Pythons kärnstrukturer.
