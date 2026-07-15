<div dir="rtl">

# الفصل 2 · المتغيرات وأنواع البيانات البسيطة

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟

سنبني في هذا الفصل مفردات Python الأساسية: سنفهم ما يحدث عند تشغيل `hello_world.py`، وننشئ المتغيرات ونعيد تسميتها، وننظف النصوص، ونعمل بالأعداد، ونكتب تعليقات مفيدة. وفي النهاية سنتعرّف باختصار إلى «Zen of Python»، وهي طريقة التفكير التي سترشدنا في بقية المساق.

## مسار التعلم

1. **نموذج ذهني للمفسّر**: من دونه يبدو كل شيء كالسحر.
2. **المتغيرات بوصفها ملصقات**: قبل معالجة البيانات نحتاج إلى تسميتها جيدًا.
3. **النصوص**: أكثر الأنواع شيوعًا، مع التنسيق والمسافات والأخطاء المعتادة.
4. **الأعداد**: العمليات وfloats والثوابت.
5. **الحقيقة والغياب والمقارنات**: لاحظ النتائج المنطقية، ومثّل غياب القيمة، وقارن أعداد float بسماحية صريحة.
6. **التعليقات وZen**: اجعل شيفرتك مفهومة.
7. **تمارين «جرّب بنفسك»** تتدرج في الصعوبة.

## أهداف التعلم

- شرح ما يفعله المفسّر خطوة خطوة عند تشغيل `hello_world.py`.
- تعريف المتغيرات وإعادة إسنادها وتسميتها وفق قواعد احترافية.
- معالجة النصوص —حالة الأحرف والمسافات والبادئات— والأعداد —`int` و`float`— بلا مفاجآت.
- استخدام `bool` ومعاملات المقارنة و`None` عن قصد، والتمييز بين مساواة القيم واختبار الهوية `is None`.
- ملاحظة سلوك floating point الثنائي واختيار سماحية تناسب المسألة بدل افتراض أن الحساب العشري دقيق.
- توثيق الشيفرة بتعليقات مفيدة واستيعاب مبادئ Zen of Python.

## المتطلبات السابقة والمسارات

- **المتطلب السابق:** أكمل checkpoint [الفصل 1](../chapter-01-introduction/README.ar.md) وتعلّم تشغيل ملف `.py`. لا يحتاج المسار الأساسي إلى معرفة الدوال أو الشروط أو الاستثناءات أو الاختبارات.
- **المسار الأساسي · 60–80 دقيقة:** الأقسام 1 و2.1 و3 و4 و5.1–5.5 و7–9، وجسر القيم البسيطة في 7.7، وcheckpoint الأخير. النتيجة: سكربت ملف شخصي صغير مع ملاحظات قابلة للرؤية عن الحقيقة والغياب ومقارنة float، من دون `if` أو `def` أو `try` أو `raise`. تنتهي عندما تطابق حالتا الاسم العادي والفارغ الناتج المحدد، ويطابق checkpoint القيم البسيطة ملاحظاته المنطقية الأربع، وتتعافى من الخطأين المتعمّدين؛ عندها يمكنك التوقف بأمان أو المتابعة إلى الفصل 3.
- **معاينة اختيارية لأجزاء النص · 20–30 دقيقة:** بعد checkpoint الأساسي شغّل المقاطع المعطاة في القسم 5.6، ولاحظ أن slicing لنص فارغ آمن وأن `find()` تعيد `-1` عند غياب المحدّد. تستخدم التحديات الإضافية مفاهيم لاحقة ولا تنتمي إلى هذا المسار؛ عد إليها بعد [الشروط](../chapter-08-conditionals/README.ar.md) و[الدوال](../chapter-11-functions/README.ar.md) و[الاستثناءات](../chapter-14-exceptions/README.ar.md).
- **معاينة احترافية اختيارية · 25–35 دقيقة:** القسمان 2.2–2.3. النتيجة: نسخ التحقق والاختبارات وفحصهما، أو تجاوزهما من دون تعطيل checkpoint. ادرس مفاهيمهما لاحقًا في الفصول 8 و11 و14 و18.

## لماذا يهم هذا؟

يخزّن كل برنامج بيانات ويحوّلها. يساعدك فهم طريقة قراءة Python للملف، ومكان «وجود» القيم، واختيار الأسماء الواضحة على تجنّب أخطاء خفية وتقليل وقت debugging، كما يجهزك لهياكل أكثر تعقيدًا مثل lists وdictionaries.

### مغامرة صغيرة

تخيّل كل متغير ملصقًا على صندوق: اليوم تلصقه على صندوق «الرسائل»، وغدًا تنقله إلى «النقاط». لا تضع Python القيمة داخل الملصق؛ الملصق يشير إلى القيمة فقط. عندما تفهم هذه الفكرة تبدأ بالتحكم في الشيفرة بدل مقاومتها.

