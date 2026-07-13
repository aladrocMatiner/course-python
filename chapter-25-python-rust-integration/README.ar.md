<div dir="rtl">

# الفصل 25 · بايثون وRust: من أول crate إلى wheel موثَّق

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية

يبدأ هذا الفصل بلا معرفة سابقة بلغة Rust. ستبني أولًا برنامجًا صغيرًا ومجال إحصاءات بلغة Rust الخالصة، ثم تعبر إلى بايثون باستخدام PyO3. النتيجة هي `faststats_rs`: حزمة مختلطة ذات typing، واختبارات حتمية، وعمل متوازٍ محدود، وsdist، وwheel خاص بالإصدار، وwheel من نوع `abi3-py311`.

كل الأمثلة مصادر أصلية مرافقة داخل [`examples/`](examples/). يكتب المتحقق الكامل builds والبيئات داخل مجلدات مؤقتة؛ لا ينشر شيئًا ولا يستخدم أي credentials.

## أهداف التعلم والمتطلبات السابقة

عند الإكمال تستطيع:

- شرح crate وcompiler وextension module وواجهة التطبيق الثنائية (ABI) وsdist وwheel؛
- قراءة variables وstructs و`Vec<T>` وslices وownership وborrowing و`Option` و`Result`؛
- إبقاء مجال Rust مستقلًا عن PyO3 وتحويل الأخطاء القابلة للاسترداد إلى exceptions في بايثون؛
- توضيح ما يُنسخ أو يُنقل أو يُستعار أو يُعدّ بالـreference count عند الحدود؛
- تثبيت عقد عددي دقيق ومحدود قبل التحسين؛
- استخدام `Python::detach` مع بيانات تملكها Rust فقط، دون ادعاء دعم free-threaded؛
- اختبار Rust وبايثون وtyping والتزامن وsdist وwheels وimports النظيفة؛
- تفسير benchmark دون الوعد بأن Rust أسرع دائمًا.

تحتاج إلى [الاستثناءات](../chapter-14-exceptions/README.ar.md) و[الوحدات](../chapter-15-modulos/README.ar.md) و[البيئات](../chapter-16-entornos/README.ar.md) و[الاختبار](../chapter-18-testing/README.ar.md) و[التسجيل](../chapter-20-logging/README.ar.md) و[الاستبطان](../chapter-22-introspection/README.ar.md). الفصلان 23 و24 ليسا متطلبين.

تحتاج CPython 3.11+، واتصال الإنترنت عند التثبيت الأولي للـtoolchain/crates، وlinker المنصة، ونحو 16 جلسة من 45–60 دقيقة. تم التحقق من هذه النسخة على Linux x86-64 وCPython 3.13.11 وRust 1.97.0 وPyO3 0.29.0 وmaturin 1.14.1. المنصات الأخرى تعليمات تحتاج تحققًا، وليست ادعاء دعم.

## خريطة المسارات

| المسار | الزمن | النتيجة المرئية | معيار الإكمال |
|---|---:|---|---|
| الإعداد | 1–2 جلسة | تقرير toolchain وأول اختبار Rust | `cargo test --locked` |
| Rust الأساسية | 4 جلسات | مجال مستقل عن بايثون | fmt وclippy والاختبارات |
| التكامل | 3 جلسات | بايثون يستورد extension خاصة | wheel مثبتة خارج source |
| الاحترافي | 3–4 جلسات | classes وerrors وtyping وparity | pytest وstubtest وmypy strict |
| Hero | 3–4 جلسات | عمل detached وwheelان مدققان | rendezvous وsdist وتثبيت نظيف |

يمكنك التوقف عند أي checkpoint. لا يلزم Hero لإكمال المسار الأساسي.

## 1. لماذا نعبر حدود اللغة؟

بايثون هي البداية الأفضل غالبًا. تضيف Rust compiler وأدوات منصة وpackaging ونموذج ذاكرة ثانيًا. لا تبرَّر هذه التكلفة إلا بعد تثبيت الصحة وقياس حد مفيد.

