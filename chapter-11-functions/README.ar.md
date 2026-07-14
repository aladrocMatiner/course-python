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

## المتطلبات السابقة والمسارات
ينبغي أن تكون مرتاحاً مع [القوائم](../chapter-03-lists/README.ar.md) و[القواميس](../chapter-04-dictionaries/README.ar.md) و[الشروط](../chapter-08-conditionals/README.ar.md) و[الحلقات](../chapter-10-loops/README.ar.md). راجع خصوصاً كيفية التكرار على تجميعة وإعادة نتيجة عند تحقق شرط.

- **المسار التأسيسي · 60–75 دقيقة:** القسم التأسيسي والتمرين 11-0 ونقطة التحقق الأساسية. النتيجة: تعريف دالة واستدعاؤها، واستخدام المعاملات الموضعية والمسمّاة والافتراضية، والتمييز بين القيمة المعادة و`None` الضمنية، وشرح النطاق المحلي، والتعافي من استدعاء غير صالح. لا يتطلب `Callable` أو closure أو decorator أو pytest أو قياس الزمن.
- **المسار المتوسط · 35–45 دقيقة:** القسمان 1–2 بعد نقطة التأسيس. النتيجة: توثيق مسؤولية واحدة، وإضافة أنواع Python 3.11، وإعادة قيم متعددة، واستخدام قيمة اختيارية آمنة.
- **المسار المتقدم الاختياري · 75–110 دقيقة:** الأقسام 3–7 والتمارين 11-1 إلى 11-3. النتيجة: بناء pipeline عالي الرتبة وشرحه باستخدام callbacks وclosures وdecorator خفيف. يعرض القسم 7 [اختبارات pytest](../chapter-18-testing/README.ar.md)؛ انسخه أو تجاوزه في القراءة الأولى.

## لماذا يهم هذا؟
تقلل الدوال الصغيرة والواضحة الأخطاء وتزيد إعادة الاستخدام. وفي تطوير الواجهات الخلفية يتيح تمرير الدوال كمعاملات، مثل أدوات التحقق والمحوّلات، بناء مكوّنات قابلة للتخصيص من دون تكرار الشيفرة.

### مغامرة صغيرة
تشبه الدالة وصفة طعام: إذا كتبتها جيداً، يمكنك طهو الطبق متى شئت من دون إعادة التفكير في كل خطوة. وإذا قرأها شخص آخر استطاع طهوه أيضاً. توفر الوصفات الجيدة الوقت وتمنع الحوادث.

## توقّع قبل التنفيذ
توقّع من دون تشغيل نتيجة `describir_tarea(" backup ")` و`describir_tarea(nombre="deploy", prioridad="high")` في المثال التأسيسي. حدّد كل معامل والقيمة الافتراضية والقيمة التي تعود إلى المستدعي. يخص توقع الـpipeline المسار المتقدم الاختياري.

---

## المسار التأسيسي: الاستدعاء والقيم المعادة والنطاق والقيم الآمنة
للاستدعاء تدفق واضح: تدخل المعاملات عبر الوسائط، وينفذ الجسم، وترسل `return` قيمة إلى المستدعي. إذا وصل التنفيذ إلى النهاية بلا `return`، تعيد Python القيمة `None`.

```python runnable
def describir_tarea(nombre, prioridad="normal"):
    etiqueta = nombre.strip()
    return f"{etiqueta}: {prioridad}"

print(describir_tarea(" backup "))
print(describir_tarea(nombre="deploy", prioridad="high"))
```

الاستدعاء الأول موضعي ويستخدم القيمة الافتراضية. يسمّي الثاني المعاملين. المتغير `etiqueta` محلي ولا يوجد إلا أثناء الاستدعاء.

```python runnable
def anunciar(mensaje):
    print(mensaje)

resultado = anunciar("ready")
print(resultado is None)
```

الطباعة أثر وليست قيمة معادة. يلاحظ السطر الأخير `None` الضمنية.

استخدم `None` إشارة لقائمة اختيارية، ثم أنشئ القائمة داخل الاستدعاء كي لا تتشارك الاستدعاءات قيمة افتراضية قابلة للتغيير:

```python runnable
def registrar(mensaje, historial=None):
    if historial is None:
        historial = []
    historial.append(mensaje)
    return historial

primero = registrar("start")
segundo = registrar("stop")
print(primero, segundo)
```

يحذف هذا الاستدعاء عمدًا المعامل المطلوب؛ الإشارة الثابتة هي `TypeError`:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
def saludar(nombre):
    return f"Hola, {nombre}"

