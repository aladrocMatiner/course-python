<div dir="rtl">

# الفصل 21 · تزامن لطيف: مقدمة إلى `asyncio`

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنستكشف سبب الحاجة إلى التزامن، والفرق بين الخيوط والبرمجة غير المتزامنة، ثم نبني مهام صغيرة باستخدام `asyncio`. سنحاكي استدعاءات API بطيئة ونرى كيف تتيح `await` للبرنامج إحراز تقدم من دون حجب التنفيذ كله.

## مسار التعلّم
1. **الدافع: المهام التي تنتظر عمليات الإدخال والإخراج**.
2. **أساسيات `async` و`await`**.
3. **تزامن مملوك باستخدام `TaskGroup`**، ثم `gather` للنتائج المرتبة.
4. **المهل والإخفاقات والإلغاء والتنظيف**.
5. **مستوى إضافي اختياري: HTTP غير المتزامن بمكتبات خارجية**.

## أهداف التعلّم
- فهم الفرق بين عمل المعالج CPU وعمل الإدخال والإخراج I/O.
- كتابة دوال `async def` واستخدام `await`.
- التمييز بين مهام asyncio التعاونية وخيوط نظام التشغيل.
- امتلاك العمل المتزامن عبر `TaskGroup` وتقييده باستخدام `asyncio.timeout` في Python 3.11+.
- معالجة إخفاق المهمة وإلغائها من دون ابتلاع إشارات التنظيف أو ترك عمل في الخلفية.

## لماذا يهم هذا؟
تنتظر الخدمات الحديثة كثيرًا استجابات خارجية من واجهات API أو قواعد البيانات. تتيح البرمجة غير المتزامنة استغلال وقت الانتظار في إنجاز أعمال أخرى.

### مغامرة صغيرة
تخيّل أنك تعمل في مقهى. أثناء انتظار آلة القهوة تستطيع تقديم الماء أو أخذ طلب آخر. هذا ما تفعله `asyncio`: عندما تكون مهمة «قيد الطهي»، تنتقل إلى مهمة أخرى بدل الوقوف أمام الآلة.

### جملة مهمة واحدة
من الطبيعي أن تبدو الفكرة غريبة في البداية. والفكرة الأساسية اليوم هي: **عندما تنتظر مهمة ما**، يستطيع برنامجك متابعة التقدم في مكان آخر.

### المهام ليست خيوطًا
يجدول event loop مهمة asyncio تعاونيًا، وعادةً داخل خيط واحد لنظام التشغيل. ولا تفسح المهمة المجال إلا عندما تصل إلى `await` يمكن أن تعلق التنفيذ. أما الخيط فيجدوله نظام التشغيل ويمكنه تشغيل شيفرة حاجبة باستقلال، مع مخاطر مزامنة مختلفة. لذلك يظل وضع `requests.get()` أو عمل CPU كثيف مباشرة داخل `async def` حاجبًا لخيط event loop؛ استخدم مكتبة غير متزامنة، أو قسّم عمل CPU بصورة مناسبة، أو اعزل استدعاءً حاجبًا عن قصد عبر `asyncio.to_thread` حين تكون المقايضة مبررة.

## المتطلبات المسبقة
- الدوال والاستثناءات والحلقات، والتمييز الواضح بين عمل CPU وانتظار I/O.
- CPython 3.11 أو أحدث؛ كل مثال مطلوب محلي ويستخدم المكتبة القياسية فقط.

## توقّع قبل التشغيل
قبل انتظار أول coroutine، توقّع متى يبدأ جسمها وأي عبارة يمكن أن تتيح لمهمة أخرى أن تعمل. بعد تشغيل المثال المحدود، قارن الترتيب الملاحظ بتوقّعك من دون اعتبار sleep ثابت دليلًا على الجدولة.

---

## 1. دالة غير متزامنة

```python illustrative
import asyncio

async def saludar(nombre):
    await asyncio.sleep(1)
    return f"Hola {nombre}"

async def main():
    mensaje = await saludar("Noor")
    print(mensaje)

asyncio.run(main())
```