## توقّع قبل التشغيل

اقرأ المثالين الأولين من دون تشغيلهما. توقّع عدد الأسطر التي يطبعها كل مثال وقيمة `message` بعد إعادة الإسناد. ثم شغّلهما واشرح أي فرق بين توقعك والناتج المشاهد.

---

## 1. ماذا يحدث عند تشغيل `hello_world.py`؟

```python runnable
# hello_world.py
print("Hello Python world!")
```

عند تنفيذ `python hello_world.py`:

1. تطلب الطرفية أو المحرر من مفسّر Python المحدد فتح المسار `hello_world.py`. اللاحقة `.py` اصطلاح مفيد، لكنها ليست ما يجعل الملف قابلًا للتنفيذ بواسطة Python.
2. يقرأ CPython المصدر ويحوّله إلى *bytecode* ثم ينفّذ التعليمات.
3. عندما يجد `print("…")` يرسل النص إلى standard output.
4. قد يستخدم المحرر *syntax highlighting* للتمييز بين الدوال مثل `print` والقيم النصية مثل `"Hello..."`. الألوان مساعدة بصرية فقط؛ تشغيل المفسّر هو ما يتحقق من صحة الصياغة.

### تجربة صغيرة

```python runnable
message = "Hello Python world!"
print(message)

message = "Hello Python Crash Course world!"
print(message)
```

النتيجة:

```text illustrative
Hello Python world!
Hello Python Crash Course world!
```

يربط المفسّر `message` بالنص الأول، ثم يحدّث الملصق ويطبع مرة أخرى. تحتفظ Python دائمًا بأحدث قيمة مسندة.

```python runnable
# multiple_messages.py
message = "Welcome to Python"
print(message)

message = "We keep learning variables"
print(message)

print(f"Último mensaje: {message}")
```

```python runnable
# variable_trace.py
step = 0
log = "Starting"

print(f"{step}: {log}")

step += 1
log = "Downloading dataset"
print(f"{step}: {log}")

step += 1
log = "Processing data"
print(f"{step}: {log}")
```

---

## 2. تسمية المتغيرات واستخدامها

القواعد الأساسية:

- استخدم الحروف والأرقام و`_`، ولا تبدأ برقم: `message_1` صحيح و`1_message` خطأ.
- لا تستخدم المسافات؛ افصل الكلمات بـ`_` مثل `greeting_message`.
- لا تستخدم الكلمات المحجوزة أو أسماء الدوال مثل `print` و`list`.
- اختر أسماء قصيرة لكنها وصفية: `name` أوضح من `n`، و`student_name` أوضح من `s_n`.
- تجنّب الخلط بين `l` الصغيرة و`O` الكبيرة وبين `1` و`0`.

> ملاحظة: استخدم الأحرف الصغيرة افتراضيًا. سنرى لاحقًا متى تناسب الأحرف الكبيرة الثوابت.

### 2.1 فحص نوع المتغير

تستنتج Python الأنواع، لكن يمكنك رؤيتها باستخدام `type()` أو التحقق من classes محددة بواسطة `isinstance()`.

```python runnable
username = "noor"
age = 28
temperature = 20.5

print(type(username))          # <class 'str'>
print(type(age))               # <class 'int'>
print(isinstance(age, int))    # True
print(isinstance(temperature, float))  # True
print(isinstance(age, (int, float)))   # True (it matches one of the types)
```

يمكن أن تقبل `isinstance` tuple من الأنواع. يفيد ذلك عندما تسمح بالأعداد الصحيحة والعشرية معًا، أو عندما تقبل الدالة عدة classes متوافقة.

### 2.2 التأكد من أن الدالة تستقبل البيانات الصحيحة

**معاينة اختيارية:** يجمع هذا القسم الدوال والشروط والاستثناءات قبل دروسها الكاملة. يكفي الآن أن تعرف أن `def` تسمّي إجراءً قابلًا لإعادة الاستخدام، و`if` تتحقق من قاعدة، و`raise` تتوقف بخطأ مسمّى. يمكنك نسخ المثال كاملًا أو الانتقال إلى القسم 3. تابع لاحقًا في [الشروط](../chapter-08-conditionals/README.ar.md) و[الدوال](../chapter-11-functions/README.ar.md) و[الاستثناءات](../chapter-14-exceptions/README.ar.md).

عند تصميم دالة، من الجيد أن تفشل مبكرًا إذا لم تطابق arguments توقعاتك. يتحقق هذا الإصدار من كون `base` و`altura` عددين قبل حساب المساحة:

