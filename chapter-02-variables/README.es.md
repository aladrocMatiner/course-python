# Capítulo 2 · Variables y Tipos de Datos Simples

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
En este capítulo levantaremos el vocabulario esencial de Python: entenderemos qué sucede al ejecutar `hello_world.py`, crearemos y renombraremos variables, limpiaremos cadenas, trabajaremos con números y escribiremos comentarios significativos. Todo culmina con una breve introducción al “Zen de Python”, la filosofía que guiará el resto del curso.

## Orden pedagógico
1. **Modelo mental del intérprete** → sin esto, el resto parece magia.
2. **Variables como etiquetas** → antes de manipular datos necesitamos nombrarlos bien.
3. **Cadenas (strings)** → el tipo más común, con formato, espacios y errores clásicos.
4. **Números** → operaciones, floats y constantes.
5. **Comentarios y Zen** → mantener el código comprensible.
6. **Ejercicios “Pruébalo tú”** escalonados para practicar cada idea.

## Objetivos de aprendizaje
- Describir paso a paso qué hace el intérprete cuando corre `hello_world.py`.
- Declarar, reasignar y nombrar variables siguiendo reglas profesionales.
- Manipular cadenas (mayúsculas, espacios, prefijos) y números (int, float) sin sorpresas.
- Documentar el código con comentarios útiles e interiorizar el Zen de Python.

## Prerrequisitos y rutas
- **Prerrequisito:** completa el checkpoint del [capítulo 1](../chapter-01-introduction/README.es.md) y aprende a ejecutar un archivo `.py`. La ruta esencial no requiere funciones, condicionales, excepciones ni testing.
- **Ruta esencial · 45–60 min:** secciones 1, 2.1, 3, 4, 5.1–5.5, 7–9 y el checkpoint final. Resultado: un pequeño script de perfil con variables claras, texto limpio y aritmética, sin `if`, `def`, `try` ni `raise`. Terminas cuando los casos de nombre normal y vacío producen la salida indicada y puedes recuperarte del `NameError` deliberado; entonces puedes parar con seguridad o continuar al capítulo 3.
- **Preview opcional de subcadenas · 20–30 min:** después del checkpoint esencial, ejecuta los bloques dados en la sección 5.6 y observa que cortar una cadena vacía es seguro y que `find()` devuelve `-1` si falta el delimitador. Los retos extra usan conceptos posteriores y no forman parte de esta ruta; vuelve a ellos después de [condicionales](../chapter-08-conditionals/README.es.md), [funciones](../chapter-11-functions/README.es.md) y [excepciones](../chapter-14-exceptions/README.es.md).
- **Preview profesional opcional · 25–35 min:** secciones 2.2–2.3. Resultado: copiar e inspeccionar validación y tests, u omitirlos sin bloquear el checkpoint. Estudia sus conceptos después en los capítulos 8, 11, 14 y 18.

## Por qué importa
Todo programa almacena y transforma datos. Comprender cómo Python interpreta tus archivos, dónde se guardan los valores y cómo elegir buenos nombres evita errores difíciles, reduce el tiempo de depuración y prepara el camino para estructuras más complejas como listas y diccionarios.

### Mini aventura
Imagina que cada variable es una etiqueta adhesiva en una caja: hoy la pegas en la caja de “mensajes”, mañana la cambias a “puntuación”. Python no mete cosas “dentro” de la etiqueta: la etiqueta solo señala dónde está el valor. Si entiendes esto, dejas de pelearte con el código y empiezas a controlarlo.

## Predicción antes de ejecutar
Lee los dos primeros ejemplos sin ejecutarlos. Predice cuántas líneas imprime cada uno y qué valor tiene `message` después de reasignarlo. Después ejecútalos y explica cualquier diferencia entre tu predicción y la salida observada.

---

## 1. Qué ocurre al ejecutar `hello_world.py`
```python runnable
# hello_world.py
print("Hello Python world!")
```
Cuando ejecutas `python hello_world.py`:
1. El shell o editor pide al intérprete de Python seleccionado que abra la ruta `hello_world.py`. El sufijo `.py` es una convención útil, no lo que hace ejecutable el archivo para Python.
2. CPython lee el código, lo compila a *bytecode* y ejecuta las instrucciones.
3. Al encontrar `print("…")`, envía el texto a la salida estándar.
4. El editor puede usar *syntax highlighting* para diferenciar funciones (`print`) de literales (`"Hello..."`). Los colores son solo una ayuda visual; ejecutar el intérprete es lo que valida la sintaxis.

