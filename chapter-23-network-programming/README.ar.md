<div dir="rtl">

# الفصل 23 · برمجة الشبكات باستخدام Python

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية (الحالية)

في هذا الفصل ستطوّر مشروع قياس محلياً واحداً: من أول صدى TCP إلى مركز غير متزامن ذي موارد محدودة. تحتاج إلى Python 3.11 أو أحدث، ولا تحتاج إلى خبرة سابقة بالشبكات أو اتصال بالإنترنت أو صلاحيات إدارية أو حزم خارجية.

تستمع كل الخوادم إلى loopback فقط: `127.0.0.1` أو `::1` في امتداد IPv6 الاختياري. لا تغيّرها إلى واجهة عامة أثناء التعلّم. فحص الشبكات والتقاط الحزم وraw sockets وspoofing والاستغلال وصنع التشفير والنشر العام كلها خارج نطاق الفصل.

## النتائج والمتطلبات والمسارات

ستتعلم الانتقال من النص إلى bytes، واختيار TCP أو UDP، وتأطير بروتوكول والتحقق منه، وخدمة عدة عملاء دون حالة غير محدودة، وتطبيق backpressure في `asyncio`، والتحقق من هوية TLS، واختبار الأعطال والإغلاق.

راجع فقط ما تحتاج إليه:

- [Streams وcontext managers في الفصل 13](../chapter-13-files/README.ar.md): تنظيف الموارد بشكل حتمي.
- [الاستثناءات في الفصل 14](../chapter-14-exceptions/README.ar.md): التعافي من الأخطاء المتوقعة.
- [الاختبارات الآلية في الفصل 18](../chapter-18-testing/README.ar.md): الإعداد والتنفيذ والتحقق.
- [HTTP في الفصل 19](../chapter-19-http/README.ar.md): HTTP بروتوكول تطبيق وليس النقل نفسه.
- [التسجيل في الفصل 20](../chapter-20-logging/README.ar.md): تشخيص مفيد دون كشف payload.
- [`asyncio` في الفصل 21](../chapter-21-async/README.ar.md): coroutines والمهام والإلغاء.

| المسار | الوقت | نقطة البداية | النتيجة القابلة للملاحظة |
|---|---:|---|---|
| الأساسي | جلستان × 45–60 دقيقة | الدوال والاستثناءات | صدى TCP محلي مفهوم |
| المتوسط | 3 جلسات × 45–60 دقيقة | نقطة التحقق الأساسية | بروتوكول متسلسل مختبر ومقارنة UDP |
| المتقدم | 3–4 جلسات × 45–60 دقيقة | النقطة المتوسطة والفصل 21 | مركز غير متزامن محدود متعدد العملاء |

TLS وIPv6 امتدادان متقدمان اختياريان. كل نقطة تحقق سابقة مفيدة من دونهما.

## المسار الأساسي — من رسالة إلى stream من TCP

### 1. مفردات شبكة صغيرة

**العميل** يبدأ المحادثة، و**الخادم** ينتظرها. **المضيف** جهاز أو بيئة شبكة. يربط نظام أسماء النطاقات (**DNS**) الأسماء بالعناوين. يحدد **عنوان IP** واجهة، بينما يختار **المنفذ** برنامجاً على المضيف. الـ **socket** نقطة نهاية يوفرها نظام التشغيل. **البروتوكول** مجموعة قواعد الرسائل المشتركة.

تخيّل رسالة ورقية: عنوان IP هو المبنى، والمنفذ هو الغرفة، والبروتوكول هو النموذج المتفق عليه. تنتهي الاستعارة هنا؛ ينقل TCP stream مرتبة من bytes وليس مظاريف منفصلة.

تفصل الطبقات المسؤوليات. ينقل IP الحزم، ويقدم TCP أو UDP خصائص النقل، ويقع HTTP وتنسيق القياس في طبقة التطبيق. ارجع إلى الفصل 19 لاستهلاك HTTP APIs؛ هنا نبني بروتوكولاً صغيراً لفهم الطبقة الأدنى.

