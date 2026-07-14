<div dir="rtl">

# الفصل 24: تكامل Python وC++ — من الصفر إلى hero

[English](README.md) | [Español](README.es.md) | [Català](README.ca.md) | [Svenska](README.sv.md) | العربية

يعلّم هذا الفصل حدًا واحدًا بين نظامين، لا لغتين منفصلتين: تحتفظ Python بواجهة API سهلة، بينما تنفّذ C++ عملاً أصليًا محدد الحدود. تبدأ من دون خبرة في C++، وتبني برنامجًا صغيرًا ثم أول extension، وتنتهي بحزمة `faststats_cpp` ذات الأنواع وhost مستقل يضمّن Python.

تم التحقق من المشاريع على Linux باستخدام CPython 3.13.11 وGCC 13.3.0 وCMake 4.1.2 وpip 25.3 وpybind11 3.0.4 وscikit-build-core 1.0.3. يستهدف التصميم CPython 3.11+ وC++17 وCMake 3.20+ وGCC/Clang/MSVC، لكن هذا السجل لا يدّعي تنفيذ كل هدف.

## أهداف التعلم والمتطلبات السابقة

بعد الفصل تستطيع:

- التمييز بين compiler وlinker وloader وAPI/ABI الخاصة بـPython وABI الخاصة بـC++ ووسوم wheel؛
- قراءة الجزء الضروري من C++17: القيم والمراجع و`const` وvectors وclasses وRAII وsmart pointers وexceptions؛
- فصل core لا يعرف Python عن binding رفيع ووحدة `_native` خاصة وواجهة عامة ذات typing؛
- تفسير النسخ والذاكرة المستعارة وowners وlifetimes وGlobal Interpreter Lock (GIL) وcallbacks وthreads؛
- بناء sdist وwheel لمنصة محددة وإثبات الحزمة المثبتة داخل بيئة نظيفة؛
- قياس جدوى الحد بدلاً من افتراض أن C++ أسرع دائمًا؛
- تضمين استراتيجية Python محلية موثوقة مع بدء وإغلاق مضبوطين.

المتطلبات: [الدوال](../chapter-11-functions/README.ar.md)، و[البرمجة الكائنية](../chapter-12-oop/README.ar.md)، و[الاستثناءات](../chapter-14-exceptions/README.ar.md)، و[الوحدات](../chapter-15-modulos/README.ar.md)، و[البيئات](../chapter-16-entornos/README.ar.md)، و[الاختبار](../chapter-18-testing/README.ar.md)، و[التسجيل](../chapter-20-logging/README.ar.md)، و[الاستبطان](../chapter-22-introspection/README.ar.md). لا تحتاج معرفة C++ سابقة.

تحتاج compiler محليًا؛ وقد يتطلب تثبيته الإنترنت أو صلاحيات النظام. تكتب أوامر البناء المقبولة في مجلدات مؤقتة. لا تحذف ملفات أخرى لحل build غير مفهوم.

## اختر مسارًا

| المسار | الوقت | النتيجة القابلة للتشغيل | معيار الإكمال |
|---|---:|---|---|
| أساسي | 4 جلسات، 45–60 دقيقة | برنامج وextension باسم `hello_cpp` | شرح compile/link/load وإعادة البناء بعد تعديل |
| مهني | 5 جلسات | core وواجهة وأخطاء وownership بأنواع واضحة | نجاح contract/parity/lifetime tests |
| متقدم | 5 جلسات | buffers وcallbacks وGIL وwheel آمنة | نجاح concurrency والتثبيت النظيف |
| Hero | 3–4 جلسات | core مع sanitizers واستراتيجية مضمّنة | ذكر الحدود وتحديد متى لا نستخدم C++ |

نقطة نهاية المسار مفيدة بذاتها، ولا تعني إكمال المسارات اللاحقة.

## المصطلحات وخريطة الحد

- **Compiler:** يحول source في C++ إلى object machine code.
- **Linker:** يصل objects وlibraries ويحل الأسماء بينها.
- **Loader:** يحمّل executable أو shared library داخل العملية.
- **API:** الأسماء والسلوك الذي يستعمله caller.
- **ABI:** عقد ثنائي؛ ABI لـCPython وABI لـC++ واعتماديات المنصة قيود مختلفة.
- **RAII:** lifetime الكائن في C++ يتحكم في cleanup المورد.
- **الاستعارة:** وصول مؤقت بلا نقل ownership.
- **GIL:** قفل CPython المطلوب عند لمس كائن Python أو C API.
- **Wheel:** أرشيف تثبيت تحمل وسومه Python وABI والمنصة.