```python runnable
def is_real_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def calcular_area_rectangulo(base, altura):
    if not is_real_number(base):
        raise TypeError("base must be numeric")
    if not is_real_number(altura):
        raise TypeError("height must be numeric")
    if base <= 0 or altura <= 0:
        raise ValueError("dimensions must be positive")

    return base * altura
```

يوضّح هذا النمط التوقعات وكيفية التعامل مع القيم غير الصالحة. رفض `bool` صراحة مهم لأن Python تتعامل مع `True` و`False` كصنفين فرعيين من الأعداد الصحيحة، لكنهما لا يمثلان أبعادًا ذات معنى هنا. ويمكن لاحقًا دعم العقد بـtype hints مثل `def calcular_area_rectangulo(base: float, altura: float) -> float:`.

### 2.3 اختبار الشروط المسبقة (اختبار صغير)

**معاينة اختيارية:** `pytest` أداة خارجية تُقدّم وتُثبّت في [فصل الاختبارات](../chapter-18-testing/README.ar.md). لا يحتاج إليها المسار الأساسي. إذا لم تكن مثبتة فاقرأ هذا المقطع أو تجاوزه، ولا تنزّل مثبّتًا غير ذي صلة.

تمنحك الاختبارات الصغيرة ثقة فورية. في `pytest` تكتب دوال تبدأ بـ`test_…` وتستدعي شيفرتك:

```python illustrative
# tests/test_rectangulos.py
import pytest
from area import calcular_area_rectangulo

def test_calcular_area_rectangulo_valores_validos():
    assert calcular_area_rectangulo(3, 4) == 12

def test_calcular_area_rectangulo_rechaza_strings():
    with pytest.raises(TypeError):
        calcular_area_rectangulo("10", 5)

def test_calcular_area_rectangulo_rechaza_negativos():
    with pytest.raises(ValueError):
        calcular_area_rectangulo(-1, 2)

def test_calcular_area_rectangulo_rechaza_booleanos():
    with pytest.raises(TypeError):
        calcular_area_rectangulo(True, 3)
```

تؤكد `pytest.raises` ظهور الاستثناء الصحيح. من دون `pytest` تجاوز هذه المعاينة؛ تشغيل ملف لا يفعل سوى تعريف الاختبارات لا ينفذها آليًا. الفكرة المهمة أن كل شرط مسبق يحتاج إلى مثال عادي وحدّي وغير صالح.

---

## 3. تجنّب `NameError` وفهم «الملصقات»

<!-- bookcheck: expect-error="NameError" -->
```python expected-error
message = "Hello Python Crash Course reader!"
print(mesage)  # typo
```

الناتج:

```text illustrative
Traceback (most recent call last):
  File "hello_world.py", line 2, in <module>
    print(mesage)
NameError: name 'mesage' is not defined. Did you mean: 'message'?
```

تعرض Python:

1. الملف والسطر الذي حدثت فيه المشكلة.
2. السطر الدقيق موضع الخطأ.
3. إشارة الخطأ الثابتة `NameError` والاسم غير المعروف `mesage`. قد يختلف النص الدقيق والاقتراح بين إصدارات Python.

هذا **خطأ متوقع** وليس مثال نجاح قابلًا للتشغيل. للتعافي اجعل الاسم عند الاستخدام مطابقًا للاسم عند الإسناد، ثم شغّل مرة أخرى:

```python runnable
message = "Hello Python Crash Course reader!"
print(message)
```

```text output
Hello Python Crash Course reader!
```

إذا تكرر الخطأ الإملائي نفسه عند التعريف والاستخدام:

```python runnable
mesage = "Hello..."
print(mesage)
```

يعمل البرنامج لأن الملصقين متطابقان. الخلاصة: فكّر في المتغيرات على أنها **ملصقات** تشير إلى القيم وليست صناديق. يشترط المفسّر تطابق الاسم *حرفيًا*.

---

## 4. جرّب بنفسك (المتغيرات الأساسية)

- **2-1 · رسالة بسيطة**: في `simple_message.py` أسند رسالة إلى متغير واطبعها.
- **2-2 · رسائل بسيطة**: في `simple_messages.py` اطبع رسالة، ثم غيّر المتغير واطبع مرة أخرى.

---

## 5. النصوص

### 5.1 تغيير حالة الأحرف

```python runnable
name = "noor lovelace"
print(name.title())
print(name.upper())
print(name.lower())
```

تجعل `title()` أول حرف في كل كلمة كبيرًا، وتساعد `upper()` و`lower()` على توحيد input المستخدم.

### 5.2 المتغيرات داخل النصوص (f-strings)

```python runnable
first_name = "noor"
last_name = "lovelace"
full_name = f"{first_name} {last_name}"
print(f"Hello, {full_name.title()}!")
message = f"Hello, {full_name.title()}!"
print(message)
```

