# Kapitel 21 · Vänlig concurrency: intro till `asyncio`

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Vi lär oss grunderna i asynkron programmering med `asyncio`: `async`/`await`, `gather`, `create_task` och hur man hanterar fel.

---

## Första async‑exemplet
```python
import asyncio

async def saludar(nombre):
    await asyncio.sleep(1)
    return f"Hola {nombre}"

async def main():
    print(await saludar("Ada"))

asyncio.run(main())
```

---

## Flera uppgifter
```python
async def procesar(usuario):
    await asyncio.sleep(1)
    return f"Listo {usuario}"

async def main():
    resultados = await asyncio.gather(procesar("Ada"), procesar("Linus"))
    print(resultados)
```

---

## Sammanfattning
Async passar när du väntar på I/O (API:er, DB). Det är inte alltid nödvändigt, men kan göra tjänster effektivare.
