<div dir="rtl">

# الفصل 14 · الاستثناءات: من المبتدئ إلى البطل

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
ستتقن نظام الاستثناءات في بايثون: اكتشاف الأخطاء، ومعالجتها باستخدام `try/except`، وإطلاق استثناءاتك الخاصة، وإنشاء أصناف مخصصة، وتصميم واجهات API متينة تشرح بوضوح ما حدث خطأ. وسنتدرب على أنماط احترافية للتحقق من الإدخال وتغليف الاستدعاءات الخطرة وتنظيف الموارد.

## مسار التعلم
1. **النموذج الذهني**: تقطع الاستثناءات التدفق الطبيعي.
2. **`try/except` الأساسية**: التقاط الأخطاء المعروفة.
3. **`else` و`finally`**: الكتل الداعمة.
4. **`raise`**: إطلاق أخطائك الخاصة.
5. **الاستثناءات المخصصة**: `class` يرث من `Exception`.
6. **تسلسل الاستثناءات (`raise ... from ...`)**.
7. **مديرو السياق والتنظيف**.
8. **اختبارات وتمارين**.

## أهداف التعلم
- تحديد الاستثناءات المحتملة والتقاطها انتقائياً.
- استخدام `else` و`finally` لضبط التدفقات الجانبية والتنظيف.
- إنشاء استثناءات مخصصة وإطلاقها لوصف أخطاء المجال.
- تسلسل الاستثناءات للاحتفاظ بالسياق الأصلي.
- اختبار الدوال التي يجب أن تطلق الأخطاء أو تعالجها.

## لماذا يهم هذا؟
يؤدي تجاهل الاستثناءات إلى إخفاقات صامتة أو رسائل غامضة. تمنح معالجة الأخطاء الجيدة واجهة API لديك موثوقية، وتجعل تصحيح أخطاء الإنتاج أسهل بكثير.

### مغامرة صغيرة
تشبه الاستثناءات إشارات الطريق والوسائد الهوائية: ليست موجودة لإزعاجك، بل لتحذيرك وحمايتك عندما يحدث خطأ. إذا تعلمت قراءتها والاستجابة لها، أصبح برنامجك أكثر أماناً بكثير.

## المتطلبات المسبقة
الفصول السابقة الموصى بها: 8, 11, 12, 13.
استخدم CPython 3.11+ في بيئة محلية مؤقتة, وأبقِ البيانات والأسرار والخدمات بعيدًا عن الأنظمة الحقيقية.

---

## 1. `try/except` من الصفر

```python runnable
try:
    result = int("abc")
    print(result)
except ValueError:
    print("That was not a valid number")
```

- لا تعمل كتلة `except` إلا إذا وقع `ValueError`.
- يلتقط `except:` المجرد حتى `KeyboardInterrupt` و`SystemExit`؛ فتجنبه. ويلتقط `except Exception:` أخطاء تطبيق كثيرة، لذلك استخدمه عند حد مقصود وفضّل استثناءً محددًا.

### التقاط عدة استثناءات
```python runnable
import json

try:
    with open("config.txt", encoding="utf-8") as file:
        data = json.load(file)
except FileNotFoundError as exc:
    print("Missing file", exc)
except json.JSONDecodeError as exc:
    print("Invalid JSON", exc)
```

---

## 2. `else` و`finally`

```python runnable
def read_config():
    # Simple example: in real life you would read from a file/JSON
    return {"debug": True}

try:
    data = read_config()
except (FileNotFoundError, ValueError):
    data = {}
else:
    print("Config loaded successfully")
finally:
    print("End of process")
```

- لا تعمل `else` إلا إذا لم يقع استثناء.
- تعمل `finally` دائماً، وهي مثالية لإغلاق الاتصالات وتحرير الموارد.

---

## 3. إطلاق استثناءاتك الخاصة (`raise`)

```python runnable
def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Denominator cannot be zero")
    return a / b
```

- توقف `raise` الدالة وتنشر الخطأ.
- فضّل الاستثناءات القياسية عندما تصف المشكلة جيداً، مثل `ValueError` و`TypeError`.

### استخدام `raise` من دون معاملات
```python illustrative
try:
    divide(10, 0)
except ZeroDivisionError:
    raise  # re-raise the same exception
```

---

## 4. الاستثناءات المخصصة

```python runnable
class ConfigError(Exception):
    """Errors related to configuration."""

class MissingConfig(ConfigError):
    pass
```

