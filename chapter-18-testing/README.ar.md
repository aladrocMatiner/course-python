<div dir="rtl">

# الفصل 18 · الاختبار باستخدام pytest: اجعل أفكارك آمنة

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنجهّز بيئة اختبار باستخدام `pytest`، ونتعلّم كتابة اختبارات واضحة، واستخدام التركيبات (fixtures)، وتمرير عدة حالات بالـ parametrization، وقياس تغطية أساسية. ستشاهد أمثلة لدوال وأصناف وشيفرة يُفترض أن تطلق استثناءات.

## مسار التعلّم
1. **لماذا نختبر؟**
2. **التثبيت وبنية المجلدات**.
3. **الاختبار الأول وتشغيل الاختبارات**.
4. **التركيبات (fixtures)**.
5. **تمرير عدة حالات (parametrization)**.
6. **نظرة سريعة إلى التغطية باستخدام `--cov`**.

## أهداف التعلّم
- إعداد `pytest` في مشاريعك.
- كتابة اختبارات للدوال النقية وللآثار الجانبية المضبوطة.
- إعادة استخدام بيانات الاختبار عبر fixtures.
- جمع قائمة من الحالات في اختبار واحد باستخدام parametrization.
- قراءة تقارير التغطية الأساسية.

## لماذا يهم هذا؟
تتيح لك الاختبارات تعديل الشيفرة بثقة، وتكتشف الأخطاء قبل وصولها إلى بيئة الإنتاج.

### مغامرة صغيرة
يسبق افتتاح المسرحية تدريبٌ بالملابس الكاملة. تخيّل كل اختبار تدريبًا صغيرًا تتحقق فيه من أن كل شخصية تقول جملتها الصحيحة. وعندما يصل الجمهور، أي المستخدمون، تؤدي دالتك دورها بسلاسة ومن دون هلع في اللحظة الأخيرة.

### كيف تستخدم هذا الفصل؟ ثلاث خطوات
1. أنشئ ملفات الأمثلة كما تظهر تمامًا.
2. شغّل `pytest` وابحث عن كلمة `passed`.
3. غيّر رقمًا عمدًا كي ترى `failed`. هذا طبيعي؛ فأنت تتعلّم اكتشاف الأخطاء.

## المتطلبات المسبقة
الفصول السابقة الموصى بها: 11, 12, 14, 16.
استخدم CPython 3.11+ في بيئة محلية مؤقتة, وأبقِ البيانات والأسرار والخدمات بعيدًا عن الأنظمة الحقيقية.

---

## 1. التثبيت والبنية

```bash illustrative
pip install pytest pytest-cov
mkdir tests
```

- ضع الاختبارات في `tests/` وسمِّ الملفات وفق النمط `test_*.py`.

---

## 2. الاختبار الأول
الملف `math_utils.py`:
```python runnable
def sumar(a, b):
    return a + b

def dividir(a, b):
    if b == 0:
        raise ZeroDivisionError("No se puede dividir entre cero")
    return a / b
```

الملف `tests/test_math_utils.py`:
```python illustrative
from math_utils import sumar, dividir

def test_sumar():
    assert sumar(2, 3) == 5

def test_dividir():
    assert dividir(10, 2) == 5
```

اقرأ `assert` بهذا المعنى: «تأكّد أن هذا صحيح». يفشل الاختبار إذا لم يكن الشرط صحيحًا.

شغّل:
```bash illustrative
pytest
```

ولناتج أقصر ومناسب للمبتدئين:
```bash illustrative
pytest -q
```

عندما يعمل كل شيء سترى ناتجًا شبيهًا بـ `2 passed`.

---

## 3. التركيبات (fixtures)

```python illustrative
import pytest

@pytest.fixture
def sample_pedidos():
    return [10, 20, 30]

def test_promedio(sample_pedidos):
    promedio = sum(sample_pedidos) / len(sample_pedidos)
    assert promedio == 20
```

- الـ fixtures دوال توفّر بيانات اختبار جاهزة للاستخدام.

---

## 4. تمرير عدة حالات (parametrization)

```python illustrative
import pytest
from math_utils import dividir

@pytest.mark.parametrize(
    "a,b,resultado",
    [ (10, 2, 5), (9, 3, 3), (5, 2, 2.5) ]
)
def test_dividir(a, b, resultado):
    assert dividir(a, b) == resultado
```

- يعمل الاختبار نفسه عدة مرات بمدخلات مختلفة.
- تخيّله «قائمة تدريبات»: النص نفسه، لكن بممثلين مختلفين.

---

## 5. الاستثناءات و`pytest.raises`

```python illustrative
from math_utils import dividir
import pytest

def test_dividir_por_cero():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)
```

---

## 6. التغطية

```bash illustrative
pytest --cov=. --cov-report=term-missing
```

- يعرض الأمر الأسطر التي لم تنفّذها اختباراتك.

---

## تمارين موجّهة (مع TODO)
1. **18-1 · fixture قابلة لإعادة الاستخدام**
   ```python todo
   # TODO 1: create fixture db_tmp that uses tmp_path to simulate a file
   # TODO 2: use it in two tests
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

2. **18-2 · تمرير حالات التحقق**
   ```python todo
   # TODO 1: create test validacion_payload with multiple valid/invalid inputs
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

3. **18-3 · التغطية**
   ```bash todo
   # TODO 1: run pytest --cov and read the report
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

---

## أخطاء شائعة
- نسيان البادئة `test_`، فلا يكتشف pytest الملف.
- خلط شيفرة الإنتاج بشيفرة الاختبار؛ أبقهما في مجلدين منفصلين.
- إنشاء fixtures ذات آثار جانبية لا تُعاد إلى حالتها الأصلية؛ استخدم `yield` للتنظيف.

---

## حلول مشروحة
1. **fixture باسم db_tmp**: ينشئ التعبير `tmp_path / "db.json"` مسارًا مؤقتًا من دون تلويث المستودع.
2. **Parametrize**: تقلل `pytest.mark.parametrize` التكرار وتدفعك إلى التفكير في الحالات الحدّية.
3. **التغطية**: راجع الأسطر الناقصة وقرّر ما إذا كانت تحتاج إلى اختبارات إضافية.

---

## الخلاصة
تمنحك `pytest` حلقة تغذية راجعة سريعة للتحقق من كل وحدة. ومع fixtures وparametrization تصبح اختباراتك معبّرة وسهلة الصيانة.

## نقطة تحقق ومعايير تقييم
- **الصحة**: تطابق النتيجة عقد الوحدة.
- **الوضوح**: تُفهم الأسماء والمسؤوليات من القراءة الأولى.
- **الأخطاء**: يُختبر مسار ناجح وحالة حدّية ومسار تعافٍ.
- **التحقق**: تعمل الأمثلة والتمارين في بيئة نظيفة.
- **الشرح**: تستطيع تبرير القرارات ومخاطرها.

## تأمل ختامي
اجعل الاختبار عادة؛ حتى البرامج النصية الصغيرة تستفيد من التحقق من سلوكها قبل دمجها في مشاريع أكبر.

</div>