```text illustrative
Python caller
  -> faststats_cpp public facade
  -> private _native binding (validate and convert)
  -> owned C++ values OR call-scoped borrowed buffer
  -> Python-independent faststats core
  -> Summary or translated exception
```

الواجهة هي العقد العام، و`_native` آلية قابلة للاستبدال. لا يضم core ملف `Python.h`. لا يدخل buffer مستعار إلى المنطقة التي أُطلق فيها GIL.

## فحص toolchain قبل البدء

أنشئ بيئة مؤقتة. قد يستخدم التثبيت الأول الشبكة، وقد يطلب مدير compiler صلاحيات إدارية.

```console illustrative
python -m venv /tmp/course-cpp-venv
source /tmp/course-cpp-venv/bin/activate       # POSIX
# .\course-cpp-venv\Scripts\Activate.ps1     # PowerShell
python -m pip install -r chapter-24-python-cpp-integration/examples/faststats-cpp/requirements-dev.lock
python -B chapter-24-python-cpp-integration/tools/preflight.py
```

يعرض preflight مسار interpreter والمعمارية والبيئة وcompiler وCMake وpip وpybind11 وscikit-build-core وbuild وpytest وmypy. أصلح الطبقة المفقودة نفسها؛ لا يصلح workaround في loader غياب compiler.

افصل خطوات المنصة عن التحقق: تستخدم Ubuntu/Debian حزمة `build-essential`، وتستخدم macOS أدوات Apple Command Line عبر `xcode-select --install`، وتستخدم Windows Visual Studio Build Tools مع **Desktop development with C++** وDeveloper PowerShell. قد تتطلب شبكة وصلاحيات. يسجل `requirements-dev.lock` إصدارات الأدوات المباشرة الدقيقة للمضيف المتحقق منه، لكنه لا يحتوي graph انتقالياً أو hashes وليس lock محكماً متعدد المنصات. ثبّته داخل venv فقط، واستخدم `constraints-build.txt` للبناء المعزول، وأعد preflight، ولا تدّع دعم منصة لم تنفذها.

تضبط عمليات PEP 517 المقبولة المتغير `PIP_BUILD_CONSTRAINT` على `constraints-build.txt`، فيستخدم العزل pybind11 3.0.4 وscikit-build-core 1.0.3. هذا مختلف عن تقييد حزم runtime.

### شخّص المرحلة لا العَرَض

| الملاحظة | المرحلة | السؤال الأول | فعل قابل للتراجع |
|---|---|---|---|
| syntax أو type غير معروف | compile | هل declaration/header ظاهر؟ | اقرأ أول diagnostic |
| unresolved symbol | link | هل رُبط object/library؟ | راجع target sources |
| الوحدة موجودة ولا تُستورد | load | هل tags/dependencies مطابقة؟ | اختبر wheel من cwd آخر |
| `TypeError` من Python | binding/API | هل القيمة ضمن العقد؟ | اختصر إلى نداء صحيح وآخر خاطئ |

## المسار الأساسي: أول برنامج C++

### الجلسة 1 — القيم والدوال وscope والتشخيص

توقّع من يدمر vector في `ScoreReport report(std::vector<double>{6,8,10})`. كائن `ScoreReport` هو owner؛ يتحرر العضو حين يخرج الكائن من scope. هذا RAII ولا توجد `free()` يدوية.

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/00-cpp-survival/src/main.cpp check=cpp:contract -->
```cpp source-ref
const course::ScoreReport report(std::vector<double>{6.0, 8.0, 10.0});
std::cout << report.label() << ": mean=" << report.mean() << '\n';
```

```console illustrative
cmake -S chapter-24-python-cpp-integration/examples/00-cpp-survival -B /tmp/cpp-survival-build -DCMAKE_BUILD_TYPE=Debug
cmake --build /tmp/cpp-survival-build --config Debug
ctest --test-dir /tmp/cpp-survival-build --output-on-failure -C Debug
```

Happy path: يظهر `practice batch: mean=8`. Edge case: يرمي vector الفارغ `std::invalid_argument` ويلتقطه `main()`. خطأ قابل للتعافي: ترجم `expected_compile_error.cpp` وحده واقرأ أول diagnostic؛ لا يضمه CMake إلى البناء العادي.

