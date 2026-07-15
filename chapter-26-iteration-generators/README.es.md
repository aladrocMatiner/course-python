# Capítulo 26 · Iteración, iteradores y generadores

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir

Muchos programas reciben una secuencia de valores y la transforman: los nombres
se convierten en etiquetas, las lecturas en resúmenes y los grupos en un único
flujo. Ya sabes hacerlo con un bucle `for`. Este capítulo conserva ese modelo
mental fiable y añade tres herramientas en un orden deliberado:

1. **Comprehensions, `enumerate` y `zip`** para transformaciones pequeñas y
   legibles de colecciones.
2. **Iteradores** para entender dónde vive el estado del recorrido y por qué un
   flujo de datos puede agotarse.
3. **Generadores** para producir valores cuando se solicitan, manteniendo al
   consumidor explícitamente acotado.

El proyecto que irá creciendo es un pipeline de iteración para el pequeño
marcador sintético de un taller. Su autoridad ejecutable es
[`examples/iteration_pipeline.py`](examples/iteration_pipeline.py), respaldada
por pruebas de la biblioteca estándar. No usa red, credenciales, datos
personales, archivos, hilos ni paquetes de terceros.

## Objetivos de aprendizaje

Al finalizar la ruta que elijas, podrás:

- **O1 — Transformar con claridad:** derivar una comprehension de lista,
  diccionario o conjunto a partir de un bucle corriente y elegir la forma más
  clara.
- **O2 — Enumerar y emparejar con seguridad:** usar `enumerate` para posiciones
  de presentación y elegir deliberadamente entre el truncamiento de `zip` y
  `zip(..., strict=True)`.
- **O3 — Explicar el estado de un iterador:** distinguir un iterable de un
  iterador, usar `iter` y `next`, observar el agotamiento y recrear un recorrido
  cuando la fuente lo permita.
- **O4 — Proteger el recorrido:** usar un valor predeterminado de agotamiento
  inequívoco y evitar mutaciones estructurales de la colección que estás
  recorriendo.
- **O5 — Construir trabajo lazy acotado:** explicar expresiones generadoras,
  `yield`, consumo de un solo uso, `yield from` y un límite finito explícito.
- **O6 — Recuperar y limpiar:** localizar un error diferido en el paso de
  consumo, terminar un generador con `return` y ejecutar una limpieza
  determinista tras un cierre anticipado.

El [registro de trazabilidad](TRACEABILITY.md) relaciona cada objetivo con la
explicación, la práctica, la recuperación, la solución, el checkpoint, el
código companion y las pruebas.

## Prerrequisitos y mapa de rutas

El punto de entrada obligatorio es el checkpoint fundamental del
[capítulo 11: Funciones](../chapter-11-functions/README.es.md). Debes sentirte a
gusto con listas, diccionarios, conjuntos, condicionales, bucles `for`/`while`
y funciones pequeñas. El número del capítulo **no** significa que necesites
redes, C++ o Rust.

- **Ruta esencial · 2 sesiones de 45–60 minutos.** Lee E1–E3, completa el reto
  esencial y usa su rúbrica. Resultado: producir un marcador numerado a partir
  de dos colecciones pequeñas y rechazar datos que no encajen. Finalización:
  al menos 4/5 puntos de la rúbrica, incluido el emparejamiento estricto.
  Continuación segura: detente aquí y sigue con el
  [capítulo 12: Clases y objetos](../chapter-12-oop/README.es.md).
- **Ruta profesional · 1–2 sesiones de 45–60 minutos.** Completa primero el
  checkpoint esencial; después, P1–P3 y el reto profesional. Resultado:
  consumir, diagnosticar y recrear deliberadamente un recorrido de un solo uso.
  Finalización: al menos 4/5 puntos, incluida la recuperación tras el
  agotamiento. Punto seguro donde parar: puedes usar iterables con confianza
  sin escribir generadores.
- **Ruta avanzada opcional · 2 sesiones de 60–75 minutos.** Completa la ruta
  profesional y repasa el
  [capítulo 14: Excepciones](../chapter-14-exceptions/README.es.md) antes de la
  sección de limpieza. Resultado: implementar y explicar un pipeline lazy
  finito, un fallo diferido, delegación y limpieza anticipada. Finalización: al
  menos 5/6 puntos, incluidos límites y limpieza. Esta ruta sigue siendo
  opcional para avanzar por el curso esencial.

¿Vuelves al tema con experiencia previa? Predice el resultado de
`list(zip(["A", "B"], [1], strict=True))`. Si puedes explicar por qué el fallo
solo aparece al consumir el objeto zip, empieza por la ruta profesional. Si
también puedes explicar por qué llamar a una función generadora no ejecuta su
cuerpo, empieza por la ruta avanzada y usa los checkpoints para confirmar
cualquier laguna.