يلخص مشروعنا حتى مليون عينة. تملك بايثون الواجهة العامة، بينما تحصل Rust على مجال ضيق مقصود. تمنع مرجعية بايثون قبول إجابة سريعة لكنها خاطئة.

**توقّع:** أيهما أفضل: native call واحدة فيها 100,000 قيمة، أم 100,000 call بقيمة واحدة؟ تدفع الثانية كلفة الحدود مرارًا. سنقيس بدل التخمين.

**Checkpoint:** اذكر سببًا لإبقاء بايثون: الأداء كافٍ، calls صغيرة، مكتبة جاهزة، أو كلفة الصيانة أكبر من الفائدة المقاسة.

## 2. الإعداد: شخّص قبل البناء

ثبّت Rust عبر `rustup` وثبّت maturin كأداة Python منشورة، لا عبر `cargo install maturin` في المسار الأساسي. يحتاج Linux إلى linker/build essentials، ويحتاج macOS إلى Xcode command-line tools، ويحتاج Windows عادةً إلى MSVC Build Tools المطابقة لبايثون 64-bit.

| النظام | المتطلب الأصلي | أول تشخيص |
|---|---|---|
| Linux | أدوات C/linker للتوزيعة | `cc --version` |
| macOS | Xcode command-line tools | `xcode-select -p` |
| Windows | MSVC Build Tools متوافقة | استخدم Developer shell |

تستبدل pins كلمة “latest” غير المستقرة:

```bash illustrative
rustup toolchain install 1.97.0 --profile minimal --component rustfmt --component clippy
python -m venv .venv
# فعّل .venv بالأمر المناسب للـshell لديك.
python -m pip install -r examples/faststats-rs/requirements-dev.lock
python -B tools/preflight.py --require-venv
```

قد يحتاج التثبيت إلى الإنترنت. يفحص preflight بالترتيب Python/venv ثم rustup/toolchain ثم Cargo/target ثم linker ثم maturin. غياب linker ليس خطأ PyO3، وvenv غير مفعّلة ليست خطأ Rust.

أخطاء قابلة للاسترداد:

- غياب `rustup`: استخدم المثبت الرسمي وأعد تشغيل shell ثم افحص version؛
- ظهور Rust 1.96: نفّذ `rustup run 1.97.0 rustc --version` ولا تخفّض pin؛
- عدم اكتشاف maturin للـvenv: فعّلها أو ابنِ wheel؛
- نجاح import من source فقط: انتقل إلى cwd مؤقت وافحص `module.__file__`.

**TODO:** احفظ تقرير preflight بصيغة JSON. **تلميح:** الأمر `python -B tools/preflight.py --json` للقراءة فقط.

## 3. أول برنامج Rust: القيم والدوال والاختبارات

الـcrate هي وحدة package/compilation في Rust، و`Cargo.toml` هو manifest. تختار Edition 2024 الأساليب الحالية، ويثبت `rust-version = "1.97.0"` الـcompiler الذي اختبرناه.

```bash illustrative
cd examples/00-rust-survival
cargo check --locked
cargo run --locked
cargo test --locked
```

الناتج المهم:

```text illustrative
workshop mean: 19.0
```

تقدم المكتبة struct وslice مستعارة و`Option` وenum و`Result` و`?` من خلال قراءة sensor محدودة.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/00-rust-survival/src/lib.rs" check="rust:contract" -->
```rust source-ref
pub fn average(values: &[f64]) -> Option<f64> { /* مصدر مختبَر */ }
pub fn parse_reading(text: &str) -> Result<Reading, ParseReadingError> { /* ... */ }
```

تقول `Option` إن متوسط القائمة الفارغة غير موجود. ويصف `Result` أخطاء معروفة قابلة للاسترداد دون sentinel سحري.

