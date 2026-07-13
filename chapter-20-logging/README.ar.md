<div dir="rtl">

# الفصل 20 · التسجيل والإعدادات

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سننفّذ التسجيل باستخدام المكتبة القياسية، ونضبط المستويات INFO وDEBUG وERROR، ونكتب السجلات إلى ملفات، ونتحكم في الإعدادات عبر الملفات ومتغيرات البيئة. وسنستخدم أيضًا `logging.config.dictConfig` ونخزّن إعداداته في ملف مثل JSON. وسنشير اختياريًا إلى YAML.

## مسار التعلّم
1. **لماذا نسجّل الأحداث؟**
2. **الإعداد الأساسي باستخدام `logging.basicConfig`**.
3. **المستويات والمسجّلات المسماة**.
4. **Handlers وformatters للملف والطرفية**.
5. **تحميل الإعداد من ملفات باستخدام `dictConfig`**.
6. **ربط التسجيل بمتغيرات البيئة**.

## أهداف التعلّم
- إصدار رسائل سجل بمستويات مختلفة للتشخيص والمراقبة.
- ضبط تنسيق المخرجات ووجهاتها، مثل الطرفية والملف.
- تغيير المستويات حسب البيئة، مثل التطوير والإنتاج.
- مركزة الإعدادات داخل ملف.

## لماذا يهم هذا؟
السجلات هي الصندوق الأسود لبرنامجك؛ فهي تخبرك بما حدث في الإنتاج. إعدادها جيدًا منذ البداية يوفر ساعات من التشخيص لاحقًا.

### مغامرة صغيرة
السجلات تشبه دفتر المحقق. إذا دوّنت كل دليل، مثل الوقت والمكان ودرجة الأهمية، استطعت إعادة بناء القصة في اليوم التالي. ومن دون الدفتر تعتمد على الذاكرة، فتصبح الألغاز مستحيلة الحل.

## المتطلبات المسبقة
الفصول السابقة الموصى بها: 13–16.
استخدم CPython 3.11+ في بيئة محلية مؤقتة, وأبقِ البيانات والأسرار والخدمات بعيدًا عن الأنظمة الحقيقية.

---

## 1. الإعداد الأساسي

```python runnable
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("Iniciando app")
logging.warning("API lenta")
```

- يتحكم `level` في الرسائل التي تظهر.
- يتحكم `format` في شكلها.

### الفرق بين `print` و`logging` في جملة واحدة
- تُستخدم `print` من أجل «عرض شيء».
- تُستخدم `logging` من أجل «ترك أدلة» يمكن ترشيحها حسب المستوى أو كتابتها إلى ملف وغير ذلك.

---

## 2. المسجّلات المسماة

```python illustrative
logger = logging.getLogger("pedidos")
logger.setLevel(logging.DEBUG)
logger.debug("Detalle interno")
```

- استخدم مسجّلًا لكل وحدة كي تستطيع ترشيح الرسائل بدقة.

---

## 3. المعالجات والملفات

```python illustrative
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
file_handler = logging.FileHandler("app.log")
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
console.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(console)
logger.addHandler(file_handler)
logger.info("Listo")
```

- يمكنك إرسال الرسالة نفسها إلى عدة وجهات.

---

## 4. الإعداد باستخدام قاموس

```python runnable
import logging.config
CONFIG = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG",
        },
    },
    "formatters": {
        "default": {
            "format": "%(levelname)s %(name)s %(message)s"
        }
    },
    "loggers": {
        "app": {
            "handlers": ["console"],
            "level": "INFO",
        }
    }
}
logging.config.dictConfig(CONFIG)
logger = logging.getLogger("app")
logger.info("Configurado por dict")
```

### تحميل إعداد JSON بأمان
```python illustrative
import json
import logging.config
from pathlib import Path

def apply_json_logging_config(path):
    try:
        with Path(path).open(encoding="utf-8") as fh:
            config = json.load(fh)
        logging.config.dictConfig(config)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(f"Invalid logging configuration: {path}") from exc
```

### تدوير محدود للملفات
```python illustrative
from logging.handlers import RotatingFileHandler

rotating = RotatingFileHandler(
    "app.log",
    maxBytes=1_000_000,
    backupCount=3,
    encoding="utf-8",
)
logger.addHandler(rotating)
```

- يناسب هذا الأسلوب تحميل الإعداد من JSON أو YAML.

---

## 5. الإعداد والبيئات

```python illustrative
import os
nivel = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=nivel)
```

- يتيح لك هذا زيادة التفاصيل أو تقليلها من دون تغيير الشيفرة.

تحدٍّ سريع: غيّر `LOG_LEVEL` ولاحظ ظهور رسائل أكثر أو أقل.
```bash illustrative
# macOS/Linux
LOG_LEVEL=DEBUG python tu_script.py
# Windows PowerShell
$env:LOG_LEVEL="DEBUG"; python tu_script.py
```

---

## تمارين موجّهة (مع TODO)
1. **20-1 · مسجّل لكل وحدة**
   ```python todo
   # TODO 1: create one logger per module (dominio, servicios)
   # TODO 2: show different levels
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

2. **20-2 · معالج ملف**
   ```python todo
   # TODO 1: write logs into app.log with rotation (use logging.handlers.RotatingFileHandler)
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

3. **20-3 · إعداد من JSON بالمكتبة القياسية**
   ```python todo
   # TODO 1: save CONFIG into config.json
   # TODO 2: read the JSON with json.load and apply it with dictConfig
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

مستوى إضافي اختياري: يتطلب تنفيذ الفكرة نفسها باستخدام YAML تثبيت `pyyaml`.

---

## أخطاء شائعة
- استدعاء `basicConfig` عدة مرات؛ إذ لا يكون إلا للاستدعاء الأول أثر في العادة.
- تسجيل بيانات حساسة مثل الرموز وكلمات المرور.
- إغفال الطابع الزمني، مما يصعّب إعادة بناء تسلسل الأحداث.

---

## حلول مشروحة
1. **مسجّل لكل وحدة**: يمنحك `logging.getLogger(__name__)` في كل ملف تحكمًا دقيقًا.
2. **معالج ملف**: يحافظ `RotatingFileHandler` على أحجام ملفات معقولة وينشئ نسخًا احتياطية.
3. **إعداد JSON**: افتح `config.json` باستخدام `with`، ثم طبّق `json.load` و`dictConfig`، والتقط أخطاء الملف وJSON لاستخدام إعداد طرفية معروف.

---

## الخلاصة
أصبحت قادرًا على التحكم في مستويات التسجيل وإرسال السجلات إلى عدة وجهات عبر إعداد مركزي.

## نقطة تحقق ومعايير تقييم
- **الصحة**: تطابق النتيجة عقد الوحدة.
- **الوضوح**: تُفهم الأسماء والمسؤوليات من القراءة الأولى.
- **الأخطاء**: يُختبر مسار ناجح وحالة حدّية ومسار تعافٍ.
- **التحقق**: تعمل الأمثلة والتمارين في بيئة نظيفة.
- **الشرح**: تستطيع تبرير القرارات ومخاطرها.

## تأمل ختامي
يهيئك تعلّم التسجيل لمراقبة الخدمات الحقيقية. ابدأ ببساطة، ثم وسّع الإعداد مع نمو مشروعك.

</div>
