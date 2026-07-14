<div dir="rtl">

# الفصل 8 · الشروط والتعبيرات الثلاثية والتفكير المنطقي

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
سنتقن اتخاذ القرارات في بايثون: `if/elif/else` والمعاملات المنطقية والتعبيرات الثلاثية وأنماط التحقق الشائعة في الواجهات الخلفية. ستتعلم اختيار مسارات مختلفة وفقاً لبيانات واجهة API، واختصار القرارات البسيطة في سطر واحد، وترجمة قواعد العالم الحقيقي إلى شيفرة.

## مسار التعلم
1. **السياق الذهني**: لماذا تمثل القرارات الجسر بين البيانات والإجراءات.
2. **`if` الأساسية**: الصياغة والمسافة البادئة والشروط المنطقية.
3. **`elif` و`else` والسلاسل الشرطية**: اختيار مسار حصري واحد.
4. **المعاملات المنطقية (`and` و`or` و`not`)**: دمج القواعد مثل منطق القضايا.
5. **المعامل الثلاثي**: قرارات قصيرة لا تتغير فيها إلا قيمة واحدة.
6. **التحقق والاختبارات**: التأكد من ثبات القواعد قبل عرض النتائج.

## أهداف التعلم
- كتابة كتل `if/elif/else` واضحة ومتوافقة مع قواعد العمل.
- دمج المقارنات باستخدام `and` و`or` و`not` مع فهم منطقها.
- استخدام التعبيرات الثلاثية بصورة مقروءة للشروط البسيطة.
- فهم القيم «الصادقة» و«الكاذبة» وكيف تؤثر في القرارات.
- إنشاء دوال تحقق واختبار المسارات الناجحة ومسارات الأخطاء.

## المتطلبات السابقة والمسارات
ينبغي أن تعرف [المتغيرات والقيم المنطقية](../chapter-02-variables/README.ar.md) و[التجميعات](../chapter-03-lists/README.ar.md) الأساسية.

- **المسار الأساسي · 45–60 دقيقة:** ادرس الأقسام 1–3 والتمرين 8-0 والتعافي ونقطة التحقق الأساسية. النتيجة: اختيار فرع واحد بالضبط، ودمج شروط بسيطة، وشرح القيمة الحدية. الجمل المباشرة والمخرجات المطبوعة هما الدليل؛ لا يتطلب دوالاً ولا pytest.
- **المسار المتوسط · 30–40 دقيقة:** أضف التعبير الثلاثي وتحويلات المنطق في القسمين 4–5. توقف حين تستطيع إعادة كتابة شرط من دون تغيير جدول حقيقته.
- **المسار المهني الاختياري · 45–60 دقيقة:** ادرس `match` ودوال التحقق والاختبارات. إنها معاينة لـ[الدوال](../chapter-11-functions/README.ar.md) و[pytest](../chapter-18-testing/README.ar.md)؛ انسخ الأمثلة الكاملة أو عد بعد هذين الفصلين.

## لماذا يهم هذا؟
تحتاج كل واجهة API أو استمارة أو سكربت أتمتة إلى اتخاذ قرارات: السماح بالوصول أو منعه، وحساب الأسعار، واختيار الرسائل، وغير ذلك. الشروط هي أساس منطق الواجهات الخلفية. وإتقانها يمنع الأخطاء الصامتة ويساعدك على التعبير عن قواعد العمل من دون غموض.

### مغامرة صغيرة
هذه «اختر مغامرتك بنفسك» ولكن في الشيفرة: اختر الباب A فيحدث شيء، أو اختر الباب B فيحدث شيء آخر. تعلّم `if/else` هو تعلّم بناء قصص تفاعلية.

## توقّع قبل التشغيل
قبل المثال الأول، توقّع أي فرع يعمل مع `amount = 120`، ثم غيّر قيمة الحد فقط على الورق. اكتب الشرط الدقيق الذي يجعل كل فرع قابلاً للوصول قبل التنفيذ.

---

## 1. النموذج الذهني: ترجمة القواعد إلى شيفرة
فكّر في الشرط كتفرع: «إذا حدث A، فنفّذ B؛ وإلا فنفّذ C». والمفتاح هو التعبير عن القاعدة كشرط منطقي.

```python runnable
# payment.py
amount = 120

if amount > 100:
    print("Apply 10% discount")
else:
    print("No discount")
```

- يجب أن يُقيّم الشرط إلى `True` أو `False`.
- استخدم مسافة بادئة من أربع مسافات، وفق PEP 8، للكتل.

---

## 2. سلاسل if/elif/else الشرطية

```python runnable
# shipping.py
weight = 3.2

if weight <= 1:
    rate = 5
elif weight <= 5:
    rate = 10
else:
    rate = 20

print(f"Rate: ${rate}")
```

- تعني `elif`: «إذا كانت الشروط السابقة خاطئة، لكن هذا الشرط صحيح».
- تُنفّذ كتلة واحدة فقط.