**عدّل:** اختبر `"lab:NaN"`. **تلميح:** ينجح parsing أولًا ثم يرفض `is_finite()` القيمة. الحل هو `NonFiniteNumber`: الشكل العددي وحده لا يحقق عقد المجال.

## 4. Ownership وborrowing: الـcompiler يعطينا دليلًا

لكل قيمة Rust مالك. قد تنقل assignment القيمة. تمنح `&T` قراءة مؤقتة، وتمنح `&mut T` استعارة mutable حصرية.

توقّع السطر الذي يفشل:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/00-rust-survival/lessons/ownership_move_error.rs" check="rust:contract" -->
```rust source-ref
let label = String::from("sensor-a");
let moved_label = label;
println!("{moved_label}");
println!("{label}"); // E0382: استخدام بعد move
```

قد يقترح الـcompiler استخدام `.clone()`، لكن اسأل أولًا من يجب أن يملك القيمة بعد call. هنا تكفي الاستعارة:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/00-rust-survival/lessons/ownership_borrow_solution.rs" check="rust:contract" -->
```rust source-ref
fn print_label(label: &str) { println!("{label}"); }
// يحتفظ caller بالـString ويعير &str مرتين.
```

خطأ شائع: إضافة clones حتى يصمت compiler. يجب تبرير كلفة clone والحاجة المقصودة إلى مالكين.

**تحقق ذاتي:** في `average(values: &[f64])` يملك caller المجموعة، وتستعير الدالة slice أثناء call، ولا يمكن للاستعارة أن تعيش أطول من البيانات.

## 5. مجال Rust خالص قبل PyO3

يستقبل المجال قيم `f64` محوّلة ولا يعرف بايثون أو Global Interpreter Lock (GIL). لذلك يعزل `cargo test` السلوك العددي.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/src/domain.rs" check="rust:contract" -->
```rust source-ref
pub const MAX_SAMPLES: usize = 1_000_000;
pub const MAX_ABS_VALUE: f64 = 1.0e150;
pub fn summarize(values: &[f64], threshold: f64)
    -> Result<SummaryData, DomainError> { /* تطبيق مختبَر */ }
```

الترتيب دقيق: validation؛ تحديث mean حسب ترتيب input عبر `mean += (value - mean) / count`؛ مرور ثانٍ مقابل المتوسط النهائي؛ عد delta فقط عندما تكون أكبر من threshold وخارج نطاق التقارب `1e-12`.

للقيم `[-3,-3,-1]` وthreshold `0.5` يكون mean هو `-7/3` وكل القيم anomalies. تعطي streaming classification جوابًا آخر.

يعدّل `OnlineStatsData.extend` نسخة من الحالة ثم يعمل commit بعد نجاح validation. يحافظ الفشل على الحالة كاملة.

**TODO:** اختبار threshold سالب. **الحل المفسر:** توقّع `DomainError::InvalidThreshold`؛ لا تعمل clamp صامتًا لأنه يغيّر طلب caller.

## 6. أول extension باستخدام PyO3

تكشف `#[pyfunction]` الدوال وتهيئ `#[pymodule]` الوحدة. تعلن الوحدة `gil_used = true` كي لا تدّعي free-threaded compatibility لم تُدقَّق.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/01-first-extension/src/lib.rs" check="rust:contract" -->
```rust source-ref
#[pyfunction]
fn double(value: i64) -> PyResult<i64> { /* ضرب مع فحص */ }

#[pymodule(gil_used = true)]
fn first_pyo3_extension(module: &Bound<'_, PyModule>) -> PyResult<()> { /* ... */ }
```

```bash illustrative
cd examples/01-first-extension
maturin develop --locked
python -c "import first_pyo3_extension as m; print(m.double(21))"
```

لاحظ:

```text illustrative
42
```

يتحول overflow إلى `ValueError`، والنوع الخاطئ إلى `TypeError`. لا تضف feature القديمة deprecated المسماة `pyo3/extension-module`؛ لا يحتاجها هذا المسار مع maturin.

