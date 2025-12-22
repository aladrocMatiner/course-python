# Capítulo 2 · Variables y Tipos de Datos Simples

## Qué vamos a construir
En este capítulo levantaremos el vocabulario esencial de Python: entenderemos qué sucede al ejecutar `hello_world.py`, crearemos y renombraremos variables, limpiaremos cadenas, trabajaremos con números y escribiremos comentarios significativos. Todo culmina con una breve introducción al “Zen de Python”, la filosofía que guiará el resto del curso.

## Orden pedagógico
1. **Modelo mental del intérprete** → sin esto, el resto parece magia.
2. **Variables como etiquetas** → antes de manipular datos necesitamos nombrarlos bien.
3. **Strings** → el tipo más común, con formato, espacios y errores clásicos.
4. **Números** → operaciones, floats y constantes.
5. **Comentarios y Zen** → mantener el código comprensible.
6. **Ejercicios “Try it yourself”** escalonados para practicar cada idea.

## Objetivos de aprendizaje
- Describir paso a paso qué hace el intérprete cuando corre `hello_world.py`.
- Declarar, reasignar y nombrar variables siguiendo reglas profesionales.
- Manipular cadenas (mayúsculas, espacios, prefijos) y números (int, float) sin sorpresas.
- Documentar el código con comentarios útiles e interiorizar el Zen de Python.

## Por qué importa
Todo programa almacena y transforma datos. Comprender cómo Python interpreta tus archivos, dónde se guardan los valores y cómo elegir buenos nombres evita errores difíciles, reduce el tiempo de depuración y prepara el camino para estructuras más complejas como listas y diccionarios.

### Mini aventura
Imagina que cada variable es una etiqueta adhesiva en una caja: hoy la pegas en la caja de “mensajes”, mañana la cambias a “puntuación”. Python no mete cosas “dentro” de la etiqueta: la etiqueta solo señala dónde está el valor. Si entiendes esto, dejas de pelearte con el código y empiezas a controlarlo.

---

## 1. Qué ocurre al ejecutar `hello_world.py`
```python
# hello_world.py
print("Hello Python world!")
```
Cuando ejecutas `python hello_world.py`:
1. El sufijo `.py` indica que es un script de Python.
2. Tu editor invoca al intérprete, que lee el archivo, lo compila a *bytecode* y ejecuta cada instrucción.
3. Al encontrar `print("…")`, envía el texto a la salida estándar.
4. El editor usa *syntax highlighting* para diferenciar funciones (`print`) de literales (`"Hello..."`). Vigila estos colores; te alertan de errores comunes como comillas sin cerrar.

### Mini experimento
```python
message = "Hello Python world!"
print(message)

message = "Hello Python Crash Course world!"
print(message)
```
Resultado:
```
Hello Python world!
Hello Python Crash Course world!
```
El intérprete asocia `message` con el primer literal, luego actualiza la etiqueta y vuelve a imprimir. Python siempre conserva el valor más reciente.

```python
# multiple_messages.py
message = "Bienvenida a Python"
print(message)

message = "Seguimos aprendiendo variables"
print(message)

print(f"Último mensaje: {message}")
```

```python
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

```python
username = "ada"
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
Al diseñar funciones conviene fallar pronto si los argumentos no cumplen lo esperado. Esta versión comprueba que `base` y `altura` sean números antes de calcular el área:

```python
def calcular_area_rectangulo(base, altura):
    if not isinstance(base, (int, float)):
        raise TypeError("base debe ser numérica")
    if not isinstance(altura, (int, float)):
        raise TypeError("altura debe ser numérica")
    if base <= 0 or altura <= 0:
        raise ValueError("las dimensiones deben ser positivas")

    return base * altura
```

Ese patrón hace obvio qué tipo de datos se esperan y cómo se manejan valores inválidos. Puedes reforzarlo con anotaciones de tipo (`def calcular_area_rectangulo(base: float, altura: float) -> float:`) para que editores y linters avisen antes.

### 2.3 Probar las precondiciones (mini test)
Aunque todavía estamos en capítulos iniciales, escribir pruebas pequeñas te da confianza inmediata. Con `pytest` bastan funciones `test_…` que llamen a tu código:

```python
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
```

`pytest.raises` confirma que se lanza la excepción adecuada. Incluso sin `pytest`, puedes ejecutar el módulo manualmente y verificar que los `raise` aparecen. Lo importante es documentar las precondiciones y comprobarlas automáticamente.

---

## 3. Evitar NameError y entender las etiquetas
```python
message = "Hello Python Crash Course reader!"
print(mesage)  # typo
```
Salida:
```
Traceback (most recent call last):
  File "hello_world.py", line 2, in <module>
    print(mesage)
NameError: name 'mesage' is not defined. Did you mean: 'message'?
```
Python muestra:
1. Archivo y línea con problema.
2. Línea exacta resaltada.
3. Tipo de error (`NameError`) y sugerencia.

Si el typo ocurre tanto en la definición como en el uso:
```python
mesage = "Hello..."
print(mesage)
```
El programa se ejecuta porque las etiquetas coinciden. Conclusión: piensa en las variables como **etiquetas** que apuntan a valores, no como cajas. El intérprete exige consistencia literal en el nombre.

---

## 4. Pruébalo tú (variables básicas)
- **2-1 · Simple Message**: `simple_message.py` → asigna un mensaje y muéstralo.
- **2-2 · Simple Messages**: `simple_messages.py` → imprime un mensaje, cambia la variable y vuelve a imprimir.

