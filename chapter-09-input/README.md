# Chapter 9 · User Input and Safe Validation

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
You’ll learn to collect data from the terminal (`input()`), from command-line arguments, and from simple files — always validating and converting values before using them. You’ll see “conversational form” examples and small console tools that simulate common backend flows.

## Learning path
1. **Mental model**: every input starts as a string; you decide how to convert it.
2. **Interactive `input()`**: basic reads and chained questions.
3. **Conversion + validation**: `int()`, `float()`, `str.strip()` and handling `ValueError`.
4. **Defaults and retries**: looping until you receive something valid.
5. **Command-line arguments**: `sys.argv` and a short intro to `argparse`.
6. **Reading simple files**: open, read, and check existence.
7. **Tests and guided exercises**.

## Learning objectives
- Collect input from the console and convert it to the right type.
- Validate data before using it, showing helpful messages when it fails.
- Implement safe retries with clear limits.
- Read command-line arguments and basic files using the standard library.
- Write tests for “pure” functions that don’t depend on the console.

## Prerequisites and routes
- **Prerequisite:** complete the [Chapter 8 checkpoint](../chapter-08-conditionals/README.md). The essential route uses strings, conversions, and conditionals.
- **Essential route · 40–55 min:** section 1, the essential subsection and exercise 9-0 below, then section 3. Outcome: normalize text, validate digits, convert one integer, and recover from invalid input using direct conditionals. Exceptions, loops, functions, and pytest are not required.
- **Intermediate route · 30–40 min:** bounded retries in section 4. This is an **optional preview** of [loops](../chapter-10-loops/README.md), [functions](../chapter-11-functions/README.md), and [exceptions](../chapter-14-exceptions/README.md); copy the complete helpers or skip them.
- **Optional professional route · 45–60 min:** CLI, files, CSV, and tests. It previews [files](../chapter-13-files/README.md) and [pytest](../chapter-18-testing/README.md). No part of this route is required for the essential checkpoint.

## Why it matters
Real programs receive data from users or other systems. If you trust input blindly, you get bugs (or even vulnerabilities). Learning to read and validate input prepares you for web forms, automation scripts, and professional CLI tools.

### Mini adventure
Imagine your program is a friendly robot. If you speak with weird phrases, the robot gets confused. Validation is teaching the robot to say: “I didn’t understand — can you repeat that in a different way?”

## Predict before reading input
If a learner types `14`, predict the value and type returned by `input()`, then the value and type after `int()`. Also predict what happens for `fourteen`; run the conversion example and identify the recovery message rather than guessing.

---

## 1. Mental model: everything arrives as text
`input()` always returns a string. You decide whether to convert it to a number/date, or compare it as text.

```python illustrative
name = input("What's your name? ")
print(f"Hello, {name}")
```

- A prompt helps the user.
- Trim extra spaces with `.strip()` when you need consistency.

---

## 2. Conversion and error handling

### 9-0 · Essential conversion without exceptions

Start with a fixed string so the example runs offline. Replace it with `input("Age: ")` only when practising interactively:

```python runnable
raw_age = "14".strip()

if raw_age.isdigit():
    age = int(raw_age)
    print(age)
else:
    print("Age must contain digits only")
```

Now observe the recovery branch with invalid text; the program remains in control instead of crashing:

```python runnable
raw_age = "fourteen".strip()

if raw_age.isdigit():
    age = int(raw_age)
    print(age)
else:
    print("Age must contain digits only")
```

Run both blocks and record the value and type before and after conversion. The `try`/`except` helper that follows is an optional preview of [exceptions](../chapter-14-exceptions/README.md).

```python illustrative
raw_age = input("Age: ")
try:
    age = int(raw_age)
except ValueError:
    print("Age must be an integer.")
    age = None
```

- Catch `ValueError` to explain what went wrong.
- You can wrap this logic into reusable functions.

### Reusable helper
```python illustrative
def ask_int(prompt, attempts=3):
    for _ in range(attempts):
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Please enter an integer.")
    raise RuntimeError("Too many attempts")
```

---

## 3. Default values

```python illustrative
city = input("City (default Barcelona): ").strip() or "Barcelona"
print(city)
```

- The expression `value or "default"` uses the default when the string is empty.

---

## 4. Retries + combined validation

```python illustrative
def ask_email():
    while True:
        email = input("Email: ").strip().lower()
        if "@" in email and "." in email:
            return email
        print("Invalid format. Try again.")
```

- Use `while True` + `return` when you need to repeat until the format is valid.
- In longer scripts, add a clear exit path (for example, a maximum number of attempts).

---

## 5. Command-line arguments

```python illustrative
# cli_args.py
import sys

if len(sys.argv) < 2:
    print("Usage: python cli_args.py <file>")
    sys.exit(1)

path = sys.argv[1]
print(f"Processing {path}")
```

