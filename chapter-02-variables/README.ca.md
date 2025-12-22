# Capítol 2 · Variables i tipus de dades simples

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
En aquest capítol construirem el vocabulari essencial de Python: entendrem què passa quan executes `hello_world.py`, crearem i canviarem variables, netejarem cadenes, treballarem amb nombres i escriurem comentaris amb sentit. Acabarem amb una introducció breu al “Zen de Python”, la manera de pensar que t’ajudarà a escriure codi clar.

## Ordre pedagògic
1. **Model mental de l’intèrpret** → sense això, la resta sembla màgia.
2. **Variables com a etiquetes** → abans de manipular dades, cal posar bons noms.
3. **Cadenes (strings)** → el tipus més comú, amb format, espais i errors típics.
4. **Nombres** → operacions, floats i constants.
5. **Comentaris i Zen** → mantenir el codi comprensible.
6. **Exercicis “Prova-ho tu”** per practicar cada idea.

## Objectius d’aprenentatge
- Descriure pas a pas què fa l’intèrpret quan executa `hello_world.py`.
- Declarar, reasignar i anomenar variables seguint regles professionals.
- Manipular cadenes (majúscules, espais, prefixos) i nombres (int, float) sense sorpreses.
- Documentar el codi amb comentaris útils i interioritzar el Zen de Python.

## Per què importa
Tots els programes guarden i transformen dades. Entendre com Python interpreta els teus fitxers, com “apunta” una variable a un valor i com triar bons noms evita errors difícils, redueix temps de depuració i prepara el camí per a estructures com llistes i diccionaris.

### Mini aventura
Imagina que cada variable és una etiqueta enganxada a una capsa: avui l’enganxes a la capsa de “missatges”, demà la mous a “puntuació”. Python no posa coses “dins” l’etiqueta: l’etiqueta només assenyala on és el valor. Si entens això, deixes de barallar-te amb el codi i comences a controlar-lo.

---

## 1. Què passa quan executes `hello_world.py`
```python
# hello_world.py
print("Hello Python world!")
```
Quan executes `python hello_world.py`:
1. El sufix `.py` indica que és un script de Python.
2. L’editor crida l’intèrpret, que llegeix el fitxer, el compila a *bytecode* i executa cada instrucció.
3. Quan troba `print("…")`, envia el text a la sortida estàndard.
4. L’editor usa *syntax highlighting* per diferenciar funcions (`print`) de literals (`"Hello..."`). Vigila els colors: sovint avisen d’errors com cometes sense tancar.

### Mini experiment
```python
message = "Hello Python world!"
print(message)

message = "Hello Python Crash Course world!"
print(message)
```
Resultat:
```
Hello Python world!
Hello Python Crash Course world!
```
L’intèrpret associa `message` amb el primer literal, després actualitza l’etiqueta i torna a imprimir. Python sempre conserva el valor més recent.

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

## 2. Anomenar i usar variables
Regles clau:
- Lletres, números i `_`. No poden començar amb número (`message_1` ✔, `1_message` ✘).
- Sense espais; usa `_` per separar paraules (`greeting_message`).
- No reutilitzis paraules reservades o noms de funcions (`print`, `list`).
- Millor noms curts però descriptius (`name` > `n`; `student_name` > `s_n`).
- Evita confondre `l` (ela minúscula) i `O` (o majúscula) amb `1` i `0`.

> Nota: usa minúscules per defecte. Més endavant veurem quan usar majúscules (constants).

### 2.1 Reconèixer el tipus d’una variable
Python dedueix el tipus de cada valor, però el pots inspeccionar amb `type()` o comprovar contra classes concretes amb `isinstance()`.

```python
username = "ada"
age = 28
temperature = 20.5

print(type(username))          # <class 'str'>
print(type(age))               # <class 'int'>
print(isinstance(age, int))    # True
print(isinstance(temperature, float))  # True
print(isinstance(age, (int, float)))   # True (coincideix amb algun dels tipus)
```

`isinstance` accepta una tupla de tipus: és útil quan vols permetre enters i flotants, o quan una funció admet diverses classes compatibles.

### 2.2 Validar que una funció rep dades correctes
Quan dissenyes funcions, és bona idea fallar aviat si els arguments no són els esperats. Aquesta versió comprova que `base` i `altura` siguin números abans de calcular l’àrea:

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

Aquest patró deixa clar què s’espera i com es tracten valors invàlids. També pots afegir anotacions de tipus (`def calcular_area_rectangulo(base: float, altura: float) -> float:`) perquè editors i linters avisin abans.

### 2.3 Provar les precondicions (mini test)
Encara que estiguem als primers capítols, escriure proves petites dona confiança immediata. Amb `pytest` n’hi ha prou amb funcions `test_…` que cridin el teu codi:

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

`pytest.raises` confirma que es llança l’excepció adequada. L’important és documentar les precondicions i comprovar-les automàticament.

---

