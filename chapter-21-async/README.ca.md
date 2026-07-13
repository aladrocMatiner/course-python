# Capítol 21 · Concurrència amable: introducció a `asyncio`

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Explorarem per què existeix la concurrència, quina diferència hi ha entre threads i async i com es creen tasques asíncrones petites amb `asyncio`. Simularem crides lentes a una API i veurem com `await` permet que el programa continuï avançant sense quedar bloquejat.

## Itinerari d'aprenentatge
1. **Motivació: tasques que esperen entrada/sortida**.
2. **Fonaments d'`async` i `await`**.
3. **`asyncio.sleep`, `gather` i `create_task`**.
4. **Errors habituals i cancel·lació**.
5. **Nivell extra opcional: HTTP asíncron amb llibreries externes**.

## Objectius d'aprenentatge
- Entendre la diferència entre treball de CPU i treball d'entrada/sortida.
- Escriure funcions `async def` i utilitzar `await`.
- Executar diverses tasques «alhora» amb `asyncio.run` i `gather`.
- Gestionar excepcions dins tasques asíncrones.

## Per què és important
Els serveis moderns sovint esperen respostes externes, com APIs o bases de dades. La programació asíncrona permet aprofitar aquest temps d'espera per fer altres coses.

### Miniaventura
Imagina que treballes en una cafeteria. Mentre esperes la màquina de cafè, pots servir aigua o prendre una altra comanda. Això és el que fa `asyncio`: mentre una tasca «es cuina», pots atendre'n una altra en lloc de mirar la màquina.

### Una frase important
Si al principi et resulta estrany, és normal. La idea clau d'avui és aquesta: **quan una tasca està esperant**, el programa pot continuar progressant en una altra banda.

## Prerequisits
Capítols previs recomanats: 10, 11, 14.
Usa CPython 3.11+ en un entorn local d’un sol ús i mantén les dades, els secrets i els serveis fora de sistemes reals.

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

## 2. Executar tasques concurrentment

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

- Totes les tasques comencen gairebé al mateix moment.

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

- `gather` retorna una llista de resultats en el mateix ordre.

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

- Gestiona les excepcions com a les funcions normals, però amb `await`.

---

## Exercicis guiats (amb TODO)
1. **21-1 · Temporitzador concurrent**
   ```python todo
   # TODO 1: launch 3 tasks that sleep different times and observe the order
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

2. **21-2 · Simulador d'API sense Internet**
   ```python todo
   # TODO 1: create async def fake_get(url): await asyncio.sleep(1); return {"url": url, "ok": True}
   # TODO 2: use asyncio.gather to request 3 "urls" concurrently
   # TODO 3: print the result list
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

3. **21-3 · Gestionar cancel·lacions**
   ```python todo
   # TODO 1: cancel a task with task.cancel()
   # TODO 2: handle asyncio.CancelledError
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

---

## Errors habituals
- Oblidar `await` i obtenir objectes `coroutine` en lloc del resultat.
- Cridar `asyncio.run` dins una funció que ja és asíncrona; no està permès.
- Barrejar crides bloquejants com `requests` dins funcions async i perdre'n el benefici.

---

## Solucions explicades
1. **Temporitzador**: `asyncio.sleep` amb durades diferents mostra que les tasques acaben segons el temps d'espera.
2. **Simulador d'API**: `fake_get` retorna un diccionari després d'esperar; `asyncio.gather` reuneix tots els resultats en una llista.
3. **Cancel·lació**: `task.cancel()` provoca `CancelledError`, que pots capturar per fer cleanup.

---

## Resum
Amb `asyncio` pots coordinar tasques que esperen entrada/sortida sense bloquejar tot el programa, i et prepares per a frameworks asíncrons com FastAPI.

## Punt de control i rúbrica
- **Correcció**: el resultat compleix el contracte de la unitat.
- **Llegibilitat**: els noms i les responsabilitats s’entenen a la primera.
- **Errors**: es proven un cas vàlid, un límit i una recuperació.
- **Verificació**: els exemples i els exercicis s’executen en un entorn net.
- **Explicació**: pots justificar les decisions i els riscos.

## Reflexió final
Utilitza aquesta introducció per reconèixer quan async és útil. No tot ho necessita, però quan s'aplica bé pot fer que els serveis siguin molt més eficients.