### Mini experimento
```python runnable
message = "Hello Python world!"
print(message)

message = "Hello Python Crash Course world!"
print(message)
```
Resultado:
```text illustrative
Hello Python world!
Hello Python Crash Course world!
```
El intérprete asocia `message` con el primer literal, luego actualiza la etiqueta y vuelve a imprimir. Python siempre conserva el valor más reciente.

```python runnable
# multiple_messages.py
message = "Bienvenida a Python"
print(message)

message = "Seguimos aprendiendo variables"
print(message)

print(f"Último mensaje: {message}")
```

```python runnable
# variable_trace.py
step = 0
log = "Iniciando"

print(f"{step}: {log}")

step += 1
log = "Descargando dataset"
print(f"{step}: {log}")

step += 1
log = "Procesando datos"
print(f"{step}: {log}")
```

---

## 2. Nombrar y usar variables
Reglas clave:
- Letras, números y `_`. No pueden iniciar con número (`message_1` ✔, `1_message` ✘).
- Sin espacios; usa `_` para separar palabras (`greeting_message`).
- No reutilices palabras reservadas o nombres de funciones (`print`, `list`).
- Prefiere nombres cortos pero descriptivos (`name` > `n`; `student_name` > `s_n`).
- Evita confundir `l` (ele minúscula) y `O` (o mayúscula) con `1` y `0`.

> Nota: usa minúsculas por defecto. Más adelante veremos cuándo usar mayúsculas (constantes).

### 2.1 Reconocer el tipo de una variable
Python infiere el tipo de cada valor, pero puedes inspeccionarlo con `type()` o comparar contra clases concretas usando `isinstance()`.

```python runnable
username = "noor"
age = 28
temperature = 20.5

print(type(username))          # <class 'str'>
print(type(age))               # <class 'int'>
print(isinstance(age, int))    # True
print(isinstance(temperature, float))  # True
print(isinstance(age, (int, float)))   # True (pertenece a alguno de los tipos)
```

`isinstance` acepta una tupla de tipos: útil cuando quieres permitir números enteros y flotantes, o cuando creas funciones que aceptan múltiples clases compatibles.

### 2.2 Validar que una función recibe los datos correctos
**Preview opcional:** esta subsección combina funciones, condicionales y excepciones antes de sus lecciones completas. Por ahora, `def` nombra una acción reutilizable, `if` comprueba una regla y `raise` se detiene con un error nombrado. Puedes copiar el ejemplo completo o saltar a la sección 3. Continúa después en [condicionales](../chapter-08-conditionals/README.es.md), [funciones](../chapter-11-functions/README.es.md) y [excepciones](../chapter-14-exceptions/README.es.md).

Al diseñar funciones conviene fallar pronto si los argumentos no cumplen lo esperado. Esta versión comprueba que `base` y `altura` sean números antes de calcular el área:

```python runnable
def is_real_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def calcular_area_rectangulo(base, altura):
    if not is_real_number(base):
        raise TypeError("base debe ser numérica")
    if not is_real_number(altura):
        raise TypeError("altura debe ser numérica")
    if base <= 0 or altura <= 0:
        raise ValueError("las dimensiones deben ser positivas")

    return base * altura
```

Ese patrón hace obvio qué tipo de datos se esperan y cómo se manejan valores inválidos. El rechazo explícito de `bool` importa porque Python trata `True` y `False` como subclases de enteros, pero aquí no son dimensiones con sentido. Más adelante puedes reforzar el contrato con anotaciones de tipo (`def calcular_area_rectangulo(base: float, altura: float) -> float:`).

### 2.3 Probar las precondiciones (mini test)
**Preview opcional:** `pytest` es una herramienta de terceros que se presenta e instala en el [capítulo de testing](../chapter-18-testing/README.es.md). La ruta esencial no la necesita. Si no está instalada, lee u omite este bloque; no descargues un instalador no relacionado.

Los tests pequeños dan confianza. Con `pytest` bastan funciones `test_…` que llamen a tu código:

