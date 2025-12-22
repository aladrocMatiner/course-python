# Kapitel 18 · Testning med pytest

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Vi installerar `pytest`, skriver våra första tester, använder `pytest.raises` och tittar snabbt på coverage.

---

## Installera
```bash
pip install pytest pytest-cov
mkdir tests
```

---

## Första testet
```python
def sumar(a, b):
    return a + b
```

```python
def test_sumar():
    assert sumar(2, 3) == 5
```

---

## Testa undantag
```python
import pytest

def test_dividir_por_cero():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)
```

---

## Coverage
```bash
pytest --cov=. --cov-report=term-missing
```

---

## Sammanfattning
Tester gör att du kan ändra kod utan rädsla. Nästa kapitel: HTTP och API:er.
