<div dir="rtl">

# الفصل 7 · الطوابير والمكدسات باستخدام `collections.deque`

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
ستتعلم استخدام `collections.deque` لنمذجة الطوابير (FIFO) والمكدسات (LIFO) والنوافذ المنزلقة. وسننفذ أمثلة مستوحاة من طوابير المهام ومخازن السجلات ومحددات المعدل الخفيفة، جاهزة للدمج في خدمات Django أو سكربتات الأتمتة.

## مسار التعلم
1. **تذكير سريع بالقوائم**: لماذا لا تتوسع `list.pop(0)` بكفاءة.
2. **جسر imports**: اطلب من المفسّر المحدد module من المكتبة القياسية وشخّص فشل البحث بأمان.
3. **التعرّف إلى `deque`**: الإنشاء والعمليات الأساسية.
4. **طابور FIFO**: الإدخال والإخراج باستخدام `append` و`popleft`.
5. **مكدس LIFO**: استخدام `append` و`pop` مع `deque` لتحقيق الاتساق.
6. **النوافذ المنزلقة وتحديد المعدل**: `maxlen` والعد ضمن مدة زمنية.
7. **التحقق والاختبارات**: التأكد من احترام السعة والترتيب.

## أهداف التعلم
- إنشاء `deque` محدودة أو غير محدودة، وفهم سبب تفوقها على القوائم في الطوابير.
- التمييز بين modules من المكتبة القياسية ومحلية ومن طرف ثالث، واستخدام `import module` و`from module import name` و`python -m module` عن قصد.
- تشخيص module مفقودة أو محجوبة عرضًا من دون تثبيت packages عشوائية أو تعديل Python نفسه.
- تنفيذ الطوابير والمكدسات بعمليات O(1) عند الطرفين.
- استخدام `maxlen` لبناء مخازن دورانية.
- بناء نوافذ منزلقة للمقاييس أو تقييد الطلبات.
- اختبار الطوابير لضمان ترتيبها وثوابتها.

## المتطلبات المسبقة والمسارات
[القوائم](../chapter-03-lists/README.ar.md) وحلقة الملف/التشغيل في الفصل 1 هما المتطلبان السابقان الوحيدان. يعلّم الجسر التالي مفهوم import الإضافي مباشرة قبل أول حاجة إلى `deque`.

- **المسار الأساسي · 60–80 دقيقة:** القسم 1، وجسر imports كاملًا، والأقسام 2–4، ومثال `maxlen` المباشر في القسم 5، والتمرينان 7-import و7-0. النتيجة: تشغيل module محلية واحدة تستخدم المكتبة القياسية بطريقتين، وتتبع حالة FIFO وLIFO والمخزن المحدود باستخدام imports وعمليات `deque` فقط. لا يتطلب شروطًا أو دوالًا أو أصنافًا أو معالجة استثناءات أو تثبيت package أو اختبارات.
- **المسار المتوسط · 25–35 دقيقة:** التمرين 7-2 بعد تعلم [الحلقات](../chapter-10-loops/README.ar.md). النتيجة: ملء مخزن ثابت وشرح القيمة التي تُحذف.
- **معاينة احترافية اختيارية · 60–90 دقيقة:** الصنف ومحدد المعدل والقسم 6 والتمرينان 7-1 و7-3. تستعرض [الشروط](../chapter-08-conditionals/README.ar.md) و[الدوال](../chapter-11-functions/README.ar.md) و[الأصناف](../chapter-12-oop/README.ar.md) و[الاستثناءات](../chapter-14-exceptions/README.ar.md) و[الاختبارات](../chapter-18-testing/README.ar.md). انسخ الأمثلة الكاملة أو تجاوزها؛ ليست مطلوبة لنقطة التحقق الأساسية.

## لماذا يهم هذا؟
من الشائع في أنظمة الواجهات الخلفية معالجة الأحداث بترتيب وصولها أو الاحتفاظ بسجل ذي حجم ثابت. `deque` أكثر كفاءة من القوائم لهذه الأنماط، وهي ضمن المكتبة القياسية، لذلك لا تحتاج إلى تبعيات إضافية.

