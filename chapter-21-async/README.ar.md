<div dir="rtl">

# الفصل 21 · مقدمة لطيفة إلى `asyncio`

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم الأساسيات: `async`/`await`، تشغيل عدة مهام بـ `gather`، وكيفية التعامل مع الأخطاء.

---

## مثال async بسيط
```python
import asyncio

async def saludar(nombre):
    await asyncio.sleep(1)
    return f"Hola {nombre}"

async def main():
    print(await saludar("Ada"))

asyncio.run(main())
```

---

## عدة مهام
```python
import asyncio

async def procesar(usuario):
    await asyncio.sleep(1)
    return f"Listo {usuario}"

async def main():
    resultados = await asyncio.gather(procesar("Ada"), procesar("Linus"))
    print(resultados)
```

---

## ملخص
الـ async مفيد عندما تنتظر I/O (شبكة/قاعدة بيانات). ليس كل شيء يحتاجه، لكنه قد يجعل البرامج أكثر كفاءة.

</div>
