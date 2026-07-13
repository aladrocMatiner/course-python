# Chapter 22 · Introspection: Python Detective Mode

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
In this chapter you’ll learn *introspection*: how to look at a value and ask “What are you?” and “What can you do?”. You’ll use tools like `type()`, `isinstance()`, `dir()`, `help()`, `getattr()` and `callable()` to explore safely.

Then you’ll build a tiny “detective tool” called `describe(value)` and (bonus) you’ll learn how to inspect a function’s parameters with `inspect.signature()` so you can validate callbacks and write better tests.

## Learning path
1. **Detect the type**: `type`, `isinstance` (and the `None` case).
2. **Print clearly**: `str` vs `repr` (why debugging loves `repr`).
3. **Methods vs attributes**: `callable` and the “missing parentheses” trap.
4. **Explore unknown objects**: `dir`, `help`, and docstrings.
5. **Safe access**: `getattr`, `hasattr`, `vars` (and when they fail).
6. **Mini‑project**: `describe(value)` (a safe object summary).
7. **Bonus**: `inspect.signature()` to validate required parameters + pytest tests.

## Learning objectives
- Tell what type a value is and check it safely with `isinstance`.
- Use `repr()` to debug “mystery values” and understand `str()` vs `repr()`.
- Avoid common traps like calling a method without `()`.
- Explore an unknown object without crashing your program.
- Safely read attributes and detect capabilities (`callable`, `hasattr`).
- Build and test small utilities that validate inputs and callbacks.

## Why it matters
When you’re learning, you’ll constantly meet values you don’t fully understand yet: strings, lists, dictionaries, objects from libraries… Introspection gives you a safe way to explore them.

In real backend projects, frameworks often use introspection too. For example: “Is this callable?”, “Does it accept `request`?”, “Does this object have `.save()`?”, “What fields exist?”. You don’t need to be a wizard — just learn the safe basics.

### Mini adventure: you are a Python detective
Imagine you’re a detective with a flashlight:
- `type()` is your **ID scanner** (“what are you?”).
- `dir()` is your **toolbox list** (“what can you do?”).
- `help()` and `__doc__` are the **manual** (“how does it work?”).
- `getattr()` is your **safe grabber** (“give me that attribute, or a default”).

It’s normal if this feels strange at first. Every programmer learns it by playing with real values.

## Prerequisites
- Types, functions, classes, exceptions, and callable arguments from Chapters 2, 11, 12, and 14.
- `pytest` from Chapter 18 only for the bonus callback tests.

---

## 1) The first question: what is this?

### `type()` tells you the exact type
```python runnable
value = 42
print(type(value))          # <class 'int'>
print(type(value).__name__) # int
```

### `isinstance()` is usually the safer check
```python runnable
value = 42
print(isinstance(value, int))          # True
print(isinstance(value, (int, float))) # True (tuple means “any of these”)
```

Why “safer”? Because it works with **subclasses** too:

```python runnable
print(isinstance(True, int))  # True (bool is a kind of int in Python)
print(type(True) is int)      # False (exact type is bool)
```

### Special case: `None`
```python runnable
x = None
print(x is None)          # the standard way
print(type(x).__name__)   # NoneType
```

---

## 2) Debug printing: `str()` vs `repr()`
When you show something to a user, `str()` is fine. When you debug, `repr()` is your best friend because it aims to be **unambiguous**.

```python runnable
text = "hello\nworld"
print(text)        # prints two lines
print(repr(text))  # 'hello\nworld' (shows the \n)
```

### Custom objects: why `repr` helps
```python runnable
class User:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"User({self.name})"

    def __repr__(self):
        return f"User(name={self.name!r})"  # !r uses repr()

u = User("Noor")
print(u)       # User(Noor)
print([u])     # [User(name='Noor')]
print(f"{u!r}")  # User(name='Noor')
```

Many people get confused here, and that’s okay: `print(u)` uses `str(u)`, but containers (like lists) often display elements using `repr(...)`.

---

## 3) Attributes vs methods (and the missing `()` trap)
An **attribute** is data. A **method** is something you can call.

```python runnable
text = "hello"
print(text.upper)         # this is a method object
print(callable(text.upper))  # True
print(text.upper())       # HELLO
```

