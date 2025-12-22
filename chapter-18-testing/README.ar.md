<div dir="rtl">

# الفصل 18 · الاختبارات باستخدام pytest

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنثبت `pytest` ونكتب أول اختبار، ونتعلم `pytest.raises` لاختبار الاستثناءات، ونرى فكرة coverage بسرعة.

---

## تثبيت
```bash
pip install pytest pytest-cov
mkdir tests
```

---

## اختبار بسيط
```python
def sumar(a, b):
    return a + b

def test_sumar():
    assert sumar(2, 3) == 5
```

---

## اختبار استثناء
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

## ملخص
الاختبارات تمنحك ثقة لتعديل الكود بدون خوف. الفصل التالي: HTTP وواجهات API.

</div>
