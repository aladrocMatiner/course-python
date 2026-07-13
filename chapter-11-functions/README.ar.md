<div dir="rtl">

# الفصل 11 · الدوال والمسؤولية وتمرير الدوال

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
سنتعمق في الدوال: كيفية تعريفها وتوثيقها وإعادة قيم متعددة منها والتعامل معها كبيانات. ستمرر الدوال كمعاملات، وتخزنها في تجميعات، وتبني خطوط معالجة صغيرة. الأمثلة مستوحاة من الواجهات الخلفية، مثل التحقق وأدوات التسلسل والخطافات، وتقدم تدريجياً الدوال عالية الرتبة.

## مسار التعلم
1. **مراجعة**: التعريف والمعاملات والقيم المعادة.
2. **المسؤولية الواحدة**: متى تقسم العمل إلى دوال أصغر.
3. **القيم الافتراضية ومعاملات الكلمات المفتاحية**.
4. **الدوال ككائنات من الدرجة الأولى**: تخزينها في متغيرات وتجميعات.
5. **الدوال كمعاملات**: الاستدعاءات الراجعة وأدوات التحقق والمرشحات المخصصة.
6. **الدوال التي تعيد دوالاً**، أي الإغلاقات.
7. **مزيّنات خفيفة**، كمقدمة مفاهيمية.
8. **الاختبارات والممارسات الجيدة**.

## أهداف التعلم
- كتابة دوال حسنة التسمية بتوثيق قصير.
- فهم المعاملات الموضعية ومعاملات الكلمات المفتاحية والقيم الافتراضية.
- تمرير الدوال كمعاملات وتصميم واجهات API قابلة للتوسعة.
- فهم الإغلاقات والدوال التي تعيد دوالاً.
- كتابة اختبارات للمسارات الناجحة ومسارات الأخطاء في الدوال عالية الرتبة.

## المتطلبات السابقة ومعاينة اختيارية
ينبغي أن تكون مرتاحاً مع [القوائم](../chapter-03-lists/README.ar.md) و[القواميس](../chapter-04-dictionaries/README.ar.md) و[الشروط](../chapter-08-conditionals/README.ar.md) و[الحلقات](../chapter-10-loops/README.ar.md). راجع خصوصاً كيفية التكرار على تجميعة وإعادة نتيجة عند تحقق شرط.

يقدّم القسم 7 معاينة عن [الاختبار باستخدام pytest](../chapter-18-testing/README.ar.md). وهو اختياري في القراءة الأولى؛ اقرأ كل `assert` الآن بمعنى «يجب أن تساوي هذه النتيجة القيمة المتوقعة».

## لماذا يهم هذا؟
تقلل الدوال الصغيرة والواضحة الأخطاء وتزيد إعادة الاستخدام. وفي تطوير الواجهات الخلفية يتيح تمرير الدوال كمعاملات، مثل أدوات التحقق والمحوّلات، بناء مكوّنات قابلة للتخصيص من دون تكرار الشيفرة.

### مغامرة صغيرة
تشبه الدالة وصفة طعام: إذا كتبتها جيداً، يمكنك طهو الطبق متى شئت من دون إعادة التفكير في كل خطوة. وإذا قرأها شخص آخر استطاع طهوه أيضاً. توفر الوصفات الجيدة الوقت وتمنع الحوادث.

## توقّع قبل التنفيذ
توقّع من دون تشغيل الشيفرة نتيجة `procesar_items(["noor", "frej"], str.upper)`. اشرح لماذا يكون المعامل `str.upper` وليس `str.upper()`. ثم توقّع هل يغيّر استبدال `[str.strip, str.upper]` بـ`[str.upper, str.strip]` نتيجة خط المعالجة للقيمة `"  hola  "`. تحقق من كل توقع وسمِّ القيمة التي تنتقل بين المراحل.

---

## 1. تعريف الدوال وتوثيقها

```python runnable
def calcular_total(items):
    """Suma los precios en una lista de items."""
    total = 0
    for item in items:
        total += item
    return total
```

- استخدم أسماء أفعال، مثل `calcular_total`.
- تشرح سلسلة التوثيق القصيرة ما تفعله الدالة وما تتوقعه.

