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
قبل تشغيل المثال الأول، حدّد الصنف والنسخة والحالة التي تخص تلك النسخة. توقّع الحالة بعد الإنشاء مباشرة وبعد استدعاء تابع. لاحقاً، قبل القسم 5، توقّع هل يفشل `Cuenta(-1)` و`cuenta.balance = -1` بالطريقة نفسها؛ وقبل القسم 6 توقّع هل يمنع `frozen=True` تغيير قائمة مخزنة داخل نسخة مجمّدة. تحقق من كل إجابة واشرح القاعدة المعنية.

## مسارات التعلم
- **المسار الأساسي — نحو جلستين:** ادرس الأقسام 1–3 و5. النتيجة: بناء صنف مركز بتمثيل مفيد وخاصية تتحقق من القيم. دليل الإكمال: تغطي الاختبارات الإنشاء الصالح وتغيير الحالة ورفض الحالة غير الصالحة.
- **المسار الاحترافي — نحو جلستين إضافيتين:** ادرس القسم 4 والأقسام 7–9. النتيجة: اختيار التركيب أو الوراثة، والتسلسل عبر حد واضح، واختبار الكائنات المتعاونة. دليل الإكمال: استبدال اعتماد ببديل اختباري من دون تغيير الصنف الرئيسي.
- **المسار المتقدم الاختياري — نحو جلسة:** ادرس القسم 6 والتسلسل المخصص في القسم 8. النتيجة: شرح `eq` و`order` و`frozen` و`replace` وقابلية التغيير المتداخلة. دليل الإكمال: بيان المقارنات التي تعمل وسبب كون منع إعادة الإسناد ليس ثباتاً عميقاً.

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
نمذج `Pedido` له ثابت واحد على الأقل، وتمثيل مقروء، وخدمة أسعار مركبة. ارفض الإنشاء غير الصالح، وسلسل الحقول العامة المقصودة فقط، واختبر السلوك الصالح والحالة غير الصالحة وخدمة بديلة. ثم برر هل الأنسب صنف تقليدي أم dataclass.

امنح نقطة لكل معيار: **الثوابت** (تتحقق كل مسارات الإنشاء والتحديث)، و**التصميم** (المسؤوليات والتركيب واضحان)، و**حد التمثيل** (لا يكشف نص التصحيح والبيانات المتسلسلة إلا المقصود)، و**التحقق** (تُختبر المسارات الإيجابية والسلبية)، و**الاستدلال** (يُشرح اختيار الصنف وأي خيار `eq` أو `order` أو `frozen` بدقة). تعني 4/5 أنك مستعد للمتابعة؛ وإلا فراجع المسار الذي يحتوي المعيار الضعيف.

---

## الخلاصة
تساعدك البرمجة كائنية التوجه في بايثون على تمثيل الكيانات الحقيقية بوضوح، وجمع البيانات والسلوك، وتطبيق أنماط مثل الوراثة والتركيب والخصائص. ومع التدريب ستعرف متى تستخدم الأصناف التقليدية بدلاً من `dataclasses`.

## تأمل ختامي
يُعد بناء أصناف حسنة التصميم خطوة أساسية نحو المشاريع الأكبر. خذ وقتك للتدرب، واكتب الاختبارات، وأبقِ كل صنف مركزاً على مسؤولية واحدة. وفي فصول لاحقة ستندمج هذه الأجزاء في تطبيقات كاملة.

</div>