ضع `f` قبل النص، وأحط المتغيرات بـ`{}`.

### 5.3 Tabs والأسطر الجديدة

```python runnable
print("Python")
print("\tPython")
print("Languages:\nPython\nC\nJavaScript")
print("Languages:\n\tPython\n\tC\n\tJavaScript")
```

### 5.4 إزالة المسافات الزائدة

```python runnable
favorite_language = "python "
print(favorite_language.rstrip())   # temporary
favorite_language = favorite_language.rstrip()  # permanent

favorite_language = " python "
print(favorite_language.rstrip())
print(favorite_language.lstrip())
print(favorite_language.strip())
```

```python runnable
# username_cleaner.py
raw_username = "  \tTaha\n"
clean_username = raw_username.strip()
print(f"Raw username: [{raw_username}]")
print(f"Clean username: [{clean_username}]")
```

تُظهر الأقواس المربعة المسافات المحيطة. يحتاج تقرير صلاحية الاسم الفارغ إلى شرط، لذلك نؤجل هذا القرار إلى [الفصل 8](../chapter-08-conditionals/README.ar.md)؛ يلاحظ المسار الأساسي القيمة المنظفة فقط.

### 5.5 إزالة البادئات واللواحق

```python runnable
nostarch_url = "https://nostarch.com"
print(nostarch_url.removeprefix("https://"))

filename = "python_notes.txt"
print(filename.removesuffix(".txt"))
```

### 5.6 أجزاء النص (slicing): اقطع النص بأمان

النص في Python **sequence** من الأحرف، لذلك تستطيع:

- أخذ حرف واحد بواسطة **index** مثل `text[0]`؛
- أخذ **جزء نصي** بواسطة `text[start:end]`.

تخيّل أنك تقطع شطيرة: `start` هو موضع البداية و`end` هو موضع التوقف، لكن **`end` غير مشمول**.

#### 5.6.1 Indexing (حرف واحد)

```python runnable
word = "python"
print(word[0])   # p
print(word[-1])  # n (last character)
```

إذا خرج index عن المجال ترفع Python الخطأ `IndexError`.

#### 5.6.2 Slicing (جزء نصي)

```python runnable
word = "python"
print(word[0:2])   # 'py'  (0 and 1)
print(word[2:])    # 'thon' (from 2 to the end)
print(word[:3])    # 'pyt'  (from start to 2)
print(word[-3:])   # 'hon'  (last 3)
```

#### 5.6.3 Slicing مع steps (ممتع ومفيد)

```python runnable
word = "abcdefgh"
print(word[::2])   # 'aceg' (every 2nd char)
print(word[::-1])  # 'hgfedcba' (reversed)
```

#### 5.6.4 البحث عن أجزاء نصية بكفاءة

في الفحوص البسيطة لا تقطع النص يدويًا، بل استخدم الأداة المناسبة:

```python runnable
email = "noor@example.com"
print("@" in email)                 # True
print(email.startswith("noor"))     # True
print(email.endswith(".com"))       # True
print(email.find("@"))              # 3 (position) or -1 if not found
```

#### 5.6.5 بناء النصوص بكفاءة باستخدام `join`

عند بناء نص داخل loop، تجنّب تكرار `+` لأنه ينشئ نصوصًا مؤقتة كثيرة. اجمع الأجزاء ثم اربطها:

```python runnable
words = ["python", "is", "fun"]
sentence = " ".join(words)
print(sentence)  # python is fun
```

### تحديات إضافية (الأجزاء النصية)

هذه تمارين عملية قصيرة مناسبة لتثبيت slicing.

**تدريب اختياري لاحق:** تستخدم عناصر TODO هذه الدوال والشروط والاستثناءات. لا تنتمي إلى checkpoint الأساسي. تجاوزها الآن وعد إليها بعد الفصول 8 و11 و14؛ يمكنك إكمال الفصل من دونها.

1. **2-S1 · إخفاء جزء من البريد الإلكتروني**
   ```python todo
   def mask_email(email):
       # TODO: return something like:
       # "n***@example.com" for "noor@example.com"
       # Edge case: if there's no "@", raise ValueError
       pass
   ```
   *تلميح*: ابحث عن موضع `"@"` واقطع النص حوله.

2. **2-S2 · لاحقة الملف**
   ```python todo
   def extension(filename):
       # TODO: return "txt" for "notes.txt"
       # Edge case: no dot → return "" (empty string)
       pass
   ```
   *تلميح*: تعثر `rfind(".")` على آخر نقطة.

