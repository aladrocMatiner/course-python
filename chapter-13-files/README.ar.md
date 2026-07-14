<div dir="rtl">

# الفصل 13 · الملفات والتدفقات من الصفر

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
ستتعلم العمل مع الملفات النصية والثنائية، واستخدام مديري السياق (`with`)، وكتابة السجلات، ومعالجة التدفقات في الزمن الحقيقي، وحماية نفسك من المشكلات الشائعة، مثل الملفات المفقودة والترميزات والتدفقات الضخمة. وسنبني أدوات تقرأ الإعدادات وتدمج البيانات وتولّد التقارير من دون تحميل كل شيء في الذاكرة.

## مسار التعلم
1. **النموذج الذهني**: الملفات كتدفقات متتابعة.
2. **الفتح والإغلاق**: `open` والأوضاع (`r` و`w` و`a` و`b`).
3. **مديرو السياق (`with`)**: تجنب تسرب الموارد.
4. **القراءة والمعالجة سطراً بسطر**.
5. **الكتابة بالتخزين المؤقت والسجلات**.
6. **الملفات الثنائية، مثل الصور والبايتات**.
7. **التدفقات القياسية (`sys.stdin` و`sys.stdout`)**.
8. **اختبارات وتمارين موجّهة**.

## أهداف التعلم
- فتح الملفات بأمان واختيار الوضع الصحيح، قراءة أو كتابة أو إلحاقاً أو ثنائياً.
- معالجة الملفات الكبيرة من دون تحميلها كاملة في الذاكرة.
- كتابة السجلات والتقارير باستخدام التخزين المؤقت.
- قراءة البيانات الثنائية وكتابتها باستخدام `rb` و`wb` و`bytes`.
- استخدام التدفقات (`stdin` و`stdout`) للتركيبات بأسلوب UNIX.

## لماذا يهم هذا؟
يقرأ كل برنامج جاد الملفات أو يكتبها: إعدادات وسجلات وعمليات تصدير وغيرها. يمنع التعامل الصحيح مع التدفقات تلف البيانات، ويجعل سكربتاتك تتوسع إلى ما بعد أمثلة الصف الدراسي.

### مغامرة صغيرة
يشبه الملف دفتر ملاحظات: إذا فتحته بصورة صحيحة وكتبت بعناية وأغلقته، فستجد ملاحظاتك غداً. أما إذا تركته مفتوحاً أو كتبت في الصفحة الخاطئة فقد تفقد أشياء. يعلمك هذا الفصل أن تكون «منظماً» مع دفاترك الرقمية.

## المتطلبات المسبقة
- الدوال والحلقات والقوائم وأساسيات `pathlib` من الفصول السابقة.
- بيئة محلية بإصدار CPython 3.11 أو أحدث، ومجلد مؤقت للتدرب.
- **معاينة اختيارية:** يلتقط التمرين 13-3 الاستثناء `FileNotFoundError`. يمكنك نسخ النمط المعروض الآن؛ يشرح [الفصل 14](../chapter-14-exceptions/README.ar.md) الاستثناءات بالكامل.

## توقّع قبل التشغيل
قبل المثال الأول، توقّع ما الذي يتغير إذا كان الملف مفقودًا، وأي عملية يجب أن تحرر مقبض الملف رغم ذلك. بعد تشغيل مثال آمن في مجلدك المؤقت، قارن المحتوى وتنظيف الموارد اللذين لاحظتهما بتوقّعك قبل المتابعة.

---

## 1. فتح الملفات النصية

```python illustrative
archivo = open("notas.txt", mode="r", encoding="utf-8")
contenido = archivo.read()
archivo.close()
```

- يخبر `mode` بايثون بكيفية الفتح: `r` للقراءة، و`w` للكتابة مع الاستبدال، و`a` للإلحاق.
- أغلق الملف دائماً لتحرير مقبضه، والأفضل أن تستخدم `with`.

### مدير السياق
```python illustrative
with open("notas.txt", mode="r", encoding="utf-8") as fh:
    for linea in fh:
        print(linea.strip())
```

- تغلق `with` الملف تلقائياً حتى إذا وقع استثناء.
- يقرأ التكرار على `fh` سطراً بسطر، ولا يحمّل كل شيء في الذاكرة.

---

## 2. كتابة الملفات

```python runnable
from pathlib import Path
from tempfile import TemporaryDirectory

nuevas_notas = ["Aprender archivos", "Practicar streams"]
with TemporaryDirectory() as temp_dir:
    ruta_notas = Path(temp_dir) / "notas.txt"
    with ruta_notas.open(mode="w", encoding="utf-8") as fh:
        for nota in nuevas_notas:
            fh.write(nota + "\n")
```

- يستبدل `w` المحتوى؛ استخدم `a` إذا أردت الإضافة في النهاية.
- لا تضيف `fh.write` سطراً جديداً تلقائياً.

### `pathlib.Path`
```python runnable
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as temp_dir:
    ruta = Path(temp_dir) / "reportes" / "hoy.txt"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("Reporte generado", encoding="utf-8")
```

- تبسط `write_text` و`read_text` العمليات السريعة.

---

## 3. الملفات الكبيرة والتخزين المؤقت

```python runnable
def contar_lineas(ruta):
    total = 0
    with open(ruta, encoding="utf-8") as fh:
        for _ in fh:
            total += 1
    return total
```

- تتجنب المعالجة سطراً بسطر تحميل الملف كله.