**TODO:** غيّر الدرجات وتوقع mean أولاً. **تلميح:** أبقِ `const`. **الحل:** يحدّث `mean += (value - mean) / count` قيمة `double` مملوكة؛ لا Python ولا إدارة ذاكرة يدوية بعد.

خطأ شائع: نسيان namespace في implementation. اقرأ أول خطأ، وافحص الاسم الكامل، وأعد بناء المجلد المؤقت فقط.

### الجلسة 2 — headers والمراجع وvectors وclasses وexceptions

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/00-cpp-survival/include/score.hpp check=cpp:contract -->
```cpp source-ref
class ScoreReport {
public:
    explicit ScoreReport(std::vector<double> values);
    [[nodiscard]] double mean() const;
    [[nodiscard]] const std::string& label() const noexcept;
};
```

يعلن header ما يمكن استعماله، ويعرّفه source. تعد `const` الأخيرة بعدم التغيير. تستعير `const std::string&` العضو بلا نسخ ما دام report حيًا. تمنع `explicit` التحويل الضمني المفاجئ. يُلتقط exception القابل للتعافي عند حد واضح ولا يخرج من destructor.

Checkpoint: اشرح owner وlifetime لمرجع `label` قبل الاستمرار.

**دورة مصغرة:** توقّع أثر إرجاع نسخة، وشغّل happy test، ثم TODO أرجع قيمة. تلميح: قارن signatures؛ يبقى constructor الفارغ edge قابلاً للتعافي. الحل موازنة copy مع lifetime dependency. تأمل أي عقد أسهل للصيانة.

### الجلسة 3 — compiler وlinker وloader

Source→object هي compile، وobjects→executable/library هي link، وimport يشغّل loader. صنّف خطأ من كل مرحلة.

**TODO:** احذف `src/score.cpp` مؤقتًا من target. **تلميح:** declaration ما زال ظاهرًا. **الحل:** تنجح compile وتفشل link لغياب definitions. أعد الملف مباشرة.

تحقق من build المستعاد وedge بلا definition. تأمل: يحدد أول diagnostic أقدم مرحلة مكسورة؛ وما بعده غالبًا نتائج.

### الجلسة 4 — أول pybind11 extension

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/01-first-extension/src/bindings.cpp check=cpp:contract -->
```cpp source-ref
PYBIND11_MODULE(hello_cpp, module) {
    module.def("add", &add, py::arg("left"), py::arg("right"));
}
```

يعرّف macro مدخل loader؛ يبني CMake، ويربط scikit-build-core بـPEP 517، وينقل wheel النتيجة. ثبّت في مؤقت واستورد من cwd آخر.

توقّع `hello_cpp.add("20",22)`: يحدث `TypeError` ولا يُحلل النص. بدّل الجمع بالطرح، راقب فشل test، ثم استعده وأعد البناء. بذلك يكتمل المسار الأساسي.

## المسار المهني: ثبّت العقد قبل التحسين

### الجلسة 5 — مرجع Python والمجال الدقيق

`_reference.py` دلالة قابلة للقراءة، وليس fallback صامتًا. تقبل `summarize` من 1 إلى 1,000,000 قيمة built-in `int`/`float` بالضبط؛ وتستبعد `bool` وsubclasses و`Fraction` و`Decimal` وNumPy scalar و`__float__`. يحقق integer `abs(x)<=2**53`، والقيمة finite `abs(x)<=1e150`، وthreshold ضمن `[0,1e150]`.

يُحسب mean بترتيب الإدخال مع `mean += (value - mean) / count`، ثم تقارن جولة ثانية بالmean النهائي. يُعد delta إن تجاوز threshold ولم يكن `isclose` عند `1e-12`. تعطي `[-3,-3,-1]` مع `0.5` ثلاث anomalies؛ لا تُعد المساواة.

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/faststats-cpp/python/faststats_cpp/_reference.py check=cpp:contract -->
```python source-ref
expected = summarize([-3, -3, -1], threshold=0.5)
assert expected.anomaly_count == 3
```

Happy: ints/floats دقيقة. Edge: عنصر واحد أو batch ثابت. الأخطاء: فارغ، non-finite، range، type، threshold. تستخدم parity العائمة rel/abs `1e-12`.