## Un pequeño glosario

- **Iterable:** objeto capaz de proporcionar un iterador. Listas, tuplas,
  diccionarios, conjuntos y cadenas son ejemplos conocidos.
- **Iterador:** objeto con estado que produce un siguiente valor cada vez.
  Recuerda hasta dónde ha avanzado el recorrido.
- **Agotamiento:** estado en el que un iterador ya no tiene un valor siguiente.
  Un `next` directo lanza entonces `StopIteration`, salvo que se indique un
  valor predeterminado.
- **Comprehension:** sintaxis compacta para construir una colección concreta a
  partir de un iterable.
- **Generador:** iterador creado por una expresión generadora o por una función
  que contiene `yield`.
- **Lazy:** producir trabajo a medida que se solicitan valores. Lazy no
  significa automáticamente finito, rápido ni seguro.
- **Consumidor:** el bucle, `next`, `list` u otra operación que pide valores a
  un iterador.

La secuencia observable siempre es la misma: obtener un iterador, solicitar un
valor, recibir un valor o agotamiento y, entonces, detenerse o volver a
solicitar. Esta secuencia en prosa es el equivalente textual de cualquier
diagrama de estado de un iterador que dibujes; ningún significado depende de la
dirección de una flecha ni de un color.

## Ruta esencial: transformaciones legibles

### E1. Deriva una comprehension a partir de un bucle

Objetivo: construir una colección pequeña sin perder el modelo mental del
bucle ordinario.

Supón que un taller registra tres puntuaciones sintéticas. Antes de ejecutar el
ejemplo, predice el valor de `doubled` después de cada iteración.

```python runnable
scores = [3, 5, 8]
doubled = []

for score in scores:
    doubled.append(score * 2)

print(doubled)
```

```text output
[6, 10, 16]
```

Lee el bucle en este orden: toma un `score`, calcula `score * 2`, añade el
resultado y repite. Una comprehension de lista expresa la misma transformación
colocando primero la expresión del resultado:

```python runnable
scores = [3, 5, 8]
doubled = [score * 2 for score in scores]
print(doubled)
```

```text output
[6, 10, 16]
```

Los corchetes significan «construye una lista». Dentro de ellos:

1. `score * 2` es el valor que se va a guardar;
2. `score` es el nombre objetivo actual; y
3. `scores` es el iterable que proporciona valores.

Una única condición puede filtrar valores, pero aparece después del iterable.
Predice qué puntuaciones sobreviven antes de ejecutar:

```python runnable
scores = [3, 5, 8]
large_doubles = [score * 2 for score in scores if score >= 5]
print(large_doubles)
```

```text output
[10, 16]
```

Las comprehensions de diccionario y conjunto siguen el mismo orden de lectura.
Un diccionario guarda pares clave/valor; un conjunto elimina duplicados
iguales. Ordenamos el conjunto solo para mostrar una salida estable: el orden
de iteración de un conjunto no es un contrato de corrección.

```python runnable
names = ["Noor", "Frej", "Taha"]
length_by_name = {name: len(name) for name in names}
unique_lengths = {len(name) for name in names}

print(length_by_name)
print(sorted(unique_lengths))
```

```text output
{'Noor': 4, 'Frej': 4, 'Taha': 4}
[4]
```

El límite de entrada vacía es tranquilo y útil: ninguno de los cuerpos se
ejecuta, de modo que cada comprehension produce una colección vacía de su
propio tipo.

```python runnable
print([value for value in []])
print({value: len(value) for value in []})
print({value for value in []})
```

```text output
[]
{}
set()
```

**Modifica — TODO O1:** reescribe este bucle como una comprehension de lista
legible. Conserva exactamente una transformación y una condición.

```python todo
scores = [2, 4, 7, 9]
selected = []
for score in scores:
    if score >= 5:
        selected.append(score + 1)

# TODO: replace the loop with selected = [...]
print(selected)
```

**Pista:** lee el cuerpo original en orden: guarda `score + 1`, toma cada
`score` de `scores` y consérvalo cuando `score >= 5`.

**Solución explicada:** primero aparece la expresión del resultado; después,
el mismo bucle y la misma condición. El resultado normal es `[8, 10]`; un
`scores` vacío continúa produciendo `[]`.

```python runnable
scores = [2, 4, 7, 9]
selected = [score + 1 for score in scores if score >= 5]
print(selected)
```

```text output
[8, 10]
```

Error común: comprimir en una única expresión bucles anidados, varias
condiciones, efectos secundarios y asignaciones. Una comprehension resulta
valiosa cuando es más fácil de leer. Conserva el bucle ordinario cuando cuente
la historia de manera más serena.

