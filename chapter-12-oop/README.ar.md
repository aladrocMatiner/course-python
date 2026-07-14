<div dir="rtl">

# الفصل 12 · البرمجة كائنية التوجه: النظرية والتطبيق

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

## ما الذي سنبنيه؟
سننشئ أصنافنا الأولى في بايثون، بدءاً من النموذج الذهني لـ«الكائن» وانتهاءً بأصناف مستوحاة من الواجهات الخلفية، مثل المستخدمين والطلبات والخدمات. سنتناول السمات والتوابع والتهيئة والوراثة والتركيب و`dataclasses` والممارسات الجيدة. هذا الفصل أطول عمداً؛ فالبرمجة كائنية التوجه تحتاج إلى التأنّي وكثرة الأمثلة.

## مسار التعلم
1. **النموذج الذهني**: ما الكائن ولماذا يوجد.
2. **صياغة الصنف الأساسية**: السمات و`__init__` والتوابع.
3. **التمثيلات (`__repr__` و`__str__`)**.
4. **توابع الصنف والتوابع الساكنة**.
5. **الوراثة والتركيب**: متى تستخدم كل واحد منهما.
6. **التغليف الخفيف والخصائص**.
7. **`dataclasses` للنماذج الخفيفة**.
8. **أنماط الاستخدام في الواجهات الخلفية**.
9. **اختبارات وتمارين موجّهة**.

## أهداف التعلم
- تعريف أصناف ذات سمات وتوابع واضحة.
- إنشاء نسخ وتغيير حالتها وتمثيل الكائنات بنص واضح.
- استخدام الوراثة والتركيب من دون بناء تسلسلات هرمية معقدة.
- استخدام `@property` وتوابع الصنف والتوابع الساكنة لقواعد محددة.
- استخدام `dataclasses` لحاويات قيم خفيفة وضبط المساواة أو الترتيب أو منع إعادة إسناد الحقول عن قصد.

## المتطلبات السابقة والمعاينات الاختيارية
راجع [القواميس](../chapter-04-dictionaries/README.ar.md) و[الدوال](../chapter-11-functions/README.ar.md) قبل البدء. ينبغي أن تستطيع تعريف دالة وتمرير المعاملات وإعادة قيمة وتحديث قاموس من دون تغيير بيانات غير مرتبطة.

تظهر [الاستثناءات](../chapter-14-exceptions/README.ar.md) و[الاختبار باستخدام pytest](../chapter-18-testing/README.ar.md) كمعاينتين اختياريتين. يكفي في القراءة الأولى أن تدرك أن `raise` يرفض الحالة غير الصالحة وأن `assert` يتحقق من نتيجة متوقعة.

## لماذا يهم هذا؟
تتيح لك الكائنات نمذجة كيانات العالم الحقيقي وجمع البيانات والسلوك معاً. في تطبيقات Django تكون النماذج والعروض وأدوات التسلسل أصنافاً؛ ويساعدك فهم الأساسيات على توسيعها بأمان.

### مغامرة صغيرة
فكّر في الصنف كقالب لشخصية لعبة فيديو: لديها إحصاءات، مثل الصحة والطاقة، ومهارات، مثل القفز والهجوم. أما الكائن فهو شخصية بعينها ذات قيمها الخاصة. وهكذا يتوقف برنامجك عن كونه أعداداً متناثرة ويصبح عالماً من الأشياء ذات المعنى.

## توقّع قبل التنفيذ
قبل تشغيل المثال الأول، حدّد الصنف والنسخة والسمات والتابع. توقّع الحالة بعد الإنشاء مباشرة وبعد استدعاء تابع. تخص التوقعات عن `Cuenta` والخصائص و`frozen=True` المسارات الاختيارية وليست مطلوبة لنقطة التحقق الأساسية.

## مسارات التعلم
- **المسار الأساسي · 70–100 دقيقة على جلستين:** ادرس القسمين 1–2 والتمرين 12-0 والتعافي ونقطة التحقق الأساسية. النتيجة: تعريف صنف وإنشاء نسخ مستقلة وتغيير الحالة بتابع وتنفيذ تمثيل مفيد. الاستدعاءات المباشرة والحالة المطبوعة هما الدليل؛ لا يتطلب استثناءات أو pytest.
- **المسار الاحترافي الاختياري · نحو جلستين إضافيتين:** ادرس الأقسام 3–5 و7–9 بعد [الاستثناءات](../chapter-14-exceptions/README.ar.md) و[الاختبارات](../chapter-18-testing/README.ar.md). النتيجة: التحقق من الثوابت واختيار التركيب أو الوراثة وتسلسل حد واستبدال اعتماد في اختبار.
- **المسار المتقدم الاختياري · نحو جلسة:** ادرس القسم 6 والتسلسل المخصص في القسم 8. النتيجة: شرح `eq` و`order` و`frozen` و`replace` وقابلية التغيير المتداخلة بأمثلة ملحوظة.