**TODO:** أضف boundary إلى اختبارات reference/native. **تلميح:** غيّر قيدًا واحدًا. الحل: تحقق من exception class وبقاء state. تأمل لماذا العقد الدقيق أفضل من “يقبل أرقامًا”.

### الجلسة 6 — core وbinding والواجهة وtyping

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/faststats-cpp/cpp/include/faststats_cpp/core.hpp check=cpp:contract -->
```cpp source-ref
[[nodiscard]] Summary summarize(const double* values, std::size_t size,
                                double threshold);
void normalize_in_place(double* values, std::size_t size);
```

يختبر CTest الـcore بلا Python. يتحقق `bindings.cpp` من Python types/buffers. تبقى `_native` خاصة؛ وتقدم `__init__.py` و`_native.pyi` و`py.typed` الواجهة والأنواع. تميز الواجهة بين “غير مبنية” وbinary معطوبة ولا تخفيها بالمرجع.

**دورة مصغرة:** توقع أي طبقة تعرف Python type خاطئًا، شغّل CTest/pytest، ثم TODO غيّر default في stub فقط. تلميح: typing وstubtest يكتشفانه. أعد default وتأمل فائدة binding الرقيق.

### الجلسة 7 — classes والأخطاء التبادلية

تقدم `OnlineStats.add/extend/reset` count/min/max/mean؛ الحالة الفارغة `(0,None,None,None)` والحد مليون. تتحقق `extend` أولًا: بعد `[1,2]` يترك `[3,inf]` الحالة `(2,1,2,1.5)` كاملة.

يصبح خطأ domain في C++ `FaststatsError`؛ وأخطاء type/range/layout `TypeError`/`ValueError`. يعود خطأ callback بعد RAII cleanup. لا يعبر exception حدود `main()` أو destructor أو `noexcept`.

**TODO:** مدد بقيم صحيحة ثم أضف قيمة خاطئة وقارن state. **تلميح:** تحقق داخل storage مؤقت. Happy: commit؛ edge: extend فارغ؛ الفشل: rollback كامل. تأمل هل إعادة محاولة عملية جزئية آمنة.

### الجلسة 8 — ownership وpolicies وsmart holders

| الحد | Owner | مدة الاستعارة | الدليل |
|---|---|---|---|
| `Summary` معادة | Python wrapper | لا شيء | properties read-only |
| `Dataset.metadata` | الأب `Dataset` | مرجع child | `reference_internal` test |
| `BorrowingView` | caller/keep-alive | lifetime للview | `keep_alive<1,2>` test |
| `TrackedResource` | unique smart holder | قابل للنقل | counter يعود للخط الأساسي |

يوضح `py::smart_holder` smart pointers وtrampolines، لكنه لا يبرر raw owner. يحتفظ `ObserverRunner` بـPython-derived observer ولا يستدعي destructor كود Python.

**TODO:** ارسم owners. **تلميح:** يبدأ السهم ممن يتحكم بالتدمير. **الحل:** تربط `reference_internal` الطفل بالأب، و`keep_alive` patient بـnurse، وتنقل `consume_resource` ownership مرة واحدة.

Checkpoint مهني: شغّل Debug/Release واشرح domain وerror وowner لكل عملية.

## المسار المتقدم: buffers وGIL والقياس وwheels

### الجلسة 9 — iterable منسوخ وbuffer مستعار

تنسخ `summarize` إلى `std::vector`؛ هذا مريح وله كلفة. تستعير `summarize_buffer` buffer أحادي البعد من native `double`، aligned وcontiguous وpositive stride. تتطلب `normalize_in_place` writable كذلك.

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/faststats-cpp/tests/test_buffers.py check=cpp:contract -->
```python source-ref
values = array("d", [2.0, 4.0, 6.0])
faststats_cpp.normalize_in_place(values)
assert values.tolist() == [0.0, 0.5, 1.0]
```

تحافظ الدالتان على GIL وتمنعان mutation متزامنة ولا تخزنان pointer. يتم التحقق كله قبل التعديل: لا تترك NaN أو فارغ أو oversized أو read-only أو strided أو multidimensional أو format/alignment خاطئ تغييرًا جزئيًا. تتحول القيم المتساوية إلى `0.0`. تبقى NumPy اختيارية؛ تكفي `array('d')` و`memoryview`.

**TODO:** جرّب `memoryview` read-only وstrided. **تلميح:** format وdimension وstride وwritable قبل القراءة. Happy: contiguous؛ edge: constant؛ خطأ قابل للتعافي: layout. تأمل متى تكون copy أكثر أمانًا من zero-copy.

