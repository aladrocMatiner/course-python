<div dir="rtl">

# الفصل 5 · المجموعات والتفرّد والعضوية

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
سنستكشف المجموعات (`set` و`frozenset`) لإزالة تكرار البيانات، والتحقق من العضوية، ودمج التجميعات باستخدام عمليات «شبيهة بالرياضيات». وسنستخدم أمثلة تركّز على الصلاحيات والوسوم ومزامنة البيانات بين المصادر.

## مسار التعلم

- **المسار الأساسي · 40–55 دقيقة.** المتطلبات: الفصلان 3–4. اقرأ القسمين 1 و3 ثم أكمل التمرين 5-0. النتيجة: إزالة التكرار من بيانات مباشرة، وفحص العضوية، ومقارنة المجموعات باستخدام `|` و`&` و`-`. الدليل: يغطي الحل المشروح حالة عادية، وحدّ المجموعة الفارغة، وخطأ الفهرسة المقصود، وتعافياً ناجحاً. تنتهي عندما تستطيع شرح سبب عدم وجود الموضع `0` في set؛ تابع إلى الفصل 6 أو توقّف هنا بأمان.
- **المسار المتوسط · 45–60 دقيقة.** المتطلبات: نقطة التحقق الأساسية و[الفصل 10](../chapter-10-loops/README.ar.md). ادرس القسم 2 ومثالي الوسوم والمزامنة في القسم 4 والقسم 5؛ وأكمل 5-1 و5-2. النتيجة: إنشاء sets باستيعاب واختيار `frozenset` لمجموعة قابلة للتجزئة. الدليل: أعد تشغيل التمرينين بإدخال فارغ. هذا المسار اختياري قبل الفصل 6.
- **معاينة مهنية اختيارية · 45–60 دقيقة.** المتطلبات: المسار المتوسط مع [الدوال](../chapter-11-functions/README.ar.md) و[الاستثناءات](../chapter-14-exceptions/README.ar.md) و[الاختبارات](../chapter-18-testing/README.ar.md). ادرس التحقق من الصلاحيات والقسم 6 والتمرين 5-3. النتيجة: التحقق من كتالوج بدالة واستثناء مقصود ودليل pytest. يمكن تخطي هذه المعاينة ولا تعيق الفصل الأساسي التالي.

## أهداف التعلم
- بناء مجموعات من تجميعات أخرى وإزالة العناصر المكررة.
- التحقق من العضوية في زمن O(1) في المتوسط باستخدام `in`.
- تطبيق عمليات المجموعات لمقارنة تجميعات البيانات ودمجها.
- الاختيار بين `set` و`frozenset` وفقاً للحاجة إلى قابلية التغيير.
- كتابة اختبارات للمسار الناجح والحالات الطرفية، مثل المجموعات الفارغة وغياب التقاطع.

## المتطلبات المسبقة والمعاينات الاختيارية
ينبغي أن تكون مرتاحاً مع [القوائم](../chapter-03-lists/README.ar.md) و[القواميس](../chapter-04-dictionaries/README.ar.md). يستخدم المسار الأساسي قيماً مباشرة من set ودوال built-in مألوفة؛ ولا يتطلب تعريف دوال أو معالجة استثناءات أو typing أو pytest. تبقى الاستيعابات والدوال والاستثناءات والاختبارات معاينات اختيارية مرتبطة في المسارات أعلاه.

## لماذا يهم هذا؟
عند إدارة عناوين البريد الإلكتروني أو الأدوار أو الوسوم، تنشئ التكرارات أخطاء خفية. تحل المجموعات هذه المشكلة بصياغة مباشرة وفعالة. وهي ممتازة في تطوير الواجهات الخلفية للصلاحيات واكتشاف أوجه عدم الاتساق ومزامنة البيانات مع الأنظمة الأخرى.

### مغامرة صغيرة
تخيّل أنك تجمع بطاقات ولا تريد نسخاً مكررة. `set` هي الصندوق الذي يقول لك، إذا حاولت وضع البطاقة نفسها مرة أخرى: «هذه البطاقة موجودة عندي بالفعل». هذه هي الفكرة.