3. **2-S3 · فحص palindrome (تحدٍ ممتع)**
   ```python todo
   def is_palindrome(text):
       # TODO: ignore spaces and case
       # Example: "Anita lava la tina" -> True
       pass
   ```
   *تلميح*: استخدم `clean = text.replace(" ", "").lower()` ثم قارنه بـ`clean[::-1]`.

### أخطاء شائعة في الأجزاء النصية

- خطأ off-by-one: لا يتضمن `text[a:b]` الموضع `b`.
- سوء فهم `find()`: تعيد `-1` إذا لم تجد القيمة، ولا ترفع خطأ.
- نسيان الحالة الفارغة: slicing لنص فارغ آمن، لكن indexing ليس كذلك.

### 5.7 تجنّب `SyntaxError` في quotes

```python runnable
message = "One of Python's strengths is its diverse community."  # ✔
# message = 'One of Python's strengths...'  # ✘: the inner quote breaks the string
```

يعني `SyntaxError: unterminated string literal` غالبًا أن quotes غير متطابقة. راقب syntax highlighting؛ إذا لوّن المحرر النص العادي كشيفرة، افحص quotes من جديد.

---

## 6. جرّب بنفسك (النصوص)

- **2-3 · رسالة شخصية**: في `personal_message.py` استخدم متغير `name` واطبع تحية.
- **2-4 · حالات الاسم**: في `name_cases.py` اطبع الاسم بحروف صغيرة وكبيرة وtitle case.
- **2-5 · اقتباس مشهور**: في `famous_quote.py` اعرض الاقتباس بين علامتي تنصيص مع صاحبه.
- **2-6 · اقتباس مشهور 2**: في `famous_quote_2.py` استخدم `famous_person` و`message`.
- **2-7 · تنظيف الأسماء**: في `stripping_names.py` أضف `\t` و`\n` ثم استخدم `lstrip()` و`rstrip()` و`strip()`.
- **2-8 · لواحق الملفات**: في `file_extensions.py` استخدم `filename.removesuffix(".txt")`.

---

## 7. الأعداد

### 7.1 الأعداد الصحيحة (`int`)

```python runnable
print(2 + 3)
print(3 - 2)
print(2 * 3)
print(3 / 2)
print(3 ** 2)
print((2 + 3) * 4)
```

```python runnable
# score_tracker.py
initial_score = 0
bonus = 15
penalty = 3

score = initial_score + bonus - penalty
print(f"Final score: {score}")
```

### 7.2 الأعداد العشرية (`float`)

```python runnable
print(0.1 + 0.2)
print(3 * 0.1)
```

قد ترى `0.30000000000000004` لأن كثيرًا من الكسور العشرية لا يمكن تمثيلها بدقة في binary floating point. يحوّل القسم 7.7 هذه الملاحظة إلى مقارنة آمنة وصريحة.

### 7.3 مزج الأعداد الصحيحة والعشرية

```python runnable
print(4 / 2)      # 2.0
print(1 + 2.0)    # 3.0
print(3.0 ** 2)   # 9.0
```

إذا احتوت العملية على `float` فسيكون الناتج `float`.

```python runnable
# shipping_cost.py
package_weight_kg = 2
price_per_kg = 4.5
fuel_surcharge = 1.2  # Float factor

base_cost = package_weight_kg * price_per_kg
final_cost = base_cost * fuel_surcharge

print(f"Final cost: {final_cost:.2f} €")
```

### 7.4 Underscores في الأعداد الطويلة

```python runnable
universe_age = 14_000_000_000
print(universe_age)  # 14000000000
```

```python runnable
# budget_overview.py
quarter_budget = 2_500_000
spend_to_date = 1_875_430
remaining = quarter_budget - spend_to_date

print(f"Remaining budget: {remaining:,} €")
```

### 7.5 الإسناد المتعدد

```python runnable
x, y, z = 0, 0, 0
```

تأكد من أن عدد القيم يساوي عدد المتغيرات.

### 7.6 الثوابت

```python runnable
MAX_CONNECTIONS = 5000
```

المتعارف عليه كتابة اسم الثابت بحروف كبيرة للإشارة إلى أنه لا ينبغي أن يتغير.

### 7.7 الحقيقة والغياب والمقارنات وسماحية float

لدى Python نوع منطقي اسمه `bool` وله قيمتان حرفيتان: `True` و`False`. المقارنة تعبير ينتج إحدى هاتين القيمتين؛ ولا تحتاج إلى عبارة `if` لمجرد ملاحظة النتيجة.

توقّع الأسطر الستة قبل تشغيل هذا block:

```python runnable
print(3 < 5)
print(3 == 3)
print(3 != 5)
print(3 <= 3)
print(5 > 3)
print(5 >= 5)
```