## 3. Evitar `NameError` i entendre les etiquetes
```python
message = "Hello Python Crash Course reader!"
print(mesage)  # typo
```
Sortida:
```
Traceback (most recent call last):
  File "hello_world.py", line 2, in <module>
    print(mesage)
NameError: name 'mesage' is not defined. Did you mean: 'message'?
```
Python mostra:
1. Fitxer i línia amb el problema.
2. La línia exacta ressaltada.
3. Tipus d’error (`NameError`) i suggeriment.

Si el typo passa tant a la definició com a l’ús:
```python
mesage = "Hello..."
print(mesage)
```
El programa s’executa perquè les etiquetes coincideixen. Conclusió: pensa en les variables com **etiquetes** que apunten a valors, no com capses. L’intèrpret exigeix que el nom coincideixi literalment.

---

## 4. Prova-ho tu (variables bàsiques)
- **2-1 · Simple Message**: `simple_message.py` → assigna un missatge i mostra’l.
- **2-2 · Simple Messages**: `simple_messages.py` → imprimeix un missatge, canvia la variable i torna a imprimir.

---

## 5. Cadenes (strings)

### 5.1 Canviar majúscules/minúscules
```python
name = "ada lovelace"
print(name.title())
print(name.upper())
print(name.lower())
```
`title()` posa cada paraula amb inicial majúscula; `upper()` i `lower()` ajuden a normalitzar entrades.

### 5.2 Variables dins cadenes (f-strings)
```python
first_name = "ada"
last_name = "lovelace"
full_name = f"{first_name} {last_name}"
print(f"Hello, {full_name.title()}!")
message = f"Hello, {full_name.title()}!"
print(message)
```
Posa `f` davant de la cadena i `{}` al voltant de les variables.

### 5.3 Tabs i salts de línia
```python
print("Python")
print("\tPython")
print("Languages:\nPython\nC\nJavaScript")
print("Languages:\n\tPython\n\tC\n\tJavaScript")
```

### 5.4 Eliminar espais en blanc
```python
favorite_language = "python "
print(favorite_language.rstrip())   # temporal
favorite_language = favorite_language.rstrip()  # permanent

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

### 5.5 Treure prefixos / sufixos
```python
nostarch_url = "https://nostarch.com"
print(nostarch_url.removeprefix("https://"))

filename = "python_notes.txt"
print(filename.removesuffix(".txt"))
```

### 5.6 Subcadenes (slicing): tallar text amb seguretat
En Python, una cadena és una **seqüència** de caràcters. Això vol dir que pots:
- agafar un caràcter per **índex** (`text[0]`)
- agafar una **subcadena** (slice) amb `text[inici:fi]`

Imagina que talles un entrepà: `inici` és on comences, `fi` és on pares (i **`fi` no s’inclou**).

#### 5.6.1 Indexació (un caràcter)
```python
word = "python"
print(word[0])   # p
print(word[-1])  # n (últim caràcter)
```

Si l’índex surt del rang, Python llança `IndexError`.

#### 5.6.2 Slicing (una subcadena)
```python
word = "python"
print(word[0:2])   # 'py'  (0 i 1)
print(word[2:])    # 'thon' (de 2 fins al final)
print(word[:3])    # 'pyt'  (de l’inici fins a 2)
print(word[-3:])   # 'hon'  (els 3 últims)
```

#### 5.6.3 Slicing amb passos (divertit + útil)
```python
word = "abcdefgh"
print(word[::2])   # 'aceg' (cada 2 caràcters)
print(word[::-1])  # 'hgfedcba' (invertit)
```

#### 5.6.4 Buscar subcadenes (comprovacions eficients)
Per comprovar coses simples, no tallis “a mà”; usa l’eina correcta:

```python
email = "ada@example.com"
print("@" in email)                 # True
print(email.startswith("ada"))      # True
print(email.endswith(".com"))       # True
print(email.find("@"))              # 3 (posició) o -1 si no hi és
```

#### 5.6.5 Construir strings amb eficiència: `join`
Si construeixes text en un bucle, evita repetir `+` (crea moltes cadenes temporals). Ajunta peces i fes `join`:

```python
words = ["python", "is", "fun"]
sentence = " ".join(words)
print(sentence)  # python is fun
```

### Reptes extra (subcadenes)
Exercicis ràpids i pràctics per dominar el slicing.

1. **2-S1 · Emmascarar un email**
   ```python
   def mask_email(email):
       # TODO: retorna una cosa com:
       # "a***@example.com" per "ada@example.com"
       # Cas límit: si no hi ha "@", llença ValueError
       pass
   ```
   *Pista*: busca la posició de `"@"` i talla amb slicing.

2. **2-S2 · Extensió de fitxer**
   ```python
   def extension(filename):
       # TODO: retorna "txt" per "notes.txt"
       # Cas límit: sense punt → retorna "" (cadena buida)
       pass
   ```
   *Pista*: `rfind(".")` troba l’últim punt.

3. **2-S3 · Palíndrom (bonus divertit)**
   ```python
   def is_palindrome(text):
       # TODO: ignora espais i majúscules/minúscules
       # Exemple: "Anita lava la tina" -> True
       pass
   ```
   *Pista*: `clean = text.replace(" ", "").lower()` i compara amb `clean[::-1]`.

### Errors comuns amb subcadenes
- Off‑by‑one: `text[a:b]` no inclou `b`.
- `find()` retorna `-1` si no troba (no és un error).
- Casos buits: slicing sobre `""` va bé, però indexar `""[0]` no.

### 5.7 Evitar `SyntaxError` amb cometes
```python
message = "One of Python's strengths is its diverse community."  # ✔
# message = 'One of Python's strengths...'  # ✘: la cometa interior trenca la cadena
```
Un `SyntaxError: unterminated string literal` sol indicar cometes mal emparellades. Observa el *syntax highlighting*; si l’editor coloreja text normal com a codi, revisa les cometes.

---

## 6. Prova-ho tu (strings)
- **2-3 · Personal Message**: `personal_message.py` → usa una variable `name` i envia una salutació.
- **2-4 · Name Cases**: `name_cases.py` → imprimeix el nom en minúscules, majúscules i format títol.
- **2-5 · Famous Quote**: `famous_quote.py` → mostra una cita amb cometes i autor.
- **2-6 · Famous Quote 2**: `famous_quote_2.py` → usa `famous_person` + `message`.
- **2-7 · Stripping Names**: `stripping_names.py` → inclou `\t` i `\n`, després aplica `lstrip()`, `rstrip()`, `strip()`.
- **2-8 · File Extensions**: `file_extensions.py` → `filename.removesuffix(".txt")`.

---

## 7. Nombres

### 7.1 Enters (`int`)
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

### 7.2 Flotants (`float`)
```python
print(0.1 + 0.2)
print(3 * 0.1)
```
A vegades veuràs `0.3000000004` per la representació binària. No t’hi encaparris ara; més endavant aprendrem a formatejar resultats.

### 7.3 Barrejar enters i flotants
```python
print(4 / 2)      # 2.0
print(1 + 2.0)    # 3.0
print(3.0 ** 2)   # 9.0
```
Si hi ha un `float` a l’operació, el resultat serà `float`.

```python
# shipping_cost.py
package_weight_kg = 2
price_per_kg = 4.5
fuel_surcharge = 1.2  # Factor flotante

