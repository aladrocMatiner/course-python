# Chapter 2 · Variables and Simple Data Types

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
In this chapter we’ll build the essential Python vocabulary: we’ll understand what happens when you run `hello_world.py`, create and rename variables, clean strings, work with numbers, and write meaningful comments. We’ll finish with a short introduction to the “Zen of Python”, the mindset that will guide the rest of the course.

## Learning path
1. **Interpreter mental model** → without it, the rest feels like magic.
2. **Variables as labels** → before manipulating data, we must name things well.
3. **Strings** → the most common type, with formatting, spaces and classic mistakes.
4. **Numbers** → operations, floats and constants.
5. **Comments and Zen** → keep your code understandable.
6. **“Try it yourself” exercises** that grow in difficulty.

## Learning objectives
- Explain step by step what the interpreter does when it runs `hello_world.py`.
- Declare, reassign and name variables using professional rules.
- Manipulate strings (case, spaces, prefixes) and numbers (int, float) without surprises.
- Document code with useful comments and internalize the Zen of Python.

## Why it matters
Every program stores and transforms data. Understanding how Python reads your files, where values “live”, and how to choose good names avoids tricky bugs, reduces debugging time, and prepares you for more complex structures like lists and dictionaries.

### Mini adventure
Imagine each variable is a sticky label on a box: today you stick it on the “messages” box, tomorrow you move it to “score”. Python doesn’t put things “inside” the label: the label just points to the value. If you get this idea, you stop fighting the code and start controlling it.

---

## 1. What happens when you run `hello_world.py`
```python
# hello_world.py
print("Hello Python world!")
```
When you run `python hello_world.py`:
1. The `.py` suffix tells your computer it’s a Python script.
2. Your editor calls the interpreter, which reads the file, compiles it to *bytecode* and runs each instruction.
3. When it finds `print("…")`, it sends text to standard output.
4. Your editor uses *syntax highlighting* to differentiate functions (`print`) from literals (`"Hello..."`). Watch the colors: they often warn you about common mistakes like unclosed quotes.

### Mini experiment
```python
message = "Hello Python world!"
print(message)

message = "Hello Python Crash Course world!"
print(message)
```
Result:
```
Hello Python world!
Hello Python Crash Course world!
```
The interpreter links `message` to the first literal, then updates the label and prints again. Python always keeps the most recent value.

```python
# multiple_messages.py
message = "Welcome to Python"
print(message)

message = "We keep learning variables"
print(message)

print(f"Último mensaje: {message}")
```

```python
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

## 2. Naming and using variables
Key rules:
- Letters, numbers and `_`. They can’t start with a number (`message_1` ✔, `1_message` ✘).
- No spaces; use `_` to separate words (`greeting_message`).
- Don’t reuse reserved words or function names (`print`, `list`).
- Prefer short but descriptive names (`name` > `n`; `student_name` > `s_n`).
- Avoid confusing `l` (lowercase L) and `O` (uppercase O) with `1` and `0`.

> Note: use lowercase by default. Later we’ll see when uppercase makes sense (constants).

### 2.1 Checking a variable’s type
Python infers types, but you can inspect them with `type()` or check against concrete classes with `isinstance()`.

```python
username = "noor"
age = 28
temperature = 20.5

print(type(username))          # <class 'str'>
print(type(age))               # <class 'int'>
print(isinstance(age, int))    # True
print(isinstance(temperature, float))  # True
print(isinstance(age, (int, float)))   # True (it matches one of the types)
```

`isinstance` can accept a tuple of types: useful when you want to allow both integers and floats, or when your functions accept multiple compatible classes.

### 2.2 Validating that a function receives the right data
When you design functions, it’s smart to fail early if arguments aren’t what you expect. This version checks that `base` and `altura` are numbers before computing the area:

```python
def calcular_area_rectangulo(base, altura):
    if not isinstance(base, (int, float)):
        raise TypeError("base must be numeric")
    if not isinstance(altura, (int, float)):
        raise TypeError("height must be numeric")
    if base <= 0 or altura <= 0:
        raise ValueError("dimensions must be positive")

    return base * altura
```

This pattern makes expectations obvious and shows how invalid values are handled. You can reinforce it with type hints (`def calcular_area_rectangulo(base: float, altura: float) -> float:`) so editors and linters warn you earlier.

### 2.3 Testing the preconditions (mini test)
Even this early, tiny tests give you instant confidence. With `pytest`, you write `test_…` functions that call your code:

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

`pytest.raises` confirms the right exception is raised. Even without `pytest`, you can run the module and verify that the `raise` happens. The important part: document your preconditions and check them automatically.

---

## 3. Avoiding NameError and understanding “labels”
```python
message = "Hello Python Crash Course reader!"
print(mesage)  # typo
```
Output:
```
Traceback (most recent call last):
  File "hello_world.py", line 2, in <module>
    print(mesage)