كل سطر يطبع `True`. تعني المعاملات عدم المساواة (`!=`)، وأصغر/أكبر من (`<` و`>`)، والحدود الشاملة (`<=` و`>=`). تستخدم المساواة `==`، أما `=` الواحدة فتسند قيمة إلى اسم.

#### تعني `None` غيابًا صريحًا

`None` كائن خاص نستخدمه لنقول «لا توجد قيمة هنا». ليست العدد صفرًا ولا نصًا فارغًا ولا `False`. استخدم `is None` —أو `is not None`— لاختبار هذا sentinel:

```python runnable
missing_score = None
zero_score = 0
empty_label = ""

print(missing_score is None)
print(zero_score is None)
print(empty_label is None)
print(False is None)
```

الناتج هو `True` ثم ثلاث قيم `False`. سيستخدم [الفصل 8](../chapter-08-conditionals/README.ar.md) هذه النتائج المنطقية في القرارات. يكفي الآن أن تعرف أن `bool(0)` و`bool("")` و`bool(None)` كلها `False`، بينما `bool("0")` هي `True`؛ لكن *قيم الحقيقة* هذه لا تجعل القيم الأصلية قابلة للتبادل في معنى المجال. وبخاصة، تكون `False == 0` مساوية لـ`True` بسبب التوافق العددي في Python، مع أن إجابة منطقية وكمية عددية تعبّران عن معنيين مختلفين.

#### تحتاج المقارنات إلى معانٍ متوافقة

لا تحوّل Python هذا النص بصمت إلى عدد صحيح في مقارنة ترتيبية:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
print(3 < "5")
```

فئة الفشل المستقرة هي `TypeError`، وقد تختلف الرسالة الكاملة بين إصدارات Python. للتعافي، قرر معنى البيانات وقارن قيمتين من النوع نفسه:

```python runnable
print(3 < 5)
print("3" < "5")
```

كلتا الملاحظتين `True` لكن لسببين مختلفين: تستخدم الأعداد الصحيحة ترتيبًا عدديًا، وتستخدم النصوص ترتيبًا معجميًا. ينتظر التحويل المقصود لمدخلات غير موثوقة حتى [الفصل 9](../chapter-09-input/README.ar.md).

#### تستخدم مقارنة floating point سماحية مختارة

توقّع النتيجتين المنطقيتين:

```python runnable
calculated = 0.1 + 0.2
target = 0.3
tolerance = 0.000_000_001

print(calculated == target)
print(abs(calculated - target) <= tolerance)
```

النتيجة الأولى `False` والثانية `True` على مفسّر CPython المستخدم كدليل للمساق. تقيس `abs` المسافة من الهدف. السماحية قاعدة صريحة لهذا المثال الصغير وليست ثابتًا عالميًا؛ فالقياسات العلمية والهندسة والمال وغيرها من المجالات تحتاج إلى تمثيلات أو سياسات خطأ مختلفة.

**معاينة اختيارية — `math.isclose`:** تُدرّس imports قبل أول استخدام مطلوب لها في [الفصل 7](../chapter-07-queues/README.ar.md). هذه المعاينة الكاملة قابلة للتجاوز:

```python runnable
import math

print(math.isclose(0.1 + 0.2, 0.3, rel_tol=1e-9, abs_tol=0.0))
```

ما زالت `math.isclose` تجري مقارنة بسماحية؛ وليست حسابًا عشريًا دقيقًا. توجد أداة لاحقة أخرى اسمها `Decimal`، لكن استخدامها الصحيح يحتاج أيضًا إلى import وإنشاء حذر من نصوص، ولذلك ليست جزءًا من هذا checkpoint.

#### TODO موجّه للقيم البسيطة والتعافي والحل

```python todo
stored_score = None
calculated = 0.1 + 0.2
target = 0.3
tolerance = 0.000_000_001

# TODO 1: print whether stored_score is absent with `is None`.
# TODO 2: print whether 3 is less than 5.
# TODO 3: print the exact float equality result.
# TODO 4: print whether the absolute difference is within tolerance.
```

**تلميح:** كل TODO تعبير واحد داخل `print(...)`؛ لا تحتاج إلى `if` أو import أو function أو exception handler.

الحل المشروح:

```python runnable
stored_score = None
calculated = 0.1 + 0.2
target = 0.3
tolerance = 0.000_000_001

