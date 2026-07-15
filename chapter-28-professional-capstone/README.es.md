# Capítulo 28 · Proyecto final profesional: un gestor de pedidos en cuatro etapas

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir

Harás crecer un único gestor local de pedidos en lugar de empezar cuatro
proyectos finales inconexos. La etapa de fundamentos combina valores
inmutables, clases y funciones en memoria. La etapa práctica mantiene el mismo
dominio y añade SQLite, una interfaz de línea de órdenes (CLI), configuración,
logging y pruebas. Una etapa opcional de sistemas expone el mismo servicio
mediante un adaptador loopback acotado. Una etapa heroica final y opcional
verifica una distribución de fuentes y un wheel sin publicar ninguno de los
dos.

Todos los ejemplos usan identificadores ficticios como `ORD-001` y etiquetas
de artículo como `widget`. No los sustituyas por información real de clientes,
direcciones, pagos, credenciales o producción.

## Objetivos de aprendizaje

Al terminar las etapas que elijas, podrás:

- modelar un `Order` inmutable y acotado, y explicar cada transición aceptada;
- separar las responsabilidades del dominio, el servicio, el repositorio, la
  CLI y la red opcional;
- conservar el estado anterior después de fallos de validación, duplicación,
  transición, bloqueo o base de datos;
- operar una CLI respaldada por SQLite con configuración explícita, salida
  estable, códigos de salida significativos y logs respetuosos con la
  privacidad;
- verificar comportamientos normales, límite, inválidos y de recuperación en
  la frontera responsable;
- ejecutar un laboratorio loopback opcional con límites explícitos de bytes,
  peticiones, concurrencia y tiempo, y un cierre determinista; y
- distinguir la evidencia del árbol de fuentes de la de un artefacto
  construido, inspeccionado e instalado en limpio, sin subirlo a ningún sitio.

## Prerrequisitos y rutas con paradas independientes

El número de catálogo no convierte automáticamente los Capítulos 23–27 en
prerrequisitos. Entra solo en la etapa para la que cumplas el punto de control
indicado.

### Ruta de fundamentos

