<div dir="rtl">

# الفصل 12 · البرمجة الكائنية (OOP): الكلاسات والكائنات

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم أساسيات الكلاسات في بايثون: `__init__` والخصائص (attributes) والطرق (methods)، ولماذا نستخدم الكائنات لنمذجة “أشياء” في البرنامج. وفي النهاية نلمس فكرة تحويل الكائنات إلى `dict`/JSON (serialization).

---

## كلاس بسيط
```python
class Usuario:
    def __init__(self, nombre, email):
        self.nombre = nombre
        self.email = email
        self.activo = True

    def desactivar(self):
        self.activo = False
```

مثال:
```python
noor = Usuario("Noor", "noor@example.com")
noor.desactivar()
print(noor.activo)  # False
```

---

## Serialization إلى dict
```python
class Pedido:
    def __init__(self, id, total, items):
        self.id = id
        self.total = total
        self.items = items

    def to_dict(self):
        return {"id": self.id, "total": self.total, "items": self.items}
```

---

## ملخص
الكلاسات تساعدك على تنظيم البيانات والسلوك معًا. الفصل التالي: الملفات و الـ streams.

</div>