- تحاكي `asyncio.sleep` عمل إدخال وإخراج.
- تعني `await`: «انتظر هنا، لكن اسمح للمهام الأخرى بالعمل إن استطاعت».

---

## 2. امتلاك المهام المتزامنة باستخدام `TaskGroup`

```python runnable
import asyncio

async def procesar(usuario):
    await asyncio.sleep(0)
    return f"Listo {usuario}"

async def main():
    usuarios = ["Noor", "Frej", "Taha"]
    async with asyncio.TaskGroup() as group:
        tareas = [group.create_task(procesar(u)) for u in usuarios]
    print([tarea.result() for tarea in tareas])

asyncio.run(main())
```

- يمتلك السياق كل مهمة منشأة ولا يخرج حتى تنتهي كلها. إذا أخفقت مهمة ابنة، تلغي `TaskGroup` الأخوات غير المنتهية، وتنتظر تنظيفها، وترفع `ExceptionGroup`. التقط إخفاقًا ورقيًا متوقعًا عبر `except*` خارج المجموعة، ولا تتجاهل الإخفاقات غير المتوقعة.

---

## 3. `asyncio.gather`

```python runnable
import asyncio

async def procesar(usuario):
    await asyncio.sleep(0)
    return f"Listo {usuario}"

async def main():
    resultados = await asyncio.gather(
        procesar("Noor"),
        procesar("Frej"),
    )
    print(resultados)

asyncio.run(main())
```

- تعيد `gather` قائمة النتائج بترتيب الإدخال. تظل مفيدة حين يكون عقد النتائج هذا هو الهدف، لكن `TaskGroup` توضح عمر المهمة وتنظيف الأخوات للعمل المتزامن المطلوب.

---

## 4. الأخطاء داخل المهام

```python runnable
import asyncio

async def puede_fallar():
    raise ValueError("Oops")

async def main():
    try:
        await puede_fallar()
    except ValueError as exc:
        print("Capturado", exc)

asyncio.run(main())
```

- عالج الاستثناءات كما تفعل في الدوال العادية، لكن مع `await`.

### تقييد مجموعة باستخدام `asyncio.timeout`
```python runnable
import asyncio

async def slow(name, events):
    events.append(f"{name}:start")
    try:
        await asyncio.sleep(10)
    finally:
        events.append(f"{name}:cleanup")

async def main():
    events = []
    try:
        async with asyncio.timeout(0.02):
            async with asyncio.TaskGroup() as group:
                group.create_task(slow("a", events))
                group.create_task(slow("b", events))
    except TimeoutError:
        events.append("timeout:handled")
    print(sorted(events))

asyncio.run(main())
```

تلغي المهلة العملية الحالية؛ وتنشر مجموعة المهام الإلغاء إلى أبنائها وتنتظر كتلتي `finally`. التقط `TimeoutError` خارج سياق المهلة. ويتبع إخفاق الابنة قاعدة الملكية نفسها: تُلغى الأخوات وتُنظف قبل أن تبلغ المجموعة عن الإخفاق.

### الإلغاء وتنظيف الموارد
```python runnable
import asyncio

async def trabajo_largo():
    try:
        await asyncio.sleep(10)
    finally:
        print("Limpieza completada")

async def main():
    tarea = asyncio.create_task(trabajo_largo())
    await asyncio.sleep(0)
    tarea.cancel()
    try:
        await tarea
    except asyncio.CancelledError:
        print("Tarea cancelada")

asyncio.run(main())
```

- الإلغاء مسار تحكم يمكن التعافي منه: استخدم `finally` لتحرير الموارد، وانتظر المهمة الملغاة، وعالج `CancelledError` عند حد التنسيق. لا تلتقط `CancelledError` داخل العاملة الملغاة لتواصل كأن شيئًا لم يحدث؛ دعه ينتشر بعد التنظيف.