---

## 5. Strings

### 5.1 Cambiar mayúsculas/minúsculas
```python
name = "ada lovelace"
print(name.title())
print(name.upper())
print(name.lower())
```
`title()` capitaliza cada palabra; `upper()` y `lower()` estandarizan entradas de usuarios.

### 5.2 Variables dentro de cadenas (f-strings)
```python
first_name = "ada"
last_name = "lovelace"
full_name = f"{first_name} {last_name}"
print(f"Hello, {full_name.title()}!")
message = f"Hello, {full_name.title()}!"
print(message)
```
Coloca `f` antes de la cadena y `{}` alrededor de las variables.

### 5.3 Tabs y saltos de línea
```python
print("Python")
print("\tPython")
print("Languages:\nPython\nC\nJavaScript")
print("Languages:\n\tPython\n\tC\n\tJavaScript")
```

### 5.4 Eliminar espacios en blanco
```python
favorite_language = "python "
print(favorite_language.rstrip())   # temporal
favorite_language = favorite_language.rstrip()  # permanente

favorite_language = " python "
print(favorite_language.rstrip())
print(favorite_language.lstrip())
print(favorite_language.strip())
```

```python
# username_cleaner.py
raw_username = "  \tAda.Lovelace\n"
clean_username = raw_username.strip()

if clean_username:
    print(f"Usuario válido: {clean_username}")
else:
    print("Nombre vacío; solicita de nuevo.")
```

### 5.5 Remover prefijos / sufijos
```python
nostarch_url = "https://nostarch.com"
print(nostarch_url.removeprefix("https://"))

filename = "python_notes.txt"
print(filename.removesuffix(".txt"))
```

### 5.6 Evitar SyntaxError con comillas
```python
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
```python
print(2 + 3)
print(3 - 2)
print(2 * 3)
print(3 / 2)
print(3 ** 2)
print((2 + 3) * 4)
```

```python
# score_tracker.py
initial_score = 0
bonus = 15
penalty = 3

score = initial_score + bonus - penalty
print(f"Puntos finales: {score}")
```

### 7.2 Flotantes (`float`)
```python
print(0.1 + 0.2)
print(3 * 0.1)
```
A veces verás `0.3000000004` por la representación binaria. Ignóralo por ahora; más adelante veremos cómo formatear resultados.

### 7.3 Mezclar enteros y flotantes
```python
print(4 / 2)      # 2.0
print(1 + 2.0)    # 3.0
print(3.0 ** 2)   # 9.0
```
Si hay un `float` en la operación, el resultado será `float`.

```python
# shipping_cost.py
package_weight_kg = 2
price_per_kg = 4.5
fuel_surcharge = 1.2  # Factor flotante

base_cost = package_weight_kg * price_per_kg
final_cost = base_cost * fuel_surcharge

print(f"Costo final: {final_cost:.2f} €")
```

### 7.4 Guiones bajos en números largos
```python
universe_age = 14_000_000_000
print(universe_age)  # 14000000000
```

```python
# budget_overview.py
quarter_budget = 2_500_000
spend_to_date = 1_875_430
remaining = quarter_budget - spend_to_date

print(f"Presupuesto restante: {remaining:,} €")
```

### 7.5 Asignación múltiple
```python
x, y, z = 0, 0, 0
```
Asegúrate de que la cantidad de valores coincida con la de variables.

### 7.6 Constantes
```python
MAX_CONNECTIONS = 5000
```
Convención: mayúsculas para indicar que no debería cambiar.

---

## 8. Pruébalo tú (números)
- **2-9 · Number Eight**: `number_eight.py` → cuatro operaciones distintas que produzcan 8.
- **2-10 · Favorite Number**: `favorite_number.py` → guarda tu número favorito y genera un mensaje.

---

## 9. Comentarios
```python
# Say hello to everyone.
print("Hello Python people!")
```
Todo lo que sigue al `#` se ignora. Usa comentarios para explicar decisiones, supuestos o pasos no obvios. Es más fácil borrar comentarios sobrantes que reconstruir tu razonamiento meses después.

### Pruébalo tú
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

### Pruébalo tú
- **2-12 · Zen of Python**: ejecuta `import this` en la terminal y quédate con una frase que quieras aplicar esta semana.

---

## Soluciones comentadas (selección)
```python
# trace_run.py
step = 1
print(f"{step}. Iniciando programa")
step += 1
print(f"{step}. Trabajando…")
step += 1
print(f"{step}. Finalizado")
# Razonamiento: usamos una variable para ver el orden de ejecución.
```

```python
# profile.py
first_name = "Ada"
last_name = "Lovelace"
age = 28
full_name = f"{first_name} {last_name}"
print(full_name)
print(f"El año que viene tendrás {age + 1}.")
# Razonamiento: separar piezas facilita los cambios y permite reutilizar datos.
```

```python
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

## Reflexión final
Ahora puedes explicar qué hace el intérprete, usar variables como etiquetas, formatear cadenas, limpiar espacios, operar con números y justificar tu código con comentarios. Además, conoces la mentalidad del Zen de Python para mantenerlo simple. En el **Capítulo 3** almacenaremos colecciones completas de datos usando **listas** y aprenderemos a recorrerlas, modificarlas y ordenarlas. Mantén a mano estos ejemplos; los reutilizaremos muy pronto.