```python illustrative
# tests/test_rectangulos.py
import pytest
from area import calcular_area_rectangulo

def test_calcular_area_rectangulo_valores_validos():
    assert calcular_area_rectangulo(3, 4) == 12

def test_calcular_area_rectangulo_rechaza_strings():
    with pytest.raises(TypeError):
        calcular_area_rectangulo("10", 5)

def test_calcular_area_rectangulo_rechaza_negativos():
    with pytest.raises(ValueError):
        calcular_area_rectangulo(-1, 2)

def test_calcular_area_rectangulo_rechaza_booleanos():
    with pytest.raises(TypeError):
        calcular_area_rectangulo(True, 3)
```

`pytest.raises` confirma que se lanza la excepción adecuada. Sin `pytest`, omite este preview: ejecutar un archivo que solo define tests no los ejecuta automáticamente. La idea importante es que cada precondición necesita un ejemplo normal, uno límite y uno inválido.

---

## 3. Evitar NameError y entender las etiquetas
<!-- bookcheck: expect-error="NameError" -->
```python expected-error
message = "Hello Python Crash Course reader!"
print(mesage)  # typo
```
Salida:
```text illustrative
Traceback (most recent call last):
  File "hello_world.py", line 2, in <module>
    print(mesage)
NameError: name 'mesage' is not defined. Did you mean: 'message'?
```
Python muestra:
1. Archivo y línea con problema.
2. Línea exacta resaltada.
3. La señal estable `NameError` y el nombre desconocido `mesage`. El texto exacto y la sugerencia pueden variar entre versiones de Python.

Este es un **error esperado**, no un ejemplo de éxito ejecutable. Para recuperarte, haz que el nombre usado coincida con el asignado y vuelve a ejecutar:

```python runnable
message = "Hello Python Crash Course reader!"
print(message)
```

```text output
Hello Python Crash Course reader!
```

Si el typo ocurre tanto en la definición como en el uso:
```python runnable
mesage = "Hello..."
print(mesage)
```
El programa se ejecuta porque las etiquetas coinciden. Conclusión: piensa en las variables como **etiquetas** que apuntan a valores, no como cajas. El intérprete exige consistencia literal en el nombre.

---

## 4. Pruébalo tú (variables básicas)
- **2-1 · Simple Message**: `simple_message.py` → asigna un mensaje y muéstralo.
- **2-2 · Simple Messages**: `simple_messages.py` → imprime un mensaje, cambia la variable y vuelve a imprimir.

---

## 5. Cadenas (strings)

### 5.1 Cambiar mayúsculas/minúsculas
```python runnable
name = "noor lovelace"
print(name.title())
print(name.upper())
print(name.lower())
```
`title()` capitaliza cada palabra; `upper()` y `lower()` estandarizan entradas de usuarios.

### 5.2 Variables dentro de cadenas (f-strings)
```python runnable
first_name = "noor"
last_name = "lovelace"
full_name = f"{first_name} {last_name}"
print(f"Hello, {full_name.title()}!")
message = f"Hello, {full_name.title()}!"
print(message)
```
Coloca `f` antes de la cadena y `{}` alrededor de las variables.

### 5.3 Tabs y saltos de línea
```python runnable
print("Python")
print("\tPython")
print("Languages:\nPython\nC\nJavaScript")
print("Languages:\n\tPython\n\tC\n\tJavaScript")
```

### 5.4 Eliminar espacios en blanco
```python runnable
favorite_language = "python "
print(favorite_language.rstrip())   # temporal
favorite_language = favorite_language.rstrip()  # permanente

favorite_language = " python "
print(favorite_language.rstrip())
print(favorite_language.lstrip())
print(favorite_language.strip())
```

```python runnable
# username_cleaner.py
raw_username = "  \tTaha\n"
clean_username = raw_username.strip()
print(f"Raw username: [{raw_username}]")
print(f"Clean username: [{clean_username}]")
```

Los corchetes hacen visibles los espacios exteriores. Decidir si un nombre vacío es válido requiere un condicional, así que esa decisión espera al [capítulo 8](../chapter-08-conditionals/README.es.md); la ruta esencial solo observa el valor limpio.

### 5.5 Remover prefijos / sufijos
```python runnable
nostarch_url = "https://nostarch.com"
print(nostarch_url.removeprefix("https://"))

filename = "python_notes.txt"
print(filename.removesuffix(".txt"))
```

### 5.6 Subcadenas (slicing): cortar texto con seguridad
En Python, un string es una **secuencia** de caracteres. Eso significa que puedes:
- tomar un carácter por **índice** (`text[0]`)
- tomar una **subcadena** (slice) con `text[inicio:fin]`