تغطي [وحدة واختبارات التزامن البنيوي المرافقة](structured_async.py) النجاح وإخفاق الابنة والمهلة وإلغاء الأخوات والتنظيف وغياب المهام المتبقية. من `chapter-21-async/` شغّل `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

---

## تمارين موجّهة (مع TODO)
1. **21-1 · مؤقّت متزامن**
   ```python todo
   # TODO 1: launch 3 owned tasks in a TaskGroup and observe completion vs result order
   ```
   *تلميح*: احتفظ بكائنات task التي أنشأتها المجموعة، واقرأ `.result()` بعد خروج السياق فقط.

2. **21-2 · محاكي API من دون إنترنت**
   ```python todo
   # TODO 1: create async def fake_get(url): await asyncio.sleep(1); return {"url": url, "ok": True}
   # TODO 2: use asyncio.gather to request 3 "urls" concurrently
   # TODO 3: print the result list
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

3. **21-3 · معالجة الإلغاء**
   ```python todo
   # TODO 1: bound a TaskGroup with asyncio.timeout
   # TODO 2: give each worker a finally cleanup marker
   # TODO 3: verify no child remains after TimeoutError
   ```
   *تلميح*: التقط `TimeoutError` خارج سياق المهلة، وضع تنظيف الموارد في كتلة `finally` لكل مهمة.

---

## أخطاء شائعة
- نسيان `await` والحصول على كائنات `coroutine` بدل النتائج.
- استدعاء `asyncio.run` داخل دالة غير متزامنة تعمل بالفعل؛ وهذا غير مسموح.
- استخدام استدعاءات حاجبة مثل `requests` داخل دوال غير متزامنة، فتفقد الفائدة.
- إنشاء مهام من دون مالك والعودة بينما ما زالت تعمل.
- ابتلاع `CancelledError` داخل العاملة، مما قد يكسر تنظيف `TaskGroup` والمهلة.

---

## حلول مشروحة
1. **المؤقّت**: أنشئ كل المؤقتات داخل `TaskGroup`؛ بعد خروج السياق تكون كل مهمة قد انتهت ويمكن قراءة `.result()` بأمان. سجّل ترتيب الانتهاء منفصلًا إن كان هذا ما تريد ملاحظته.
2. **محاكي API**: تعيد `fake_get` قاموسًا بعد الانتظار، وتجمع `asyncio.gather` النتائج كلها في قائمة.
3. **الإلغاء**: تلغي `asyncio.timeout` العملية المملوكة؛ تنظف كل عاملة في `finally`، وتنتظر المجموعة جميع الأخوات، ويلتقط المنسق `TimeoutError` بعد السياق. تحقق من أن `asyncio.all_tasks()` لا تحتوي مهمة غير مكتملة سوى مهمة الاختبار الحالية.

---

## الخلاصة
باستخدام `asyncio` تستطيع تنسيق المهام التي تنتظر الإدخال والإخراج من دون حجب البرنامج كله، وهو تمهيد لأطر غير متزامنة مثل FastAPI.

## نقطة تحقق ومعايير تقييم
- **الصحة**: يمتلك event loop واحد المهام المتزامنة ويحافظ على ترتيب النتائج فقط حيث وُعد به.
- **الوضوح**: تُفهم الأسماء والمسؤوليات من القراءة الأولى.
- **الأخطاء**: يلغي إخفاق المهمة والمهلة الأخوات، وينتشران بصورة صحيحة، وينظفان الموارد.
- **التحقق**: شغّل كل كتلة runnable وأثبت أن النجاح والإخفاق والمهلة لا تترك مهام خلفية.
- **الشرح**: اشرح الفرق بين المهام والخيوط، ومتى يفيد async، ولماذا تزيل الاستدعاءات الحاجبة فائدته.

## تأمل ختامي
استخدم هذه المقدمة للتعرّف إلى المواضع التي تفيد فيها البرمجة غير المتزامنة. ليست كل مهمة بحاجة إليها، لكنها قد تجعل خدماتك أكثر كفاءة عندما تستخدمها في موضعها الصحيح.

</div>
