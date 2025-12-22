# Kapitel 14 · Undantag (exceptions): från nybörjare till hjälte

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Du lär dig hantera fel med `try/except`, använda `else`/`finally`, kasta egna fel med `raise` och skriva enkla tester som bekräftar att fel kastas.

---

## `try/except`
```python
try:
    resultado = int("abc")
    print(resultado)
except ValueError:
    print("No era un número válido")
```

---

## `raise`
```python
def dividir(a, b):
    if b == 0:
        raise ZeroDivisionError("El denominador no puede ser cero")
    return a / b
```

---

## Testa undantag
```python
import pytest

def test_dividir_zero():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)
```

---

## Sammanfattning
Bra felhantering gör din kod tryggare och lättare att felsöka. Nästa kapitel: moduler och paket.
