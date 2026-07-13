# Kapitel 2 · Variabler och enkla datatyper

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

I kapitlet bygger vi Pythons grundläggande ordförråd. Vi undersöker vad som händer när `hello_world.py` körs, skapar och byter värden på variabler, rensar strängar, arbetar med tal och skriver meningsfulla kommentarer. Till sist får du en kort introduktion till ”The Zen of Python”, tankesättet som följer oss genom kursen.

## Lärväg

1. **En mental modell av tolken** – utan den känns resten som magi.
2. **Variabler som etiketter** – innan data bearbetas behöver saker tydliga namn.
3. **Strängar** – den vanligaste typen, med formatering, blanksteg och klassiska misstag.
4. **Tal** – operationer, flyttal och konstanter.
5. **Kommentarer och Zen** – håll koden begriplig.
6. **Öva själv** med uppgifter som blir gradvis svårare.

## Lärandemål

- Förklara steg för steg vad tolken gör när `hello_world.py` körs.
- Deklarera, tilldela om och namnge variabler enligt professionella regler.
- Hantera strängar (skiftläge, blanksteg och prefix) och tal (`int`, `float`) utan överraskningar.
- Dokumentera kod med användbara kommentarer och ta till dig Zen of Python.

## Förkunskaper och vägar

- **Förkunskap:** slutför kontrollpunkten i [kapitel 1](../chapter-01-introduction/README.sv.md) och lär dig köra en `.py`-fil. Grundvägen kräver inte funktioner, villkor, undantag eller tester.
- **Grundväg · 45–60 min:** avsnitt 1, 2.1, 3–5, 7 och 9. Resultat: ett litet profilskript med tydliga variabler, rensad text och aritmetik.
- **Mellanväg · 25–35 min:** lägg till slicing och delsträngsutmaningarna. Resultat: hantera en tom sträng och en avgränsare som saknas.
- **Frivillig professionell förhandsblick · 25–35 min:** avsnitt 2.2–2.3. Resultat: kopiera och granska validering/tester, eller hoppa över dem utan att blockera kontrollpunkten.

## Varför det spelar roll

Alla program lagrar och omvandlar data. När du förstår hur Python läser filer, var värden ”finns” och hur bra namn väljs undviker du svårfunna fel, felsöker snabbare och blir redo för samlingar som listor och dictionaries.

### Miniäventyr

Tänk att varje variabel är en flyttbar etikett på en låda. I dag pekar den på ”meddelanden”, i morgon på ”poäng”. Python lägger inte värdet inuti etiketten; etiketten pekar på värdet. Med den modellen kan du styra koden i stället för att kämpa mot den.

## Förutsäg före körning

Läs de två första exemplen utan att köra dem. Förutsäg hur många rader varje exempel skriver ut och vilket värde `message` har efter omtilldelningen. Kör sedan och förklara varje skillnad mellan förutsägelsen och den observerade utdata.

---

## 1. Vad händer när `hello_world.py` körs?

```python runnable
# hello_world.py
print("Hello Python world!")
```

När du kör `python hello_world.py`:

1. Skalet eller editorn ber den valda Python-tolken att öppna sökvägen `hello_world.py`. Ändelsen `.py` är en användbar konvention, inte det som gör filen körbar för Python.
2. CPython läser källkoden, kompilerar den till *bytecode* och kör instruktionerna.
3. Vid `print("…")` skickas text till standard output.
4. Editorn kan använda *syntax highlighting* för att skilja funktioner (`print`) från litteraler (`"Hello..."`). Färgerna är bara ett visuellt stöd; det är körningen i tolken som validerar syntaxen.

### Miniexperiment

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

Tolken kopplar `message` till den första litteralen, flyttar sedan etiketten till det nya värdet och skriver ut igen. Det senaste tilldelade värdet gäller alltid.

```python runnable
# multiple_messages.py
message = "Welcome to Python"
print(message)

message = "We keep learning variables"
print(message)

print(f"Último mensaje: {message}")
```

```python runnable
# variable_trace.py
step = 0
log = "Starting"

print(f"{step}: {log}")

step += 1
log = "Downloading dataset"
print(f"{step}: {log}")

step += 1
log = "Processing data"
print(f"{step}: {log}")
```