### E2. Enumera posiciones sin un contador manual

Objetivo: adjuntar posiciones orientadas a personas sin actualizar una
variable independiente.

`enumerate` produce pares `(position, value)`. `start=1` es útil para etiquetas
que verá una persona; no cambia que los índices de la colección empiecen en
cero. Predice las dos líneas impresas:

```python runnable
names = ["Noor", "Frej"]

for position, name in enumerate(names, start=1):
    print(f"{position}: {name}")
```

```text output
1: Noor
2: Frej
```

El caso límite es un iterable vacío: el cuerpo del bucle se ejecuta cero veces
y no imprime nada. No hay que inventar ninguna posición especial.

**Modifica — TODO O2:** cambia el número inicial mostrado a `10` y predice las
dos etiquetas antes de ejecutar.

```python todo
names = ["Noor", "Frej"]
# TODO: enumerate names starting at 10 and print "position: name"
```

**Pista:** cambia solo el argumento `start`; no añadas ni incrementes un
contador independiente.

**Solución explicada:** `enumerate(names, start=10)` produce `(10, "Noor")` y
`(11, "Frej")`. La lista no cambia.

```python runnable
names = ["Noor", "Frej"]
print(list(enumerate(names, start=10)))
```

```text output
[(10, 'Noor'), (11, 'Frej')]
```

### E3. Empareja datos sin pérdidas silenciosas

Objetivo: hacer visible el contrato de longitud cuando dos fuentes de datos
pertenecen la una a la otra.

El `zip` ordinario se detiene cuando se agota la entrada más corta. Puede ser
deliberado, pero también puede ocultar una puntuación ausente:

```python runnable
names = ["Noor", "Frej"]
scores = [7]
print(list(zip(names, scores)))
```

```text output
[('Noor', 7)]
```

`"Frej"` desaparece porque el iterable de puntuaciones no tiene un segundo
valor. Cuando la igualdad de longitudes forma parte de la corrección, pide ese
contrato explícitamente con `strict=True`. La función companion consume el zip
en una lista, por lo que el desajuste no puede pasar inadvertido dentro de un
objeto zip que nadie haya consumido.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def strict_pairs(left, right):
    """Return pairs, rejecting unequal input lengths."""
    return list(zip(left, right, strict=True))
```

En el camino normal, las pruebas verifican
`strict_pairs(["Noor", "Frej"], [7, 9]) == [("Noor", 7), ("Frej", 9)]`.
Dos entradas vacías producen correctamente `[]`.

Predice cuándo falla el siguiente ejemplo: ¿al crear `zip` o cuando `list` le
pide sus valores?

<!-- bookcheck: expect-error="ValueError" -->
```python expected-error
names = ["Noor", "Frej"]
scores = [7]
pairs = zip(names, scores, strict=True)
print(list(pairs))
```

La señal estable es `ValueError`. La construcción solo crea el iterador; el
consumo descubre que la entrada derecha ha terminado primero. El texto completo
del traceback puede cambiar entre versiones de mantenimiento de Python.

**Recuperación:** corrige la puntuación ausente y vuelve a ejecutar el mismo
contrato estricto.

```python runnable
names = ["Noor", "Frej"]
scores = [7, 9]
print(list(zip(names, scores, strict=True)))
```

```text output
[('Noor', 7), ('Frej', 9)]
```

Eliminar `strict=True` también es un diseño válido cuando ignorar los valores
sobrantes es explícitamente aceptable. Escribe esa decisión en el contrato del
dominio; no conviertas el truncamiento silencioso en la reparación accidental.

### Reto esencial guiado

Construye un marcador numerado. Primero predice las dos líneas de salida y el
fallo causado por una puntuación ausente.

```python todo
names = ["Noor", "Frej"]
scores = [7, 9]

# TODO 1: pair names and scores with strict=True.
# TODO 2: enumerate the pairs starting at 1.
# TODO 3: build lines like "1. Noor: 7" with a list comprehension.
# TODO 4: print each line.
```

**Pista:** crea primero `pairs`. Después, la comprehension puede desempaquetar
`position, (name, score)` desde `enumerate(pairs, start=1)`.

**Solución explicada:** el emparejamiento estricto protege la alineación de los
datos; la enumeración crea las posiciones de presentación; la comprehension
formatea una línea por pareja. Cada paso tiene una responsabilidad.

```python runnable
names = ["Noor", "Frej"]
scores = [7, 9]
pairs = list(zip(names, scores, strict=True))
lines = [
    f"{position}. {name}: {score}"
    for position, (name, score) in enumerate(pairs, start=1)
]

