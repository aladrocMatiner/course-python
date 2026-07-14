# Capítol 21 · Concurrència amable: introducció a `asyncio`

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Explorarem per què existeix la concurrència, quina diferència hi ha entre threads i async i com es creen tasques asíncrones petites amb `asyncio`. Simularem crides lentes a una API i veurem com `await` permet que el programa continuï avançant sense quedar bloquejat.

## Itinerari d'aprenentatge
1. **Motivació: tasques que esperen entrada/sortida**.
2. **Fonaments d'`async` i `await`**.
3. **Concurrència amb propietari mitjançant `TaskGroup`**, i després `gather` per a resultats ordenats.
4. **Timeouts, fallades, cancel·lació i neteja**.
5. **Nivell extra opcional: HTTP asíncron amb llibreries externes**.

## Objectius d'aprenentatge
- Entendre la diferència entre treball de CPU i treball d'entrada/sortida.
- Escriure funcions `async def` i utilitzar `await`.
- Distingir les tasques cooperatives d'asyncio dels threads del sistema operatiu.
- Posseir el treball concurrent amb `TaskGroup` i acotar-lo amb `asyncio.timeout` a Python 3.11+.
- Gestionar fallades i cancel·lacions sense empassar-se senyals de neteja ni deixar treball en segon pla.

## Per què és important
Els serveis moderns sovint esperen respostes externes, com APIs o bases de dades. La programació asíncrona permet aprofitar aquest temps d'espera per fer altres coses.

### Miniaventura
Imagina que treballes en una cafeteria. Mentre esperes la màquina de cafè, pots servir aigua o prendre una altra comanda. Això és el que fa `asyncio`: mentre una tasca «es cuina», pots atendre'n una altra en lloc de mirar la màquina.

### Una frase important
Si al principi et resulta estrany, és normal. La idea clau d'avui és aquesta: **quan una tasca està esperant**, el programa pot continuar progressant en una altra banda.

### Les tasques no són threads
Una tasca d'asyncio és planificada cooperativament per un event loop, normalment en un sol thread del sistema operatiu. Només cedeix el torn quan arriba a un `await` que es pot suspendre. El sistema operatiu planifica un thread, que pot executar codi bloquejant independentment i té altres riscos de sincronització. Per tant, posar `requests.get()` o treball intensiu de CPU directament dins `async def` continua bloquejant el thread de l'event loop; usa una biblioteca asíncrona, divideix el treball de CPU adequadament o aïlla deliberadament una crida bloquejant amb `asyncio.to_thread` quan la compensació estigui justificada.

## Prerequisits
- Funcions, excepcions, bucles i una distinció clara entre el treball de CPU i l'espera d'E/S.
- CPython 3.11+; tots els exemples obligatoris són locals i només usen la biblioteca estàndard.

## Prediu abans d'executar
Abans d'esperar la primera corrutina amb `await`, prediu quan comença el cos i quina sentència pot deixar que s'executi una altra tasca. Després d'executar l'exemple acotat, compara l'ordre observat amb la predicció sense usar una espera fixa com a prova de la planificació.

---

## 1. Una funció asíncrona

```python illustrative
import asyncio

async def saludar(nombre):
    await asyncio.sleep(1)
    return f"Hola {nombre}"

async def main():
    mensaje = await saludar("Noor")
    print(mensaje)

asyncio.run(main())
```

- `asyncio.sleep` simula treball d'entrada/sortida.
- `await` significa «espera aquí, però deixa que altres tasques s'executin si poden».

---

## 2. Posseir tasques concurrents amb `TaskGroup`

```python runnable
import asyncio

async def procesar(usuario):
    await asyncio.sleep(0)
    return f"Listo {usuario}"

async def main():
    usuarios = ["Noor", "Frej", "Taha"]
    async with asyncio.TaskGroup() as group:
        tareas = [group.create_task(procesar(u)) for u in usuarios]
    print([tarea.result() for tarea in tareas])

asyncio.run(main())
```

- El context posseeix totes les tasques creades i no acaba fins que totes han finalitzat.
- Si una filla falla, `TaskGroup` cancel·la les germanes pendents, espera la seva neteja i llança un `ExceptionGroup`. Captura una fallada fulla esperada amb `except*` fora del grup; no descartis fallades inesperades.

---

## 3. `asyncio.gather`

```python runnable
import asyncio

async def procesar(usuario):
    await asyncio.sleep(0)
    return f"Listo {usuario}"

async def main():
    resultados = await asyncio.gather(
        procesar("Noor"),
        procesar("Frej"),
    )
    print(resultados)

asyncio.run(main())
```

- `gather` retorna una llista de resultats en l'ordre d'entrada. Continua sent útil quan aquest contracte és l'objectiu, però `TaskGroup` fa explícits la vida de les tasques i la neteja de germanes per al treball concurrent obligatori.

---

## 4. Errors dins les tasques

```python runnable
import asyncio

async def puede_fallar():
    raise ValueError("Oops")

async def main():
    try:
        await puede_fallar()
    except ValueError as exc:
        print("Capturado", exc)

asyncio.run(main())
```

- Gestiona les excepcions com a les funcions normals, però amb `await`.

