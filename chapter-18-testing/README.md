# Chapter 18 · Testing with pytest: Make Your Ideas Safe

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll set up a test environment with `pytest`, learn to write clear tests, use fixtures, parametrize cases, and measure basic coverage. You’ll see examples for functions, classes, and exception‑raising code.

## Learning path
1. **Why test?**
2. **Install and folder structure**.
3. **First test + running tests**.
4. **Fixtures**.
5. **Parametrization**.
6. **Quick coverage (`--cov`)**.

## Learning objectives
- Set up `pytest` in your projects.
- Write tests for pure functions and for controlled side effects.
- Reuse test data with fixtures.
- Parametrize lists of cases in a single test.
- Read basic coverage reports.

## Why it matters
Tests let you change code without fear and catch bugs before they reach production.

### Mini adventure
Before a play opens, there are dress rehearsals. Imagine each test is a tiny rehearsal: you verify each character says the right line. Then when the audience arrives (users), your function performs smoothly — no last‑minute panic.

### How to use this chapter (3 steps)
1. Create the example files exactly as shown.
2. Run `pytest` and look for `passed`.
3. Change a number on purpose to see a `failed` (it’s normal — you’re learning to detect errors).

---

## 1. Installation and structure

```bash
pip install pytest pytest-cov
mkdir tests
```

- Put tests in `tests/` and name them `test_*.py`.

---

## 2. First test
`math_utils.py`
```python
def sumar(a, b):
    return a + b

def dividir(a, b):
    if b == 0:
        raise ZeroDivisionError("No se puede dividir entre cero")
    return a / b
```

`tests/test_math_utils.py`
```python
from math_utils import sumar, dividir

def test_sumar():
    assert sumar(2, 3) == 5

def test_dividir():
    assert dividir(10, 2) == 5
```

Read `assert` as: “make sure this is true”. If it’s not, the test fails.

Run:
```bash
pytest
```

For a shorter output (nice for beginners):
```bash
pytest -q
```

When everything is fine you’ll see something like `2 passed`.

---

## 3. Fixtures

```python
import pytest

@pytest.fixture
def sample_pedidos():
    return [10, 20, 30]

def test_promedio(sample_pedidos):
    promedio = sum(sample_pedidos) / len(sample_pedidos)
    assert promedio == 20
```

- Fixtures are functions that provide ready-to-use test data.

---

## 4. Parametrization

```python
import pytest
from math_utils import dividir

@pytest.mark.parametrize(
    "a,b,resultado",
    [ (10, 2, 5), (9, 3, 3), (5, 2, 2.5) ]
)
def test_dividir(a, b, resultado):
    assert dividir(a, b) == resultado
```

- One test runs multiple times with different inputs.
- Think of it like a “rehearsal list”: same script, different actors.

---

## 5. Exceptions and `pytest.raises`

```python
from math_utils import dividir
import pytest

def test_dividir_por_cero():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)
```

---

## 6. Coverage

```bash
pytest --cov=. --cov-report=term-missing
```

- Shows which lines weren’t executed by your tests.

---

## Guided exercises (with TODOs)
1. **18-1 · Reusable fixture**
   ```python
   # TODO 1: create fixture db_tmp that uses tmp_path to simulate a file
   # TODO 2: use it in two tests
   ```

2. **18-2 · Parametrize validations**
   ```python
   # TODO 1: create test validacion_payload with multiple valid/invalid inputs
   ```

3. **18-3 · Coverage**
   ```bash
   # TODO 1: run pytest --cov and read the report
   ```

---

## Common mistakes
- Forgetting the `test_` prefix and pytest doesn’t detect the file.
- Mixing production code with test code (keep separate folders).
- Fixtures with side effects that aren’t reset (use `yield` for cleanup).

---

## Explained solutions
1. **Fixture db_tmp**: `tmp_path / "db.json"` creates temporary paths without dirtying the repo.
2. **Parametrize**: `pytest.mark.parametrize` reduces duplication and forces you to think about edge cases.
3. **Coverage**: look at missing lines and decide whether you need more tests.

---

## Summary
`pytest` gives you a fast feedback loop to validate each module. With fixtures and parametrization, your tests become expressive and easy to maintain.

## Closing reflection
Make testing a habit: even small scripts benefit from verifying behavior before you integrate them into bigger projects.