for line in lines:
    print(line)
```

```text output
1. Noor: 7
2. Frej: 9
```

Con `names = []` y `scores = []`, `pairs` y `lines` están vacías y no se
imprime nada. Para longitudes distintas, `ValueError` es el diagnóstico
esperado; repara los datos en lugar de ocultar el desajuste.

### Checkpoint y rúbrica esenciales

Completa el marcador con entradas normales, vacías y de longitudes distintas.
Explica por qué la salida normal está ordenada, por qué el resultado vacío es
válido y por qué el desajuste falla durante el consumo.

Suma un punto por cada criterio:

- **Corrección:** la entrada normal produce las dos líneas numeradas exactas.
- **Límite:** dos entradas vacías producen un resultado vacío sin una fila
  inventada.
- **Recuperación:** las entradas desiguales lanzan `ValueError` y la entrada
  corregida funciona.
- **Legibilidad:** cada comprehension contiene una transformación clara y como
  máximo una condición sencilla.
- **Explicación:** distingues posiciones de presentación, índices de colección
  y el contrato de emparejamiento estricto.

Un 4/5, incluida **Recuperación**, completa la ruta esencial. Puedes detenerte
con seguridad y continuar al capítulo 12. Reflexión: ¿en qué programa que
conozcas sería peligroso un truncamiento silencioso?

## Ruta profesional: un estado de iterador que puedes explicar

### P1. Iterable e iterador son papeles diferentes

Objetivo: localizar el estado del recorrido en vez de imaginar que un bucle
`for` recuerda mágicamente una posición.

Una lista es un **iterable**: puede proporcionar un iterador. `iter(values)`
pide uno. El iterador devuelto guarda el progreso del recorrido.
`next(cursor)` pide un valor a ese iterador concreto.

Predice cada línea antes de ejecutar:

```python runnable
values = ["A", "B"]
cursor = iter(values)

print(iter(cursor) is cursor)
print(next(cursor))
print(next(cursor))
print(next(cursor, "done"))
```

```text output
True
A
B
done
```

La secuencia en prosa es:

1. `values` puede crear recorridos.
2. `cursor` comienza antes del primer valor.
3. el primer `next` avanza y devuelve `"A"`;
4. el segundo avanza y devuelve `"B"`; y
5. el tercero encuentra el agotamiento y devuelve el valor predeterminado.

`iter(cursor) is cursor` es `True` porque un iterador es su propio iterador. En
cambio, llamadas separadas a `iter(values)` producen recorridos separados con
su propio estado.

La cuenta atrás del companion también es un iterador, pero es un generador de
un solo uso y no una colección reutilizable:

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def countdown(start):
    """Yield ``start`` down to 1 after validating a finite bound."""
    _require_bounded_integer(start, name="start", maximum=MAX_SQUARES)
    current = start
    while current > 0:
        yield current
        current -= 1
```

Las pruebas verifican que `list(countdown(3))` es `[3, 2, 1]` y que
`list(countdown(0))` es el límite vacío `[]`. Los límites negativos, booleanos,
no enteros y superiores al máximo se rechazan cuando empieza el consumo.

**Modifica — TODO O3:** crea dos iteradores a partir de la misma lista. Consume
dos valores del primero y uno del segundo. Predice los tres resultados.

```python todo
values = ["A", "B"]
first = iter(values)
second = iter(values)
# TODO: call next twice on first and once on second, then print each result.
```

**Pista:** el estado del iterador pertenece a `first` o a `second`, no a
`values`.

**Solución explicada:** las observaciones son `A`, `B` y después `A`. El segundo
iterador inicia su propio recorrido.

```python runnable
values = ["A", "B"]
first = iter(values)
second = iter(values)
print(next(first))
print(next(first))
print(next(second))
```

```text output
A
B
A
```

### P2. Agotamiento, valores predeterminados y recuperación

Objetivo: reconocer el agotamiento como un evento normal del protocolo y
elegir una recuperación explícita.

Un `next` directo sin valor predeterminado lanza `StopIteration` después del
último valor:

<!-- bookcheck: expect-error="StopIteration" -->
```python expected-error
cursor = iter(["A"])
print(next(cursor))
print(next(cursor))
```

La primera llamada imprime `A`; la segunda alcanza la señal estable prevista
`StopIteration`. Un bucle `for` gestiona internamente esta señal y termina con
normalidad. No captures todas las excepciones de forma amplia solo para seguir
pidiendo valores.

Hay dos recuperaciones habituales:

1. Si la fuente es reutilizable, pídele un **iterador nuevo**.
2. Si se espera el agotamiento en una API paso a paso, pasa a `next` un valor
   predeterminado elegido deliberadamente.

