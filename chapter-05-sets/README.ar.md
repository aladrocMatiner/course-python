<div dir="rtl">

# الفصل 5 · المجموعات والتفرّد والعضوية

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
سنستكشف المجموعات (`set` و`frozenset`) لإزالة تكرار البيانات، والتحقق من العضوية، ودمج التجميعات باستخدام عمليات «شبيهة بالرياضيات». وسنستخدم أمثلة تركّز على الصلاحيات والوسوم ومزامنة البيانات بين المصادر.

## مسار التعلم
1. **الفكرة الأساسية**: تجميع لا يحتوي على تكرارات.
2. **الإنشاء والاستعلام**: البناء من القوائم، واستيعاب المجموعات، وقابلية التغيير.
3. **العمليات الرئيسية**: الاتحاد والتقاطع والفرق والمجموعات الجزئية.
4. **حالات واقعية**: الصلاحيات والوسوم والمزامنة بين المصادر.
5. **`frozenset` واستخدام المجموعات كمفاتيح**: عندما تحتاج إلى عدم القابلية للتغيير.
6. **التحقق والاختبارات**: التأكد من ثبات قواعد الوصول وإزالة التكرار.

## أهداف التعلم
- بناء مجموعات من تجميعات أخرى وإزالة العناصر المكررة.
- التحقق من العضوية في زمن O(1) في المتوسط باستخدام `in`.
- تطبيق عمليات المجموعات لمقارنة تجميعات البيانات ودمجها.
- الاختيار بين `set` و`frozenset` وفقاً للحاجة إلى قابلية التغيير.
- كتابة اختبارات للمسار الناجح والحالات الطرفية، مثل المجموعات الفارغة وغياب التقاطع.

## المتطلبات المسبقة والمعاينات الاختيارية
ينبغي أن تكون مرتاحاً مع [القوائم](../chapter-03-lists/README.ar.md) و[القواميس](../chapter-04-dictionaries/README.ar.md). تظهر الدوال والاستثناءات وpytest هنا بوصفها أنماطاً قابلة لإعادة الاستخدام فقط؛ وستدرسها بالتفصيل في [الفصل 11](../chapter-11-functions/README.ar.md) و[الفصل 14](../chapter-14-exceptions/README.ar.md) و[الفصل 18](../chapter-18-testing/README.ar.md).

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
1. **5-1 · وسوم فريدة**
   ```python todo
   etiquetas = ["api", "python", "api", "monitoring"]
   # TODO 1: convert to a set
   # TODO 2: ask the user for a new tag and add it if it doesn't exist
   # TODO 3: print how many unique tags there are
   ```
   *تلميح*: استخدم `if nueva not in etiquetas_set` قبل الإضافة.

2. **5-2 · تقاطع المهارات**
   ```python todo
   backend = {"python", "django", "postgres"}
   frontend = {"javascript", "react", "django"}
   # TODO 1: compute shared skills
   # TODO 2: compute backend-only skills
   # TODO 3: create a message explaining the result
   ```
   *تلميح*: استخدم `backend & frontend` و`backend - frontend`.

3. **5-3 · التحقق من الأدوار**
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
1. **الوسوم الفريدة**: تزيل `etiquetas_unicas = set(etiquetas)` التكرارات؛ ثم احسب العدد باستخدام `len(etiquetas_unicas)`.
2. **تقاطع المهارات**: استخدم `compartidas = backend & frontend` و`solo_backend = backend - frontend`، واشرح النتائج بسلسلة f.
3. **التحقق من الأدوار**: احسب `extra = asignados - permitidos` وأطلق `ValueError` إذا لم تكن فارغة؛ وأضف اختباراً يؤكد أن `check_roles(set(), permitidos)` تعيد `True`.

---

## نقطة تحقق وتقييم ذاتي
من دون تشغيل الشيفرة، اشرح لماذا يكون اختبار العضوية O(1) في المتوسط، ومتى تحتاج إلى `frozenset`، وما الذي تعيده كل من `|` و`&` و`-`. ثم حل تمريناً واختبر حالة عادية وحالة مجموعة فارغة.

- **مستعد**: تختار العملية المناسبة ولا تعتمد على الترتيب وتبرر الاختبارين.
- **على وشك الإتقان**: تعمل الشيفرة، لكنك ما زلت تحتاج إلى مرجع لاختيار العملية أو الحالة الطرفية.
- **راجع**: عد إلى الأقسام 1 و3 و5 ثم حاول ببيانات أخرى.

## الخلاصة
تستطيع باستخدام المجموعات إزالة تكرار البيانات، والتحقق من العضوية، ودمج التجميعات بعمليات تصريحية. وهذا يبسّط إدارة الصلاحيات والوسوم والمزامنة في أي نظام واجهة خلفية.

## تأمل ختامي
يمكنك الآن اكتشاف أوجه عدم الاتساق سريعاً بعمليات المجموعات، والتحقق من كتالوجات كاملة قبل إرسالها إلى طبقة أخرى. سنستكشف بعد ذلك الصفوف لتمثيل السجلات غير القابلة للتغيير والقيم المتعددة المعادة من الدوال.

</div>