---

## 2. Namnge och använda variabler

Viktiga regler:

- Använd bokstäver, siffror och `_`, men börja inte med en siffra (`message_1` ✔, `1_message` ✘).
- Använd inga mellanslag; skilj ord med `_`, till exempel `greeting_message`.
- Återanvänd inte reserverade ord eller funktionsnamn som `print` och `list`.
- Välj korta men beskrivande namn (`name` är bättre än `n`; `student_name` är bättre än `s_n`).
- Undvik att blanda ihop lilla `l` och stora `O` med `1` och `0`.

> Obs: använd gemener som standard. Senare ser vi när versaler passar, nämligen för konstanter.

### 2.1 Kontrollera en variabels typ

Python härleder typer, men du kan inspektera dem med `type()` eller kontrollera konkreta klasser med `isinstance()`.

```python runnable
username = "noor"
age = 28
temperature = 20.5

print(type(username))          # <class 'str'>
print(type(age))               # <class 'int'>
print(isinstance(age, int))    # True
print(isinstance(temperature, float))  # True
print(isinstance(age, (int, float)))   # True (it matches one of the types)
```

`isinstance` kan ta en tuple av typer. Det är praktiskt när både heltal och flyttal tillåts eller när en funktion accepterar flera kompatibla klasser.

### 2.2 Kontrollera att en funktion får rätt data

**Frivillig förhandsblick:** det här avsnittet kombinerar funktioner, villkor och undantag före de fullständiga lektionerna. Just nu räcker det att veta att `def` namnger en återanvändbar handling, `if` kontrollerar en regel och `raise` avbryter med ett namngivet fel. Kopiera hela exemplet eller hoppa till avsnitt 3. Fortsätt senare med [villkor](../chapter-08-conditionals/README.sv.md), [funktioner](../chapter-11-functions/README.sv.md) och [undantag](../chapter-14-exceptions/README.sv.md).

När du utformar funktioner är det bra att misslyckas tidigt om argumenten inte uppfyller kontraktet. Här kontrolleras att `base` och `altura` är tal innan arean beräknas:

```python runnable
def is_real_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def calcular_area_rectangulo(base, altura):
    if not is_real_number(base):
        raise TypeError("base must be numeric")
    if not is_real_number(altura):
        raise TypeError("height must be numeric")
    if base <= 0 or altura <= 0:
        raise ValueError("dimensions must be positive")

    return base * altura
```

Mönstret gör förväntningarna tydliga och visar hur ogiltiga värden hanteras. Det uttryckliga förbudet mot `bool` behövs eftersom Python behandlar `True` och `False` som underklasser till heltal, men de är inte meningsfulla mått här. Type hints kan senare förstärka kontraktet, exempelvis `def calcular_area_rectangulo(base: float, altura: float) -> float:`.

### 2.3 Testa förvillkoren (minitest)

**Frivillig förhandsblick:** `pytest` är ett tredjepartsverktyg som presenteras och installeras i det lokaliserade [testkapitlet](../chapter-18-testing/README.sv.md). Grundvägen behöver det inte. Om det inte är installerat läser eller hoppar du över blocket; hämta inte ett orelaterat installationsskript.

Små tester ger snabb trygghet. Med `pytest` skriver du funktioner vars namn börjar med `test_` och som anropar koden:

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

`pytest.raises` bekräftar att rätt undantag kastas. Utan `pytest` hoppar du över förhandsblicken; en fil som bara definierar tester kör dem inte automatiskt. Den viktiga idén är att varje förvillkor behöver ett normalt, ett gräns- och ett ogiltigt exempel.

---

## 3. Undvika NameError och förstå ”etiketter”

```python illustrative
message = "Hello Python Crash Course reader!"
print(mesage)  # typo
```

Utdata:

```text illustrative
Traceback (most recent call last):
  File "hello_world.py", line 2, in <module>
    print(mesage)
NameError: name 'mesage' is not defined. Did you mean: 'message'?
```

Python visar:

1. Filen och raden där problemet uppstod.
2. Den exakta markerade raden.
3. Feltypen (`NameError`) och ett förslag.

