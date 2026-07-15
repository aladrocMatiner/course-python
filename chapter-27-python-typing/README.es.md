# Capítulo 27 · Tipado gradual y análisis estático

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir

Python permite añadir información de tipos de forma gradual. Hoy puedes anotar
una frontera útil sin reescribir todo el programa. Las anotaciones ayudan a una
persona, un editor o un comprobador estático a razonar sobre los valores antes
de ejecutar. No inspeccionan ni rechazan valores automáticamente durante la
ejecución.

Haremos crecer un ejemplo pequeño de inventario sintético en tres etapas
tranquilas:

1. **Esencial:** anotar funciones y colecciones, representar la ausencia con
   `None`, estrechar una unión y mantener explícita la validación en tiempo de
   ejecución.
2. **Profesional:** dar forma a registros de diccionario con `TypedDict`,
   aceptar comportamiento estructuralmente con `Protocol`, pasar funciones
   invocables tipadas, conservar un tipo de resultado genérico y usar `Self`
   para un método fluido.
3. **Ruta opcional del comprobador:** comparar un consumidor válido con otro
   deliberadamente no válido, reconocer categorías de error estables, reparar
   el contrato y ejecutar un verificador acotado cuando la versión exacta
   fijada del comprobador ya esté preparada.

La autoridad ejecutable es
[`examples/typed_inventory.py`](examples/typed_inventory.py). Las pruebas de
ejecución y los fixtures del comprobador usan únicamente SKU y cantidades
sintéticos. No usan red, base de datos, credenciales, registros personales,
índices de paquetes ni archivos de quien aprende.

## Objetivos de aprendizaje

Al finalizar la ruta que elijas, podrás:

- **O1 — Leer y escribir anotaciones:** anotar parámetros, valores de retorno y
  colecciones concretas sin afirmar que las anotaciones ejecutan validación.
- **O2 — Modelar la ausencia:** usar `T | None`, conservar valores válidos que
  se evalúan como falsos, como la cantidad `0`, y estrechar la ausencia con
  `is None`.
- **O3 — Validar una frontera en tiempo de ejecución:** aceptar un `object`,
  comprobar su tipo real y sus límites de dominio, rechazar `bool` cuando se
  necesita exactamente un entero y recuperarse sin una mutación parcial.
- **O4 — Describir la forma de un registro:** usar `TypedDict` para las claves
  estables y los tipos de valor de un diccionario que ya está dentro del núcleo
  tipado.
- **O5 — Tipar comportamiento y algoritmos reutilizables:** usar `Callable`,
  `Protocol` estructural, `TypeVar` y `Self` donde cada herramienta aclare un
  contrato real.
- **O6 — Leer con honestidad la evidencia estática:** separar los diagnósticos
  del comprobador de las excepciones de Python, apoyarse en categorías estables
  en lugar del texto completo y corregir un consumidor no válido hasta obtener
  un resultado limpio.
- **O7 — Explicar la frontera de la evidencia:** indicar qué hacen las pruebas
  de ejecución, un comprobador y la revisión humana, y qué no demuestra ninguno
  de ellos por sí solo.

El [registro de trazabilidad](TRACEABILITY.md) relaciona estos objetivos con la
explicación, la práctica, las soluciones, las referencias a fuentes, las
pruebas y los checkpoints.

## Prerrequisitos y mapa de rutas

Antes de empezar, completa los checkpoints fundamentales de:

- [Capítulo 11: Funciones](../chapter-11-functions/README.es.md), para
  parámetros, valores de retorno y `None`;
- [Capítulo 15: Módulos](../chapter-15-modulos/README.es.md), para imports y
  fronteras públicas de módulos;
- [Capítulo 18: Pruebas](../chapter-18-testing/README.es.md), para contratos
  normales y de fallo observables; y
- [Capítulo 22: Introspección](../chapter-22-introspection/README.es.md), para
  distinguir el comportamiento de un objeto en tiempo de ejecución de la
  información que inspeccionan las herramientas.

Su posición numérica después del capítulo 26 no convierte las redes, C++ ni
Rust en prerrequisitos.

- **Ruta esencial · 2 sesiones de 45–60 minutos.** Lee E1–E4, completa el reto
  esencial y evalúalo con su rúbrica. Resultado: una búsqueda tipada más una
  frontera de entero validada explícitamente. Finalización: al menos 4/5 puntos,
  incluida la distinción entre lo estático y la ejecución, además de la
  recuperación de `None`. Punto seguro donde parar: usa estas anotaciones en
  Python ordinario y continúa sin instalar un comprobador.
