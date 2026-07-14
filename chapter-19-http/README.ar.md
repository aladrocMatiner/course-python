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
- الاستثناءات والوحدات والبيئات وJSON من الفصول 13–16.
- تثبيت `requests` في بيئة افتراضية وتوفر طرفيتين محليتين؛ تبقى حركة المرور المطلوبة كلها على `localhost`.

## توقّع قبل التشغيل
قبل بدء العميل المحلي، توقّع رمز الحالة لمسار health والاستثناء الذي ينبغي أن تراه إذا لم يكن هناك خادم يستمع. اختبر إعداد `localhost` المحدود فقط، ثم قارن النتيجتين بتوقّعك.

---

## 1. عميل `requests`

إذا لم تكن `requests` مثبّتة، فارجع إلى الفصل 16 أو نفّذ الأمر التالي. شغّل الخادم المحلي المحدود في القسم 4 قبل تنفيذ أمثلة العميل؛ لا يحتاج المسار الإلزامي إلى الإنترنت.

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
import socket
from urllib.parse import urlsplit

class EchoHandler(BaseHTTPRequestHandler):
    MAX_BODY = 1_000_000
    READ_TIMEOUT = 5

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in {"/health", "/search"}:
            self._send_json(200, {"ok": True})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if urlsplit(self.path).path != "/echo":
            self._send_json(404, {"error": "not found"})
            return
        if self.headers.get_content_type() != "application/json":
            self._send_json(415, {"error": "application/json required"})
            return

        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            self._send_json(411, {"error": "content length required"})
            return
        if not raw_length.isascii() or not raw_length.isdecimal():
            self._send_json(400, {"error": "invalid content length"})
            return
        normalized_length = raw_length.lstrip("0") or "0"
        maximum = str(self.MAX_BODY)
        if len(normalized_length) > len(maximum) or (
            len(normalized_length) == len(maximum) and normalized_length > maximum
        ):
            self._send_json(413, {"error": "payload too large"})
            return
        length = int(normalized_length)

        self.connection.settimeout(self.READ_TIMEOUT)
        try:
            data = self.rfile.read(length)
        except (TimeoutError, socket.timeout):
            self._send_json(408, {"error": "request body timeout"})
            return
        if len(data) != length:
            self._send_json(400, {"error": "incomplete request body"})
            return
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

- يفيد هذا الخادم في اختبار العملاء من دون واجهات API خارجية. لا يقبل العقد سوى مساري GET الدقيقين `/health` و`/search`، ومسار POST الدقيق `/echo`، ونوع الوسائط `application/json` (تُقبل معاملات مثل charset). يتطلب POST قيمة `Content-Length` عشرية ضمن `0..1_000_000` قبل أي قراءة. وتتبع الأجسام ذات الطول الغائب أو السالب أو المشوه أو المفرط، والمنتهية مهلتها أو غير المكتملة، مسارات `4xx` محدودة.

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

### التحقق من حدود الطلب
يبدأ [معالج HTTP المحدود واختبارات الانحدار](bounded_http.py) خادماً مؤقتاً على loopback، ويختبر النجاح والأطوال السالبة والمشوهة والمفرطة والمسار المجهول ونوع الوسائط الخاطئ:

```bash illustrative
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
```

نفّذ الأمر من `chapter-19-http/`. يجب أن يعيد اختبار الطول السالب `400` سريعاً؛ ويجب ألا يصل مطلقاً إلى `read(-1)` أو ينتظر إغلاق العميل للاتصال.

---

## تمارين موجّهة (مع TODO)
1. **19-1 · استهلاك واجهة API المحلية**
   ```python todo
   # TODO 1: use requests.get to fetch http://localhost:8000/health with timeout=5
   # TODO 2: verify status 200 and print the JSON
   ```
   *تلميح*: شغّل `EchoHandler` في طرفية أخرى، واستدعِ `resp.raise_for_status()` قبل `resp.json()`.

2. **19-2 · POST مع تحقق**
   ```python todo
   # TODO 1: send a payload to http://localhost:8000/echo
   # TODO 2: verify the response JSON matches what you sent
   ```
   *تلميح*: قارن `resp.json()["received"]` بالحمولة التي أرسلتها.

3. **19-3 · العميل والخادم**
   ```python todo
   # TODO 1: run the EchoHandler server
   # TODO 2: create a client that sends it data
   ```
   *تلميح*: اختبر المسار الناجح، والطول الغائب (411)، والسالب أو المشوه (400)، والمفرط (413)، ونوع الوسائط الخاطئ (415)، والمسار الخاطئ (404)، وJSON المشوه (400)، ثم أوقف الخادم باستخدام Ctrl-C.

---

## أخطاء شائعة
- نسيان `timeout`، فقد يظل الاتصال عالقًا إلى أجل غير محدد.
- عدم استخدام `raise_for_status()` وافتراض نجاح كل شيء.
- كتابة مفاتيح API مباشرة في الشيفرة بدل قراءتها من متغيرات البيئة.
- استدعاء `read()` قبل التحقق من طول غير سالب ذي حد أعلى؛ فقد تتحول القيمة السالبة إلى قراءة غير محدودة.
- قبول كل مسار أو نوع وسائط وعرض API أوسع من الموثق في الدرس من دون قصد.

---

## حلول مشروحة
1. **واجهة API المحلية**: استدعِ `/health` بمهلة زمنية، واستخدم `raise_for_status()` ثم حلّل `resp.json()`.
2. **POST**: قارن `resp.json()["received"]` بالحمولة المرسلة.
3. **العميل والخادم**: شغّل الخادم المحدود في طرفية والعميل في أخرى. تحقق من مسارات 200 و400 و404 و411 و413 و415. تحقّق من المسار ونوع الوسائط والمجال العشري قبل قراءة عدد البايتات المعلن بالضبط مع مهلة socket. ثم أوقفه عبر Ctrl-C كي يحرر `server_close()` المنفذ.

---

## الخلاصة
أصبحت قادرًا على استهلاك واجهات API أساسية وعرضها في Python، مع معالجة الأخطاء والمهل الزمنية.

## نقطة تحقق ومعايير تقييم
- **الصحة**: يستخدم عملاء GET وPOST مهلاً زمنية، ويعيد الخادم رموز الحالة المناسبة.
- **الوضوح**: المسارات وحدود الحمولة واستجابات الخطأ صريحة.
- **الأخطاء**: تحقق من النجاح، والأطوال الغائبة والسالبة والمشوهة والمفرطة، والمسار أو نوع الوسائط الخاطئ، وJSON المشوه، والتعافي عند غياب الخدمة.
- **التحقق**: شغّل العميل والخادم محلياً، ثم تأكد من تحرير المنفذ بعد الإيقاف.
- **الشرح**: اشرح لماذا تتجنب التمارين المطلوبة الخدمات العامة.

## تأمل ختامي
تمثّل هذه المهارات جسرًا إلى أطر عمل مثل Django REST Framework. تدرب ببناء خدمات صغيرة تتحدث إلى بعضها.

</div>