Common mistake:
```python runnable
text = "hello"
shout = text.upper   # forgot () → shout is not a string
print(shout)         # <built-in method upper of str object at ...>
```

If you see something like `<built-in method ...>`, it means you grabbed the method but didn’t call it.

---

## 4) Exploring an unknown object: `dir()` + `help()`
### `dir(obj)` gives you a list of names
```python runnable
text = "hello"
names = [name for name in dir(text) if "upper" in name]
print(names)  # ['isupper', 'upper']
```

This list can be long. That’s normal. Filter it!

### `help(...)` and docstrings explain how to use it
```python runnable
print(str.upper.__doc__)
```

And if you want the full manual:
```python runnable
help(str.upper)
```

---

## 5) Safe access: `getattr()`, `hasattr()`, `vars()`

### `getattr(obj, "name", default)`
This is perfect when you’re not sure the attribute exists:

```python runnable
class Player:
    def __init__(self, name):
        self.name = name

p = Player("Frej")
print(getattr(p, "name", "<anonymous>"))     # Frej
print(getattr(p, "nickname", "<anonymous>")) # <anonymous>
```

### `hasattr(obj, "name")`
```python illustrative
print(hasattr(p, "name"))     # True
print(hasattr(p, "nickname")) # False
```

### `vars(obj)` (or `obj.__dict__`) for simple objects
```python illustrative
print(vars(p))  # {'name': 'Frej'}
```

Important: `vars()` does **not** work for every object. If it fails, that’s normal — some objects store data differently.

---

## Mini‑project: `describe(value)` (a defensive summary)
We’ll write a small function for ordinary built-in and course objects. Python can run user code inside `repr()` or a property, so no introspection helper can promise safety for every hostile object.

```python runnable
def describe(value):
    info = {
        "type": type(value).__name__,
        "repr": repr(value),
        "is_callable": callable(value),
    }

    # Does it have a length?
    try:
        info["len"] = len(value)
        info["has_len"] = True
    except TypeError:
        info["len"] = None
        info["has_len"] = False

    # Does it have a "name" attribute?
    info["name_attr"] = getattr(value, "name", None)
    return info

print(describe("hello"))
print(describe([1, 2, 3]))

class Box:
    def __init__(self, name):
        self.name = name
print(describe(Box("Taha")))
```

This is the kind of tool you write when you’re debugging: it gives you safe clues.

---

## Bonus: validate function parameters with `inspect.signature()`
Sometimes you accept a function (a callback) and you want to ensure it has the parameters you need.

Example: you want a callback that can accept `user_id` and `payload`.

```python runnable
import inspect

def require_named_params(fn, required_names):
    sig = inspect.signature(fn)
    probe = {name: object() for name in required_names}
    try:
        sig.bind(**probe)
    except TypeError as exc:
        raise TypeError(
            f"{fn.__name__} must accept these named arguments: {', '.join(required_names)}"
        ) from exc
```

### Quick demo
```python illustrative
def ok(user_id, payload):
    return (user_id, payload)

def flexible(**kwargs):
    return kwargs

def bad(user_id):
    return user_id

def positional_only(user_id, payload, /):
    return (user_id, payload)

require_named_params(ok, ["user_id", "payload"])        # OK
require_named_params(flexible, ["user_id", "payload"])  # OK (**kwargs)
require_named_params(bad, ["user_id", "payload"])       # raises TypeError
require_named_params(positional_only, ["user_id", "payload"])  # raises TypeError
```

### Tiny tests (pytest)
```python illustrative
# tests/test_introspection.py
import pytest
from chapter_22 import require_named_params

def ok(user_id, payload):
    return (user_id, payload)

def flexible(**kwargs):
    return kwargs

def bad(user_id):
    return user_id

def positional_only(user_id, payload, /):
    return (user_id, payload)

def test_require_named_params_ok():
    require_named_params(ok, ["user_id", "payload"])

def test_require_named_params_kwargs_ok():
    require_named_params(flexible, ["user_id", "payload"])

def test_require_named_params_raises():
    with pytest.raises(TypeError):
        require_named_params(bad, ["user_id", "payload"])

def test_require_named_params_rejects_positional_only():
    with pytest.raises(TypeError):
        require_named_params(positional_only, ["user_id", "payload"])
```

