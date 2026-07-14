<div dir="rtl">

# الفصل 3 · مقدمة إلى القوائم

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
ستتعلم في هذا الفصل ماهية القائمة، وكيفية الوصول إلى كل عنصر فيها، وكيفية تغييرها وترتيبها وحماية شيفرتك من الأخطاء الشائعة. سنتدرّب على الدوال الأساسية (`append` و`insert` و`pop` و`remove` و`sort`)، وسنكتب اختبارات صغيرة تضمن أن دوالنا تتصرف كما نتوقع.

## مسار التعلم
1. **المقدمة**: نموذج ذهني للقائمة وسبب أهمية الأقواس المربعة (`[]`).
2. **الوصول والاستخدام**: الفهارس، واستخدام `-1` للوصول إلى النهاية، وإعادة استعمال القيم داخل الرسائل.
3. **التعديل والإضافة والحذف**: `append` و`insert` و`del` و`pop` و`remove`، ومتى تختار كل واحدة منها.
4. **التنظيم**: `sort` و`sorted` و`reverse` و`len`، مع فحوص سريعة.
5. **تجنب الأخطاء**: اكتشاف `IndexError` ومنعه.
6. **اختبارات وتمارين موجّهة** تجعل التعامل مع القوائم آمناً.

## أهداف التعلم
- تعريف القائمة والوصول إلى عناصرها حسب الموضع، بما في ذلك الفهارس السالبة.
- تعديل العناصر الموجودة وإضافة العناصر أو حذفها وفقاً لاحتياجات برنامجك.
- إعادة ترتيب القوائم مؤقتاً أو دائماً وقياس طولها.
- تجنب `IndexError` بالتحقق من الفهارس واستخدام `len()` و`-1` بصورة صحيحة.
- في المسار الاحترافي الاختياري، كتابة اختبارات صغيرة تؤكد أن دوال القوائم لا تُحدث آثاراً جانبية غير مرغوبة.

## المتطلبات السابقة والمسارات
- **المتطلب السابق:** أكمل checkpoint [الفصل 2](../chapter-02-variables/README.ar.md). يستخدم المسار الأساسي المتغيرات والنصوص والأعداد واستدعاءات `print` المباشرة.
- **المسار الأساسي · 55–70 دقيقة:** إنشاء القوائم والوصول والتعديل والحذف والترتيب والطول والتمرين 3-11. النتيجة: صيانة قائمة ضيوف أو مهام والتعافي من فهرس غير صالح.
- **المسار المتوسط · 30–40 دقيقة:** أكمل التمارين 3-4 إلى 3-10 واشرح العمليات التي تغيّر القائمة الأصلية.
- **معاينة احترافية اختيارية · 40–50 دقيقة:** ابدأ من «اختبارات آلية صغيرة» وتابع مهام TODO الموجّهة. تستبق [الشروط](../chapter-08-conditionals/README.ar.md) و[الحلقات](../chapter-10-loops/README.ar.md) و[الدوال](../chapter-11-functions/README.ar.md) و[الاستثناءات](../chapter-14-exceptions/README.ar.md) و[pytest](../chapter-18-testing/README.ar.md). يمكنك نسخ الأمثلة الكاملة أو الانتقال مباشرة إلى «أخطاء شائعة»؛ وهي غير مطلوبة لـcheckpoint الأساسي.

## لماذا يهم هذا؟
من دون القوائم لا يمكنك الاحتفاظ إلا بقيمة واحدة في كل متغير. تتيح لك القوائم تخزين الكتالوجات أو المستخدمين أو الطلبات أو القراءات في حاوية واحدة مرتبة وديناميكية. إتقان هذه الأنماط يفتح الباب لمعالجة مئات أو آلاف العناصر باستعمال بضعة توابع وحلقات فقط.

### مغامرة صغيرة
تخيّل القائمة كحقيبة ظهر ذات جيوب مرقمة. يمكنك وضع الأشياء فيها وإخراجها ونقلها وعدّها. عند البرمجة، تتيح لك هذه الحقيبة حمل «أشياء كثيرة متشابهة» من دون الاضطرار إلى إنشاء متغير منفصل لكل عنصر.

## توقّع قبل التشغيل
انظر إلى قائمة `bicycles` الأولى. قبل تشغيلها، توقّع القيم عند الفهارس `0` و`-1` و`4`. شغّل عمليات الوصول الصالحة أولًا، ثم استخدم قسم `IndexError` لشرح التوقع غير الصالح والتعافي منه.

---

## ما القائمة؟
القائمة مجموعة مرتبة من العناصر. تنشئها في بايثون بالأقواس المربعة `[]`، وتفصل بين عناصرها بفواصل.