Om samma stavfel finns både vid definition och användning:

```python runnable
mesage = "Hello..."
print(mesage)
```

…körs programmet, eftersom etiketterna stämmer överens. Slutsats: tänk på variabler som **etiketter** som pekar på värden, inte som lådor. Namnet måste stämma exakt.

---

## 4. Prova själv (grundläggande variabler)

- **2-1 · Enkelt meddelande**: `simple_message.py` → tilldela ett meddelande och skriv ut det.
- **2-2 · Enkla meddelanden**: `simple_messages.py` → skriv ut, ändra variabeln och skriv ut igen.

---

## 5. Strängar

### 5.1 Ändra skiftläge

```python runnable
name = "noor lovelace"
print(name.title())
print(name.upper())
print(name.lower())
```

`title()` gör varje ord till titelstil; `upper()` och `lower()` hjälper till att normalisera användarindata.

### 5.2 Variabler inuti strängar (f-strängar)

```python runnable
first_name = "noor"
last_name = "lovelace"
full_name = f"{first_name} {last_name}"
print(f"Hello, {full_name.title()}!")
message = f"Hello, {full_name.title()}!"
print(message)
```

Sätt `f` före strängen och omge variablerna med `{}`.

### 5.3 Tabbar och nya rader

```python runnable
print("Python")
print("\tPython")
print("Languages:\nPython\nC\nJavaScript")
print("Languages:\n\tPython\n\tC\n\tJavaScript")
```

### 5.4 Ta bort omgivande whitespace

```python runnable
favorite_language = "python "
print(favorite_language.rstrip())   # temporary
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

if clean_username:
    print(f"Valid user: {clean_username}")
else:
    print("Empty name; ask again.")
```

### 5.5 Ta bort prefix och suffix

```python runnable
nostarch_url = "https://nostarch.com"
print(nostarch_url.removeprefix("https://"))

filename = "python_notes.txt"
print(filename.removesuffix(".txt"))
```

### 5.6 Delsträngar (slicing): skär text säkert

En sträng är en **sekvens** av tecken. Du kan därför:

- hämta ett tecken med ett **index**, exempelvis `text[0]`
- hämta en **delsträng**, en slice, med `text[start:end]`

Tänk dig att skära en smörgås: `start` är där snittet börjar och `end` där det slutar, men **end ingår inte**.

#### 5.6.1 Indexering (ett tecken)

```python runnable
word = "python"
print(word[0])   # p
print(word[-1])  # n (last character)
```

Ligger indexet utanför intervallet höjer Python `IndexError`.

#### 5.6.2 Slicing (en delsträng)

```python runnable
word = "python"
print(word[0:2])   # 'py'  (0 and 1)
print(word[2:])    # 'thon' (from 2 to the end)
print(word[:3])    # 'pyt'  (from start to 2)
print(word[-3:])   # 'hon'  (last 3)
```

#### 5.6.3 Slicing med steg (roligt och användbart)

```python runnable
word = "abcdefgh"
print(word[::2])   # 'aceg' (every 2nd char)
print(word[::-1])  # 'hgfedcba' (reversed)
```

#### 5.6.4 Hitta delsträngar med rätt verktyg

Skär inte manuellt för enkla kontroller; använd uttrycksfulla operationer:

```python runnable
email = "noor@example.com"
print("@" in email)                 # True
print(email.startswith("noor"))     # True
print(email.endswith(".com"))       # True
print(email.find("@"))              # 3 (position) or -1 if not found
```

#### 5.6.5 Bygga strängar effektivt med `join`

Om text byggs i en loop bör upprepad `+` undvikas eftersom många tillfälliga strängar skapas. Samla delarna och sammanfoga dem:

```python runnable
words = ["python", "is", "fun"]
sentence = " ".join(words)
print(sentence)  # python is fun
```

### Extra utmaningar med delsträngar

Det här är korta, praktiska övningar som ökar svårigheten gradvis.