- **Ruta profesional · 2 sesiones de 50–70 minutos.** Completa el checkpoint
  esencial y después P1–P4 y el reto profesional. Resultado: ampliar el
  contrato de inventario probado con filas tipadas, una búsqueda genérica, una
  fuente estructural de precios y llamadas fluidas que conservan la subclase.
  Finalización: al menos 5/6 puntos, incluida la conservación de la frontera en
  tiempo de ejecución. Punto seguro donde parar: puedes consumir interfaces de
  bibliotecas tipadas sin recorrer la ruta opcional del comprobador.
- **Ruta opcional del comprobador · 1 sesión de 45–60 minutos.** Completa el
  checkpoint profesional y usa un entorno aislado donde la versión exacta
  fijada de la herramienta directa ya se haya instalado deliberadamente.
  Resultado: explicar tres categorías de diagnóstico, observar un caso de prueba que debe
  terminar con código distinto de cero y demostrar que su versión corregida
  queda limpia. Finalización: la ejecución pasa, el caso positivo pasa, el
  negativo falla por todas las categorías declaradas, el corregido pasa y la
  limpieza pasa. Un comprobador ausente o de otra versión produce el resultado
  «falta el prerrequisito»: no es un checkpoint fallido, y nunca es un aprobado.

¿Vuelves al tema con experiencia previa? Explica por qué
`def echo(value: str) -> str:` no impide que una llamada en tiempo de ejecución
reciba `7`. Después explica por qué `if value is None` conserva un `0` válido.
Si ambas ideas están claras, empieza por la ruta profesional. Si además puedes
explicar el subtipado estructural y por qué `list[Dog]` no es automáticamente
un `list[Animal]`, usa el checkpoint profesional como revisión rápida antes de
la ruta opcional del comprobador.

## Un pequeño glosario

- **Anotación:** información de tipos vinculada a un nombre, parámetro o
  posición de retorno. Son metadatos; Python no los convierte por defecto en un
  validador.
- **Comprobador estático:** herramienta separada que analiza el código fuente
  sin usar cada valor de una ejecución real.
- **Validación en tiempo de ejecución:** comprobaciones ejecutables como
  `isinstance`, comprobaciones de tipo exacto, comprobaciones de rango y
  excepciones explícitas.
- **Unión:** valor que puede tener uno entre varios tipos declarados.
  `int | None` significa un entero o ausencia.
- **Estrechamiento:** evidencia que permite a un comprobador y a quien lee
  reducir una unión dentro de una rama, como `value is None`.
- **Tipado estructural:** aceptar un objeto porque tiene la forma de método
  necesaria, no porque herede de una clase base concreta.
- **Genérico:** código cuya relación entre entrada y salida se expresa con una
  variable de tipo en lugar de un tipo de datos fijo.
- **Vía de escape:** `Any`, `cast` o una instrucción para ignorar que pide al
  comprobador confiar en código que no puede demostrar. Las vías de escape
  requieren una frontera estrecha y explicada.

El flujo completo, expresado en prosa, es el siguiente: una persona desarrolla
el código fuente y sus anotaciones; un comprobador puede analizar esas
anotaciones antes de una ejecución; el intérprete ejecuta el código; las
comprobaciones explícitas inspeccionan valores reales en las fronteras; las
pruebas observan ejecuciones seleccionadas. No hace falta ninguna flecha, color
ni posición en un diagrama para distinguir esas cuatro responsabilidades.

## Ruta esencial: información útil sin promesas falsas de validación

### E1. Anota una función que ya entiendas

Objetivo: comunicar el tipo de cada entrada y del resultado devuelto sin
alterar el comportamiento conocido de la función.

Lee esta firma de izquierda a derecha: se espera que `sku` sea una cadena,
`stock` asocia cadenas con enteros y la función devuelve un entero o `None`.
Antes de ejecutarla, predice ambas líneas. En particular, decide si una cantidad
almacenada de `0` significa «ausente».

```python runnable
def find_quantity(sku: str, stock: dict[str, int]) -> int | None:
    return stock.get(sku)


quantities = {"PART-7": 0, "PART-8": 4}
print(find_quantity("PART-7", quantities))
print(find_quantity("UNKNOWN", quantities))
```