```python runnable
values = ["A"]
spent = iter(values)
print(next(spent))
print(next(spent, "done"))

fresh = iter(values)
print(next(fresh))
```

```text output
A
done
A
```

Una cadena predeterminada es ambigua si el flujo puede contener legítimamente
esa misma cadena. Un objeto centinela privado permite distinguir la ausencia
por identidad:

```python runnable
missing = object()
value = next(iter([]), missing)
print(value is missing)
```

```text output
True
```

**Modifica — TODO O4:** con `values = [0]`, usa un centinela privado para
distinguir el valor real `0` del agotamiento. Observa las dos solicitudes.

```python todo
values = [0]
missing = object()
cursor = iter(values)
# TODO: request twice with missing as the default and compare each result by identity.
```

**Pista:** `0` es false-like, pero está presente. Comprueba la ausencia con
`is missing`, no con `if not value`.

**Solución explicada:** el primer resultado es `0` y `first is missing` es
`False`; el segundo resultado es el centinela y `second is missing` es `True`.

```python runnable
values = [0]
missing = object()
cursor = iter(values)
first = next(cursor, missing)
second = next(cursor, missing)
print(first, first is missing)
print(second is missing)
```

```text output
0 False
True
```

### P3. Mantén separada la mutación de la fuente

Objetivo: evitar cambios en la estructura que controla el recorrido, salvo que
se haya enseñado y probado el contrato específico de esa colección.

Eliminar o insertar elementos en la misma lista que se recorre puede saltarse
valores, porque las posiciones cambian mientras avanza el iterador. Construye
en su lugar un resultado separado:

```python runnable
raw_labels = ["draft", "", "review", ""]
clean_labels = []

for label in raw_labels:
    if label:
        clean_labels.append(label)

print(raw_labels)
print(clean_labels)
```

```text output
['draft', '', 'review', '']
['draft', 'review']
```

El original continúa disponible para el diagnóstico y el resultado tiene un
contrato evidente. Una comprehension también resulta clara aquí:
`[label for label in raw_labels if label]`.

Error común: observar un ejemplo de mutación que parece funcionar y suponer que
todas las colecciones lo garantizan. No comparten un único contrato de mutación
durante el recorrido. Prefiere una instantánea o un resultado separado, salvo
que el comportamiento exacto sea necesario y esté verificado.

### Reto profesional guiado

Recorre una cola de etapas sintéticas sin modificarla. Consume `"draft"`,
después `"review"`, observa el agotamiento con un centinela privado y
recupérate creando un recorrido nuevo que vuelva a producir `"draft"`.

```python todo
stages = ["draft", "review"]
missing = object()
cursor = iter(stages)
# TODO 1: consume and print both stages.
# TODO 2: request once more with missing as the default and prove identity.
# TODO 3: create a fresh iterator and print its first value.
```

**Pista:** no asignes `fresh = cursor`; así obtendrías el mismo objeto agotado.
Vuelve a llamar a `iter(stages)`.

**Solución explicada:** el estado del recorrido queda aislado en cada iterador.
La lista original es reutilizable; asignar otro nombre no reinicia `cursor`.

```python runnable
stages = ["draft", "review"]
missing = object()
cursor = iter(stages)
print(next(cursor))
print(next(cursor))
print(next(cursor, missing) is missing)

fresh = iter(stages)
print(next(fresh))
```

```text output
draft
review
True
draft
```

### Checkpoint y rúbrica profesionales

Completa el recorrido guiado y las pruebas límite de la cuenta atrás. Explica
con tus palabras iterable, iterador, estado actual, agotamiento, valor
predeterminado y recreación.

Suma un punto por cada criterio:

- **Identidad:** distingues una lista reutilizable de cada iterador que crea.
- **Estado:** tu predicción sigue cada iterador de forma independiente.
- **Límite:** un iterador vacío usa un centinela inequívoco.
- **Recuperación:** se crea un recorrido nuevo a partir de la fuente
  reutilizable.
- **Seguridad y explicación:** la fuente no se muta estructuralmente y puedes
  explicar por qué asignar otro nombre no rebobina un iterador.

Un 4/5, incluida **Recuperación**, completa la ruta profesional. Reflexión:
¿cuáles de las API que usas devuelven colecciones reutilizables y cuáles pueden
devolver iteradores de un solo uso?

## Ruta avanzada opcional: pipelines lazy acotados

Repasa el capítulo 14 antes de A6 y A7: esas secciones usan `try`, `finally` y
categorías de excepciones. Todo lo que sigue continúa siendo opcional para el
avance esencial del curso.

### A1. Las expresiones generadoras aplazan el trabajo

Objetivo: distinguir una colección materializada de un iterador bajo demanda.