### مغامرة صغيرة
فكّر في طابور مدينة ألعاب: أول شخص يصل هو أول من يركب. باستخدام `deque` تبني ذلك الطابور بكفاءة؛ تضيف الأشخاص في النهاية وتخرجهم من البداية من دون دفع الجميع إلى الأمام.

## توقّع قبل التشغيل
ارسم محتوى `deque` بعد كل `append` و`popleft` و`pop` قبل العمليات الأولى. توقّع أي عنصر تحذفه `deque(maxlen=3)` عند إضافة عنصر رابع. يخص توقع محدد المعدل المعاينة الاحترافية الاختيارية.

---

## 1. لماذا لا نستخدم القوائم وحدها؟
يجب على `list.pop(0)` إزاحة العناصر المتبقية، مما يجعل تعقيدها O(n). وفي طوابير المهام أو السجلات يصبح ذلك عنق زجاجة. صُممت `deque` للإدراج والحذف عند الطرفين في زمن O(1).

---

## جسر imports: تعرّف إلى modules قبل `deque`

يطلب import من **مفسّر Python المحدد نفسه** الذي يشغّل ملفك أن يعثر على module ويحمّلها. تكون module عادة ملف `.py` أو module توفرها Python. ميّز بين ثلاثة مصادر:

- تأتي **المكتبة القياسية** مع تثبيت Python المعلن؛ ومن أمثلتها `collections` و`random`، فلا تثبتهما باستخدام `pip`؛
- **module محلية** هي ملف `.py` قابل للـimport أنشأته أنت، مثل `queue_demo.py`؛
- **package من طرف ثالث** تُثبّت منفصلة داخل environment. يعلّم الفصل 16 هذا المسار، ولا يحتاج المسار الأساسي هنا إلى أي منها.

تُشرح بنية packages وتصميم APIs العامة القابلة لإعادة الاستخدام بتوسع في [الفصل 15](../chapter-15-modulos/README.ar.md). نحتاج هنا فقط إلى معرفة كافية بـimports لاستخدام `deque` بصدق.

### صيغتا import ومساحتا أسماء

توقّع أي spelling ينشئ الطابور في كل مثال كامل:

```python runnable
import collections

queue = collections.deque(["A", "B"])
print(queue.popleft())
```

تربط `import collections` اسم module، لذلك نصل إلى الاسم مؤهلًا هكذا: `collections.deque`. وعلى النقيض:

```python runnable
from collections import deque

queue = deque(["A", "B"])
print(queue.popleft())
```

تربط `from collections import deque` الاسم العام المحدد مباشرة. يطبع المثالان `A` تمامًا. لا يتوفر `deque(...)` عاريًا بعد `import collections` وحدها، لأن الصيغتين تربطان اسمين مختلفين.

### شغّل module محلية بالمفسّر المحدد

احفظ الآتي باسم `queue_demo.py` داخل مجلد disposable تملكه للتعلّم:

```python runnable
from collections import deque

queue = deque(["A", "B"])
print(queue.popleft())
```

يشغّل كل من أمري shell التاليين الملف مرة واحدة من داخل ذلك المجلد وينتج السطر نفسه:

```bash illustrative
python queue_demo.py
python -m queue_demo
```

تطلب صيغة `-m` من هذا المفسّر إيجاد module المحلية القابلة للـimport والمسماة `queue_demo` من موقع import الحالي. لا تتضمن `.py`. لا يقدّم هذا المثال ذو الملف الواحد imports نسبية داخل package بعد.

### توقّع ولاحظ module مفقودة

هذه module مخترعة للمساق وغير موجودة:

```python illustrative
import course_module_that_does_not_exist
```