### الأنواع والقيم المتعددة المعادة
```python runnable
from typing import List, Tuple
def resumen_pedidos(pedidos: List[int]) -> Tuple[int, float]:
    cantidad = len(pedidos)
    total = sum(pedidos)
    promedio = total / cantidad if cantidad else 0
    return cantidad, promedio
```

---

## 2. القيم الافتراضية ومعاملات الكلمات المفتاحية

```python runnable
def aplicar_descuento(total, porcentaje=0.1):
    return total * (1 - porcentaje)

print(aplicar_descuento(100))      # usa 10%
print(aplicar_descuento(100, 0.2)) # 20%
```

- استخدم الكلمات المفتاحية للوضوح: `aplicar_descuento(total=100, porcentaje=0.15)`.
- تجنب القيم الافتراضية القابلة للتغيير، مثل القوائم والقواميس.

---

## 3. الدوال ككائنات من الدرجة الأولى
يمكن تخزين الدوال وتمريرها مثل أي قيمة أخرى.

```python runnable
def notificar_email(mensaje):
    print(f"Email: {mensaje}")

def notificar_sms(mensaje):
    print(f"SMS: {mensaje}")

canales = [notificar_email, notificar_sms]
for canal in canales:
    canal("Deploy completado")
```

- تشترك كل دالة في «الشكل» نفسه، أي التوقيع نفسه.
- يظهر هذا النمط في الخطافات وأنظمة الأحداث.

---

## 4. تمرير الدوال كمعاملات

```python runnable
def procesar_items(items, transformacion):
    return [transformacion(item) for item in items]

procesar_items(["noor", "frej"], str.upper)  # ['NOOR', 'FREJ']
```

- `transformacion` دالة. يمكنك تمرير الدوال المدمجة، مثل `str.upper`، أو دوالك الخاصة.
- وثّق في المشاريع الحقيقية ما تتوقعه، مثل `Callable[[str], str]`.

### أدوات تحقق قابلة للتخصيص
```python runnable
from typing import Callable

def guardar_usuario(data, validador: Callable[[dict], None]):
    validador(data)
    print("Guardado", data)

def validar_email(data):
    if "@" not in data["email"]:
        raise ValueError("Invalid email")

payload = {"email": "noor@example.com"}
guardar_usuario(payload, validar_email)
```

---

## 5. الدوال التي تعيد دوالاً (الإغلاقات)

```python runnable
def crear_multiplicador(factor):
    def multiplicar(valor):
        return valor * factor
    return multiplicar

duplicar = crear_multiplicador(2)
print(duplicar(10))  # 20
```

- «تتذكر» `multiplicar` القيمة `factor` حتى بعد انتهاء `crear_multiplicador`.
- يفيد ذلك للسلوك القابل للإعداد، مثل إنشاء مرشحات مخصصة.

### مثال بأسلوب الواجهات الخلفية
```python runnable
def crear_validador_longitud(minimo):
    def validar(texto):
        if len(texto) < minimo:
            raise ValueError("Muy corto")
        return texto
    return validar

validar_usuario = crear_validador_longitud(3)
validar_usuario("api")  # OK
```

---

## 6. مزيّنات خفيفة (الصورة العامة)

```python runnable
import functools

def loggear(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Ejecutando {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@loggear
def procesar():
    print("Procesando...")
```

- يطبق `@loggear` دالة المزيّن.
- تحافظ `functools.wraps` على الاسم وسلسلة التوثيق الأصليين.
- استخدم المزيّنات للاهتمامات العابرة، مثل التسجيل والصلاحيات.

---

## 7. اختبار الدوال عالية الرتبة

```python runnable
# pipelines.py
def aplicar_pipeline(valor, etapas):
    for etapa in etapas:
        valor = etapa(valor)
    return valor
```

```python illustrative
# tests/test_pipelines.py
from pipelines import aplicar_pipeline

def test_aplicar_pipeline():
    etapas = [str.strip, str.upper]
    resultado = aplicar_pipeline("  hola  ", etapas)
    assert resultado == "HOLA"
```

