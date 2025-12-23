<div dir="rtl">

# الفصل 10 · الحلقات (Loops) والتعقيد

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم `for` و`while` و`break`/`continue`، ونبدأ بفكرة التعقيد الزمني: O(n) و O(n²) لفهم لماذا الحلقات المتداخلة قد تكون مكلفة.

---

## `for` + `enumerate`
```python
tareas = ["instalar dependencias", "correr tests", "hacer deploy"]
for indice, tarea in enumerate(tareas, start=1):
    print(f"{indice}. {tarea}")
```

---

## `while`
```python
contador = 0
while contador < 3:
    print(contador)
    contador += 1
```

---

## حلقات متداخلة (O(n²) تقريبًا)
```python
usuarios = ["noor", "frej", "taha"]
permisos = ["ver", "editar", "borrar"]
for u in usuarios:
    for p in permisos:
        pass
```

---

## ملخص
الحلقات قوية لكنها قد تصبح بطيئة عندما تكبر البيانات. الفصل التالي: الدوال (Functions) وتمرير الدوال كمعطيات.

</div>