1. **2-S1 · Maskera en e-postadress**

   ```python todo
   def mask_email(email):
       # TODO: return something like:
       # "n***@example.com" for "noor@example.com"
       # Edge case: if there's no "@", raise ValueError
       pass
   ```

   *Ledtråd*: hitta positionen för `"@"` och använd slices runt den.

2. **2-S2 · Filändelse**

   ```python todo
   def extension(filename):
       # TODO: return "txt" for "notes.txt"
       # Edge case: no dot → return "" (empty string)
       pass
   ```

   *Ledtråd*: `rfind(".")` hittar den sista punkten.

3. **2-S3 · Palindromkontroll (frivillig bonus)**

   ```python todo
   def is_palindrome(text):
       # TODO: ignore spaces and case
       # Example: "Anita lava la tina" -> True
       pass
   ```

   *Ledtråd*: skapa `clean = text.replace(" ", "").lower()` och jämför med `clean[::-1]`.

### Vanliga misstag med delsträngar

- Off-by-one: `text[a:b]` innehåller inte position `b`.
- Resultatet från `find()` misstolkas; `-1` betyder ”hittades inte”, inte ett undantag.
- Tomma fall glöms: slicing av en tom sträng går bra, indexering gör det inte.

### 5.7 Undvika `SyntaxError` med citattecken

```python runnable
message = "One of Python's strengths is its diverse community."  # ✔
# message = 'One of Python's strengths...'  # ✘: the inner quote breaks the string
```

`SyntaxError: unterminated string literal` betyder oftast att citattecknen inte matchar. Titta på syntaxfärgerna: om vanlig text färgas som kod bör citattecknen kontrolleras.

---

## 6. Prova själv (strängar)

- **2-3 · Personligt meddelande**: `personal_message.py` → använd variabeln `name` och skriv en hälsning.
- **2-4 · Namnets skiftlägen**: `name_cases.py` → skriv namnet med gemener, versaler och titelstil.
- **2-5 · Berömt citat**: `famous_quote.py` → visa ett citat med citattecken och författare.
- **2-6 · Berömt citat 2**: `famous_quote_2.py` → använd `famous_person` och `message`.
- **2-7 · Rensa namn**: `stripping_names.py` → inkludera `\t` och `\n`, använd sedan `lstrip()`, `rstrip()` och `strip()`.
- **2-8 · Filändelser**: `file_extensions.py` → använd `filename.removesuffix(".txt")`.

---

## 7. Tal

### 7.1 Heltal (`int`)

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
print(f"Final score: {score}")
```

### 7.2 Flyttal (`float`)

```python runnable
print(0.1 + 0.2)
print(3 * 0.1)
```

Ibland visas `0.30000000000000004`, eftersom många decimala bråk inte kan representeras exakt med binära flyttal. Oroa dig inte ännu; senare lär vi oss att formatera resultat och jämföra flyttal säkert.

### 7.3 Blanda heltal och flyttal

```python runnable
print(4 / 2)      # 2.0
print(1 + 2.0)    # 3.0
print(3.0 ** 2)   # 9.0
```

Om operationen innehåller en `float` blir resultatet en `float`.

```python runnable
# shipping_cost.py
package_weight_kg = 2
price_per_kg = 4.5
fuel_surcharge = 1.2  # Float factor

base_cost = package_weight_kg * price_per_kg
final_cost = base_cost * fuel_surcharge

print(f"Final cost: {final_cost:.2f} €")
```

### 7.4 Understreck i långa tal

```python runnable
universe_age = 14_000_000_000
print(universe_age)  # 14000000000
```

```python runnable
# budget_overview.py
quarter_budget = 2_500_000
spend_to_date = 1_875_430
remaining = quarter_budget - spend_to_date

print(f"Remaining budget: {remaining:,} €")
```

### 7.5 Flera tilldelningar

```python runnable
x, y, z = 0, 0, 0
```

Antalet värden måste motsvara antalet variabler.

### 7.6 Konstanter

```python runnable
MAX_CONNECTIONS = 5000
```

Konventionen är versaler för att signalera ”det här värdet ska inte ändras”.

---

## 8. Prova själv (tal)

- **2-9 · Talet åtta**: `number_eight.py` → fyra olika operationer som ger 8.
- **2-10 · Favorittal**: `favorite_number.py` → lagra ditt favorittal och skriv ett meddelande.

---

## 9. Kommentarer

```python runnable
# Say hello to everyone.
print("Hello Python people!")
```

Allt efter `#` ignoreras. Använd kommentarer för beslut, antaganden och steg som inte är självklara. Det är lättare att ta bort överflödiga kommentarer än att återskapa tankegången flera månader senare.

