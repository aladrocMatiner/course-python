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

## Prerequisits i rutes
- **Prerequisit:** completa el checkpoint del [capítol 1](../chapter-01-introduction/README.ca.md) i aprèn a executar un fitxer `.py`. La ruta essencial no requereix funcions, condicionals, excepcions ni testing.
- **Ruta essencial · 45–60 min:** seccions 1, 2.1, 3, 4, 5.1–5.5, 7–9 i el checkpoint final. Resultat: un petit script de perfil amb variables clares, text net i aritmètica, sense `if`, `def`, `try` ni `raise`. Acabes quan els casos de nom normal i buit produeixen la sortida indicada i et pots recuperar del `NameError` deliberat; llavors pots aturar-te amb seguretat o continuar al capítol 3.
- **Preview opcional de subcadenes · 20–30 min:** després del checkpoint essencial, executa els blocs proporcionats a la secció 5.6 i observa que fer slicing d'una cadena buida és segur i que `find()` retorna `-1` si falta el delimitador. Els reptes extra usen conceptes posteriors i no formen part d'aquesta ruta; torna-hi després de [condicionals](../chapter-08-conditionals/README.ca.md), [funcions](../chapter-11-functions/README.ca.md) i [excepcions](../chapter-14-exceptions/README.ca.md).
- **Preview professional opcional · 25–35 min:** seccions 2.2–2.3. Resultat: copiar i inspeccionar validació i tests, o ometre'ls sense bloquejar el checkpoint. Estudia'n els conceptes després als capítols 8, 11, 14 i 18.

## Per què importa
Tots els programes guarden i transformen dades. Entendre com Python interpreta els teus fitxers, com “apunta” una variable a un valor i com triar bons noms evita errors difícils, redueix temps de depuració i prepara el camí per a estructures com llistes i diccionaris.

### Mini aventura
Imagina que cada variable és una etiqueta enganxada a una capsa: avui l’enganxes a la capsa de “missatges”, demà la mous a “puntuació”. Python no posa coses “dins” l’etiqueta: l’etiqueta només assenyala on és el valor. Si entens això, deixes de barallar-te amb el codi i comences a controlar-lo.

## Predicció abans d'executar
Llegeix els dos primers exemples sense executar-los. Prediu quantes línies imprimeix cadascun i quin valor té `message` després de reasignar-lo. Després executa'ls i explica qualsevol diferència entre la predicció i la sortida observada.

---

## 1. Què passa quan executes `hello_world.py`
```python runnable
# hello_world.py
print("Hello Python world!")
```
Quan executes `python hello_world.py`:
1. El shell o editor demana a l'intèrpret de Python seleccionat que obri la ruta `hello_world.py`. El sufix `.py` és una convenció útil, no allò que fa executable el fitxer per a Python.
2. CPython llegeix el codi, el compila a *bytecode* i executa les instruccions.
3. Quan troba `print("…")`, envia el text a la sortida estàndard.
4. L'editor pot usar *syntax highlighting* per diferenciar funcions (`print`) de literals (`"Hello..."`). Els colors només són una ajuda visual; executar l'intèrpret és el que valida la sintaxi.

### Mini experiment
```python runnable
message = "Hello Python world!"
print(message)

message = "Hello Python Crash Course world!"
print(message)
```
Resultat:
```text illustrative
Hello Python world!
Hello Python Crash Course world!
```
L’intèrpret associa `message` amb el primer literal, després actualitza l’etiqueta i torna a imprimir. Python sempre conserva el valor més recent.

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

