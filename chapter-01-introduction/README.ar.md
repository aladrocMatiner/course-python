<div dir="rtl">

# الفصل 1 · المقدمة وإعداد البيئة

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟

قبل أن نكتب أي شيفرة، سنجهّز «ورشة بايثون» الخاصة بك: سنثبّت إصدارًا حديثًا من Python، ونتأكد من أن `pip` يعمل، ونتعلم —اختياريًا— كيف ندير أكثر من إصدار من دون إرباك. الهدف بسيط: عندما تنفّذ `python --version` يجيبك الحاسوب، وتستطيع بدء البرمجة بدل الصراع مع الإعدادات.

## مسار التعلم

1. **ثبّت Python** وتأكد من أن الأمر يعمل.
2. **افحص `pip`** حتى نستطيع تثبيت المكتبات عند الحاجة.
3. **البيئات الافتراضية**: أنشئ «صندوقًا» صغيرًا (`.venv`) لكل مشروع.
4. **مستوى إضافي**: استخدم `asdf` إذا أردت إعدادًا احترافيًا جدًا.

## أهداف التعلم

- التحقق من تثبيت Python وفهم معنى رقم الإصدار.
- التأكد من أن `pip` يعمل وتحديثه.
- إنشاء بيئة افتراضية (`venv`) لمشروع وتفعيلها.
- تجنّب مشكلة «يعمل على جهازي فقط» الشائعة.

## المتطلبات السابقة

- لا تحتاج إلى معرفة سابقة ببايثون.
- تحتاج إلى طرفية وصلاحية تثبيت البرامج على حاسوبك. إذا كان الجهاز مُدارًا من المدرسة أو العمل، فاطلب مساعدة المسؤول بدل تجاوز القيود.
- أبقِ هذا الفصل مفتوحًا في علامة تبويب أو جهاز آخر كي تستطيع قراءة خطوات الاسترداد إذا فشل أمر ما.

## توقّع قبل الإعداد

قبل تنفيذ أي شيء، دوّن الأمر الذي تتوقع أنه يشغّل Python على نظامك: `python` أو `python3` أو `py`. بعد التثبيت ستقارن توقعك بالأمر الذي يستجيب فعلًا وبمسار الملف التنفيذي الذي يعرضه Python.

## لماذا يهم هذا؟

إذا لم تكن البيئة مضبوطة، قد تنسخ مثالًا صحيحًا ثم تشغّله فتحصل على خطأ لا يأتي من الشيفرة، بل من إعداد الحاسوب. يمنع هذا الفصل تلك البداية المحبطة. بعد تجهيز البيئة يصبح باقي المساق أكثر متعة.

### مغامرة صغيرة

تخيّل حاسوبك دراجة جديدة: قبل رحلة طويلة تضبط المقعد، وتنفخ الإطارات، وتفحص المكابح. نفعل هنا الأمر نفسه لنبدأ رحلة تعلم آمنة.

### تعرّف إلى شخصياتنا (مرح اختياري)

سترى أسماء **نور** و**فريج** و**طه** في أمثلة الكتاب. إنها أسماء بديلة فحسب؛ يمكنك استبدالها باسمك أو بأسماء أصدقائك أو شخصياتك المفضلة.

---

## 1. تثبيت Python (يُنصح بالإصدار 3.11 أو أحدث)

### Windows