يشغّل عقد الفصل القابل للتنفيذ هذا import في subprocess معزول. الفئة المستقرة هي `ModuleNotFoundError`؛ أما الرسالة الكاملة المعتمدة على البيئة فليست جزءًا من العقد. شخّص بهذا الترتيب:

1. افحص التهجئة.
2. قرر هل يفترض أن يكون الاسم من المكتبة القياسية أم محليًا أم من طرف ثالث.
3. بالنسبة إلى module محلية، افحص اسم الملف وworking directory في shell.
4. بالنسبة إلى dependency معروفة من طرف ثالث فقط، اتبع تعليمات تثبيت المشروع التي تمت مراجعتها لاحقًا في الفصل 16.

لا تستجب لكل import مفقود بتثبيت package مشابهة الاسم من index.

### Shadowing: حين يحجب ملفك module المقصودة

قد يعثر بحث imports في Python على ملف يملكه المتعلّم قبل module المكتبة المقصودة. لذلك يمكن لملف أو مجلد اسمه `collections.py` أو `typing.py` أو `random.py` داخل مجلد التمرين أن **يحجب** module. قد يظهر ذلك في مسار مصدر مفاجئ أو رسالة تقول إن module المستوردة لا تملك attribute المتوقعة.

التعافي محلي وقابل للعكس:

1. افحص مسار module المبلّغ عنه في process تشخيص جديدة، مثل `python -c "import collections; print(collections.__file__)"`.
2. إذا كان المسار يشير إلى ملف متعارض أنشأته داخل مجلد التمرين disposable، فأعد تسمية ذلك الملف وحده باسم يصف المجال مثل `queue_notes.py`.
3. أنهِ REPL القديم إن كان مفتوحًا، وابدأ process مفسّر جديدة في المجلد المقصود، ثم أعد تشغيل `from collections import deque`.
4. احذف فقط ملفات cache المنشأة داخل مجلد التمرين disposable إن بقيت؛ ولا تحذف أو تعدّل ملفًا من المكتبة القياسية أبدًا.

يطبع مثال الطابور بعد التعافي `A` مجددًا. إعادة البدء مهمة لأن process قيد التشغيل قد تحتفظ بـmodules سبق أن استوردتها.

### TODO موجّه للـimport مع تلميح وحل مشروح

```python todo
# queue_demo.py
# TODO 1: import the standard-library deque name from collections.
# TODO 2: create a deque containing "A" and "B".
# TODO 3: remove and print the oldest value.
# TODO 4: run this file as a path and then with `python -m queue_demo`.
```

**تلميح:** تبدأ الصيغة المباشرة بـ`from collections import ...`، وتحذف `popleft()` من طرف الوصول. يدخل اسم الملف في أمر المسار، لكن لاحقة `.py` تُحذف بعد `-m`.

```python runnable
from collections import deque

queue = deque(["A", "B"])
print(queue.popleft())
```
```text output
A
```

تكمل جسر imports حين تنتج صيغتا shell هذا السطر، وتلاحظ الفشل المتوقع للـmodule المخترعة وتصنّفه، وتستطيع شرح لماذا تكون إعادة تسمية ملف shadow يملكه المتعلّم أكثر أمانًا من تغيير تثبيت Python.

امنح نفسك نقطة لكل من **الـimport المباشر الصحيح**، و**شرح الصيغة المؤهلة**، و**صيغتي التشغيل المحلي**، و**التعافي من module مفقودة/محجوبة**، و**تحديد `collections` بوصفها من المكتبة القياسية**. تكمل 5/5 الجسر؛ ويبقى الفصل 15 للتعمق لاحقًا.

---

## 2. الإنشاء والعمليات الأساسية

```python runnable
from collections import deque

queue = deque(["task-1", "task-2"])
queue.append("task-3")
print(queue)

last = queue.pop()
print(f"Last removed: {last}")
```

- تنشئ `deque()` من دون معاملات بنية فارغة.
- يمكنك تمرير `maxlen` لتحديد الحجم الأقصى.

---

## 3. طابور FIFO (الأول دخولاً هو الأول خروجاً)

