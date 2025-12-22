<div dir="rtl">

# الفصل 13 · الملفات و الـ Streams

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم قراءة وكتابة ملفات النصوص والملفات الثنائية، واستخدام `with` لإغلاق الملفات دائمًا، وكيف نتعامل مع ملفات كبيرة بقراءة سطر‑بسطر أو chunks.

---

## قراءة ملف نصي
```python
with open("notas.txt", mode="r", encoding="utf-8") as fh:
    for linea in fh:
        print(linea.strip())
```

---

## كتابة ملف
```python
nuevas_notas = ["Aprender archivos", "Practicar streams"]
with open("notas.txt", mode="w", encoding="utf-8") as fh:
    for nota in nuevas_notas:
        fh.write(nota + "\n")
```

---

## نسخ ملف ثنائي على شكل chunks
```python
with open("entrada.dat", "rb") as origen, open("salida.dat", "wb") as destino:
    while chunk := origen.read(8192):
        destino.write(chunk)
```

---

## ملخص
الملفات أساس الإعدادات والـ logs والتصدير. الفصل التالي: الاستثناءات (Exceptions).

</div>