1. افتح [صفحة تنزيل Python الرسمية لنظام Windows](https://www.python.org/downloads/windows/) ونزّل المثبّت الرسمي (`python-3.x.x-amd64.exe`).
2. أثناء التثبيت، فعّل خيار **“Add python.exe to PATH”** حتى لا تضبط المسار يدويًا لاحقًا.
3. أكمل التثبيت ثم تحقّق:
   ```powershell illustrative
   python --version
   pip --version
   ```
4. بديل آلي في Windows 11 أو أحدث:
   ```powershell illustrative
   winget install --id Python.Python.3.11 --source winget
   ```

### macOS

1. نزّل ملف `.pkg` من [صفحة تنزيل Python الرسمية لنظام macOS](https://www.python.org/downloads/macos/).
2. شغّل المثبّت واقبل الخيارات الافتراضية؛ سيُثبَّت Python داخل `/Library/Frameworks/Python.framework`.
3. تحقّق:
   ```bash illustrative
   python3 --version
   pip3 --version
   ```
4. بديل باستخدام Homebrew:
   ```bash illustrative
   brew update
   brew install python@3.11
   python3.11 --version
   python3.11 -m pip --version
   ```
   لا تكتب `/opt/homebrew` بصورة ثابتة في ملف إعداد الطرفية؛ يستخدم Homebrew بادئات مختلفة على Apple Silicon وIntel. إذا لم يُعثر على `python3.11`، فنفّذ `brew info python@3.11` واتبع الملاحظة الخاصة بتثبيتك.

### Linux (Debian/Ubuntu)

```bash illustrative
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
python3 --version
pip3 --version
```

إذا كانت توزيعتك توفر إصدارًا أقدم من 3.11، فلا تضف مستودعًا خارجيًا غير مُراجع لمجرد متابعة الفصل. استخدم تعليمات Python الرسمية لتوزيعتك أو مسار `asdf` الاختياري أدناه.

### Linux (Fedora/CentOS/RHEL)

```bash illustrative
sudo dnf install -y python3 python3-pip
python3 --version
pip3 --version
```

---

## 2. التأكد من توفر `pip`

- افحص أولًا `pip` المرتبط بالمفسّر الذي ستستخدمه:
  ```bash illustrative
  python3 -m pip --version
  ```
- `ensurepip` وحدة اختيارية في CPython. إذا ثبّت Python من `python.org` وكانت الوحدة موجودة، فيمكنها تهيئة `pip` من دون تنزيله:
  ```bash illustrative
  python3 -m ensurepip --upgrade
  ```
- إذا ظهر `No module named ensurepip`، فاستخدم المثبّت الرسمي أو مدير حزم نظامك (`python3-pip` في عائلتي Debian وFedora)، ولا تنسخ سكربت تهيئة عشوائيًا.
- حدّث `pip` فقط بعد تفعيل البيئة الافتراضية للمشروع:
  ```bash illustrative
  python -m pip install --upgrade pip
  ```

---

## 3. إدارة أكثر من إصدار باستخدام `asdf` (اختياري واحترافي)

يتيح لك `asdf` تثبيت إصدارات Python مختلفة والتبديل بينها —وبين أدوات أخرى— حسب المشروع، فتظل البيئات متسقة.

هذا المسار اختياري، ولا يحتاج إليه checkpoint الأساسي. ثبّت إصدار `asdf` الحالي باتباع [دليل البدء الرسمي](https://asdf-vm.com/guide/getting-started.html) الذي يغطي نظامك ومعماريته. تستخدم الأوامر الآتية الواجهة التنفيذية الحالية؛ ولا تنطبق تعليمات `asdf.sh` و`asdf global` القديمة.

1. تحقّق من التثبيت:
   ```bash illustrative
   asdf --version
   ```
2. أضف ملحق Python المجتمعي بعد مراجعة المصدر الذي يعرضه فهرس الملحقات الرسمي. إذا ظهر `python` بالفعل في `asdf plugin list` فتجاوز الأمر:
   ```bash illustrative
   asdf plugin add python
   ```
3. ثبّت أحدث إصدار تصحيحي مستقر من 3.11 واكتب الاختيار الفعلي في `.tool-versions` الخاص بالمشروع:
   ```bash illustrative
   asdf install python latest:3.11
   asdf set python latest:3.11
   ```
4. تحقّق:
   ```bash illustrative
   python --version
   python -m pip --version
   ```

قورنت هذه التعليمات الحساسة للإصدارات بوثائق Python وHomebrew و`asdf` الرسمية في 2026-07-13.

الفوائد:

- يستطيع كل مستودع تحديد ملف `.tool-versions` لتثبيت الإصدارات المطلوبة.
- تتجنّب التعارض بين مشاريع تحتاج إلى إصدارات مختلفة.

### النسخ الاحتياطي والاسترداد لتعديلات الطرفية الاختيارية

لا يتطلب المسار الأساسي أعلاه تعديل ملف بدء الطرفية. إذا طلب دليل رسمي لأداة اختيارية تعديل `~/.zshrc` أو `~/.bashrc`، فانسخه أولًا، مثلًا باستخدام `cp "$HOME/.zshrc" "$HOME/.zshrc.python-course.bak"`. أضف السطر الموثق فقط. إذا توقفت طرفية جديدة عن العمل، فاحذف ذلك السطر من الطرفية القديمة أو استعد النسخة فورًا. لا تستعد نسخة قديمة بعد إجراء تعديلات أحدث لا علاقة لها.

---

## 4. أول الممارسات الجيدة

- **البيئات الافتراضية**: استخدم `python -m venv .venv` ثم فعّلها باستخدام `source .venv/bin/activate`، أو `.\.venv\Scripts\Activate.ps1` في Windows PowerShell.
- **الصلاحيات**: تجنّب `sudo pip install`، واستخدم البيئات الافتراضية أو `pipx`.
- **فحص سريع**: بعد التثبيت نفّذ `python -m pip list` لتتأكد من أن `pip` يستجيب بلا أخطاء.

---

## تمارين موجهة (مع TODOs)

1. **1-1 · افحص Python**
   ```bash todo
   # TODO: run one of these commands and write down the version you get
   python --version
   python3 --version
   ```
   *تلميح*: في Windows يكون الأمر غالبًا `python`، وفي macOS وLinux يكون غالبًا `python3`.

2. **1-2 · أنشئ أول «صندوق» (`.venv`)**
   ```bash todo
   # TODO 1: create the virtual environment
   python -m venv .venv
   # TODO 2: activate it (pick the command for your system)
   # macOS/Linux: source .venv/bin/activate
   # Windows: .\.venv\Scripts\Activate.ps1
   # TODO 3: verify which Python and pip the environment uses
   python -c "import sys; print(sys.executable)"
   python -m pip --version
   ```

3. **1-3 · مرحبًا بالطرفية**
   ```bash todo
   # TODO: create a file hello.py with a print and run it
   python hello.py
   ```

---

## أخطاء شائعة

- تثبيت Python من دون تفعيل “Add python.exe to PATH” في Windows، فيصبح أمر `python` غير معروف.
- استخدام `pip` تابع لإصدار Python مختلف عن الإصدار الذي تشغّله، فتُثبَّت المكتبة في مكان آخر.
- نسيان تفعيل `.venv`، فيستخدم المشروع dependencies غير المقصودة.
- استخدام `sudo pip install`، وقد يفسد حزم النظام؛ استخدم `.venv` بدلًا منه.

---

## حلول مفسرة

- إذا لم يوجد `python`: افحص PATH أو أعد التثبيت في Windows، وجرّب `python3` في macOS وLinux.
- لتجنّب `pip` الخطأ، استخدم دائمًا `python -m pip ...`؛ عندها يرتبط `pip` بنفس Python.
- إذا تعذر تفعيل `venv`، تأكد من أنك في المجلد الصحيح وأن `.venv/` موجود.

---

## الخلاصة

أصبح Python و`pip` يعملان، وتعرف الآن كيف تنشئ بيئة افتراضية ولماذا يسبب خلط dependencies بين المشاريع مشكلات.

## Checkpoint وتقييم ذاتي

داخل `.venv` المفعّلة، تأكد من أن `python --version` و`python -c "import sys; print(sys.executable)"` و`python -m pip --version` تستجيب. يجب أن يشير مسار الملف التنفيذي إلى داخل `.venv`.

امنح نفسك نقطة لكل معيار:
- **الصحة:** الإصدار 3.11 أو أحدث، وتنجح الفحوص الثلاثة.
- **الوضوح:** تسجل ملاحظتك القصيرة الأمر ومسار الملف التنفيذي اللذين استخدمتهما فعلًا.
- **الاسترداد:** تستطيع تنفيذ `deactivate` وتعرف كيف تتراجع عن أي تعديل اختياري للطرفية.
- **التحقق:** بعد إعادة تفعيل `.venv` يظل المسار داخل البيئة.
- **الشرح:** تستطيع أن تشرح بكلماتك لماذا يمنع `python -m pip` والبيئة الافتراضية خلط عمليات التثبيت.

أنت مستعد للفصل 2 عند حصولك على 5/5. إذا فشل معيار، فاستخدم الحلول السابقة وأعد ذلك الفحص وحده.

## تأمل ختامي

إذا وصلت إلى هنا فقد أنجزت خطوة مهمة: جعلت حاسوبك مكانًا موثوقًا للتعلم. في الفصل 2 سنبدأ البرمجة الفعلية باستخدام المتغيرات والأنواع البسيطة.

</div>
