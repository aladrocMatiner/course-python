<div dir="rtl">

# الفصل 7 · الطوابير والمكدسات باستخدام `collections.deque`

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
ستتعلم استخدام `collections.deque` لنمذجة الطوابير (FIFO) والمكدسات (LIFO) والنوافذ المنزلقة. وسننفذ أمثلة مستوحاة من طوابير المهام ومخازن السجلات ومحددات المعدل الخفيفة، جاهزة للدمج في خدمات Django أو سكربتات الأتمتة.

## مسار التعلم
1. **تذكير سريع بالقوائم**: لماذا لا تتوسع `list.pop(0)` بكفاءة.
2. **التعرّف إلى `deque`**: الإنشاء والعمليات الأساسية.
3. **طابور FIFO**: الإدخال والإخراج باستخدام `append` و`popleft`.
4. **مكدس LIFO**: استخدام `append` و`pop` مع `deque` لتحقيق الاتساق.
5. **النوافذ المنزلقة وتحديد المعدل**: `maxlen` والعد ضمن مدة زمنية.
6. **التحقق والاختبارات**: التأكد من احترام السعة والترتيب.

## أهداف التعلم
- إنشاء `deque` محدودة أو غير محدودة، وفهم سبب تفوقها على القوائم في الطوابير.
- تنفيذ الطوابير والمكدسات بعمليات O(1) عند الطرفين.
- استخدام `maxlen` لبناء مخازن دورانية.
- بناء نوافذ منزلقة للمقاييس أو تقييد الطلبات.
- اختبار الطوابير لضمان ترتيبها وثوابتها.

## المتطلبات المسبقة والمسارات
تمثل [القوائم](../chapter-03-lists/README.ar.md) المتطلب المسبق الوحيد.

- **المسار الأساسي · 45–60 دقيقة:** الأقسام 1–4، ومثال `maxlen` المباشر في القسم 5، والتمرين 7-0. النتيجة: تتبّع حالة FIFO وLIFO والمخزن المحدود بعمليات `deque` فقط. لا يتطلب شروطًا أو دوالًا أو أصنافًا أو معالجة استثناءات أو اختبارات.
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
أكمل 7-0، وتوقّع كل قيمة تُحذف، وشغّل الحالة العادية، ولاحظ عمدًا `IndexError` الموثق للـdeque الفارغة، ثم شغّل حالة التعافي. محدد المعدل وحده الزمني جزء من المعاينة الاحترافية الاختيارية.

امنح نقطة لكل من **صحة FIFO** و**صحة LIFO** و**حد `maxlen`** و**التعافي من الخطأ** و**شرح الطرفين**. تكمل 4/5 المسار الأساسي؛ وإلا فعد إلى الأقسام 2–5 وارسم الحالة مجددًا.

## الخلاصة
`collections.deque` حل فعال للطوابير والمكدسات والنوافذ المنزلقة. أصبحت تعرف متى تفضّلها على القوائم، وكيف تستخدم `maxlen`، وكيف تتحقق من السلوك باختبارات بسيطة.

## تأمل ختامي
يمكنك باستخدام طوابير متينة بناء محددات معدل ومخازن مؤقتة ومعالجات أحداث تتوسع بصورة أفضل. ولديك الآن الأساس لدمج هذه البُنى في واجهات API والعُمّال وأدوات المراقبة، وبذلك تكتمل مقدمة قوية إلى بُنى بيانات بايثون الأساسية.

</div>