### القيم الصادقة والكاذبة
```python runnable
user = ""  # empty string counts as False
if user:
    print("User present")
else:
    print("Missing user")
```

تُعد قيم مثل `0` و`""` و`[]` و`{}` و`None` كاذبة، وتُعد كل القيم الأخرى صادقة. يفيد ذلك في التحقق السريع من الاستمارات.

---

## 3. المعاملات المنطقية (`and` و`or` و`not`)

```python runnable
age = 20
country = "ES"

if age >= 18 and country == "ES":
    print("Can sign the contract")

if age < 18 or country != "ES":
    print("We need additional authorization")

if not country:
    print("You must provide a country")
```

- تتطلب `and` صحة الشرطين معاً.
- تكون `or` صحيحة إذا صح شرط واحد على الأقل.
- تعكس `not` النتيجة.

### التقييم قصير الدارة
يتوقف بايثون عن التقييم بمجرد أن يعرف النتيجة. لن تنفذ `condicion and expensive_call()` الدالة `expensive_call` إلا إذا كانت `condicion` تساوي `True`. استخدم ذلك للتحقق من الشروط المسبقة قبل العمل المكلف.

---

## 4. المعامل الثلاثي: قرارات قصيرة
استخدم المعامل الثلاثي عندما تكون النتيجة قيمة بسيطة.

```python runnable
# ternary.py
score = 75
status = "passed" if score >= 60 else "needs review"
print(status)
```

- الصياغة هي: `value_if_true if condition else value_if_false`.
- استخدمه للتعيينات أو القيم المعادة القصيرة، لا للمنطق الطويل.

### مثال في نقاط النهاية
```python runnable
from time import time

def status_response(success: bool) -> dict:
    return {
        "status": "ok" if success else "error",
        "timestamp": time()
    }
```

---

## 5. التفكير بمنطق القضايا
يمكننا إعادة كتابة القواعد باستخدام جداول الصدق:

- لا تكون `A and B` صحيحة إلا حين تكونان صحيحتين معاً.
- لا تكون `A or B` خاطئة إلا حين تكونان خاطئتين معاً.
- تعكس `not A` قيمة A.

### تبسيط التعبيرات
```python illustrative
# Before
if (not user_active) or (user_active and user_banned):
    block = True
else:
    block = False

# After (using logic)
block = (not user_active) or user_banned
```

تساعد قوانين دي مورغان على تقليل الشروط المتداخلة:
- تكافئ `not (A and B)` العبارة `not A or not B`.
- تكافئ `not (A or B)` العبارة `not A and not B`.

يحسّن ذلك سهولة القراءة ويقلل الأخطاء.

### ملاحظة: `match` و`case` (بايثون 3.10 فأحدث)
قدّم بايثون 3.10 *مطابقة الأنماط الهيكلية*، وهي بديل حديث لـ`switch/case` التقليدية.

```python runnable
def order_status(order):
    match order:
        case {"status": "pending", "total": total} if total > 100:
            return "manual review due to high total"
        case {"status": "pending"}:
            return "queued"
        case {"status": "shipped"}:
            return "shipped"
        case _:
            return "unknown"
```

- تستطيع `match` مقارنة البُنى، مثل القواميس والصفوف والكائنات، ويمكن أن تتضمن *حراساً* (`if total > 100`).
- وهي متاحة في بايثون 3.10 والإصدارات الأحدث. إذا كنت تستخدم إصداراً أقدم، فالتزم بـ`if/elif/else`.

---

## 6. التحقق والاختبارات

```python runnable
# discounts.py
def calculate_discount(total, vip_customer):
    if total < 0:
        raise ValueError("total cannot be negative")
    if total >= 100 or vip_customer:
        return total * 0.1
    return 0
```

```python illustrative
# tests/test_discounts.py
import pytest
from discounts import calculate_discount

def test_discount_for_high_total():
    assert calculate_discount(150, vip_customer=False) == 15

def test_discount_for_vip_customer():
    assert calculate_discount(50, vip_customer=True) == 5

def test_no_discount():
    assert calculate_discount(50, vip_customer=False) == 0

def test_negative_total():
    with pytest.raises(ValueError):
        calculate_discount(-10, vip_customer=False)
```

- ترى ثلاثة «مسارات ناجحة» وحالة خطأ واحدة.
- تجبرك الاختبارات على التفكير في شروط الحدود.

---

## تدريب أساسي وتعافٍ

### 8-0 · قرار صريح واحد

شغّل الحالة العادية، ثم غيّر `age` إلى `17` وتوقع فرع الحد قبل إعادة التشغيل:

```python runnable
age = 18
has_permission = True

if age >= 18 and has_permission:
    print("Access granted")
else:
    print("Access denied")
```

من الأخطاء الشائعة الإسناد داخل الشرط. الكتلة التالية غير صالحة عمداً؛ `SyntaxError` هو التشخيص المتوقع:

