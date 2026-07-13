# Kapitel 21 · Vänlig concurrency: introduktion till `asyncio`

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Vi utforskar varför concurrency finns, skillnaden mot trådar och små async tasks med `asyncio`. Långsamma API-anrop simuleras så att `await` kan låta programmet göra framsteg utan blockering.

## Lärväg

1. **Motivation**: tasks som väntar på I/O.
2. **`async` och `await`**.
3. **`asyncio.sleep`, `gather`, `create_task`**.
4. **Vanliga misstag och cancellation**.
5. **Frivillig bonus**: async HTTP med externa bibliotek.

## Lärandemål

- Skilja CPU-arbete från I/O-väntan.
- Skriva `async def` och använda `await`.
- Köra flera tasks tillsammans med `asyncio.run` och `gather`.
- Hantera undantag i async tasks.

## Varför det spelar roll

Moderna tjänster väntar ofta på API:er och databaser. Async använder väntetiden till annat arbete.

### Miniäventyr

I ett kafé kan du ta en ny beställning medan kaffemaskinen arbetar. `asyncio` låter en annan task gå vidare när en väntar.

### En viktig mening

Det är normalt att detta känns ovant. Kärnan är: **när en task väntar kan programmet göra framsteg på annat håll**.

## Förkunskaper
Rekommenderade tidigare kapitel: 10, 11, 14.
Använd CPython 3.11+ i en tillfällig lokal miljö och håll data, hemligheter och tjänster borta från verkliga system.

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

## 2. Köra tasks samtidigt

```python illustrative
async def procesar(usuario):
    await asyncio.sleep(1)
    return f"Listo {usuario}"

async def main():
    usuarios = ["Noor", "Frej", "Taha"]
    tareas = [asyncio.create_task(procesar(u)) for u in usuarios]
    for tarea in tareas:
        print(await tarea)

asyncio.run(main())
```

Alla tasks startar nästan samtidigt.

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

`gather` returnerar resultaten i anropsordning.

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

Undantag hanteras som i vanliga funktioner, men vid `await`.

---

## Vägledda övningar (med TODO)

1. **21-1 · Samtidig timer**

   ```python todo
   # TODO 1: launch 3 tasks that sleep different times and observe the order
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

2. **21-2 · API-simulator utan Internet**

   ```python todo
   # TODO 1: create async def fake_get(url): await asyncio.sleep(1); return {"url": url, "ok": True}
   # TODO 2: use asyncio.gather to request 3 "urls" concurrently
   # TODO 3: print the result list
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

3. **21-3 · Hantera cancellation**

   ```python todo
   # TODO 1: cancel a task with task.cancel()
   # TODO 2: handle asyncio.CancelledError
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

---

## Vanliga misstag

- Glömma `await` och få coroutine-objekt.
- Anropa `asyncio.run` inuti redan async kod.
- Köra blockerande `requests` i async-funktion och förlora vinsten.

---

## Förklarade lösningar

1. **Timer**: olika `asyncio.sleep` visar avslut efter varaktighet.
2. **Simulator**: `fake_get` returnerar dict efter väntan och `gather` samlar listan.
3. **Cancellation**: `task.cancel()` utlöser `CancelledError`, som fångas för cleanup.

---

## Sammanfattning

`asyncio` koordinerar I/O-väntande tasks utan att blockera hela programmet och förbereder async frameworks som FastAPI.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: resultatet uppfyller enhetens kontrakt.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: ett normalfall, ett gränsfall och en återhämtning testas.
- **Verifiering**: exempel och övningar körs i en ren miljö.
- **Förklaring**: du kan motivera besluten och deras risker.

## Avslutande reflektion

Känn igen när async hjälper. Allt behöver det inte, men rätt använd kan effektivisera tjänster.