```python runnable
from collections import deque

queue = deque(["ticket-a", "ticket-b"])
queue.append("ticket-c")
first = queue.popleft()
print(first)
print(list(queue))
```

تضيف `append` عند طرف الوصول، وتحذف `popleft` أقدم عنصر. هذا هو نموذج FIFO الأساسي الكامل.

### معاينة اختيارية: تغليف الطابور في صنف

```python runnable
from collections import deque

class SupportQueue:
    def __init__(self):
        self._queue = deque()

    def enqueue(self, ticket):
        self._queue.append(ticket)

    def handle_next(self):
        if not self._queue:
            return None
        return self._queue.popleft()  # O(1)

    def pending(self):
        return list(self._queue)
```

- تحافظ `append` و`popleft` على ترتيب الوصول.
- يسهّل التحويل إلى قائمة (`list(self._queue)`) عرض الحالة في واجهة المستخدم أو السجلات.

---

## 4. مكدس LIFO بالبنية نفسها

```python runnable
from collections import deque

stack = deque()
stack.append("deploy")
stack.append("rollback")

last = stack.pop()
print(last)
```

- يوحّد استخدام `deque` للمكدسات بُنى بياناتك؛ ويمكنك تبديل السلوك من دون تبديل النوع.

---

## 5. النوافذ المنزلقة و`maxlen` وتحديد المعدل

```python runnable
from collections import deque

logs = deque(["start", "connect", "query"], maxlen=3)
logs.append("disconnect")
print(list(logs))  # ['connect', 'query', 'disconnect']
```

تحذف الإضافة الرابعة أقدم قيمة. هذا المخزن المباشر المحدود جزء من المسار الأساسي.

### معاينة احترافية اختيارية: محدد معدل زمني

```python runnable
from collections import deque
from time import monotonic

class RateLimiter:
    def __init__(self, max_requests, window_seconds, clock=monotonic):
        if isinstance(max_requests, bool) or not isinstance(max_requests, int) or max_requests <= 0:
            raise ValueError("max_requests must be a positive integer")
        if isinstance(window_seconds, bool) or not isinstance(window_seconds, (int, float)) or window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        if not callable(clock):
            raise TypeError("clock must be callable")
        self.window = float(window_seconds)
        self.max_requests = max_requests
        self.timestamps = deque()
        self._clock = clock

    def allow(self):
        now = self._clock()
        cutoff = now - self.window
        while self.timestamps and self.timestamps[0] <= cutoff:
            self.timestamps.popleft()
        if len(self.timestamps) >= self.max_requests:
            return False
        self.timestamps.append(now)
        return True

ticks = iter([0.0, 1.0, 2.0, 10.0])
limiter = RateLimiter(2, 10, clock=lambda: next(ticks))
assert [limiter.allow() for _ in range(4)] == [True, True, False, True]
```

- احذف الطوابع الزمنية الواقعة عند حد النافذة أو قبله؛ فيكون المجال النشط `(الآن - النافذة، الآن]`.
- ارفض عندما تكون `len(self.timestamps) >= max_requests`؛ ويجعل حقن الساعة الرتيبة اختبار الحد حتمياً.
- يجب أن تكون الساعة المحقونة قابلة للاستدعاء وأن تعيد أعداداً غير متناقصة مثل `monotonic()`.

### المخازن الدائرية باستخدام `maxlen`
```python illustrative
logs = deque(maxlen=3)
for event in ["start", "connect", "query", "disconnect"]:
    logs.append(event)
print(list(logs))  # only keeps the last 3 events
```

---

## 6. التحقق والاختبارات

```python runnable
# queues.py
from collections import deque

class BoundedQueue:
    def __init__(self, maxlen):
        if maxlen <= 0:
            raise ValueError("maxlen must be positive")
        self._data = deque(maxlen=maxlen)

    def push(self, value):
        if len(self._data) == self._data.maxlen:
            raise OverflowError("Queue full")
        self._data.append(value)

    def pop(self):
        if not self._data:
            raise IndexError("Queue empty")
        return self._data.popleft()
```