saludar()
```

تعافَ بمطابقة الاستدعاء مع التوقيع ثم شغله مجددًا:

```python runnable
def saludar(nombre):
    return f"Hola, {nombre}"

print(saludar("Noor"))
```

تحقق من الأساسيات باستدعاءات مباشرة وقيم مطبوعة. تأتي الاختبارات الآلية في الفصل 18 وليست متطلبًا مخفيًا هنا.

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
def resumen_pedidos(pedidos: list[int]) -> tuple[int, float]:
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
0. **11-0 · دالة تسمية تأسيسية**
   ```python todo
   def crear_etiqueta(nombre, prefijo="user"):
       # TODO 1: احذف الفراغات المحيطة بـnombre في متغير محلي
       # TODO 2: أعد "prefijo:nombre_limpio"
       pass

   # TODO 3: استدعها مرة موضعيًا ومرة بمعاملات مسماة
   # TODO 4: اطبع القيمتين المعادتين واختبر حد السلسلة الفارغة
   ```
   *تلميح*: تُلاحظ النتيجة الأساسية باستخدام `print`؛ لا تحتاج callbacks أو closures أو decorators أو pytest أو مؤقتًا.

تنتمي التمارين 11-1 إلى 11-3 إلى المسار المتقدم الاختياري.

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
### حل 11-0 التأسيسي
ينتمي `nombre_limpio` المحلي إلى استدعاء واحد، ولا تُستخدم القيمة الافتراضية إلا عند حذف `prefijo`، ويتلقى المستدعي السلسلة بعد `return`.

```python runnable
def crear_etiqueta(nombre, prefijo="user"):
    nombre_limpio = nombre.strip()
    return f"{prefijo}:{nombre_limpio}"

print(crear_etiqueta(" Noor "))
print(crear_etiqueta(nombre="Frej", prefijo="admin"))
print(crear_etiqueta(""))
```

السلسلة الفارغة حد وليست عطلًا مخفيًا. يمكن للبرنامج الذي يجب أن يرفضها إضافة تلك السياسة لاحقًا؛ نتعلم هنا الاستدعاء والإعادة أولًا. يُنفذ `TypeError` للاستدعاء غير الصالح والتعافي في القسم التأسيسي.

1. **المحوّل المرن**: تكرر `convertir(items, funcion)` وتطبق الدالة؛ فتحقق أولاً باستخدام `if not callable(funcion): raise TypeError`. وهذا يتيح الجمع بين الدوال المدمجة والمخصصة.
2. **أدوات التحقق المتسلسلة**: تكرر `run_validators` على دوال التحقق؛ فإذا أطلقت إحداها `ValueError` توقفت، على غرار تدفق التحقق في أدوات تسلسل Django.
3. **المزيّن البسيط**: تغلّف `measure_time` الدالة الأصلية، وتقيس الزمن قبلها وبعدها، ثم تطبع النتيجة. وهي طريقة ممتازة لرؤية أثر الحلقات أو خطوط المعالجة.

---

## نقطة تحقق وسلّم تقييم
أنشئ `crear_etiqueta(nombre, prefijo="user")`، واستدعها موضعيًا وبالأسماء، وتحقق من الاسم العادي والفارغ والمعامل المفقود. أضف دالة منفصلة `mostrar(mensaje)` بلا `return` واشرح لماذا يلاحظ المستدعي `None`. لا تستخدم callbacks أو closures أو decorators أو pytest أو مؤقتًا.

امنح نقطة لكل من **التوقيع والاستدعاءات** و**صحة القيم المعادة** و**القيمة الافتراضية الآمنة** و**التعافي الموثق من `TypeError`** و**شرح النطاق المحلي مقابل `None` الضمنية**. تكمل 4/5 المسار التأسيسي وتجهزك لمسار الفصل 12 الأساسي. يبقى تحدي الـpipeline السابق تحديًا متقدمًا اختياريًا.

---

## الخلاصة
الدوال كتل قابلة لإعادة الاستخدام ذات مسؤوليات واضحة. وعندما تتعامل معها كبيانات تستطيع بناء خطوط معالجة وأدوات تحقق قابلة للإعداد ومزيّنات تضيف سلوكاً من دون تكرار المنطق.

## تأمل ختامي
تتيح لك معرفة تعريف الدوال ودمجها وتمريرها تصميم واجهات API مرنة ومعبرة. وهذه المهارات ضرورية في أطر عمل مثل Django، حيث تتصل الدوال بعروض الاستمارات والبرمجيات الوسيطة والإشارات.

</div>
