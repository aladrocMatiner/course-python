<div dir="rtl">

# الفصل 19 · HTTP وواجهات API أساسية باستخدام Python

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنستهلك واجهات API باستخدام `requests`، ونرسل بيانات JSON، ونتعامل مع استجابات HTTP وأخطائها، ثم نبني خادمًا محليًا صغيرًا باستخدام `http.server`. وحتى إذا لم يتوفر اتصال بالإنترنت، تستطيع التدريب بالكامل عبر الخادم المحلي.

## مسار التعلّم
1. **مراجعة HTTP: الأفعال ورموز الحالة**.
2. **عميل باستخدام `requests`**.
3. **إرسال البيانات: JSON والترويسات**.
4. **الأخطاء وإعادة المحاولة البسيطة**.
5. **خادم أساسي باستخدام `http.server`**.
6. **ممارسات جيدة: المهل الزمنية والتسجيل**.

## أهداف التعلّم
- إجراء طلبات GET وPOST وتحليل الاستجابات.
- إرسال حمولات JSON ومصادقة بسيطة.
- معالجة أخطاء HTTP برسائل مفهومة.
- إنشاء خادم محلي صغير لمحاكاة نقاط النهاية.

## لماذا يهم هذا؟
تتواصل خدمات الخلفية عبر HTTP. وفهم استهلاك واجهات API وعرضها ضروري قبل الانتقال إلى أطر العمل المتقدمة.

### مغامرة صغيرة
تخيّل HTTP خدمة البريد الخاصة بالإنترنت. كل طلب رسالة أو طرد له عنوان ومرسل وطابع. عندما تتعلّم إرسال الرسائل واستقبالها تصبح «ساعي بريد رقميًا» يصل التطبيقات كما يصل البريد بين المدن.

## المتطلبات المسبقة
الفصول السابقة الموصى بها: 13, 14, 16.
استخدم CPython 3.11+ في بيئة محلية مؤقتة, وأبقِ البيانات والأسرار والخدمات بعيدًا عن الأنظمة الحقيقية.

---

## 1. عميل `requests`

إذا لم تكن `requests` مثبّتة، فارجع إلى الفصل 16 أو نفّذ:

```bash illustrative
pip install requests
```

```python illustrative
import requests

resp = requests.get("http://localhost:8000/health", timeout=5)
print(resp.status_code)
print(resp.json())
```

- يبيّن `status_code` نجاح الطلب بالرمز 200 أو وجود خطأ ضمن 4xx أو 5xx.
- تفك `.json()` ترميز جسم الاستجابة على أنه JSON.

### نظرية HTTP في 60 ثانية
- **GET**: «أعطني معلومات»، أي قراءة.
- **POST**: «هذه بيانات»، أي إنشاء أو إرسال.
- **200**: الطلب ناجح.
- **400**: يوجد خطأ في طلبك.
- **404**: المسار غير موجود.
- **500**: خطأ في الخادم.

لا تحتاج إلى حفظ كل شيء الآن. تذكّر فقط أن 200 جيد، وأن 4xx و5xx يعنيان وجود مشكلة.

إذا لم يتوفر الإنترنت الآن فلا بأس؛ انتقل إلى القسم 4 وجرّب الخادم المحلي.

### GET مع معاملات الاستعلام
```python illustrative
params = {"query": "python"}
resp = requests.get("http://localhost:8000/search", params=params, timeout=5)
```

---

## 2. إرسال JSON عبر POST

```python illustrative
payload = {"email": "noor@example.com", "rol": "admin"}
resp = requests.post("http://localhost:8000/echo", json=payload, timeout=5)
```

- يتولى المعامل `json=` التسلسل تلقائيًا.
- للواجهات التي تتطلب ترويسات، يمكنك تمرير `headers={"Authorization": "Bearer token"}`.

### المهل الزمنية ومعالجة الأخطاء
```python illustrative
try:
    resp = requests.get("http://localhost:8000/health", timeout=5)
    resp.raise_for_status()
except requests.exceptions.Timeout:
    print("The API took too long")
except requests.exceptions.HTTPError as exc:
    print("Error HTTP", exc.response.status_code)
```