#### توقّع ثم نفّذ ولاحظ

تتبادل sockets في Python قيماً من **bytes**. يحتاج النص إلى encoding متفق عليه. توقّع ناتج `len(encoded)`:

<!-- bookcheck: expect="temperature=21.5\n16" timeout=2 -->
```python runnable
text = "temperature=21.5"
encoded = text.encode("utf-8")
print(encoded.decode("utf-8"))
print(len(encoded))
```

ستشاهد النص نفسه ثم `16`. تشغل أحرف ASCII هنا byte واحداً، لكن ذلك لا ينطبق على كل الأحرف.

**عدّل:** استخدم `café` وتوقّع عدد الأحرف وbytes. **تلميح:** قارن `len(text)` بـ `len(text.encode("utf-8"))`. الحل المفسّر: الحرف `é` حرف Python واحد لكنه يحتاج إلى اثنين من UTF-8 bytes.

**المسار الناجح:** يستخدم الطرفان UTF-8. **الحالة الحدية:** قد يمتد حرف واحد عبر عدة bytes. **خطأ قابل للتعافي:** تسبب bytes غير الصالحة `UnicodeDecodeError`؛ ارفض frame عند حد البروتوكول ولا تخمّن encoding.

### 2. العناوين والأسماء والتجارب المحلية

`localhost` اسم محلي. loopback في IPv4 هو `127.0.0.1` وفي IPv6 هو `::1`. تعيد `socket.getaddrinfo()` مرشحين بدلاً من افتراض address family. لا يتصل المثال بأي مضيف عام.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/address_demo.py check=network:network-suite -->
```python source-ref
socket.getaddrinfo("localhost", 0, type=socket.SOCK_STREAM)
```

نفّذ من جذر المستودع:

```text illustrative
python -B chapter-23-network-programming/examples/telemetry/address_demo.py
```

تعتمد العناوين وترتيبها على البيئة. يذكر السطر الأخير هل نجح bind على IPv6 loopback؛ يبقى IPv4 هو fallback المطلوب.

قد تتطلب المنافذ دون 1024 صلاحيات. يستخدم صدى الطرفيتين `65432`، بينما تربط الاختبارات المنفذ `0` ليختار نظام التشغيل ephemeral port حراً. عند `Address already in use` اختر منفذاً غير مميز آخر أو `0` في الكود المنسق. لا توقف عملية لا تعرفها عشوائياً.

### 3. أول تبادل TCP حاجب

يقدم TCP stream مرتبة وإعداد اتصال وEOF. الخادم: create → bind → listen → accept → receive/send → close. العميل: create → connect → send/receive → close. يستخدم الطرفان timeouts وcontext managers كي تغلق الموارد حتى عند الفشل.

توقّع أي طرفية تنتظر أولاً ثم نفّذ:

```text illustrative
# Terminal 1
python -B chapter-23-network-programming/examples/telemetry/echo.py server --port 65432

# Terminal 2, within thirty seconds
python -B chapter-23-network-programming/examples/telemetry/echo.py client --port 65432 --text "hello, network"
```

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/echo.py check=network:network-suite -->
```python source-ref
with socket.create_connection(("127.0.0.1", port), timeout=30.0) as connection:
    connection.sendall(text.encode("utf-8"))
```

لاحظ النص العائد وانتهاء العمليتين. تعني `recv()` الفارغة EOF. ترسل `sendall()` كل bytes أو ترفع خطأ، لكنها لا تصنع حدود رسائل.

**تمرين موجّه:** أرسل `å` في `--text`. **TODO:** توقّع UTF-8 bytes. **تلميح:** يجمع العميل chunks قبل decode. **النجاح:** يعود النص نفسه وتنتهي العمليتان. يعمل الحل لأنه لا يفك ترميز chunk جزئي.

**خطأ شائع:** تشغيل العميل أولاً يعطي `ConnectionRefusedError`. شغّل listener وتحقق من المنفذ ثم أعد المحاولة. يعني timeout أن الطرف لم يتقدم؛ سجّل ذلك ونظّف الموارد من دون إعادة غير محدودة.

