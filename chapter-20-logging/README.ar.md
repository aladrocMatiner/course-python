<div dir="rtl">

# الفصل 20 · Logging وإدارة الإعدادات

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنستخدم `logging` من مكتبة بايثون القياسية لكتابة سجلات بمستويات مختلفة (INFO/DEBUG/ERROR)، ونغيّر مستوى السجلات عبر متغيرات البيئة.

---

## إعداد بسيط
```python
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("Iniciando app")
logging.warning("API lenta")
```

---

## مستوى السجلات من متغير بيئة
```python
import os
import logging

nivel = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=nivel)
```

---

## ملخص
الـ logging هو “الصندوق الأسود” لفهم ما يحدث في الإنتاج. الفصل التالي: `asyncio`.

</div>
