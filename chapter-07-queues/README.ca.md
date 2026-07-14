# Capítol 7 · Cues i piles amb `collections.deque`

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Aprendràs a usar `collections.deque` per modelar cues (FIFO), piles (LIFO) i finestres lliscants. Farem exemples inspirats en cues de tasques, buffers de logs i rate limiters lleugers, a punt per integrar-se en serveis Django o scripts.

## Ordre pedagògic
1. **Recordatori de llistes**: per què `list.pop(0)` no escala.
2. **Introducció a `deque`**: creació i operacions bàsiques.
3. **Cua FIFO**: encolar i desencolar amb `append`/`popleft`.
4. **Pila LIFO**: `append`/`pop` amb `deque` per consistència.
5. **Finestra lliscant i rate limiting**: `maxlen`, comptar dins d’un temps.
6. **Validacions i proves**: capacitat i ordre.

## Objectius d’aprenentatge
- Crear `deque` (acotades o no) i entendre l’avantatge respecte a llistes.
- Implementar cues i piles amb operacions O(1) als dos extrems.
- Fer servir `maxlen` per construir buffers rotatius.
- Muntar finestres lliscants per mètriques o límits de peticions.
- Provar el comportament per garantir ordre i invariants.

## Prerequisits i rutes
Les [llistes](../chapter-03-lists/README.ca.md) són l’únic prerequisit.

- **Ruta essencial · 45–60 min:** seccions 1–4, l’exemple directe de `maxlen` de la secció 5 i l’exercici 7-0. Resultat: seguir l’estat FIFO, LIFO i d’un buffer acotat només amb operacions de `deque`. No exigeix condicionals, funcions, classes, excepcions ni proves.
- **Ruta intermèdia · 25–35 min:** exercici 7-2 després d’aprendre [bucles](../chapter-10-loops/README.ca.md). Resultat: omplir un buffer fix i explicar quin valor es descarta.
- **Avançament professional opcional · 60–90 min:** la classe, el limitador, la secció 6 i els exercicis 7-1/7-3. Anticipa [condicionals](../chapter-08-conditionals/README.ca.md), [funcions](../chapter-11-functions/README.ca.md), [classes](../chapter-12-oop/README.ca.md), [excepcions](../chapter-14-exceptions/README.ca.md) i [proves](../chapter-18-testing/README.ca.md). Copia els exemples complets o salta’ls; no calen per al punt essencial.

## Per què importa
En backend és comú processar esdeveniments en ordre d’arribada o mantenir un historial de mida fixa. `deque` és eficient per aquests patrons i és part de la llibreria estàndard.

### Mini aventura
Pensa en la cua d’un parc d’atraccions: la primera persona que arriba és la primera que puja. Amb `deque` fas aquesta fila ràpid: entres pel final i surts pel davant sense empènyer a tothom.

## Prediu abans d'executar
Abans de les primeres operacions, dibuixa la deque després de cada `append`, `popleft` i `pop`. Prediu quin element descarta `deque(maxlen=3)` en afegir-ne un quart. La predicció del limitador pertany a l’avançament professional opcional.

---

## 1. Per què no usar només llistes?
`list.pop(0)` desplaça la resta d’elements i és O(n). En cues de tasques o logs això pot crear colls d’ampolla. `deque` està pensada per afegir i treure pels dos extrems en O(1).

---

## 2. Creació i operacions bàsiques

```python runnable
from collections import deque

queue = deque(["task-1", "task-2"])
queue.append("task-3")
print(queue)

last = queue.pop()
print(f"Últim extret: {last}")
```

- Sense arguments, `deque()` crea una estructura buida.
- Accepta `maxlen` per limitar la mida.

---

## 3. Cua FIFO (primer en entrar, primer en sortir)

```python runnable
from collections import deque

queue = deque(["ticket-a", "ticket-b"])
queue.append("ticket-c")
first = queue.popleft()
print(first)
print(list(queue))
```

`append` afegeix per l’extrem d’arribada i `popleft` retira l’element més antic. Aquest és el model FIFO essencial complet.

### Avançament opcional: embolcallar la cua en una classe

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

- `append` i `popleft` mantenen l’ordre d’arribada.
- Convertir a llista ajuda a mostrar estat en UI o logs.

---

## 4. Pila LIFO amb la mateixa estructura

```python runnable
from collections import deque

stack = deque()
stack.append("deploy")
stack.append("rollback")

last = stack.pop()
print(last)
```

- Usar `deque` per piles unifica estructures. Pots canviar comportament sense canviar de tipus.

---

## 5. Finestres lliscants, `maxlen` i rate limiting

```python runnable
from collections import deque

logs = deque(["start", "connect", "query"], maxlen=3)
logs.append("disconnect")
print(list(logs))  # ['connect', 'query', 'disconnect']
```

La quarta inserció descarta el valor més antic. Aquest buffer directe i acotat forma part de la ruta essencial.

### Avançament professional opcional: limitador basat en temps

```python runnable
from collections import deque
from time import monotonic

class RateLimiter:
    def __init__(self, max_requests, window_seconds, clock=monotonic):
        if isinstance(max_requests, bool) or not isinstance(max_requests, int) or max_requests <= 0:
            raise ValueError("max_requests ha de ser un enter positiu")
        if isinstance(window_seconds, bool) or not isinstance(window_seconds, (int, float)) or window_seconds <= 0:
            raise ValueError("window_seconds ha de ser positiu")
        if not callable(clock):
            raise TypeError("clock ha de ser invocable")
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

- S'eliminen els instants iguals o anteriors al límit; l'interval actiu és `(ara - finestra, ara]`.
- Es rebutja quan `len(self.timestamps) >= max_requests`; el rellotge monotònic injectable fa determinista la prova del límit.
- El rellotge injectat ha de ser invocable i retornar nombres no decreixents, com `monotonic()`.

### Buffers circulars amb `maxlen`
```python illustrative
logs = deque(maxlen=3)
for event in ["start", "connect", "query", "disconnect"]:
    logs.append(event)
