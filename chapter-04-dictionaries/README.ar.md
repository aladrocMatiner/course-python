<div dir="rtl">

# الفصل 4 · القواميس (بيانات المفتاح والقيمة)

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
ستتعلم تمثيل المعلومات المهيكلة باستخدام القواميس (`dict`). سنعمل على ملفات تعريف المستخدمين، وكائنات الإعداد، والاستجابات الشبيهة بـJSON والمعتادة في تطوير الواجهات الخلفية. وستتدرّب على إنشاء القواميس وتحديثها ودمجها والتحقق منها قبل عرضها عبر واجهة API أو تخزينها في قاعدة بيانات.

## مسار التعلم
1. **النموذج الذهني**: القواميس خرائط تربط المفاتيح بالقيم.
2. **الإنشاء والوصول**: القراءة الآمنة (`[]` مقابل `get`) والتنسيق الواضح.
3. **التحديث والحذف**: `.update` و`del` و`pop` والقيم الافتراضية.
4. **التكرار**: `keys` و`values` و`items` واستيعاب القواميس.
5. **البُنى المتداخلة**: قوائم من القواميس وقواميس داخل قواميس.
6. **التحقق والاختبارات**: التأكد من احتواء الحمولات على الحقول المطلوبة.

## أهداف التعلم
- تعريف قواميس تمثل كيانات حقيقية، مثل المستخدمين والطلبات والإعدادات.
- قراءة المفاتيح وتحديثها بأمان، بالوصول الصارم أو المتسامح.
- في المسار الاحترافي الاختياري، التكرار على القواميس وبناء بُنى مشتقة.
- دمج القواميس والتعامل مع المفاتيح المتداخلة من دون فقدان الاتساق.
- في المسار الاحترافي الاختياري، كتابة اختبارات تتحقق من وجود المفاتيح المطلوبة أو غيابها.

## المتطلبات السابقة والمسارات
- **المتطلب السابق:** أكمل checkpoint [الفصل 3](../chapter-03-lists/README.ar.md). لا يحتاج المسار الأساسي إلا إلى مبادئ القوائم والمتغيرات.
- **المسار الأساسي · 45–60 دقيقة:** الأقسام 1–3 مع تجاوز معاينة دالة التنسيق الاختيارية، والتمرين 4-1 ونقطة التحقق. النتيجة: إنشاء قاموس وقراءته وتحديثه ودمجه وتنظيفه بجمل مباشرة؛ لا يتطلب دوالاً.
- **المسار المتوسط · 25–35 دقيقة:** البُنى المتداخلة والتمرين 4-2. النتيجة: فحص الحقول الخارجية المفقودة باستخدام `get` قبل الفهرسة.
- **معاينة احترافية اختيارية · 35–45 دقيقة:** القسمان 4 و6 والتمرين 4-3. تستبق [الشروط](../chapter-08-conditionals/README.ar.md) و[الحلقات](../chapter-10-loops/README.ar.md) و[الدوال](../chapter-11-functions/README.ar.md) و[الاستثناءات](../chapter-14-exceptions/README.ar.md) و[pytest](../chapter-18-testing/README.ar.md). انسخ الأمثلة الكاملة أو تجاوزها من دون تعطيل checkpoint الأساسي.

## لماذا يهم هذا؟
القواميس هي أساس JSON، الصيغة التي تستخدمها واجهات API الحديثة لإرسال البيانات. يعني إتقان `dict` القدرة على معالجة الحمولات واستجابات HTTP والمعاملات وكائنات الإعداد بسلاسة. كما يهيئك لتسلسل البيانات وإلغاء تسلسلها بين بايثون والأنظمة الأخرى.

### مغامرة صغيرة
القاموس شبيه بجهات الاتصال في هاتفك: تبحث عن اسم، وهو المفتاح، فتحصل على معلومة، وهي القيمة. إذا كنت تعرف كيفية عمل جهات الاتصال، فقد فهمت الفكرة بالفعل. أما السحر فهو أن برنامجك يستطيع العثور على الأشياء «فوراً» من دون مسح قائمة كاملة.

