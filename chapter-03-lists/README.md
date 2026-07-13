# Chapter 3 · Introducing Lists

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
In this chapter you’ll learn what a list is, how to access each element, and how to change, sort, and protect your code from common mistakes. We’ll practice the essential methods (`append`, `insert`, `pop`, `remove`, `sort`) and write tiny tests to guarantee our functions behave the way we expect.

## Learning path
1. **Intro**: a mental model of a list and why square brackets (`[]`) matter.
2. **Access and use**: indexes, `-1` for the end, and reusing values in messages.
3. **Modify/add/remove**: `append`, `insert`, `del`, `pop`, `remove` and when to choose each.
4. **Organize**: `sort`, `sorted`, `reverse`, `len` and quick checks.
5. **Avoid errors**: spotting `IndexError` and preventing it.
6. **Tests and guided exercises** to make list work safe.

## Learning objectives
- Define a list and access elements by position, including negative indexes.
- Modify existing items and add/remove items depending on your program’s needs.
- Reorder lists temporarily or permanently and measure their length.
- Avoid `IndexError` by validating indexes and using `len()` and `-1` correctly.
- In the optional professional route, write small tests that confirm list functions don’t create unwanted side effects.

## Prerequisites and routes
- **Prerequisite:** complete the [Chapter 2 checkpoint](../chapter-02-variables/README.md). The essential route uses variables, strings, numbers, and direct `print` calls.
- **Essential route · 55–70 min:** list creation, access, mutation, removal, sorting, length, and exercise 3-11. Outcome: maintain a guest or task list and recover from an invalid index.
- **Intermediate route · 30–40 min:** complete exercises 3-4 through 3-10 and explain which operations mutate the original list.
- **Optional professional preview · 40–50 min:** start at “Mini automated tests” and continue through the guided TODOs. It previews [conditionals](../chapter-08-conditionals/README.md), [loops](../chapter-10-loops/README.md), [functions](../chapter-11-functions/README.md), [exceptions](../chapter-14-exceptions/README.md), and [pytest](../chapter-18-testing/README.md). You may copy those complete examples or skip directly to “Common mistakes”; they are not required for the essential checkpoint.

## Why it matters
Without lists, you can only hold one value per variable. Lists let you store catalogs, users, orders, or readings in one ordered, dynamic container. Mastering these patterns opens the door to processing hundreds or thousands of elements with just a few methods and loops.

### Mini adventure
Think of a list like a backpack with numbered pockets. You can put things in, take them out, move them around, and count how many you have. When you program, that backpack lets you carry “many similar things” without going crazy creating one variable per item.

## Predict before running
Look at the first `bicycles` list. Before executing it, predict the values at indexes `0`, `-1`, and `4`. Run only the valid accesses first, then use the `IndexError` section to explain and recover from the invalid prediction.

---

## What is a list?
A list is an ordered collection of items. In Python you create it with square brackets `[]`, and items are separated with commas.

```python runnable
# bicycles.py
bicycles = ["trek", "cannondale", "redline", "specialized"]
print(bicycles)
```

Output:
```text illustrative
['trek', 'cannondale', 'redline', 'specialized']
```
Python prints the literal representation, but usually you want to access each item.

### Accessing elements in a list
Use the index (position) inside brackets to get one element:

```python illustrative
print(bicycles[0])
print(bicycles[0].title())
```

### Indexes start at 0
The first element is index `0`, the second is `1`, etc. The fourth element is `bicycles[3]`. Negative indexes count from the end (`-1` is last, `-2` is second-to-last).

### Using individual values from a list
You can place list items inside messages using f-strings:

```python illustrative
message = f"My first bicycle was a {bicycles[0].title()}."
print(message)
```

Example with people:
```python runnable
names = ["Noor", "Frej", "Taha"]
print(names[0])
print(f"Hello, {names[1]}!")
```

### Try it yourself (3-1 to 3-3)
1. **3-1 · Names**: create a `names` list with friends and print each name one by one.
2. **3-2 · Greetings**: reuse the list but print a personalized greeting for each person.
3. **3-3 · Your own list**: create a list of your favorite transport and generate sentences like “I would like to own a …”.

---

## Modifying, adding, and removing elements
Lists are dynamic: you can change them as your program runs.

### Modifying elements in a list
```python runnable
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles)

motorcycles[0] = 'ducati'
print(motorcycles)
```

### Appending elements
```python illustrative
motorcycles.append('ducati')
print(motorcycles)

# Build from scratch
teams = []
teams.append('frontend')
teams.append('backend')
print(teams)
```

### Inserting elements
```python illustrative
motorcycles.insert(0, 'victory')
print(motorcycles)
```

### Removing elements
- `del lista[i]` removes by position (does not return the value).
- `pop()` removes and returns the last item (or an optional index).
- `remove(valor)` finds and removes the first item equal to `valor`.