print(list(logs))  # solo conserva los últimos 3 eventos
```

---

## 6. Validacions i proves

```python runnable
# queues.py
from collections import deque

class BoundedQueue:
    def __init__(self, maxlen):
        if maxlen <= 0:
            raise ValueError("maxlen ha de ser positiu")
        self._data = deque(maxlen=maxlen)

    def push(self, value):
        if len(self._data) == self._data.maxlen:
            raise OverflowError("Cola llena")
        self._data.append(value)

    def pop(self):
        if not self._data:
            raise IndexError("Cola vacía")
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

## Exercicis guiats (amb TODOs)
0. **7-0 · Seguiment essencial d’una cua**
   ```python todo
   from collections import deque
   tickets = deque(["A", "B"])
   # TODO 1: afegeix "C" i retira el ticket més antic amb popleft
   # TODO 2: usa una altra deque com a pila i retira l’element més nou amb pop
   # TODO 3: crea deque(["one", "two"], maxlen=2), afegeix "three" i prediu el resultat
   ```
   *Pista*: dibuixa els dos extrems després de cada operació; no calen `if`, funcions, classes ni proves.

Els exercicis restants són avançaments opcionals que fan servir capítols posteriors.

1. **7-1 · Cua d’emails**
   ```python todo
   from collections import deque
   emails = deque()
   # TODO 1: afegeix tres correus simulats
   # TODO 2: crea send_next(queue) que faci popleft i retorni el correu
   # TODO 3: si la cua és buida, retorna None
   ```
   *Pista*: reutilitza `SupportQueue` com a referència.

2. **7-2 · Buffer de logs acotat**
   ```python todo
   from collections import deque
   logs = deque(maxlen=5)
   events = ["start", "init", "load", "ready", "request", "error"]
   # TODO 1: afegeix cada esdeveniment
   # TODO 2: imprimeix només els que queden guardats
   # TODO 3: explica per què maxlen evita usar més memòria
   ```
   *Pista*: `list(logs)` et mostra el buffer final.

3. **7-3 · Finestra lliscant de mètriques**
   ```python todo
   from collections import deque
   measurements = deque(maxlen=3)
   # TODO 1: escriu add_measurement(value) que afegeixi i retorni la mitjana actual
   # TODO 2: calcula la mitjana només amb els valors dins la finestra
   # TODO 3: prova que la finestra mai supera maxlen
   ```
   *Pista*: `sum(measurements)/len(measurements)` després d’afegir.

---

## Errors comuns
- Usar llistes per cues intensives ⇒ rendiment dolent. Canvia a `deque` si fas `pop(0)` sovint.
- Oblidar buidar elements antics ⇒ les finestres temporals creixen indefinidament.
- Assumir que `maxlen` llança error ⇒ per defecte descarta elements de l'altre extrem; si vols un error, comprova `len` abans d’`append`, com a `BoundedQueue`.
- Compartir una `deque` entre fils sense protecció ⇒ usa locks o `queue.Queue` si hi ha concurrència.

---

## Explicació de solucions
### Solució essencial 7-0 i recuperació
`append` canvia l’extrem dret, `popleft` l’esquerre, `pop` el dret i `maxlen` descarta per l’extrem oposat.

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

Un `popleft` extra sobre una deque buida falla amb el senyal estable `IndexError`:

<!-- bookcheck: expect-error="IndexError" -->
```python expected-error
from collections import deque
deque().popleft()
```

Recupera’t comprovant la longitud dibuixada o impresa i executant només una extracció vàlida:

```python runnable
from collections import deque
tickets = deque(["A"])
print(tickets.popleft())
```

1. **Cua d’emails**: `send_next` fa `popleft()` i retorna `None` si és buida; així evita excepcions i és idempotent.
2. **Buffer de logs**: `logs.append(event)` manté només els últims cinc; `list(logs)` mostra el contingut final per verificar-lo.
3. **Finestra de mètriques**: després de cada inserció, calcula `average = sum(measurements) / len(measurements)`; la prova comprova que `len(measurements)` continua sent 3 després de moltes insercions.

---

## Punt de control i autoavaluació
Completa 7-0, prediu cada valor retirat o descartat, executa el cas normal, observa deliberadament l’`IndexError` documentat de la deque buida i torna a executar el cas recuperat. El limitador i la frontera temporal són un avançament professional opcional.

Suma un punt per **FIFO correcte**, **LIFO correcte**, **límit de `maxlen`**, **recuperació de l’error** i **explicació dels dos extrems**. Amb 4/5 completes la ruta essencial; si no, torna a les seccions 2–5 i redibuixa l’estat.

## Resum
`collections.deque` és una solució eficient per cues, piles i finestres lliscants. Ja saps quan preferir-la a llistes, com usar `maxlen` i com validar el comportament amb proves.

## Reflexió final
Amb cues robustes pots construir rate limiters, buffers i processadors d’esdeveniments que escalen millor. Aquestes bases són molt útils en APIs i serveis reals.