## توقّع قبل التشغيل
قبل المثال الأول، توقّع محتوى المجموعة ونتيجة اختبار العضوية. لا تتوقّع ترتيب التكرار الخام، لأن المجموعات لا توفر ترتيب عرض ثابتاً، ولذلك يرتّب المثال القيم للعرض فقط.

---

## 1. النموذج الذهني: تجميع بلا تكرارات

```python runnable
correos = ["noor@example.com", "frej@example.com", "noor@example.com"]
correos_unicos = set(correos)
print(sorted(correos_unicos))  # ['frej@example.com', 'noor@example.com']

print("noor@example.com" in correos_unicos)  # True
```

- لا تضمن المجموعات ترتيباً؛ فهي تركّز على العضوية.
- تحويل قائمة إلى مجموعة هو أسهل طريقة لإزالة التكرارات.

---

## 2. إنشاء المجموعات واستيعابها

**معاينة متوسطة اختيارية:** يستخدم هذا القسم `range` واستيعاب set، ويعلّمهما [الفصل 10](../chapter-10-loops/README.ar.md) بالترتيب. يمكن لمتعلم المسار الأساسي الانتقال مباشرة إلى القسم 3.

```python runnable
lenguajes = {"python", "go", "rust"}
otros = set(["python", "java"])  # desde iterable

cuadrados = {n**2 for n in range(5)}
print(sorted(cuadrados))
```

- استخدم `{}` مع عناصر لكتابة مجموعة حرفية. أما `{}` الفارغة فهي قاموس؛ استخدم `set()` لإنشاء مجموعة فارغة.
- يعمل استيعاب المجموعات مثل استيعاب القوائم، لكنه يزيل التكرارات تلقائياً.

---

## 3. عمليات المجموعات

```python runnable
permisos_admin = {"view", "edit", "delete"}
permisos_editor = {"view", "edit"}
permisos_guest = {"view"}

union = permisos_admin | permisos_guest           # {'view', 'edit', 'delete'}
interseccion = permisos_admin & permisos_editor   # {'view', 'edit'}
solo_admin = permisos_admin - permisos_editor     # {'delete'}
simetrica = permisos_admin ^ permisos_editor      # {'delete'}

print(permisos_guest <= permisos_editor)  # True: guest es subconjunto de editor
```

- يعني `|` الاتحاد، و`&` التقاطع، و`-` الفرق، و`^` الفرق المتماثل.
- استخدم `<=` أو `<` للتحقق مما إذا كانت مجموعة ما مجموعة جزئية من أخرى.

---

## 4. حالات عملية

### ضبط الوسوم
```python runnable
etiquetas_existentes = {"python", "django", "api"}
etiquetas_propuestas = {"python", "rest", "observability"}

nuevas = etiquetas_propuestas - etiquetas_existentes
print(f"Etiquetas a crear: {sorted(nuevas)}")
```

### مزامنة البيانات
```python runnable
local_users = {"noor", "frej", "taha"}
remote_users = {"frej", "taha", "grace"}

missing = remote_users - local_users
inactive = local_users - remote_users
```

### التحقق من الصلاحيات

**معاينة مهنية اختيارية:** يعرّف هذا المثال دالة ويطلق استثناءً. تخطّه في المسار الأساسي؛ يعلّم الفصلان [11](../chapter-11-functions/README.ar.md) و[14](../chapter-14-exceptions/README.ar.md) هاتين الأداتين أولاً.

```python runnable
def validate_permissions(assigned, allowed):
    extra = assigned - allowed
    if extra:
        raise ValueError(f"Invalid permissions: {extra}")
    return True
```

---

## 5. `frozenset` والمجموعات بوصفها مفاتيح
عندما تحتاج إلى مجموعة غير قابلة للتغيير، مثلاً لاستخدامها مفتاحاً في قاموس، فاستخدم `frozenset`.

هذا عمق متوسط مفيد، لكنه غير مطلوب لنقطة التحقق الأساسية.

```python runnable
segments = {
    frozenset({"ios", "premium"}): "Campaign A",
    frozenset({"android", "free"}): "Campaign B",
}

query = frozenset({"premium", "ios"})
print(segments.get(query))
```