```text output
0
None
```

La anotación no cambia `dict.get`. El comportamiento en tiempo de ejecución
sigue procediendo del cuerpo de la función. La anotación de retorno hace
visibles los dos resultados antes de que alguien tenga que leer todos los
lugares donde se llama a la función.

Las colecciones tipadas describen sus elementos:

- `list[str]` es una lista cuyos valores son cadenas;
- `dict[str, int]` asocia claves de cadena con valores enteros; y
- `tuple[str, int]` es una tupla de dos posiciones, primero una cadena y después
  un entero.

Prefiere el tipo concreto que exprese la operación real. No añadas un tipo solo
porque parezca más avanzado.

**Modifica — TODO O1:** Añade anotaciones de parámetro y retorno sin cambiar el
cuerpo ni la salida.

```python todo
def total_units(quantities):
    return sum(quantities)


print(total_units([2, 3, 5]))
```

**Pista:** la entrada es una lista concreta de enteros y `sum` devuelve un
entero en este dominio. Empieza con `list[int]`; la profundidad sobre iterables
genéricos pertenece a la ruta profesional.

**Solución explicada:** `def total_units(quantities: list[int]) -> int:` cuenta
la verdad sobre la colección que acepta este ejercicio. El cuerpo sigue siendo
`return sum(quantities)`, así que la salida continúa siendo `10`. Una anotación
es especialmente útil cuando conserva y aclara un contrato ya elegido.

### E2. Estrecha `None` sin perder un cero válido

Objetivo: distinguir la ausencia de un valor presente que se evalúa como falso.

Cuando un valor tiene el tipo `int | None`, comprueba primero `is None`. En la
otra rama, el valor se ha estrechado a `int`. Predice la salida para `0` y
`None`:

```python runnable
def quantity_label(quantity: int | None) -> str:
    if quantity is None:
        return "unknown"
    return f"{quantity} units"


print(quantity_label(0))
print(quantity_label(None))
```

```text output
0 units
unknown
```

La tentadora forma `if not quantity:` mezclaría `0` con la ausencia y cambiaría
el contrato del inventario. La verdad lógica puede ser útil, pero no sustituye
una decisión explícita sobre la ausencia.

**Caso límite:** una colección vacía, una cadena vacía, `False` y `0` se
consideran falsos en contextos booleanos, pero ninguno es el centinela `None`.
Plantea «¿está ausente?» y «¿está vacío o vale cero?» como preguntas de dominio
separadas.

### E3. Observa que las anotaciones no ejecutan validación

Objetivo: separar metadatos, operaciones y validación explícita.

Esta función declara cadenas, pero su cuerpo se limita a devolver el objeto que
recibe. Python almacena las anotaciones y ejecuta el cuerpo; no añade una
comprobación de tipos oculta. Predice qué imprime esta llamada deliberadamente
incorrecta:

```python runnable
def echo_label(label: str) -> str:
    return label


print(echo_label(7))
```

```text output
7
```

Que el proceso termine correctamente **no** demuestra que la llamada respete
el contrato declarado. Un comprobador estático puede informar de la
incompatibilidad. La ejecución también puede fallar más adelante cuando una
operación necesite el comportamiento prometido:

<!-- bookcheck: expect-error=TypeError timeout=5 -->
```python expected-error
def add_one(quantity: int) -> int:
    return quantity + 1


print(add_one("2"))
```

La señal estable es `TypeError`; el texto completo del traceback puede cambiar.
El fallo procede de intentar sumar una cadena y un entero, no de la anotación.

**Recuperación:** proporciona a la función un entero real. Este caso vecino
correcto demuestra que la corrección alcanza la operación prevista:

```python runnable
def add_one(quantity: int) -> int:
    return quantity + 1


print(add_one(2))
```

```text output
3
```

Error frecuente: afirmar que «Python comprobó el tipo» porque un valor
incorrecto provocó una excepción. La operación rechazó ese valor concreto. Otro
cuerpo podría aceptarlo por accidente, como hizo `echo_label`.

### E4. Valida la frontera y después confía en el núcleo tipado

Objetivo: convertir un valor desconocido en tiempo de ejecución en un entero
validado o en un error claro del que sea posible recuperarse.

