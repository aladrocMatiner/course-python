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
- الملفات والاستثناءات والوحدات وJSON ومتغيرات البيئة من الفصول 13–16.
- مجلد محلي مؤقت، كي لا تكتب file handlers في سجل مهم للمشروع.

## توقّع قبل التشغيل
قبل مثال التسجيل الأول، توقّع الرسائل التي ستتجاوز المستوى المضبوط والوجهة التي ستستقبلها. شغّل المثال، وقارن السجلات الملاحظة بتوقّعك، ثم حدد الإعداد المسؤول عن أي فرق.

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

هذا الحرفي إعداد تملكه التطبيق. يستطيع `dictConfig` حلّ الأصناف القابلة للاستيراد ومفتاح المصنع الخاص `"()"`، لذلك لا تمرر إليه مباشرة قاموسًا اعتباطيًا من طلب أو تنزيل أو ملف يتحكم فيه المتعلم.

### تحميل إعداد JSON مملوك للتطبيق عبر قائمة سماح
```python illustrative
import json
import logging.config
from pathlib import Path

ALLOWED_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

def build_logging_config(settings):
    if not isinstance(settings, dict) or set(settings) != {"level"}:
        raise ValueError("logging settings must contain only 'level'")
    level = settings["level"]
    if not isinstance(level, str) or level not in ALLOWED_LEVELS:
        raise ValueError("unsupported logging level")
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": level,
            }
        },
        "formatters": {
            "default": {"format": "%(levelname)s %(name)s %(message)s"}
        },
        "root": {"handlers": ["console"], "level": level},
    }

def apply_application_logging_settings(path):
    with Path(path).open(encoding="utf-8") as fh:
        settings = json.load(fh)
    logging.config.dictConfig(build_logging_config(settings))
```

لا يحتوي الملف إلا على `{"level": "INFO"}`. تتحقق الشيفرة من هذا المخطط الصغير وتبني القاموس الكامل بنفسها. تلتقط حدود التطبيق أخطاء `OSError` و`JSONDecodeError` و`ValueError` المتوقعة، وتبلغ عن المسار المملوك للتطبيق، وتعود إلى إعداد طرفية معروف. إذا جاء الإعداد من جهة غير موثوقة فارفضه، أو انسخ فقط القيم الأولية المسموح بها صراحة إلى إعداد تبنيه بنفسك؛ ولا تمرر حقول `class` أو `()` أو handler أو formatter أو filter.

تثبت [اختبارات إعداد التسجيل الموثوق المرافقة](trusted_logging.py) أن المستوى المسموح يعمل وأن القواميس التي تحتوي حقول مصنع أو handlers تُرفض. من `chapter-20-logging/` شغّل `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

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

3. **20-3 · إعدادات موثوقة من JSON بالمكتبة القياسية**
   ```python todo
   # TODO 1: save only {"level": "INFO"} in an application-owned config.json
   # TODO 2: validate the allowlisted schema
   # TODO 3: construct the full dict in code and apply it with dictConfig
   ```
   *تلميح*: ارفض المفاتيح الإضافية، وخصوصًا `"()"` و`"class"`؛ والتقط أخطاء الملف وJSON والقيمة المتوقعة عند حدود التطبيق، واحتفظ بإعداد طرفية معروف.

مستوى إضافي اختياري: يتطلب تنفيذ الفكرة نفسها باستخدام YAML تثبيت `pyyaml`.

---

## أخطاء شائعة
- استدعاء `basicConfig` عدة مرات؛ إذ لا يكون إلا للاستدعاء الأول أثر في العادة.
- تسجيل بيانات حساسة مثل الرموز وكلمات المرور.
- إغفال الطابع الزمني، مما يصعّب إعادة بناء تسلسل الأحداث.
- اعتبار JSON الاعتباطي إعداد بيانات غير ضار: يستطيع `dictConfig` حل الأصناف والمصانع، لذا يجب أن يكون إدخاله موثوقًا أو مختزلًا عبر قائمة سماح صارمة.

---

## حلول مشروحة
1. **مسجّل لكل وحدة**: يمنحك `logging.getLogger(__name__)` في كل ملف تحكمًا دقيقًا.
2. **معالج ملف**: يحافظ `RotatingFileHandler` على أحجام ملفات معقولة وينشئ نسخًا احتياطية.
3. **إعدادات JSON الموثوقة**: حمّل الملف المملوك للتطبيق، واشترط `level` واحدًا مسموحًا، وابنِ قاموس handler وformatter المعروف في الشيفرة، ثم استدعِ `dictConfig`. ارفض حقول handler والصنف والمرشح والمصنع غير الموثوقة؛ والتقط أخطاء الملف وJSON والقيمة المتوقعة وطبّق إعداد طرفية معروفًا.

---

## الخلاصة
أصبحت قادرًا على التحكم في مستويات التسجيل وإرسال السجلات إلى عدة وجهات عبر إعداد مركزي.

## نقطة تحقق ومعايير تقييم
- **الصحة**: تطابق النتيجة عقد الوحدة.
- **الوضوح**: تُفهم الأسماء والمسؤوليات من القراءة الأولى.
- **الأخطاء**: يؤدي JSON غير الصالح أو المفتاح غير المسموح إلى fallback آمن، ولا يصل قاموس غير موثوق إلى `dictConfig`، ولا تحتوي السجلات أسرارًا.
- **التحقق**: اختبر خرج الطرفية ورفض حقول المصنع والتدوير المحدود في مجلد مؤقت.
- **الشرح**: اشرح لماذا ينتمي الإعداد إلى حدود التطبيق، ولماذا إدخال `dictConfig` حد ثقة لا بيانات مستخدم غير ضارة.

## تأمل ختامي
يهيئك تعلّم التسجيل لمراقبة الخدمات الحقيقية. ابدأ ببساطة، ثم وسّع الإعداد مع نمو مشروعك.

</div>
