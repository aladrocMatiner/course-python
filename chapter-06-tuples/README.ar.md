<div dir="rtl">

# الفصل 6 · الصفوف وعدم القابلية العملية للتغيير

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
سنرى كيف تساعد الصفوف في تمثيل السجلات الخفيفة والقيم المتعددة المعادة والمفاتيح المركبة ذات العناصر القابلة للتجزئة. وسنعمل مع الإحداثيات ونتائج الدوال والبُنى الصغيرة التي ينبغي ألا تتغير مواضعها بعد إنشائها.

## مسار التعلم
1. **النموذج الذهني**: الفرق بين القوائم والصفوف.
2. **الإنشاء والوصول**: القيم الحرفية و`tuple()` وفك التعبئة.
3. **القيم المتعددة المعادة**: دوال تعيد أكثر من معلومة واحدة.
4. **الصفوف بوصفها مفاتيح**: قواميس تستخدم الصفوف لفهرسة البيانات المركبة.
5. **`namedtuple` و«كائنات البيانات» الخفيفة** لتحسين سهولة القراءة.
6. **التحقق والاختبارات**: ضمان عدم إمكان تعديل البيانات المهمة.

## أهداف التعلم
- إنشاء صفوف لتمثيل بيانات ينبغي ألا تتغير.
- فك الصفوف إلى متغيرات واستخدام `_` للقيم التي لا تحتاج إليها.
- إعادة قيم متعددة من دالة من دون إنشاء أصناف كاملة.
- استخدام الصفوف مفاتيح للقواميس أو عناصر في المجموعات عندما تكون كل قيمها قابلة للتجزئة.
- كتابة اختبارات تؤكد عدم قابلية التغيير والبنية المتوقعة.

## المتطلبات المسبقة والمعاينات الاختيارية
ينبغي أن تعرف [القوائم](../chapter-03-lists/README.ar.md) و[القواميس](../chapter-04-dictionaries/README.ar.md). تعد القيم المعادة من الدوال والاستثناءات و`namedtuple` وpytest معاينات؛ اتبع الأنماط الآن ثم ادرس [الدوال](../chapter-11-functions/README.ar.md) و[الأصناف](../chapter-12-oop/README.ar.md) و[الاستثناءات](../chapter-14-exceptions/README.ar.md) و[الاختبارات](../chapter-18-testing/README.ar.md) في فصولها.

## لماذا يهم هذا؟
تحتاج في كثير من واجهات API إلى تجميع البيانات لفترة قصيرة، مثل الإحداثيات والنطاقات الزمنية وأزواج الحالات. الصفوف أخف من القوائم وتوصل معنى «لا تغيّر هذه القيم»، مما يمنع الأخطاء في خطوط المعالجة وذاكرات التخزين المؤقت والمفاتيح المركبة.

### مغامرة صغيرة
يشبه الصف كتابة إحداثي على خريطة بحبر دائم؛ فلا يمكن إعادة إسناد مواضعه. لكن التشبيه لا يشمل الكائنات القابلة للتغيير الموجودة داخله، فالصف لا يجمّدها.

## توقّع قبل التشغيل
قبل المثال الأول، توقّع أي إسناد ينجح وأيهما يطلق `TypeError`. ثم اسأل هل `(1, [])` قابل للتجزئة؛ تفصل الإجابة بين ثبات بنية الصف وقابلية الكائنات الموجودة داخله للتغيير.

---

## 1. النموذج الذهني: القائمة مقابل الصف

```python runnable
point_list = [10, 20]
point_tuple = (10, 20)

point_list[0] = 99       # ✔ can mutate
# point_tuple[0] = 99    # ✘ TypeError: tuples are immutable
```