## توقّع قبل التشغيل
في مثال `user` الأول، توقّع نتيجة الوصول الصارم إلى `"username"`، والوصول المتسامح إلى `"timezone"` المفقود، والوصول الصارم إلى المفتاح المفقود نفسه. شغّل الأولين فقط واشرح كيف توفر `get` مسار تعافٍ من `KeyError`.

---

## 1. النموذج الذهني: القواميس بوصفها خرائط
فكّر في القاموس كدليل هاتف: تبحث عن مفتاح، أي الاسم، وتسترجع قيمة، أي الرقم.

```python runnable
user = {
    "username": "noor",
    "email": "noor@example.com",
    "roles": ["admin", "editor"],
}

print(user["username"])  # strict access
print(user.get("timezone", "UTC"))  # tolerant access with a default
```

الوصول الصارم إلى مفتاح غائب دليل مفيد. تثير الكتلة التالية `KeyError` عمداً:

<!-- bookcheck: expect-error="KeyError" -->
```python expected-error
user = {"username": "noor"}
print(user["timezone"])
```

تعافَ بالوصول المتسامح وقيمة افتراضية صريحة:

```python runnable
user = {"username": "noor"}
print(user.get("timezone", "UTC"))
```

- يجب أن تكون المفاتيح **hashable**، أي أسماء بحث مستقرة لبايثون. استخدم النصوص أو الأعداد في المسار الأساسي. مفاتيح tuple معاينة اختيارية بعد [الفصل 6](../chapter-06-tuples/README.ar.md)، ولا تعمل إلا إذا كانت كل قيمة داخل tuple قابلة للـhash أيضًا. أما القيم فيمكن أن تكون أي كائن.
- استخدم `get` عندما لا تكون واثقاً من وجود المفتاح؛ فهي تتجنب `KeyError` وتتيح لك تعريف قيم افتراضية معقولة.

---

## 2. إنشاء القيم وقراءتها وتطبيعها

```python runnable
profile = {}
profile["first_name"] = "Grace"
profile["last_name"] = "Hopper"
profile.setdefault("language", "Python")  # only sets if missing

full_name = f"{profile['first_name']} {profile['last_name']}"
print(full_name)
```

- تمنع `setdefault` الكتابة فوق قيمة مضبوطة مسبقاً.
- عند بناء السلاسل النصية، تأكد من وجود المفاتيح أو استخدم `get` مع قيم افتراضية.

### دالة للتنسيق
**معاينة اختيارية للدوال:** تُدرّس `def` و`return` في [الفصل 11](../chapter-11-functions/README.ar.md). انسخ النمط كاملًا إن أفادك أو تجاوزه من دون التأثير في نقطة التحقق الأساسية.

```python illustrative
def format_profile(data):
    first = data.get("first_name", "Unknown")
    last = data.get("last_name", "")
    return f"{first} {last}".strip()
```

---

## 3. تحديث القواميس ودمجها وتنظيفها

```python runnable
base_config = {"timeout": 5, "retries": 3}
user_config = {"timeout": 10, "region": "eu-west"}

final_config = base_config | user_config  # Python 3.9+: creates a new dict
base_config.update({"logging": True})      # modifies in place

print(final_config)
print(base_config)
```

```python runnable
feature_flags = {"beta": True, "legacy": False}
legacy = feature_flags.pop("legacy")  # returns the removed value
print(legacy)

del feature_flags["beta"]
print(feature_flags)
```

- استخدم `|` أو `|=` لدمج الإعدادات من دون كتابة حلقات.
- تحذف `pop` قيمة وتعيدها، وهو أمر مفيد عند نقل البيانات إلى مكان آخر.
- تحذف `del` القيمة من دون إعادتها، وهي مثالية حين لا تحتاج إلى القيمة المحذوفة.

---

## 4. التكرار على القواميس وبناء بيانات مشتقة

```python runnable
permissions = {"alice": "admin", "bob": "editor", "taha": "viewer"}

for user, role in permissions.items():
    print(f"{user} → {role}")

roles = {role for role in permissions.values()}  # set comprehension
print(roles)

greetings = {user: f"Hello, {user.title()}" for user in permissions.keys()}
print(greetings)
```

