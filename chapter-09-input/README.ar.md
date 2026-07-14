<div dir="rtl">

# الفصل 9 · إدخال المستخدم والتحقق الآمن

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
ستتعلم جمع البيانات من الطرفية باستخدام `input()`، ومن معاملات سطر الأوامر، ومن ملفات بسيطة، مع التحقق من القيم وتحويلها دائماً قبل استخدامها. وسترى أمثلة على «استمارات حوارية» وأدوات صغيرة لوحدة التحكم تحاكي مسارات شائعة في الواجهات الخلفية.

## مسار التعلم
1. **النموذج الذهني**: يبدأ كل إدخال كسلسلة نصية، وأنت تقرر كيفية تحويله.
2. **`input()` التفاعلية**: قراءات أساسية وأسئلة متتابعة.
3. **التحويل والتحقق**: `int()` و`float()` و`str.strip()` ومعالجة `ValueError`.
4. **القيم الافتراضية وإعادة المحاولة**: التكرار حتى تتلقى قيمة صالحة.
5. **معاملات سطر الأوامر**: `sys.argv` ومقدمة قصيرة إلى `argparse`.
6. **قراءة ملفات بسيطة**: الفتح والقراءة والتحقق من الوجود.
7. **اختبارات وتمارين موجّهة**.

## أهداف التعلم
- جمع الإدخال من وحدة التحكم وتحويله إلى النوع الصحيح.
- التحقق من البيانات قبل استخدامها وعرض رسائل مفيدة عند فشلها.
- تنفيذ إعادات محاولة آمنة بحدود واضحة.
- قراءة معاملات سطر الأوامر والملفات الأساسية باستخدام المكتبة القياسية.
- كتابة اختبارات لدوال «خالصة» لا تعتمد على وحدة التحكم.

## المتطلبات السابقة والمسارات
- **المتطلب السابق:** أكمل checkpoint [الفصل 8](../chapter-08-conditionals/README.ar.md). يستخدم المسار الأساسي النصوص والتحويلات والشروط.
- **المسار الأساسي · 40–55 دقيقة:** ادرس القسم 1، والقسم الأساسي والتمرين 9-0 أدناه، ثم القسم 3. النتيجة: تطبيع النص والتحقق من الأرقام وتحويل عدد صحيح والتعافي من إدخال غير صالح بشروط مباشرة. لا يتطلب استثناءات ولا حلقات ولا دوالاً ولا pytest.
- **المسار المتوسط · 30–40 دقيقة:** إعادات المحاولة المحدودة في القسم 4. وهي **معاينة اختيارية** لـ[الحلقات](../chapter-10-loops/README.ar.md) و[الدوال](../chapter-11-functions/README.ar.md) و[الاستثناءات](../chapter-14-exceptions/README.ar.md)؛ انسخ الدوال المساعدة الكاملة أو تجاوزها.
- **المسار الاحترافي الاختياري · 45–60 دقيقة:** CLI والملفات وCSV والاختبارات. يستبق [الملفات](../chapter-13-files/README.ar.md) و[pytest](../chapter-18-testing/README.ar.md). لا يلزم منه شيء لـcheckpoint الأساسي.

## لماذا يهم هذا؟
تتلقى البرامج الحقيقية البيانات من المستخدمين أو الأنظمة الأخرى. إذا وثقت بالإدخال بلا تحقق، فستحصل على أخطاء، وربما ثغرات أمنية. يهيئك تعلم قراءة الإدخال والتحقق منه لاستمارات الويب وسكربتات الأتمتة وأدوات سطر الأوامر الاحترافية.

### مغامرة صغيرة
تخيّل أن برنامجك روبوت ودود. إذا تحدثت إليه بعبارات غريبة فسيرتبك. التحقق هو تعليم الروبوت أن يقول: «لم أفهم، هل يمكنك إعادة ذلك بطريقة مختلفة؟»

## توقّع قبل قراءة الإدخال
إذا كتب شخص `14`، فتوقّع القيمة والنوع اللذين تعيدهما `input()`، ثم القيمة والنوع بعد `int()`. وتوقّع ما يحدث مع `fourteen`؛ شغّل مثال التحويل وحدد رسالة التعافي بدل التخمين.

---

## 1. النموذج الذهني: يصل كل شيء كنص
تعيد `input()` دائماً سلسلة نصية. وأنت تقرر هل تحولها إلى عدد أو تاريخ أم تقارنها كنص.

```python illustrative
name = input("What's your name? ")
print(f"Hello, {name}")
```

- تساعد رسالة الطلب المستخدم.
- احذف المسافات الزائدة باستخدام `.strip()` عندما تحتاج إلى الاتساق.

---

## 2. التحويل ومعالجة الأخطاء