base_cost = package_weight_kg * price_per_kg
final_cost = base_cost * fuel_surcharge

print(f"Costo final: {final_cost:.2f} €")
```

### 7.4 Guions baixos en nombres llargs
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

### 7.5 Assignació múltiple
```python
x, y, z = 0, 0, 0
```
Assegura’t que la quantitat de valors coincideix amb la de variables.

### 7.6 Constants
```python
MAX_CONNECTIONS = 5000
```
Convenció: majúscules per indicar que “no hauria de canviar”.

---

## 8. Prova-ho tu (nombres)
- **2-9 · Number Eight**: `number_eight.py` → quatre operacions diferents que donin 8.
- **2-10 · Favorite Number**: `favorite_number.py` → guarda el teu número preferit i genera un missatge.

---

## 9. Comentaris
```python
# Say hello to everyone.
print("Hello Python people!")
```
Tot el que va després de `#` s’ignora. Usa comentaris per explicar decisions, supòsits o passos no evidents. És més fàcil esborrar comentaris sobrants que reconstruir el teu raonament mesos després.

### Prova-ho tu
- **2-11 · Adding Comments**: agafa dos programes previs i afegeix com a mínim un comentari significatiu (nom, data, propòsit).

---

## 10. El Zen de Python
`import this` imprimeix 19 principis de Tim Peters. Alguns destacats:
- **Beautiful is better than ugly.**
- **Simple is better than complex.**
- **Readability counts.**
- **Now is better than never.**

### Prova-ho tu
- **2-12 · Zen of Python**: executa `import this` a la terminal i tria una frase que vulguis aplicar aquesta setmana.

---

## Solucions comentades (selecció)
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

## Errors comuns
- Fer ombra a funcions built‑in (`list = []`).
- Concatenar cadenes i enters sense conversió.
- Deixar espais/tabs que trenquen comparacions de strings.
- Dependre de la memòria per recordar què volen dir els nombres (falta de comentaris).
- Cometes mal emparellades que provoquen `SyntaxError`.

---

## Reflexió final
Ara pots explicar què fa l’intèrpret, usar variables com a etiquetes, formatejar cadenes, netejar espais, operar amb nombres i justificar el codi amb comentaris. També coneixes la mentalitat del Zen de Python per mantenir-ho simple. Al **Capítol 3** emmagatzemarem col·leccions completes de dades amb **llistes** i aprendrem a recórrer-les, modificar-les i ordenar-les.
