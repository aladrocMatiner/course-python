<div dir="rtl">

# الفصل 15 · الموديولات والحزم (Modules/Packages)

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم تقسيم المشروع إلى ملفات `.py` (موديولات)، وإنشاء حزم (packages) باستخدام `__init__.py`، وكيف نكتب “نقطة دخول” (entry point) نظيفة.

---

## مثال بسيط
`saludos.py`
```python
def hola(nombre):
    return f"Hola {nombre}!"
```

`app.py`
```python
import saludos
print(saludos.hola("Ada"))
```

---

## Entry point
```python
def main():
    print("Hola! Soy tu CLI")

if __name__ == "__main__":
    main()
```

---

## ملخص
تنظيم الكود إلى موديولات يجعل المشاريع الكبيرة ممكنة وأسهل في الاختبار. الفصل التالي: البيئات الافتراضية والاعتمادات.

</div>
