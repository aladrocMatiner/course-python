<div dir="rtl">

# الفصل 22 · الاستبطان: وضع المحقق في Python

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
ستتعلّم في هذا الفصل *الاستبطان* (introspection): أي النظر إلى قيمة وسؤالها «ما أنت؟» و«ماذا تستطيع أن تفعل؟». ستستخدم أدوات مثل `type()` و`isinstance()` و`dir()` و`help()` و`getattr()` و`callable()` للاستكشاف بأمان.

بعد ذلك ستبني أداة محقق صغيرة باسم `describe(value)`. وفي القسم الإضافي ستتعلّم فحص معاملات دالة باستخدام `inspect.signature()` كي تتحقق من callbacks وتكتب اختبارات أفضل.

## مسار التعلّم
1. **اكتشاف النوع**: `type` و`isinstance`، وحالة `None`.
2. **الطباعة بوضوح**: الفرق بين `str` و`repr` ولماذا تفضّل عملية التشخيص `repr`.
3. **الطرائق والسمات**: `callable` وفخ نسيان الأقواس.
4. **استكشاف كائنات مجهولة**: `dir` و`help` وسلاسل التوثيق.
5. **الوصول الآمن**: `getattr` و`hasattr` و`vars` ومتى تفشل.
6. **مشروع صغير**: `describe(value)` لتلخيص كائن بأمان.
7. **قسم إضافي**: `inspect.signature()` للتحقق من المعاملات المطلوبة مع اختبارات pytest.

## أهداف التعلّم
- معرفة نوع قيمة والتحقق منه بأمان باستخدام `isinstance`.
- استخدام `repr()` لتشخيص «القيم الغامضة» وفهم الفرق بين `str()` و`repr()`.
- تفادي أخطاء شائعة مثل الإشارة إلى طريقة من دون `()`.
- استكشاف الكائنات المضمّنة وكائنات الدورة العادية مع إدراك أي hooks يمكنه تنفيذ شيفرة.
- قراءة السمات بصورة دفاعية واكتشاف الإمكانات باستخدام `callable` و`hasattr` من دون اعتبار الكائنات غير الموثوقة بيانات خاملة.
- بناء أدوات صغيرة واختبارها للتحقق من المدخلات والـ callbacks.

## لماذا يهم هذا؟
أثناء التعلّم ستقابل باستمرار قيمًا لا تفهمها بالكامل بعد، مثل النصوص والقوائم والقواميس وكائنات المكتبات. يمنحك الاستبطان وسيلة آمنة لاستكشافها.

تستخدم أطر العمل الاستبطان في مشاريع الخلفية الحقيقية أيضًا. فقد تسأل: «هل هذا قابل للاستدعاء؟»، أو «هل يقبل `request`؟»، أو «هل يملك هذا الكائن `.save()`؟»، أو «ما الحقول الموجودة؟». لست بحاجة إلى السحر؛ تعلّم الأساسيات الآمنة فقط.

### مغامرة صغيرة: أنت محقق Python
تخيّل أنك محقق يحمل مصباحًا:
- `type()` هو **ماسح الهوية**: «ما أنت؟».
- `dir()` هو **قائمة صندوق الأدوات**: «ماذا تستطيع أن تفعل؟».
- `help()` و`__doc__` هما **الدليل**: «كيف يعمل هذا؟».
- `getattr()` هي **أداة الالتقاط الآمنة**: «أعطني هذه السمة، أو قيمة افتراضية».

من الطبيعي أن يبدو هذا غريبًا في البداية. يتعلّمه كل مبرمج بالتجربة على قيم حقيقية.

## المتطلبات المسبقة
- الأنواع والدوال والأصناف والاستثناءات والمعاملات القابلة للاستدعاء من الفصول 2 و11 و12 و14.
- يلزم `pytest` من الفصل 18 لاختبارات callbacks الإضافية فقط.

## توقّع قبل التشغيل
اختر قيمة عادية وتوقّع ما الذي ستكشفه `type()` و`repr()` ومكالمة آمنة واحدة لـ`getattr()`. نفّذ هذه الملاحظات نفسها، وقارنها بتوقّعك، وتذكر أن introspection hooks في الكائنات غير الموثوقة قد تنفذ شيفرة.

---

## 1) السؤال الأول: ما هذا؟

### تخبرك `type()` بالنوع الدقيق
```python runnable
value = 42
print(type(value))          # <class 'int'>
print(type(value).__name__) # int
```

### غالبًا ما يكون `isinstance()` الفحص الأكثر أمانًا
```python runnable
value = 42
print(isinstance(value, int))          # True
print(isinstance(value, (int, float))) # True (tuple means “any of these”)
```

