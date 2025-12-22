<div dir="rtl">

# الفصل 2 · المتغيرات وأنواع البيانات البسيطة

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم أساسيات بايثون: كيف تعمل الملفات `.py`، كيف نفهم المتغيرات كـ “ملصقات” تشير إلى قيم، وكيف نتعامل مع النصوص (strings) والأرقام. سنرى أيضًا كيف نتحقق من نوع المتغير وكيف نختبر دوالنا بشكل صحيح.

## أفكار مهمة
- المتغير ليس “صندوقًا” بل اسم يشير إلى قيمة.
- النصوص: تنظيف المسافات، تغيير الأحرف، f-strings.
- الأرقام: `int` و`float` وبعض الحيل المفيدة.
- الأنواع: `type()` و`isinstance()`.

---

## 1) مثال تشغيل ملف
```python
print("Hello Python world!")
```

---

## 2) التحقق من نوع المتغير
```python
username = "ada"
age = 28
temperature = 20.5

print(type(username))          # <class 'str'>
print(type(age))               # <class 'int'>
print(isinstance(age, int))    # True
print(isinstance(temperature, float))  # True
print(isinstance(age, (int, float)))   # True
```

---

## 3) التحقق من مدخلات الدالة (Validation)
فكرة مهمة في البرمجة الاحترافية: إذا كانت المدخلات غير صحيحة، من الأفضل أن تفشل مبكرًا برسالة واضحة.

```python
def calcular_area_rectangulo(base, altura):
    if not isinstance(base, (int, float)):
        raise TypeError("base debe ser numérica")
    if not isinstance(altura, (int, float)):
        raise TypeError("altura debe ser numérica")
    if base <= 0 or altura <= 0:
        raise ValueError("las dimensiones deben ser positivas")

    return base * altura
```

---

## 4) اختبار سريع بـ pytest
```python
import pytest
from area import calcular_area_rectangulo

def test_calcular_area_rectangulo_valores_validos():
    assert calcular_area_rectangulo(3, 4) == 12

def test_calcular_area_rectangulo_rechaza_strings():
    with pytest.raises(TypeError):
        calcular_area_rectangulo("10", 5)
```

---

## ملخص
الآن تعرف كيف تستخدم المتغيرات بثقة، كيف تتعامل مع النصوص والأرقام، وكيف تتحقق من الأنواع وتكتب اختبارات بسيطة. في الفصل التالي سننتقل إلى القوائم (Lists).

</div>