This is a real testing angle: you’re not only testing outputs — you’re testing that your system rejects the wrong *shape* of function early, with a clear error.

---

## Guided exercises (with TODOs and hints)

### 22-1 · Type reporter (easy)
Write a function that returns a list of strings describing each value’s type.

```python todo
def report_types(values):
    # TODO: return something like:
    # ["'hi' -> str", "3 -> int", "None -> NoneType"]
    pass
```

*Hint*: `type(x).__name__` and `repr(x)`.

---

### 22-2 · Safe method caller (medium)
Write a function that calls a method **only if it exists and is callable**.

```python todo
def call_method(obj, method_name, *args, **kwargs):
    # TODO 1: fetch attribute with getattr(obj, method_name, None)
    # TODO 2: if not callable, raise TypeError with a friendly message
    # TODO 3: call and return the result
    pass
```

*Hint*: `callable(attr)` is your friend.

---

### 22-3 · Better `describe(value)` (medium+)
Upgrade `describe(value)` to include:
- `has_len` and `len` (already done above)
- `has_items` and `first_item` (if it’s indexable)

```python todo
def describe2(value):
    # TODO: start from describe(value)
    # TODO: if value supports indexing, store first_item safely
    pass
```

*Hint*: Accessing `value[0]` can raise `TypeError`, `IndexError`, or `KeyError`. Catch all three expected lookup failures.

---

### 22-4 · Validate callbacks (advanced, bonus)
Implement `require_named_params(fn, required_names)` using `inspect.signature`.
Add tests for:
- happy path
- function with **kwargs
- missing parameters (raises TypeError)

*Hint*: Look at the “Bonus” section and copy the idea, then test it.

---

## Common mistakes (and how to avoid them)
- **Using `type(x) == SomeType` everywhere**: prefer `isinstance(x, SomeType)` for flexibility.
- **Forgetting `()`**: `text.upper` is a method, `text.upper()` is the result.
- **Calling `dir()` and getting overwhelmed**: filter the list (search for a word).
- **Using `getattr(obj, "x")` without a default**: it raises `AttributeError` if missing.
- **Assuming `vars(obj)` always works**: it doesn’t for many built‑ins (and that’s normal).
- **Over‑using introspection**: introspection is great for learning and debugging, but in real code it’s better to design clear interfaces.

---

## Explained solutions (short and clear)

### Solution 22-1
```python runnable
def report_types(values):
    result = []
    for v in values:
        result.append(f"{repr(v)} -> {type(v).__name__}")
    return result
```

### Solution 22-2
```python runnable
def call_method(obj, method_name, *args, **kwargs):
    attr = getattr(obj, method_name, None)
    if not callable(attr):
        raise TypeError(f"{type(obj).__name__} has no callable '{method_name}'")
    return attr(*args, **kwargs)
```

### Solution 22-3
```python runnable
def describe2(value):
    info = describe(value)
    try:
        info["first_item"] = value[0]
        info["has_items"] = True
    except (TypeError, IndexError, KeyError):
        info["first_item"] = None
        info["has_items"] = False
    return info
```

### Solution 22-4 (core)
```python runnable
import inspect

def require_named_params(fn, required_names):
    sig = inspect.signature(fn)
    probe = {name: object() for name in required_names}
    try:
        sig.bind(**probe)
    except TypeError as exc:
        raise TypeError(
            f"{fn.__name__} must accept these named arguments: {', '.join(required_names)}"
        ) from exc
```

---

## Checkpoint and rubric
- **Correctness**: helpers distinguish missing, non-callable, positional-only, and lookup-failure cases.
- **Readability**: returned metadata and errors use stable, descriptive names.
- **Error handling**: claims are defensive rather than promising safety for hostile objects.
- **Verification**: test lists, empty sequences, dictionaries, callables, and positional-only callbacks.
- **Explanation**: explain when introspection helps and when a clear interface is better.

## Closing reflection
Today you learned how to *ask Python questions* about values: what they are, what they can do, and how to use them safely. That’s a superpower for debugging and learning new libraries.

Next time you see an error like “object has no attribute…”, don’t panic:
use `type()`, `dir()`, `help()`, and `getattr()` like a calm detective. You’ve got this.
