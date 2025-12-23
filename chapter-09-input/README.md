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

## Why it matters
Real programs receive data from users or other systems. If you trust input blindly, you get bugs (or even vulnerabilities). Learning to read and validate input prepares you for web forms, automation scripts, and professional CLI tools.

### Mini adventure
Imagine your program is a friendly robot. If you speak with weird phrases, the robot gets confused. Validation is teaching the robot to say: “I didn’t understand — can you repeat that in a different way?”

---

## 1. Mental model: everything arrives as text
`input()` always returns a string. You decide whether to convert it to a number/date, or compare it as text.

```python
name = input("What's your name? ")
print(f"Hello, {name}")
```

- A prompt helps the user.
- Trim extra spaces with `.strip()` when you need consistency.

---

## 2. Conversion and error handling

```python
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
```python
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

```python
city = input("City (default Barcelona): ").strip() or "Barcelona"
print(city)
```

- The expression `value or "default"` uses the default when the string is empty.

---

## 4. Retries + combined validation

```python
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

```python
# cli_args.py
import sys

if len(sys.argv) < 2:
    print("Usage: python cli_args.py <file>")
    sys.exit(1)

path = sys.argv[1]
print(f"Processing {path}")
```

### Short `argparse` example
```python
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

```python
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

```python
# forms.py
def normalize_name(name):
    clean = name.strip().title()
    if not clean:
        raise ValueError("Name cannot be empty")
    return clean
```

```python
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
   ```python
   # TODO 1: ask for first name and last name, combine them with title()
   # TODO 2: validate that neither is empty
   # TODO 3: print a welcome message with defaults if something is missing
   ```
   *Hint*: use `.strip()` and `or "Guest"`.

2. **9-2 · Notes CLI**
   ```python
   # TODO 1: use argparse to accept --title and --message
   # TODO 2: save the note in a .txt file with Path.write_text()
   # TODO 3: handle errors when the title is missing
   ```
   *Hint*: `parser.add_argument("--title", required=True)`.

3. **9-3 · Import a simple CSV**
   ```python
   # TODO 1: ask for a CSV path using input()
   # TODO 2: verify it exists and read it line by line
   # TODO 3: print how many valid rows you found
   ```
   *Hint*: use `Path.open()` and `split(",")` to separate fields.

---

## Common mistakes
- Trusting input format blindly ⇒ catch `ValueError` and validate explicitly.
- Not trimming whitespace ⇒ strings that look “the same” fail comparisons.
- Forgetting `sys.exit(1)` in CLIs when args are missing ⇒ the program continues in a weird state.
- Reading files without checking existence ⇒ unexpected `FileNotFoundError`.

---

## Explained solutions
1. **Quick registration**: clean each `input()` and validate with `if not value:`; defaults (`"Guest"`) avoid breaking the flow.
2. **Notes CLI**: `argparse` ensures `--title` and `--message` are present; `Path(title).with_suffix(".txt")` creates the final file path.
3. **CSV import**: `Path(path).exists()` prevents failures; a counter accumulates valid rows and reports back.

---

## Summary
You learned patterns to read data from the console, CLI args, and files, converting safely and validating each step. Now you can build interactive assistants and CLI scripts without fearing messy input.

## Closing reflection
Every interaction with people or systems depends on reliable input. With these techniques you can guide users, anticipate errors, and respond with clear messages. Next we’ll apply these inputs inside loops and start building intuition about performance cost.
