<div dir="rtl">

# الفصل 15 · الوحدات والحزم وتنظيم الشيفرة

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
ستتعلم تقسيم المشروع إلى ملفات ومجلدات، واستيراد الدوال والأصناف، وإنشاء حزم قابلة لإعادة الاستخدام، وتجنب الاستيرادات الدائرية. وسنحاكي تطبيقاً صغيراً بوحدات `dominio` و`servicios` و`cli` كي ترى كيفية اتصالها.

## مسار التعلم
1. **النموذج الذهني**: كل ملف `.py` هو وحدة واحدة.
2. **الاستيرادات الأساسية**: `import` و`from ... import ...`.
3. **المجلدات كحزم**: `__init__.py` والاستيرادات النسبية و`PYTHONPATH`.
4. **بنية المشروع الموصى بها**.
5. **تجنب دورات الاستيراد**.
6. **تحزيم خفيف** باستخدام `if __name__ == "__main__"`.

## أهداف التعلم
- تنظيم الشيفرة في وحدات مترابطة منطقياً.
- استيراد الدوال والأصناف من ملفات أخرى بدلاً من تكرار المنطق.
- إنشاء حزم باستخدام `__init__.py` وفهم الاستيرادات النسبية.
- اكتشاف الاستيرادات الدائرية وإصلاحها.
- إعداد وحدة نظيفة تكون «نقطة الدخول الرئيسية».

## لماذا يهم هذا؟
لا تتسع المشاريع الحقيقية في ملف واحد. ويسهّل فصل المسؤوليات الاختبار وإعادة الاستخدام والتعاون.

### مغامرة صغيرة
تخيّل أن فرقاً مختلفة تبني لعبتك المفضلة: الشخصيات والمراحل والموسيقى. لو كان كل شيء في ملف واحد لاستحال التعاون. تشبه الوحدات غرفاً مرتبة في منزل؛ يعرف الجميع مكان عملهم، ويسهل العثور عليه لاحقاً.

### كيفية التدرب على هذا الفصل (ببساطة شديدة)
1. أنشئ ملفين: `saludos.py` و`app.py` في المجلد نفسه.
2. شغّل `python app.py`.
3. إذا حصلت على خطأ، فاقرأ اسم الخطأ ورقم السطر؛ هذا طبيعي أثناء التعلم.

## المتطلبات المسبقة
الفصول السابقة الموصى بها: 11, 12, 13.
استخدم CPython 3.11+ في بيئة محلية مؤقتة, وأبقِ البيانات والأسرار والخدمات بعيدًا عن الأنظمة الحقيقية.

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

## 3. مستوى إضافي: بنية أكثر احترافية (اختياري)
إذا كنت في بدايتك، يمكنك تجاوز هذا القسم. أما إذا أردت العمل «كمشروع حقيقي»، فستساعدك هذه البنية كثيراً:

```text illustrative
project/
├── src/
│   ├── __init__.py
│   ├── dominio/
│   │   ├── __init__.py
│   │   └── pedidos.py
│   ├── servicios/
│   │   ├── __init__.py
│   │   └── descuentos.py
│   └── cli.py
└── tests/
```

- يحتوي `src/` على الشيفرة، ويفصل `tests/` الاختبارات.
- لأن هذا التخطيط التعليمي يجعل `src` حزمة، استخدم `from src.dominio.pedidos import Pedido`.

### التشغيل من جذر المشروع
عندما تستخدم الحزم، شغّل من مجلد جذر المشروع. ومن الحيل الشائعة:

```bash illustrative
python -m src.cli
```

### التحقق من الحزمة
```bash illustrative
python -c "from src.dominio.pedidos import Pedido; print(Pedido.__name__)"
```

ويعني ذلك: «شغّل `cli.py` كجزء من حزمة `src`»، مما يجعل الاستيرادات تعمل بموثوقية أكبر.

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
   # TODO 1: create dominio/productos.py with class Producto
   # TODO 2: create servicios/precios.py and use Producto
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.
   إضافة: أضف التابع `aplicar_descuento(porcentaje)` إلى `Producto`.

2. **15-2 · أداة سطر أوامر معيارية**
   ```python todo
   # TODO 1: create cli.py that imports functions from servicios
   # TODO 2: run python -m cli to validate the import path
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

---

## حلول مشروحة
1. **المجال مقابل الخدمات**: يحصل كل مجال على وحدته الخاصة؛ وتستورد الخدمات المجال لتجنب خلط المسؤوليات.
2. **أداة سطر الأوامر المعيارية**: لا تفعل `cli.py` سوى التنسيق؛ ويعيش منطق العمل في `servicios`، مما يسهل اختباره.
3. **إصلاح الدورة**: تزيل عملية نقل الدوال المشتركة إلى `utils` التبعيات الدائرية وتوضح الطبقات.

---

## الخلاصة
يحافظ تقسيم الشيفرة إلى وحدات وحزم على تنظيم مشروعك. ويمكنك الآن استيراد ما تحتاج إليه فقط وإنشاء نقاط دخول نظيفة.

## نقطة تحقق ومعايير تقييم
- **الصحة**: تطابق النتيجة عقد الوحدة.
- **الوضوح**: تُفهم الأسماء والمسؤوليات من القراءة الأولى.
- **الأخطاء**: يُختبر مسار ناجح وحالة حدّية ومسار تعافٍ.
- **التحقق**: تعمل الأمثلة والتمارين في بيئة نظيفة.
- **الشرح**: تستطيع تبرير القرارات ومخاطرها.

## تأمل ختامي
اسأل نفسك دائماً: «أين ينبغي أن تعيش هذه القطعة من المنطق؟» تهيئك الوحدات الواضحة لمشاريع أكبر وأطر عمل مثل Django.

</div>
