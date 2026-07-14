# Kapitel 21 · Vänlig concurrency: introduktion till `asyncio`

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Vi utforskar varför concurrency finns, skillnaden mot trådar och små async tasks med `asyncio`. Långsamma API-anrop simuleras så att `await` kan låta programmet göra framsteg utan blockering.

## Lärväg

1. **Motivation**: tasks som väntar på I/O.
2. **`async` och `await`**.
3. **Ägd samtidighet med `TaskGroup`**, därefter `gather` för ordnade resultat.
4. **Timeout, fel, cancellation och städning**.
5. **Frivillig bonus**: async HTTP med externa bibliotek.

## Lärandemål

- Skilja CPU-arbete från I/O-väntan.
- Skriva `async def` och använda `await`.
- Skilja kooperativa asyncio-tasks från operativsystemtrådar.
- Äga samtidigt arbete med `TaskGroup` och begränsa det med `asyncio.timeout` i Python 3.11+.
- Hantera taskfel och cancellation utan att svälja städsignaler eller lämna bakgrundsarbete.

## Varför det spelar roll

Moderna tjänster väntar ofta på API:er och databaser. Async använder väntetiden till annat arbete.

### Miniäventyr

I ett kafé kan du ta en ny beställning medan kaffemaskinen arbetar. `asyncio` låter en annan task gå vidare när en väntar.

### En viktig mening

Det är normalt att detta känns ovant. Kärnan är: **när en task väntar kan programmet göra framsteg på annat håll**.

### Tasks är inte trådar

En asyncio-task schemaläggs kooperativt av en event loop, vanligen i en enda operativsystemtråd. Den lämnar över kontroll först vid en `await` som kan suspendera. En tråd schemaläggs av operativsystemet och kan köra blockerande kod självständigt, med andra synkroniseringsrisker. Därför blockerar `requests.get()` eller CPU-tungt arbete direkt i `async def` fortfarande event-loop-tråden; använd ett async-bibliotek, dela CPU-arbetet lämpligt eller isolera avsiktligt ett blockerande anrop med `asyncio.to_thread` när avvägningen är motiverad.

## Förkunskaper
- Funktioner, undantag, loopar och en tydlig skillnad mellan CPU-arbete och väntan på I/O.
- CPython 3.11+; varje obligatoriskt exempel är lokalt och använder bara standardbiblioteket.

## Förutsäg innan du kör
Innan du inväntar den första coroutinen: förutsäg när dess kropp börjar köras och vilken sats som kan låta en annan task köra. När du har kört det avgränsade exemplet jämför du den observerade ordningen med din förutsägelse, utan att använda en fast sleep som bevis för schemaläggning.

---

## 1. En async-funktion

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

- `asyncio.sleep` simulerar I/O.
- `await` väntar här men låter andra körbara tasks fortsätta.

---

## 2. Äg samtidiga tasks med `TaskGroup`

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

Kontexten äger varje skapad task och avslutas inte förrän alla är klara. Om ett barn misslyckas avbryter `TaskGroup` ofärdiga syskon, väntar på deras städning och höjer en `ExceptionGroup`. Fånga ett väntat bladfel med `except*` utanför gruppen; kasta inte bort oväntade fel.

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

`gather` returnerar resultaten i indataordning. Det är fortsatt användbart när det resultatkontraktet är målet, men `TaskGroup` gör livstid och syskonstädning tydliga för obligatoriskt samtidigt arbete.

---

## 4. Fel i tasks

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

Undantag hanteras som i vanliga funktioner, men vid `await`.

### Begränsa en grupp med `asyncio.timeout`

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

Timeouten avbryter den aktuella operationen; task-gruppen sprider cancellation till sina barn och väntar på båda `finally`-blocken. Fånga `TimeoutError` utanför timeout-kontexten. Ett barnfel följer samma ägarregel: syskon avbryts och städas innan gruppen rapporterar felet.

### Avbrytning och städning
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

Cancellation är en återhämtningsbar kontrollväg: använd `finally` för att frigöra resurser, vänta på den avbrutna tasken och hantera `CancelledError` vid koordinatorgränsen. Fånga inte `CancelledError` inne i arbetaren för att fortsätta som om inget hänt; låt felet spridas efter städningen.

Den kompletterande [modulen och testerna för strukturerad samtidighet](structured_async.py) täcker framgång, barnfel, timeout, syskon-cancellation, städning och att inga tasks blir kvar. Kör från `chapter-21-async/` med `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

---

## Vägledda övningar (med TODO)

1. **21-1 · Samtidig timer**

   ```python todo
   # TODO 1: launch 3 owned tasks in a TaskGroup and observe completion vs result order
   ```
   *Ledtråd*: behåll task-objekten som gruppen skapade och läs `.result()` först när kontexten har avslutats.

2. **21-2 · API-simulator utan Internet**

   ```python todo
   # TODO 1: create async def fake_get(url): await asyncio.sleep(1); return {"url": url, "ok": True}
   # TODO 2: use asyncio.gather to request 3 "urls" concurrently
   # TODO 3: print the result list
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

3. **21-3 · Hantera cancellation**

   ```python todo
   # TODO 1: bound a TaskGroup with asyncio.timeout
   # TODO 2: give each worker a finally cleanup marker
   # TODO 3: verify no child remains after TimeoutError
   ```
   *Ledtråd*: fånga `TimeoutError` utanför timeout-kontexten och placera resursstädning i varje tasks `finally`-block.

---

## Vanliga misstag

- Glömma `await` och få coroutine-objekt.
- Anropa `asyncio.run` inuti redan async kod.
- Köra blockerande `requests` i async-funktion och förlora vinsten.
- Skapa tasks utan ägare och returnera medan de fortfarande kör.
- Svälja `CancelledError` inne i en task, vilket kan bryta städningen i `TaskGroup` och timeout.

---

## Förklarade lösningar

1. **Timer**: skapa alla timers i en `TaskGroup`; efter kontexten är varje task klar och `.result()` kan läsas säkert. Registrera avslutsordningen separat om det är den du vill observera.
2. **Simulator**: `fake_get` returnerar dict efter väntan och `gather` samlar listan.
3. **Cancellation**: `asyncio.timeout` avbryter den ägda operationen; varje task städar i `finally`, gruppen väntar på syskonen och koordinatorn fångar `TimeoutError` efter kontexten. Bekräfta att `asyncio.all_tasks()` inte innehåller någon oavslutad task utom den aktuella test-tasken.

---

## Sammanfattning

`asyncio` koordinerar I/O-väntande tasks utan att blockera hela programmet och förbereder async frameworks som FastAPI.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: en event loop äger samtidiga tasks och bevarar resultatordning endast där den utlovas.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: taskfel och timeout avbryter syskon, sprids korrekt och städar resurser.
- **Verifiering**: kör varje runnable-block och bevisa att framgång, fel och timeout inte lämnar bakgrundstasks.
- **Förklaring**: förklara tasks mot trådar, när async hjälper och varför blockerande anrop tar bort vinsten.

## Avslutande reflektion

Känn igen när async hjälper. Allt behöver det inte, men rätt använd kan effektivisera tjänster.