### نقطة التحقق الأساسية

ينبغي أن تشرح bytes والفرق بين العنوان والمنفذ ودورة TCP، وأن تكمل صدى loopback. المنتج القابل للتشغيل هو صدى محدود في طرفيتين. بعد ذلك نضيف حدود الرسائل والتحقق.

## المسار المتوسط — تصميم عقد حقيقي للرسائل

### 4. TCP ليس قائمة رسائل: التأطير

قد تصل `sendall()` واحدة عبر عدة استدعاءات `recv()`، وقد تصل عدة عمليات إرسال معاً. توقّع فشل `json.loads(connection.recv(4096))`: JSON المجزأ ناقص، والمندمج يحتوي عدة مستندات.

نستخدم JSON المحدد بأسطر (**NDJSON**): كائن UTF-8 واحد ثم `\n`. يحتفظ `NDJSONDecoder` بـ buffer تزايدي، ويعيد كل سطر كامل، ويبقي اللاحقة الناقصة فقط. يسمح بـ 65,536 byte قبل newline؛ يؤدي byte رقم 65,537 من دون delimiter إلى فشل مغلق ومسح buffer.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/protocol.py check=network:network-suite -->
```python source-ref
messages = decoder.feed(chunk)  # zero, one, or several complete objects
```

العقد الدقيق للقراءة في الإصدار 1:

| الحقل | القيمة المقبولة | الرفض |
|---|---|---|
| `version` | العدد الصحيح `1` وليس `bool` | إصدار آخر → `unsupported_version` |
| `type` | النص `reading` | نوع آخر → `invalid_message` |
| `sensor_id` | 1–64 ASCII وفق `[A-Za-z0-9][A-Za-z0-9._-]{0,63}` | غير صالح → `invalid_message` |
| `sequence` | عدد صحيح غير boolean ضمن `0..2**31-1` | مكرر/متراجع → `out_of_order` |
| `value` | عدد finite غير boolean ضمن `-1_000_000..1_000_000` | النوع/النطاق → `invalid_message` |

يلزم وجود الحقول الخمسة بالضبط. تعيد القراءة المقبولة:

```json illustrative
{"version":1,"type":"ack","sensor_id":"lab.temperature","sequence":7,"status":"accepted"}
```

يحوي الخطأ `version` و`type` و`code` مستقراً و`message` محدوداً فقط، ولا يعكس payload كاملاً. تتتبع كل وصلة 64 مستشعراً كحد أقصى ولا تحتفظ إلا بآخر 256 قراءة مقبولة. يعيد المستشعر 65 `resource_limit` دون طرد الحالة. عند بلوغ حد السجل تُحذف أقدم ملاحظة، لكن حالة sequence تبقى صحيحة. يحدث التحقق قبل mutation، لذلك كل رفض transactional.

#### تمرين: اختبر الافتراضات لا الأنظمة

قسّم frame صالحاً إلى ثلاثة أجزاء ثم ضع frameين في chunk واحد. **TODO:** تحقق من صفر/واحد/اثنين من الكائنات. **تلميح:** استخدم `encode_frame()` وslices. **النجاح:** يحفظ الترتيب ويعود `buffered_bytes` إلى صفر.

غيّر `sequence=True`، وأضف حقلاً، واستخدم `1_000_001`، وكرر sequence، ثم جرّب المستشعر 65. توقّع code. يشرح `test_protocol.py` الحل ويستخدم snapshots لإثبات أن الرفض لا يغير الحالة.

```text illustrative
python -B -m unittest discover -s chapter-23-network-programming/examples/tests -p test_protocol.py -v
```

تغلق UTF-8/JSON غير الصالحة وEOF الجزئية والتأطير غير الآمن الاتصال لأن إعادة المزامنة غير موثوقة. يمكن لكائن JSON محدد جيداً ذي schema خاطئ أن يتلقى error ويتابع.

### 5. مقارنة UDP datagrams

