# Capítulo 21 · Concurrencia amigable: introducción a `asyncio`

## Qué vamos a construir
Exploraremos por qué existe la concurrencia, diferencia entre hilos y async, y crearemos pequeñas tareas asíncronas con `asyncio`. Simularemos llamadas a APIs que tardan y veremos cómo `await` permite avanzar sin bloquear.

## Orden pedagógico
1. **Motivación**: tareas que esperan (I/O).
2. **`async`/`await` básico**.
3. **`asyncio.sleep`, `gather`, `create_task`**.
4. **Integración con `requests`?** (usaremos `httpx` async) o simular.
5. **Errores comunes y cancelación**.

## Objetivos de aprendizaje
- Diferenciar trabajo CPU vs I/O.
- Declarar funciones `async def` y usar `await`.
- Ejecutar múltiples tareas en paralelo con `asyncio.run` y `gather`.
- Manejar excepciones en tareas async.

## Por qué importa
Los servicios modernos suelen esperar respuestas externas (APIs, bases). La programación asíncrona permite aprovechar ese tiempo para hacer otras tareas.

---

## 1. Función async

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

- `asyncio.sleep` simula trabajo I/O.

---

## 2. Ejecutar tareas en paralelo

```python
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

- Todas las tareas se inician casi al mismo tiempo.

---

## 3. `asyncio.gather`

```python
async def main():
    resultados = await asyncio.gather(
        procesar("Ada"),
        procesar("Linus"),
    )
    print(resultados)
```

- `gather` devuelve una lista con los resultados en orden.

---

## 4. Errores en tareas

```python
async def puede_fallar():
    raise ValueError("Oops")

async def main():
    try:
        await puede_fallar()
    except ValueError as exc:
        print("Capturado", exc)
```

- Maneja excepciones como en funciones normales, pero con `await`.

---

## Ejercicios guiados (con TODOs)
1. **21-1 · Temporizador concurrente**
   ```python
   # TODO 1: lanza 3 tareas que duerman distintos tiempos y observa el orden
   ```

2. **21-2 · Cliente async**
   ```python
   # TODO 1: instala httpx
   # TODO 2: usa httpx.AsyncClient para pedir 3 URLs en paralelo
   ```

3. **21-3 · Manejar cancelaciones**
   ```python
   # TODO 1: cancela una tarea con task.cancel()
   # TODO 2: maneja asyncio.CancelledError
   ```

---

## Errores comunes
- Olvidar `await` y recibir objetos `coroutine`.
- Llamar `asyncio.run` dentro de una función ya async (no permitido).
- Mezclar operaciones que bloquean (`requests`) dentro de funciones async -> se pierde el beneficio.

---

## Explicación de soluciones
1. **Temporizador**: `asyncio.sleep` con diferentes segundos muestra cómo finalizan según su duración.
2. **Cliente async**: `async with httpx.AsyncClient() as client:` y `await client.get(url)`; `gather` combina resultados.
3. **Cancelación**: `task.cancel()` lanza `CancelledError` que puedes atrapar para limpiar.

---

## Resumen
Con `asyncio` puedes coordinar tareas que esperan I/O sin bloquear el programa, preparando tu mente para frameworks async como FastAPI.

## Reflexión final
Usa esta introducción para reconocer cuándo te conviene async. No todo lo necesita, pero cuando lo aplicas bien, tus servicios se vuelven más eficientes.