```python runnable
# bicycles.py
bicycles = ["trek", "cannondale", "redline", "specialized"]
print(bicycles)
```

الناتج:
```text illustrative
['trek', 'cannondale', 'redline', 'specialized']
```
يطبع بايثون التمثيل الحرفي للقائمة، لكنك سترغب عادةً في الوصول إلى كل عنصر على حدة.

### الوصول إلى عناصر القائمة
استخدم الفهرس، أي الموضع، داخل الأقواس للحصول على عنصر واحد:

```python illustrative
print(bicycles[0])
print(bicycles[0].title())
```

### تبدأ الفهارس من 0
فهرس العنصر الأول هو `0`، والثاني `1`، وهكذا. العنصر الرابع هو `bicycles[3]`. تعدّ الفهارس السالبة من النهاية (`-1` هو الأخير و`-2` هو ما قبل الأخير).

### استخدام قيم منفردة من قائمة
يمكنك إدراج عناصر القائمة داخل الرسائل باستعمال سلاسل f:

```python illustrative
message = f"My first bicycle was a {bicycles[0].title()}."
print(message)
```

مثال بأسماء أشخاص:
```python runnable
names = ["Noor", "Frej", "Taha"]
print(names[0])
print(f"Hello, {names[1]}!")
```

### جرّب بنفسك (من 3-1 إلى 3-3)
1. **3-1 · الأسماء**: أنشئ قائمة `names` تضم أسماء أصدقاء، واطبع كل اسم على حدة.
2. **3-2 · التحيات**: أعد استعمال القائمة، لكن اطبع تحية مخصصة لكل شخص.
3. **3-3 · قائمتك الخاصة**: أنشئ قائمة بوسائل النقل المفضلة لديك، وولّد جملاً مثل «أود امتلاك …».

---

## تعديل العناصر وإضافتها وحذفها
القوائم ديناميكية: يمكنك تغييرها أثناء تشغيل برنامجك.

### تعديل عناصر القائمة
```python runnable
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles)

motorcycles[0] = 'ducati'
print(motorcycles)
```

### إلحاق العناصر
```python illustrative
motorcycles.append('ducati')
print(motorcycles)

# Build from scratch
teams = []
teams.append('frontend')
teams.append('backend')
print(teams)
```

### إدراج العناصر
```python illustrative
motorcycles.insert(0, 'victory')
print(motorcycles)
```

### حذف العناصر
- تحذف `del lista[i]` العنصر حسب موضعه، ولا تعيد قيمته.
- تحذف `pop()` العنصر الأخير وتعيده، ويمكن تمرير فهرس اختياري إليها.
- تبحث `remove(valor)` عن أول عنصر يساوي `valor` وتحذفه.

```python runnable
motorcycles = ['honda', 'yamaha', 'suzuki', 'ducati']

last = motorcycles.pop()
print(f"Last: {last}")

first = motorcycles.pop(0)
print(f"First: {first}")

motorcycles.remove('yamaha')
print(motorcycles)
```

> ملاحظة: لا تحذف `remove` إلا أول تطابق. إذا احتجت إلى حذف جميع التطابقات، فستستخدم الحلقات لاحقاً.

### جرّب بنفسك (من 3-4 إلى 3-7)
1. **3-4 · قائمة الضيوف**: أنشئ قائمة ضيوف واطبع دعوات مخصصة.
2. **3-5 · تغيير قائمة الضيوف**: استبدل ضيفاً لا يستطيع الحضور، ثم أعد طباعة الدعوات.
3. **3-6 · مزيد من الضيوف**: أعلن عن طاولة أكبر، واستخدم `insert` و`append` لإضافة ثلاثة أشخاص آخرين.
4. **3-7 · تقليص قائمة الضيوف**: قلّصها إلى شخصين باستعمال `pop`، واشكرهما، ثم احذف البقية باستخدام `del`.

---

## تنظيم قائمة
عندما تصل البيانات بترتيب غير متوقع، ستحتاج غالباً إلى عرضها مرتبة من دون إتلاف ترتيبها الأصلي.

### الترتيب الدائم باستخدام `sort()`
```python runnable
cars = ['bmw', 'audi', 'toyota', 'subaru']
cars.sort()
print(cars)  # ['audi', 'bmw', 'subaru', 'toyota']
```
تعكس `cars.sort(reverse=True)` الترتيب الأبجدي وتعدّل القائمة في مكانها.

### الترتيب المؤقت باستخدام `sorted()`
```python illustrative
print(sorted(cars))          # sorted copy
print(sorted(cars, reverse=True))
print(cars)                  # the original list did not change
```

