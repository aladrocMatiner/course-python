<div dir="rtl">

# الفصل 16 · البيئات والتبعيات والمشاريع القابلة لإعادة الإنتاج

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
ستُعد بيئات افتراضية (`venv`)، وتثبت التبعيات باستخدام `pip`، وتدير `requirements.txt` و`pyproject.toml`، وتتعلم تحميل متغيرات البيئة للإعداد الآمن. وسنتدرب بمشروع صغير يثبت `requests` ويستخدم ملف `.env`.

## مسار التعلم
1. **لماذا نعزل التبعيات؟**
2. **إنشاء `venv` وتنشيطها**.
3. **تثبيت الحزم باستخدام `pip`**.
4. **تثبيت الإصدارات (`requirements.txt`)**.
5. **أساسيات `pyproject.toml`**.
6. **متغيرات البيئة (`os.environ`) و`.env`**.

## أهداف التعلم
- إنشاء البيئات الافتراضية وتنشيطها على Windows وmacOS وLinux.
- تثبيت المكتبات وتثبيت إصداراتها لإعادة إنتاج المشاريع.
- تصدير التبعيات واستيرادها باستخدام `pip freeze`.
- تحميل الإعدادات الحساسة من متغيرات البيئة.

## لماذا يهم هذا؟
من دون بيئات معزولة، يمكن لمشروع أن يعطّل مشروعاً آخر. والتبعيات المضبوطة هي أساس العمل الجماعي الاحترافي.

### مغامرة صغيرة
فكّر في كل بيئة افتراضية كصندوق LEGO يحتوي على القطع الدقيقة لمشروع واحد. إذا مزجت قطع المجموعات كلها، يصبح بناء أي شيء فوضى. باستخدام `venv` تُبقي كل مجموعة منفصلة، وتستطيع دائماً إعادة بناء النموذج من دون فقدان القطع.

## المتطلبات المسبقة
الفصول السابقة الموصى بها: 15.
استخدم CPython 3.11+ في بيئة محلية مؤقتة, وأبقِ البيانات والأسرار والخدمات بعيدًا عن الأنظمة الحقيقية.

---

## 1. إنشاء `venv` وتنشيطها

```bash illustrative
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

- ستظهر `(.venv)` في طرفيتك لتبين أنك داخل البيئة.
- استخدم `deactivate` للخروج.

إذا التبس عليك أي `pip` تستخدم، فهذه الحيلة تعمل دائماً:
```bash illustrative
python -m pip install requests
```
وهي تضمن التثبيت في بايثون الذي تشغله.

---

## 2. تثبيت الحزم

```bash illustrative
pip install requests
python -c "import requests; print(requests.__version__)"
```

- لكل بيئة نسختها الخاصة من `pip`.

### `requirements.txt`
```bash illustrative
pip freeze > requirements.txt
git add requirements.txt
```

- للتثبيت على جهاز آخر: `pip install -r requirements.txt`.

---

## 3. `pyproject.toml` (اختياري لكنه حديث)

```toml illustrative
[project]
name = "mi-proyecto"
version = "0.1.0"
dependencies = [
  "requests>=2.31",
]
```

- تستخدم أدوات مثل `pip-tools` و`poetry` و`pdm` هذه الصيغة.

---

## 4. متغيرات البيئة

```python runnable
import os
API_KEY = os.environ.get("API_KEY", "dummy")
```

- لا تودع الأسرار في مستودعك.

### ملف `.env` باستخدام `python-dotenv`
```bash illustrative
pip install python-dotenv
```

```python illustrative
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.environ["API_KEY"]
```

- أنشئ ملف `.env` يحتوي على `API_KEY=value` وأضفه إلى `.gitignore`.

ملف `.gitignore` نموذجي:
```gitignore illustrative
.venv/
.env
__pycache__/
```

---

## تمارين موجّهة (مع مهام TODO)
1. **16-1 · إعداد البيئة**
   ```bash todo
   # TODO 1: create .venv and activate it
   # TODO 2: install requests and python-dotenv
   # TODO 3: generate requirements.txt
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

2. **16-2 · سكربت مضبوط بالإعدادات**
   ```python todo
   # TODO 1: create config.py that loads variables from .env
   # TODO 2: use os.environ to read API_KEY
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

3. **16-3 · ملف pyproject أدنى**
   ```text todo
   # TODO 1: create pyproject.toml with basic dependencies
   # TODO 2: document in README how to install
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.
   ملاحظة: هذا «مستوى إضافي». إذا كنت في البداية، فإن `requirements.txt` ممتاز بالفعل.

---

## أخطاء شائعة
- نسيان تنشيط البيئة قبل تثبيت الحزم.
- عدم إيداع `requirements.txt` وفقدان ضبط الإصدارات.
- إيداع ملفات `.env` المحتوية على أسرار؛ استخدم `.gitignore`.

---

## حلول مشروحة
1. **إعداد البيئة**: تجعل `python -m venv .venv` و`pip freeze > requirements.txt` المشروع قابلاً لإعادة الإنتاج.
2. **السكربت المضبوط بالإعدادات**: تتيح `load_dotenv()` لـ`os.environ` قراءة المتغيرات من الملفات المحلية.
3. **pyproject**: يساعد توثيق تعليمات التثبيت الفريق على اتباع الطريقة نفسها.

---

## الخلاصة
أصبحت تعرف كيفية إنشاء البيئات وتثبيت التبعيات والحفاظ على أمان الإعداد باستخدام متغيرات البيئة.

## نقطة تحقق ومعايير تقييم
- **الصحة**: تطابق النتيجة عقد الوحدة.
- **الوضوح**: تُفهم الأسماء والمسؤوليات من القراءة الأولى.
- **الأخطاء**: يُختبر مسار ناجح وحالة حدّية ومسار تعافٍ.
- **التحقق**: تعمل الأمثلة والتمارين في بيئة نظيفة.
- **الشرح**: تستطيع تبرير القرارات ومخاطرها.

## تأمل ختامي
تتيح لك هذه الأساسيات مشاركة المشاريع من دون عبارة «إنه يعمل على جهازي». استخدمها في كل مرة تبدأ فيها مستودعاً جديداً.

</div>