يحافظ UDP على حدود كل datagram لكنه لا يضمن الوصول أو عدم التكرار أو الترتيب. لا يملك اتصال TCP أو EOF. اختره فقط إذا كان التطبيق يتحمل هذه الخصائص أو يصلحها ويحافظ على رسائل صغيرة.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/udp_demo.py check=network:network-suite -->
```python source-ref
sender.sendto(message, receiver_address)
data, sender_address = receiver.recvfrom(1024)
```

```text illustrative
python -B chapter-23-network-programming/examples/telemetry/udp_demo.py
```

يطبع المسار المحلي الناجح `received:temperature=21.5`، والحالة الحدية timeout. قد تفقد شبكة حقيقية البيانات أو تكررها أو تعيد ترتيبها. لا تعد إشارة UDP بعقد sequence/ack الموثوق الخاص بـ TCP.

**قرار موجّه:** اختر النقل لملف ولتحديث موقع لعبة قابل للاستبدال. **تلميح:** هل يجب وصول كل byte بالترتيب؟ الحل: TCP للملف؛ قد يناسب UDP التحديثات القابلة للاستبدال إذا عالجت اللعبة الفقد والحجم.

### 6. المتانة والتسجيل والاختبارات الحتمية

قيّد الوقت وbytes والعملاء والمستشعرات والسجل المحتفَظ به والخرج المعلّق. يغلق selector أي peer بعد ثانية واحدة بلا تقدم في القراءة أو الكتابة؛ ولا يحتفظ أي من hubين بأكثر من 256 ملاحظة مقبولة للفحص التعليمي. سجّل peer وفئة خطأ مستقرة، لا أسراراً أو payload كاملاً. أعد فقط العمليات الآمنة بعدد قليل وbackoff؛ لا يعيد المشروع الكتابة آلياً.

تستخدم الاختبارات loopback وephemeral ports وevents/readiness وtimeouts قصيرة و`finally`، ولا تستخدم الإنترنت أو sleeps ثابتة للتنسيق. timeout والانقطاع وسط frame والرفض والدخل الخاطئ مسارات تعافٍ متوقعة.

**خطأ شائع:** التقاط `Exception` ومتابعة حالة تالفة. التقط خطأ الحد المحدد، وسجّل رسالة محدودة، وأغلق عند framing غير آمن، ولا تغيّر الحالة المقبولة.

### نقطة التحقق المتوسطة

لديك الآن core متسلسل مختبر ومقارنة UDP. تستطيع شرح التجزئة والدمج والتحقق قبل mutation وحدود الموارد. في المسار التالي لن يستطيع عميل بطيء حجب الآخرين.

## المسار المتقدم — concurrency محدودة وasyncio وTLS

### 7. عدة عملاء باستخدام selectors

ينتظر الخادم المتسلسل داخل `recv()`. تسأل `selectors.DefaultSelector` نظام التشغيل أي sockets جاهزة. تقبل النسخة المرافقة 32 عميلاً كحد أقصى، وتحفظ 65,536 byte ناقصة و64 مستشعراً و256 قراءة حديثة لكل اتصال، وترمّز رداً معلقاً واحداً وتغلق peer بعد ثانية بلا تقدم.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/selector_hub.py check=network:network-suite -->
```python source-ref
for key, mask in selector.select(timeout):
    # Accept, read, or continue a partial write only when ready.
    ...
```

قد يبدأ thread لكل اتصال ببساطة، لكنه يضيف دورة حياة ومزامنة حالة. تغلف `socketserver` أنماطاً متزامنة. ننفذ selectors لإظهار readiness والحدود؛ لا يوجد اختيار «أفضل» دائماً.

**توقّع:** يرسل A نصف frame ويتوقف، ويرسل B frame كاملاً. ينبغي أن يستلم B ack أولاً. يثبت integration test ذلك ويغطي frames المدمجة أيضاً. يغلق العميل 33 في زمن محدود بدلاً من دخوله queue غير محدودة.

### 8. Asyncio streams وbackpressure