NameError: name 'mesage' is not defined. Did you mean: 'message'?
```
Python shows you:
1. The file and line where the problem happened.
2. The exact line highlighted.
3. The error type (`NameError`) and a suggestion.

If the typo appears both where you define and where you use it:
```python
mesage = "Hello..."
print(mesage)
```
…your program runs because the labels match. Conclusion: think of variables as **labels** pointing to values, not boxes. The interpreter requires the name to match *exactly*.

---

## 4. Try it yourself (basic variables)
- **2-1 · Simple Message**: `simple_message.py` → assign a message and print it.
- **2-2 · Simple Messages**: `simple_messages.py` → print a message, change the variable, and print again.

---

## 5. Strings

### 5.1 Changing case
```python
name = "noor lovelace"
print(name.title())
print(name.upper())
print(name.lower())
```
`title()` capitalizes each word; `upper()` and `lower()` help standardize user input.

### 5.2 Variables inside strings (f-strings)
```python
first_name = "noor"
last_name = "lovelace"
full_name = f"{first_name} {last_name}"
print(f"Hello, {full_name.title()}!")
message = f"Hello, {full_name.title()}!"
print(message)
```
Put an `f` before the string and `{}` around variables.

### 5.3 Tabs and new lines
```python
print("Python")
print("\tPython")
print("Languages:\nPython\nC\nJavaScript")
print("Languages:\n\tPython\n\tC\n\tJavaScript")
```

### 5.4 Stripping whitespace
```python
favorite_language = "python "
print(favorite_language.rstrip())   # temporary
favorite_language = favorite_language.rstrip()  # permanent

favorite_language = " python "
print(favorite_language.rstrip())
print(favorite_language.lstrip())
print(favorite_language.strip())
```

```python
# username_cleaner.py
raw_username = "  \tTaha\n"
clean_username = raw_username.strip()

if clean_username:
    print(f"Valid user: {clean_username}")
else:
    print("Empty name; ask again.")
```

### 5.5 Removing prefixes / suffixes
```python
nostarch_url = "https://nostarch.com"
print(nostarch_url.removeprefix("https://"))

filename = "python_notes.txt"
print(filename.removesuffix(".txt"))
```

### 5.6 Substrings (slicing): cut text safely
In Python, a string is a **sequence** of characters. That means you can:
- take one character by **index** (`text[0]`)
- take a **substring** (a slice) with `text[start:end]`

Think of it like cutting a sandwich: `start` is where you begin, `end` is where you stop (and **end is not included**).

#### 5.6.1 Indexing (one character)
```python
word = "python"
print(word[0])   # p
print(word[-1])  # n (last character)
```

If the index is outside the range, Python raises `IndexError`.

#### 5.6.2 Slicing (a substring)
```python
word = "python"
print(word[0:2])   # 'py'  (0 and 1)
print(word[2:])    # 'thon' (from 2 to the end)
print(word[:3])    # 'pyt'  (from start to 2)
print(word[-3:])   # 'hon'  (last 3)
```

#### 5.6.3 Slicing with steps (fun + useful)
```python
word = "abcdefgh"
print(word[::2])   # 'aceg' (every 2nd char)
print(word[::-1])  # 'hgfedcba' (reversed)
```

#### 5.6.4 Finding substrings (efficient checks)
For simple checks, don’t slice manually; use the right tool:

```python
email = "noor@example.com"
print("@" in email)                 # True
print(email.startswith("noor"))     # True
print(email.endswith(".com"))       # True
print(email.find("@"))              # 3 (position) or -1 if not found
```

#### 5.6.5 Building strings efficiently: `join`
If you build text in a loop, avoid repeated `+` (it creates many temporary strings). Collect pieces and join them:

```python
words = ["python", "is", "fun"]
sentence = " ".join(words)
print(sentence)  # python is fun
```

### Extra challenges (substrings)
These are quick, practical substring exercises (great for a 14‑year‑old brain).

1. **2-S1 · Mask an email**
   ```python
   def mask_email(email):
       # TODO: return something like:
       # "n***@example.com" for "noor@example.com"
       # Edge case: if there's no "@", raise ValueError
       pass
   ```
   *Hint*: find the `"@"` position and slice around it.

2. **2-S2 · File extension**
   ```python
   def extension(filename):
       # TODO: return "txt" for "notes.txt"
       # Edge case: no dot → return "" (empty string)
       pass
   ```
   *Hint*: `rfind(".")` finds the last dot.

3. **2-S3 · Palindrome check (bonus fun)**
   ```python
   def is_palindrome(text):
       # TODO: ignore spaces and case
       # Example: "Anita lava la tina" -> True
       pass
   ```
   *Hint*: `clean = text.replace(" ", "").lower()` and compare with `clean[::-1]`.

### Common substring mistakes
- Off‑by‑one: `text[a:b]` does not include `b`.
- Confusing `find()` results: it returns `-1` when not found (not an error).
- Forgetting empty cases: slicing an empty string is fine, but indexing it is not.

### 5.7 Avoiding `SyntaxError` with quotes
```python
message = "One of Python's strengths is its diverse community."  # ✔
# message = 'One of Python's strengths...'  # ✘: the inner quote breaks the string
```
A `SyntaxError: unterminated string literal` usually means your quotes don’t match. Watch the syntax highlighting: if your editor colors normal text as code, re-check your quotes.

---

## 6. Try it yourself (strings)
- **2-3 · Personal Message**: `personal_message.py` → use a `name` variable and print a greeting.
- **2-4 · Name Cases**: `name_cases.py` → print the name in lowercase, uppercase, and title case.
- **2-5 · Famous Quote**: `famous_quote.py` → show a quote with quotation marks and the author.
- **2-6 · Famous Quote 2**: `famous_quote_2.py` → use `famous_person` + `message`.
- **2-7 · Stripping Names**: `stripping_names.py` → include `\t` and `\n`, then apply `lstrip()`, `rstrip()`, `strip()`.
- **2-8 · File Extensions**: `file_extensions.py` → `filename.removesuffix(".txt")`.

---

## 7. Numbers

### 7.1 Integers (`int`)
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
print(f"Final score: {score}")
```