### 9-0 · تحويل أساسي بلا استثناءات

ابدأ بنص ثابت كي يعمل المثال دون تفاعل. استبدله بـ`input("Age: ")` عند التدريب التفاعلي فقط:

```python runnable
raw_age = "14".strip()

if raw_age.isdigit():
    age = int(raw_age)
    print(age)
else:
    print("Age must contain digits only")
```

راقب الآن فرع التعافي مع نص غير صالح؛ يبقى البرنامج مسيطراً بدلاً من الانهيار:

```python runnable
raw_age = "fourteen".strip()

if raw_age.isdigit():
    age = int(raw_age)
    print(age)
else:
    print("Age must contain digits only")
```

شغّل الكتلتين وسجل القيمة والنوع قبل التحويل وبعده. المساعد التالي الذي يستخدم `try`/`except` معاينة اختيارية لـ[الاستثناءات](../chapter-14-exceptions/README.ar.md).

```python illustrative
raw_age = input("Age: ")
try:
    age = int(raw_age)
except ValueError:
    print("Age must be an integer.")
    age = None
```

- التقط `ValueError` لتشرح ما حدث خطأ.
- يمكنك تغليف هذا المنطق في دوال قابلة لإعادة الاستخدام.

### دالة مساعدة قابلة لإعادة الاستخدام
```python illustrative
def ask_int(prompt, attempts=3):
    for _ in range(attempts):
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Please enter an integer.")
    raise RuntimeError("Too many attempts")
```

---

## 3. القيم الافتراضية

```python illustrative
city = input("City (default Barcelona): ").strip() or "Barcelona"
print(city)
```

- يستخدم التعبير `value or "default"` القيمة الافتراضية عندما تكون السلسلة فارغة.

---

## 4. إعادة المحاولة مع تحقق مركب

```python illustrative
def ask_email():
    while True:
        email = input("Email: ").strip().lower()
        if "@" in email and "." in email:
            return email
        print("Invalid format. Try again.")
```

- استخدم `while True` مع `return` عندما تحتاج إلى التكرار حتى يصبح التنسيق صالحاً.
- أضف في السكربتات الأطول مسار خروج واضحاً، مثل حد أقصى لعدد المحاولات.

---

## 5. معاملات سطر الأوامر

```python illustrative
# cli_args.py
import sys

if len(sys.argv) < 2:
    print("Usage: python cli_args.py <file>")
    sys.exit(1)

path = sys.argv[1]
print(f"Processing {path}")
```

### مثال قصير على `argparse`
```python illustrative
import argparse

parser = argparse.ArgumentParser(description="Calculator")
parser.add_argument("operation", choices=["add", "subtract"])
parser.add_argument("a", type=int)
parser.add_argument("b", type=int)
args = parser.parse_args()

if args.operation == "add":
    print(args.a + args.b)
else:
    print(args.a - args.b)
```

- تتحقق `argparse` من المدخلات وتولّد المساعدة تلقائياً.

---

## 6. قراءة ملف بسيط

```python illustrative
from pathlib import Path

path = Path("data.txt")
if not path.exists():
    raise FileNotFoundError("data.txt not found")

content = path.read_text(encoding="utf-8")
print(content)
```

- استخدم `Path` للتعامل المحمول مع المسارات.
- التقط `FileNotFoundError` لعرض رسالة واضحة.

---

## 7. اختبار الدوال الخالصة
بدلاً من اختبار `input()` مباشرة، غلّف المنطق ومرر البيانات كمعاملات. وبذلك يمكنك استخدام `pytest` من دون الاعتماد على وحدة التحكم.

```python runnable
# forms.py
def normalize_name(name):
    clean = name.strip().title()
    if not clean:
        raise ValueError("Name cannot be empty")
    return clean
```

```python illustrative
# tests/test_forms.py
import pytest
from forms import normalize_name

def test_normalize_name_ok():
    assert normalize_name("  noor ") == "Noor"

def test_normalize_name_rejects_empty():
    with pytest.raises(ValueError):
        normalize_name("   ")
```

---

## تمارين موجّهة (مع مهام TODO)
1. **9-1 · تسجيل سريع**
   ```python todo
   # TODO 1: ask for first name and last name, combine them with title()
   # TODO 2: validate that neither is empty
   # TODO 3: print a welcome message with defaults if something is missing
   ```
   *تلميح*: استخدم `.strip()` و`or "Guest"`.