### الجلسة 10 — callbacks وGIL وconcurrency حتمية

تتحقق `summarize_many` وتنسخ مع GIL، وتطلقه حول core يعمل على storage مملوكة فقط، ثم تستعيده قبل النتيجة أو الخطأ. لا تدخل buffers أوcallbacks هناك.

يستخدم target مستقل `_faststats_test` مع `FASTSTATS_TEST_HOOKS` mutex/condition-variable: يجب أن تدخل مكالمتان قبل أن تكملا. تفشل النسخة serial أو GIL-held، ولا يحتوي wheel على hook.

خطأ شائع: إطلاق GIL مع `py::object`. الترتيب الصحيح: validate/convert → own → release → pure C++ → reacquire → Python.

**TODO:** احذف `gil_scoped_release` من test target فقط. **تلميح:** لا يعبر threadان rendezvous. استعده بعد timeout محدود؛ يثبت happy دخولًا متزامنًا. تأمل لماذا sleep دليل أضعف.

### الجلسة 11 — benchmarks صادقة

يتحقق benchmark من parity ويعمل warm-up وتكرارات وmedian ويسجل السياق، مع أحجام 1 و10 و1,000 و100,000. قد تخسر المكالمة الصغيرة بسبب boundary؛ وهذه نتيجة مفيدة.

```console illustrative
python chapter-24-python-cpp-integration/examples/faststats-cpp/benchmarks/benchmark.py --profile release --repeats 7
```

**TODO:** توقع crossover. **تلميح:** فكر في batching. **الحل:** أبقِ Python للعمل الصغير أو المفوض؛ استخدم C++ بعد صحة وقياس ممثل.

### الجلسة 12 — sdist وwheel وtags والتثبيت النظيف

يبني `verify_artifacts.py` sdist ويفحصه، ثم يعيد wheel منه ويثبته في venv/cwd نظيفين. يشغّل `pip check` وsmoke و`mypy.stubtest` وconsumer صارمًا واختبارات type سلبية لثلاثة constructors native-only ويتأكد من غياب hook. على المضيف المدعوم يفشل إذا أبلغ `ldd` عن `not found`.

تشفّر tags Python/ABI/platform، لا compiler/C++ ABI/shared libs؛ وتُفحص هذه منفصلة. لا تعِد تسمية wheel إلى `abi3`: إن Limited API وCPython ABI وC++ ABI والمنصة وعود مختلفة.

Checkpoint: لماذا import بجانب source أضعف من sdist→wheel→clean venv؟

**TODO:** افحص اسم wheel وما لا يعد به. **تلميح:** tags مقابل compiler/C++ ABI/shared libs. Happy: clean install؛ edge: interpreter آخر؛ loader error ظاهر. تأمل قبل وصفه portable.

## مسار hero: debugging وembedding والحدود

### الجلسة 13 — Debug وwarnings وsanitizers

يحفظ Debug الرموز، ويمثل Release التوزيع. تصبح warnings العالية أخطاء. مع GCC/Clang يضيف `FASTSTATS_ENABLE_SANITIZERS=ON` ASan/UBSan إلى core المستقل فقط؛ وتقدم البيئات الأخرى skip مفسرًا.

لا تتعمد segfault داخل Python. استخدم رسومات owner وcounters وC++ tests وsanitizer داخل build مؤقت قابل للتراجع.

**TODO:** شغّل core مع sanitizer وحدد flags. **تلميح:** targets مستقلة فقط. يكتب CMake دليل capability؛ لا يُعلن النجاح إلا عند `enabled:<compiler>`، ويعطي compiler غير المدعوم skip صريحاً. يبدأ report تحقيقاً قابلاً للتعافي. تأمل أصغر reproducer آمن.

### الجلسة 14 — تضمين استراتيجية موثوقة

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/embed-python/src/main.cpp check=cpp:contract -->
```cpp source-ref
py::scoped_interpreter interpreter;
py::module_ strategy = py::module_::import("trusted_strategy");
py::object result = strategy.attr("evaluate")(values);
```

يتطلب host `--strategy-dir`، ويحوّل المسار إلى canonical، ويستبدل `sys.path`، ويستورد اسمًا ثابتًا، ويرسل list ذات أنواع، ويشترط float دقيقًا. حالات missing/raise/invalid لها exit غير صفر. لا يفوز module خداع في cwd.