```python runnable
username = "noor"
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
**Preview opcional:** aquesta subsecció combina funcions, condicionals i excepcions abans de les lliçons completes. Per ara, `def` anomena una acció reutilitzable, `if` comprova una regla i `raise` s'atura amb un error anomenat. Pots copiar l'exemple complet o saltar a la secció 3. Continua després a [condicionals](../chapter-08-conditionals/README.ca.md), [funcions](../chapter-11-functions/README.ca.md) i [excepcions](../chapter-14-exceptions/README.ca.md).

Quan dissenyes funcions, és bona idea fallar aviat si els arguments no són els esperats. Aquesta versió comprova que `base` i `altura` siguin números abans de calcular l’àrea:

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

Aquest patró deixa clar què s'espera i com es tracten valors invàlids. El rebuig explícit de `bool` importa perquè Python tracta `True` i `False` com a subclasses d'enters, però aquí no són dimensions amb sentit. Més endavant pots reforçar el contracte amb anotacions de tipus (`def calcular_area_rectangulo(base: float, altura: float) -> float:`).

### 2.3 Provar les precondicions (mini test)
**Preview opcional:** `pytest` és una eina de tercers que es presenta i s'instal·la al [capítol de testing](../chapter-18-testing/README.ca.md). La ruta essencial no la necessita. Si no està instal·lada, llegeix o omet aquest bloc; no descarreguis un instal·lador no relacionat.

Les proves petites donen confiança. Amb `pytest` n'hi ha prou amb funcions `test_…` que cridin el teu codi:

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

`pytest.raises` confirma que es llança l'excepció adequada. Sense `pytest`, omet aquest preview: executar un fitxer que només defineix tests no els executa automàticament. La idea important és que cada precondició necessita un exemple normal, un de límit i un d'invàlid.

---

## 3. Evitar `NameError` i entendre les etiquetes
<!-- bookcheck: expect-error="NameError" -->
```python expected-error
message = "Hello Python Crash Course reader!"
print(mesage)  # typo
```
Sortida:
```text illustrative
Traceback (most recent call last):
  File "hello_world.py", line 2, in <module>
    print(mesage)
NameError: name 'mesage' is not defined. Did you mean: 'message'?
```
Python mostra:
1. Fitxer i línia amb el problema.
2. La línia exacta ressaltada.
3. El senyal estable `NameError` i el nom desconegut `mesage`. El text exacte i el suggeriment poden variar entre versions de Python.

Aquest és un **error esperat**, no un exemple d'èxit executable. Per recuperar-te, fes que el nom usat coincideixi amb el nom assignat i torna a executar:

```python runnable
message = "Hello Python Crash Course reader!"
print(message)
```

```text output
Hello Python Crash Course reader!
```

Si el typo passa tant a la definició com a l’ús:
```python runnable
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
```python runnable
name = "noor lovelace"
print(name.title())
print(name.upper())
print(name.lower())
```
`title()` posa cada paraula amb inicial majúscula; `upper()` i `lower()` ajuden a normalitzar entrades.

### 5.2 Variables dins cadenes (f-strings)
```python runnable
first_name = "noor"
last_name = "lovelace"
full_name = f"{first_name} {last_name}"
print(f"Hello, {full_name.title()}!")
message = f"Hello, {full_name.title()}!"
print(message)
```
Posa `f` davant de la cadena i `{}` al voltant de les variables.

### 5.3 Tabs i salts de línia
```python runnable
print("Python")
print("\tPython")
print("Languages:\nPython\nC\nJavaScript")
print("Languages:\n\tPython\n\tC\n\tJavaScript")
```

### 5.4 Eliminar espais en blanc
```python runnable
favorite_language = "python "
print(favorite_language.rstrip())   # temporal
favorite_language = favorite_language.rstrip()  # permanent

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

Els claudàtors fan visibles els espais exteriors. Decidir si un nom buit és vàlid requereix un condicional, així que aquesta decisió espera al [capítol 8](../chapter-08-conditionals/README.ca.md); la ruta essencial només observa el valor net.

### 5.5 Treure prefixos / sufixos
```python runnable
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
```python runnable
word = "python"
print(word[0])   # p
print(word[-1])  # n (últim caràcter)
```

Si l’índex surt del rang, Python llança `IndexError`.

#### 5.6.2 Slicing (una subcadena)
```python runnable
word = "python"
print(word[0:2])   # 'py'  (0 i 1)
print(word[2:])    # 'thon' (de 2 fins al final)
print(word[:3])    # 'pyt'  (de l’inici fins a 2)
print(word[-3:])   # 'hon'  (els 3 últims)
```

#### 5.6.3 Slicing amb passos (divertit + útil)
```python runnable
word = "abcdefgh"
print(word[::2])   # 'aceg' (cada 2 caràcters)
print(word[::-1])  # 'hgfedcba' (invertit)
```