print(stored_score is None)
print(3 < 5)
print(calculated == target)
print(abs(calculated - target) <= tolerance)
```
```text output
True
True
False
True
```

يلاحظ السطر الأول الغياب، والثاني الترتيب العددي، ويكشف الثالث تمثيل floating point الثنائي، ويطبق الرابع قاعدة المجال المعلنة. لإكمال هذا الجسر، توقّع الأسطر الأربعة، ولاحظ `TypeError` الناتج عن نوعين غير متوافقين، وأصلحه باختيار نوع مشترك عن قصد، ثم أعد تشغيل الحل.

امنح نفسك نقطة لكل من **الناتج الصحيح**، و**استخدام `is None`**، و**التمييز بين المساواة والسماحية**، و**التعافي من `TypeError`**، و**شرح سبب ارتباط السماحية بالمجال**. تكمل نتيجة 5/5 جسر القيم البسيطة، وتبقى `math.isclose` اختيارية.

---

## 8. جرّب بنفسك (الأعداد)

- **2-9 · العدد ثمانية**: في `number_eight.py` اكتب أربع عمليات مختلفة نتيجتها 8.
- **2-10 · العدد المفضل**: في `favorite_number.py` خزّن عددك المفضل واطبع رسالة.
- **2-10b · تقرير الحقيقة**: أكمل TODO الموجّه في 7.7، ثم غيّر مقارنة متوافقة واحدة لتلاحظ `TypeError` الموثق وتتعافى منه.

---

## 9. التعليقات

```python runnable
# Say hello to everyone.
print("Hello Python people!")
```

تتجاهل Python كل ما يأتي بعد `#`. استخدم التعليقات لشرح القرارات والافتراضات والخطوات غير الواضحة. حذف تعليق زائد أسهل من إعادة بناء منطقك بعد أشهر.

### جرّب بنفسك: التعليقات

- **2-11 · إضافة تعليقات**: خذ برنامجين سابقين وأضف إلى كل منهما تعليقًا مفيدًا واحدًا على الأقل يشرح الاسم أوالتاريخ أوالهدف.

---

## 10. Zen of Python

يطبع `import this` تسعة عشر مبدأ كتبها Tim Peters. من أهمها:

- **الجميل أفضل من القبيح.** يمكن للشيفرة أن تكون أنيقة وينبغي لها ذلك.
- **البسيط أفضل من المعقد.** إذا نجحت النسخة البسيطة فاخترها.
- **المعقد أفضل من المربك.** عندما يكون الواقع معقدًا اختر أوضح حل.
- **سهولة القراءة مهمة.** سهّل على الآخرين متابعة تفكيرك.
- **ينبغي أن توجد طريقة واضحة واحدة، ويفضل واحدة فقط.** يصبح التعاون أسهل عندما تتقارب الحلول.
- **الآن أفضل من أبدًا.** لا تنتظر حتى «تعرف كل شيء» قبل أن تبني.

### جرّب بنفسك: Zen of Python

- **2-12 · Zen of Python**: نفّذ `import this` في الطرفية واختر جملة تريد تطبيقها هذا الأسبوع.

---

## حلول مشروحة مختارة

```python runnable
# trace_run.py
step = 1
print(f"{step}. Starting program")
step += 1
print(f"{step}. Working...")
step += 1
print(f"{step}. Finished")
# Reasoning: we use a variable to show execution order.
```

```python runnable
# profile.py
first_name = "Noor"
last_name = "Frej"
age = 14
full_name = f"{first_name} {last_name}"
print(full_name)
print(f"Next year you will be {age + 1}.")
# Reasoning: splitting pieces makes changes easier and lets you reuse data.
```

```python runnable
# time_math.py
days_per_week = 7        # Cambia a 5 si necesitas semana laboral
hours_per_day = 24
minutes_per_hour = 60
minutes_per_week = days_per_week * hours_per_day * minutes_per_hour
print(f"Minutos en la semana: {minutes_per_week}")
# Reasoning: comments explain "magic numbers".
```

---

## أخطاء شائعة

- حجب دوال built-in مثل `list = []`.
- جمع النصوص والأعداد من دون conversion.
- ترك spaces أوtabs زائدة تكسر مقارنة النصوص.
- الاعتماد على الذاكرة لمعنى الأعداد بدل كتابة comments.
- عدم تطابق quotes والتسبب في `SyntaxError`.
- معاملة `None` و`0` و`""` و`False` بوصفها قيمة المجال نفسها؛ استخدم `is None` حين يكون السؤال عن الغياب.
- مقارنة floats باستخدام `==` فقط، أو نسخ سماحية واحدة إلى كل مسألة من دون تعريف مقدار الخطأ المقبول.
- ترتيب معانٍ غير متوافقة مثل عدد صحيح ونص يبدو عدديًا بدل التحويل عند حد الإدخال.

---

## Checkpoint وتقييم ذاتي

أنشئ ملف `profile.py` واحدًا باستخدام الإسناد وطرق النص والحساب وf-strings و`print` فقط. توقّع أسطر الناتج الثلاثة قبل إكمال الأسطر الناقصة.

### TODO موجّه