## 7. حزمة مختلطة: native خاصة وواجهة عامة

`faststats_rs._native` تفصيل compiled، و`faststats_rs` هي الـAPI العامة ذات typing. يصل `python-source` و`module-name` الطبقتين. تنتج crate كلًا من `cdylib` و`rlib`.

الملف `_reference.py` oracle للصحة، وليس fallback صامتًا. تشخَّص `_native` الغائبة كامتداد غير مبني، ويبقى الخطأ الأصلي إذا فشل binary داخلي.

**توقّع:** الاختبار من cwd أجنبي يمنع `sys.path` من إخفاء ملفات مفقودة من wheel.

**Checkpoint:** caller ← الواجهة ← `_native` ← extraction ← `Vec<f64>` مملوكة ← domain ← class أو exception.

## 8. الأنواع الدقيقة وlifetimes في PyO3

نقبل فقط `int` و`float` built-in بالضبط. نرفض `bool` و`Fraction` و`Decimal` وsubclasses وNumPy scalars وكائنات `__float__`. الأعداد الصحيحة: `abs<=2**53`؛ والقيم المحوّلة finite و`abs<=1e150`.

تُحوّل/تُنسخ sequence إلى `Vec<f64>` قبل الحساب detached؛ هذا ليس zero-copy.

- يثبت `Python<'py>` أن thread في حالة attached؛
- يرتبط `Bound<'py,T>` بهذه attachment؛
- يملك `Py<T>` reference count لكنه يحتاج attachment صحيحة للوصول.

لا تدخل Python borrow إلى `domain.rs` ولا تعبر detach. تختبر `describe_payload` Unicode وbytes وoptional.

**Optional preview:** تحتاج NumPy وArrow وbuffers إلى عقود layout وlifetime وaliasing وmutation؛ وهي خارج المشروع الإلزامي.

## 9. عقد `faststats_rs` الدقيق

تقبل `summarize(samples, *, threshold)` من 1 إلى 1,000,000 عنصر وتعيد `Summary` frozen وفيها count/minimum/maximum/mean/anomaly_count/anomaly_ratio.

- domain/size/range/finiteness/threshold غير صالح → `ValueError`؛
- type مرفوض → `TypeError`؛
- مساواة threshold أو التقارب منه بـ`1e-12` → ليست anomaly؛
- الحقول الصحيحة exact، وfloats بتسامح `1e-12`.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/tests/test_parity.py" check="rust:contract" -->
```python source-ref
def assert_equivalent(samples, threshold):
    """يقارن الاختبار المرافق بين المرجع وnative."""
```

**تمرين:** توقّع نتائج `[True]` و`[2**53+1]` و`[nan]`. **الحل:** يعطي `True` خطأ `TypeError`؛ والآخران من نوع مقبول لكن بقيمة غير صالحة فيعطيان `ValueError`.

## 10. Classes مناسبة لبايثون وحالة transaction

`Summary` frozen للقراءة فقط. تملك `OnlineStats` الدوال `add` و`extend` و`reset` وproperties؛ حالة empty/reset هي `0/None/None/None`. الحد الإجمالي مليون.

تبقى methods دائمًا attached/GIL-held ولا تستخدم detach. ليست primitive للتعديل المتزامن. تحوّل `extend([4,bad,5])` القيم وتتحقق منها قبل commit؛ لا تتغير الحالة عند الفشل.

خطأ شائع: زيادة count أثناء extraction. يترك الخطأ الوسطي حالة جزئية، لذلك يحضّر التصميم التحديث ثم يؤكده.

## 11. الأخطاء وحدود panic

تعبر الأخطاء المتوقعة كـ`Result<T,DomainError>` ثم `TypeError`/`ValueError`. تستخدم عمليات PyO3 نوع `PyResult` والمعامل `?` دون فقدان exception الفعالة.

لا يستخدم `unwrap` أو`expect` على input خارجي. تحمي عبارتا `expect` في برنامج survival ثوابت literal مثبتة. لا يُستخدم panic كـvalidation ولا ننفذه داخل interpreter أو عبر FFI يدوي.