تنشئ `asyncio.start_server()` مهمة لكل stream مقبول. ما زالت `reader.read()` تعيد chunks اعتباطية، ولذلك نستخدم decoder نفسه. بعد كل `writer.write()` محدود، تطبق `await writer.drain()` backpressure حتى ينتظر المنتج بدلاً من نمو الخرج بلا حد.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/async_hub.py check=network:network-suite -->
```python source-ref
writer.write(encode_frame(response))
await asyncio.wait_for(writer.drain(), timeout=client_timeout)
```

خطأ شائع بسبب الشرطة في اسم المجلد:

```text illustrative
python -B -m chapter-23-network-programming.examples.telemetry.async_hub
```

الأمر الصحيح القابل للنقل:

```text illustrative
cd chapter-23-network-programming/examples
python -B -m telemetry.async_hub
```

الأول خطأ مفسر وليس إرشاداً قابلاً للتشغيل. يستخدم الثاني ephemeral port ويرسل قراءة ويعرض ack ثم يغلق.

ترتيب الإغلاق: أوقف القبول، أغلق writers، انتظر `wait_closed()`، ألغِ handlers المتبقية، ثم اجمعها. يوفر `asyncio.Event` أو `KeyboardInterrupt` مساراً متعدد المنصات؛ إشارات POSIX امتداد اختياري.

**تمرين:** نفّذ `send_readings()` مرتين باستخدام `asyncio.gather()`. **TODO:** sensor ID مختلف لكل عميل. **تلميح:** أبق طلباً واحداً معلقاً حتى رده. **النجاح:** يحصل الاثنان على `accepted` ولا يترك `hub.close()` handlers أو writers. يعيد الحل استخدام helper المختبر.

### 9. امتداد اختياري: TLS مع التحقق

تشفّر Transport Layer Security (**TLS**) النقل وتتيح للعميل التحقق من شهادة الخادم. لا تصادق تلقائياً على العميل ولا تمنحه authorization. تبقى tokens وmTLS والسياسات خارج المشروع الأساسي.

يطبق الخادم حد العميل البالغ ثانية واحدة على تفاوض TLS وإغلاقه أيضاً. لذلك تنتهي مهلة peer خام من TCP لا يرسل ClientHello قبل إنشاء handler التطبيق، ولا يستطيع إبقاء الإغلاق معلقاً بلا حد.

المفاتيح والشهادات في `examples/certificates/` fixtures تعليمية عامة، ولا تحمي هوية حقيقية ولا تصلح للنشر. يثق العميل فقط بـ `lab-ca-cert.pem`؛ تحفظ `ssl.create_default_context(cafile=...)` التحقق من الشهادة وhostname. لا «تصلح» الفشل باستخدام `CERT_NONE` أو `check_hostname=False`.

تثبت الاختبارات offline أربع حالات: تنجح CA الموثوقة مع `localhost`؛ وتفشل بشكل مغلق حالات hostname الخاطئ والشهادة المنتهية وCA غير الموثوقة. تنتهي الشهادة الصالحة في يوليو 2046 ويحذر test حين يبقى أقل من عشر سنوات.

**التعافي:** افحص hostname ومصدر الثقة والساعة والتجديد. لا يثبت التشفير من دون التحقق من الهوية مَن في الطرف الآخر.

### 10. امتداد اختياري: IPv6

إذا نجح probe في bind على `::1`، ابدأ المركز مع `family=socket.AF_INET6`؛ وإلا سجّل skip مفسراً واستخدم IPv4. يختبر ذلك القدرة المحلية فقط ولا يدعي توافق الشبكة العامة.

### 11. تشغيل كل الأدلة

```text illustrative
python -B -m unittest discover -s chapter-23-network-programming/examples/tests -v
python -B tools/validate_book.py --plugin chapter-23-network-programming/tools/bookcheck_plugin.py
```

ينفذ الأمر الأول 33 اختباراً من المكتبة القياسية. يجمع الثاني checks العامة مع `network:network-suite`. يمتلك plugin سلوك البروتوكول ودورة الحياة المحلية فقط؛ تمتلك أداة الجذر Markdown والروابط ومبدلات اللغة وإشارات accessibility والبنية اللغوية والنظافة.