### طباعة قائمة بترتيب معكوس
```python illustrative
cars.reverse()
print(cars)
```
تقلب `reverse()` الترتيب الحالي، ولا «ترتبه تنازلياً»، ويمكنك التراجع عن أثرها باستدعائها مرة أخرى.

### إيجاد طول قائمة
```python illustrative
print(len(cars))
```
يساعدك الطول على التحقق من الفهارس وعرض «عدد العناصر» لديك، مثل الضيوف أو الإدخالات المتبقية.

### جرّب بنفسك (من 3-8 إلى 3-10)
1. **3-8 · رؤية العالم**: أنشئ قائمة بأماكن، وتدرّب على `sorted` و`reverse` و`sort` و`len` من دون فقدان الترتيب الأصلي.
2. **3-9 · ضيوف العشاء**: انطلاقاً من التمارين 3-4 إلى 3-7، اطبع عدد الأشخاص الذين تدعوهم باستخدام `len()`.
3. **3-10 · كل الدوال**: اختر أي قائمة، مثل الجبال أو المدن، واستخدم كل تابع في هذا الفصل مرة واحدة على الأقل.

---

## تجنب `IndexError` عند العمل مع القوائم
الخطأ الأكثر شيوعاً هو طلب فهرس خارج النطاق:

<!-- bookcheck: expect-error="IndexError" -->
```python expected-error
motorcycles = ["honda", "yamaha", "suzuki"]
print(motorcycles[3])
```

يوضح التشخيص أن الموضع المطلوب غير موجود. تعافَ بفهرس مشتق من الطول المرصود بدلاً من التخمين:

```python runnable
motorcycles = ["honda", "yamaha", "suzuki"]
last_index = len(motorcycles) - 1
print(motorcycles[last_index])
```

نصائح لمنعه:
- تحقق من الطول قبل الوصول (`if len(motorcycles) > 2:`).
- استخدم `-1` للعنصر الأخير، ولا تفترض حجماً معيناً.
- إذا حذفت عناصر أثناء التكرار، فكرّر على نسخة (`for item in items[:]`).
- **معاينة اختيارية:** تنتمي الدالة والشرط التاليان إلى [الفصل 11](../chapter-11-functions/README.ar.md) و[الفصل 8](../chapter-08-conditionals/README.ar.md)؛ ولا يحتاجهما المسار الأساسي. إذا تلقت دالة لاحقاً فهرساً خارجياً، فتحقق منه:
  ```python illustrative
  def get_item(items, index):
      if not 0 <= index < len(items):
          raise IndexError("index out of range")
      return items[index]
  ```
- إذا واجهت `IndexError`، فاطبع القائمة أو `len(items)` للتأكد من حالتها الحقيقية.

### جرّب بنفسك (3-11)
أكمل البداية بلا حلقة ولا دالة. شغّل الخطأ المقصود أعلاه مرة واحدة فقط، واقرأ `IndexError`، ثم شغّل التعافي.

```python todo
tasks = ["read", "practice", "rest"]
# TODO 1: predict and print the first and last tasks
# TODO 2: append one task, remove one task, and print a sorted copy
# TODO 3: print the original list and its length
```

*تلميح*: استخدم `[0]` و`[-1]` و`append` و`pop` و`sorted` و`len`؛ ولا يحتاج أي منها إلى فصل لاحق.

---

## اختبارات آلية صغيرة
**معاينة اختيارية:** تستخدم الأقسام الآتية `def` و`if` و`raise` والحلقات وcomprehensions والاستيرادات و`pytest`. الفكرة الدنيا أن الدالة تسمّي عملًا قابلًا لإعادة الاستخدام وأن الاختبار يستدعيه بإدخال معروف. انسخ كل ملف كاملًا أو أجّل المسار حتى الفصول المرتبطة؛ ولا تثبّت `pytest` من مصدر غير ذي صلة.

```python illustrative
# lists_utils.py
def prioritize_task(tasks, new_task):
    if not isinstance(tasks, list):
        raise TypeError("tasks must be a list")
    copy = tasks[:]
    copy.insert(0, new_task)
    return copy

# tests/test_lists_utils.py
import pytest
from lists_utils import prioritize_task

def test_prioritize_task_adds_to_front():
    original = ["document", "refactor"]
    result = prioritize_task(original, "set up CI")
    assert result[0] == "set up CI"
    assert original[0] == "document"  # the copy protects the original list

def test_prioritize_task_rejects_non_lists():
    with pytest.raises(TypeError):
        prioritize_task("not-a-list", "something")
```

