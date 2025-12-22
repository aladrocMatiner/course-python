<div dir="rtl">

# الفصل 14 · الاستثناءات (Exceptions): من مبتدئ إلى محترف

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم التعامل مع الأخطاء عبر `try/except`، واستخدام `raise` لرفع أخطاء واضحة، وكتابة اختبارات تؤكد أن الدالة ترمي الاستثناء الصحيح.

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

## اختبار الاستثناء
```python
import pytest

def test_dividir_zero():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)
```

---

## ملخص
إدارة الأخطاء بشكل جيد تجعل برنامجك أكثر أمانًا وأسهل في التصحيح. الفصل التالي: الموديولات والحزم (Modules/Packages).

</div>