Los corchetes construyen inmediatamente todos los valores de una lista. Los
paréntesis alrededor de la misma sintaxis de comprensión crean una expresión
generadora:

```python runnable
numbers = [1, 2, 3]
materialized = [number * number for number in numbers]
lazy = (number * number for number in numbers)

print(materialized)
print(next(lazy))
print(list(lazy))
```

```text output
[1, 4, 9]
1
[4, 9]
```

El primer `next` consume `1`; `list(lazy)` recibe solo los valores restantes.
El generador es de un solo uso. La evaluación diferida cambia **cuándo** se
solicitan los valores; no promete que el trabajo sea rápido ni que un
consumidor sin límite sea seguro.

**Modifica — TODO O5:** Predice el resultado de dos llamadas a `next(lazy)`
seguidas de `list(lazy)` para cuatro números de entrada. Después ejecuta una
versión finita.

**Pista:** tacha un valor de la fuente cada vez que el consumidor solicite uno.

### A2. Las funciones generadoras se detienen en `yield`

Una función que contiene `yield` crea un generador. Llamarla crea el objeto
generador, pero todavía no ejecuta su cuerpo. Cada petición reanuda la ejecución
hasta el siguiente `yield`, un `return` normal o un fallo.

La fuente probada `countdown` apareció en P1. Para `countdown(3)`, tres
peticiones producen `3`, `2` y `1`; la petición siguiente observa el
agotamiento. Su validación también comienza al consumir, por lo que es posible
construir `countdown(-1)`, pero falla con `ValueError` cuando se consume por
primera vez.

**Modifica — TODO O5:** Predice `list(countdown(0))` y
`list(countdown(2))` antes de consultar los resultados de las pruebas.

**Solución explicada:** cero entra en el límite válido, pero el cuerpo del
bucle nunca se ejecuta, así que el resultado es `[]`. Dos produce `[2, 1]` y
después termina normalmente.

### A3. Acota una fuente que, de otro modo, sería infinita

`itertools.count()` puede seguir produciendo enteros. El companion coloca
delante un límite explícito y validado, y restringe el límite solicitado a
`MAX_SQUARES = 10_000`. Es una barrera de seguridad didáctica, no una constante
universal del dominio.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def bounded_squares(limit):
    """Yield the first ``limit`` squares from an otherwise infinite source."""
    _require_bounded_integer(limit, name="limit", maximum=MAX_SQUARES)
    squares = (number * number for number in count())
    yield from islice(squares, limit)
```

Las pruebas consumen exactamente cinco valores y observan
`[0, 1, 4, 9, 16]`. Un límite cero no produce nada. Un valor negativo,
booleano, no entero o superior al límite se rechaza en el primer paso de
consumo.

No materialices una fuente infinita sin un limitador. Incluso un productor
lazy deja de estar acotado si el consumidor sigue solicitando valores para
siempre o almacena cada resultado. Acota el número de elementos, el tiempo, la
entrada y los recursos propios en la frontera adecuada.

**Modifica — TODO O5:** Cambia un límite finito de `islice` de 5 a 7 y predice
los dos cuadrados finales. Después prueba `limit = 0`.

**Pista:** la fuente comienza en cero; eleva al cuadrado los índices 5 y 6 para
obtener la nueva cola.

**Solución explicada:** siete valores son
`[0, 1, 4, 9, 16, 25, 36]`; cero valores producen `[]`. Es el limitador, no la
expresión generadora por sí sola, lo que garantiza la terminación.

### A4. Delega con `yield from`

Objetivo: reenviar valores de un subiterable finito sin escribir manualmente un
bucle anidado con `yield`.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def flatten(groups):
    """Yield every value from each finite group in order."""
    for group in groups:
        yield from group
```

Para `[["A", "B"], [], ["C"]]`, el resultado verificado es
`["A", "B", "C"]`. El grupo interior vacío no aporta ningún valor y no
necesita un caso especial.

**Modifica — TODO O5:** Añade grupos vacíos al principio y al final. Predice el
mismo resultado antes de ejecutar.

**Pista:** `yield from []` simplemente termina de inmediato.

### A5. Un fallo aplazado sigue siendo un fallo

Objetivo: relacionar un diagnóstico con el paso de consumo que alcanzó los
datos no válidos.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def reciprocals(values):
    """Yield reciprocals; an invalid later value fails when it is consumed."""
    for value in values:
        yield 1 / value
