# Capítol 21 · Concurrència amable: introducció a `asyncio`

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Explorarem per què existeix la concurrència, la diferència entre fils i async, i crearem tasques asíncrones amb `asyncio`. Simularem crides que triguen i veurem com `await` permet avançar sense bloquejar.

## Objectius d’aprenentatge
- Distingir treball CPU vs I/O.
- Escriure `async def` i usar `await`.
- Llançar diverses tasques amb `asyncio.gather` i `create_task`.
- Gestionar errors i cancel·lacions.

---

## Funció async

```python
import asyncio

async def saludar(nombre):
    await asyncio.sleep(1)
    return f"Hola {nombre}"

async def main():
    mensaje = await saludar("Ada")
    print(mensaje)

asyncio.run(main())
```

---

## Tasques en paral·lel

```python
import asyncio

async def procesar(usuario):
    await asyncio.sleep(1)
    return f"Listo {usuario}"

async def main():
    usuarios = ["Ada", "Linus", "Carol"]
    tareas = [asyncio.create_task(procesar(u)) for u in usuarios]
    for tarea in tareas:
        print(await tarea)

asyncio.run(main())
```

---

## `asyncio.gather`
```python
async def main():
    resultados = await asyncio.gather(
        procesar("Ada"),
        procesar("Linus"),
    )
    print(resultados)
```

---

## Resum
Amb `asyncio` pots coordinar tasques que esperen I/O sense bloquejar el programa. No tot ho necessita, però quan ho apliques bé, els serveis poden ser més eficients.