```python illustrative
# tests/test_queues.py
import pytest
from queues import BoundedQueue

def test_bounded_queue_keeps_order():
    queue = BoundedQueue(maxlen=2)
    queue.push("a")
    queue.push("b")
    assert queue.pop() == "a"

def test_bounded_queue_respects_maxlen():
    queue = BoundedQueue(maxlen=1)
    queue.push("a")
    with pytest.raises(OverflowError):
        queue.push("b")
```

---

## تمارين موجّهة (مع مهام TODO)
0. **7-import · استورد `queue_demo` وشغّلها**

   أكمل TODO الموجّه للـimport أعلاه، وشغّل صيغتي shell الموثقتين، واشرح لماذا لا تحتاج `collections` إلى تثبيت منفصل. احتفظ بكل الملفات داخل مجلد disposable تملكه للتعلم.

   *تلميح*: بعد التشغيلين الناجحين، استخدم block الـmodule غير الموجودة عمدًا للتدرّب على التشخيص؛ ولا تثبّتها.

0. **7-0 · تتبّع الطابور الأساسي**
   ```python todo
   from collections import deque
   tickets = deque(["A", "B"])
   # TODO 1: أضف "C" واحذف أقدم تذكرة باستخدام popleft
   # TODO 2: استخدم deque أخرى كمكدس واحذف أحدث عنصر باستخدام pop
   # TODO 3: أنشئ deque(["one", "two"], maxlen=2)، وأضف "three"، وتوقع النتيجة
   ```
   *تلميح*: ارسم الطرفين بعد كل عملية؛ لا تحتاج إلى `if` أو دالة أو صنف أو اختبار.

التمارين المتبقية معاينات اختيارية تستخدم فصولًا لاحقة.

1. **7-1 · طابور بريد إلكتروني**
   ```python todo
   from collections import deque
   emails = deque()
   # TODO 1: add three fake emails
   # TODO 2: write send_next(queue) that does popleft and returns the email
   # TODO 3: handle empty queue by returning None
   ```
   *تلميح*: استلهم من `SupportQueue`.

2. **7-2 · مخزن سجلات محدود**
   ```python todo
   from collections import deque
   logs = deque(maxlen=5)
   events = ["start", "init", "load", "ready", "request", "error"]
   # TODO 1: append each event to the deque
   # TODO 2: print only the events that stayed in the buffer
   # TODO 3: explain why maxlen prevents using more memory
   ```
   *تلميح*: حوّل إلى قائمة لعرض المخزن النهائي.

3. **7-3 · نافذة منزلقة للمقاييس**
   ```python todo
   from collections import deque
   measurements = deque(maxlen=3)
   # TODO 1: write add_measurement(value) that appends and returns the current average
   # TODO 2: compute the average only with the values in the current window
   # TODO 3: add a test confirming the window never exceeds maxlen
   ```
   *تلميح*: احسب `sum(measurements)/len(measurements)` بعد الإضافة.

---

## أخطاء شائعة
- **استخدام القوائم للطوابير كثيفة العمليات** ← بطيء. انتقل إلى `deque` عندما تستخدم `pop(0)` أو `insert(0)` كثيراً.
- **عدم حذف العناصر القديمة** ← تكبر النوافذ الزمنية إلى الأبد. نظّفها بحلقة `while` كما في `RateLimiter`.
- **افتراض أن `maxlen` تطلق أخطاء** ← تتخلص افتراضياً من العناصر عند الطرف الآخر؛ وإذا أردت أخطاء فتحقق من `len` قبل `append`، كما في `BoundedQueue`.
- **مشاركة `deque` نفسها بين خيوط من دون أقفال** ← استخدم الأقفال أو الطوابير الآمنة للخيوط، مثل `queue.Queue`، عند وجود تزامن.
- **تثبيت `collections` من package index** ← هي موجودة أصلًا في مكتبة Python القياسية؛ تحقق من المفسّر المحدد بدلًا من ذلك.
- **تسمية ملف محلي `collections.py` أو `typing.py`** ← قد يحجب module المقصودة؛ أعد تسمية مصدرك المحلي وحده ثم أعد بدء process.
- **كتابة `python -m queue_demo.py`** ← يستخدم وضع module اسم import، أي `queue_demo` من دون لاحقة الملف.