En la frontera de un archivo, comando, HTTP o mapeo con una forma poco
definida, el tipo de entrada honesto puede ser `object`. Comprueba primero el
tipo durante la ejecución y después el rango del dominio. Aquí usamos
deliberadamente una comprobación de tipo exacto porque `bool` es una subclase de
`int`, mientras que una cantidad de inventario no debe aceptar `True` como una
unidad.

```python runnable
def parse_quantity(value: object) -> int:
    if type(value) is not int:
        raise TypeError("quantity must be a built-in int, not bool")
    if not 0 <= value <= 1_000_000:
        raise ValueError("quantity must be between 0 and 1000000")
    return value


print(parse_quantity(0))
print(parse_quantity(1_000_000))
```

```text output
0
1000000
```

Predice la categoría de la excepción antes de ejecutar este fallo en la
frontera:

<!-- bookcheck: expect-error=TypeError timeout=5 -->
```python expected-error
def parse_quantity(value: object) -> int:
    if type(value) is not int:
        raise TypeError("quantity must be a built-in int, not bool")
    if not 0 <= value <= 1_000_000:
        raise ValueError("quantity must be between 0 and 1000000")
    return value


print(parse_quantity(True))
```

**Recuperación:** sustituye `True` por el entero previsto, vuelve a ejecutar y
mantén sin cambios el valor externo original hasta que la validación termine
correctamente. La validación debe ocurrir antes de añadir el valor a una
colección o actualizar cualquier otro estado.

### Reto esencial guiado

Construye `reorder_message`. Recibe el resultado opcional de `find_quantity` y
debe distinguir entre un valor desconocido, cero y una cantidad positiva.

```python todo
def reorder_message(quantity: int | None) -> str:
    # TODO 1: return "unknown SKU" only for None
    # TODO 2: return "reorder now" for zero
    # TODO 3: otherwise return "stock: N"
    ...


print(reorder_message(None))
print(reorder_message(0))
print(reorder_message(4))
```

**Pista:** estrecha primero con `is None`. Después de esa rama, `quantity` es
un entero, así que compáralo con `0`.

**Solución explicada:** el orden de las preguntas conserva el dominio. Primero
pregunta si el valor está ausente y después si el entero presente es cero.

```python runnable
def reorder_message(quantity: int | None) -> str:
    if quantity is None:
        return "unknown SKU"
    if quantity == 0:
        return "reorder now"
    return f"stock: {quantity}"


print(reorder_message(None))
print(reorder_message(0))
print(reorder_message(4))
```

```text output
unknown SKU
reorder now
stock: 4
```

### Checkpoint y rúbrica esenciales

Suma 0 o 1 punto por cada criterio:

1. **Corrección:** los casos normal, cero y ausente producen el resultado
   indicado.
2. **Claridad de las anotaciones:** los parámetros y retornos expresan el
   contrato real.
3. **Frontera en tiempo de ejecución:** un `bool` no válido, un tipo incorrecto
   y los valores fuera del rango se rechazan antes de mutar nada.
4. **Recuperación:** puedes explicar y demostrar una nueva ejecución corregida.
5. **Explicación:** puedes contar por qué una anotación, un comprobador, una
   operación y la validación explícita son cosas diferentes.

Para completar la ruta necesitas al menos 4/5 y debes incluir los puntos 3 y 5.
Puedes detenerte aquí: ya puedes añadir anotaciones útiles sin instalar ninguna
herramienta de terceros. Reflexión: ¿qué frontera de uno de tus programas recibe
valores que las anotaciones por sí solas no pueden hacer seguros?

## Ruta profesional: forma, comportamiento y relaciones

### P1. Proporciona una forma estable a los registros de diccionario con `TypedDict`

Objetivo: describir claves conocidas sin olvidar que el objeto en tiempo de
ejecución sigue siendo un diccionario ordinario.

El registro normalizado del companion tiene exactamente los dos campos que usa
esta lección:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
class InventoryRow(TypedDict):
    """A normalized inventory record used inside the typed core."""

    sku: str
    quantity: int
```

`TypedDict` ayuda a las herramientas estáticas a comprobar nombres y valores de
campos. No envuelve el diccionario ni rechaza un mapeo incorrecto durante la
ejecución. La frontera explícita sigue siendo `parse_row`:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
def parse_row(raw: Mapping[str, object]) -> InventoryRow:
    """Validate and normalize one untrusted mapping without mutating it.

    ``sku`` must be a string whose stripped form contains 1 through 32
    characters.  ``quantity`` must be a built-in ``int`` (never ``bool``) in
    the inclusive range 0 through 1,000,000.
    """
```