### 7.2 Floats (`float`)
```python
print(0.1 + 0.2)
print(3 * 0.1)
```
Sometimes you’ll see `0.3000000004` because of binary representation. Ignore it for now; later we’ll learn how to format results.

### 7.3 Mixing integers and floats
```python
print(4 / 2)      # 2.0
print(1 + 2.0)    # 3.0
print(3.0 ** 2)   # 9.0
```
If there’s a `float` in the operation, the result will be a `float`.

```python
# shipping_cost.py
package_weight_kg = 2
price_per_kg = 4.5
fuel_surcharge = 1.2  # Float factor

base_cost = package_weight_kg * price_per_kg
final_cost = base_cost * fuel_surcharge

print(f"Final cost: {final_cost:.2f} €")
```

### 7.4 Underscores in long numbers
```python
universe_age = 14_000_000_000
print(universe_age)  # 14000000000
```

```python
# budget_overview.py
quarter_budget = 2_500_000
spend_to_date = 1_875_430
remaining = quarter_budget - spend_to_date

print(f"Remaining budget: {remaining:,} €")
```

### 7.5 Multiple assignment
```python
x, y, z = 0, 0, 0
```
Make sure the number of values matches the number of variables.

### 7.6 Constants
```python
MAX_CONNECTIONS = 5000
```
Convention: uppercase names to signal “this shouldn’t change”.

---

## 8. Try it yourself (numbers)
- **2-9 · Number Eight**: `number_eight.py` → four different operations that result in 8.
- **2-10 · Favorite Number**: `favorite_number.py` → store your favorite number and print a message.

---

## 9. Comments
```python
# Say hello to everyone.
print("Hello Python people!")
```
Everything after `#` is ignored. Use comments to explain decisions, assumptions, or non-obvious steps. It’s easier to delete extra comments than to reconstruct your reasoning months later.

### Try it yourself
- **2-11 · Adding Comments**: take two previous programs and add at least one meaningful comment (name, date, purpose).

---

## 10. The Zen of Python
`import this` prints 19 principles by Tim Peters. Some highlights:
- **Beautiful is better than ugly.** Code can and should be elegant.
- **Simple is better than complex.** If the simple version works, pick that.
- **Complex is better than complicated.** When reality is complex, choose the clearest solution.
- **Readability counts.** Make it easy for another person to follow your thinking.
- **There should be one—and preferably only one—obvious way to do it.** Collaboration gets easier when solutions converge.
- **Now is better than never.** Don’t wait to “know everything” before building.

### Try it yourself
- **2-12 · Zen of Python**: run `import this` in the terminal and pick one sentence you want to apply this week.

---

## Commented solutions (selection)
```python
# trace_run.py
step = 1
print(f"{step}. Starting program")
step += 1
print(f"{step}. Working...")
step += 1
print(f"{step}. Finished")
# Reasoning: we use a variable to show execution order.
```

```python
# profile.py
first_name = "Noor"
last_name = "Frej"
age = 14
full_name = f"{first_name} {last_name}"
print(full_name)
print(f"Next year you will be {age + 1}.")
# Reasoning: splitting pieces makes changes easier and lets you reuse data.
```

```python
# time_math.py
days_per_week = 7        # Cambia a 5 si necesitas semana laboral
hours_per_day = 24
minutes_per_hour = 60
minutes_per_week = days_per_week * hours_per_day * minutes_per_hour
print(f"Minutos en la semana: {minutes_per_week}")
# Reasoning: comments explain "magic numbers".
```

---

## Common mistakes
- Shadowing built-in functions (`list = []`).
- Concatenating strings and integers without conversion.
- Leaving extra spaces/tabs that break string comparisons.
- Relying on memory for what numbers mean (missing comments).
- Mismatched quotes causing `SyntaxError`.

---

## Closing reflection
Now you can explain what the interpreter does, use variables as labels, format strings, clean whitespace, do math with numbers, and justify your code with comments. You also know the Zen of Python mindset: keep it simple and readable. In **Chapter 3** we’ll store whole collections of data using **lists** and learn how to read, modify, and sort them. Keep these examples close — we’ll reuse them soon.
