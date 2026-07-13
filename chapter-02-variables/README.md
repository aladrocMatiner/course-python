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

## Prerequisites and routes
- **Prerequisite:** complete the [Chapter 1 setup checkpoint](../chapter-01-introduction/README.md) and know how to run a `.py` file. No knowledge of functions, conditionals, exceptions, or testing is required for the essential route.
- **Essential route · 45–60 min:** sections 1, 2.1, 3–5, 7 and 9. Outcome: a small profile script using clear variables, cleaned text, and arithmetic.
- **Intermediate route · 25–35 min:** add slicing and the substring challenges. Outcome: correctly handle an empty string and a missing delimiter.
- **Optional professional preview · 25–35 min:** sections 2.2–2.3. Outcome: copy and inspect validation/tests, or skip them without blocking the checkpoint.

## Why it matters
Every program stores and transforms data. Understanding how Python reads your files, where values “live”, and how to choose good names avoids tricky bugs, reduces debugging time, and prepares you for more complex structures like lists and dictionaries.

### Mini adventure
Imagine each variable is a sticky label on a box: today you stick it on the “messages” box, tomorrow you move it to “score”. Python doesn’t put things “inside” the label: the label just points to the value. If you get this idea, you stop fighting the code and start controlling it.

## Predict before running
Read the first two examples without executing them. Predict how many lines each prints and which value `message` has after reassignment. Then run them and explain any difference between your prediction and the observed output.

---

## 1. What happens when you run `hello_world.py`
```python runnable
# hello_world.py
print("Hello Python world!")
```
When you run `python hello_world.py`:
1. Your shell or editor asks the selected Python interpreter to open the path `hello_world.py`. The `.py` suffix is a useful convention, not what makes the file executable by Python.
2. CPython reads the source, compiles it to *bytecode*, and executes the instructions.
3. When it finds `print("…")`, it sends text to standard output.
4. Your editor may use *syntax highlighting* to distinguish functions (`print`) from literals (`"Hello..."`). Colors are only a visual aid; running the interpreter is what validates the syntax.

### Mini experiment
```python runnable
message = "Hello Python world!"
print(message)

message = "Hello Python Crash Course world!"
print(message)
```
Result:
```text illustrative
Hello Python world!
Hello Python Crash Course world!
```
The interpreter links `message` to the first literal, then updates the label and prints again. Python always keeps the most recent value.

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

`isinstance` can accept a tuple of types: useful when you want to allow both integers and floats, or when your functions accept multiple compatible classes.

### 2.2 Validating that a function receives the right data
**Optional preview:** this subsection combines functions, conditionals, and exceptions before their full lessons. For now, `def` names a reusable action, `if` checks a rule, and `raise` stops with a named error. You may copy the complete example or skip to section 3. Continue later in [conditionals](../chapter-08-conditionals/README.md), [functions](../chapter-11-functions/README.md), and [exceptions](../chapter-14-exceptions/README.md).

When you design functions, it’s smart to fail early if arguments aren’t what you expect. This version checks that `base` and `altura` are numbers before computing the area:

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

This pattern makes expectations obvious and shows how invalid values are handled. The explicit `bool` rejection matters because Python treats `True` and `False` as integer subclasses, but they are not meaningful dimensions here. You can reinforce the contract later with type hints (`def calcular_area_rectangulo(base: float, altura: float) -> float:`).

### 2.3 Testing the preconditions (mini test)
**Optional preview:** `pytest` is a third-party tool introduced and installed in the localized [testing chapter](../chapter-18-testing/README.md). The essential route does not require it. If it is not installed, read or skip this block; do not download an unrelated installer.

Tiny tests give you instant confidence. With `pytest`, you write `test_…` functions that call your code:

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

`pytest.raises` confirms the right exception is raised. Without `pytest`, simply skip this preview; running a file that only defines tests does not execute those tests automatically. The important idea is that each precondition needs a normal, boundary, and invalid example.

---

## 3. Avoiding NameError and understanding “labels”
```python illustrative
message = "Hello Python Crash Course reader!"
print(mesage)  # typo
```
Output:
```text illustrative
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
```python runnable
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
```python runnable
name = "noor lovelace"
print(name.title())
print(name.upper())
print(name.lower())
```
`title()` capitalizes each word; `upper()` and `lower()` help standardize user input.

### 5.2 Variables inside strings (f-strings)
```python runnable
first_name = "noor"
last_name = "lovelace"
full_name = f"{first_name} {last_name}"
print(f"Hello, {full_name.title()}!")
message = f"Hello, {full_name.title()}!"
print(message)
```
Put an `f` before the string and `{}` around variables.

### 5.3 Tabs and new lines
```python runnable
print("Python")
print("\tPython")
print("Languages:\nPython\nC\nJavaScript")
print("Languages:\n\tPython\n\tC\n\tJavaScript")
```

### 5.4 Stripping whitespace
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