```python runnable
motorcycles = ['honda', 'yamaha', 'suzuki', 'ducati']

last = motorcycles.pop()
print(f"Last: {last}")

first = motorcycles.pop(0)
print(f"First: {first}")

motorcycles.remove('yamaha')
print(motorcycles)
```

> Note: `remove` only deletes the first match. If you need to remove all of them, you’ll use loops later.

### Try it yourself (3-4 to 3-7)
1. **3-4 · Guest List**: make a list of guests and print personalized invitations.
2. **3-5 · Changing Guest List**: replace a guest who can’t come and reprint invitations.
3. **3-6 · More Guests**: announce a bigger table; use `insert` and `append` to add three more people.
4. **3-7 · Shrinking Guest List**: reduce to two people using `pop`; thank them and delete the rest with `del`.

---

## Organizing a list
When data arrives in an unpredictable order, you often want to show it sorted without destroying the original order.

### Sorting permanently with `sort()`
```python runnable
cars = ['bmw', 'audi', 'toyota', 'subaru']
cars.sort()
print(cars)  # ['audi', 'bmw', 'subaru', 'toyota']
```
`cars.sort(reverse=True)` reverses alphabetic order and modifies the list in place.

### Sorting temporarily with `sorted()`
```python illustrative
print(sorted(cars))          # sorted copy
print(sorted(cars, reverse=True))
print(cars)                  # the original list did not change
```

### Printing a list in reverse order
```python illustrative
cars.reverse()
print(cars)
```
`reverse()` flips the current order (it does not “sort backwards”), and you can undo it by calling it again.

### Finding the length of a list
```python illustrative
print(len(cars))
```
Length helps you validate indexes and show “how many items” you have (guests, remaining entries, etc.).

### Try it yourself (3-8 to 3-10)
1. **3-8 · Seeing the World**: create a list of places and practice `sorted`, `reverse`, `sort` and `len` without losing the original order.
2. **3-9 · Dinner Guests**: using exercises 3-4 to 3-7, print how many people you’re inviting with `len()`.
3. **3-10 · Every function**: pick any list (mountains, cities, etc.) and use each method from this chapter at least once.

---

## Avoiding `IndexError` when working with lists
The most common error is asking for an out-of-range index:

```python illustrative
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles[3])  # IndexError
```

Tips to prevent it:
- Check the length before accessing (`if len(motorcycles) > 2:`).
- Use `-1` for the last item and don’t assume the size.
- If you remove items while iterating, loop over a copy (`for item in items[:]`).
- If your function receives an external index, validate it:
  ```python illustrative
  def get_item(items, index):
      if not 0 <= index < len(items):
          raise IndexError("index out of range")
      return items[index]
  ```
- If you hit an `IndexError`, print the list (or `len(items)`) to confirm its real state.

### Try it yourself (3-11)
Trigger an `IndexError` on purpose by changing a valid index to an invalid one, then fix it. You’ll understand Python’s debugging flow much better.

---

## Mini automated tests
**Optional preview:** the next sections use `def`, `if`, `raise`, loops, comprehensions, imports, and `pytest`. The minimum idea is that a function names reusable work and a test calls it with a known input. Copy each complete file exactly or skip this route until the linked later chapters; do not install `pytest` from an unrelated source.

```python illustrative
# lists_utils.py
def prioritize_task(tasks, new_task):
    if not isinstance(tasks, list):
        raise TypeError("tasks must be a list")
    copy = tasks[:]
    copy.insert(0, new_task)
    return copy

# tests/test_lists_utils.py
import pytest
from lists_utils import prioritize_task

def test_prioritize_task_adds_to_front():
    original = ["document", "refactor"]
    result = prioritize_task(original, "set up CI")
    assert result[0] == "set up CI"
    assert original[0] == "document"  # the copy protects the original list

def test_prioritize_task_rejects_non_lists():
    with pytest.raises(TypeError):
        prioritize_task("not-a-list", "something")
```

---

## Progressive examples: playing with interesting angles
These examples ramp up difficulty to show how lists behave in real backend-ish situations.

### Example 1 · Interactive checklist
```python runnable
checklist = ["Create virtualenv", "Install dependencies", "Run tests"]

for step in checklist:
    print(f"- [ ] {step}")

print(f"The checklist has {len(checklist)} steps.")
last = checklist.pop()              # Get the last step
print(f"Last completed step: {last}")
checklist.append("Publish release")  # Add a new task at the end
```
- You practice direct access, `len()`, and basic mutations (`pop`, `append`).
- Useful for CLI scripts where the steps change while the program runs.

### Example 2 · Support queue (list as queue)
```python runnable
ticket_queue = ["BUG-101", "BUG-102", "BUG-103"]

def handle_ticket(queue):
    if not queue:
        return None
    return queue.pop(0)  # pop(0) simulates a FIFO queue

def register_ticket(queue, ticket):
    queue.append(ticket)

current_ticket = handle_ticket(ticket_queue)
print(f"Handling: {current_ticket}")
register_ticket(ticket_queue, "BUG-200")
print(f"Pending: {ticket_queue}")
```
- `pop(0)` has a higher cost, but it makes FIFO behavior clear; later you can swap in `collections.deque`.
- These methods are ready to plug into a Django view or a webhook without storage yet.

