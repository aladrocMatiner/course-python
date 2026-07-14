<div dir="rtl">

# الفصل 17 · تخزين خفيف للبيانات: CSV وJSON وSQLite

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنربط برامجنا بوسائل تخزين أساسية. سنبدأ بملفات CSV وJSON المنظّمة، ثم ننتقل إلى SQLite المضمّنة في Python. ستتعلّم قراءة السجلات وكتابتها، وتجميع الاستعلامات داخل مستودعات، والتمهيد لاستخدام أدوات الربط الكائني العلائقي (ORM) مثل Django.

## مسار التعلّم
1. **تذكير سريع بالملفات المنظّمة**.
2. **حفظ البيانات باستخدام CSV وJSON**.
3. **مقدمة إلى SQLite عبر `sqlite3`**.
4. **الاستعلامات ذات المعاملات، والإدراج، والقراءة**.
5. **صنف مستودع بسيط**.
6. **«ترحيلات» صغيرة: إنشاء الجداول عند غيابها**.

## أهداف التعلّم
- حفظ البيانات وتحميلها بصيغتي CSV وJSON مع تحقق أساسي.
- الاتصال بـ SQLite عبر `sqlite3` وتنفيذ استعلامات آمنة.
- حصر عمليات قاعدة البيانات داخل صنف مستودع.
- فهم كيفية تحويل الصفوف المسترجعة إلى كائنات.

## لماذا يهم هذا؟
حتى لو كنت ستستخدم ORM قريبًا، فإن فهم الأساسيات يساعدك على تشخيص المشكلات ومعرفة ما يحدث في الطبقات الداخلية.

### مغامرة صغيرة
حفظ البيانات يشبه تدوين يومياتك: إذا كتبتها بترتيب، استطعت قراءة قصصك بعد سنوات. تمنحك CSV وJSON دفاتر بسيطة للملاحظات السريعة، بينما تمنحك SQLite دفترًا منظّمًا بفواصل وفهارس. تعلّم الوسيلتين يجعل برنامجك قادرًا على «تذكّر» رحلته.

## المتطلبات المسبقة
- الملفات وJSON/CSV من الفصل 13، والاستثناءات من الفصل 14، والأصناف وdataclasses من الفصل 12.
- بيئة محلية بإصدار CPython 3.11 أو أحدث؛ تعد `sqlite3` جزءًا من المكتبة القياسية.

## توقّع قبل التشغيل
اختر طلبًا وتوقّع الأنواع التي ستبقى بلا تغيير بعد ذهابها وعودتها عبر CSV، والقيم التي ستعود كنص. بعد قراءة الصف، قارن كل حقل بتوقّعك قبل إنشاء كائن.

---

## 1. حفظ البيانات في CSV
يشبه ملف CSV جدولًا في دفتر: أعمدة وصفوف.

```python runnable
import csv

def guardar_pedidos(ruta, pedidos):
    with open(ruta, mode="w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "cliente", "total"])
        writer.writeheader()
        for pedido in pedidos:
            writer.writerow(pedido)
```

```python illustrative
with open("pedidos.csv", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    pedidos = list(reader)
print(pedidos)
```

ناتج متوقّع شائع؛ لاحظ أن كل ما يُقرأ من CSV يصل على هيئة نص:
```text illustrative
[{'id': '1', 'cliente': 'Noor', 'total': '120'}]
```

تحدٍّ سريع: أضف طلبًا آخر، ثم احفظ الملف واقرأه من جديد.

---

## 2. JSON

```python illustrative
import json
from pathlib import Path

ruta = Path("pedidos.json")
payload = json.loads(ruta.read_text())
payload.append({"id": 3, "total": 50})
ruta.write_text(json.dumps(payload, indent=2))
```

- تناسب JSON ملفات الإعدادات ومجموعات البيانات الصغيرة.

---

## 3. SQLite عبر `sqlite3`
SQLite قاعدة بيانات صغيرة تعيش داخل ملف واحد بامتداد `.db`. تخيّلها دفترًا ذا «جداول» أو صفحات منظّمة جدًا.

```python runnable
import sqlite3

conn = sqlite3.connect("pedidos.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY, cliente TEXT, total REAL)")
conn.commit()
conn.close()
```