### Acotar un grup amb `asyncio.timeout`
```python runnable
import asyncio

async def slow(name, events):
    events.append(f"{name}:start")
    try:
        await asyncio.sleep(10)
    finally:
        events.append(f"{name}:cleanup")

async def main():
    events = []
    try:
        async with asyncio.timeout(0.02):
            async with asyncio.TaskGroup() as group:
                group.create_task(slow("a", events))
                group.create_task(slow("b", events))
    except TimeoutError:
        events.append("timeout:handled")
    print(sorted(events))

asyncio.run(main())
```

El timeout cancel·la l'operació actual; el grup propaga la cancel·lació a les filles i espera tots dos blocs `finally`. Captura `TimeoutError` fora del context de timeout. La fallada d'una filla segueix la mateixa regla de propietat: es cancel·len i netegen les germanes abans que el grup comuniqui la fallada.

### Cancel·lació i neteja
```python runnable
import asyncio

async def trabajo_largo():
    try:
        await asyncio.sleep(10)
    finally:
        print("Limpieza completada")

async def main():
    tarea = asyncio.create_task(trabajo_largo())
    await asyncio.sleep(0)
    tarea.cancel()
    try:
        await tarea
    except asyncio.CancelledError:
        print("Tarea cancelada")

asyncio.run(main())
```

- La cancel·lació és una ruta de control recuperable: usa `finally` per alliberar recursos, espera la tasca cancel·lada i gestiona `CancelledError` al límit coordinador. Dins la treballadora cancel·lada no capturis `CancelledError` per continuar com si no hagués passat res; deixa que es propagui després de la neteja.

El [mòdul i les proves de concurrència estructurada](structured_async.py) cobreixen èxit, fallada d'una filla, timeout, cancel·lació de germanes, neteja i absència de tasques sobrants. Des de `chapter-21-async/`, executa `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

---

## Exercicis guiats (amb TODO)
1. **21-1 · Temporitzador concurrent**
   ```python todo
   # TODO 1: launch 3 owned tasks in a TaskGroup and observe completion vs result order
   ```
   *Pista*: conserva els objectes task creats pel grup i llegeix `.result()` només després que acabi el context.

2. **21-2 · Simulador d'API sense Internet**
   ```python todo
   # TODO 1: create async def fake_get(url): await asyncio.sleep(1); return {"url": url, "ok": True}
   # TODO 2: use asyncio.gather to request 3 "urls" concurrently
   # TODO 3: print the result list
   ```
   *Pista*: passa les corrutines directament a `asyncio.gather` i executa un únic `main()` de nivell superior.

3. **21-3 · Gestionar cancel·lacions**
   ```python todo
   # TODO 1: bound a TaskGroup with asyncio.timeout
   # TODO 2: give each worker a finally cleanup marker
   # TODO 3: verify no child remains after TimeoutError
   ```
   *Pista*: captura `TimeoutError` fora del context de timeout i posa la neteja de recursos al bloc `finally` de cada tasca.

---

## Errors habituals
- Oblidar `await` i obtenir objectes `coroutine` en lloc del resultat.
- Cridar `asyncio.run` dins una funció que ja és asíncrona; no està permès.
- Barrejar crides bloquejants com `requests` dins funcions async i perdre'n el benefici.
- Crear tasques sense propietari i retornar mentre encara s'executen.
- Empassar-se `CancelledError` dins una tasca, cosa que pot trencar la neteja de `TaskGroup` i timeout.

---

## Solucions explicades
1. **Temporitzador**: crea tots els temporitzadors dins un `TaskGroup`; quan surt del context totes les tasques han acabat i pots llegir `.result()` amb seguretat. Registra l'ordre de finalització per separat si això és el que vols observar.
2. **Simulador d'API**: `fake_get` retorna un diccionari després d'esperar; `asyncio.gather` reuneix tots els resultats en una llista.
3. **Cancel·lació**: `asyncio.timeout` cancel·la l'operació posseïda; cada tasca neteja a `finally`, el grup espera totes les germanes i el coordinador captura `TimeoutError` després del context. Confirma que `asyncio.all_tasks()` no conté cap tasca pendent llevat de la tasca de prova actual.

---

## Resum
Amb `asyncio` pots coordinar tasques que esperen entrada/sortida sense bloquejar tot el programa, i et prepares per a frameworks asíncrons com FastAPI.

## Punt de control i rúbrica
- **Correcció**: un event loop posseeix les tasques concurrents i només conserva l'ordre dels resultats on es promet.
- **Llegibilitat**: les responsabilitats de les corrutines, les tasques i el coordinador són diferents.
- **Errors**: la fallada d'una tasca i el timeout cancel·len germanes, es propaguen correctament i netegen recursos.
- **Verificació**: executa cada bloc runnable i demostra que èxit, fallada i timeout no deixen tasques en segon pla.
- **Explicació**: explica tasques enfront de threads, quan ajuda async i per què les crides bloquejants eliminen l'avantatge.

## Reflexió final
Utilitza aquesta introducció per reconèixer quan async és útil. No tot ho necessita, però quan s'aplica bé pot fer que els serveis siguin molt més eficients.