- تتصرف `frozenset` مثل المجموعة، إلا أنك لا تستطيع إضافة عناصر إليها أو حذفها منها.
- وهي ممتازة لتمثيل توليفات فريدة من السمات.

---

## 6. التحقق والاختبارات

**معاينة مهنية اختيارية:** يجمع هذا القسم بين الدوال والاستثناءات وفحوص النوع وpytest. أكمل أولاً الفصول [11](../chapter-11-functions/README.ar.md) و[14](../chapter-14-exceptions/README.ar.md) و[18](../chapter-18-testing/README.ar.md)، أو انسخ النمط من دون اعتباره عملاً مطلوباً.

```python runnable
# permissions.py
VALID_PERMISSIONS = {"view", "edit", "delete"}

def normalize_permissions(permission_list):
    if not isinstance(permission_list, (list, set, tuple)):
        raise TypeError("permissions must be iterable")
    permissions = set(permission_list)
    invalid = permissions - VALID_PERMISSIONS
    if invalid:
        raise ValueError(f"Invalid permissions: {invalid}")
    return permissions
```

```python illustrative
# tests/test_permissions.py
import pytest
from permissions import normalize_permissions

def test_normalize_permissions_deduplicates():
    result = normalize_permissions(["view", "view", "edit"])
    assert result == {"view", "edit"}

def test_normalize_permissions_rejects_invalid():
    with pytest.raises(ValueError):
        normalize_permissions(["hack"])
```

---

## تمارين موجّهة (مع مهام TODO)
1. **5-0 · خريطة العضوية الأساسية**

   توقّع النتائج الأربع قبل كتابة الشيفرة. المجموعة الفارغة هي الحالة الحدّية.

   ```python todo
   skills = ["python", "python", "git"]
   required = {"python", "sql"}
   # TODO 1: create unique_skills from skills
   # TODO 2: print membership for "python"
   # TODO 3: print the shared and missing sets in sorted order
   # TODO 4: print the size of an empty set
   ```

   *تلميح*: استخدم `set(skills)` و`&` و`-` و`sorted(...)` و`len(set())`. لا تحتاج إلى حلقة أو تعريف دالة.

2. **5-1 · وسوم فريدة** *(متوسط)*
   ```python todo
   etiquetas = ["api", "python", "api", "monitoring"]
   # TODO 1: convert to a set
   # TODO 2: ask the user for a new tag and add it if it doesn't exist
   # TODO 3: print how many unique tags there are
   ```
   *تلميح*: استخدم `if nueva not in etiquetas_set` قبل الإضافة.

3. **5-2 · تقاطع المهارات** *(متوسط)*
   ```python todo
   backend = {"python", "django", "postgres"}
   frontend = {"javascript", "react", "django"}
   # TODO 1: compute shared skills
   # TODO 2: compute backend-only skills
   # TODO 3: create a message explaining the result
   ```
   *تلميح*: استخدم `backend & frontend` و`backend - frontend`.

4. **5-3 · التحقق من الأدوار** *(معاينة مهنية اختيارية)*
   ```python todo
   roles_permitidos = {"admin", "editor", "viewer"}
   asignados = {"admin", "auditor"}
   # TODO 1: write check_roles(asignados, permitidos)
   # TODO 2: the function must raise ValueError if it finds roles outside the catalog
   # TODO 3: add a test confirming empty sets are valid
   ```
   *تلميح*: أعد استخدام `extra = asignados - permitidos` و`pytest.raises`.

---

## أخطاء شائعة
- **محاولة فهرسة مجموعة**: ليس للمجموعات ترتيب أو مواضع. حوّلها إلى قائمة إذا احتجت إلى الفهارس.
- **توقع ترتيب حتمي**: يمكن أن يتغير ترتيب المجموعة بين عمليات التشغيل. لا تستخدم المجموعات لإخراج واجهة المستخدم من دون تحويل.
- **نسيان أن `{}` قاموس**: استخدم `set()` لإنشاء مجموعة فارغة.
- **مقارنة المراجع بدلاً من المحتوى**: استخدم عمليات المجموعات لاكتشاف الفروق بصورة تصريحية.

