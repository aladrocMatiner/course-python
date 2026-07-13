<div dir="rtl">

# الملحق A · بناء أدوات سطر الأوامر بالمكتبة القياسية

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

## ماذا سنبني؟
سنصمم أمرًا للطرفية مستوحى من الأدوات الحقيقية. سيقبل أوامر فرعية وخيارات مطلوبة، ويعرض المساعدة تلقائيًا. سنستخدم `argparse` و`pathlib` و`logging` كي تتمكن من نشر برامج نصية احترافية من دون تبعيات خارجية.

## مسار التعلّم
1. **تذكير بـ`sys.argv` وحدوده**.
2. **البنية الأساسية لـ`argparse`**: الوصف والمعاملات الموضعية والاختيارية.
3. **الأوامر الفرعية باستخدام `add_subparsers`**: عدة إجراءات في أداة واحدة.
4. **مخرجات أغنى**: التنسيق ورموز الخروج والتسجيل.
5. **حزم أساسية**: نقطة دخول باستخدام `if __name__ == "__main__"`.
6. **اختبار خفيف**: `argparse` مع `pytest` و`capsys`.

## أهداف التعلّم
- إعداد `ArgumentParser` بمعاملات مطلوبة واختيارية.
- تنفيذ أوامر فرعية لتجميع الوظائف.
- قراءة الملفات وكتابتها عبر `Path` وفق معاملات المستخدم.
- تسجيل الرسائل وإعادة رموز خروج مناسبة.
- اختبار الأوامر بمحاكاة argv.

## لماذا يهم هذا؟
رغم وجود أطر أقوى، فإن إتقان المكتبة القياسية يجنبك التبعيات ويتيح لك بناء أدوات داخلية وبرامج نشر وأدوات بيانات بسرعة.

### مغامرة صغيرة
تشبه واجهة سطر الأوامر جهاز تحكم عن بعد لبرنامجك: بدل النقر، تكتب أوامر قصيرة. وإذا كان جهاز التحكم مصممًا جيدًا، مع مساعدة وخيارات واضحة، استطاع الجميع استخدامه بثقة.

## المتطلبات المسبقة
الفصول السابقة الموصى بها: 9, 11, 13–16, 18.
استخدم CPython 3.11+ في بيئة محلية مؤقتة, وأبقِ البيانات والأسرار والخدمات بعيدًا عن الأنظمة الحقيقية.

---

## 1. أساسيات `argparse`

```python illustrative
# cli.py
import argparse

parser = argparse.ArgumentParser(description="Notes manager")
parser.add_argument("title", help="Note file name")
parser.add_argument("--message", required=True)
parser.add_argument("--tags", nargs="*", default=[])
args = parser.parse_args()

print(args.title, args.message, args.tags)
```

- يسمح `nargs="*"` بعدة وسوم.
- تتحقق `parser.parse_args()` من المعاملات وتولّد المساعدة تلقائيًا.

### المساعدة المولّدة
```text illustrative
python cli.py --help
```
يطبع الأمر الوصف والمعاملات وطريقة الاستخدام تلقائيًا.

---

## 2. الأوامر الفرعية

```python illustrative
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(prog="todos")
subparsers = parser.add_subparsers(dest="command", required=True)

add_parser = subparsers.add_parser("add", help="Add task")
add_parser.add_argument("text")

list_parser = subparsers.add_parser("list", help="List tasks")

args = parser.parse_args()
file_path = Path("todos.txt")

if args.command == "add":
    with file_path.open("a", encoding="utf-8") as fh:
        fh.write(args.text + "\n")
elif args.command == "list":
    if file_path.exists():
        print(file_path.read_text(encoding="utf-8"))
    else:
        print("No tasks yet.")
```

- يخبرك `dest="command"` بالأمر الفرعي الذي استُخدم.
- للإضافة إلى آخر الملف، استخدم `file_path.open("a", encoding="utf-8")` كما في المثال. تستبدل `Path.write_text()` الملف ولا تقبل معاملًا باسم `append=True`.

