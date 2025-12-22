<div dir="rtl">

# الفصل 9 · الإدخال (Input) والتحقق الآمن

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم قراءة الإدخال من `input()` ومن سطر الأوامر ومن ملفات بسيطة، ثم تحويله والتحقق منه قبل استخدامه.

---

## كل شيء يأتي كنص
```python
nombre = input("¿Cómo te llamas? ")
print(f"Hola, {nombre}")
```

---

## تحويل + معالجة أخطاء
```python
raw_age = input("Edad: ")
try:
    edad = int(raw_age)
except ValueError:
    print("La edad debe ser un número entero.")
    edad = None
```

---

## قراءة ملف بسرعة
```python
from pathlib import Path

ruta = Path("datos.txt")
if not ruta.exists():
    raise FileNotFoundError("datos.txt no encontrado")
```

---

## ملخص
التحقق من الإدخال يجعل برنامجك أقوى. الفصل التالي: الحلقات (Loops) وفهم تكلفة الحلقات المتداخلة.

</div>