#### 5.6.4 Buscar subcadenes (comprovacions eficients)
Per comprovar coses simples, no tallis “a mà”; usa l’eina correcta:

```python runnable
email = "noor@example.com"
print("@" in email)                 # True
print(email.startswith("noor"))     # True
print(email.endswith(".com"))       # True
print(email.find("@"))              # 3 (posició) o -1 si no hi és
```

#### 5.6.5 Construir strings amb eficiència: `join`
Si construeixes text en un bucle, evita repetir `+` (crea moltes cadenes temporals). Ajunta peces i fes `join`:

```python runnable
words = ["python", "is", "fun"]
sentence = " ".join(words)
print(sentence)  # python is fun
```

### Reptes extra (subcadenes)
Exercicis ràpids i pràctics per dominar el slicing.

**Pràctica posterior opcional:** aquests TODO usen funcions, condicionals i excepcions. No pertanyen al checkpoint essencial. Omet-los ara i torna-hi després dels capítols 8, 11 i 14; pots completar el capítol sense ells.

1. **2-S1 · Emmascarar un email**
   ```python todo
   def mask_email(email):
       # TODO: retorna una cosa com:
       # "n***@example.com" per "noor@example.com"
       # Cas límit: si no hi ha "@", llença ValueError
       pass
   ```
   *Pista*: busca la posició de `"@"` i talla amb slicing.

2. **2-S2 · Extensió de fitxer**
   ```python todo
   def extension(filename):
       # TODO: retorna "txt" per "notes.txt"
       # Cas límit: sense punt → retorna "" (cadena buida)
       pass
   ```
   *Pista*: `rfind(".")` troba l’últim punt.

3. **2-S3 · Palíndrom (bonus divertit)**
   ```python todo
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
```python runnable
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

### 7.2 Flotants (`float`)
```python runnable
print(0.1 + 0.2)
print(3 * 0.1)
```
A vegades veuràs `0.30000000000000004` perquè moltes fraccions decimals no es poden representar exactament en coma flotant binària. No t'hi amoïnis ara; més endavant aprendrem a formatar resultats i comparar floats de manera segura.

### 7.3 Barrejar enters i flotants
```python runnable
print(4 / 2)      # 2.0
print(1 + 2.0)    # 3.0
print(3.0 ** 2)   # 9.0
```
Si hi ha un `float` a l’operació, el resultat serà `float`.

```python runnable
# shipping_cost.py
package_weight_kg = 2
price_per_kg = 4.5
fuel_surcharge = 1.2  # Factor flotante

base_cost = package_weight_kg * price_per_kg
final_cost = base_cost * fuel_surcharge

print(f"Costo final: {final_cost:.2f} €")
```

### 7.4 Guions baixos en nombres llargs
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

### 7.5 Assignació múltiple
```python runnable
x, y, z = 0, 0, 0
```
Assegura’t que la quantitat de valors coincideix amb la de variables.

### 7.6 Constants
```python runnable
MAX_CONNECTIONS = 5000
```
Convenció: majúscules per indicar que “no hauria de canviar”.

---

## 8. Prova-ho tu (nombres)
- **2-9 · Number Eight**: `number_eight.py` → quatre operacions diferents que donin 8.
- **2-10 · Favorite Number**: `favorite_number.py` → guarda el teu número preferit i genera un missatge.

---

## 9. Comentaris
```python runnable
# Say hello to everyone.
print("Hello Python people!")
```
Tot el que va després de `#` s’ignora. Usa comentaris per explicar decisions, supòsits o passos no evidents. És més fàcil esborrar comentaris sobrants que reconstruir el teu raonament mesos després.

### Prova-ho tu: comentaris
- **2-11 · Adding Comments**: agafa dos programes previs i afegeix com a mínim un comentari significatiu (nom, data, propòsit).

---

## 10. El Zen de Python
`import this` imprimeix 19 principis de Tim Peters. Alguns destacats:
- **Beautiful is better than ugly.** El codi pot ser elegant i convé que ho sigui.
- **Simple is better than complex.** Si la versió senzilla funciona, tria-la.
- **Complex is better than complicated.** Quan la realitat és complexa, tria la solució més clara.
- **Readability counts.** Facilita que una altra persona pugui seguir el teu raonament.
- **There should be one—and preferably only one—obvious way to do it.** La col·laboració és més fàcil quan les solucions convergeixen.
- **Now is better than never.** No esperis a «saber-ho tot» abans de construir.

