<div dir="rtl">

# الفصل 8 · الشروط (Conditionals) والمنطق و Ternary

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم اتخاذ القرار في بايثون: `if/elif/else`، و`and/or/not`، والـ ternary operator. وسنذكر `match/case` كبديل حديث (Python 3.10+).

---

## `if/elif/else`
```python
peso = 3.2

if peso <= 1:
    tarifa = 5
elif peso <= 5:
    tarifa = 10
else:
    tarifa = 20
```

---

## Ternary
```python
score = 75
estado = "aprobado" if score >= 60 else "recuperación"
```

---

## هل يوجد switch؟
لا يوجد `switch` التقليدي في بايثون، لكن يوجد `match/case` ابتداءً من Python 3.10.

---

## ملخص
الشروط هي طريقة كتابة “قواعد” البرنامج. الفصل التالي: إدخال المستخدم (`input`) والتحقق من صحة البيانات.

</div>
