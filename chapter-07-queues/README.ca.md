# Capítol 7 · Cues i piles amb `collections.deque`

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Aprendràs a usar `collections.deque` per modelar cues (FIFO), piles (LIFO) i finestres lliscants. Farem exemples inspirats en cues de tasques, buffers de logs i rate limiters lleugers, a punt per integrar-se en serveis Django o scripts.

## Ordre pedagògic
1. **Recordatori de llistes**: per què `list.pop(0)` no escala.
2. **Pont d’imports**: demanar a l’intèrpret seleccionat un mòdul de la biblioteca estàndard i diagnosticar de manera segura les fallades de cerca.
3. **Introducció a `deque`**: creació i operacions bàsiques.
4. **Cua FIFO**: encolar i desencolar amb `append`/`popleft`.
5. **Pila LIFO**: `append`/`pop` amb `deque` per consistència.
6. **Finestra lliscant i rate limiting**: `maxlen`, comptar dins d’un temps.
7. **Validacions i proves**: capacitat i ordre.

## Objectius d’aprenentatge
- Crear `deque` (acotades o no) i entendre l’avantatge respecte a llistes.
- Distingir mòduls de la biblioteca estàndard, locals i de tercers, i usar deliberadament `import module`, `from module import name` i `python -m module`.
- Diagnosticar un mòdul absent o ocult accidentalment sense instal·lar paquets arbitraris ni modificar Python.
- Implementar cues i piles amb operacions O(1) als dos extrems.
- Fer servir `maxlen` per construir buffers rotatius.
- Muntar finestres lliscants per mètriques o límits de peticions.
- Provar el comportament per garantir ordre i invariants.

## Prerequisits i rutes
Les [llistes](../chapter-03-lists/README.ca.md) i el cicle de fitxer/execució del capítol 1 són els únics prerequisits. El pont d’imports següent ensenya el concepte addicional immediatament abans del primer ús de `deque`.

- **Ruta essencial · 60–80 min:** secció 1, el pont d’imports complet, seccions 2–4, l’exemple directe de `maxlen` de la secció 5 i els exercicis 7-import/7-0. Resultat: executar un mòdul local que usa la biblioteca estàndard de dues maneres i seguir l’estat FIFO, LIFO i d’un buffer acotat només amb imports i operacions de `deque`. No exigeix condicionals, funcions, classes, excepcions, instal·lació de paquets ni proves.
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

## Pont d’imports: mòduls abans de `deque`

Un import demana al **mateix intèrpret de Python seleccionat** que executa el fitxer que localitzi i carregui un mòdul. Un mòdul sol ser un fitxer `.py` o un mòdul proporcionat per Python. Cal distingir tres orígens:

- la **biblioteca estàndard** acompanya la instal·lació declarada de Python; `collections` i `random` en són exemples, així que no els instal·lis amb `pip`;
- un **mòdul local** és un fitxer `.py` importable que has creat tu, com ara `queue_demo.py`;
- un **paquet de tercers** s’instal·la separadament dins d’un entorn. El [capítol 16](../chapter-16-entornos/README.ca.md) ensenya aquest flux; aquesta ruta essencial no en necessita cap.

L’estructura de paquets i les API públiques reutilitzables es tracten a fons al [capítol 15](../chapter-15-modulos/README.ca.md). Aquí només necessitem prou coneixement dels imports per usar `deque` honestament.

### Dues formes d’import, dos espais de noms

Prediu quina forma crea la cua a cada exemple complet:

```python runnable
import collections

queue = collections.deque(["A", "B"])
print(queue.popleft())
```

`import collections` vincula el nom del mòdul; per això l’accés qualificat és `collections.deque`. En canvi:

```python runnable
from collections import deque

queue = deque(["A", "B"])
print(queue.popleft())
```

`from collections import deque` vincula directament aquest nom públic. Tots dos exemples imprimeixen exactament `A`. Després de només `import collections`, `deque(...)` no està vinculat com a nom independent perquè les dues formes defineixen noms diferents.

### Executa un mòdul local amb l’intèrpret seleccionat

Desa aquest codi com a `queue_demo.py` dins d’un directori propi i d’un sol ús:

```python runnable
from collections import deque

queue = deque(["A", "B"])
print(queue.popleft())
```

Des d’aquest directori, les dues ordres del shell executen el fitxer una vegada i produeixen la mateixa línia:

```bash illustrative
python queue_demo.py
python -m queue_demo
```

La forma `-m` diu a aquest intèrpret que trobi el mòdul local importable anomenat `queue_demo` des de la ubicació d’import actual. No inclou `.py`. Aquest exemple d’un sol fitxer encara no introdueix imports relatius de paquets.

### Prediu i observa un mòdul absent

Aquest mòdul inventat del curs no existeix:

```python illustrative
import course_module_that_does_not_exist
```

El contracte executable del capítol prova aquest import en un subprocés aïllat. La categoria estable és `ModuleNotFoundError`; el missatge complet, dependent de l’entorn, no forma part del contracte. Diagnostica en aquest ordre:

1. Comprova l’ortografia.
2. Decideix si el nom hauria de pertànyer a la biblioteca estàndard, ser local o ser de tercers.
3. Si és un mòdul local, comprova el nom del fitxer i el directori de treball del shell.
4. Només per a una dependència de tercers coneguda, segueix més endavant les instruccions d’instal·lació revisades del projecte al capítol 16.

No responguis a qualsevol import absent instal·lant des d’un índex un paquet de nom semblant.

### Shadowing: quan el teu fitxer oculta el mòdul correcte

La cerca d’imports de Python pot trobar un fitxer teu abans que el mòdul de biblioteca previst. Per això, un fitxer o directori anomenat `collections.py`, `typing.py` o `random.py` dins de la carpeta de l’exercici pot fer **shadowing** del mòdul correcte. Un símptoma pot ser una ruta inesperada o un missatge que digui que el mòdul importat no té l’atribut esperat.

La recuperació és local i reversible:

1. Inspecciona la ruta del mòdul indicada en un procés de diagnòstic nou, per exemple amb `python -c "import collections; print(collections.__file__)"`.
2. Si la ruta identifica un fitxer conflictiu que has creat al directori d’exercici d’un sol ús, canvia només el nom d’aquell fitxer per un nom del domini com ara `queue_notes.py`.
3. Tanca el REPL antic si n’hi ha un d’obert, inicia un procés nou de l’intèrpret al directori previst i torna a executar `from collections import deque`.
4. Elimina només els fitxers de memòria cau creats dins del directori d’exercici si en queda cap; no esborris ni modifiquis mai un fitxer de la biblioteca estàndard.

L’exemple de cua recuperat torna a imprimir `A`. Reiniciar importa perquè un procés en execució pot retenir els mòduls que ja havia importat.

### TODO guiat d’imports, pista i solució explicada

```python todo
# queue_demo.py
# TODO 1: import the standard-library deque name from collections.
# TODO 2: create a deque containing "A" and "B".
# TODO 3: remove and print the oldest value.
# TODO 4: run this file as a path and then with `python -m queue_demo`.
```

**Pista:** la forma directa comença per `from collections import ...`; `popleft()` elimina l’element de l’extrem d’arribada. El nom del fitxer va a l’ordre per ruta, però el sufix `.py` s’omet després de `-m`.

```python runnable
from collections import deque

queue = deque(["A", "B"])
print(queue.popleft())
```

```text output
A
```

Completa el pont d’imports quan les dues formes del shell produeixin aquesta línia, observis i classifiquis la fallada esperada del mòdul inventat i puguis explicar per què canviar el nom d’un fitxer teu que fa shadowing és més segur que modificar la instal·lació de Python.

Suma un punt per l’**import directe correcte**, per l’**explicació correcta de la forma qualificada**, per les **dues formes d’execució local**, per la **recuperació d’un mòdul absent/ocult** i per **identificar `collections` com a biblioteca estàndard**. Un 5/5 completa el pont; el capítol 15 continua sent aprofundiment posterior.

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
0. **7-import · Importa i executa `queue_demo`**

   Completa el TODO guiat d’imports anterior, executa les dues formes documentades del shell i explica per què `collections` no necessita cap instal·lació separada. Mantén tots els fitxers dins d’un directori propi i d’un sol ús.

   *Pista*: després de les dues execucions correctes, usa el bloc del mòdul deliberadament inexistent per practicar el diagnòstic; no l’instal·lis.

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
- Instal·lar `collections` des d’un índex de paquets ⇒ ja forma part de la biblioteca estàndard de Python; verifica l’intèrpret seleccionat.
- Anomenar un fitxer local `collections.py` o `typing.py` ⇒ pot ocultar el mòdul previst; canvia només el nom del teu codi font i reinicia el procés.
- Escriure `python -m queue_demo.py` ⇒ el mode de mòdul usa el nom importable `queue_demo`, sense el sufix del fitxer.

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
Completa 7-import i 7-0. Executa `queue_demo.py` tant per ruta com amb `-m`, classifica el `ModuleNotFoundError` documentat, explica la recuperació del shadowing, prediu cada valor retirat o descartat, observa deliberadament l’`IndexError` de la deque buida i torna a executar el cas recuperat. El limitador i la frontera temporal són un avançament professional opcional.

Suma un punt per la **correcció d’import/execució**, el **FIFO correcte**, el **LIFO correcte**, el **límit de `maxlen`** i les **dues explicacions de recuperació**. Amb 5/5 completes la ruta essencial; si no, torna al pont d’imports o a les seccions 2–5 i repeteix només l’observació que falta.

## Resum
`collections.deque` és una solució eficient de la biblioteca estàndard per a cues, piles i finestres lliscants. Ja saps com la resol l’intèrpret seleccionat, quan preferir-la a les llistes, com usar `maxlen` i com validar-ne el comportament amb proves.

## Reflexió final
Quina pregunta de diagnòstic faries primer davant d’un import absent: ortografia, origen del mòdul, directori de treball o instal·lació? Explica per què la resposta depèn de si el mòdul és de la biblioteca estàndard, local o de tercers. Amb cues robustes pots construir rate limiters, buffers i processadors d’esdeveniments mantenint la cerca de mòduls comprensible i recuperable.