### Short `argparse` example
```python illustrative
import argparse

parser = argparse.ArgumentParser(description="Calculator")
parser.add_argument("operation", choices=["add", "subtract"])
parser.add_argument("a", type=int)
parser.add_argument("b", type=int)
args = parser.parse_args()

if args.operation == "add":
    print(args.a + args.b)
else:
    print(args.a - args.b)
```

- `argparse` validates inputs and generates help automatically.

---

## 6. Simple file reading

```python illustrative
from pathlib import Path

path = Path("data.txt")
if not path.exists():
    raise FileNotFoundError("data.txt not found")

content = path.read_text(encoding="utf-8")
print(content)
```

- Use `Path` for portable path handling.
- Catch `FileNotFoundError` to show a clear message.

---

## 7. Testing pure functions
Instead of testing `input()` directly, encapsulate the logic and pass data as arguments. That way you can use `pytest` without depending on the console.

```python runnable
# forms.py
def normalize_name(name):
    clean = name.strip().title()
    if not clean:
        raise ValueError("Name cannot be empty")
    return clean
```

```python illustrative
# tests/test_forms.py
import pytest
from forms import normalize_name

def test_normalize_name_ok():
    assert normalize_name("  noor ") == "Noor"

def test_normalize_name_rejects_empty():
    with pytest.raises(ValueError):
        normalize_name("   ")
```

---

## Guided exercises (with TODOs)
1. **9-1 · Quick registration**
   ```python todo
   # TODO 1: ask for first name and last name, combine them with title()
   # TODO 2: validate that neither is empty
   # TODO 3: print a welcome message with defaults if something is missing
   ```
   *Hint*: use `.strip()` and `or "Guest"`.

2. **9-2 · Notes CLI**
   ```python todo
   # TODO 1: use argparse to accept --title and --message
   # TODO 2: derive a confined path with safe_note_path(title)
   # TODO 3: write with UTF-8 and refuse to overwrite an existing note
   ```
   *Hint*: `parser.add_argument("--title", required=True)`.

   Use this helper so a title cannot inject `/`, `\\`, or `..` into the output path:
   ```python illustrative
   from pathlib import Path

   def safe_note_path(title, root=Path("notes")):
       safe_stem = "".join(
           char for char in title.strip()
           if char.isalnum() or char in ("-", "_")
       )
       if not safe_stem:
           raise ValueError("title must contain a letter or number")
       root.mkdir(parents=True, exist_ok=True)
       path = root / f"{safe_stem}.txt"
       if path.exists():
           raise FileExistsError(f"refusing to overwrite {path}")
       return path
   ```

3. **9-3 · Import a simple CSV**
   ```python todo
   import csv
   # TODO 1: ask for a CSV path using input()
   # TODO 2: open with newline="" and encoding="utf-8"
   # TODO 3: count valid rows with csv.reader
   ```
   *Hint*: pass the opened file to `csv.reader`; unlike `split(",")`, it handles quoted commas.

---

## Common mistakes
- Trusting input format blindly ⇒ catch `ValueError` and validate explicitly.
- Not trimming whitespace ⇒ strings that look “the same” fail comparisons.
- Forgetting `sys.exit(1)` in CLIs when args are missing ⇒ the program continues in a weird state.
- Reading files without checking existence ⇒ unexpected `FileNotFoundError`.
- Deriving a path directly from a title ⇒ traversal or accidental overwrite; confine and sanitize the filename first.
- Parsing CSV with `split(",")` ⇒ quoted commas become fake columns; use the `csv` module.

---

## Explained solutions
1. **Quick registration**: clean each `input()` and validate with `if not value:`; defaults (`"Guest"`) avoid breaking the flow.
2. **Notes CLI**: `argparse` ensures `--title` and `--message` are present; `safe_note_path` keeps the filename inside `notes/`, rejects an empty sanitized title, and refuses overwrite before `path.write_text(args.message, encoding="utf-8")`.
3. **CSV import**: `Path(path).exists()` prevents a missing-file failure; `csv.reader` preserves quoted fields and a counter increments only for rows with the expected column count.

---

## Checkpoint and self-assessment
Use fictional fixed strings to simulate a name and age. Predict their types, normalize the name, validate the age with `.isdigit()`, and convert only inside the valid branch. Run once with digits and once with nonnumeric text; the latter must print a recovery message without crashing. Do not use a loop, function, exception, or test framework.

Score one point for each criterion: **correctness** (valid text becomes the expected integer), **normalization** (surrounding whitespace is removed), **boundary** (empty and nonnumeric text take the invalid branch), **recovery** (the message says what format is required), and **evidence** (predicted types and observed outputs are recorded). A score of 4/5 means you may continue; otherwise repeat 9-0. Bounded retries, exception handling, CLI/files, and pytest belong to the intermediate or professional routes.

---

## Summary
You learned patterns to read data from the console, CLI args, and files, converting safely and validating each step. Now you can build interactive assistants and CLI scripts without fearing messy input.

## Closing reflection
Every interaction with people or systems depends on reliable input. With these techniques you can guide users, anticipate errors, and respond with clear messages. Next we’ll apply these inputs inside loops and start building intuition about performance cost.