---

## 3. التسجيل ورموز الخروج

```python runnable
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

try:
    # logic
    logging.info("Note saved")
except Exception as exc:
    logging.error("Failure: %s", exc)
    sys.exit(1)
```

- يعني `sys.exit(0)` النجاح، ويعني أي رمز غير صفري وجود خطأ.

---

## 4. ممارسات جيدة
- ضع المنطق داخل دوال لتسهيل اختباره وإعادة استخدامه.
- استخدم `Path` للمسارات ولا تجمع النصوص لبنائها.
- أضف أمثلة عبر `ArgumentParser(description=...)` و`epilog`.

### بنية مقترحة
```python illustrative
def build_parser():
    parser = argparse.ArgumentParser(...)
    # configure
    return parser

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    # logic

if __name__ == "__main__":
    main()
```

### اختبار argv
```python illustrative
def test_build_parser_add():
    parser = build_parser()
    args = parser.parse_args(["add", "Learn argparse"])
    assert args.command == "add"
    assert args.text == "Learn argparse"
```

- تتيح لك هذه البنية تمرير `argv` مخصّصة أثناء الاختبارات.

---

## تمارين موجّهة (مع TODO)
1. **A-1 · واجهة مصروفات**
   ```python todo
   # TODO 1: "add" subcommand with amount and description
   # TODO 2: "report" subcommand that shows the total
   # TODO 3: store data in CSV format using Path
   ```
   *تلميح*: استخدم `Path("expenses.csv").open("a", newline="", encoding="utf-8")`.

2. **A-2 · مسجّل قابل للضبط**
   ```python todo
   # TODO 1: add --debug option that sets logging to DEBUG
   # TODO 2: print messages only if the level matches
   # TODO 3: try capsys in pytest
   ```
   *تلميح*: استخدم `if args.debug: logging.getLogger().setLevel(logging.DEBUG)`.

---

## أخطاء شائعة
- نسيان `dest` أو `required=True` للأوامر الفرعية، فلا تعرف الأداة ما الذي ينبغي تشغيله.
- عدم تغليف المنطق بـ`try/except`، فتظهر tracebacks خام لأخطاء متوقعة.
- استخدام `print` لكل شيء بدل التسجيل، مما يصعّب الترشيح.
- عدم اختبار `argparse` بمعاملات محاكية.

---

## حلول مشروحة
1. **واجهة المصروفات**: استخدم `subparsers.add_parser("add")` و`"report"`، واكتب الصفوف في `expenses.csv`. يقرأ الأمر `report` القيم ويجمعها.
2. **المسجّل القابل للضبط**: فعّل `--debug` عبر `store_true` واختبر السجلات باستخدام `caplog`؛ واترك `capsys` لـ`stdout` و`stderr`.

---

## الخلاصة
باستخدام `argparse` و`logging` و`pathlib` تستطيع إنشاء أدوات طرفية متينة توثّق نفسها ويسهل اختبارها، من دون أطر خارجية.

## نقطة تحقق ومعايير تقييم
- **الصحة**: تطابق النتيجة عقد الوحدة.
- **الوضوح**: تُفهم الأسماء والمسؤوليات من القراءة الأولى.
- **الأخطاء**: يُختبر مسار ناجح وحالة حدّية ومسار تعافٍ.
- **التحقق**: تعمل الأمثلة والتمارين في بيئة نظيفة.
- **الشرح**: تستطيع تبرير القرارات ومخاطرها.

## تأمل ختامي
عندما تتقن بناء واجهات الطرفية بالمكتبة القياسية تكتسب استقلالية لأتمتة المهام وبناء أدوات احترافية يستطيع زملاؤك تشغيلها من دون تثبيت أي شيء آخر. وتظهر هذه الأنماط مجددًا في برامج النشر وأدوات DevOps.

</div>
