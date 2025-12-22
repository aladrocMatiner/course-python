<div dir="rtl">

# الفصل 22 · الاستبطان (Introspection): وضع المحقق في بايثون

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
في هذا الفصل ستتعلم *الاستبطان* (Introspection): كيف تنظر إلى قيمة وتُسائلها: “ما أنت؟” و “ماذا تستطيع أن تفعل؟”. سنستخدم أدوات مثل `type()` و `isinstance()` و `dir()` و `help()` و `getattr()` و `callable()` لكي نستكشف الأشياء بأمان.

ثم سنبني أداة “محقق” صغيرة اسمها `describe(value)`، و (كمكافأة) سنتعرّف على `inspect.signature()` لفهم معاملات (parameters) الدوال والتحقق منها — وهذا مفيد جدًا عند اختبار الـ callbacks.

## أهداف التعلم
- معرفة نوع القيمة باستخدام `type()` والتحقق بأمان باستخدام `isinstance()`.
- فهم الفرق بين `str()` و `repr()` (التصحيح Debug يحب `repr`).
- التمييز بين السمة (attribute) والطريقة (method) وتجنب خطأ نسيان `()`.
- استكشاف كائن غير معروف باستخدام `dir()` و `help()`.
- قراءة السمات بأمان باستخدام `getattr()` وبناء ملخّص عبر `describe()`.

## لماذا هذا مهم؟
أحيانًا ستتعامل مع قيم “غامضة” (من إدخال المستخدم، من ملف، من مكتبة). الاستبطان يساعدك أن تفهمها بدل التخمين.

---

## 1) ما هذا؟
```python
value = 42
print(type(value).__name__)          # int
print(isinstance(value, int))        # True
print(isinstance(value, (int, float)))  # True
```

`None`:
```python
x = None
print(x is None)
print(type(x).__name__)  # NoneType
```

---

## 2) الطباعة للتصحيح: `str()` و `repr()`
```python
text = "hello\nworld"
print(text)
print(repr(text))
```

---

## 3) سمة أم طريقة؟ (ولا تنسَ `()`)
```python
text = "hello"
print(text.upper)
print(callable(text.upper))
print(text.upper())
```

---

## 4) الاستكشاف: `dir()` و `help()`
```python
text = "hello"
names = [name for name in dir(text) if "upper" in name]
print(names)
print(str.upper.__doc__)
help(str.upper)
```

---

## 5) وصول آمن: `getattr()` و `vars()`
```python
class Player:
    def __init__(self, name):
        self.name = name

p = Player("Frej")
print(getattr(p, "name", "<anonymous>"))
print(getattr(p, "nickname", "<anonymous>"))
print(vars(p))
```

---

## مشروع صغير: `describe(value)`
```python
def describe(value):
    info = {
        "type": type(value).__name__,
        "repr": repr(value),
        "is_callable": callable(value),
    }
    try:
        info["len"] = len(value)
        info["has_len"] = True
    except TypeError:
        info["len"] = None
        info["has_len"] = False
    info["name_attr"] = getattr(value, "name", None)
    return info
```

---

## مكافأة: التحقق من معاملات الدوال (`inspect.signature()`)
```python
import inspect

def require_named_params(fn, required_names):
    sig = inspect.signature(fn)
    params = sig.parameters
    if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()):
        return
    missing = [name for name in required_names if name not in params]
    if missing:
        raise TypeError(f"{fn.__name__} must accept: {', '.join(missing)}")
```

---

## تمارين (TODO + تلميحات)
1. اكتب `report_types(values)` باستخدام `type(x).__name__` و `repr(x)`.
2. اكتب `call_method(obj, method_name, ...)` باستخدام `getattr` و `callable`.
3. طوّر `describe` بإضافة `first_item` مع التعامل مع `TypeError` و `IndexError`.
4. مكافأة: اكتب اختبارات pytest لـ `require_named_params`.

---

## أخطاء شائعة
- `dir()` يعطي قائمة طويلة: صفِّها بكلمة.
- `getattr(obj, "x")` بدون قيمة افتراضية قد يفشل.
- نسيان `()` في الطرق: `text.upper` مقابل `text.upper()`.

---

## تأمل ختامي
الاستبطان هو “مصباحك” عندما تتعلم وتصحح الأخطاء. اسأل القيم بهدوء باستخدام `type()` و `dir()` و `help()` خطوة بخطوة.

</div>

