<div dir="rtl">

# الفصل 15 · الوحدات والحزم وتنظيم الشيفرة

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
ستتعلم تقسيم المشروع إلى ملفات ومجلدات، واستيراد الدوال والأصناف، وإنشاء حزم قابلة لإعادة الاستخدام، وتجنب الاستيرادات الدائرية. وسنحاكي تطبيقاً صغيراً بوحدات `dominio` و`servicios` و`cli` كي ترى كيفية اتصالها.

## مسار التعلم
1. **النموذج الذهني**: كل ملف `.py` هو وحدة واحدة.
2. **الاستيرادات الأساسية**: `import` و`from ... import ...`.
3. **المجلدات كحزم**: `__init__.py` والاستيرادات النسبية.
4. **بنية قابلة للتثبيت `src/<package>`**.
5. **تجنب دورات الاستيراد**.
6. **تحزيم خفيف** باستخدام `if __name__ == "__main__"`.

## أهداف التعلم
- تنظيم الشيفرة في وحدات مترابطة منطقياً.
- استيراد الدوال والأصناف من ملفات أخرى بدلاً من تكرار المنطق.
- إنشاء حزم باستخدام `__init__.py` وفهم الاستيرادات النسبية.
- اكتشاف الاستيرادات الدائرية وإصلاحها.
- إعداد وحدة نظيفة تكون «نقطة الدخول الرئيسية».
- بناء حزمة وتثبيتها واستيرادها من خارج مجلد المصدر.

## لماذا يهم هذا؟
لا تتسع المشاريع الحقيقية في ملف واحد. ويسهّل فصل المسؤوليات الاختبار وإعادة الاستخدام والتعاون.

### مغامرة صغيرة
تخيّل أن فرقاً مختلفة تبني لعبتك المفضلة: الشخصيات والمراحل والموسيقى. لو كان كل شيء في ملف واحد لاستحال التعاون. تشبه الوحدات غرفاً مرتبة في منزل؛ يعرف الجميع مكان عملهم، ويسهل العثور عليه لاحقاً.

### كيفية التدرب على هذا الفصل (ببساطة شديدة)
1. أنشئ ملفين: `saludos.py` و`app.py` في المجلد نفسه.
2. شغّل `python app.py`.
3. إذا حصلت على خطأ، فاقرأ اسم الخطأ ورقم السطر؛ هذا طبيعي أثناء التعلم.

## المتطلبات المسبقة
- الدوال والأصناف والاستيرادات من المكتبة القياسية وأساسيات التنقل في الطرفية.
- بيئة محلية بإصدار CPython 3.11 أو أحدث، مع إذن بإنشاء مجلد مؤقت للمشروع.

## توقّع قبل التشغيل
قبل استيراد الوحدة الأولى، توقّع الملف الذي يوفر `hola` والمجلد الذي يجب أن يعثر عليه Python. بعد تشغيل المثال، افحص مسار الوحدة المستوردة وقارنه بتوقّعك.

---

## 1. الوحدات الأساسية
`saludos.py`
```python runnable
def hola(nombre):
    return f"Hola {nombre}!"
```

`app.py`
```python illustrative
import saludos
print(saludos.hola("Taha"))
```

الناتج المتوقع:
```text illustrative
Hola Taha!
```

تحدٍّ سريع: استبدل `"Taha"` باسمك وشغّل البرنامج مرة أخرى.

### `from ... import ...`
```python illustrative
from saludos import hola
print(hola("Frej"))
```

- تجنب `import *`؛ فهو يصعّب معرفة مصدر كل اسم.

---

## 2. الحزم
البنية:
```text illustrative
mi_app/
    __init__.py
    dominio.py
    servicios.py
main.py
```

`mi_app/dominio.py`
```python runnable
class Pedido:
    def __init__(self, id, total):
        self.id = id
        self.total = total
```

`mi_app/servicios.py`
```python illustrative
from .dominio import Pedido

def procesar_pedido(pedido: Pedido):
    # Ejemplo: aplicar un descuento del 10%
    pedido.total = pedido.total * 0.9
    return pedido
```

`main.py`
```python illustrative
from mi_app.dominio import Pedido
from mi_app.servicios import procesar_pedido

pedido = Pedido(1, 100)
pedido = procesar_pedido(pedido)
print(pedido.total)
```