إذا ظهر `PanicException`، أعد الحالة في subprocess، وافحص invariant، وحوّل الفشل المتوقع إلى `Result`؛ لا تستخدم panic كمنطق عادي.

## 12. اختبارات باللغتين وtyping

- fmt للتنسيق، وclippy مع `-D warnings` للأنماط المشبوهة؛
- Cargo tests للمجال دون بايثون؛
- pytest للواجهة وparity والأخطاء وclasses وthreads وnative import الحقيقي؛
- stubtest لمقارنة runtime المثبت بالـstubs؛
- mypy strict لتجربة المستهلك.

يمثل `_native.pyi` اليدوي و`py.typed` العقد المستقر. تبقى introspection التجريبية في PyO3 اختيارية. توقف الاختبارات cache وتشرح الخطر؛ لا تعوض نسبة coverage عن اختبار السلوك.

## 13. `Python::detach` والتزامن الحتمي

يحدث extraction في حالة attached ثم تُنقل البيانات المملوكة إلى closure:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/src/lib.rs" check="rust:contract" -->
```rust source-ref
let result = py.detach(move || domain::summarize(&values, threshold));
```

لا يوجد داخلها `Python` أو`Bound` أوcallback أوPython borrow. تُنشأ class/exception بعدها في حالة attached.

لا يثبت timeout وحده دخولًا متوازيًا. يستخدم build القبول `test-hooks` آليتي `Mutex` و`Condvar`: يجب أن تدخل closureان قبل أن تستمر أي منهما. تكون feature متوقفة افتراضيًا، ولا يدخل `src/test_hooks.rs` في sdist، ولا تعرض wheels release أي API/symbol للاختبار.

تبقى الوحدة الأساسية `gil_used=true`. تحرير GIL في منطقة واحدة ليس audit كاملًا لـfree-threaded Python.

## 14. Benchmark صادق: الحدود والنسخ وbatching

نثبت equality أولًا، ثم نسجل release profile وwarm-up وتكرارات وmedian وأحجامًا متعددة. كلفة النسخ إلى `Vec` محسوبة.

```bash illustrative
python benchmarks/benchmark.py
```

قد تكون المدخلات الصغيرة أبطأ في Rust بسبب overhead. اجمع العمل في batch أو احتفظ ببايثون. لا يوجد speedup أدنى مطلوب.

**TODO:** أضف `n=100`. **تلميح:** قارن medians وسجل السياق والضوضاء، ولا تعمم جهازًا واحدًا.

## 15. التوزيع: sdist وwheelان

يحتوي sdist على metadata وlicense وREADME والواجهة/stubs وRust source وCargo/locks وtoolchain؛ ويستبعد targets وcaches وbinaries وrendezvous. يُفك ثم يبنى الـwheelان منه.

يعكس wheel الخاص Python/ABI/platform، مثل `cp313-cp313-manylinux_..._x86_64`. لا يعد targets أخرى.

تنتج feature `abi3-py311` اسم `cp311-abi3-<platform>` لـCPython المتوافق ذي GIL من 3.11، لكنها تبقى مقيدة بـOS/architecture/APIs. يحتاج `abi3t` إلى Python 3.15+ وfree-threaded audit منفصل؛ لا تدعيه النسخة الأساسية.

## 16. التحقق بأمر واحد

من داخل الفصل:

```bash illustrative
python -B examples/faststats-rs/tools/verify.py
```

يستخدم targets وwheels وvenvs وcwd مؤقتة، ويفحص pins وfmt/clippy/Cargo وخطأ move وحله وأول extension وhook wheel وsdist والـwheelين وpytest وtyping وbenchmark وimports/tags/content وhygiene.

يستدعي gate الكتاب adapter الخاص بـRust:

```bash illustrative
python -B ../tools/validate_book.py --plugin chapter-25-python-rust-integration/tools/bookcheck_plugin.py
```