```

Construir `reciprocals([2, 0, 4])` funciona porque todavía no se ha realizado
ninguna división. El primer `next` produce `0.5`; el segundo llega a cero y
lanza la categoría estable `ZeroDivisionError`. El `4` posterior nunca llega a
consumirse desde ese generador fallido.

**Recuperación — TODO O6:** Corrige la entrada no válida y crea un generador
nuevo. No supongas que el objeto fallido se puede rebobinar.

**Pista:** la entrada de recuperación probada es `[2, 4]`.

**Solución explicada:** un `reciprocals([2, 4])` nuevo produce `[0.5, 0.25]`.
La corrección cambia el valor de dominio no válido y reinicia el recorrido
desde un estado conocido.

### A6. Limpieza determinista tras un cierre anticipado

Objetivo: liberar un recurso local propio cuando un generador iniciado termina,
falla o se cierra explícitamente.

Este companion acepta un callback `close` falso para que la prueba pueda
observar la limpieza sin abrir un archivo ni una conexión de red reales:

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def managed_values(values, close):
    """Yield values and call ``close`` once when an active generator ends."""
    if not callable(close):
        raise TypeError("close must be callable")
    try:
        yield from values
    finally:
        close()
```

La prueba de limpieza inicia el generador, consume `"A"`, llama a
`cursor.close()` y observa `events == ["closed"]`. Llamar a `close` de nuevo no
añade un segundo evento. El agotamiento completo normal también ejecuta la
limpieza una sola vez. Un valor de limpieza no invocable lanza `TypeError`
cuando comienza el consumo.

Detalle importante: cerrar un generador que nunca se ha iniciado no entra en
su cuerpo, por lo que no puede depender de ese cuerpo para adquirir y después
liberar un recurso. Adquiere un recurso únicamente dentro del tiempo de vida
activo que controlas y cierra explícitamente un generador iniciado cuando el
consumidor se detenga antes de tiempo. No dependas del momento en que actúe el
recolector de basura.

**Modifica — TODO O6:** Usa `events = []`, inicia un `managed_values` de dos
valores, consume uno, ciérralo y comprueba el único evento de limpieza.

**Pista:** inspecciona `events` antes y después de `cursor.close()`.

### A7. Termina con `return`, no con `StopIteration`

Un generador termina normalmente cuando la ejecución llega al final o ejecuta
`return`. Lanzar explícitamente `StopIteration` dentro de su cuerpo se traduce
a la categoría estable `RuntimeError` en la versión de Python declarada.
Predice la categoría final de la excepción:

<!-- bookcheck: expect-error="RuntimeError" -->
```python expected-error
def broken_generator():
    yield "ready"
    raise StopIteration("finished")

cursor = broken_generator()
print(next(cursor))
print(next(cursor))
```

La primera petición imprime `ready`; la segunda alcanza el lanzamiento
explícito incorrecto y falla con `RuntimeError`. El texto completo del traceback
no forma parte del contrato.

**Recuperación:** sustituye el lanzamiento explícito por `return`.

```python runnable
def finished_generator():
    yield "ready"
    return

print(list(finished_generator()))
```

```text output
['ready']
```

### Reto guiado avanzado

Construye un informe finito solo con herramientas de la biblioteca estándar:

```python todo
from itertools import count, islice

limit = 4
# TODO 1: create a generator expression of squares from count().
# TODO 2: bound it with islice(..., limit).
# TODO 3: materialize only those four values and print them.
# TODO 4: repeat with limit = 0.
```

**Pista:** el consumidor debe recibir `islice(squares, limit)`, nunca la fuente
no acotada directamente.

**Solución explicada:** crea la expresión lazy de cuadrados, coloca `islice`
entre ella y `list`, y después materializa la vista finita.

```python runnable
from itertools import count, islice

limit = 4
squares = (number * number for number in count())
result = list(islice(squares, limit))
print(result)
```

```text output
[0, 1, 4, 9]
```

El límite cero devuelve `[]`. Un límite negativo o enorme elegido por quien
aprende necesita validarse antes de llegar a esta construcción; el
`bounded_squares` del companion es propietario de ese contrato comprobado.

### Checkpoint y rúbrica avanzados

Completa el informe acotado, la recuperación del fallo aplazado y el TODO de
limpieza. Después explica cuándo comienza a trabajar cada generador y cómo
termina.

Suma un punto por cada criterio:

- **Evaluación diferida:** distingues la construcción del primer paso de
  consumo.
- **Límites:** toda fuente que, de otro modo, sería infinita tiene un límite
  finito explícito y validado en el consumidor.
- **Estado de un solo uso:** un generador agotado o fallido se recrea
  deliberadamente.
- **Recuperación:** la entrada no válida se corrige y el caso vecino reparado
  funciona.
- **Delegación:** `yield from` conserva el orden de los grupos finitos,
  incluidos los vacíos.
- **Limpieza y explicación:** un generador iniciado cierra su recurso falso
  exactamente una vez y explicas por qué `return` es una terminación normal.