التشغيل:
```bash illustrative
python main.py
```

الناتج المتوقع:
```text illustrative
90.0
```

- تعني `.` استيراداً نسبياً من الحزمة نفسها.
- يمكن أن يكون `__init__.py` فارغاً؛ فهو يخبر بايثون أن «هذا المجلد حزمة».

---

## 3. مستوى إضافي: تخطيط `src` قابل للتثبيت (اختياري)
يمكن للمبتدئ تجاوز هذا القسم. في تخطيط `src` الحقيقي يكون `src/` حاوية فقط، وتوجد الحزمة القابلة للاستيراد تحته بمستوى. الحزمة هنا هي `mi_app`، لذلك نستورد `mi_app` لا `src`.

```text illustrative
project/
├── pyproject.toml
├── src/
│   └── mi_app/
│       ├── __init__.py
│       ├── domain.py
│       └── cli.py
└── tests/
```

يخبر `pyproject.toml` أداة البناء أن تكتشف الحزم تحت `src`:

```toml illustrative
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "course-mi-app"
version = "0.1.0"
requires-python = ">=3.11"

[tool.setuptools.packages.find]
where = ["src"]
```

### البناء والتثبيت والتحقق من مكان آخر
ثبّت المشروع في بيئة افتراضية جديدة، ثم غيّر مجلد عمل العملية عمداً قبل الاستيراد. يثبت ذلك استخدام التوزيعة المثبتة بدلاً من استيراد نسخة المصدر مصادفة:

```bash illustrative
# macOS/Linux (outside the checkout):
python -m venv /tmp/course-mi-app-venv
source /tmp/course-mi-app-venv/bin/activate
# Windows PowerShell alternative:
# python -m venv "$env:TEMP\course-mi-app-venv"
# & "$env:TEMP\course-mi-app-venv\Scripts\Activate.ps1"
# Run the remaining commands from project/
python -m pip install .
python -m unittest discover -s tests -v
python -c "import os, tempfile; os.chdir(tempfile.mkdtemp()); import mi_app; print(mi_app.__name__)"
```

يقع مسار البيئة خارج نسخة المصدر عمداً؛ عطّل البيئة واحذفها بعد التمرين. يستخدم `pip install .` عزل PEP 517 وقد يحتاج إلى جلب `setuptools>=68` مع المتطلب `wheel` الذي يعلنه backend من index أو cache مجهزة مسبقاً. لمختبر بلا شبكة، جهّز مسبقاً wheels متوافقة ومراجعة لمدخلي البناء كليهما. لا تستخدم `--no-build-isolation` إلا إذا كان backend ومتطلبات بنائه مثبتة وتحققت من إصداراتها؛ فهذا البديل لا يثبت build معزولاً.

يجب أن يطبع الاستيراد `mi_app`. توجد نسخة كاملة في [مثال `src` القابل للتثبيت للفصل 15](examples/src-layout/). عند الفشل تحقق من `python -m pip --version`، وأعد التثبيت في البيئة الصحيحة، وتأكد من `src/mi_app/__init__.py`. لا تضف نسخة المصدر إلى `PYTHONPATH` لأن ذلك يخفي خطأ التحزيم.

يمكن لصائن الكتاب تشغيل `python -B chapter-15-modulos/examples/src-layout/tools/verify_artifact.py` من جذر المستودع. يبني المتحقق نسخة مؤقتة بعزل PEP 517، ويفحص محتوى wheel وبياناتها الوصفية، ثم يثبت تلك wheel بعينها في بيئة ثانية ويشغّل `pip check` وentry point المثبتة والاختبار واستيراداً من مجلد أجنبي قبل حذف الآثار المؤقتة. في مختبر بلا شبكة، مرّر `--wheelhouse PATH` وفيه توزيعتان متوافقتان ومراجعتان من `setuptools>=68` و`wheel`؛ عدم توفير أي منهما فشل في المتطلب السابق وليس بناءً معزولاً ناجحاً.

---

## 4. تجنب الاستيرادات الدائرية

```python illustrative
# dominio.py
from servicios import descuentos  # ⚠️ if servicios imports dominio → cycle
```

