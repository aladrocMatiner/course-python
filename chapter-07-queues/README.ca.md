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

## Prerequisits i avançaments opcionals
Les [llistes](../chapter-03-lists/README.ca.md) són l'únic prerequisit. Els condicionals, les classes, les dependències injectades, les excepcions i pytest són avançaments; segueix ara els patrons i estudia després [condicionals](../chapter-08-conditionals/README.ca.md), [funcions](../chapter-11-functions/README.ca.md), [classes](../chapter-12-oop/README.ca.md), [excepcions](../chapter-14-exceptions/README.ca.md) i [proves](../chapter-18-testing/README.ca.md).

## Per què importa
En backend és comú processar esdeveniments en ordre d’arribada o mantenir un historial de mida fixa. `deque` és eficient per aquests patrons i és part de la llibreria estàndard.

### Mini aventura
Pensa en la cua d’un parc d’atraccions: la primera persona que arriba és la primera que puja. Amb `deque` fas aquesta fila ràpid: entres pel final i surts pel davant sense empènyer a tothom.

## Prediu abans d'executar
Abans de les primeres operacions, dibuixa la deque després de cada `append`, `popleft` i `pop`. Per al limitador, prediu `[True, True, False, True]` i explica per què caduca un instant situat exactament al límit.

---

## 1. Per què no usar només llistes?
`list.pop(0)` desplaça la resta d’elements i és O(n). En cues de tasques o logs això pot crear colls d’ampolla. `deque` està pensada per afegir i treure pels dos extrems en O(1).

---

## 2. Creació i operacions bàsiques

```python runnable
from collections import deque

cola = deque(["task-1", "task-2"])
cola.append("task-3")
print(cola)

ultimo = cola.pop()
print(f"Último extraído: {ultimo}")
```

- Sense arguments, `deque()` crea una estructura buida.
- Accepta `maxlen` per limitar la mida.

---

## 3. Cua FIFO (primer en entrar, primer en sortir)

```python runnable
from collections import deque

class ColaSoporte:
    def __init__(self):
        self._cola = deque()

    def encolar(self, ticket):
        self._cola.append(ticket)

    def atender(self):
        if not self._cola:
            return None
        return self._cola.popleft()  # O(1)

    def pendientes(self):
        return list(self._cola)
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

ultimo = stack.pop()
print(ultimo)
```

- Usar `deque` per piles unifica estructures. Pots canviar comportament sense canviar de tipus.

---

## 5. Finestres lliscants, `maxlen` i rate limiting

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
        ahora = self._clock()
        limite = ahora - self.window
        while self.timestamps and self.timestamps[0] <= limite:
            self.timestamps.popleft()
        if len(self.timestamps) >= self.max_requests:
            return False
        self.timestamps.append(ahora)
        return True

instants = iter([0.0, 1.0, 2.0, 10.0])
limiter = RateLimiter(2, 10, clock=lambda: next(instants))
assert [limiter.allow() for _ in range(4)] == [True, True, False, True]
```

- S'eliminen els instants iguals o anteriors al límit; l'interval actiu és `(ara - finestra, ara]`.
- Es rebutja quan `len(self.timestamps) >= max_requests`; el rellotge monotònic injectable fa determinista la prova del límit.
- El rellotge injectat ha de ser invocable i retornar nombres no decreixents, com `monotonic()`.

### Buffers circulars amb `maxlen`
```python illustrative
logs = deque(maxlen=3)
for evento in ["start", "connect", "query", "disconnect"]:
    logs.append(evento)
print(list(logs))  # solo conserva los últimos 3 eventos
```

---

## 6. Validacions i proves

```python runnable
# queues.py
from collections import deque

class ColaAcotada:
    def __init__(self, maxlen):
        if maxlen <= 0:
            raise ValueError("maxlen debe ser positivo")
        self._datos = deque(maxlen=maxlen)

    def push(self, valor):
        if len(self._datos) == self._datos.maxlen:
            raise OverflowError("Cola llena")
        self._datos.append(valor)

    def pop(self):
        if not self._datos:
            raise IndexError("Cola vacía")
        return self._datos.popleft()
```

```python illustrative
# tests/test_queues.py
import pytest
from queues import ColaAcotada

def test_cola_acotada_mantiene_orden():
    cola = ColaAcotada(maxlen=2)
    cola.push("a")
    cola.push("b")
    assert cola.pop() == "a"

def test_cola_acotada_no_supera_maxlen():
    cola = ColaAcotada(maxlen=1)
    cola.push("a")
    with pytest.raises(OverflowError):
        cola.push("b")
```

---

## Exercicis guiats (amb TODOs)
1. **7-1 · Cua d’emails**
   ```python todo
   from collections import deque
   emails = deque()
   # TODO 1: afegeix tres correus simulats
   # TODO 2: crea send_next(queue) que faci popleft i retorni el correu
   # TODO 3: si la cua és buida, retorna None
   ```
   *Pista*: reutilitza `ColaSoporte` com a referència.

2. **7-2 · Buffer de logs acotat**
   ```python todo
   from collections import deque
   logs = deque(maxlen=5)
   eventos = ["start", "init", "load", "ready", "request", "error"]
   # TODO 1: afegeix cada esdeveniment
   # TODO 2: imprimeix només els que queden guardats
   # TODO 3: explica per què maxlen evita usar més memòria
   ```
   *Pista*: `list(logs)` et mostra el buffer final.

3. **7-3 · Finestra lliscant de mètriques**
   ```python todo
   from collections import deque
   mediciones = deque(maxlen=3)
   # TODO 1: escriu add_measurement(valor) que afegeixi i retorni la mitjana actual
   # TODO 2: calcula la mitjana només amb els valors dins la finestra
   # TODO 3: prova que la finestra mai supera maxlen
   ```
   *Pista*: `sum(mediciones)/len(mediciones)` després d’afegir.

---

## Errors comuns
- Usar llistes per cues intensives ⇒ rendiment dolent. Canvia a `deque` si fas `pop(0)` sovint.
- Oblidar buidar elements antics ⇒ les finestres temporals creixen indefinidament.
- Assumir que `maxlen` llança error ⇒ per defecte descarta elements; si vols error, comprova `len` abans d’`append`.
- Compartir una `deque` entre fils sense protecció ⇒ usa locks o `queue.Queue` si hi ha concurrència.

---

## Explicació de solucions
1. **Cua d’emails**: `send_next` fa `popleft()` i retorna `None` si és buida.
2. **Buffer de logs**: `logs.append(evento)` manté només els últims; `list(logs)` ajuda a verificar.
3. **Finestra de mètriques**: calcula la mitjana després d’afegir; la prova comprova que `len(mediciones)` continua sent 3.

---

## Punt de control i autoavaluació
Explica FIFO davant de LIFO, per què `pop(0)` és O(n), com descarta valors `maxlen` i per què un limitador usa `monotonic()` en lloc de l'hora civil. Prova després capacitat, entrada buida i el límit temporal exacte.

- **Preparat**: conserves els invariants d'ordre i fas determinista el comportament temporal.
- **Gairebé**: les operacions funcionen, però encara necessites ajuda amb capacitat o límits.
- **Repassa**: torna a les seccions 1, 3 i 5 i traça cada estat de la deque en paper.

## Resum
`collections.deque` és una solució eficient per cues, piles i finestres lliscants. Ja saps quan preferir-la a llistes, com usar `maxlen` i com validar el comportament amb proves.

## Reflexió final
Amb cues robustes pots construir rate limiters, buffers i processadors d’esdeveniments que escalen millor. Aquestes bases són molt útils en APIs i serveis reals.