### التحكم في التخزين المؤقت
```python runnable
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as temp_dir:
    ruta_log = Path(temp_dir) / "log.txt"
    with ruta_log.open(mode="a", buffering=1, encoding="utf-8") as log:
        log.write("[INFO] Inicio\n")
```

- يفعّل `buffering=1` التخزين المؤقت حسب السطر، ويفرغ المخزن عند `\n`.

---

## 4. الملفات الثنائية

```python illustrative
with open("imagen.png", mode="rb") as fh:
    datos = fh.read()
print(len(datos))
```

```python illustrative
with open("copia.png", mode="wb") as destino:
    destino.write(datos)
```

- استخدم `rb` و`wb` للبايتات، ولا تضبط `encoding`.
- اقرأ الملفات الضخمة في كتل (`fh.read(4096)`).

### التدفق الثنائي
```python illustrative
with open("entrada.dat", "rb") as origen, open("salida.dat", "wb") as destino:
    while chunk := origen.read(8192):
        destino.write(chunk)
```

---

## 5. JSON وCSV والدوال المساعدة

```python illustrative
import json
from pathlib import Path

ruta = Path("config.json")
data = json.loads(ruta.read_text())
data["debug"] = True
ruta.write_text(json.dumps(data, indent=2))
```

- تحوّل `json.dumps` و`loads` بين القواميس وJSON.
- تجعل `indent=2` الناتج مقروءاً.

```python illustrative
import csv
with open("usuarios.csv", newline="", encoding="utf-8") as fh:
    lector = csv.DictReader(fh)
    for fila in lector:
        print(fila["email"])
```

- تنشئ `DictReader` قاموساً لكل صف، وهو مناسب عندما تريد الأعمدة حسب الاسم.

---

## 6. التدفقات القياسية

```python runnable
import sys

for linea in sys.stdin:
    sys.stdout.write(linea.upper())
```

- يتيح ذلك تركيبات مثل `cat archivo.txt | python script.py`.
- استخدم `sys.stderr` للأخطاء (`sys.stderr.write("Error\n")`).

---

## 7. الاختبارات
احتفظ بالمنطق في دوال تستقبل مسارات أو كائنات شبيهة بالملفات لتسهيل الاختبار.

```python runnable
def procesar_fichero(fh):
    return [linea.strip() for linea in fh]
```

```python runnable
from io import StringIO

def test_procesar_fichero():
    fake = StringIO("uno\ndos\n")
    assert procesar_fichero(fake) == ["uno", "dos"]
```

- تحاكي `StringIO` ملفاً نصياً، و`BytesIO` ملفاً ثنائياً.

---

## تمارين موجّهة (مع مهام TODO)
1. **13-1 · تنظيف السجلات**
   ```python todo
   # TODO 1: read logs.txt line by line
   # TODO 2: drop lines containing "DEBUG"
   # TODO 3: write the result to logs_filtrados.txt
   ```
   *تلميح*: استخدم مديري سياق في سطر واحد: `with open(...) as origen, open(...) as destino:`.

2. **13-2 · نسخ ملف كبير**
   ```python todo
   # TODO 1: implement copiar(origen, destino) reading 4096-byte chunks
   # TODO 2: print progress every 1 MB using sys.stdout
   ```
   *تلميح*: استخدم `tamano += len(chunk)` داخل الحلقة.

3. **13-3 · أداة دمج لسطر الأوامر**
   ```python todo
   # TODO 1: use argparse to accept multiple files and a destination
   # TODO 2: concatenate their content into one file
   # TODO 3: handle errors when a file does not exist
   ```
   *تلميح*: استخدم `Path.exists()` مع `try/except FileNotFoundError`.

---

## أخطاء شائعة
- نسيان إغلاق الملفات؛ تجنب ذلك باستخدام `with`.
- مزج الوضعين النصي والثنائي، مثل `r` و`rb`، والحصول على أخطاء ترميز.
- استبدال الملفات بالخطأ (`mode="w"`).
- قراءة ملفات عملاقة باستخدام `.read()` ونفاد الذاكرة.

---

## حلول مشروحة
1. **تنظيف السجلات**: استخدم `if "DEBUG" not in linea` ثم `destination.write(linea)`؛ فهذه معالجة متدفقة.
2. **نسخ ملف كبير**: تحافظ القراءة في كتل على استقرار الذاكرة، ويساعد عرض التقدم على تشخيص الاختناقات.
3. **أداة الدمج**: افتح كل مسار في `for ruta in args.archivos:` على حدة واكتب إلى الوجهة، وتعامل مع الأخطاء برسائل واضحة.

---

## الخلاصة
أصبحت تعرف أساسيات القراءة والكتابة، ومتى تستخدم الوضع النصي بدلاً من الثنائي، وكيف تعالج التدفقات من دون استنفاد الموارد. وهذه الأنماط أساس عمليات ETL والتقارير وأدوات سطر الأوامر.

## نقطة تحقق ومعايير تقييم
- **الصحة**: تطابق النتيجة عقد الوحدة.
- **الوضوح**: تُفهم الأسماء والمسؤوليات من القراءة الأولى.
- **الأخطاء**: يُختبر مسار ناجح وحالة حدّية ومسار تعافٍ.
- **التحقق**: تعمل الأمثلة والتمارين في بيئة نظيفة.
- **الشرح**: تستطيع تبرير القرارات ومخاطرها.

## تأمل ختامي
يتطلب العمل مع الملفات والتدفقات انضباطاً: اختر الأوضاع بعناية، وتحقق من المسارات، واحمِ نفسك من الملفات الضخمة. ومع التدريب ستبني أدوات تعالج غيغابايتات من البيانات بأمان.

</div>