<!-- bookcheck: expect-error="SyntaxError" -->
```python expected-error
age = 18
if age = 18:
    print("Access granted")
```

تعافَ بالمقارنة باستخدام `==`، ثم اشرح لماذا يمكن الوصول إلى الفرع:

```python runnable
age = 18
if age == 18:
    print("Access granted")
```

دليل الإكمال هو المخرجان العاديان المرصودان وجملة تشرح `>=` عند الحد. توقف هنا في المسار الأساسي؛ التمارين الباقية توسعات.

## تمارين موجّهة (مع مهام TODO)
1. **8-1 · مصنّف درجات الحرارة**
   ```python todo
   temperature = 27
   # TODO 1: print "Cold" if temp < 15, "Warm" if 15-25, "Hot" if >25
   # TODO 2: use a ternary to set a "hydrate" message when temperature > 30
   ```
   *تلميح*: ادمج `if/elif/else` مع تعبير ثلاثي مخزّن في متغير مستقل.

2. **8-2 · التحكم في الوصول**
   ```python todo
   user = {"active": True, "role": "editor"}
   # TODO 1: allow access if user is active AND role is admin OR editor
   # TODO 2: print "Needs review" if the role is not recognized
   # TODO 3: add a test confirming inactive users are blocked
   ```
   *تلميح*: استخدم `if user["active"] and user["role"] in {"admin", "editor"}`.

3. **8-3 · التحقق المنطقي باستخدام دي مورغان**
   ```python todo
   payload = {"email": "noor@example.com", "terms": True}
   # TODO 1: write a function is_valid(payload)
   # TODO 2: it must return False if email is missing OR terms is False
   # TODO 3: simplify the expression using `not` and sets
   ```
   *تلميح*: تمثل `if not payload.get("email") or not payload.get("terms"):` الصيغة المباشرة.

---

## أخطاء شائعة
- **نسيان المسافة البادئة** ← يؤدي إلى `IndentationError`. استخدم أربع مسافات لكل كتلة.
- **الخلط بين `=` و`==`** ← تسند `=` قيمة، بينما تقارن `==` بين قيمتين.
- **الشروط الطويلة من دون أقواس** ← تؤدي إلى التباس الأولوية. اجمع الشروط بـ`()` عند مزج `and` و`or`.
- **الإفراط في استخدام التعبيرات الثلاثية** ← إذا صار السطر صعب القراءة، فعُد إلى `if/else` التقليدية.

---

## حلول مشروحة
1. **مصنّف درجات الحرارة**: تعرض `if temperature < 15: ... elif temperature <= 25: ... else: ...` ثم `message = "hydrate" if temperature > 30 else ""` الأسلوبين.
2. **التحكم في الوصول**: استخدم `if user["active"] and user["role"] in {...}` للسماح؛ وتعامل مع المستخدم غير النشط في `else`، ومع الأدوار المجهولة في `elif` إضافية. يبني الاختبار حمولة غير نشطة ويتوقع المنع.
3. **التحقق المنطقي**: تمثل `return bool(payload.get("email")) and payload.get("terms")` صيغة مختصرة. ويساعد دي مورغان حين تحتاج إلى الشرط «المعاكس» لرسائل الخطأ: `if not payload.get("email") or not payload.get("terms"):`.

---

## نقطة تحقق وتقييم ذاتي
أنشئ برنامج `if/elif/else` مباشراً لثلاث فئات من الدرجات. شغّل قيمة عادية والحدين الدقيقين، ثم أعد إنتاج الخطأ بين `=` و`==` وصححه. لا تستخدم دالة ولا إطار اختبار.

امنح نقطة لكل معيار: **الفروع** (يعمل فرع واحد فقط)، و**الحدود** (كلاهما صحيح)، و**المنطق** (تشرح `and`/`or`)، و**التعافي** (يتبع `SyntaxError` المتوقع كود عامل)، و**الدليل** (تسجل التوقعات والمخرجات). تعني 4/5 أنك تستطيع المتابعة؛ وإلا فراجع الأقسام 1–3. تبقى التعبيرات الثلاثية ودي مورغان و`match` والدوال وpytest أدلة اختيارية.

## الخلاصة
تعلّمت التعبير عن القواعد باستخدام `if/elif/else`، وربط الشروط بالمعاملات المنطقية، واستخدام التعبيرات الثلاثية للقرارات البسيطة، والتفكير بمنطق القضايا لتبسيط الشيفرة. كما تحققت من القواعد بالاختبارات.

## تأمل ختامي
يمر كل قرار في تطبيقك عبر شرط في مكان ما. يمكنك الآن كتابة الشروط بثقة، وتقليل التعقيد بالمنطق الصوري، واستخدام التعبيرات الثلاثية حين تزيد الوضوح. سننتقل بعد ذلك إلى الحلقات لتكرار الإجراءات استناداً إلى الشروط نفسها.

</div>