---

## أمثلة متدرجة: استكشاف زوايا مثيرة للاهتمام
تزداد صعوبة هذه الأمثلة تدريجياً لتوضّح سلوك القوائم في مواقف تشبه ما يحدث فعلياً في الواجهات الخلفية.

### المثال 1 · قائمة تحقق تفاعلية
```python runnable
checklist = ["Create virtualenv", "Install dependencies", "Run tests"]

for step in checklist:
    print(f"- [ ] {step}")

print(f"The checklist has {len(checklist)} steps.")
last = checklist.pop()              # Get the last step
print(f"Last completed step: {last}")
checklist.append("Publish release")  # Add a new task at the end
```
- تتدرب على الوصول المباشر و`len()` والتعديلات الأساسية (`pop` و`append`).
- يفيد ذلك في سكربتات سطر الأوامر التي تتغير خطواتها أثناء تشغيل البرنامج.

### المثال 2 · طابور الدعم (قائمة تُستخدم كطابور)
```python runnable
ticket_queue = ["BUG-101", "BUG-102", "BUG-103"]

def handle_ticket(queue):
    if not queue:
        return None
    return queue.pop(0)  # pop(0) simulates a FIFO queue

def register_ticket(queue, ticket):
    queue.append(ticket)

current_ticket = handle_ticket(ticket_queue)
print(f"Handling: {current_ticket}")
register_ticket(ticket_queue, "BUG-200")
print(f"Pending: {ticket_queue}")
```
- تكلفة `pop(0)` أعلى، لكنها توضّح سلوك «الأول دخولاً هو الأول خروجاً»؛ ويمكنك لاحقاً استبدالها بـ`collections.deque`.
- هذه التوابع جاهزة للدمج في عرض Django أو webhook حتى قبل إضافة التخزين.

### المثال 3 · أداة لتطبيع القراءات (تحقق واختبارات)
```python runnable
# normalizer.py
def normalize_readings(readings, *, max_limit):
    if not isinstance(readings, list):
        raise TypeError("readings must be a list")
    if not all(isinstance(value, (int, float)) for value in readings):
        raise ValueError("all readings must be numeric")
    if not readings:
        return {"average": 0, "out_of_range": [], "top3": []}

    out_of_range = [value for value in readings if value > max_limit]
    average = sum(readings) / len(readings)
    top3 = sorted(readings, reverse=True)[:3]
    return {"average": average, "out_of_range": out_of_range, "top3": top3}
```

```python illustrative
# tests/test_normalizer.py
import pytest

from normalizer import normalize_readings

def test_normalize_readings_detects_outliers():
    data = [19.2, 20.1, 22.5, 18.0]
    result = normalize_readings(data, max_limit=20)
    assert result["out_of_range"] == [22.5]
    assert result["top3"][0] == 22.5

def test_normalize_readings_validates_types():
    with pytest.raises(ValueError):
        normalize_readings([10, "not-num"], max_limit=50)

def test_normalize_readings_empty_keeps_schema():
    result = normalize_readings([], max_limit=20)
    assert result == {"average": 0, "out_of_range": [], "top3": []}
```
- يجمع المثال بين التقطيع (`[:3]`) والترتيب والتحقق الصارم قبل وضع الوظيفة خلف واجهة API.
- لاحظ كيف تصف الاختبارات الزوايا المهمة: القيم الشاذة والإبلاغ الصحيح عن الأخطاء.

---

## تمارين موجّهة (مع مهام TODO)
1. **G3-1 · دعوات ديناميكية**
   ```python todo
   guests = ["Noor", "Frej", "Taha"]
   # TODO 1: print a personalized message for each guest
   # TODO 2: add two new people at the end using append
   # TODO 3: remove the second guest and print who won’t attend
   ```
   *تلميح*: تكفي `append` و`pop` وحلقة `for`.

2. **G3-2 · قائمة أسعار**
   ```python todo
   prices = [12.5, 9.99, 3.5, 18.0]
   # TODO 1: compute the average with sum/len
   # TODO 2: create a list of prices with VAT (21%)
   # TODO 3: use slicing to show only the two highest prices
   ```
   *تلميح*: ادمج `sorted(prices)` مع `[-2:]`.

3. **G3-3 · المستشعرات والتحقق**
   ```python todo
   readings = [19.2, 20.1, 21.3, 18.9]
   # TODO 1: write function out_of_range(readings, limit)
   # TODO 2: add a test that confirms False when all are in range
   # TODO 3: test that it raises TypeError if readings is not a list
   ```
   *تلميح*: استخدم `any(value > limit for value in readings)` ونمط الاختبار السابق.