---

## 1. النموذج الذهني: الكائنات «أشياء لها بيانات وأفعال»
فكّر في الصنف كمخطط، والكائنات كنسخ من ذلك المخطط. مثلاً يمتلك `Usuario` بيانات (`nombre` و`email`) وأفعالاً، مثل التعطيل والإشعار.

```python runnable
class Usuario:
    def __init__(self, nombre, email):
        self.nombre = nombre
        self.email = email
        self.activo = True

    def desactivar(self):
        self.activo = False
```

- تشير `self` إلى النسخة نفسها.
- تنشئ السمات عادةً داخل `__init__`.

### إنشاء نسخ
```python illustrative
noor = Usuario("Noor", "noor@example.com")
print(noor.nombre)
noor.desactivar()
print(noor.activo)  # False
```

---

## 2. تمثيل الكائنات (`__repr__` و`__str__`)

```python runnable
class Ticket:
    def __init__(self, id, estado):
        self.id = id
        self.estado = estado

    def __repr__(self):
        return f"Ticket(id={self.id!r}, estado={self.estado!r})"

    def __str__(self):
        return f"Ticket #{self.id} ({self.estado})"
```

- يعيد `repr(obj)` تمثيلاً مناسباً لتصحيح الأخطاء.
- يستخدم `print` ناتج `str(obj)`.

---

## 3. توابع الصنف والتوابع الساكنة

```python runnable
class Sesion:
    activa = 0  # atributo de clase

    def __init__(self, usuario):
        self.usuario = usuario
        Sesion.activa += 1

    @classmethod
    def creadas(cls):
        return cls.activa

    @staticmethod
    def formato_id(value):
        return f"SES-{value}"
```

- يستقبل `@classmethod` المعامل `cls`، أي الصنف، ويمكنه قراءة سمات الصنف أو تعديلها.
- لا يستقبل `@staticmethod` أياً من `self` أو `cls`؛ فهو دالة مساعدة تعيش في نطاق أسماء الصنف.

---

## 4. الوراثة والتركيب

### الوراثة
```python runnable
class Notificacion:
    def enviar(self, mensaje):
        raise NotImplementedError

class EmailNotificacion(Notificacion):
    def enviar(self, mensaje):
        print(f"Email: {mensaje}")
```

- استخدم الوراثة عندما تشترك الأصناف في واجهة موحدة.

### التركيب
```python runnable
class ServicioMensajes:
    def __init__(self, canal):
        self.canal = canal

    def enviar(self, mensaje):
        self.canal.enviar(mensaje)
```

- يعني التركيب أن صنفاً يستخدم صنفاً آخر داخلياً. وهو أكثر مرونة من الوراثة لمزج السلوكيات.

---

## 5. التغليف الخفيف والخصائص

```python runnable
class Cuenta:
    def __init__(self, balance):
        self.balance = balance

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, valor):
        if valor < 0:
            raise ValueError("Balance negativo no permitido")
        self.__balance = valor
```

- يستخدم `__balance` آلية *name mangling* لتقليل الكتابات المباشرة العرضية؛ وليس حدّاً أمنياً. يمر كل من الإنشاء العادي والإسناد عبر الخاصية التي تتحقق من القيمة.
- تعرض `@property` دالة جلب وضبط من دون تغيير صياغة الاستدعاء (`cuenta.balance = 100`).

---

## 6. استخدام `dataclasses` للنماذج الخفيفة

```python runnable
from dataclasses import dataclass

@dataclass
class Coordenada:
    lat: float
    lon: float
    etiqueta: str = ""
```

- تولّد `@dataclass` افتراضياً `__init__` و`__repr__` والمساواة (`eq=True`). تتطلب توابع الترتيب `order=True`، ويجب أن تدعم الحقول المشاركة تلك المقارنات.
- يمنع `frozen=True` إعادة الإسناد العادية للحقول، لكنه لا يحقق ثباتاً عميقاً؛ إذ تظل القيمة القابلة للتغيير المخزنة في حقل قابلة للتعديل.

