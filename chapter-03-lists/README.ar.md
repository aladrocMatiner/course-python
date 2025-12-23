<div dir="rtl">

# الفصل 3 · القوائم (Lists)

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم ما هي القائمة، كيف نصل إلى العناصر باستخدام الفهارس (indexes)، وكيف نضيف/نحذف/نرتّب العناصر. سنرى أخطاء شائعة مثل `IndexError` وكيف نتجنبها.

## أفكار مهمة
- الفهرس يبدأ من 0.
- `-1` يعني آخر عنصر.
- أهم الدوال: `append`, `insert`, `pop`, `remove`, `sort`.

---

## مثال سريع
```python
bicycles = ["trek", "cannondale", "redline", "specialized"]
print(bicycles[0])
print(bicycles[-1])
```

مثال بأسماء:
```python
names = ["Noor", "Frej", "Taha"]
print(names[0])
print(f"مرحبا، {names[1]}!")
```

---

## إضافة وحذف
```python
motorcycles = ["honda", "yamaha", "suzuki"]
motorcycles.append("ducati")
motorcycles.insert(0, "victory")
last = motorcycles.pop()
motorcycles.remove("yamaha")
```

---

## ترتيب
```python
cars = ["bmw", "audi", "toyota", "subaru"]
print(sorted(cars))
cars.sort(reverse=True)
```

---

## ملخص
القوائم تسمح لك بحمل “مجموعة” من القيم بدل متغير واحد. في الفصل التالي سنتعلم القواميس (Dictionaries) وهي أساس JSON.

</div>