إذا حدث ذلك فليس «خطأك»؛ إنها مشكلة طبيعية عندما تكبر المشاريع.

الحلول:
- انقل المنطق المشترك إلى وحدة مستقلة.
- استخدم الاستيرادات المحلية داخل الدوال لكسر الدورة:
```python illustrative
def calcular(total):
    # Local import: only happens when the function is called
    from servicios.descuentos import aplicar_descuento
    return aplicar_descuento(total)
```
(الفكرة أن `aplicar_descuento` تعيش في مسار مثل `servicios/descuentos.py`.)

---

## 5. نقطة الدخول

```python runnable
# cli.py
def main():
    print("Hola! Soy tu CLI")

if __name__ == "__main__":
    main()
```

- يتيح لك ذلك تشغيل `python cli.py` أو استيراد `main` في الاختبارات من دون تنفيذ تلقائي.

---

## تمارين موجّهة (مع مهام TODO)
1. **15-1 · فصل المجال عن الخدمات**
   ```python todo
   # TODO 1: create src/mi_app/dominio.py with class Producto
   # TODO 2: create src/mi_app/precios.py and use Producto
   # TODO 3: add pyproject.toml and install the distribution in a clean venv
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.
   إضافة: أضف التابع `aplicar_descuento(porcentaje)` إلى `Producto`.
   تلميح: `src` ليست الحزمة؛ الحزمة هي `mi_app`.

2. **15-2 · أداة سطر أوامر معيارية**
   ```python todo
   # TODO 1: create src/mi_app/cli.py that imports functions from servicios
   # TODO 2: after installation, run python -m mi_app.cli to validate the import path
   ```
   تلميح: إذا حصلت على `ModuleNotFoundError`، فتأكد من التشغيل من المجلد الصحيح.

3. **15-3 · إصلاح دورة استيراد**
   ```python todo
   # TODO 1: create a small artificial cycle and fix it by moving functions to utils
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.
   حالة طرفية: اكتب اختباراً يستورد الوحدتين ليتأكد من زوال الدورة.

---

## أخطاء شائعة
- استيرادات نسبية خاطئة (`from .. import` من دون `__init__.py`).
- تكرار الشيفرة عبر الوحدات بدلاً من استيرادها.
- التشغيل من مجلدات مختلفة وكسر المسارات؛ استخدم `python -m`.
- وضع `__init__.py` مباشرة تحت `src/` واستيراد `src`؛ يجب أن تعيش الحزمة الحقيقية تحت `src/<package>/` وأن تُثبّت.

---

## حلول مشروحة
1. **المجال مقابل الخدمات**: ضع الوحدات تحت `src/mi_app/`، واضبط اكتشافها في `pyproject.toml`، وثبّتها في بيئة جديدة، ثم تحقق من `import mi_app` من مجلد مؤقت.
2. **أداة سطر الأوامر المعيارية**: لا تفعل `mi_app/cli.py` سوى التنسيق، ويعيش منطق العمل في `servicios`. يشغّل `python -m mi_app.cli` بعد التثبيت مسار استيراد الحزمة، ويبقى سهل الاختبار.
3. **إصلاح الدورة**: تزيل عملية نقل الدوال المشتركة إلى `utils` التبعيات الدائرية وتوضح الطبقات.

---

## الخلاصة
يحافظ تقسيم الشيفرة إلى وحدات وحزم على تنظيم مشروعك. ويمكنك الآن استيراد ما تحتاج إليه فقط وإنشاء نقاط دخول نظيفة.

## نقطة تحقق ومعايير تقييم
- **الصحة**: تُثبّت التوزيعة وتُستورد الحزمة الحقيقية من خارج جذر المشروع.
- **الوضوح**: تُفهم الأسماء والمسؤوليات من القراءة الأولى.
- **الأخطاء**: يُختبر مسار ناجح وحالة حدّية ومسار تعافٍ.
- **التحقق**: تعمل الوحدة والاستيراد من مجلد عمل آخر في عملية جديدة.
- **الشرح**: تستطيع تبرير القرارات ومخاطرها.

## تأمل ختامي
اسأل نفسك دائماً: «أين ينبغي أن تعيش هذه القطعة من المنطق؟» تهيئك الوحدات الواضحة لمشاريع أكبر وأطر عمل مثل Django.

</div>
