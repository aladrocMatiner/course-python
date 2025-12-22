# Capítulo 21 · Concurrencia amigable: introducción a `asyncio`

## Qué vamos a construir
Exploraremos por qué existe la concurrencia, diferencia entre hilos y async, y crearemos pequeñas tareas asíncronas con `asyncio`. Simularemos llamadas a APIs que tardan y veremos cómo `await` permite avanzar sin bloquear.

## Orden pedagógico
1. **Motivación**: tareas que esperan (I/O).
2. **`async`/`await` básico**.
3. **`asyncio.sleep`, `gather`, `create_task`**.
4. **Errores comunes y cancelación**.
5. **Nivel extra (opcional)**: llamadas HTTP asíncronas con librerías externas.

## Objetivos de aprendizaje
- Diferenciar trabajo CPU vs I/O.
- Declarar funciones `async def` y usar `await`.
- Ejecutar múltiples tareas en paralelo con `asyncio.run` y `gather`.
- Manejar excepciones en tareas async.

## Por qué importa
Los servicios modernos suelen esperar respuestas externas (APIs, bases). La programación asíncrona permite aprovechar ese tiempo para hacer otras tareas.

### Mini aventura
Imagina que eres camarera en una cafetería. Mientras esperas a que la máquina de café termine, aprovechas para servir agua o cobrar a otra persona. Eso mismo hace `asyncio`: mientras una tarea “se cocina”, puedes avanzar con otra sin quedarte inmóvil mirando la cafetera.

### Una frase importante
Si esto te parece raro al principio, es normal. Lo importante hoy es entender la idea: **cuando una tarea está esperando**, tu programa puede avanzar con otra.

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
- `await` significa “espera aquí, pero deja que otras tareas se muevan si pueden”.

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

2. **21-2 · Simulador de API (sin Internet)**
   ```python
   # TODO 1: crea async def fake_get(url): await asyncio.sleep(1); return {"url": url, "ok": True}
   # TODO 2: usa asyncio.gather para pedir 3 \"urls\" en paralelo
   # TODO 3: imprime la lista de resultados
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
2. **Simulador de API**: `fake_get` devuelve un dict tras esperar; `asyncio.gather` reúne todos los resultados en una lista.
3. **Cancelación**: `task.cancel()` lanza `CancelledError` que puedes atrapar para limpiar.

---

## Resumen
Con `asyncio` puedes coordinar tareas que esperan I/O sin bloquear el programa, preparando tu mente para frameworks async como FastAPI.

## Reflexión final
Usa esta introducción para reconocer cuándo te conviene async. No todo lo necesita, pero cuando lo aplicas bien, tus servicios se vuelven más eficientes.