### 5.5 Removing prefixes / suffixes
```python runnable
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
```python runnable
word = "python"
print(word[0])   # p
print(word[-1])  # n (last character)
```

If the index is outside the range, Python raises `IndexError`.

#### 5.6.2 Slicing (a substring)
```python runnable
word = "python"
print(word[0:2])   # 'py'  (0 and 1)
print(word[2:])    # 'thon' (from 2 to the end)
print(word[:3])    # 'pyt'  (from start to 2)
print(word[-3:])   # 'hon'  (last 3)
```

#### 5.6.3 Slicing with steps (fun + useful)
```python runnable
word = "abcdefgh"
print(word[::2])   # 'aceg' (every 2nd char)
print(word[::-1])  # 'hgfedcba' (reversed)
```

#### 5.6.4 Finding substrings (efficient checks)
For simple checks, don’t slice manually; use the right tool:

```python runnable
email = "noor@example.com"
print("@" in email)                 # True
print(email.startswith("noor"))     # True
print(email.endswith(".com"))       # True
print(email.find("@"))              # 3 (position) or -1 if not found
```

#### 5.6.5 Building strings efficiently: `join`
If you build text in a loop, avoid repeated `+` (it creates many temporary strings). Collect pieces and join them:

```python runnable
words = ["python", "is", "fun"]
sentence = " ".join(words)
print(sentence)  # python is fun
```

### Extra challenges (substrings)
These are quick, practical substring exercises (great for a 14‑year‑old brain).

1. **2-S1 · Mask an email**
   ```python todo
   def mask_email(email):
       # TODO: return something like:
       # "n***@example.com" for "noor@example.com"
       # Edge case: if there's no "@", raise ValueError
       pass
   ```
   *Hint*: find the `"@"` position and slice around it.

2. **2-S2 · File extension**
   ```python todo
   def extension(filename):
       # TODO: return "txt" for "notes.txt"
       # Edge case: no dot → return "" (empty string)
       pass
   ```
   *Hint*: `rfind(".")` finds the last dot.

3. **2-S3 · Palindrome check (bonus fun)**
   ```python todo
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
```python runnable
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

### 7.2 Floats (`float`)
```python runnable
print(0.1 + 0.2)
print(3 * 0.1)
```
Sometimes you’ll see `0.30000000000000004` because many decimal fractions cannot be represented exactly in binary floating point. Don’t worry about it yet; later we’ll learn how to format results and compare floats safely.

### 7.3 Mixing integers and floats
```python runnable
print(4 / 2)      # 2.0
print(1 + 2.0)    # 3.0
print(3.0 ** 2)   # 9.0
```
If there’s a `float` in the operation, the result will be a `float`.

```python runnable
# shipping_cost.py
package_weight_kg = 2
price_per_kg = 4.5
fuel_surcharge = 1.2  # Float factor

base_cost = package_weight_kg * price_per_kg
final_cost = base_cost * fuel_surcharge

print(f"Final cost: {final_cost:.2f} €")
```

### 7.4 Underscores in long numbers
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

### 7.5 Multiple assignment
```python runnable
x, y, z = 0, 0, 0
```
Make sure the number of values matches the number of variables.

### 7.6 Constants
```python runnable
MAX_CONNECTIONS = 5000
```
Convention: uppercase names to signal “this shouldn’t change”.

---

## 8. Try it yourself (numbers)
- **2-9 · Number Eight**: `number_eight.py` → four different operations that result in 8.
- **2-10 · Favorite Number**: `favorite_number.py` → store your favorite number and print a message.

---

## 9. Comments
```python runnable
# Say hello to everyone.
print("Hello Python people!")
```
Everything after `#` is ignored. Use comments to explain decisions, assumptions, or non-obvious steps. It’s easier to delete extra comments than to reconstruct your reasoning months later.

### Try it yourself: comments
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

### Try it yourself: Zen of Python
- **2-12 · Zen of Python**: run `import this` in the terminal and pick one sentence you want to apply this week.

---

## Commented solutions (selection)
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

## Common mistakes
- Shadowing built-in functions (`list = []`).
- Concatenating strings and integers without conversion.
- Leaving extra spaces/tabs that break string comparisons.
- Relying on memory for what numbers mean (missing comments).
- Mismatched quotes causing `SyntaxError`.

---

## Checkpoint and self-assessment
Create one `profile.py` that stores a name and age, strips surrounding whitespace, prints a formatted greeting, and calculates next year's age. Before running, predict its two output lines. Then deliberately misspell one variable, read the `NameError`, restore the correct spelling, and run again.

Score one point for each criterion:
- **Correctness:** the final script prints the two predicted values.
- **Readability:** names describe their values and formatting is easy to follow.
- **Error handling:** you can identify the failing line and recover from the deliberate `NameError`.
- **Verification:** you rerun after the fix and compare observed output with your prediction.
- **Explanation:** you can explain reassignment, string cleanup, and why `True` is rejected as a rectangle dimension in the optional preview.

The essential route is complete with the first four points. The fifth confirms the optional professional preview.

---

## Closing reflection
Now you can explain what the interpreter does, use variables as labels, format strings, clean whitespace, do math with numbers, and justify your code with comments. You also know the Zen of Python mindset: keep it simple and readable. In **Chapter 3** we’ll store whole collections of data using **lists** and learn how to read, modify, and sort them. Keep these examples close — we’ll reuse them soon.