### Prova-ho tu: Zen de Python
- **2-12 · Zen of Python**: executa `import this` a la terminal i tria una frase que vulguis aplicar aquesta setmana.

---

## Solucions comentades (selecció)
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

## Errors comuns
- Fer ombra a funcions built‑in (`list = []`).
- Concatenar cadenes i enters sense conversió.
- Deixar espais/tabs que trenquen comparacions de strings.
- Dependre de la memòria per recordar què volen dir els nombres (falta de comentaris).
- Cometes mal emparellades que provoquen `SyntaxError`.

---

## Checkpoint i autoavaluació
Crea un únic `profile.py` usant només assignació, mètodes de text, aritmètica, f-strings i `print`. Abans de completar les línies que falten, prediu les tres línies de sortida.

### TODO guiat

```python todo
raw_name = "  Noor  "
age = 14

# TODO 1: crea clean_name eliminant els espais exteriors de raw_name.
# TODO 2: crea next_age sumant 1 a age.
# TODO 3: imprimeix "Profile: [Noor]" i "Next year: 15" amb f-strings.

empty_raw_name = " \t\n "
# TODO 4: neteja empty_raw_name i imprimeix "Empty profile: []".
```

**Pista:** `strip()` retorna una cadena nova; assigna aquest resultat a una variable nova i descriptiva. El cas buit usa la mateixa operació que el normal: no cal cap condicional.

El cas normal ha de conservar `Noor` i calcular `15`. El cas límit és una cadena que només conté espais; després de `strip()` ha de quedar buida, per això els claudàtors es toquen: `[]`.

### Error recuperable

Després de completar el TODO, canvia temporalment un ús de `clean_name` per `clean_nam`:

<!-- bookcheck: expect-error="NameError" -->
```python expected-error
raw_name = "  Noor  "
clean_name = raw_name.strip()
print(f"Profile: [{clean_nam}]")
```

L'execució s'ha d'aturar amb el senyal estable `NameError` i identificar `clean_nam`. Per recuperar-te, restaura la `e` final; aquí no necessites `try`/`except`. Després usa aquesta solució explicada:

### Solució explicada

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

`strip()` produeix un valor net sense canviar `raw_name`, de manera que `clean_name` fa visible la transformació. `age + 1` produeix el valor següent sense canviar el significat d'`age`. La mateixa neteja funciona al límit: una cadena formada només per espais es converteix en `""`, i els claudàtors fan observable aquest resultat buit.

### Verificació i rúbrica

Executa `python profile.py` després de la reparació i comprova que la sortida coincideix exactament amb les tres línies anteriors.

Suma un punt per criteri:
- **Correcció:** els casos de nom normal i buit imprimeixen les tres línies indicades.
- **Llegibilitat:** cada variable descriu el valor anterior o posterior a la neteja.
- **Recuperació de l'error:** identifiques `clean_nam`, restaures `clean_name` i aconsegueixes una execució correcta.
- **Verificació:** compares les tres línies observades amb la teva predicció.
- **Explicació:** expliques amb les teves paraules per què `strip()` produeix `[]` al cas límit i per què corregir l'etiqueta elimina el `NameError`.

La ruta essencial acaba amb 5/5. No requereix condicionals, funcions, gestió d'excepcions ni tests.

---

## Reflexió final
Quina predicció ha canviat després d'executar els casos normal, límit i reparat? Explica per què la mateixa expressió amb `strip()` pot netejar un nom visible i un altre format només per espais sense usar `if`.

Ara pots explicar què fa l’intèrpret, usar variables com a etiquetes, formatejar cadenes, netejar espais, operar amb nombres i recuperar-te d'un error de nom. També coneixes la mentalitat del Zen de Python per mantenir-ho simple. Al **Capítol 3** emmagatzemarem col·leccions completes de dades amb **llistes** i aprendrem a recórrer-les, modificar-les i ordenar-les.