---

## حلول مشروحة
### حل 7-0 الأساسي والتعافي
تغيّر `append` الطرف الأيمن، وتغيّر `popleft` الطرف الأيسر، وتغيّر `pop` الطرف الأيمن، وتحذف `maxlen` من الطرف المقابل.

```python runnable
from collections import deque
tickets = deque(["A", "B"])
tickets.append("C")
print(tickets.popleft())
stack = deque(["draft", "publish"])
print(stack.pop())
bounded = deque(["one", "two"], maxlen=2)
bounded.append("three")
print(list(bounded))
```

تفشل `popleft` إضافية على deque فارغة بالإشارة الثابتة `IndexError`:

<!-- bookcheck: expect-error="IndexError" -->
```python expected-error
from collections import deque
deque().popleft()
```

تعافَ بالتحقق من الطول المرسوم أو المطبوع ثم نفّذ حذفًا صالحًا فقط:

```python runnable
from collections import deque
tickets = deque(["A"])
print(tickets.popleft())
```

1. **طابور البريد الإلكتروني**: تستدعي `send_next` الدالة `popleft()` وتعيد `None` إذا كان الطابور فارغاً، فتتجنب الاستثناءات وتجعل الدالة قابلة للتكرار بأمان.
2. **مخزن السجلات المحدود**: يحافظ التكرار وتنفيذ `logs.append(event)` على آخر خمسة عناصر فقط؛ وتعرض `list(logs)` المحتوى النهائي.
3. **مقاييس النافذة المنزلقة**: بعد كل إدراج، احسب `average = sum(measurements) / len(measurements)`؛ ويتحقق الاختبار من بقاء `len(measurements)` مساوية لـ3 بعد إدراجات كثيرة.

---

## نقطة تحقق وتقييم ذاتي
أكمل 7-import و7-0. شغّل `queue_demo.py` بوصفها مسارًا وباستخدام `-m`، وصنّف `ModuleNotFoundError` الموثقة، واشرح التعافي من shadowing، وتوقّع كل قيمة تُحذف أو تُستبعد، ولاحظ عمدًا `IndexError` الموثقة للـdeque الفارغة، ثم أعد تشغيل حالة التعافي. محدد المعدل وحدّه الزمني جزء من المعاينة الاحترافية الاختيارية.

امنح نقطة لكل من **صحة import والتشغيل** و**صحة FIFO** و**صحة LIFO** و**حد `maxlen`** و**شرحي التعافي**. تكمل 5/5 المسار الأساسي؛ وإلا فعد إلى جسر imports أو الأقسام 2–5 وكرر الملاحظة الناقصة وحدها.

## الخلاصة
`collections.deque` حل فعال من المكتبة القياسية للطوابير والمكدسات والنوافذ المنزلقة. أصبحت تعرف كيف يعثر عليها المفسّر المحدد، ومتى تفضّلها على القوائم، وكيف تستخدم `maxlen`، وكيف تتحقق من السلوك باختبارات بسيطة.

## تأمل ختامي
أي سؤال تشخيصي ستطرحه أولًا عند import مفقود: التهجئة أم مصدر module أم working directory أم التثبيت؟ اشرح لماذا تعتمد الإجابة على كون module من المكتبة القياسية أو محلية أو من طرف ثالث. باستخدام طوابير متينة تستطيع بناء محددات معدل ومخازن مؤقتة ومعالجات أحداث مع إبقاء بحث modules مفهومًا وقابلًا للتعافي.

</div>