2. **9-2 · أداة ملاحظات لسطر الأوامر**
   ```python todo
   # TODO 1: use argparse to accept --title and --message
   # TODO 2: derive a confined path with safe_note_path(title)
   # TODO 3: write with UTF-8 and refuse to overwrite an existing note
   ```
   *تلميح*: استخدم `parser.add_argument("--title", required=True)`.

   استخدم هذه الدالة المساعدة كي لا يستطيع العنوان حقن `/` أو`\\` أو`..` في مسار الناتج:
   ```python illustrative
   from pathlib import Path

   def safe_note_path(title, root=Path("notes")):
       safe_stem = "".join(
           char for char in title.strip()
           if char.isalnum() or char in ("-", "_")
       )
       if not safe_stem:
           raise ValueError("title must contain a letter or number")
       root.mkdir(parents=True, exist_ok=True)
       path = root / f"{safe_stem}.txt"
       if path.exists():
           raise FileExistsError(f"refusing to overwrite {path}")
       return path
   ```

3. **9-3 · استيراد ملف CSV بسيط**
   ```python todo
   import csv
   # TODO 1: ask for a CSV path using input()
   # TODO 2: open with newline="" and encoding="utf-8"
   # TODO 3: count valid rows with csv.reader
   ```
   *تلميح*: مرر الملف المفتوح إلى `csv.reader`؛ فهي تتعامل مع الفواصل داخل الاقتباسات بخلاف `split(",")`.

---

## أخطاء شائعة
- الثقة العمياء بتنسيق الإدخال ← التقط `ValueError` وتحقق صراحة.
- عدم حذف المسافات البيضاء ← تفشل مقارنة سلاسل تبدو «متطابقة».
- نسيان `sys.exit(1)` في أدوات سطر الأوامر عند غياب المعاملات ← يواصل البرنامج العمل في حالة غير سليمة.
- قراءة الملفات من دون التحقق من وجودها ← يؤدي إلى `FileNotFoundError` غير متوقع.
- اشتقاق المسار مباشرة من العنوان ← قد يسمح باجتياز المسار أو الاستبدال العرضي؛ احصر اسم الملف ونظفه أولًا.
- تحليل CSV باستخدام `split(",")` ← تصبح الفواصل المقتبسة أعمدة زائفة؛ استخدم وحدة `csv`.

---

## حلول مشروحة
1. **التسجيل السريع**: نظف كل `input()` وتحقق باستخدام `if not value:`؛ وتمنع القيم الافتراضية (`"Guest"`) انقطاع التدفق.
2. **أداة الملاحظات**: تفرض `argparse` وجود `--title` و`--message`؛ وتحصر `safe_note_path` الاسم داخل `notes/`، وترفض عنوانًا فارغًا بعد التنظيف، وتمنع الاستبدال قبل `path.write_text(args.message, encoding="utf-8")`.
3. **استيراد CSV**: تمنع `Path(path).exists()` غياب الملف؛ وتحافظ `csv.reader` على الحقول المقتبسة، ولا يزيد العداد إلا للصفوف ذات عدد الأعمدة المتوقع.

---

## Checkpoint وتقييم ذاتي
استخدم نصوصاً ثابتة خيالية لمحاكاة الاسم والعمر. توقع نوعيهما، وطبّع الاسم، وتحقق من العمر بـ`.isdigit()`، ولا تحوّله إلا داخل الفرع الصالح. شغّل مرة بأرقام ومرة بنص غير رقمي؛ يجب أن تطبع الثانية رسالة تعافٍ دون انهيار. لا تستخدم حلقة ولا دالة ولا استثناء ولا إطار اختبار.

امنح نقطة لكل معيار: **الصحة** (يتحول النص الصالح إلى العدد المتوقع)، و**التطبيع** (تحذف المسافات الخارجية)، و**الحد** (يذهب الفارغ وغير الرقمي إلى الفرع غير الصالح)، و**التعافي** (توضح الرسالة التنسيق)، و**الدليل** (تسجل الأنواع المتوقعة والمخرجات). تعني 4/5 أنك تستطيع المتابعة؛ وإلا فأعد 9-0. تنتمي إعادة المحاولة والاستثناءات وCLI/الملفات وpytest إلى المسارات اللاحقة.

---

## الخلاصة
تعلّمت أنماطاً لقراءة البيانات من وحدة التحكم ومعاملات سطر الأوامر والملفات، مع التحويل الآمن والتحقق في كل خطوة. ويمكنك الآن بناء مساعدين تفاعليين وسكربتات لسطر الأوامر من دون الخوف من الإدخال الفوضوي.

## تأمل ختامي
يعتمد كل تفاعل مع الأشخاص أو الأنظمة على إدخال موثوق. وباستخدام هذه التقنيات يمكنك إرشاد المستخدمين وتوقع الأخطاء والاستجابة برسائل واضحة. سنطبق هذه المدخلات في الفصل التالي داخل الحلقات، ونبدأ بناء حدس عن تكلفة الأداء.

</div>
