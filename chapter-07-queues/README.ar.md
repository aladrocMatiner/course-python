<div dir="rtl">

# الفصل 7 · الصفوف والمكدسات باستخدام `collections.deque`

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنتعلم `deque` لبناء Queue (FIFO) وStack (LIFO) و“نافذة” منزلقة. `deque` أسرع من list عندما تحتاج إزالة عناصر من البداية.

---

## Queue (FIFO)
```python
from collections import deque

q = deque()
q.append("a")
q.append("b")
print(q.popleft())  # a
```

---

## Stack (LIFO)
```python
from collections import deque

s = deque()
s.append("deploy")
s.append("rollback")
print(s.pop())
```

---

## ملخص
`deque` ممتاز للصفوف والمكدسات والـ buffers. الفصل التالي: الشروط والمنطق (if/else, and/or, ternary).

</div>