Un 5/6, incluidos **Límites** y **Limpieza y explicación**, completa la ruta
avanzada opcional. Reflexión: ¿qué límite pertenece al productor, cuál al
consumidor y quién es responsable de la limpieza en tu pipeline?

## Errores frecuentes y recuperaciones serenas

- **Comprensiones densas:** si necesitas descifrar la línea dos veces, vuelve a
  un bucle con nombre o separa los valores intermedios.
- **Depender del orden de un conjunto:** compara la pertenencia al conjunto u
  ordena solo para obtener una presentación estable; no prometas un orden de
  representación arbitrario.
- **Usar `zip` ordinario cuando las longitudes deben coincidir:** selecciona
  `strict=True`, consume el resultado, corrige la discrepancia de las fuentes y
  vuelve a ejecutar.
- **Suponer que `zip` valida al construirse:** descubre el agotamiento de la
  entrada a medida que avanza el consumidor.
- **Llamar a `next` indefinidamente:** gestiona el agotamiento con un bucle
  `for`, un valor predeterminado deliberado o un iterador nuevo creado desde una
  fuente reutilizable.
- **Tratar un generador como si se pudiera rebobinar:** recréalo a partir de las
  entradas originales.
- **Mutar la colección que se recorre:** construye un resultado separado o una
  instantánea explícita.
- **Decir que un pipeline es «seguro porque es lazy»:** añade un límite de
  elementos, tiempo o entrada y una limpieza determinista de recursos.
- **Esperar que la validación ocurra al construir el generador:** recuerda que
  el cuerpo de un generador comienza al consumir; prueba la primera petición.
- **Lanzar `StopIteration` dentro de un generador:** usa `return` para el final
  normal.

Los errores de este capítulo son observaciones, no fallos personales. Reduce
el ejemplo a un productor, un consumidor y un único valor siguiente esperado;
después repara ese contrato mínimo y vuelve a ejecutar su caso vecino válido.

## Verificar el contrato ejecutable

Desde la raíz del repositorio, ejecuta la suite declarada de la biblioteca
estándar:

```bash illustrative
python -B -m unittest discover -s chapter-26-iteration-generators/examples/tests -t chapter-26-iteration-generators/examples -p 'test_*.py'
```

`-B` evita la creación de cachés de bytecode. El descubrimiento añade el
directorio `examples` del companion como raíz de importación de las pruebas y
solo ejecuta `test_*.py` dentro de su paquete `tests`. La suite comprueba:

- emparejamiento estricto normal y vacío, además de `ValueError` por longitudes
  diferentes;
- cuentas atrás normales, con cero, con límite no válido, agotadas y recreadas;
- los cinco primeros cuadrados acotados y límites no válidos;
- delegación finita con grupos vacíos;
- `ZeroDivisionError` aplazado y recuperación con la entrada corregida; y
- cierre parcial, agotamiento normal, limpieza no válida y limpieza exactamente
  una vez.

Se espera que el comando termine con código cero. La ausencia del intérprete o
un resultado de prueba distinto de cero no cuenta como éxito: lee la primera
prueba que falla, corrige el contrato más pequeño, elimina el estado temporal y
vuelve a ejecutar tanto ese caso como su vecino válido.

Los bloques Markdown `source-ref` están registrados bajo
`learning:contract`. Son enlaces de evidencia, no código que ejecute la ruta
Markdown genérica. La comprobación explícita de puentes de aprendizaje es la
responsable del comportamiento de sus companions; los bloques pequeños
`runnable` y `expected-error` siguen siendo aptos para el verificador genérico
acotado.

La verificación demuestra el comportamiento ejercitado en el intérprete
seleccionado. Por sí sola no demuestra calidad didáctica, fluidez de la
traducción, compatibilidad amplia entre plataformas, accesibilidad ni
aprobación para publicar.

## Resumen y reflexión final

Ahora puedes elegir una herramienta de recorrido según su contrato:

- usa un bucle ordinario cuando sus pasos sean la opción más clara;
- usa una comprensión sencilla para construir una colección concreta pequeña;
- usa `enumerate` para las posiciones y `zip` estricto para emparejar
  longitudes iguales;
- trata de forma explícita el estado y el agotamiento de los iteradores; y
- usa un generador solo con un límite deliberado en el consumidor y un
  responsable de la limpieza definido de forma explícita.

Antes de continuar, explica un pipeline en voz alta: dónde se originan los
valores, dónde vive el estado, qué detiene el consumo, qué fallo es recuperable
y quién limpia. Si cada respuesta es concreta, la sintaxis ya no es magia:
estás diseñando el flujo de datos.