### Example 3 · Readings normalizer (validation + tests)
```python runnable
# normalizer.py
def normalize_readings(readings, *, max_limit):
    if not isinstance(readings, list):
        raise TypeError("readings must be a list")
    if not all(isinstance(value, (int, float)) for value in readings):
        raise ValueError("all readings must be numeric")
    if not readings:
        return {"average": 0, "out_of_range": [], "top3": []}

    out_of_range = [value for value in readings if value > max_limit]
    average = sum(readings) / len(readings)
    top3 = sorted(readings, reverse=True)[:3]
    return {"average": average, "out_of_range": out_of_range, "top3": top3}
```

```python illustrative
# tests/test_normalizer.py
import pytest

from normalizer import normalize_readings

def test_normalize_readings_detects_outliers():
    data = [19.2, 20.1, 22.5, 18.0]
    result = normalize_readings(data, max_limit=20)
    assert result["out_of_range"] == [22.5]
    assert result["top3"][0] == 22.5

def test_normalize_readings_validates_types():
    with pytest.raises(ValueError):
        normalize_readings([10, "not-num"], max_limit=50)

def test_normalize_readings_empty_keeps_schema():
    result = normalize_readings([], max_limit=20)
    assert result == {"average": 0, "out_of_range": [], "top3": []}
```
- Combines slicing (`[:3]`), sorting, and strong validation before you put it behind an API.
- Notice how the tests describe the interesting angles: outliers and correct error signaling.

---

## Guided exercises (with TODOs)
1. **G3-1 · Dynamic invitations**
   ```python todo
   guests = ["Noor", "Frej", "Taha"]
   # TODO 1: print a personalized message for each guest
   # TODO 2: add two new people at the end using append
   # TODO 3: remove the second guest and print who won’t attend
   ```
   *Hint*: `append`, `pop`, and a `for` loop are enough.

2. **G3-2 · Price list**
   ```python todo
   prices = [12.5, 9.99, 3.5, 18.0]
   # TODO 1: compute the average with sum/len
   # TODO 2: create a list of prices with VAT (21%)
   # TODO 3: use slicing to show only the two highest prices
   ```
   *Hint*: combine `sorted(prices)` and `[-2:]`.

3. **G3-3 · Sensors and validations**
   ```python todo
   readings = [19.2, 20.1, 21.3, 18.9]
   # TODO 1: write function out_of_range(readings, limit)
   # TODO 2: add a test that confirms False when all are in range
   # TODO 3: test that it raises TypeError if readings is not a list
   ```
   *Hint*: use `any(value > limit for value in readings)` and the test pattern above.

---

## Common mistakes
- Starting to count from 1 and getting `IndexError`.
- Modifying a list while iterating without copying first.
- Confusing `append` (adds the list as a single element) with `extend`.
- Changing the original order with `sort()` when you needed a sorted copy (`sorted`).
- Forgetting that `remove` only removes the first occurrence.

---

## Explained solutions for the guided exercises
1. **G3-1**: generate messages with a `for` loop, `append` adds guests, and `pop(1)` returns who was removed so you can announce it.
2. **G3-2**: average is `sum(prices)/len(prices)`; VAT list is `[price * 1.21 for price in prices]`; top two come from `sorted(prices)[-2:]`.
3. **G3-3**: `any(value > limit for value in readings)` detects out-of-range values after `isinstance(readings, list)`; tests cover the happy path and type errors.

---

## Checkpoint and self-assessment
Build a list with three tasks. Predict the first and last values, add one task, remove one, show a sorted copy, and prove the original order is unchanged. Then request an invalid index on purpose, read `IndexError`, and recover by checking `len()` before trying again.

Score one point for each criterion:
- **Correctness:** access, add, remove, and sorted-copy results match your predictions.
- **Readability:** names communicate what the list contains and each operation has one clear purpose.
- **Error handling:** you can explain the invalid index and recover without guessing the list length.
- **Verification:** you print both original and derived lists and identify which operation mutated data.
- **Explanation:** you can justify choosing `pop`, `remove`, `sort`, or `sorted` for a concrete case.

The essential route is complete with 5/5. The optional route adds one more check: `normalize_readings([], max_limit=20)` preserves all three result keys, including `top3`.

---

## Summary
In this chapter you defined lists, accessed elements with positive and negative indexes, reused values inside strings, modified the list in real time (add, insert, remove), sorted it permanently or temporarily, and used `len()` and `reverse()` to inspect it. You also learned how to avoid `IndexError` and even wrote tests to validate these operations.

## Closing reflection
Mastering lists means handling whole collections of data with just a few lines: you can add, remove, slice, sort, and validate information without duplicating code. In the next chapter we’ll move on to structures that pair *keys* with *values* (dictionaries), which is the foundation of JSON and APIs.