تموت handles قبل interpreter ويلتقط `main()` الأخطاء. لا يوجد eval أو module غير موثوق: تملك Python المضمنة صلاحيات عملية host.

**TODO:** شغّل good وraising وinvalid من decoy cwd. **تلميح:** module الثابت من canonical directory. Happy: success؛ edges: callable/result؛ Python error: exit غير صفر. تأمل كيف يغير `eval` نموذج التهديد.

### الجلسة 15 — free-threading وsubinterpreters تدقيق مستقبلي

لا تستخدم الوحدة `mod_gil_not_used()` ولا تدعي الدعم. يجب تدقيق globals وallocators وholders وcallbacks وlocks وinit وinterpreter-local data وteardown ومصفوفة تنفيذ حقيقية. لا يكفي tag.

Cython وnanobind وSWIG و`ctypes` وC API بدائل وليست مسارات موازية. لا يشمل الفصل GPU وSIMD وOpenMP وcross-compilation وmobile/WASM والنشر ومكتبة خارجية كبيرة.

**TODO:** اكتب support matrix دون كود. **تلميح:** runtime وinterpreter count وcallbacks وglobals وteardown. Happy: GIL build مختبر؛ edges: free-threaded/subinterpreters. الحل change جديدة بدليل لا tag. تأمل كلفة كل وعد توافق.

## التحقق من capstone

شغّل الأوامر من جذر المستودع. ينشئ المتحقق venv ومجلدات build وwheels داخل أدلة مؤقتة، وقد يحتاج إلى الشبكة عند التثبيت الأول للأدوات ذات الـpins المباشرة.

```console illustrative
python -B chapter-24-python-cpp-integration/tools/verify_all.py
python -B tools/validate_book.py --plugin chapter-24-python-cpp-integration/tools/bookcheck_plugin.py
```

يغطي survival وأول extension وCTest وpytest في Debug/Release وconcurrency وsanitizer المتاح وsdist→wheel وtyping وdependencies وembedding. يجب أن يجد scan صريح صفر venv/build/dist/archive/library/object/cache داخل الفصل، حتى المسارات المتجاهلة.

## تمارين وتلميحات وحلول مفسرة

1. **أساسي:** أضف `range()` إلى `ScoreReport` وتوقع السالب. تلميح: min/max في دورة. الحل: ownership داخل class والتحقق من الفارغ قبل index.
2. **مهني:** أضف `variance` read-only إلى المرجع أولاً. تلميح: ثبّت الدلالة. الحل: reference→core→binding→stub→CTest→pytest→docs.
3. **متقدم:** قارن iterable/buffer لـ100,000 doubles. تلميح: parity قبل timing. الحل: انسب الكلفة إلى conversion/copy/boundary.
4. **Hero:** اقترح free-threading بلا تنفيذ. تلميح: اذكر globals ومسارات Python. الحل: matrix/tests قبل وعد التوافق.

## معيار التقييم الذاتي

| المجال | جاهز | يحتاج مراجعة | الدليل |
|---|---|---|---|
| الصحة/API | العقد والمعاملات متطابقة | النتائج تبدو معقولة فقط | CTest وpytest parity |
| Ownership/الأمان | تشرح owner/borrow/GIL | تخمّن policies | lifetime وbuffer وcallback وrendezvous |
| التحقق | Debug/Release والآثار مؤقتة | import بجانب source | logs وclean venv |
| القرار الهندسي | تقيس وتذكر الحدود | تعد بسرعة عامة | benchmark وABI audit |

تأمل: ما الحد الأقل ثقة لديك، وما الدليل الذي يحسنه؟ إن كانت الإجابة فقط «لقد تم تجميعه»، فأضف input خاطئًا أو lifetime أو packaging scenario.

## المصادر والنَّسب

النص والتمارين أصلية. المراجع: [Python extending and embedding](https://docs.python.org/3/extending/index.html)، و[pybind11 build systems](https://pybind11.readthedocs.io/en/stable/compiling.html)، و[call policies](https://pybind11.readthedocs.io/en/stable/advanced/functions.html)، و[smart holders](https://pybind11.readthedocs.io/en/stable/advanced/smart_ptrs.html)، و[scikit-build-core](https://scikit-build-core.readthedocs.io/en/stable/guide/getting_started.html)، و[CMake FindPython](https://cmake.org/cmake/help/latest/module/FindPython.html).

</div>
