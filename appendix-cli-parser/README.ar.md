<div dir="rtl">

# الملحق A · بناء أدوات CLI بالمكتبة القياسية

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
أداة سطر أوامر باستخدام `argparse`: أوامر فرعية، خيارات إجبارية، ومساعدة تلقائية. سنستخدم أيضًا `pathlib` و`logging`.

---

## مثال `argparse`
```python
import argparse

parser = argparse.ArgumentParser(description="Gestor de notas")
parser.add_argument("titulo", help="Nombre del archivo de nota")
parser.add_argument("--mensaje", required=True)
parser.add_argument("--tags", nargs="*", default=[])
args = parser.parse_args()
```

---

## ملخص
أدوات CLI ممتازة للأتمتة. وباستخدام المكتبة القياسية يمكنك بناء الكثير بدون تبعيات إضافية.

</div>