---

## 3. إعادة محاولة بسيطة

```python illustrative
url = "http://localhost:8000/health"

for intento in range(3):
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        break
    except requests.exceptions.RequestException as exc:
        print("Fallo", exc)
else:
    raise RuntimeError("Servicio no disponible")
```

- يعمل بلوك `else` إذا انتهت الحلقة من دون الوصول إلى `break`.

---

## 4. خادم محلي سريع

```python illustrative
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class EchoHandler(BaseHTTPRequestHandler):
    MAX_BODY = 1_000_000

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/health") or self.path.startswith("/search"):
            self._send_json(200, {"ok": True})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "invalid content length"})
            return
        if length > self.MAX_BODY:
            self._send_json(413, {"error": "payload too large"})
            return
        data = self.rfile.read(length)
        try:
            payload = json.loads(data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "invalid json"})
            return
        self._send_json(200, {"ok": True, "received": payload})

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), EchoHandler)
    print("Escuchando en http://localhost:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Deteniendo servidor")
    finally:
        server.server_close()
```

- يفيد هذا الخادم في اختبار العملاء من دون واجهات API خارجية.

### اختبار الخادم بعميل في طرفية أخرى
أبقِ الخادم قيد التشغيل، ثم نفّذ هذا العميل:

```python illustrative
import requests

resp = requests.post("http://localhost:8000/echo", json={"mensaje": "hola"}, timeout=5)
print(resp.status_code)
print(resp.json())
```

الناتج المتوقّع:
```text illustrative
200
{'ok': True, 'received': {'mensaje': 'hola'}}
```

---

## تمارين موجّهة (مع TODO)
1. **19-1 · استهلاك واجهة API المحلية**
   ```python todo
   # TODO 1: use requests.get to fetch http://localhost:8000/health with timeout=5
   # TODO 2: verify status 200 and print the JSON
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

2. **19-2 · POST مع تحقق**
   ```python todo
   # TODO 1: send a payload to http://localhost:8000/echo
   # TODO 2: verify the response JSON matches what you sent
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

3. **19-3 · العميل والخادم**
   ```python todo
   # TODO 1: run the EchoHandler server
   # TODO 2: create a client that sends it data
   ```
   *تلميح*: ابدأ من أقرب مثال، وتحقق من مسار ناجح وحالة حدّية والتعافي قبل قراءة الحل.

---

## أخطاء شائعة
- نسيان `timeout`، فقد يظل الاتصال عالقًا إلى أجل غير محدد.
- عدم استخدام `raise_for_status()` وافتراض نجاح كل شيء.
- كتابة مفاتيح API مباشرة في الشيفرة بدل قراءتها من متغيرات البيئة.

---

## حلول مشروحة
1. **واجهة API المحلية**: استدعِ `/health` بمهلة زمنية، واستخدم `raise_for_status()` ثم حلّل `resp.json()`.
2. **POST**: قارن `resp.json()["received"]` بالحمولة المرسلة.
3. **العميل والخادم**: تحقق محليًا من 200 و400 و413 ثم أوقف الخادم عبر Ctrl-C.

---

## الخلاصة
أصبحت قادرًا على استهلاك واجهات API أساسية وعرضها في Python، مع معالجة الأخطاء والمهل الزمنية.

## نقطة تحقق ومعايير تقييم
- **الصحة**: تطابق النتيجة عقد الوحدة.
- **الوضوح**: تُفهم الأسماء والمسؤوليات من القراءة الأولى.
- **الأخطاء**: يُختبر مسار ناجح وحالة حدّية ومسار تعافٍ.
- **التحقق**: تعمل الأمثلة والتمارين في بيئة نظيفة.
- **الشرح**: تستطيع تبرير القرارات ومخاطرها.

## تأمل ختامي
تمثّل هذه المهارات جسرًا إلى أطر عمل مثل Django REST Framework. تدرب ببناء خدمات صغيرة تتحدث إلى بعضها.

</div>
