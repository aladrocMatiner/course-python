<div dir="rtl">

# الفصل 21 · تزامن لطيف: مقدمة إلى `asyncio`

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنستكشف سبب الحاجة إلى التزامن، والفرق بين الخيوط والبرمجة غير المتزامنة، ثم نبني مهام صغيرة باستخدام `asyncio`. سنحاكي استدعاءات API بطيئة ونرى كيف تتيح `await` للبرنامج إحراز تقدم من دون حجب التنفيذ كله.

## مسار التعلّم
1. **الدافع: المهام التي تنتظر عمليات الإدخال والإخراج**.
2. **أساسيات `async` و`await`**.
3. **`asyncio.sleep` و`gather` و`create_task`**.
4. **الأخطاء الشائعة وإلغاء المهام**.
5. **مستوى إضافي اختياري: HTTP غير المتزامن بمكتبات خارجية**.

## أهداف التعلّم
- فهم الفرق بين عمل المعالج CPU وعمل الإدخال والإخراج I/O.
- كتابة دوال `async def` واستخدام `await`.
- تشغيل عدة مهام «في الوقت نفسه» باستخدام `asyncio.run` و`gather`.
- معالجة الاستثناءات داخل المهام غير المتزامنة.

## لماذا يهم هذا؟
تنتظر الخدمات الحديثة كثيرًا استجابات خارجية من واجهات API أو قواعد البيانات. تتيح البرمجة غير المتزامنة استغلال وقت الانتظار في إنجاز أعمال أخرى.

### مغامرة صغيرة
تخيّل أنك تعمل في مقهى. أثناء انتظار آلة القهوة تستطيع تقديم الماء أو أخذ طلب آخر. هذا ما تفعله `asyncio`: عندما تكون مهمة «قيد الطهي»، تنتقل إلى مهمة أخرى بدل الوقوف أمام الآلة.

### جملة مهمة واحدة
من الطبيعي أن تبدو الفكرة غريبة في البداية. والفكرة الأساسية اليوم هي: **عندما تنتظر مهمة ما**، يستطيع برنامجك متابعة التقدم في مكان آخر.

## المتطلبات المسبقة
الفصول السابقة الموصى بها: 10, 11, 14.
استخدم CPython 3.11+ في بيئة محلية مؤقتة, وأبقِ البيانات والأسرار والخدمات بعيدًا عن الأنظمة الحقيقية.

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

## 2. تشغيل المهام بتزامن

```python illustrative
async def procesar(usuario):
    await asyncio.sleep(1)
    return f"Listo {usuario}"

async def main():
    usuarios = ["Noor", "Frej", "Taha"]
    tareas = [asyncio.create_task(procesar(u)) for u in usuarios]
    for tarea in tareas:
        print(await tarea)

asyncio.run(main())
```

- تبدأ جميع المهام في وقت متقارب جدًا.

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

- تعيد `gather` قائمة النتائج بالترتيب.

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

- عالج الاستثناءات كما تفعل في الدوال العادية، لكن مع `await`.

---

## تمارين موجّهة (مع TODO)
1. **21-1 · مؤقّت متزامن**
   ```python todo
   # TODO 1: launch 3 tasks that sleep different times and observe the order
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

2. **21-2 · محاكي API من دون إنترنت**
   ```python todo
   # TODO 1: create async def fake_get(url): await asyncio.sleep(1); return {"url": url, "ok": True}
   # TODO 2: use asyncio.gather to request 3 "urls" concurrently
   # TODO 3: print the result list
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

3. **21-3 · معالجة الإلغاء**
   ```python todo
   # TODO 1: cancel a task with task.cancel()
   # TODO 2: handle asyncio.CancelledError
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

---

## أخطاء شائعة
- نسيان `await` والحصول على كائنات `coroutine` بدل النتائج.
- استدعاء `asyncio.run` داخل دالة غير متزامنة تعمل بالفعل؛ وهذا غير مسموح.
- استخدام استدعاءات حاجبة مثل `requests` داخل دوال غير متزامنة، فتفقد الفائدة.

---

## حلول مشروحة
1. **المؤقّت**: توضح مدد `asyncio.sleep` المختلفة أن المهام تنتهي وفق مدة كل واحدة.
2. **محاكي API**: تعيد `fake_get` قاموسًا بعد الانتظار، وتجمع `asyncio.gather` النتائج كلها في قائمة.
3. **الإلغاء**: يطلق `task.cancel()` الاستثناء `CancelledError`، ويمكنك التقاطه لتنظيف الموارد.

---

## الخلاصة
باستخدام `asyncio` تستطيع تنسيق المهام التي تنتظر الإدخال والإخراج من دون حجب البرنامج كله، وهو تمهيد لأطر غير متزامنة مثل FastAPI.

## نقطة تحقق ومعايير تقييم
- **الصحة**: تطابق النتيجة عقد الوحدة.
- **الوضوح**: تُفهم الأسماء والمسؤوليات من القراءة الأولى.
- **الأخطاء**: يُختبر مسار ناجح وحالة حدّية ومسار تعافٍ.
- **التحقق**: تعمل الأمثلة والتمارين في بيئة نظيفة.
- **الشرح**: تستطيع تبرير القرارات ومخاطرها.

## تأمل ختامي
استخدم هذه المقدمة للتعرّف إلى المواضع التي تفيد فيها البرمجة غير المتزامنة. ليست كل مهمة بحاجة إليها، لكنها قد تجعل خدماتك أكثر كفاءة عندما تستخدمها في موضعها الصحيح.

</div>