لماذا نقول «أكثر أمانًا»؟ لأنه يعمل مع **الأصناف الفرعية** أيضًا:

```python runnable
print(isinstance(True, int))  # True (bool is a kind of int in Python)
print(type(True) is int)      # False (exact type is bool)
```

### حالة خاصة: `None`
```python runnable
x = None
print(x is None)          # the standard way
print(type(x).__name__)   # NoneType
```

---

## 2) الطباعة للتشخيص: `str()` و`repr()`
عند عرض شيء للمستخدم تكون `str()` مناسبة. أما عند التشخيص فـ`repr()` صديقك الأفضل، لأنها تحاول إنتاج تمثيل **غير ملتبس**.

```python runnable
text = "hello\nworld"
print(text)        # prints two lines
print(repr(text))  # 'hello\nworld' (shows the \n)
```

### الكائنات المخصّصة: لماذا تساعد `repr`؟
```python runnable
class User:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"User({self.name})"

    def __repr__(self):
        return f"User(name={self.name!r})"  # !r uses repr()

u = User("Noor")
print(u)       # User(Noor)
print([u])     # [User(name='Noor')]
print(f"{u!r}")  # User(name='Noor')
```

يحتار كثيرون هنا، وهذا طبيعي: تستخدم `print(u)` التعبير `str(u)`، بينما تعرض الحاويات، مثل القوائم، عناصرها غالبًا باستخدام `repr(...)`.

---

## 3) السمات والطرائق وفخ نسيان `()`
**السمة** بيانات، أما **الطريقة** فهي شيء تستطيع استدعاءه.

```python runnable
text = "hello"
print(text.upper)         # this is a method object
print(callable(text.upper))  # True
print(text.upper())       # HELLO
```

خطأ شائع:
```python runnable
text = "hello"
shout = text.upper   # forgot () → shout is not a string
print(shout)         # <built-in method upper of str object at ...>
```

إذا رأيت شيئًا مثل `<built-in method ...>`، فقد حصلت على الطريقة نفسها لكنك لم تستدعها.

---

## 4) استكشاف كائن مجهول باستخدام `dir()` و`help()`
### تمنحك `dir(obj)` قائمة بالأسماء
```python runnable
text = "hello"
names = [name for name in dir(text) if "upper" in name]
print(names)  # ['isupper', 'upper']
```

قد تكون القائمة طويلة، وهذا طبيعي. رشّحها!

### تشرح `help(...)` وسلاسل التوثيق طريقة الاستخدام
```python runnable
print(str.upper.__doc__)
```

وإذا أردت الدليل كاملًا:
```python runnable
help(str.upper)
```

---

## 5) الوصول الآمن: `getattr()` و`hasattr()` و`vars()`

### `getattr(obj, "name", default)`
هذا مناسب عندما لا تعرف إن كانت السمة موجودة:

```python runnable
class Player:
    def __init__(self, name):
        self.name = name

p = Player("Frej")
print(getattr(p, "name", "<anonymous>"))     # Frej
print(getattr(p, "nickname", "<anonymous>")) # <anonymous>
```

### `hasattr(obj, "name")`
```python illustrative
print(hasattr(p, "name"))     # True
print(hasattr(p, "nickname")) # False
```

ينفذ `hasattr` داخليًا بحثًا عن السمة، ولذلك قد يشغّل شيفرة الخاصية أو descriptor نفسها التي يشغلها `getattr`؛ فهو ليس فحص أمان خاليًا من الآثار الجانبية.

### `vars(obj)` أو `obj.__dict__` للكائنات البسيطة
```python illustrative
print(vars(p))  # {'name': 'Frej'}
```

مهم: لا تعمل `vars()` مع كل كائن. وفشلها طبيعي، لأن بعض الكائنات تخزّن بياناتها بطريقة مختلفة.

### قد ينفذ الاستبطان hooks
تستطيع كائنات Python تخصيص `__repr__` و`__len__` و`__dir__` و`__getattribute__` وdescriptors والخصائص. لذلك قد تنفذ `repr` و`len` و`dir` و`vars` و`getattr` و`hasattr` شيفرة المستخدم، أو تُحدث آثارًا جانبية، أو ترفع استثناء، أو تحجب التنفيذ، أو تستهلك الموارد. استخدم هذه الأدوات مع كائنات تثق بها في العملية الحالية؛ ولا تصف قيمة plugin عدائية بأنها «آمنة».

يستطيع `inspect.getattr_static` فحص سمة من دون استدعاء بحث descriptor/الخاصية المعتاد، لكنه يعيد descriptor نفسه لا قيمته المحسوبة:

```python runnable
import inspect

class Probe:
    calls = 0

    @property
    def status(self):
        type(self).calls += 1
        return "ready"

probe = Probe()
descriptor = inspect.getattr_static(probe, "status")
print(type(descriptor).__name__, Probe.calls)  # property 0
print(getattr(probe, "status"), Probe.calls)   # ready 1
```

يضيّق البحث الساكن خطرًا واحدًا؛ لكنه لا يجعل الاستدعاءات اللاحقة للكائن المعاد آمنة ولا يضع شيفرة اعتباطية داخل sandbox للوقت أو الموارد.

---

## مشروع صغير: `describe(value)` لملخص دفاعي
سنكتب دالة صغيرة تعيد قاموسًا يصف قيمة من دون أن تتعطل.

```python runnable
def describe(value):
    info = {
        "type": type(value).__name__,
        "repr": repr(value),
        "is_callable": callable(value),
    }

    # Does it have a length?
    try:
        info["len"] = len(value)
        info["has_len"] = True
    except TypeError:
        info["len"] = None
        info["has_len"] = False

    # Does it have a "name" attribute?
    info["name_attr"] = getattr(value, "name", None)
    return info

print(describe("hello"))
print(describe([1, 2, 3]))

class Box:
    def __init__(self, name):
        self.name = name
print(describe(Box("Taha")))
```

تمنح الأداة أدلة دفاعية للقيم العادية؛ فقد تنفذ `repr()` والخصائص شيفرة من الكائن، لذلك لا تعد بالأمان مع الكائنات العدائية.

---

## قسم إضافي: التحقق من معاملات الدوال باستخدام `inspect.signature()`
قد تقبل أحيانًا دالة، أي callback، وتريد التأكد من أن لديها المعاملات التي تحتاجها.

في هذا المثال نريد callback تستطيع قبول `user_id` و`payload`.

```python runnable
import inspect

def require_named_params(fn, required_names):
    sig = inspect.signature(fn)
    probe = {name: object() for name in required_names}
    try:
        sig.bind(**probe)
    except TypeError as exc:
        raise TypeError(
            f"{fn.__name__} must accept these named arguments: {', '.join(required_names)}"
        ) from exc
```

### عرض سريع
```python illustrative
def ok(user_id, payload):
    return (user_id, payload)

def flexible(**kwargs):
    return kwargs

def bad(user_id):
    return user_id

def positional_only(user_id, payload, /):
    return (user_id, payload)

require_named_params(ok, ["user_id", "payload"])        # OK
require_named_params(flexible, ["user_id", "payload"])  # OK (**kwargs)
require_named_params(bad, ["user_id", "payload"])       # raises TypeError
require_named_params(positional_only, ["user_id", "payload"])  # raises TypeError
```

### اختبارات صغيرة باستخدام pytest
```python illustrative
# tests/test_introspection.py
import pytest
from chapter_22 import require_named_params

def ok(user_id, payload):
    return (user_id, payload)

def flexible(**kwargs):
    return kwargs

def bad(user_id):
    return user_id

def positional_only(user_id, payload, /):
    return (user_id, payload)

def test_require_named_params_ok():
    require_named_params(ok, ["user_id", "payload"])

def test_require_named_params_kwargs_ok():
    require_named_params(flexible, ["user_id", "payload"])

def test_require_named_params_raises():
    with pytest.raises(TypeError):
        require_named_params(bad, ["user_id", "payload"])

def test_require_named_params_rejects_positional_only():
    with pytest.raises(TypeError):
        require_named_params(positional_only, ["user_id", "payload"])
```

`chapter_22` وحدة مرافقة حقيقية في [أدوات الفصل 22 القابلة للاستيراد](chapter_22.py)، وليس اسمًا بديلًا. من `chapter-22-introspection/` شغّل `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`؛ يستورد الاختبار الوحدة، ويفحص المعاملات المسماة مقابل الموضعية فقط، ويثبت أن البحث الساكن لا ينفذ خاصية.

هذه زاوية اختبار حقيقية: لا تختبر المخرجات وحدها، بل تختبر أيضًا أن نظامك يرفض مبكرًا «شكل» الدالة غير الصحيح مع رسالة واضحة.

---

## تمارين موجّهة مع TODO وتلميحات

### 22-1 · تقرير الأنواع، سهل
اكتب دالة تعيد قائمة نصوص تصف نوع كل قيمة.

```python todo
def report_types(values):
    # TODO: return something like:
    # ["'hi' -> str", "3 -> int", "None -> NoneType"]
    pass
```

*تلميح*: استخدم `type(x).__name__` و`repr(x)`.

---

### 22-2 · مستدعي طريقة آمن، متوسط
اكتب دالة تستدعي طريقة **فقط إذا كانت موجودة وقابلة للاستدعاء**.