يملك plugin فقط Rust/Cargo/PyO3/source refs، بينما يملك root فحوص Markdown وselectors وlinks وRTL وإمكانية الوصول والتصنيف وhygiene.

## 17. تعديلات موجهة

### تمرين A: حد العدد الصحيح

أضف `-(2**53)` و`-(2**53)-1`. التلميح: تُقبل الأولى وتعطي الثانية `ValueError`. النجاح: يتفق reference وnative.

### تمرين B: الحفاظ على transaction

ابدأ بـ`[1,2]` ثم جرّب `[3,inf,4]`. احفظ properties الأربع، وتحقق من exception ومن بقاء snapshot. يعرض `tests/test_classes.py` الحل المفسر.

### تمرين C: اختيار عدم استخدام Rust

قس workload في بايثون، وافحص batching وكلفة build/release/maintenance. “الاحتفاظ ببايثون” نتيجة صحيحة إذا دعمتها الأدلة.

## 18. أخطاء شائعة حسب الطبقة

- Compiler: حدد move/borrow/scope قبل clone.
- Cargo: حدّث lock بقصد ثم أعد suite.
- Linker: ثبّت build tools؛ لا يصلحه تعديل بايثون.
- maturin: فعّل venv أو ابنِ wheel.
- Import: استخدم cwd خارجيًا و`module.__file__`.
- Extraction: افحص النوع exact.
- GIL: بيانات مملوكة قبل detach ونتيجة Python بعدها.
- Packaging: أعد البناء دائمًا من sdist.
- Performance: equality وwarm-up وتكرار وسياق.

الخطأ دليل من طبقة، وليس حكمًا على المتعلم. شخّص أدنى طبقة تفشل أولًا.

## 19. Checkpoints وسلّم التقييم

الإعداد: toolchain والاسترداد. الأساسي: owner/borrow/Result. التكامل: call path. الاحترافي: parity/transaction/typing/import. Hero: detach/rendezvous/benchmark/tags.

التقييم 0–2 لكل بند: الصحة، ownership الملائم، أمان الحدود، API، الاسترداد، اختبارات Rust/Python، التزامن الحتمي، القياس الصادق، packaging/typing، والشرح. المشروع الكامل: لا يوجد صفر والمجموع 16/20 على الأقل.

## 20. مسرد وتأمل

- **crate:** وحدة Rust؛ **ownership:** مسؤولية التحرير؛ **borrow:** وصول مؤقت.
- **PyO3:** bindings/macros لـCPython؛ **GIL:** قفل CPython العادي.
- **ABI:** اتفاق ثنائي؛ **sdist:** أرشيف source؛ **wheel:** توزيع مبني؛ **abi3:** ABI مستقر مع حد Python ومنصة.

تأمل: ما أضيق native boundary مفيدة؟ ماذا يتغير مع NumPy buffer mutable أوPython handles عالمية؟ إن لم تستطع تسمية owner وlifetime وerror وtest وcompatibility فالحدود غير جاهزة.

## مراجع تم التحقق منها

- [التثبيت الرسمي لـRust](https://rust-lang.org/tools/install/)
- [كتاب Rust: ownership](https://doc.rust-lang.org/stable/book/ch04-01-what-is-ownership.html)
- [كتاب Rust: معالجة الأخطاء](https://doc.rust-lang.org/stable/book/ch09-00-error-handling.html)
- [دليل PyO3 0.29](https://pyo3.rs/v0.29.0/)
- [التوازي في PyO3 و`Python::detach`](https://pyo3.rs/main/parallelism)
- [ترتيب المشروع المختلط في maturin](https://www.maturin.rs/project_layout.html)
- [bindings وABI المستقر في maturin](https://www.maturin.rs/bindings.html)

تم فحص المادة الحساسة للإصدارات في 2026-07-13 وتثبيت pins في assets. أعد تشغيل المتحقق الكامل قبل تغيير أي pin.

</div>