El contrato probado elimina los espacios exteriores de un SKU y lo convierte a
mayúsculas; acepta de 1 a 32 caracteres normalizados y una cantidad cuyo tipo
sea exactamente entero entre 0 y 1 000 000. Los campos ausentes o con tipos
incorrectos lanzan `TypeError`; los SKU vacíos o demasiado largos y las
cantidades fuera de rango lanzan `ValueError`. El mapeo de entrada permanece
sin cambios en todos los casos.

Ejecuta la evidencia de la biblioteca estándar desde la raíz del repositorio:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --runtime
```

La entrada válida `{"sku": "  part-7 ", "quantity": 0}` se convierte en
`{"sku": "PART-7", "quantity": 0}`. Se acepta el límite superior: 32
caracteres y 1 000 000 de unidades. Un SKU de 33 caracteres, `-1`, `1_000_001`
o una cantidad booleana se rechazan antes de añadir ninguna fila al inventario.

**Modifica — TODO O3/O4:** añade una prueba en tiempo de ejecución para un
campo `quantity` ausente. Predice la categoría de la excepción y copia la
entrada antes de la llamada. **Pista:** en este contrato didáctico, un campo
obligatorio ausente es un error de forma/tipo. **Solución:** comprueba
`TypeError` y después que el mapeo siga siendo igual a la copia. No conviertas
el campo estático en opcional solo para silenciar un requisito real de la
frontera.

### P2. Expresa una relación de callback con `Callable` y `TypeVar`

Objetivo: conservar el tipo del elemento mientras se acepta una operación de
predicado.

`Callable[[T], bool]` se lee «un callable que recibe un `T` y devuelve un
booleano». El mismo `T` en el resultado indica que la función devuelve un
elemento del tipo de entrada o `None`:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
def first_matching(items: Iterable[T], predicate: Callable[[T], bool]) -> T | None:
    """Return the first matching item, or ``None`` after finite exhaustion."""

    for item in items:
        if predicate(item):
            return item
    return None
```

La función se detiene en la primera coincidencia. Una entrada finita vacía o
sin coincidencias devuelve `None`. Si la entrada es un iterador de un solo uso,
su posición queda después del elemento coincidente; el tipado no lo rebobina.

**Predice:** para los valores generados `1, 2, 3, 4` y el predicado
`value == 3`, ¿cuántas llamadas al predicado ocurren y qué devuelve el siguiente
`next` directo? Las pruebas observan tres llamadas al predicado y después el
valor `4`.

**Modifica — TODO O5:** usa `first_matching` para localizar la primera fila con
cantidad `0`. **Pista:** el parámetro del callback es un `InventoryRow`, así que
accede a `row["quantity"]`. La solución explicada devuelve
`InventoryRow | None`; estrecha con `is None` antes de leer `row["sku"]`.

Error frecuente: sustituir `T` por `object`. Eso perdería la relación útil entre
los elementos de entrada y la coincidencia devuelta. Una variable de tipo no
significa «cualquier valor sin comprobaciones»; conecta posiciones dentro de
una misma llamada.

### P3. Acepta comportamiento estructuralmente con `Protocol`

Objetivo: depender de la forma de un único método sin imponer herencia.

El inventario necesita una fuente que pueda conocer o no un precio:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
class PriceSource(Protocol):
    """Anything with this method shape can supply an optional unit price."""

    def unit_price(self, sku: str) -> float | None:
        """Return the unit price, or ``None`` when the SKU is unknown."""
```

Una clase no tiene que heredar de `PriceSource`. Si su método acepta `str` y
devuelve `float | None`, un comprobador estático puede aceptarla de forma
estructural:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_positive.py check=learning:contract -->
```python source-ref
class Catalogue:
    def unit_price(self, sku: str) -> float | None:
        return {"PART-7": 2.5}.get(sku)