```python todo
def call_method(obj, method_name, *args, **kwargs):
    # TODO 1: fetch attribute with getattr(obj, method_name, None)
    # TODO 2: if not callable, raise TypeError with a friendly message
    # TODO 3: call and return the result
    pass
```

*تلميح*: `callable(attr)` صديقك.

---

### 22-3 · نسخة أفضل من `describe(value)`، متوسط فأعلى
طوّر `describe(value)` لتضمين:
- `has_len` و`len`، وقد نُفّذا في الأعلى.
- `has_items` و`first_item` إذا كانت القيمة قابلة للفهرسة.

```python todo
def describe2(value):
    # TODO: start from describe(value)
    # TODO: if value supports indexing, store first_item safely
    pass
```

*تلميح*: قد يؤدي الوصول إلى `value[0]` إلى `TypeError` أو `IndexError`. التقط كليهما.

---

### 22-4 · التحقق من callbacks، متقدم وإضافي
نفّذ `require_named_params(fn, required_names)` باستخدام `inspect.signature`.
أضف اختبارات للحالات التالية:
- المسار الناجح.
- دالة فيها `**kwargs`.
- معاملات ناقصة تؤدي إلى `TypeError`.

*تلميح*: راجع القسم الإضافي وانسخ الفكرة، ثم اختبرها.

---

## أخطاء شائعة وكيف تتفاداها
- **استخدام `type(x) == SomeType` في كل مكان**: فضّل `isinstance(x, SomeType)` لأنه أكثر مرونة.
- **نسيان `()`**: التعبير `text.upper` طريقة، أما `text.upper()` فهو النتيجة.
- **استدعاء `dir()` والشعور بالإرباك**: رشّح القائمة وابحث عن كلمة.
- **استخدام `getattr(obj, "x")` بلا قيمة افتراضية**: يؤدي غياب السمة إلى `AttributeError`.
- **افتراض أن `vars(obj)` تعمل دائمًا**: لا تعمل مع كثير من الأنواع المضمّنة، وهذا طبيعي.
- **افتراض أن البحث خامل**: قد تنفذ الخصائص وdescriptors و`__dir__` وغيرها من hooks شيفرة؛ استخدم `inspect.getattr_static` حين تحتاج تعريف السمة الساكن فقط.
- **الإفراط في الاستبطان**: يفيد الاستبطان في التعلّم والتشخيص، لكن تصميم واجهات واضحة أفضل في الشيفرة الحقيقية.

---

## حلول مشروحة قصيرة وواضحة

### حل 22-1
```python runnable
def report_types(values):
    result = []
    for v in values:
        result.append(f"{repr(v)} -> {type(v).__name__}")
    return result
```

### حل 22-2
```python runnable
def call_method(obj, method_name, *args, **kwargs):
    attr = getattr(obj, method_name, None)
    if not callable(attr):
        raise TypeError(f"{type(obj).__name__} has no callable '{method_name}'")
    return attr(*args, **kwargs)
```

### حل 22-3
```python runnable
def describe2(value):
    info = describe(value)
    try:
        info["first_item"] = value[0]
        info["has_items"] = True
    except (TypeError, IndexError, KeyError):
        info["first_item"] = None
        info["has_items"] = False
    return info
```

### حل 22-4، الجزء الأساسي
```python runnable
import inspect

def require_named_params(fn, required_names):
    sig = inspect.signature(fn)
    probe = {name: object() for name in required_names}
    try:
        sig.bind(**probe)
    except TypeError as exc:
        raise TypeError(
            f"{fn.__name__} must accept these named arguments: {', '.join(required_names)}"
        ) from exc
```

---

## نقطة تحقق ومعايير تقييم
- **الصحة**: تطابق النتيجة عقد الوحدة.
- **الوضوح**: تُفهم الأسماء والمسؤوليات من القراءة الأولى.
- **الأخطاء**: الادعاءات دفاعية ولا تعد بالأمان من الكائنات العدائية أو الخصائص أو descriptors.
- **التحقق**: اختبر القوائم والتسلسلات الفارغة والقواميس والكائنات القابلة للاستدعاء وcallbacks ذات المعاملات الموضعية فقط وخاصية ذات hook ملحوظ.
- **الشرح**: تستطيع تبرير القرارات ومخاطرها.

## تأمل ختامي
تعلّمت اليوم كيف «تسأل Python أسئلة» عن القيم: ما هي، وماذا تستطيع أن تفعل، وكيف تستخدمها بأمان. وهذه قدرة كبيرة في التشخيص وتعلّم المكتبات الجديدة.

في المرة القادمة التي ترى فيها خطأ مثل «الكائن لا يملك السمة…»، لا تقلق. استخدم `type()` و`dir()` و`help()` و`getattr()` مثل محقق هادئ. أنت قادر على ذلك.

</div>
