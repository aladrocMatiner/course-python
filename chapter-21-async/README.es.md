# Capítulo 21 · Concurrencia amigable: introducción a `asyncio`

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Exploraremos por qué existe la concurrencia, diferencia entre hilos y async, y crearemos pequeñas tareas asíncronas con `asyncio`. Simularemos llamadas a APIs que tardan y veremos cómo `await` permite avanzar sin bloquear.

## Orden pedagógico
1. **Motivación**: tareas que esperan (I/O).
2. **`async`/`await` básico**.
3. **Concurrencia con propietario mediante `TaskGroup`**, y después `gather` para resultados ordenados.
4. **Timeouts, fallos, cancelación y limpieza**.
5. **Nivel extra (opcional)**: llamadas HTTP asíncronas con librerías externas.

## Objetivos de aprendizaje
- Diferenciar trabajo CPU vs I/O.
- Declarar funciones `async def` y usar `await`.
- Distinguir las tareas cooperativas de asyncio de los hilos del sistema operativo.
- Ser propietario del trabajo concurrente con `TaskGroup` y acotarlo con `asyncio.timeout` en Python 3.11+.
- Manejar fallos y cancelaciones sin tragarse las señales de limpieza ni dejar trabajo en segundo plano.

## Por qué importa
Los servicios modernos suelen esperar respuestas externas (APIs, bases). La programación asíncrona permite aprovechar ese tiempo para hacer otras tareas.

### Mini aventura
Imagina que eres camarera en una cafetería. Mientras esperas a que la máquina de café termine, aprovechas para servir agua o cobrar a otra persona. Eso mismo hace `asyncio`: mientras una tarea “se cocina”, puedes avanzar con otra sin quedarte inmóvil mirando la cafetera.

### Una frase importante
Si esto te parece raro al principio, es normal. Lo importante hoy es entender la idea: **cuando una tarea está esperando**, tu programa puede avanzar con otra.

### Las tareas no son hilos
Una tarea de asyncio es planificada cooperativamente por un event loop, normalmente en un único hilo del sistema operativo. Solo cede el turno al llegar a un `await` que pueda suspenderse. El sistema operativo planifica un hilo, que puede ejecutar código bloqueante independientemente y tiene otros riesgos de sincronización. Por tanto, ejecutar `requests.get()` o trabajo intensivo de CPU directamente dentro de `async def` sigue bloqueando el hilo del event loop; usa una biblioteca asíncrona, divide el trabajo de CPU de forma adecuada o aísla deliberadamente una llamada bloqueante con `asyncio.to_thread` cuando la compensación esté justificada.

## Prerrequisitos
- Funciones, excepciones, bucles y una distinción clara entre el trabajo de CPU y la espera de E/S.
- CPython 3.11+; todos los ejemplos obligatorios son locales y solo usan la biblioteca estándar.

## Predice antes de ejecutar
Antes de esperar la primera corrutina con `await`, predice cuándo comienza su cuerpo y qué sentencia puede dejar que se ejecute otra tarea. Después de ejecutar el ejemplo acotado, compara el orden observado con tu predicción sin usar una espera fija como prueba de la planificación.

---

## 1. Función async

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

- `asyncio.sleep` simula trabajo I/O.
- `await` significa “espera aquí, pero deja que otras tareas se muevan si pueden”.

---

## 2. Ser propietario de tareas concurrentes con `TaskGroup`

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

- El contexto posee todas las tareas creadas y no termina hasta que todas finalizan.
- Si una hija falla, `TaskGroup` cancela a sus hermanas sin terminar, espera su limpieza y lanza un `ExceptionGroup`. Captura un fallo hoja esperado con `except*` fuera del grupo; no descartes fallos inesperados.

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

- `gather` devuelve una lista con los resultados en el orden de entrada. Sigue siendo útil cuando ese contrato de resultados es el objetivo, pero `TaskGroup` hace explícitos la vida de las tareas y la limpieza de hermanas para trabajo concurrente obligatorio.

---

## 4. Errores en tareas

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

- Maneja excepciones como en funciones normales, pero con `await`.

### Acotar un grupo con `asyncio.timeout`
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