- **Entrada:** el [punto de control de clases del Capítulo 12](../chapter-12-oop/README.es.md#punto-de-control-y-rúbrica)
  y su [ejercicio de clase de datos inmutable](../chapter-12-oop/README.es.md#ejercicios-guiados-con-todos),
  además de las funciones, los condicionales, los bucles y las colecciones de
  los Capítulos 3–11.
- **Tiempo:** 2–3 sesiones de 50–75 minutos.
- **Resultado:** un servicio en memoria probado que crea, lista y hace avanzar
  pedidos sintéticos inmutables.
- **Salida:** se cumplen los cinco elementos de la rúbrica de fundamentos.
- **Parada segura:** conserva el artefacto en memoria; la persistencia, las
  redes y el empaquetado no son obligatorios.

### Ruta práctica

- **Entrada:** la salida de fundamentos más los Capítulos
  [13](../chapter-13-files/README.es.md#punto-de-control-y-rúbrica) a
  [18](../chapter-18-testing/README.es.md#punto-de-control-y-rúbrica). Completa
  el [punto de control del apéndice de CLI](../appendix-cli-parser/README.es.md#punto-de-control-y-rúbrica)
  antes de implementar el adaptador de órdenes, y completa el
  [punto de control de logging del Capítulo 20](../chapter-20-logging/README.es.md#punto-de-control-y-rúbrica)
  antes del subpunto de control sobre privacidad de logs; así se evita que el
  logging sea un concepto nuevo oculto.
- **Tiempo:** 4–6 sesiones de 50–80 minutos.
- **Resultado:** una CLI transaccional con SQLite, configuración explícita,
  eventos respetuosos con la privacidad, evidencia de subprocesos y
  recuperación.
- **Salida:** la suite de la biblioteca estándar pasa y quien aprende puede
  explicar una reversión y la regla de precedencia de la CLI.
- **Parada segura:** este es un proyecto final práctico completo. El servidor y
  la construcción del paquete son opcionales.

### Ruta de sistemas opcional

- **Entrada:** la salida práctica, el
  [punto de control de asyncio del Capítulo 21](../chapter-21-async/README.es.md#punto-de-control-y-rúbrica)
  y la [rúbrica de evaluación de redes del Capítulo 23](../chapter-23-network-programming/README.es.md#rúbrica-de-evaluación).
- **Tiempo:** 2–3 sesiones de 50–75 minutos.
- **Resultado:** un servicio JSON delimitado por saltos de línea y probado en
  `127.0.0.1`, en un puerto asignado por el sistema operativo, con recuperación
  de capacidad y cierre limpio.
- **Salida:** las ocho pruebas de loopback pasan y se puede explicar cada límite
  declarado.
- **Parada segura:** no se afirma exposición pública, TLS, autenticación ni
  despliegue.

### Ruta heroica opcional de empaquetado

- **Entrada:** la salida práctica más las lecciones sobre paquetes y entornos
  de los [Capítulos 15](../chapter-15-modulos/README.es.md#punto-de-control-y-rúbrica)
  y [16](../chapter-16-entornos/README.es.md#punto-de-control-y-rúbrica).
- **Tiempo:** 2–3 sesiones de 50–80 minutos después de haber provisionado
  deliberadamente las entradas de construcción exactas.
- **Resultado:** evidencia local de la secuencia sdist → wheel → instalación
  limpia desde un directorio de trabajo externo.
- **Salida:** pasan todas las fases del verificador y quien aprende puede
  indicar qué host se ha probado realmente.
- **Parada segura:** ninguna subida, firma, atestación, token ni mutación de un
  índice de paquetes pertenece a este capítulo.

## Arquitectura expresada con palabras

La CLI y el adaptador loopback opcional traducen la entrada externa. Ambos
llaman a `OrderService`. El servicio crea valores `Order` y pide a un
`OrderRepository` que los almacene o los haga avanzar.
`InMemoryOrderRepository` y `SQLiteOrderRepository` implementan las mismas
operaciones. SQLite es, por tanto, un detalle de persistencia reemplazable, no
un segundo conjunto de reglas de negocio.

La secuencia de control es:

1. un adaptador analiza y acota la entrada;
2. el servicio construye o solicita una operación de dominio;
3. el pedido inmutable valida el dominio exacto;
4. el repositorio seleccionado confirma el cambio completo o conserva el
   estado anterior;
5. el adaptador emite una salida acotada o una categoría de error estable.

Esta descripción numerada es el equivalente textual completo de un diagrama de
arquitectura; ningún significado depende del color, las flechas o la posición
en pantalla.

## Proyecto complementario y directorio de trabajo de verificación

La autoridad ejecutable es
`chapter-28-professional-capstone/examples/order-tracker/`. Ejecuta la suite
completa de la biblioteca estándar desde la raíz del repositorio:

```bash illustrative
python -B -m unittest discover \
  -s chapter-28-professional-capstone/examples/order-tracker/tests \
  -t chapter-28-professional-capstone/examples/order-tracker \
  -p 'test_*.py'
```

Esta orden ejercita el dominio, ambos repositorios, el servicio, los
subprocesos de la CLI, la privacidad de los logs, el ciclo de vida de loopback,
los metadatos, la comprobación previa de artefactos y los fixtures de inspección
de archivos. Usa directorios temporales, datos falsos, puertos efímeros, salida
acotada de procesos hijos y tiempos de espera acotados.

---

## Etapa 1 · Fundamentos: dominio inmutable y servicio en memoria

### Objetivos y contexto de fundamentos

Un gestor de pedidos parece sencillo hasta que un duplicado sobrescribe un
pedido anterior o un pedido enviado retrocede. La etapa de fundamentos hace
observables estas reglas antes de que una base de datos o un adaptador añadan
carga cognitiva.

Aprenderás a:

- crear un pedido inmutable en estado `pending`;
- permitir solo `pending → packed → shipped`;
- aceptar los límites inclusivos exactos de texto y cantidad;
- listar por `order_id` en lugar de depender por accidente del orden de
  inserción; y
- demostrar que cada operación rechazada deja intacto el estado anterior.

### Predice el ciclo de vida

Antes de leer la implementación, predice estas observaciones:

1. ¿Qué estados resultan de dos llamadas a `advance("ORD-001")`?
2. ¿Qué debería hacer una tercera llamada?
3. Si una segunda creación usa `ORD-001` con un artículo distinto, ¿qué pedido
   debería conservarse?
4. ¿Debe aceptarse `True` como cantidad `1`?

Escribe el estado previsto o la categoría de excepción, no un traceback
completo.

### Teoría mínima: valor, servicio y repositorio

`Order` es una clase de datos congelada, de acuerdo con el ejercicio de clase
de datos inmutable del Capítulo 12. Una transición devuelve una instantánea
nueva; no edita el valor anterior. `OrderService` coordina el caso de uso. Un
pequeño contrato de herencia nombra las cinco operaciones del repositorio, e
`InMemoryOrderRepository` las implementa con un diccionario devuelto en orden
de identificador. Esta etapa no requiere ningún concepto de tipado estructural
del Capítulo 27.

Los fallos estables del dominio son:

- `OrderValidationError` para valores acotados no válidos;
- `DuplicateOrderError` para un identificador existente;
- `UnknownOrderError` para un identificador ausente;
- `InvalidTransitionError` al hacer avanzar `shipped`; y
- `RepositoryError` para fallos de persistencia o ciclo de vida.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/domain.py check=learning:contract -->
```python source-ref
pending = Order("ORD-001", "widget", 2)
packed = pending.advanced()
assert pending.status == "pending"
assert packed.status == "packed"
```

### Límites del dominio

Después de eliminar los espacios de los extremos:

- `order_id` tiene de 1 a 32 caracteres;
- `item` tiene de 1 a 80 caracteres;
- `quantity` es un `int` integrado exacto de 1 a 1000;
- se rechazan `bool` y las subclases de `int`; y
- `status` es exactamente `pending`, `packed` o `shipped`.

Se aceptan los valores 32, 80, 1 y 1000. El texto vacío, las longitudes 33/81,
las cantidades 0/1001 y cualquiera de los booleanos se rechazan antes de que
cambie el estado del repositorio.

### TODO guiado de fundamentos

Trabaja en una copia desechable o en un archivo temporal que importe el proyecto
complementario:

```python todo
repository = InMemoryOrderRepository()
service = OrderService(repository)

# TODO 1: create ORD-001 for two widgets and record its status.
# TODO 2: advance it twice and record both new statuses.
# TODO 3: try one more advance and record the exception category.
# TODO 4: list again and prove ORD-001 is still shipped.
```

**Pista:** compara una instantánea inmutable capturada antes de la operación
rechazada con `service.get("ORD-001")` después. No captures `Exception`; nombra
el fallo de dominio que esperas.

### Evidencia feliz, límite, de fallo y de recuperación

- **Caso feliz:** `pending`, `packed` y `shipped` aparecen en ese orden.
- **Límite:** pasan un identificador de longitud 32, un artículo de longitud 80
  y las cantidades 1/1000.
- **Fallo recuperable:** un duplicado provoca `DuplicateOrderError` y conserva
  el artículo y la cantidad originales.
- **Recuperación:** vuelve a intentarlo con un identificador único; funciona sin
  reparar el estado interno del repositorio.
- **Fallo terminal:** hacer avanzar `shipped` provoca
  `InvalidTransitionError`; al volver a cargarlo sigue devolviendo `shipped`.

Ejecuta la evidencia específica:

```bash illustrative
cd chapter-28-professional-capstone/examples/order-tracker
python -B -m unittest tests.test_domain tests.test_service -v
```

### Solución de fundamentos explicada

La solución construye `Order` antes de llamar a `repository.add`, por lo que
los datos no válidos nunca llegan al almacenamiento. `advanced()` usa un único
mapa explícito del estado siguiente y devuelve un valor congelado nuevo. El
repositorio asigna ese valor solo después de que la validación de la transición
termine correctamente. Los duplicados se detectan antes de asignar en el
diccionario. Este orden convierte la recuperación sin cambios de estado en una
propiedad del diseño, no en un truco de limpieza.

### Errores comunes de fundamentos

- Mutar directamente `order.status` anula las instantáneas inmutables y falla.
- Tratar `bool` como una cantidad acepta un valor técnicamente similar a un
  entero, pero con un significado de dominio equivocado.
- Capturar todas las excepciones oculta si fallaron la validación, la búsqueda,
  la transición o la persistencia.
- Devolver el orden de inserción del diccionario crearía un contrato de orden
  accidental; el servicio exige identificadores ordenados.

### Punto de control y rúbrica de fundamentos

Suma un punto por cada elemento:

- **Corrección:** un pedido alcanza los tres estados en orden.
- **Límite:** pasan los límites inclusivos de texto y cantidad, y fallan los
  primeros valores no válidos.
- **Recuperación:** los fallos de duplicación y transición terminal conservan
  las instantáneas.
- **Separación:** quien aprende puede distinguir el valor, el servicio y el
  repositorio.
- **Explicación:** quien aprende explica por qué una instantánea inmutable nueva
  simplifica el razonamiento sobre la reversión.

Cinco puntos completan la etapa de fundamentos. Con cuatro, repite solo el caso
que falta; por debajo de cuatro, revisa las pruebas de límites y conservación
del estado. Puedes parar aquí con un artefacto en memoria completo y probado.

### Reflexión de fundamentos

¿Qué decisión de orden —validar, calcular y después asignar— hace más por
proteger el estado, y qué se rompería si la asignación ocurriera primero?

---

## Etapa 2 · Práctica: SQLite, CLI, configuración, logging y pruebas

### Objetivos prácticos y predicción

La etapa práctica conserva el mismo servicio y solo sustituye su repositorio.
Antes de ejecutarla, predice:

- qué base de datos gana cuando existen tanto `ORDER_TRACKER_DB` como
  `--database`;
- si una configuración de base de datos ausente debe crear `orders.db`
  implícitamente;
- qué permanece después de que una actualización de SQLite se interrumpa antes
  de confirmar la transacción; y
- qué flujo transporta los resultados estables y cuál lleva los diagnósticos y
  eventos.

Las respuestas son: gana el argumento explícito; no se crea ningún archivo
predeterminado; se conserva el estado confirmado anteriormente; stdout
transporta los resultados y stderr, los diagnósticos y eventos opcionales.

### Frontera de transacción de SQLite

`SQLiteOrderRepository` crea su esquema de forma idempotente y abre conexiones
de corta duración con un tiempo de espera de ocupación predeterminado de
250 ms. Las escrituras empiezan explícitamente una transacción, validan o leen,
aplican una mutación completa y después confirman. Una excepción de base de
datos ejecuta una reversión y se transforma en `RepositoryError` sin exponer
SQL, el texto del artículo pasado como parámetro ni una ruta completa.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/repositories.py check=learning:contract -->
```python source-ref
repository = SQLiteOrderRepository(database, busy_timeout_ms=250)
service = OrderService(repository)
service.create("ORD-001", "widget", 2)
```

Las pruebas compartidas de repositorio ejecutan el mismo contrato
add/get/list/advance contra memoria y SQLite. Un trigger controlado interrumpe
una actualización; la prueba observa `pending` después, elimina solo su propio
trigger y entonces avanza correctamente. Otra prueba mantiene un bloqueo
temporal explícito durante más de 50 ms, observa un fallo acotado, lo libera y
lo reintenta.

### Contrato de la CLI

La orden instalada admite:

```bash illustrative
order-tracker --database path/to/disposable/orders.sqlite3 add ORD-001 widget 2
order-tracker --database path/to/disposable/orders.sqlite3 advance ORD-001
order-tracker --database path/to/disposable/orders.sqlite3 list
```

La salida estable cuando hay éxito es JSON compacto:

```text illustrative
{"order_id":"ORD-001","status":"pending"}
```

Listar un pedido pendiente produce:

```text illustrative
{"item":"widget","order_id":"ORD-001","quantity":2,"status":"pending"}
```

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/cli.py check=learning:contract -->
```python source-ref
configured = args.database if args.database is not None else environment.get("ORDER_TRACKER_DB")
```

El código de salida forma parte de la interfaz:

- `0`: la orden se completó;
- `1`: el dominio o el repositorio rechazó la operación;
- `2`: los argumentos o la configuración de la base de datos no se pueden usar.

Sin configuración, stderr explica cómo recuperarse y no se crea ninguna base de
datos. Una cantidad no entera en la CLI es un error de uso (2); un entero fuera
del dominio es un error de dominio (1). Una invocación válida posterior contra
la misma base de datos seleccionada funciona.

### Privacidad del logging

`--verbose` añade un evento acotado a stderr. Una creación correcta se ve así:

```text illustrative
event=add order_id=ORD-LOG outcome=success
```

Los eventos pueden contener la fase, un identificador estable de pedido, el
recuento, el resultado y una categoría estable. Nunca contienen el texto del
artículo, una ruta completa de la base de datos, valores del entorno, SQL con
datos, secretos ni detalles del traceback de un error esperado. Stdout no
cambia, para que los scripts puedan analizarlo.

### TODO práctico guiado

Añade una prueba de subproceso, no una llamada a un auxiliar privado de la CLI:

```python todo
# TODO 1: invoke the CLI to create ORD-RECOVER in a temporary database.
# TODO 2: invoke the same add again and assert exit 1 plus duplicate-order.
# TODO 3: invoke list and prove the original item/quantity remain.
# TODO 4: retry with ORD-RECOVER-2 and assert exit 0.
```

**Pista:** comprueba el código de retorno, stdout, stderr y el estado de la base
de datos. Acota el tiempo de espera del subproceso y la salida capturada. Usa
solo un `TemporaryDirectory` y valores sintéticos.

### Evidencia práctica y solución explicada

Ejecuta:

```bash illustrative
cd chapter-28-professional-capstone/examples/order-tracker
python -B -m unittest \
  tests.test_repository_contract tests.test_cli tests.test_metadata -v
```

La solución explicada invoca `python -m order_tracker` desde un directorio de
trabajo temporal externo con solo el directorio `src` del proyecto
complementario en la ruta de importación usada por las pruebas de fuentes. No
elude `argparse`. La misma categoría de dominio o repositorio que expone el
servicio rechaza la inserción duplicada. Un `list` final demuestra que la fila
original sobrevivió; un identificador nuevo demuestra la recuperación.

### Errores prácticos comunes

- Elegir una base de datos predeterminada oculta hace que una orden inocente
  modifique el árbol de trabajo.
- Imprimir una ruta completa de base de datos o el artículo en los logs
  convierte los diagnósticos en una filtración de datos.
- Probar solo `cli.main` puede pasar por alto el análisis de la entrada, los
  flujos, el código de salida y problemas del directorio de trabajo externo.
- Capturar `sqlite3.Error` en la CLI filtra detalles de persistencia y duplica
  la responsabilidad del repositorio.
- Eliminar una base de datos bloqueada o dañada como «recuperación» puede
  destruir datos ajenos; corrige la ruta desechable o libera solo el bloqueo
  que posee tu prueba.

### Punto de control práctico y rúbrica

Suma un punto por cada elemento:

- **Contrato de repositorio:** memoria y SQLite producen el mismo ciclo de vida
  y los mismos errores observables.
- **Atomicidad:** una actualización controlada que falla conserva la fila
  anterior y una transacción limpia posterior funciona.
- **CLI/configuración:** la precedencia, JSON, la separación de flujos y los
  códigos de salida 0/1/2 coinciden con el contrato.
- **Privacidad del logging:** los eventos contienen la fase y el resultado,
  pero ninguno de los valores prohibidos.
- **Pruebas/recuperación:** las pruebas de subprocesos cubren comportamientos
  normales, límite, inválidos y de reintento sin dejar residuos.
- **Explicación:** quien aprende puede explicar dónde se confirma la transacción
  y por qué gana `--database`.

La etapa práctica se completa con los seis puntos. El trabajo opcional de
sistemas o empaquetado no puede compensar un cero aquí. Este es un punto de
parada profesional seguro.

### Reflexión práctica

¿Por qué «el mismo servicio, otro repositorio» aporta una evidencia más sólida
que escribir desde cero una segunda aplicación específica para SQLite?

---

## Etapa 3 · Extensión de sistemas opcional: adaptador loopback acotado

### Objetivo de sistemas y límites exactos

Este adaptador opcional enseña el ciclo de vida, no el despliegue en Internet.
Usa JSON UTF-8 delimitado por saltos de línea, una petición por conexión,
`127.0.0.1` y un puerto asignado por el sistema operativo.

Los límites predeterminados son:

- bytes de petición: 1024, incluido el salto de línea;
- bytes de respuesta: 4096, incluido el salto de línea;
- total de peticiones aceptadas: 8;
- manejadores activos simultáneos: 4;
- pedidos devueltos por una respuesta de lista: 20; y
- plazo de lectura o escritura inactivas: 0,5 segundos.

La validación del constructor permite tamaños de petición de 1 a 65 536 bytes,
tamaños de respuesta de 38 a 65 536 bytes, recuentos de peticiones o listas de
1 a 100, concurrencia de 1 a 32 y plazos de 0,05 a 10 segundos. El mínimo de
38 bytes es la trama completa del error `response-limit`, así que incluso ese
mensaje de recuperación respeta el límite elegido. El adaptador no conserva un
historial de peticiones ni una cola de salida sin acotar. Una conexión admitida
después de superar el control de concurrencia consume una plaza del total de
peticiones, aunque su trama esté después mal formada o supere el tiempo de
espera; un cliente rechazado como `busy` no consume ninguna.

### Predice el enmarcado y la capacidad

Predice qué ocurre cuando un cliente:

1. envía JSON válido por debajo de 1024 bytes;
2. envía 1025 bytes antes de un salto de línea;
3. abre el único manejador permitido y se queda bloqueado;
4. envía UTF-8 o JSON mal formado; o
5. solicita una novena petición.

Los errores estables son, respectivamente: éxito; `request-too-large`; `busy`
para el cliente concurrente, seguido de recuperación de capacidad;
`malformed-request`; y `request-limit`, seguido de un cierre limpio.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/loopback.py check=learning:contract -->
```python source-ref
async with LoopbackOrderServer(service) as server:
    response = await send_request(server.address, {"action": "list"})
```

Una petición válida es:

```json illustrative
{"action":"add","order_id":"NET-1","item":"widget","quantity":2}
```

La respuesta acotada es:

```json illustrative
{"ok":true,"order":{"item":"widget","order_id":"NET-1","quantity":2,"status":"pending"}}
```

### TODO guiado de sistemas

Amplía la prueba temporal, no un servicio público:

```python todo
# TODO 1: start with max_concurrency=1 and an ephemeral port.
# TODO 2: open one client and wait on connection_started without sleeping.
# TODO 3: prove a second client receives busy.
# TODO 4: finish/close the first client, await capacity_available, and retry.
# TODO 5: close the server and assert zero active connections/tasks.
```

**Pista:** la disponibilidad inicial y la recuperación son eventos. Una espera
fija no puede demostrar ninguna de las dos. Cierra siempre el escritor del
cliente en un bloque `finally`.

### Fallos, recuperación, cancelación y solución

La batería de pruebas cubre los límites del constructor, una petición en el
límite exacto de bytes, operaciones válidas de añadir/listar, entrada mal
formada, entrada demasiado grande, límites de lista/respuesta, un manejador
ocupado, el plazo de inactividad, el agotamiento del total de peticiones, la
cancelación de un manejador bloqueado, la recuperación de capacidad y el cierre
del escuchador. El servidor cierra el escuchador, cancela y espera todos los
manejadores que posee y después completa `wait_closed()`. `CancelledError`
vuelve a propagarse después de cerrar cada escritor.

Ejecuta solo la evidencia opcional:

```bash illustrative
cd chapter-28-professional-capstone/examples/order-tracker
python -B -m unittest tests.test_loopback -v
```

La solución explicada nunca se enlaza a `0.0.0.0`, nunca elige un puerto fijo,
nunca contacta con un destino público, nunca desactiva una comprobación de
seguridad y nunca afirma ofrecer TLS, autenticación o endurecimiento para
producción. Aplica límites de bytes/estado antes de conservar datos y demuestra
una petición posterior o un cierre limpio tras el rechazo.

### Errores frecuentes de sistemas

- No está garantizado que una escritura TCP corresponda a una lectura; el salto
  de línea es el límite de trama declarado.
- Una espera fija no constituye evidencia de que el servidor esté listo ni de
  que haya limpiado sus recursos.
- Loopback evita el enrutamiento público, pero no todas las preocupaciones de
  seguridad de la aplicación.
- Cancelar tareas sin esperarlas puede dejar sockets abiertos y advertencias.
- Un adaptador opcional no debe convertirse en un prerrequisito de importación o
  empaquetado.

### Punto de control y rúbrica de sistemas

Asigna un punto por **enlace loopback/puerto efímero**, **enmarcado y límites de
bytes**, **límites de peticiones/concurrencia**, **recuperación de
plazo/capacidad**, **cancelación/cierre** y **explicar por qué esto no es
producción**. Los seis puntos completan la etapa opcional de sistemas. En caso
contrario, conserva el resultado de la etapa práctica e informa de que la
evidencia de sistemas está incompleta.

### Reflexión de sistemas

¿Qué recurso acota cada número y qué aserción demuestra que la capacidad se
recupera?

---

## Etapa 4 · Empaquetado hero opcional: verifica el artefacto, no el checkout

### Objetivo de empaquetado y límite de la evidencia

Que las pruebas de fuente pasen demuestra el checkout. No demuestra que un
sdist contenga todas las fuentes, que una wheel tenga metadatos correctos, que
la instalación funcione ni que la importación se resuelva fuera del
repositorio. La etapa hero comprueba esas afirmaciones por separado.

La distribución es `course-order-tracker`, el paquete importable
`order_tracker`, el comando `order-tracker`, la versión `1.0.0`,
`Requires-Python >=3.11` y no tiene dependencias de ejecución. Su wheel declara
`py3-none-any`. Esa etiqueta es una declaración de compatibilidad, no una
prueba para hosts que no se hayan ejecutado.

### Las entradas de construcción son pines directos, no un lock

`requirements-build.txt` registra `build==1.3.0`,
`setuptools==80.9.0` y `wheel==0.45.1` como pines directos exactos para este
flujo de trabajo. No incluye hashes, procedencia del resolutor, matriz
multiplataforma ni instantánea transitiva del índice, así que no se denomina un
lock completo.

El [registro de entradas de construcción](examples/order-tracker/BUILD_INPUTS.md)
registra por separado los nombres de archivo de las versiones seleccionadas,
los valores SHA-256 observados en PyPI, los metadatos de licencia publicados y
las referencias primarias de los formatos. El verificador comprueba los hashes
de las dos wheels de backend offline. Esta observación de procedencia sigue sin
ser un grafo de dependencias resuelto ni una aprobación humana de
licencia/publicación.

La adquisición inicial de herramientas es un paso de mantenimiento separado y
deliberado que puede necesitar una red o un índice aprobados. El verificador
nunca la realiza. Antes de ejecutar el comando aceptado, el host debe ofrecer
grupos de procesos POSIX para la limpieza acotada del árbol de procesos hijos,
`build==1.3.0` ya debe poder importarse y `ORDER_TRACKER_WHEELHOUSE` debe
designar un directorio offline dedicado que contenga únicamente los artefactos
exactos de setuptools y wheel registrados. Una entrada ausente, adicional o
que no coincida es un estado de prerrequisito no superado.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/tools/verify_artifact.py check=learning:contract -->
```python source-ref
wheelhouse = require_prerequisites()
verify(wheelhouse)
```

Desde la raíz del repositorio, el comando aceptado es:

```bash illustrative
python -B chapter-28-professional-capstone/examples/order-tracker/tools/verify_artifact.py
```

En este checkout, si las herramientas no están preparadas, el resultado veraz
es distinto de cero y comienza así:

```text illustrative
prerequisite missing:
```

Eso no es una superación de la prueba del artefacto y no invalida la etapa
práctica de fuentes ya completada.

### Fases de verificación

El verificador:

1. calcula las huellas y examina el árbol de fuentes;
2. lo copia a una raíz de fuentes temporal independiente;
3. ejecuta construcciones PEP 517 aisladas y offline desde el wheelhouse
   declarado;
4. inspecciona el sdist exacto y la wheel pura inicial;
5. desempaqueta de forma segura el sdist en una segunda raíz de fuentes;
6. vuelve a construir una wheel desde esa fuente distribuida;
7. comprueba metadatos, miembros obligatorios, `RECORD`, licencia, ausencia de
   dependencias de ejecución y `py3-none-any`;
8. instala la wheel reconstruida exacta con `--no-index --no-deps` en un
   entorno nuevo;
9. ejecuta `pip check` y pruebas de humo de metadatos/importación/dominio/CLI
   desde un directorio ajeno;
10. informa de nombres de archivo y observaciones SHA-256 junto con las
    versiones ejecutadas; y
11. elimina todas las raíces temporales de fuente, salida, instalación, caché,
    base de datos y directorio ajeno, tanto si hay éxito como si hay fallo.

Rechaza un miembro individual de fuente/archivo superior a 2 MiB, una
instantánea del proyecto superior a 8 MiB, un archivo superior a 12 MiB
comprimido o expandido, una salida combinada de procesos hijos superior a
16 KiB, una fase inicial/de reconstrucción/instalación superior a 180 segundos
o cualquier otra fase hija superior a 30 segundos. Un host que no sea POSIX
informa de un estado de prerrequisito; este curso no lo sustituye por una
afirmación más débil sobre la limpieza de procesos.

SHA-256 demuestra qué bytes se observaron en esa ejecución. No constituye una
afirmación de construcción reproducible byte a byte.

### TODO guiado de empaquetado

Antes de ejecutar, completa este plan de evidencia:

```text todo
TODO 1: name the source input and the two independently built wheels.
TODO 2: predict where order_tracker.__file__ must resolve after clean install.
TODO 3: name the phase that should reject a database or .env inside an archive.
TODO 4: record the exact interpreter/host actually executed.
TODO 5: state why no command in the plan uploads an artifact.
```

**Pista:** «las pruebas pasaron» no basta. Registra por separado la
construcción, inspección, reconstrucción, instalación, importación,
comportamiento, CLI y limpieza. Un prerrequisito ausente sigue ausente.

### Fallos y recuperación de empaquetado

- Frontend/wheelhouse ausente: prepara explícitamente las entradas exactas; no
  desactives el aislamiento ni permitas un fallback implícito al índice.
- Miembro ausente del sdist: corrige `MANIFEST.in`/los metadatos, descarta todos
  los artefactos temporales y vuelve a construir desde el principio.
- Fuga de importación desde el árbol de fuentes: cambia al intérprete nuevo y
  al directorio de trabajo ajeno; no añadas el checkout a `PYTHONPATH`.
- Base de datos/caché/credencial prohibida: elimina la causa en las fuentes y
  repite la inspección antes de instalar.
- Fallo de la prueba de humo de la CLI: corrige el paquete/punto de entrada y
  vuelve a ejecutar todas las fases posteriores, no solo el comando final.

La verificación termina localmente. La publicación requiere autorización,
credenciales, revisión, política de firma/atestación y controles del índice
independientes que este capítulo ni solicita ni ejercita.

### Errores frecuentes de empaquetado

- Llamar lock universal a los pines directos exagera su evidencia.
- Tratar el nombre de una wheel como prueba de ejecución exagera la
  compatibilidad.
- Instalar desde el checkout permite que pase inadvertido un archivo ausente
  del paquete.
- Reutilizar una construcción/caché anterior invalida la evidencia de una
  construcción limpia.
- Informar de una herramienta de construcción ausente como «omitida/superada»
  inventa un éxito.
- Añadir un comando de subida amplía la autoridad más allá de este proyecto
  final.

### Punto de control y rúbrica de empaquetado

Si se selecciona, asigna un punto por **construcción aislada**, **inspección del
sdist**, **wheel reconstruida desde el sdist**, **instalación limpia y
`pip check`**, **evidencia de metadatos/importación/dominio/CLI desde un
directorio ajeno**, **registro de digest/toolchain**, **limpieza** y
**explicación de que no se publica**. Los ocho puntos completan la etapa hero.
Si alguno no está disponible, informa de la fase exacta no superada y conserva
la etapa práctica completada de forma independiente.

### Reflexión de empaquetado

¿Qué defecto pueden ocultar las pruebas de fuente pero revelar una wheel
reconstruida desde el sdist?

---

## Evaluación final de las etapas seleccionadas

Para cada etapa seleccionada, ninguna categoría obligatoria puede puntuar cero:

- **Corrección del dominio:** los valores y las transiciones coinciden con el
  contrato exacto.
- **Separación de responsabilidades:** los adaptadores no son propietarios de
  las reglas del dominio/SQLite.
- **Atomicidad de la persistencia:** un rechazo conserva el estado confirmado.
- **CLI/configuración:** la precedencia, JSON, streams y códigos de salida son
  estables.
- **Privacidad del logging:** los diagnósticos no revelan artículos, rutas,
  entorno, datos SQL, credenciales ni tracebacks de errores esperados.
- **Pruebas y recuperación:** el comportamiento normal, límite, inválido y
  reparado es observable.
- **Ciclo de vida de sistemas, si se selecciona:** los límites, la cancelación y
  la limpieza se superan.
- **Evidencia del artefacto, si se selecciona:** las fases desde fuentes hasta
  la instalación se superan localmente.
- **Explicación:** el estudiante puede justificar una decisión de diseño y un
  límite de recuperación.

Los puntos opcionales no pueden ocultar un fallo de fundamentos o de la etapa
práctica. Una herramienta que da resultado positivo sin una explicación deja
incompleta esa categoría de la rúbrica.

## Trazabilidad y verificación completas

La [trazabilidad del capítulo 28](TRACEABILITY.md) relaciona cada funcionalidad
con la enseñanza previa, la sección para el estudiante, el código fuente
complementario, la prueba exacta y el elemento de la rúbrica. La [guía de
verificación](examples/order-tracker/README.md) complementaria registra los
comandos y el límite de prerrequisitos del artefacto.

## Comprobación de higiene del repositorio

Después de verificar, inspecciona incluso las rutas ignoradas dentro del
capítulo. No debe quedar ningún entorno virtual, `build/`, `dist/`, wheel,
sdist, base de datos SQLite, `*.egg-info`, caché, bytecode, cobertura,
credencial, datos del estudiante, socket activo ni proceso hijo. Todo el estado
generado debe vivir en raíces temporales.

## Fuentes, originalidad y límite de revisión humana

La prosa del capítulo, los escenarios ficticios de pedidos, los TODO, las
pruebas y el código complementario se escribieron como material original del
curso. El comportamiento técnico se contrastó con la documentación oficial de
Python para [`dataclasses`](https://docs.python.org/3/library/dataclasses.html),
[`sqlite3`](https://docs.python.org/3/library/sqlite3.html),
[`argparse`](https://docs.python.org/3/library/argparse.html) y los
[streams de `asyncio`](https://docs.python.org/3/library/asyncio-stream.html),
además de las referencias primarias de empaquetado enumeradas en el registro
complementario de entradas de construcción. No se presenta ninguna prosa ni
ejercicio como copia de esas referencias.

Esa declaración y las pruebas/estructura automatizadas no aprueban la
procedencia, las obligaciones de licencia, la calidad de las traducciones, la
accesibilidad renderizada, el bidi árabe ni la publicación. Todo ello continúa
siendo un conjunto de puertas explícitas que debe revisar personal competente.

## Reflexión final

El proyecto final está completo en la etapa elegida cuando coinciden el
comportamiento, la recuperación, la limpieza y tu explicación. ¿Qué límite
—dominio inmutable, transacción, adaptador o artefacto— te aportó la evidencia
nueva más sólida y qué verificarías después antes de una publicación real?