Imagina que cortas un bocadillo: `inicio` es donde empiezas, `fin` es donde paras (y **fin no se incluye**).

#### 5.6.1 Indexación (un carácter)
```python runnable
word = "python"
print(word[0])   # p
print(word[-1])  # n (último carácter)
```

Si el índice se sale del rango, Python lanza `IndexError`.

#### 5.6.2 Slicing (una subcadena)
```python runnable
word = "python"
print(word[0:2])   # 'py'  (0 y 1)
print(word[2:])    # 'thon' (desde 2 hasta el final)
print(word[:3])    # 'pyt'  (desde el inicio hasta 2)
print(word[-3:])   # 'hon'  (los 3 últimos)
```

#### 5.6.3 Slicing con pasos (divertido + útil)
```python runnable
word = "abcdefgh"
print(word[::2])   # 'aceg' (cada 2 caracteres)
print(word[::-1])  # 'hgfedcba' (invertido)
```

#### 5.6.4 Buscar subcadenas (comprobaciones eficientes)
Para comprobar cosas simples, no cortes “a mano”; usa la herramienta correcta:

```python runnable
email = "noor@example.com"
print("@" in email)                 # True
print(email.startswith("noor"))     # True
print(email.endswith(".com"))       # True
print(email.find("@"))              # 3 (posición) o -1 si no aparece
```

#### 5.6.5 Construir strings con eficiencia: `join`
Si construyes texto en un bucle, evita repetir `+` (crea muchas cadenas temporales). Junta piezas y usa `join`:

```python runnable
words = ["python", "is", "fun"]
sentence = " ".join(words)
print(sentence)  # python is fun
```

### Retos extra (subcadenas)
Ejercicios rápidos y prácticos para dominar los slices.

**Práctica posterior opcional:** estos TODO usan funciones, condicionales y excepciones. No pertenecen al checkpoint esencial. Omítelos ahora y vuelve después de los capítulos 8, 11 y 14; puedes completar el capítulo sin ellos.

1. **2-S1 · Enmascarar un email**
   ```python todo
   def mask_email(email):
       # TODO: devuelve algo como:
       # "n***@example.com" para "noor@example.com"
       # Caso borde: si no hay "@", lanza ValueError
       pass
   ```
   *Pista*: busca la posición de `"@"` y corta con slicing.

2. **2-S2 · Extensión de archivo**
   ```python todo
   def extension(filename):
       # TODO: devuelve "txt" para "notes.txt"
       # Caso borde: sin punto → devuelve "" (cadena vacía)
       pass
   ```
   *Pista*: `rfind(".")` encuentra el último punto.

3. **2-S3 · Palíndromo (bonus divertido)**
   ```python todo
   def is_palindrome(text):
       # TODO: ignora espacios y mayúsculas/minúsculas
       # Ejemplo: "Anita lava la tina" -> True
       pass
   ```
   *Pista*: `clean = text.replace(" ", "").lower()` y compara con `clean[::-1]`.

### Errores comunes con subcadenas
- Off‑by‑one: `text[a:b]` no incluye `b`.
- `find()` devuelve `-1` si no encuentra (no es un error).
- Casos vacíos: slicing sobre `""` va bien, pero indexar `""[0]` no.

### 5.7 Evitar SyntaxError con comillas
```python runnable
message = "One of Python's strengths is its diverse community."  # ✔
# message = 'One of Python's strengths...'  # ✘: comilla interior rompe la cadena
```
Un `SyntaxError: unterminated string literal` suele indicar comillas mal emparejadas. Observa el *syntax highlighting*; si el editor colorea texto ordinario como código, revisa tus comillas.

---

## 6. Pruébalo tú (strings)
- **2-3 · Personal Message**: `personal_message.py` → usa una variable `name` y envía un saludo.
- **2-4 · Name Cases**: `name_cases.py` → imprime nombre en minúsculas, mayúsculas y formato título.
- **2-5 · Famous Quote**: `famous_quote.py` → muestra una cita con comillas y autor.
- **2-6 · Famous Quote 2**: `famous_quote_2.py` → usa `famous_person` + `message`.
- **2-7 · Stripping Names**: `stripping_names.py` → incluye `\t` y `\n`, luego aplica `lstrip()`, `rstrip()`, `strip()`.
- **2-8 · File Extensions**: `file_extensions.py` → `filename.removesuffix(".txt")`.