---

## 7. أنماط الواجهات الخلفية
- **النماذج**: تحتفظ بالبيانات والتحقق، مثل `Usuario` و`Pedido`.
- **الخدمات**: تنسق خطوات متعددة، مثل `ServicioMensajes`.
- **المستودعات**: تجرّد الوصول إلى البيانات؛ ويمكنك تمرير دوال، أي استدعاءات راجعة، لتحويل النتائج.

### مثال
```python runnable
class ServicioDescuentos:
    def __init__(self, calculo_descuento):
        self.calculo_descuento = calculo_descuento

    def procesar(self, pedido):
        descuento = self.calculo_descuento(pedido)
        pedido.total -= descuento
        return pedido
```

- `calculo_descuento` دالة؛ وهذا يمزج البرمجة كائنية التوجه بالدوال عالية الرتبة.

---

## 8. تسلسل الكائنات وإلغاء تسلسلها
يعني التسلسل تحويل كائن إلى بنية، مثل قاموس أو JSON، كي تتمكن من تخزينه أو إرساله. أما إلغاء التسلسل فهو إعادة بناء الكائن من تلك البنية.

### `to_dict` و`from_dict`
```python runnable
class Pedido:
    def __init__(self, id, total, items):
        self.id = id
        self.total = total
        self.items = items

    def to_dict(self):
        return {
            "id": self.id,
            "total": self.total,
            "items": self.items,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            total=data["total"],
            items=data.get("items", []),
        )
```

```python illustrative
pedido = Pedido(1, 120, ["libro", "cuaderno"])
payload = pedido.to_dict()
pedido_recuperado = Pedido.from_dict(payload)
```

- هذا مثالي لتحويل النسخ إلى حمولات JSON أو سجلات قاعدة بيانات.

### JSON
```python illustrative
import json

class UsuarioJSON(Usuario):
    def to_json(self):
        return json.dumps({
            "nombre": self.nombre,
            "email": self.email,
        })

    @classmethod
    def from_json(cls, raw):
        data = json.loads(raw)
        return cls(data["nombre"], data["email"])
```

- عالج `json.JSONDecodeError` عندما تأتي البيانات من مصادر خارجية.

### `dataclasses.asdict`
```python runnable
from dataclasses import dataclass, asdict

@dataclass
class Configuracion:
    env: str
    debug: bool = False

conf = Configuracion("prod")
conf_dict = asdict(conf)  # {'env': 'prod', 'debug': False}
```

- تحوّل `asdict` أصناف البيانات بصورة متكررة إلى قواميس جاهزة للتسلسل.

### إلغاء التسلسل الآمن
- تحقق من الحقول المطلوبة قبل بناء النسخة (`if "id" not in data: raise ValueError`).
- حوّل الأنواع صراحة، مثل `int(data["id"])`، عندما تتوقع أعداداً.
- لا تثق بالبُنى الخارجية أبداً من دون التحقق منها.

---

## 9. اختبار الكائنات
استخدم `pytest` للتحقق من السلوك.

```python illustrative
# tests/test_usuario.py
from usuarios import Usuario

def test_usuario_se_desactiva():
    user = Usuario("Noor", "ana@example.com")
    user.desactivar()
    assert user.activo is False
```

لتشغيل هذا الاختبار، أنشئ ملف `usuarios.py` وانسخ إليه صنف `Usuario` من بداية الفصل.

- تحقق من الحالة قبل الإجراء وبعده.
- بالنسبة إلى الأصناف ذات التبعيات، احقن «بدائل اختبارية»، أي كائنات وهمية بسيطة تنفذ الواجهة نفسها.

---

## تدريب أساسي وتعافٍ

### 12-0 · عدّادان مستقلان

توقع التمثيلين، وشغّل الكتلة، واشرح لماذا لا يؤدي تغيير `first` إلى تغيير `second`:

```python runnable
class Counter:
    def __init__(self, start=0):
        self.value = start

    def increment(self):
        self.value += 1

    def __repr__(self):
        return f"Counter(value={self.value})"


first = Counter()
second = Counter(10)
first.increment()
print(first)
print(second)
```

يحذف الصنف التالي `self` عمداً؛ يؤدي استدعاء تابعه إلى `TypeError` المتوقع:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
class Counter:
    def increment():
        pass


counter = Counter()
counter.increment()
```

تعافَ بقبول النسخة صراحة وراقب حالتها المتغيرة:

```python runnable
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1