## التحدي النهائي

طوّر عميل المستشعر مع إبقاء عقد الإصدار 1 من دون تغيير:

1. **سهل:** أرسل ثلاث قراءات متزايدة لمستشعر واحد. **TODO:** تحقق من ثلاث رسائل ack دقيقة. **تلميح:** ابدأ بالتسلسل صفر.
2. **متوسط:** أرسل قراءة مكررة بين قراءتين صالحتين. **TODO:** أثبت أن `out_of_order` لا يمنع التسلسل الأكبر اللاحق. **تلميح:** يجب ألا يغيّر الرفض الحالة.
3. **متقدم:** شغّل عميلين بينما يتوقف ثالث في منتصف frame، ثم أغلق الخادم. **TODO:** أثبت تقدم العميلين النشطين وعدم بقاء أي task. **تلميح:** استخدم events و`wait_for` محدودة، ولا تعتمد على مدة انتظار تخمينية.
4. **امتداد Hero:** فعّل سياق TLS الموثوق أو مسار IPv6 المشروط، واذكر بدقة ما اختبره جهازك.

يجمع الحل المفسر `AsyncTelemetryHub` و`send_readings()` و`ConnectionState` والاختبارات الموجودة؛ ولا ينشئ بروتوكولاً ثانياً. اختبر رسائل ack الناجحة وerror envelope واحداً وحالة الخادم والتنظيف بعد timeout و`hub.close()`. أبق كل العناوين على loopback.

## معيار التقييم

امنح كل جانب 0 (غائباً) أو 1 (جزئياً) أو 2 (مثبتاً):

- **البروتوكول:** الحقول الدقيقة وframing ورموز ack/error ودلالة التسلسل.
- **الحدود:** حجم frame وخمول selector لمدة ثانية واحدة و32 عميلاً و64 مستشعراً والاحتفاظ بـ256 ملاحظة واستجابة معلقة واحدة.
- **التعافي:** input غير الصالح وtimeout وEOF والرفض من دون mutation جزئية.
- **التزامن:** يتقدم عميل آخر بينما يتوقف أحد العملاء.
- **الأمان:** استخدام loopback افتراضياً والتحقق من ثقة TLS وhostname وعدم تسجيل الأسرار.
- **التحقق:** اختبارات unit/integration حتمية ودليل محلي صريح.
- **التنظيف والشرح:** لا موارد متروكة، ويمكنك شرح كل قرار تصميم.

اثنتا عشرة نقطة أو أكثر من دون صفر في البروتوكول أو الحدود أو التنظيف نتيجة قوية. الدرجة تغذية راجعة وليست وصفاً للمتعلم؛ حسّن سلوكاً واحداً قابلاً للملاحظة في كل مرة.

## التأمل الأخير والمسرد

لماذا يحتاج TCP إلى framing؟ لماذا نتحقق قبل mutation؟ لماذا يعد `drain()` وtimeouts تحكماً بالموارد؟ افصل ما اختبره جهازك محلياً عن مشكلات النشر التي لم نتحقق منها.

- **Backpressure:** إبطاء المنتج عندما لا يلحق المستهلك أو buffer به.
- **EOF:** نهاية stream الخارجة من peer، وتدل عليها قراءة TCP فارغة.
- **Ephemeral port:** منفذ حر يختاره نظام التشغيل.
- **Framing:** قواعد استعادة حدود رسائل التطبيق من stream من bytes.
- **Loopback:** مسار المضيف الخاص عائداً إلى نفسه.
- **NDJSON:** قيمة JSON واحدة في كل frame محدد بسطر جديد.
- **TLS:** نقل مشفر مع تحقق هوية peer باستخدام الشهادة.

انتقلت من «إرسال نص» إلى بروتوكول يعرّف كل محادثة ويحدها ويراقبها ويختبرها ويغلقها. تنتقل هذه الدقة إلى HTTP وmessage brokers وقواعد البيانات والأنظمة الشبكية الأخرى.

</div>
