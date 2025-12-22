# Kapitel 7 · Köer och stackar med `collections.deque`

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Vi använder `deque` för köer (FIFO), stackar (LIFO) och glidande fönster. Det är snabbare än listor när du behöver ta bort från början.

---

## Varför `deque`?
`list.pop(0)` är O(n). `deque.popleft()` är O(1).

---

## FIFO‑kö
```python
from collections import deque

q = deque()
q.append("a")
q.append("b")
print(q.popleft())  # a
```

---

## LIFO‑stack
```python
from collections import deque

s = deque()
s.append("deploy")
s.append("rollback")
print(s.pop())
```

---

## Sammanfattning
`deque` är perfekt för köer, stackar och buffertar. Nästa kapitel: villkor (if/else), logik och ternary.
