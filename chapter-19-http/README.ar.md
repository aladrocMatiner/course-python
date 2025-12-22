<div dir="rtl">

# الفصل 19 · HTTP وواجهات API مع Python

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنقوم بطلب GET/POST باستخدام `requests`، إرسال JSON، فهم status codes، وبناء خادم محلي صغير بـ `http.server` للتجربة بدون إنترنت.

---

## GET
```python
import requests

resp = requests.get("https://httpbin.org/get")
print(resp.status_code)
print(resp.json())
```

---

## POST JSON
```python
payload = {"email": "ada@example.com", "rol": "admin"}
resp = requests.post("https://httpbin.org/post", json=payload)
```

---

## خادم محلي سريع
```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class EchoHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length)
        payload = json.loads(data)
        respuesta = json.dumps({"ok": True, "received": payload}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(respuesta)
```

---

## ملخص
HTTP هو “لغة” التواصل بين الخدمات. الفصل التالي: logging وإدارة الإعدادات.

</div>