---

## 7. Números

### 7.1 Enteros (`int`)
```python runnable
print(2 + 3)
print(3 - 2)
print(2 * 3)
print(3 / 2)
print(3 ** 2)
print((2 + 3) * 4)
```

```python runnable
# score_tracker.py
initial_score = 0
bonus = 15
penalty = 3

score = initial_score + bonus - penalty
print(f"Puntos finales: {score}")
```

### 7.2 Flotantes (`float`)
```python runnable
print(0.1 + 0.2)
print(3 * 0.1)
```
A veces verás `0.30000000000000004` porque muchas fracciones decimales no se pueden representar exactamente en coma flotante binaria. No te preocupes todavía; más adelante veremos cómo formatear resultados y comparar floats de forma segura.

### 7.3 Mezclar enteros y flotantes
```python runnable
print(4 / 2)      # 2.0
print(1 + 2.0)    # 3.0
print(3.0 ** 2)   # 9.0
```
Si hay un `float` en la operación, el resultado será `float`.

```python runnable
# shipping_cost.py
package_weight_kg = 2
price_per_kg = 4.5
fuel_surcharge = 1.2  # Factor flotante

base_cost = package_weight_kg * price_per_kg
final_cost = base_cost * fuel_surcharge

print(f"Costo final: {final_cost:.2f} €")
```

### 7.4 Guiones bajos en números largos
```python runnable
universe_age = 14_000_000_000
print(universe_age)  # 14000000000
```

```python runnable
# budget_overview.py
quarter_budget = 2_500_000
spend_to_date = 1_875_430
remaining = quarter_budget - spend_to_date

print(f"Presupuesto restante: {remaining:,} €")
```

### 7.5 Asignación múltiple
```python runnable
x, y, z = 0, 0, 0
```
Asegúrate de que la cantidad de valores coincida con la de variables.

### 7.6 Constantes
```python runnable
MAX_CONNECTIONS = 5000
```
Convención: mayúsculas para indicar que no debería cambiar.

---

## 8. Pruébalo tú (números)
- **2-9 · Number Eight**: `number_eight.py` → cuatro operaciones distintas que produzcan 8.
- **2-10 · Favorite Number**: `favorite_number.py` → guarda tu número favorito y genera un mensaje.

---

## 9. Comentarios
```python runnable
# Say hello to everyone.
print("Hello Python people!")
```
Todo lo que sigue al `#` se ignora. Usa comentarios para explicar decisiones, supuestos o pasos no obvios. Es más fácil borrar comentarios sobrantes que reconstruir tu razonamiento meses después.

### Pruébalo tú: comentarios
- **2-11 · Adding Comments**: toma dos programas previos y agrega al menos un comentario significativo (nombre, fecha, propósito).

---

## 10. El Zen de Python
`import this` imprime 19 principios de Tim Peters. Algunos destacados:
- **Beautiful is better than ugly.** El código puede y debe ser elegante.
- **Simple is better than complex.** Si la versión simple funciona, elige esa.
- **Complex is better than complicated.** Cuando la realidad es compleja, busca la solución más clara posible.
- **Readability counts.** Prioriza que otra persona pueda seguir tu razonamiento.
- **There should be one—and preferably only one—obvious way to do it.** Las soluciones deben converger, facilitando la colaboración.
- **Now is better than never.** No esperes a “saberlo todo” para construir.

### Pruébalo tú: Zen de Python
- **2-12 · Zen of Python**: ejecuta `import this` en la terminal y quédate con una frase que quieras aplicar esta semana.

---

## Soluciones comentadas (selección)
```python runnable
# trace_run.py
step = 1
print(f"{step}. Iniciando programa")
step += 1
print(f"{step}. Trabajando…")
step += 1
print(f"{step}. Finalizado")
# Razonamiento: usamos una variable para ver el orden de ejecución.
```

```python runnable
# profile.py
first_name = "Noor"
last_name = "Frej"
age = 14
full_name = f"{first_name} {last_name}"
print(full_name)
print(f"El año que viene tendrás {age + 1}.")
# Razonamiento: separar piezas facilita los cambios y permite reutilizar datos.
```