---

## حلول مشروحة

### الحل الأساسي 5-0

حوّل القائمة مرة واحدة أولاً. يحتفظ التقاطع بالقيم الموجودة في المجموعتين، ويحتفظ الفرق بالمتطلبات التي ما زالت ناقصة. توفر `set()` الحد الفارغ بلا حالة خاصة.

```python runnable
skills = ["python", "python", "git"]
unique_skills = set(skills)
required = {"python", "sql"}

print(sorted(unique_skills))
print("python" in unique_skills)
print(sorted(unique_skills & required))
print(sorted(required - unique_skills))
print(len(set()))
```

لاحظ `['git', 'python']` و`True` و`['python']` و`['sql']` و`0` بهذا الترتيب. يختفي التكرار وتبقى المجموعة الفارغة إدخالاً صالحاً.

لا تملك set مواضع ثابتة. يفهرس هذا المقطع مجموعة عمداً، لذا فالإشارة التشخيصية المستقرة هي `TypeError`:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
languages = {"python", "rust"}
print(languages[0])
```

تعافَ بالسؤال عن العضوية أو بالترتيب للعرض فقط:

```python runnable
languages = {"python", "rust"}
print("python" in languages)
print(sorted(languages))
```

تطبع الاستعادة `True` و`['python', 'rust']`؛ ولا تدّعي أن set نفسها اكتسبت ترتيباً.

### ملاحظات حلول المسارات الاختيارية

1. **الوسوم الفريدة**: تزيل `etiquetas_unicas = set(etiquetas)` التكرارات؛ ثم احسب العدد باستخدام `len(etiquetas_unicas)`.
2. **تقاطع المهارات**: استخدم `compartidas = backend & frontend` و`solo_backend = backend - frontend`، واشرح النتائج بسلسلة f.
3. **التحقق من الأدوار**: احسب `extra = asignados - permitidos` وأطلق `ValueError` إذا لم تكن فارغة؛ وأضف اختباراً يؤكد أن `check_roles(set(), permitidos)` تعيد `True`.

---

## نقطة تحقق وتقييم ذاتي
أكمل 5-0، وتوقّع قبل كل تشغيل، وقارن الحالات العادية والفارغة والخطأ والتعافي بالحل. ثم اشرح بصوت عالٍ سبب فشل `languages[0]` بينما يكون `"python" in languages` ذا معنى.

- **الصحة:** تختفي التكرارات، وتطابق العضوية والتقاطع والفرق والحد الفارغ النتائج المذكورة.
- **الوضوح:** تصف الأسماء المجموعتين، ولا يُستخدم الترتيب إلا للعرض.
- **معالجة الخطأ:** تحدد `TypeError` بوصفها الإشارة المستقرة وتتعافى بلا فهرسة أو اعتماد على ترتيب التكرار.
- **التحقق:** تشغّل فعلياً مقاطع الحالة العادية والحد والخطأ المتوقع والتعافي باستخدام CPython 3.11+.
- **الشرح:** تميّز بين العضوية والموضع وتشرح عملية واحدة بكلماتك.

**انتقل عندما تتحقق النقاط الخمس.** تابع إلى الفصل 6؛ يبقى المساران المتوسط والمهني اختياريين. إذا نقصت نقطة، فعد إلى القسمين 1 و3 وأعد 5-0 باستخدام `skills = []`.

## الخلاصة
تستطيع باستخدام المجموعات إزالة تكرار البيانات، والتحقق من العضوية، ودمج التجميعات بعمليات تصريحية. وهذا يبسّط إدارة الصلاحيات والوسوم والمزامنة في أي نظام واجهة خلفية.

## تأمل ختامي
يمكنك الآن اكتشاف أوجه عدم الاتساق سريعاً بعمليات المجموعات، والتحقق من كتالوجات كاملة قبل إرسالها إلى طبقة أخرى. سنستكشف بعد ذلك الصفوف لتمثيل السجلات غير القابلة للتغيير والقيم المتعددة المعادة من الدوال.

</div>
