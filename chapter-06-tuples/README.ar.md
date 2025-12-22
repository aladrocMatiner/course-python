<div dir="rtl">

# الفصل 6 · Tuples وعدم القابلية للتغيير

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم `tuple`: قيم مرتبة وخفيفة وغالبًا “لا تتغير”. مفيدة للإحداثيات، وإرجاع أكثر من قيمة من دالة، وكـ مفاتيح في القواميس.

---

## List vs tuple
```python
punto_lista = [10, 20]
punto_tupla = (10, 20)

punto_lista[0] = 99
# punto_tupla[0] = 99  # TypeError
```

---

## Unpacking
```python
coordenada = (41.40338, 2.17403)
latitud, longitud = coordenada
```

---

## إرجاع قيم متعددة
```python
def dividir_y_residuo(dividendo, divisor):
    if divisor == 0:
        raise ZeroDivisionError("Divisor no puede ser cero")
    return dividendo // divisor, dividendo % divisor
```

---

## ملخص
tuples تساعدك على التعبير عن بيانات “لا يجب أن تتغير”. الفصل التالي: `deque` للصفوف (queues) والمكدسات (stacks).

</div>