```python runnable
# time_math.py
days_per_week = 7        # Cambia a 5 si necesitas semana laboral
hours_per_day = 24
minutes_per_hour = 60
minutes_per_week = days_per_week * hours_per_day * minutes_per_hour
print(f"Minutos en la semana: {minutes_per_week}")
# Razonamiento: los comentarios explican “números mágicos”.
```

---

## Errores comunes
- Sombras funciones built-in (`list = []`).
- Concatenar cadenas y enteros sin conversión.
- Dejar espacios o tabs extra que rompen comparaciones de strings.
- Depender de la memoria para recordar qué significan los números (falta de comentarios).
- Comillas mal emparejadas que provocan `SyntaxError`.

---

## Checkpoint y autoevaluación
Crea un único `profile.py` usando solo asignación, métodos de texto, aritmética, f-strings y `print`. Antes de completar las líneas que faltan, predice las tres líneas de salida.

### TODO guiado

```python todo
raw_name = "  Noor  "
age = 14

# TODO 1: crea clean_name eliminando los espacios exteriores de raw_name.
# TODO 2: crea next_age sumando 1 a age.
# TODO 3: imprime "Profile: [Noor]" y "Next year: 15" con f-strings.

empty_raw_name = " \t\n "
# TODO 4: limpia empty_raw_name e imprime "Empty profile: []".
```

**Pista:** `strip()` devuelve una cadena nueva; asigna ese resultado a una variable nueva y descriptiva. El caso vacío usa la misma operación que el normal: no hace falta ningún condicional.

El caso normal debe conservar `Noor` y calcular `15`. El caso límite es una cadena que solo contiene espacios; después de `strip()` debe quedar vacía, por eso los corchetes se tocan: `[]`.

### Error recuperable

Tras completar el TODO, cambia temporalmente un uso de `clean_name` por `clean_nam`:

<!-- bookcheck: expect-error="NameError" -->
```python expected-error
raw_name = "  Noor  "
clean_name = raw_name.strip()
print(f"Profile: [{clean_nam}]")
```

La ejecución debe detenerse con la señal estable `NameError` e identificar `clean_nam`. Para recuperarte, restaura la `e` final; aquí no necesitas `try`/`except`. Después usa esta solución explicada:

### Solución explicada

```python runnable
# profile.py
raw_name = "  Noor  "
age = 14

clean_name = raw_name.strip()
next_age = age + 1
print(f"Profile: [{clean_name}]")
print(f"Next year: {next_age}")

empty_raw_name = " \t\n "
empty_clean_name = empty_raw_name.strip()
print(f"Empty profile: [{empty_clean_name}]")
```

```text output
Profile: [Noor]
Next year: 15
Empty profile: []
```

`strip()` produce un valor limpio sin cambiar `raw_name`, de modo que `clean_name` hace visible la transformación. `age + 1` produce el valor siguiente sin cambiar el significado de `age`. La misma limpieza funciona en el límite: una cadena formada solo por espacios se convierte en `""`, y los corchetes hacen observable ese resultado vacío.

### Verificación y rúbrica

Ejecuta `python profile.py` después de la reparación y comprueba que su salida coincide exactamente con las tres líneas anteriores.

Suma un punto por criterio:
- **Corrección:** los casos de nombre normal y vacío imprimen las tres líneas indicadas.
- **Legibilidad:** cada variable describe el valor anterior o posterior a la limpieza.
- **Recuperación del error:** identificas `clean_nam`, restauras `clean_name` y logras una ejecución correcta.
- **Verificación:** comparas las tres líneas observadas con tu predicción.
- **Explicación:** explicas con tus palabras por qué `strip()` produce `[]` en el caso límite y por qué corregir la etiqueta elimina el `NameError`.

La ruta esencial termina con 5/5. No requiere condicionales, funciones, manejo de excepciones ni tests.

---

## Reflexión final
¿Qué predicción cambió después de ejecutar los casos normal, límite y reparado? Explica por qué la misma expresión con `strip()` puede limpiar un nombre visible y otro formado solo por espacios sin usar `if`.

Ahora puedes explicar qué hace el intérprete, usar variables como etiquetas, formatear cadenas, limpiar espacios, operar con números y recuperarte de un error de nombre. Además, conoces la mentalidad del Zen de Python para mantenerlo simple. En el **Capítulo 3** almacenaremos colecciones completas de datos usando **listas** y aprenderemos a recorrerlas, modificarlas y ordenarlas. Mantén a mano estos ejemplos; los reutilizaremos muy pronto.