- استخدم الصفوف عندما تريد إشارة واضحة إلى بنية ثابتة أو «للقراءة فقط». لا يمكن إعادة إسناد عناصر الصف نفسه، لكن الكائن القابل للتغيير المخزّن داخله يظل قابلاً للتعديل.
- لا يكون الصف قابلاً للتجزئة إلا إذا كانت كل قيمة يحتويها قابلة للتجزئة؛ وعندها فقط يصلح مفتاحاً لقاموس أو عنصراً في مجموعة.

---

## 2. الإنشاء وفك التعبئة

```python runnable
coordinate = (41.40338, 2.17403)
latitude, longitude = coordinate
print(latitude, longitude)

hours = tuple(range(0, 24))
print(hours[:3])
```

```python runnable
record = ("Noor", "Frej", 1815)
first_name, last_name, _ = record  # ignore the year with _
print(first_name, last_name)
```

- يحسن فك التعبئة سهولة القراءة ويجنبك «الفهارس السحرية».
- استخدم `_` للقيم التي تتجاهلها عن قصد.

---

## 3. إعادة قيم متعددة

```python runnable
def divide_and_remainder(dividend, divisor):
    if divisor == 0:
        raise ZeroDivisionError("Divisor cannot be zero")
    return dividend // divisor, dividend % divisor

quotient, remainder = divide_and_remainder(10, 3)
print(quotient, remainder)
```

- هذا أوضح من إعادة قاموس عندما لا تحتاج إلا إلى زوج مرتب.
- وثّق ترتيب القيم المعادة لتجنب الالتباس.

---

## 4. الصفوف بوصفها مفاتيح للقواميس

```python runnable
city_coordinates = {
    (41.3874, 2.1686): "Barcelona",
    (40.4168, -3.7038): "Madrid",
}

print(city_coordinates.get((41.3874, 2.1686)))
```

```python runnable
response_cache = {}

params = ("/api/report", "POST", frozenset({("team", "analytics")}))
response_cache[params] = {"status": 200, "body": "OK"}
```

- اجمع المعاملات ذات المعنى في صفوف لإنشاء مفاتيح مستقرة لذاكرة التخزين المؤقت.
- يتيح مزج الصفوف مع `frozenset` تضمين المعاملات بأي ترتيب من دون إفساد المفتاح.

---

## 5. استخدام `namedtuple` لإضافة معنى

```python runnable
from collections import namedtuple

Coordinate = namedtuple("Coordinate", ["lat", "lon"])
point = Coordinate(lat=41.4, lon=2.17)
print(point.lat)
```

- تحصل على مزايا الصفوف، أي عدم قابلية التغيير وخفة الوزن، مع إمكانية الوصول بالأسماء.
- وهي مفيدة لإعادة بُنى توثّق نفسها من الدوال أو الخدمات.

---

## 6. التحقق والاختبارات

```python runnable
# ranges.py
from typing import Tuple

HourRange = Tuple[int, int]

def validate_range(interval: HourRange) -> bool:
    start, end = interval
    if not (0 <= start < 24 and 0 <= end < 24):
        raise ValueError("Hours out of range")
    if start >= end:
        raise ValueError("Start must be before end")
    return True
```

```python illustrative
# tests/test_ranges.py
import pytest
from ranges import validate_range

def test_validate_range_ok():
    assert validate_range((9, 17)) is True

def test_validate_range_rejects_invalid():
    with pytest.raises(ValueError):
        validate_range((20, 8))
```

---

## تمارين موجّهة (مع مهام TODO)
1. **6-1 · إحداثيات غير قابلة للتغيير**
   ```python todo
   locations = [
       ("HQ", (41.0, 2.0)),
       ("DataCenter", (40.4, -3.7)),
   ]
   # TODO 1: iterate and print name + lat/lon
   # TODO 2: try to modify a coordinate to see the exception
   # TODO 3: create a dict that uses coordinates as keys
   ```
   *تلميح*: التقط الاستثناء واشرح لماذا يحمي عدم قابلية التغيير البيانات.

