<div dir="rtl">

# الملحق B · خوارزميات أساسية: البحث في Python

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنرى ثلاث طرق للبحث: بحث خطي، بحث ثنائي، وBFS في الرسوم البيانية. وسنتكلم عن التعقيد بشكل مبسط.

---

## البحث الخطي (O(n))
```python
def busqueda_lineal(elementos, objetivo):
    for indice, valor in enumerate(elementos):
        if valor == objetivo:
            return indice
    return -1
```

---

## البحث الثنائي (O(log n) ويتطلب قائمة مرتبة)
```python
def busqueda_binaria(ordenados, objetivo):
    izquierda, derecha = 0, len(ordenados) - 1
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        valor = ordenados[medio]
        if valor == objetivo:
            return medio
        if valor < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    return -1
```

---

## BFS (O(V+E))
```python
from collections import deque

def bfs(grafo, inicio, objetivo):
    visitados = set([inicio])
    cola = deque([inicio])
    while cola:
        nodo = cola.popleft()
        if nodo == objetivo:
            return True
        for vecino in grafo.get(nodo, []):
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append(vecino)
    return False
```

---

## ملخص
اختيار الخوارزمية المناسبة يوفر وقتًا كبيرًا عندما تكبر البيانات: الخطي بسيط، الثنائي سريع على القوائم المرتبة، وBFS ممتاز للشبكات والعلاقات.

</div>
