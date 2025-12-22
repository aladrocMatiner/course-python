<div dir="rtl">

# الفصل 4 · القواميس (Dictionaries) — مفتاح/قيمة

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم `dict`: تخزين البيانات كـ “مفتاح → قيمة”، القراءة الآمنة بـ `get` بدل `KeyError`، وكيف نتحقق من وجود حقول مطلوبة في payloads (مثل JSON).

---

## إنشاء وقراءة
```python
usuario = {
    "username": "ada",
    "email": "ada@example.com",
    "roles": ["admin", "editor"],
}

print(usuario["username"])
print(usuario.get("timezone", "UTC"))
```

---

## دمج (Merge) وتحديث
```python
config_base = {"timeout": 5, "retries": 3}
config_usuario = {"timeout": 10, "region": "eu-west"}
config_final = config_base | config_usuario  # Python 3.9+
```

---

## التحقق من حقول مطلوبة
```python
def validar_perfil(datos):
    campos_requeridos = {"username", "email"}
    faltantes = campos_requeridos - datos.keys()
    if faltantes:
        raise ValueError(f"Faltan campos: {sorted(faltantes)}")
    return True
```

---

## ملخص
القواميس هي أساس JSON وبيانات الـ API. في الفصل التالي سننتقل إلى المجموعات (Sets) لإزالة التكرار بسرعة.

</div>