```

Esta es una relación estática. El protocolo base no está marcado como
`runtime_checkable`; incluso una comprobación de forma durante la ejecución no
demostraría que todos los valores de retorno futuros respeten la anotación. Las
pruebas y la validación en la frontera siguen siendo responsables del
comportamiento en tiempo de ejecución.

**Caso límite:** el precio `0.0` está presente y no debe confundirse con
`None`. **Incompatibilidad recuperable:** si una implementación acepta SKU
`int` y devuelve `str`, corrige la firma y el comportamiento de su método
público; no añadas herencia ni `cast` solo para suprimir el diagnóstico del
comprobador.

### P4. Conserva el tipo de la instancia fluida con `Self`

Objetivo: indicar que un método fluido devuelve exactamente el tipo receptor,
incluidas sus subclases.

El companion valida y copia una fila antes de mutar, y después devuelve la
misma instancia:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
    def add(self, row: InventoryRow) -> Self:
        """Validate, copy, and append ``row``; return this exact instance."""

        normalized = parse_row(row)
        self._rows.append(normalized)
        return self
```

`Self` es más preciso que escribir `Inventory`: llamar al método heredado `add`
sobre un `LabelledInventory` conserva el tipo `LabelledInventory`. En tiempo de
ejecución, la prueba también demuestra la identidad con `is`; no se limita a
confiar en la anotación.

**Fallo y recuperación:** añadir una cantidad booleana lanza una excepción
antes de añadirla. La tupla anterior de filas permanece igual. Corrige la
entrada y vuelve a llamar a `add`; la misma instancia recibe una copia
normalizada. Mutar el diccionario original de la llamada o un diccionario
devuelto por `.rows` no modifica el estado almacenado.

### Reto profesional guiado

Crea una clase `WarehousePrices` con
`unit_price(sku: str) -> float | None`; después encuentra la primera fila cuya
cantidad sea cero y consulta su precio.

```python todo
from typing import assert_type

# TODO 1: implement WarehousePrices without inheriting PriceSource
# TODO 2: find the first zero-quantity InventoryRow
# TODO 3: narrow the optional row and optional price with `is None`
# TODO 4: add the row to a subclass of Inventory and preserve the subclass type
```

**Pista:** a un protocolo estructural le importa la forma del método público.
Mantén separadas las dos decisiones de ausencia: que no haya una fila
coincidente y que no haya precio son resultados de dominio diferentes.

**Solución explicada:** `WarehousePrices.unit_price` acepta `str` y devuelve el
resultado de un `dict[str, float].get`, por lo que satisface `PriceSource` sin
herencia. `first_matching` conserva `InventoryRow` como su `T`. Después de cada
rama `is None`, el valor restante queda estrechado. `Self` conserva la subclase
del inventario a través de `add`. Las pruebas en tiempo de ejecución siguen
siendo necesarias para los límites de entrada, la ausencia de mutación y la
identidad de los objetos.

### Checkpoint y rúbrica profesionales

Suma 0 o 1 punto por cada criterio:

1. Los campos de `TypedDict` coinciden con el contrato normalizado en tiempo de
   ejecución.
2. `Callable` y `TypeVar` conservan la relación entre el callback y el retorno.
3. Una implementación estructural de `Protocol` funciona sin herencia forzada.
4. `Self` conserva tanto la subclase estática como la identidad del objeto en
   tiempo de ejecución.
5. Una entrada no válida en la frontera deja sin cambios todas las filas
   existentes.
6. Tu explicación separa la forma estática del comportamiento en tiempo de
   ejecución.

Para completar la ruta necesitas al menos 5/6 y debes incluir los puntos 5 y 6.
Puedes detenerte aquí con un companion completamente ejecutable y probado.
Reflexión: ¿qué interfaz de un proyecto mayor necesita un contrato de
comportamiento y qué frontera de entrada sigue necesitando validación
ejecutable?

## Ruta avanzada opcional: evidencia del comprobador y recuperación

### A1. Prepara deliberadamente la herramienta declarada

La ruta de ejecución usa solo la biblioteca estándar. La ruta del comprobador
declara una única versión exacta fijada de una herramienta directa de desarrollo
en `requirements-dev.lock`: `mypy==2.2.0`. Pese a su nombre, este archivo **no**
es un archivo de bloqueo completo de resolución, transitivo, multiplataforma y
con hashes. Registra una única versión de herramienta directa para el contrato
de evidencia declarado.

Si una persona responsable del mantenimiento prepara deliberadamente un entorno
virtual desechable fuera del repositorio, este comando de instalación puede
necesitar acceso a la red o a un índice:

```text illustrative
python -m pip install -r chapter-27-python-typing/requirements-dev.lock
```

