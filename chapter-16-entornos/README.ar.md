<div dir="rtl">

# الفصل 16 · البيئات والاعتمادات (Dependencies)

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم `venv` و`pip` و`requirements.txt` وكيف نستخدم متغيرات البيئة لإعدادات آمنة (بدون وضع الأسرار داخل git).

---

## إنشاء `.venv`
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install requests
```

---

## تثبيت نفس الاعتمادات لاحقًا
```bash
pip freeze > requirements.txt
pip install -r requirements.txt
```

---

## متغيرات البيئة
```python
import os
API_KEY = os.environ.get("API_KEY", "dummy")
```

---

## ملخص
البيئات المعزولة تجعل المشروع “قابل لإعادة التشغيل” على أي جهاز. الفصل التالي: حفظ البيانات (CSV/JSON/SQLite).

</div>