- تنشئ `connect` ملف `.db` إذا لم يكن موجودًا.
- ينشئ `CREATE TABLE` جدولًا عند غيابه. والجدول شبيه بورقة بيانات مكوّنة من صفوف وأعمدة.

### الإدراج والاستعلام
```python illustrative
from contextlib import closing

with closing(sqlite3.connect("pedidos.db")) as conn:
    with conn:  # commits on success and rolls back on failure
        cur = conn.cursor()
        cur.execute("INSERT INTO pedidos(cliente, total) VALUES (?, ?)", ("Noor", 120))

with closing(sqlite3.connect("pedidos.db")) as conn:
    cur = conn.cursor()
    cur.execute("SELECT id, cliente, total FROM pedidos")
    filas = cur.fetchall()
```

- استخدم معاملات `?` لتفادي حقن SQL.
- اكتسب منذ البداية عادة **عدم** جمع النصوص لبناء استعلام SQL، حتى وأنت ما زلت تتعلّم.

---

## 4. مستودع بسيط

```python runnable
class PedidoRepo:
    def __init__(self, conexion):
        self.conn = conexion

    def crear(self, cliente, total):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO pedidos(cliente, total) VALUES (?, ?)", (cliente, total))
        self.conn.commit()
        return cur.lastrowid

    def listar(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, cliente, total FROM pedidos")
        return cur.fetchall()
```

```python illustrative
from contextlib import closing

with closing(sqlite3.connect("pedidos.db")) as conn:
    repo = PedidoRepo(conn)
    repo.crear("Frej", 90)
    print(repo.listar())
```

- اجمع SQL داخل المستودع كي يبقى باقي البرنامج واضحًا ونظيفًا.

---

## تمارين موجّهة (مع TODO)
1. **17-1 · من CSV إلى كائنات**
   ```python todo
   # TODO 1: read pedidos.csv and convert each row into a Pedido object
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

2. **17-2 · عمليات CRUD أساسية في SQLite**
   ```python todo
   # TODO 1: implement update(id, total)
   # TODO 2: implement delete(id)
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

3. **17-3 · خدمة مع مستودع**
   ```python todo
   # TODO 1: create PedidoService that uses PedidoRepo
   # TODO 2: add validation before inserting
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

---

## أخطاء شائعة
- نسيان `conn.commit()` بعد الإدراج أو التحديث.
- لا تفترض أن `with conn:` يغلق SQLite؛ فهو يؤكد المعاملة أو يتراجع عنها فقط. استدعِ `close()` أو استخدم `contextlib.closing`.
- بناء SQL بجمع النصوص، وهو ما يعرّض البرنامج لخطر الحقن.

---

## حلول مشروحة
1. **من CSV إلى كائنات**: حوّل `id` عبر `int()` و`total` عبر `float()` قبل إنشاء `Pedido`، وارفض الحقول الغائبة أو غير الصالحة باستخدام `ValueError`.
2. **CRUD**: استخدم `UPDATE pedidos SET total=? WHERE id=?` للتحديث و`DELETE FROM pedidos WHERE id=?` للحذف.
3. **الخدمة والمستودع**: أبقِ التحقق في الخدمة وحفظ البيانات في المستودع؛ فهذا نمط شائع في أطر العمل.

---

## الخلاصة
أصبحت قادرًا على حفظ البيانات وتحميلها من ملفات منظّمة ومن SQLite، وهو تمهيد مناسب لاستخدام ORM.

## نقطة تحقق ومعايير تقييم
- **الصحة**: تطابق النتيجة عقد الوحدة.
- **الوضوح**: تُفهم الأسماء والمسؤوليات من القراءة الأولى.
- **الأخطاء**: يُختبر مسار ناجح وحالة حدّية ومسار تعافٍ.
- **التحقق**: تعمل الأمثلة والتمارين في بيئة نظيفة.
- **الشرح**: تستطيع تبرير القرارات ومخاطرها.

## تأمل ختامي
تبقى أساسيات التخزين قيّمة حتى مع الأدوات الحديثة، لأنها تساعدك على تشخيص الأخطاء وفهم حركة البيانات.

</div>
