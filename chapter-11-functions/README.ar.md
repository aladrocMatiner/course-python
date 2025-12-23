<div dir="rtl">

# الفصل 11 · الدوال (Functions) وتمرير الدوال كمعطيات

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم كتابة دوال واضحة، استخدام قيم افتراضية، وفكرة مهمة: في بايثون الدوال “قيم” يمكن تخزينها وتمريرها كوسيط (مثل callbacks) وبناء pipelines بسيطة.

---

## دالة بسيطة
```python
def calcular_total(items):
    """Suma los precios en una lista de items."""
    total = 0
    for item in items:
        total += item
    return total
```

---

## تمرير دالة كوسيط
```python
def procesar_items(items, transformacion):
    return [transformacion(item) for item in items]

procesar_items(["noor", "frej"], str.upper)
```

---

## دالة تُرجِع دالة (Closure)
```python
def crear_multiplicador(factor):
    def multiplicar(valor):
        return valor * factor
    return multiplicar
```

---

## ملخص
هذه الأفكار تساعدك على بناء كود مرن وقابل لإعادة الاستخدام. الفصل التالي: الكائنات والكلاسات (OOP).

</div>
