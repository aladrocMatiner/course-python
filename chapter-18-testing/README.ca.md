# Capítol 18 · Proves amb pytest: assegura les teves idees

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Crearem un entorn de proves amb `pytest` i aprendrem a escriure tests clars, usar fixtures, parametritzar casos i mirar cobertura bàsica.

## Objectius d’aprenentatge
- Configurar `pytest`.
- Escriure proves per funcions (i excepcions).
- Reutilitzar dades amb fixtures.
- Parametritzar casos.
- Interpretar cobertura amb `--cov`.

---

## Instal·lació
```bash
pip install pytest pytest-cov
mkdir tests
```

---

## Primer test
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

Executa:
```bash
pytest -q
```

---

## `pytest.raises`
```python
import pytest
from math_utils import dividir

def test_dividir_por_cero():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)
```

---

## Cobertura
```bash
pytest --cov=. --cov-report=term-missing
```

---

## Resum
`pytest` et dona un feedback ràpid. Amb fixtures i parametrització, els tests són fàcils de mantenir i et deixen canviar codi sense por.