La instalación es una acción de preparación independiente. El verificador
nunca la ejecuta, nunca accede a un índice y nunca considera equivalente un
comprobador global o de otra versión. No crees `.venv` dentro de este capítulo.

### A2. Compara consumidores positivos, negativos y corregidos

El consumidor positivo comprueba filas tipadas, inferencia de retorno genérica,
una fuente estructural de precios y `Self`:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_positive.py check=learning:contract -->
```python source-ref
prices: PriceSource = Catalogue()
assert_type(prices.unit_price(row["sku"]), float | None)

inventory = LabelledInventory()
assert_type(inventory.add(row), LabelledInventory)
```

El consumidor negativo es deliberadamente incorrecto. Léelo antes de ejecutar
y predice una categoría para cada error:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_negative.py check=learning:contract -->
```python source-ref
bad_row: InventoryRow = {"sku": "PART-7", "quantity": "many"}
Inventory().add("not an inventory row")


class BrokenPrices:
    def unit_price(self, sku: int) -> str:
        return str(sku)


prices: PriceSource = BrokenPrices()
```

Las categorías de aceptación estables son:

- `[typeddict-item]` para el valor incorrecto de un campo declarado en
  `TypedDict`;
- `[arg-type]` para el argumento incompatible de `Inventory.add`; y
- `[assignment]` para asignar a `PriceSource` una clase con un método
  incompatible.

El texto completo, los prefijos de las fuentes, las notas, los colores y el
formato de los indicadores no forman parte de la salida de referencia. El
verificador exige un resultado distinto de cero y los tres tokens de categoría.

El consumidor corregido repara los contratos en lugar de ocultarlos:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_corrected.py check=learning:contract -->
```python source-ref
row: InventoryRow = {"sku": "PART-7", "quantity": 3}
inventory = Inventory().add(row)
assert_type(inventory, Inventory)


class FixedPrices:
    def unit_price(self, sku: str) -> float | None:
        return 1.25 if sku == "PART-7" else None
```

Error frecuente: añadir un `Any` sin límites, un `# type: ignore` sin
calificador o un `cast` que no cambia el comportamiento en tiempo de ejecución.
Corrige primero el valor, la firma o la frontera. Cuando una limitación externa
real requiera una vía de escape, restríngela a la expresión más pequeña, usa una
instrucción para ignorar un código concreto cuando sea compatible y documenta
por qué la evidencia de ejecución cubre esa laguna.

**Modifica — TODO O6:** copia un caso negativo en un archivo de trabajo
desechable, predice su categoría, corrige el contrato subyacente y vuelve a
ejecutar la misma configuración del comprobador. **Pista:** no edites el caso de
prueba negativo canónico; el verificador lo necesita como evidencia de un fallo
esperado. **Solución:** el caso corregido demuestra las tres reparaciones,
mientras que la suite de ejecución demuestra que el núcleo tipado sigue
funcionando.

### A3. Ejecuta el verificador acotado

Desde la raíz del repositorio, la verificación de ejecución siempre se
selecciona explícitamente:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --runtime
```

La verificación con el comprobador se selecciona por separado:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --checker
```

El verificador:

1. crea una instantánea del código fuente del capítulo y rechaza cachés o
   bytecode preexistentes;
2. copia únicamente el companion, las pruebas y los tres consumidores a una
   raíz temporal;
3. usa el intérprete actual con `-I -B`, sin entrada estándar, un entorno
   mínimo, un límite de 20 segundos, un límite de 64 KiB para la salida
   combinada y limpieza del grupo de procesos;
4. ejecuta las pruebas en tiempo de ejecución o comprueba la versión exacta de
   `mypy==2.2.0`;
5. en modo comprobador, exige que el caso positivo esté limpio, que el negativo
   termine con código distinto de cero y las tres categorías estables, y que el
   corregido esté limpio; y
6. elimina la raíz temporal, compara la instantánea del capítulo, busca
   residuos e informa de la limpieza de forma independiente.

El estado de salida `0` significa que el contrato seleccionado y la limpieza
han pasado. El estado `1` significa que ha fallado un comportamiento, límite,
comprobación de integridad de las fuentes o limpieza seleccionados. El estado
`2` significa que el uso del comando es incorrecto o falta el prerrequisito
exacto del comprobador. Cuando falta evidencia del comprobador, debe seguir
figurando como **prerrequisito ausente**; no puede proyectarse como aprobado.