- تمنحك `items()` أزواج المفتاح والقيمة.
- يُعد استيعاب القواميس (`{key: value for ...}`) طريقة واضحة لبناء خرائط جديدة.

---

## 5. البُنى المتداخلة

```python runnable
users = {
    "noor": {"email": "noor@example.com", "active": True},
    "frej": {"email": "frej@example.com", "active": False},
}

for username, details in users.items():
    status = "active" if details.get("active") else "inactive"
    print(f"{username}: {status}")
```

```python runnable
# Dictionaries inside lists
api_response = {
    "results": [
        {"id": 1, "status": "ok"},
        {"id": 2, "status": "failed", "error": "timeout"},
    ],
    "meta": {"count": 2}
}

failed = [item for item in api_response["results"] if item["status"] != "ok"]
print(failed)
```

- تحقق دائماً من وجود المفاتيح قبل فهرستها؛ فقد تحذفها واجهات API الخارجية.
- بالنسبة إلى البُنى الأعمق، فكّر في دوال مساعدة تغلّف الوصول المتداخل.

---

## 6. التحقق والاختبارات

```python runnable
# profiles.py
def validate_profile(data):
    required_fields = {"username", "email"}
    missing = required_fields - data.keys()
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")
    if "@" not in data["email"]:
        raise ValueError("Invalid email")
    return True
```

```python illustrative
# tests/test_profiles.py
import pytest
from profiles import validate_profile

def test_validate_profile_success():
    payload = {"username": "noor", "email": "noor@example.com"}
    assert validate_profile(payload) is True

def test_validate_profile_detects_missing_fields():
    with pytest.raises(ValueError) as exc:
        validate_profile({"username": "noor"})
    assert "email" in str(exc.value)
```

تضمن الاختبارات امتلاك القاموس للحد الأدنى من الحقول المطلوبة قبل دخوله إلى عرض أو أداة تسلسل.

---

## تمارين موجّهة (مع مهام TODO)
1. **4-1 · ملف تعريف عام**
   ```python todo
   profile = {"username": "alba", "skills": ["python", "django"]}
   # TODO 1: add first_name and last_name fields
   # TODO 2: print a formatted message using get with defaults
   # TODO 3: add a "links" field that is another dict (github, linkedin)
   ```
   *تلميح*: استخدم `setdefault` لتجنب الكتابة فوق البيانات الموجودة.

2. **4-2 · إعداد مدمج**
   ```python todo
   default = {"timeout": 5, "cache": True}
   user = {"timeout": 10, "debug": False}
   # TODO 1: create merge_config(base, custom) -> dict
   # TODO 2: make sure base is not modified (use a copy)
   # TODO 3: write a test that confirms base stays the same after merge
   ```
   *تلميح*: استخدم `base | custom` أو `copy()` ثم `update()`.

3. **4-3 · تدقيق الحقول**
   ```python todo
   record = {"id": 1, "status": "ok", "duration_ms": 120}
   # TODO 1: write requires_fields(record, required_fields)
   # TODO 2: the function must return a tuple (valid, missing)
   # TODO 3: add a test that confirms optional extra fields are allowed
   ```
   *تلميح*: أعد استخدام عمليات المجموعات (`required_fields - record.keys()`).

---

## أخطاء شائعة
- **افتراض وجود مفتاح** ← يؤدي إلى `KeyError`. استخدم `get` أو تحقق أولاً.
- **تعديل القاموس نفسه في مواضع متعددة** ← يؤدي إلى آثار جانبية. أنشئ نسخاً (`dict.copy()` أو `|`).
- **الخلط بين القوائم والقواميس** ← فهرسة القاموس بالأعداد أو العكس.
- **عدم تطبيع المفاتيح** ← يؤدي اختلاف حالة الأحرف إلى تكرارات.

---