- تؤكد الاختبارات أن الترتيب مهم وأن كل خطوة مطبقة.

---

## تمارين موجّهة (مع مهام TODO)
1. **11-1 · محوّل مرن**
   ```python todo
   # TODO 1: create convertir(items, funcion)
   # TODO 2: pass str.upper, then a function that adds a prefix
   # TODO 3: validate it raises if funcion is not callable
   ```
   *تلميح*: تعيد `callable(funcion)` القيمة `True` أو `False`.

2. **11-2 · أدوات تحقق متسلسلة**
   ```python todo
   def validar_no_vacio(texto):
       # TODO: raise ValueError if texto is empty
       pass

   def validar_minimo(texto):
       # TODO: raise ValueError if len(texto) is less than a minimum
       pass
   # TODO 1: create run_validators(texto, validadores)
   # TODO 2: stop at the first error and re-raise it
   # TODO 3: add pytest tests
   ```

3. **11-3 · مزيّن بسيط**
   ```python todo
   # TODO 1: write decorator measure_time(func)
   # TODO 2: print how long it took to run
   # TODO 3: use it on a loop-heavy function to demonstrate
   ```
   *تلميح*: استخدم `time.perf_counter()` لقياس الزمن.

---

## أخطاء شائعة
- استخدام قيم افتراضية قابلة للتغيير (`def foo(items=[])`). الأفضل استخدام `None` وإنشاء القائمة داخل الدالة.
- نسيان `return` في الدوال التي تحوّل البيانات.
- عدم توثيق تواقيع الدوال المتوقعة عند تمرير الاستدعاءات الراجعة ← يؤدي إلى استدعاءات غير متوافقة.
- إعادة استخدام الإغلاقات من دون فهم ما تلتقطه ← يؤدي إلى قيم مفاجئة.

---

## حلول مشروحة
1. **المحوّل المرن**: تكرر `convertir(items, funcion)` وتطبق الدالة؛ فتحقق أولاً باستخدام `if not callable(funcion): raise TypeError`. وهذا يتيح الجمع بين الدوال المدمجة والمخصصة.
2. **أدوات التحقق المتسلسلة**: تكرر `run_validators` على دوال التحقق؛ فإذا أطلقت إحداها `ValueError` توقفت، على غرار تدفق التحقق في أدوات تسلسل Django.
3. **المزيّن البسيط**: تغلّف `measure_time` الدالة الأصلية، وتقيس الزمن قبلها وبعدها، ثم تطبع النتيجة. وهي طريقة ممتازة لرؤية أثر الحلقات أو خطوط المعالجة.

---

## نقطة تحقق وسلّم تقييم
أنشئ `normalizar_registros(registros, transformadores)` بحيث يمر كل قاموس بجميع المحوّلات بالترتيب من دون تغيير قائمة الإدخال. ارفض المحوّل غير القابل للاستدعاء باستخدام `TypeError`، واختبر خط معالجة فارغاً، ومرحلتين مرتبتين، ومسار الخطأ.

امنح نقطة لكل معيار: **العقد** (المدخلات والمخرجات والأخطاء صريحة)، و**الصحة** (يعمل الترتيب وكل الحالات)، و**المسؤولية** (تظل الدالة مركزة)، و**التحقق** (تغطي الاختبارات النجاح والفشل)، و**الشرح** (تميّز بين تمرير الدالة واستدعائها). تعني 4/5 أنك مستعد للأصناف؛ وإلا فراجع الأقسام 3 و4 و7.

---

## الخلاصة
الدوال كتل قابلة لإعادة الاستخدام ذات مسؤوليات واضحة. وعندما تتعامل معها كبيانات تستطيع بناء خطوط معالجة وأدوات تحقق قابلة للإعداد ومزيّنات تضيف سلوكاً من دون تكرار المنطق.

## تأمل ختامي
تتيح لك معرفة تعريف الدوال ودمجها وتمريرها تصميم واجهات API مرنة ومعبرة. وهذه المهارات ضرورية في أطر عمل مثل Django، حيث تتصل الدوال بعروض الاستمارات والبرمجيات الوسيطة والإشارات.

</div>