El verificador limita accidentes procedentes de fuentes didácticas de
confianza; no es un entorno aislado capaz de contener código hostil. Solo
demuestra la ejecución del intérprete o herramienta seleccionados. No demuestra
todas las plataformas, todas las versiones de Python, la naturalidad de una
traducción, la eficacia didáctica, la accesibilidad, la compatibilidad de
paquetes ni la seguridad en producción.

### Checkpoint y rúbrica avanzados

Suma 0 o 1 punto por cada criterio:

1. La versión exacta del comprobador preparado coincide con la versión directa
   fijada.
2. Los consumidores positivo y corregido están limpios con las mismas opciones
   estrictas.
3. El consumidor negativo termina con código distinto de cero por las tres
   categorías estables.
4. Las pruebas en tiempo de ejecución siguen pasando después de la corrección.
5. Ningún `Any` amplio, `ignore` sin calificar ni `cast` usado solo como
   evidencia oculta un defecto.
6. La limpieza pasa y no aparece ningún caché del comprobador en el
   repositorio.

Para completar la ruta se necesitan los seis puntos. Si la versión fijada está ausente,
mantén esta ruta pendiente y conserva el checkpoint profesional. Reflexión:
¿qué encontró el comprobador antes de la ejecución y qué hecho importante de
tiempo de ejecución seguía sin poder demostrar?

## Errores frecuentes y recuperación serena

- **«Anotado significa validado».** Vuelve a E3, identifica la operación que se
  ejecutó realmente y coloca validación explícita en la frontera de entrada.
- **Usar `if not value` para `T | None`.** Vuelve al caso `0` y estrecha con
  `is None` cuando la pregunta sea si el valor está ausente.
- **Anotar todos los valores con el tipo más amplio.** Empieza por el contrato
  que se acepta de verdad; amplíalo solo cuando el comportamiento admita más.
- **Usar `TypedDict` como parser en tiempo de ejecución.** Conserva `parse_row` en la
  frontera no confiable y devuelve la forma tipada solo después de validar.
- **Forzar herencia de protocolos.** Haz coincidir la forma del método público;
  la herencia es una decisión de diseño independiente.
- **Silenciar diagnósticos.** Corrige la incompatibilidad más pequeña y después
  vuelve a ejecutar su caso vecino en tiempo de ejecución y la comprobación estática desde
  una raíz temporal limpia.
- **Llamar archivo de bloqueo universal a una versión directa fijada.** Registra la herramienta, la
  versión, el host, el objetivo de Python, las suposiciones de adquisición y la
  ejecución real. No deduzcas una resolución transitiva ni multiplataforma.

## Verificación para responsables de mantenimiento y frontera de evidencia

Todos los extractos del companion de este capítulo usan la comprobación
registrada de referencias a fuentes `learning:contract`. El plugin propietario
puede seleccionar ese contrato; la validación genérica del libro comprueba el
Markdown y la forma declarada de las referencias sin ejecutar silenciosamente
archivos arbitrarios del companion.

Ejecuta primero la evidencia estrecha de ejecución:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --runtime
```

Ejecuta la evidencia del comprobador solo si `mypy==2.2.0` ya está presente en
el intérprete seleccionado:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --checker
```

No instales un comprobador como paso oculto de validación. Registra por separado
los resultados de ejecución y del comprobador. Un comprobador que pasa no
sustituye las pruebas en tiempo de ejecución; una estructura correcta no
aprueba la fluidez lingüística, la pedagogía, la accesibilidad, el renderizado
bidireccional, la procedencia ni la publicación.

## Reflexión final y próximos pasos

Un buen tipado facilita la comprensión de una frontera real. No vuelve Python
menos dinámico ni elimina la necesidad de validar valores externos. Usa la
anotación más pequeña que aclare una relación y después demuestra el
comportamiento en tiempo de ejecución en la frontera donde importan los errores.

Para interfaces de paquetes nativos, continúa de forma independiente con el
[Capítulo 24: Python y C++](../chapter-24-python-cpp-integration/README.es.md) o
el [Capítulo 25: Python y Rust](../chapter-25-python-rust-integration/README.es.md).
Para un proyecto que combina modelado del dominio, persistencia, CLI, pruebas,
registro de eventos (`logging`) y verificación de artefactos, continúa con el
[Capítulo 28: Proyecto final profesional](../chapter-28-professional-capstone/README.es.md).