### Prova själv: kommentarer

- **2-11 · Lägg till kommentarer**: välj två tidigare program och lägg till minst en meningsfull kommentar med exempelvis namn, datum och syfte.

---

## 10. The Zen of Python

`import this` skriver ut 19 principer av Tim Peters. Några höjdpunkter:

- **Beautiful is better than ugly.** Kod kan och bör vara elegant.
- **Simple is better than complex.** Välj den enkla versionen när den fungerar.
- **Complex is better than complicated.** När verkligheten är komplex bör lösningen ändå vara så tydlig som möjligt.
- **Readability counts.** Gör tankegången lätt att följa för nästa person.
- **There should be one—and preferably only one—obvious way to do it.** Samarbete förenklas när lösningar närmar sig varandra.
- **Now is better than never.** Vänta inte tills du ”kan allt” innan du bygger.

### Prova själv: Zen of Python

- **2-12 · Zen of Python**: kör `import this` i terminalen och välj en mening du vill tillämpa den här veckan.

---

## Kommenterade lösningar (urval)

```python runnable
# trace_run.py
step = 1
print(f"{step}. Starting program")
step += 1
print(f"{step}. Working...")
step += 1
print(f"{step}. Finished")
# Reasoning: we use a variable to show execution order.
```

```python runnable
# profile.py
first_name = "Noor"
last_name = "Frej"
age = 14
full_name = f"{first_name} {last_name}"
print(full_name)
print(f"Next year you will be {age + 1}.")
# Reasoning: splitting pieces makes changes easier and lets you reuse data.
```

```python runnable
# time_math.py
days_per_week = 7        # Cambia a 5 si necesitas semana laboral
hours_per_day = 24
minutes_per_hour = 60
minutes_per_week = days_per_week * hours_per_day * minutes_per_hour
print(f"Minutos en la semana: {minutes_per_week}")
# Reasoning: comments explain "magic numbers".
```

---

## Vanliga misstag

- Inbyggda funktioner skuggas, till exempel `list = []`.
- Strängar och heltal sammanfogas utan konvertering.
- Extra blanksteg och tabbar gör att strängjämförelser misslyckas.
- Talens betydelse lämnas åt minnet i stället för att förklaras.
- Citatttecken matchar inte och orsakar `SyntaxError`.

---

## Kontrollpunkt och självbedömning

Skapa en enda `profile.py` som lagrar namn och ålder, tar bort omgivande blanksteg, skriver en formaterad hälsning och beräknar nästa års ålder. Förutsäg de två utdataraderna före körning. Felstava sedan en variabel medvetet, läs `NameError`, återställ rätt namn och kör igen.

Ge dig en poäng per kriterium:
- **Korrekthet:** slutskriptet skriver de två förutsagda värdena.
- **Läsbarhet:** namnen beskriver sina värden och formateringen är lätt att följa.
- **Felhantering:** du hittar den felande raden och återhämtar dig från det avsiktliga `NameError`.
- **Verifiering:** du kör igen efter rättningen och jämför observerad utdata med förutsägelsen.
- **Förklaring:** du kan förklara omtilldelning, textrensning och varför den frivilliga förhandsblicken avvisar `True` som mått.

Grundvägen är klar med de fyra första poängen. Den femte bekräftar den frivilliga professionella förhandsblicken.

---

## Avslutande reflektion

Nu kan du förklara tolken, använda variabler som etiketter, formatera strängar, rensa whitespace, räkna med tal och motivera kod med kommentarer. Du känner också till Zen of Python: håll lösningen enkel och läsbar. I **kapitel 3** lagrar vi hela samlingar i **listor** och lär oss läsa, ändra och sortera dem. Behåll exemplen nära till hands; vi återanvänder dem snart.