```python runnable
def load_config(path):
    if not path.exists():
        raise MissingConfig(f"Missing {path}")
    # ...
```

- يتيح لك الإرث من `Exception`، أو من صنف فرعي مناسب، تمييز أخطاء مجالك.
- أبقِ التسلسلات الهرمية صغيرة ووصفية.

---

## 5. التسلسل (`raise ... from ...`)

```python illustrative
import json

class ConfigDecodeError(ConfigError):
    pass

try:
    config = json.loads(raw)
except json.JSONDecodeError as exc:
    raise ConfigDecodeError("Invalid config") from exc
```

- يحتفظ `from exc` بالتتبّع الأصلي، مما يسهّل تصحيح الأخطاء.

---

## 6. مديرو السياق والتنظيف

```python runnable
class TemporaryFile:
    def __enter__(self):
        self.fh = open("temp.txt", "w")
        return self.fh

    def __exit__(self, exc_type, exc, tb):
        self.fh.close()
        if exc_type:
            print("An error occurred", exc)
            return False  # Propagate the exception
```

- يضمن مديرو السياق المخصصون التنظيف حتى إذا وقع خطأ داخل `with`.

---

## 7. اختبار الاستثناءات

```python illustrative
import pytest

def test_divide_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

- تؤكد `pytest.raises` إطلاق الاستثناء الصحيح.
- استخدم `match="text"` للتحقق من رسالة الخطأ.

---

## تمارين موجّهة (مع مهام TODO)
1. **14-1 · أداة تحقق متينة**
   ```python todo
   def validate_payload(data):
       # TODO 1: raise ValueError if "email" is missing
       # TODO 2: use try/except to normalize type errors
   ```
   *تلميح*: استخدم `if "email" not in data: raise ValueError(...)`.

2. **14-2 · أداة سطر أوامر قادرة على التعافي**
   ```python todo
   # TODO 1: process files, catch FileNotFoundError and show a friendly message
   # TODO 2: use `sys.exit(1)` when it’s critical
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

3. **14-3 · استثناء مخصص**
   ```python todo
   class InsufficientFunds(Exception):
       pass
   # TODO 1: implement withdraw(amount) that raises InsufficientFunds
   # TODO 2: handle the exception and print the remaining balance
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

---

## أخطاء شائعة
- التقاط استثناءات عامة أكثر من اللازم وإخفاء المشكلة الحقيقية.
- عدم إعادة الإطلاق (`raise`) عندما لا تستطيع حل الخطأ.
- تجاهل `finally` وترك الموارد مفتوحة.
- إطلاق استثناءات برسائل غامضة؛ أدرج السياق دائماً.

---

## حلول مشروحة
1. **أداة التحقق المتينة**: استخدم `try: email = data["email"]` ثم `except KeyError as exc: raise ValueError("Missing email") from exc`. تسهّل الرسائل الواضحة تصحيح الأخطاء.
2. **أداة سطر الأوامر القادرة على التعافي**: تطبع `try/except FileNotFoundError` اسم الملف الذي فشل، وتخرج بالرمز 1 كي تتمكن السكربتات الأخرى من اكتشافه.
3. **الاستثناء المخصص**: تتحقق `withdraw` من الرصيد وتطلق `InsufficientFunds`؛ وتخبر `try/except` في المستوى الأعلى المستخدم من دون إغراقه بتتبّع خام.

---

## الخلاصة
يساعدك فهم الاستثناءات والتحكم فيها على كتابة شيفرة متينة: تختار ما تعالجه وما تنشره وكيف توصل المشكلات. وتضيف الاستثناءات المخصصة معنى إلى واجهات API.

## نقطة تحقق ومعايير تقييم
- **الصحة**: تطابق النتيجة عقد الوحدة.
- **الوضوح**: تُفهم الأسماء والمسؤوليات من القراءة الأولى.
- **الأخطاء**: يُختبر مسار ناجح وحالة حدّية ومسار تعافٍ.
- **التحقق**: تعمل الأمثلة والتمارين في بيئة نظيفة.
- **الشرح**: تستطيع تبرير القرارات ومخاطرها.

## تأمل ختامي
أن تكون «بطلاً» في الاستثناءات يعني توقع الإخفاقات وتصميم رسائل واضحة وعدم الخوف من إطلاق الأخطاء عندما لا تتحقق القواعد. واصل التدريب في مشاريعك، وستلاحظ أن شيفرتك تصبح أوثق وأسهل صيانة.

</div>