counter = Counter()
counter.increment()
print(counter.value)
```

الحالتان المطبوعتان ومخرجات التعافي هي دليل الإكمال الأساسي. توقف قبل الوراثة وproperties وdataclasses والتسلسل وpytest.

## تمارين موجّهة (مع مهام TODO)
1. **12-1 · صنف `Producto`**
   ```python todo
   class Producto:
       # TODO 1: define attributes nombre, precio, stock
       # TODO 2: add vender(cantidad) that subtracts stock and validates availability
       # TODO 3: implement __repr__ for debugging
   ```
   *تلميح*: أطلق `ValueError` إذا كانت `cantidad` أكبر من `stock`.

2. **12-2 · تركيب الخدمات**
   ```python todo
   class EmailService:
       # TODO: implement send(mensaje)
       pass

   class SMSService:
       # TODO: implement send(mensaje)
       pass

   class NotificationCenter:
       # TODO 1: accept a list of services
       # TODO 2: implement notify(mensaje)
   ```
   *تلميح*: كرر على الخدمات واستدعِ `service.send(mensaje)`.

3. **12-3 · صنف بيانات غير قابل للتغيير**
   ```python todo
   from dataclasses import dataclass, replace
   @dataclass(frozen=True)
   class Config:
       env: str
       debug: bool = False
   # TODO 1: show how to create a new config changing env
   # TODO 2: explain why frozen prevents accidental modifications
   ```

---

## أخطاء شائعة
- نسيان `self` كأول معامل في التوابع، مما يسبب `TypeError`.
- تعريف السمات خارج `__init__` من دون إدراك أنها تصبح سمات للصنف.
- بناء أشجار وراثة عميقة حين كان التركيب كافياً.
- عدم توثيق ما يجب على الأصناف الفرعية تنفيذه ← يؤدي إلى غياب `NotImplementedError`.

---

## حلول مشروحة
1. **Producto**: تتحقق `vender` من المخزون، وتطرح الكمية، وتعيد القيمة الجديدة؛ ويساعد `__repr__` على فحص النسخ في السجلات.
2. **NotificationCenter**: يستقبل خدمات تشترك في `send()`. يتيح التركيب إضافة القنوات وحذفها من دون وراثة متعددة.
3. **Config المجمّد**: يمنع `dataclass(frozen=True)` إعادة الإسناد العادية للحقول. وبما أن `replace` مستوردة أعلاه، تنشئ `nueva = replace(config, env="prod")` نسخة معدّلة. يقلل ذلك إعادة الإسناد العرضية، لكنه لا يجمّد القيم القابلة للتغيير داخل الحقول تجميداً عميقاً.

---

## نقطة تحقق وسلّم تقييم
أنشئ صنف `Counter` بقيمة ابتدائية وتابع يغير الحالة و`__repr__` مقروء. أنشئ نسختين وغير واحدة فقط واطبع الاثنتين، ثم أعد إنتاج `TypeError` الناتج من حذف `self` وصححه. استخدم استدعاءات مباشرة؛ لا تتطلب استثناءات ولا pytest.

امنح نقطة لكل معيار: **الإنشاء** (الحالتان الأوليتان صحيحتان)، و**الاستقلال** (لا تشترك النسختان في الحالة)، و**السلوك** (يغير التابع مستقبله فقط)، و**التمثيل** (الحالة المطبوعة واضحة)، و**التعافي** (يتبع الخطأ المتوقع كود عامل). تعني 4/5 أنك تستطيع المتابعة؛ وإلا فأعد القسمين 1–2 و12-0. الثوابت والوراثة/التركيب وdataclasses والتسلسل وpytest أدلة لاحقة أو اختيارية.

---

## الخلاصة
تساعدك البرمجة كائنية التوجه في بايثون على تمثيل الكيانات الحقيقية بوضوح، وجمع البيانات والسلوك، وتطبيق أنماط مثل الوراثة والتركيب والخصائص. ومع التدريب ستعرف متى تستخدم الأصناف التقليدية بدلاً من `dataclasses`.

## تأمل ختامي
يُعد بناء أصناف حسنة التصميم خطوة أساسية نحو المشاريع الأكبر. خذ وقتك للتدرب، واكتب الاختبارات، وأبقِ كل صنف مركزاً على مسؤولية واحدة. وفي فصول لاحقة ستندمج هذه الأجزاء في تطبيقات كاملة.

</div>
