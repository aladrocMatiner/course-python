<div dir="rtl">

# الفصل 5 · المجموعات (Sets) وعدم التكرار

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم `set` و`frozenset` لإزالة العناصر المكررة، وفحص “هل هذا العنصر موجود؟” بسرعة، ومقارنة مجموعات البيانات بعمليات مثل الاتحاد والتقاطع.

---

## إزالة التكرار + `in`
```python
correos = ["ada@example.com", "linus@example.com", "ada@example.com"]
correos_unicos = set(correos)
print("ada@example.com" in correos_unicos)
```

---

## عمليات المجموعات
```python
permisos_admin = {"view", "edit", "delete"}
permisos_editor = {"view", "edit"}

print(permisos_admin & permisos_editor)  # تقاطع
print(permisos_admin - permisos_editor)  # فرق
```

---

## `frozenset` (غير قابل للتغيير)
مفيد عندما تحتاج مجموعة كـ “مفتاح” داخل قاموس.

---

## ملخص
المجموعات رائعة للـ permissions والـ tags ومنع التكرار. في الفصل التالي سنتعلم tuples (قيم مرتبة وغير قابلة للتغيير غالبًا).

</div>