El timeout cancela la operación actual; el grupo propaga la cancelación a sus hijas y espera ambos bloques `finally`. Captura `TimeoutError` fuera del contexto de timeout. El fallo de una hija sigue la misma regla de propiedad: se cancelan y limpian sus hermanas antes de que el grupo comunique el fallo.

### Cancelación y limpieza
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

- La cancelación es una ruta de control recuperable: usa `finally` para liberar recursos, espera la tarea cancelada y maneja `CancelledError` en el límite coordinador. Dentro de la trabajadora cancelada no captures `CancelledError` para continuar como si nada; deja que se propague tras la limpieza.

El [módulo y las pruebas de concurrencia estructurada](structured_async.py) cubren éxito, fallo de una hija, timeout, cancelación de hermanas, limpieza y ausencia de tareas sobrantes. Desde `chapter-21-async/`, ejecuta `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

---

## Ejercicios guiados (con TODOs)
1. **21-1 · Temporizador concurrente**
   ```python todo
   # TODO 1: launch 3 owned tasks in a TaskGroup and observe completion vs result order
   ```
   *Pista*: conserva los objetos task creados por el grupo y lee `.result()` solo después de que termine el contexto.

2. **21-2 · Simulador de API (sin Internet)**
   ```python todo
   # TODO 1: create async def fake_get(url): await asyncio.sleep(1); return {"url": url, "ok": True}
   # TODO 2: use asyncio.gather to request 3 "urls" concurrently
   # TODO 3: print the result list
   ```
   *Pista*: pasa las corrutinas directamente a `asyncio.gather` y ejecuta un único `main()` de nivel superior.

3. **21-3 · Manejar cancelaciones**
   ```python todo
   # TODO 1: bound a TaskGroup with asyncio.timeout
   # TODO 2: give each worker a finally cleanup marker
   # TODO 3: verify no child remains after TimeoutError
   ```
   *Pista*: captura `TimeoutError` fuera del contexto de timeout y coloca la limpieza de recursos en el bloque `finally` de cada tarea.

---

## Errores comunes
- Olvidar `await` y recibir objetos `coroutine`.
- Llamar `asyncio.run` dentro de una función ya async (no permitido).
- Mezclar operaciones que bloquean (`requests`) dentro de funciones async -> se pierde el beneficio.
- Crear tareas sin propietario y regresar mientras siguen ejecutándose.
- Tragarse `CancelledError` dentro de una tarea, lo que puede romper la limpieza de `TaskGroup` y timeout.

---

## Explicación de soluciones
1. **Temporizador**: crea todos los temporizadores dentro de un `TaskGroup`; al salir de su contexto, cada tarea ha terminado y puedes leer `.result()` con seguridad. Registra el orden de finalización aparte si eso es lo que quieres observar.
2. **Simulador de API**: `fake_get` devuelve un dict tras esperar; `asyncio.gather` reúne todos los resultados en una lista.
3. **Cancelación**: `asyncio.timeout` cancela la operación poseída; cada tarea limpia en `finally`, el grupo espera a todas las hermanas y el coordinador captura `TimeoutError` después del contexto. Confirma que `asyncio.all_tasks()` no contiene ninguna tarea sin terminar salvo la tarea de prueba actual.

---

## Resumen
Con `asyncio` puedes coordinar tareas que esperan I/O sin bloquear el programa, preparando tu mente para frameworks async como FastAPI.

## Punto de control y rúbrica
- **Corrección**: un event loop posee las tareas concurrentes y solo conserva el orden de resultados donde se promete.
- **Legibilidad**: las responsabilidades de las corrutinas, las tareas y el coordinador son distintas.
- **Errores**: el fallo de una tarea y el timeout cancelan hermanas, se propagan correctamente y limpian recursos.
- **Verificación**: ejecuta cada bloque runnable y demuestra que éxito, fallo y timeout no dejan tareas en segundo plano.
- **Explicación**: explica tareas frente a hilos, cuándo ayuda async y por qué las llamadas bloqueantes eliminan la ventaja.

## Reflexión final
Usa esta introducción para reconocer cuándo te conviene async. No todo lo necesita, pero cuando lo aplicas bien, tus servicios se vuelven más eficientes.