---

## أخطاء شائعة
- بدء العد من 1 والتسبب في `IndexError`.
- تعديل قائمة أثناء التكرار عليها من دون إنشاء نسخة أولاً.
- الخلط بين `append`، التي تضيف القائمة كعنصر واحد، و`extend`.
- تغيير الترتيب الأصلي باستخدام `sort()` حين كنت تحتاج إلى نسخة مرتبة (`sorted`).
- نسيان أن `remove` لا تحذف إلا أول ظهور للقيمة.

---

## حلول مشروحة للتمارين الموجّهة
1. **G3-1**: ولّد الرسائل بحلقة `for`، واستخدم `append` لإضافة الضيوف، بينما تعيد `pop(1)` الشخص المحذوف كي تتمكن من الإعلان عن ذلك.
2. **G3-2**: المتوسط هو `sum(prices)/len(prices)`؛ وقائمة الأسعار مع الضريبة هي `[price * 1.21 for price in prices]`؛ وأعلى سعرين يأتيان من `sorted(prices)[-2:]`.
3. **G3-3**: تكتشف `any(value > limit for value in readings)` القيم الخارجة عن النطاق بعد التحقق بـ`isinstance(readings, list)`؛ وتغطي الاختبارات المسار الناجح وأخطاء النوع.

---

## Checkpoint وتقييم ذاتي

### الحل المشروح للتمرين 3-11

تحقق أولًا من المسار العادي:

```python runnable
tasks = ["read", "practice", "rest"]
print(tasks[0])
print(tasks[-1])
tasks.append("review")
removed = tasks.pop(1)
sorted_tasks = sorted(tasks)
print(removed)
print(sorted_tasks)
print(tasks)
print(len(tasks))
```

ثم تحقق من حد القائمة الفارغة من دون فهرستها:

```python runnable
tasks = []
print(tasks)
print(len(tasks))
print(sorted(tasks))
```

يتطلب التحقق ثلاثة سجلات: المخرجات العادية، و`0` للحد الفارغ، و`IndexError` المتوقع السابق متبوعًا مباشرة بالتعافي القابل للتشغيل. تأمل في جملة: لماذا يكون اشتقاق `last_index` من `len()` أكثر أمانًا من تخمين موضع؟

أنشئ قائمة بثلاث مهام. توقّع القيمتين الأولى والأخيرة، وأضف مهمة، واحذف أخرى، واعرض نسخة مرتبة، وأثبت أن الترتيب الأصلي لم يتغير. ثم اطلب عمدًا فهرسًا غير صالح، واقرأ `IndexError`، وتعافَ بالتحقق من `len()` قبل المحاولة التالية.

امنح نفسك نقطة لكل معيار:
- **الصحة:** تطابق نتائج الوصول والإضافة والحذف والنسخة المرتبة توقعاتك.
- **سهولة القراءة:** توضّح الأسماء محتوى القائمة ولكل عملية غرض واضح.
- **معالجة الخطأ:** تشرح الفهرس غير الصالح وتتعافى من دون تخمين طول القائمة.
- **التحقق:** تطبع القائمة الأصلية والمشتقة وتحدد العملية التي غيّرت البيانات.
- **الشرح:** تبرر اختيار `pop` أو`remove` أو`sort` أو`sorted` في حالة محددة.

يكتمل المسار الأساسي بـ5/5. عند 4/5 راجع دليل الحالة العادية أو الحد أو التعافي الناقص قبل المتابعة؛ وتحت 4/5 أعد 3-11. تبقى الدوال والحلقات والاستثناءات وcomprehensions وpytest معاينات اختيارية.

---

## الخلاصة
عرّفت في هذا الفصل القوائم، ووصلت إلى عناصرها بفهارس موجبة وسالبة، وأعدت استعمال القيم داخل السلاسل النصية، وعدّلت القائمة أثناء التشغيل بالإضافات والإدراج والحذف. كما رتبتها دائماً أو مؤقتاً، واستخدمت `len()` و`reverse()` لفحصها. وتعلمت أيضاً تجنب `IndexError`، بل وكتبت اختبارات للتحقق من هذه العمليات.

## تأمل ختامي
يعني إتقان القوائم القدرة على التعامل مع مجموعات كاملة من البيانات في أسطر قليلة: يمكنك إضافة المعلومات وحذفها وتقطيعها وترتيبها والتحقق منها من دون تكرار الشيفرة. في الفصل التالي سننتقل إلى بُنى تقرن *المفاتيح* بـ*القيم*، وهي القواميس التي تشكّل أساس JSON وواجهات API.

</div>
