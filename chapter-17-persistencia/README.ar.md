<div dir="rtl">

# الفصل 17 · حفظ البيانات: CSV/JSON و SQLite

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم حفظ البيانات في ملفات CSV/JSON، ثم استخدام SQLite عبر `sqlite3`. سنركز على الاستعلامات الآمنة باستخدام معاملات `?` بدل بناء SQL بالنص.

---

## CSV (فكرة)
```python
import csv

def guardar_pedidos(ruta, pedidos):
    with open(ruta, mode="w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "cliente", "total"])
        writer.writeheader()
        for pedido in pedidos:
            writer.writerow(pedido)
```

---

## SQLite (إنشاء جدول)
```python
import sqlite3

conn = sqlite3.connect("pedidos.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY, cliente TEXT, total REAL)")
conn.commit()
conn.close()
```

---

## ملخص
الآن تستطيع حفظ واسترجاع البيانات وفهم الأساس وراء ORM. الفصل التالي: الاختبارات بـ pytest.

</div>