2. **6-2 · النطاقات الزمنية**
   ```python todo
   ranges = [(9, 12), (13, 17)]
   # TODO 1: write total_hours(ranges) that sums each interval
   # TODO 2: validate that no range is reversed
   # TODO 3: add a test for the reversed range
   ```
   *تلميح*: أعد استخدام `validate_range` أو أنشئ دالة مساعدة مشابهة.

3. **6-3 · استخدام namedtuple للمقاييس**
   ```python todo
   from collections import namedtuple
   Point = namedtuple("Point", ["x", "y", "label"])
   samples = [Point(1, 2, "ok"), Point(3, 5, "alert")]
   # TODO 1: count how many samples have label "alert"
   # TODO 2: convert each namedtuple into dict using _asdict()
   # TODO 3: create a test that confirms Point is immutable
   ```
   *تلميح*: توقّع `pytest.raises(AttributeError)` عند محاولة إعادة تعيين `samples[0].x`.

---

## أخطاء شائعة
- **نسيان الفاصلة في الصف ذي العنصر الواحد**: `(42)` عدد صحيح؛ استخدم `(42,)`.
- **محاولة تعديل صف**: يؤدي ذلك إلى `TypeError`. حوّله إلى قائمة إذا كنت تحتاج حقاً إلى تغييرات.
- **عدم توثيق ترتيب القيم المعادة**: يتسبب ذلك في أخطاء خفية عند تبديل القيم.
- **استخدام صفوف ضخمة**: إذا احتجت إلى حقول كثيرة، ففكّر في أصناف البيانات أو كائن أكثر تعبيراً.

---

## حلول مشروحة
1. **الإحداثيات غير القابلة للتغيير**: إذا حاولت تنفيذ `locations[0][1][0] = 0` فستحصل على `TypeError`. وعندما تستخدم الإحداثيات مفاتيح، مثل `cities[locations[0][1]] = ...`، فإنك تضمن عدم إمكان إفساد الموقع.
2. **النطاقات الزمنية**: تجمع `total_hours` ناتج `end - start` بعد التحقق من كل صف؛ ويؤكد اختبار بالقيمة `(15, 10)` أن التحقق يعمل.
3. **namedtuple للمقاييس**: تحوّل `_asdict()` كل نقطة إلى قاموس من أجل التسلسل؛ ويحاول الاختبار تنفيذ `samples[0].x = 99` ويتوقع `AttributeError`، مثبتاً منع إعادة إسناد الحقل.

---

## نقطة تحقق وتقييم ذاتي
اشرح من دون تشغيل الشيفرة فاصلة `(42,)`، وفك التعبئة باستخدام `_`، والقيم المعادة المتعددة، والقاعدة التي تجعل الصف قابلاً للتجزئة. ثم حل تمريناً واختبر نتيجته ومدخلاً غير صالح.

- **مستعد**: تميّز البنية الثابتة عن عدم القابلية العميقة للتغيير، وتختار الصف أو القائمة أو `namedtuple` عن قصد.
- **على وشك الإتقان**: تستخدم الصفوف، لكنك ما زلت تحتاج إلى مرجع لفك التعبئة أو قابلية التجزئة.
- **راجع**: عد إلى الأقسام 1 و2 و4 ثم جرّب صفاً يحتوي قائمة.

## الخلاصة
تعطي الصفوف البيانات بنية خارجية ثابتة، وتعيد قيماً متعددة من دون أصناف معقدة، وتبني مفاتيح مركبة إذا كانت كل العناصر قابلة للتجزئة. وهي خفيفة، لكنها لا تجمّد الكائنات القابلة للتغيير الموجودة داخلها.

## تأمل ختامي
يمكنك الآن اختيار متى تستخدم الصفوف، أو `namedtuple`، لتوصيل المعنى وحماية بياناتك. سنواصل في الفصل التالي مع الطوابير الفعالة، حيث تساعدنا `collections.deque` على نمذجة سير العمل والنوافذ المنزلقة.

</div>