## حلول مشروحة
1. **ملف التعريف العام**: تملأ `profile.setdefault("first_name", "")` البيانات من دون فقدان ما لديك؛ وابنِ الرسائل باستخدام `profile.get("first_name", "Unknown")` لتجنب الأخطاء.
2. **الإعداد المدمج**: ابنِ `merged = base | custom`، أو استخدم `merged = base.copy(); merged.update(custom)`، ثم اختبر أن `base` يحتفظ بقيمته الأصلية.
3. **تدقيق الحقول**: تمنحك `missing = required - record.keys()`، واختيارياً `extra = record.keys() - required`، رؤية واضحة لما هو مفقود أو زائد كي تنشئ رسائل خطأ أفضل.

---

## Checkpoint وتقييم ذاتي

### المهمة الأساسية 4-0

أكمل البداية باستخدام عمليات قاموس مباشرة فقط:

```python todo
profile = {"username": "alba", "email": "alba@example.test"}
# TODO 1: update email and add one preference without changing profile
# TODO 2: merge profile and preference into a new dictionary
# TODO 3: remove the preference from the merged dictionary and print both
```

*تلميح*: استخدم الإسناد بالمفتاح و`|` و`pop` و`get`؛ ولا تحتاج إلى دالة أو حلقة أو set أو tuple أو معالجة استثناء أو إطار اختبار.

### الحل المشروح

تحقق من المسار العادي للتحديث والدمج والحذف:

```python runnable
profile = {"username": "alba", "email": "alba@example.test"}
profile["email"] = "new@example.test"
preferences = {"theme": "dark"}
merged = profile | preferences
removed = merged.pop("theme")
print(profile)
print(merged)
print(removed)
```

تحقق من حد القاموس الفارغ بالوصول المتسامح:

```python runnable
empty_profile = {}
print(empty_profile.get("timezone", "UTC"))
print(empty_profile)
```

احتفظ بثلاثة أدلة: المخرجات العادية، والقيمة الافتراضية للحد الفارغ، و`KeyError` المتوقع السابق متبوعًا مباشرة بالتعافي القابل للتشغيل باستخدام `get`. تأمل في جملة: متى يكون الوصول الصارم `[]` أفضل من `get` المتسامحة؟

شغّل المهمة 4-0 وقارن القاموس الأصلي بالنسخة المدمجة. ثم شغّل الوصول المقصود إلى مفتاح غائب مرة واحدة، واقرأ `KeyError`، وتعافَ بمثال `get` المجاور. لا تستخدم دالة ولا حلقة ولا معالجة استثناء ولا set ولا tuple ولا إطار اختبار.

امنح نفسك نقطة لكل معيار:
- **المسار العادي:** ينتج التحديث والدمج و`pop` القيم المتوقعة.
- **الحد:** يعيد الوصول المتسامح إلى القاموس الفارغ `"UTC"` من دون تغييره.
- **التعافي:** يتبع `KeyError` المتوقع مباشرة وصول `get` عامل.
- **التحقق:** يثبت طبع الأصل والنسخة العمليات التي غيّرت البيانات.
- **الشرح:** تبرر `[]` الصارمة مقابل `get` المتسامحة لمفتاح محدد.

يكتمل المسار الأساسي عند 4/5 أو 5/5. وإلا فأعد المهمة 4-0 وزوج الخطأ/التعافي. الدوال والتكرار والسجلات الخارجية المتداخلة ومساعدات التحقق والاستثناءات وpytest أدلة لمسارات لاحقة.

---

## الخلاصة
تدرّبت على تعريف القواميس وقراءتها ودمجها والتحقق منها، وعلى التكرار فوقها والتعامل مع البُنى المتداخلة. وأصبحت تعرف متى تستخدم `[]` بدلاً من `get`، وكيف تنقل المفاتيح باستخدام `pop`، وكيف تتحقق من اكتمال حمولة قبل معالجتها.

## تأمل ختامي
تعتمد كل واجهة API تبنيها على القواميس لتمثيل البيانات. يمكنك الآن تنظيمها بعناية، وحماية نفسك من المفاتيح المفقودة، وكتابة اختبارات تمنع التراجعات. سندرس بعد ذلك `set`، وهي مثالية لإزالة التكرارات والاستدلال على العضوية عندما تكبر المجموعات.

</div>