```python todo
raw_name = "  Noor  "
age = 14

# TODO 1: create clean_name by removing surrounding whitespace from raw_name.
# TODO 2: create next_age by adding 1 to age.
# TODO 3: print "Profile: [Noor]" and "Next year: 15" with f-strings.

empty_raw_name = " \t\n "
# TODO 4: clean empty_raw_name and print "Empty profile: []".
```

**تلميح:** تعيد `strip()` نصًا جديدًا؛ أسند النتيجة إلى متغير جديد ذي اسم واضح. تستخدم الحالة الفارغة العملية نفسها التي تستخدمها الحالة العادية، ولا تحتاج إلى شرط.

يجب أن تحافظ الحالة العادية على `Noor` وتحسب `15`. الحالة الحدّية نص لا يحتوي إلا على مسافات؛ بعد `strip()` يجب أن يصبح فارغًا، لذلك يتلامس القوسان: `[]`.

### خطأ قابل للتعافي

بعد إكمال TODO غيّر مؤقتًا أحد استخدامات `clean_name` إلى `clean_nam`:

<!-- bookcheck: expect-error="NameError" -->
```python expected-error
raw_name = "  Noor  "
clean_name = raw_name.strip()
print(f"Profile: [{clean_nam}]")
```

يجب أن يتوقف التشغيل بإشارة `NameError` الثابتة وأن يحدد `clean_nam`. تعافَ بإعادة الحرف `e` الأخير؛ لا حاجة هنا إلى `try`/`except`. ثم استخدم هذا الحل المشروح:

### الحل المشروح

```python runnable
# profile.py
raw_name = "  Noor  "
age = 14

clean_name = raw_name.strip()
next_age = age + 1
print(f"Profile: [{clean_name}]")
print(f"Next year: {next_age}")

empty_raw_name = " \t\n "
empty_clean_name = empty_raw_name.strip()
print(f"Empty profile: [{empty_clean_name}]")
```

```text output
Profile: [Noor]
Next year: 15
Empty profile: []
```

تنتج `strip()` قيمة منظفة من دون تغيير `raw_name`، لذلك يجعل `clean_name` التحويل ظاهرًا. وينتج `age + 1` القيمة التالية من دون تغيير معنى `age`. تعمل عملية التنظيف نفسها عند الحد: يتحول النص المكوّن من مسافات فقط إلى `""`، وتجعل الأقواس المربعة النتيجة الفارغة قابلة للملاحظة.

### التحقق ومعايير التقييم

شغّل `python profile.py` بعد الإصلاح، وتحقق من أن الناتج يطابق الأسطر الثلاثة أعلاه تمامًا.

امنح نفسك نقطة لكل معيار:
- **الصحة:** تطبع حالتا الاسم العادي والفارغ الأسطر الثلاثة المحددة.
- **سهولة القراءة:** يصف كل اسم متغير القيمة قبل التنظيف أو بعده.
- **التعافي من الخطأ:** تحدد `clean_nam` وتستعيد `clean_name` وتحصل على تشغيل ناجح.
- **التحقق:** تقارن الأسطر الثلاثة المشاهدة بتوقعك.
- **الشرح:** تشرح بكلماتك لماذا تنتج `strip()` الرمز `[]` في الحالة الحدّية، ولماذا تزيل تسمية المتغير الصحيحة `NameError`.

يكتمل checkpoint الملف الشخصي عند 5/5. يحتاج المسار الأساسي أيضًا إلى 5/5 في جسر القيم البسيطة في القسم 7.7. لا يحتاج أي من checkpointين إلى شروط أو دوال أو معالجة استثناءات أو imports أو اختبارات.

---

## تأمل ختامي

أي توقع تغيّر بعد تشغيل الحالات العادية والحدّية والمُصلحة؟ اشرح لماذا تستطيع عبارة `strip()` نفسها تنظيف اسم ظاهر واسم مكوّن من مسافات فقط من دون `if`. ثم اشرح لماذا قد تؤدي `None` و`0` و`False` كلها إلى ملاحظات false-like مع أنها تمثل حقائق مختلفة.

تستطيع الآن شرح عمل المفسّر، واستخدام المتغيرات كملصقات، وتنسيق النصوص وتنظيف المسافات، وإجراء العمليات الحسابية، وتمثيل الغياب، وملاحظة المقارنات، ومقارنة floats تحت قاعدة صريحة، والتعافي من أخطاء الاسم والنوع. وتعرف أيضًا روح Zen of Python: اجعل الحل بسيطًا وقابلًا للقراءة. في **الفصل 3** سنخزّن مجموعات كاملة من البيانات باستخدام **lists** ونتعلم قراءتها وتعديلها وترتيبها. احتفظ بهذه الأمثلة قريبًا؛ سنستخدمها مجددًا.

</div>
