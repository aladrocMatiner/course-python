<div dir="rtl">

# الفصل 1 · المقدمة والإعداد

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
قبل أن نكتب أي كود، سنجهّز “ورشة” بايثون على جهازك: تثبيت نسخة حديثة من Python، التأكد أن `pip` يعمل، و(اختياريًا) تعلّم إدارة أكثر من نسخة بدون صداع. الهدف بسيط: عندما تكتب `python --version` يردّ الجهاز، وتبدأ البرمجة بدون مشاكل.

## لماذا هذا مهم؟
إذا كانت البيئة غير صحيحة ستظهر أخطاء “ليست خطأك” بل مشكلة إعداد. هذا الفصل يجعل البداية سلسة، وبعده يصبح التعلم ممتعًا.

## “شخصياتنا” (للمرح)
في أمثلة الكود سنستخدم كثيرًا الأسماء **Noor** و **Frej** و **Taha**. هذه مجرد أسماء مثال — غيّرها لاسمك أو أسماء أصدقائك أو شخصياتك المفضلة.

---

## 1) تثبيت Python (موصى به 3.11+)

### Windows
1. نزّل المثبت من: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
2. أثناء التثبيت فعّل خيار **“Add python.exe to PATH”**.
3. تحقّق:
   ```powershell
   python --version
   pip --version
   ```

### macOS
```bash
python3 --version
pip3 --version
```

### Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
python3 --version
pip3 --version
```

---

## 2) التأكد من `pip`
```bash
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip
```

---

## 3) بيئة افتراضية بسرعة (`.venv`)
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install requests
```

---

## ملخص
الآن Python و`pip` يعملان ويمكنك إنشاء بيئة افتراضية. في الفصل التالي سنبدأ بالمتغيرات وأنواع البيانات البسيطة.

</div>
