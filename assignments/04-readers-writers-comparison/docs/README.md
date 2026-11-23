<div dir="rtl" align="right">

# راهنمای فنی تمرین ۴ — مسئلهٔ Readers–Writers

## ۱. تعریف مسئله و خواص

یک ساختار دادهٔ مشترک توسط `R` خواننده و `W` نویسنده استفاده می‌شود. هر تعداد reader می‌توانند هم‌زمان در ناحیهٔ خواندن باشند؛ هر writer باید به‌تنهایی و بدون reader یا writer دیگر در ناحیهٔ نوشتن باشد. سه پرسش جدا باید پاسخ داده شوند:

- **Safety:** آیا دسترسی ناسازگار هم‌زمان رخ می‌دهد؟
- **Progress:** اگر منبع آزاد است، آیا درخواست واجد شرایط در نهایت وارد می‌شود؟
- **Fairness/bounded waiting:** آیا درخواست قدیمی ممکن است به‌علت ورودهای جدید بارها کنار زده شود؟

«Mutual exclusion» یک شرط safety است و به‌تنهایی fairness یا progress را ثابت نمی‌کند.

## ۲. Dekker و Peterson

Dekker و Peterson راه‌حل‌های نرم‌افزاری کلاسیک برای **دو شرکت‌کننده** در mutual exclusion هستند. Peterson از دو flag برای اعلام نیت و متغیر `turn` برای حل رقابت استفاده می‌کند؛ Dekker از نیت و تقدم متقابل با rollback استفاده می‌کند. هر دو در ارائهٔ textbook معمولاً atomic read/write، ترتیب حافظهٔ مناسب و دو فرایند را فرض می‌کنند و busy-wait دارند.

این الگوریتم‌ها قفل چندreader/چندwriter نیستند. ساختن تعمیم بی‌واسطه یا اجرای pseudocode کلاسیک روی Python threadها ادعای درستی ایجاد نمی‌کند؛ مدل حافظهٔ زبان، atomicity و memory-ordering باید جدا تحلیل شود. بنابراین این پروژه برای آن‌ها مقایسهٔ نظری و pseudocode ارائه می‌دهد، نه ماژول اجرایی.

### Peterson برای دو شرکت‌کننده — pseudocode

```text
flag[i] ← true
turn ← j
while flag[j] and turn = j: wait
critical section
flag[i] ← false
```

این قطعه به‌تنهایی قفل readers-writers را پیاده‌سازی نمی‌کند و به ترتیب حافظهٔ معتبر نیاز دارد.

## ۳. Semaphore: الگوی readers-preference

با `mutex=1`، `resource=1` و `read_count=0`:

```text
READER:
    wait(mutex)
    read_count ← read_count + 1
    if read_count = 1: wait(resource)
    signal(mutex)
    read data
    wait(mutex)
    read_count ← read_count - 1
    if read_count = 0: signal(resource)
    signal(mutex)

WRITER:
    wait(resource)
    write data
    signal(resource)
```

`mutex` شمارنده را محافظت می‌کند؛ اولین reader منبع را برای گروه readerها می‌گیرد و آخرین reader آن را آزاد می‌کند. Writerها کل منبع را می‌گیرند. چون reader تازه می‌تواند قبل از writer منتظر وارد شود، در حضور موج پیوستهٔ readerها writer ممکن است مدت نامحدود منتظر بماند. این الگوریتم reader-preference است، نه راه‌حل FIFO.

تغییر به writer-preference می‌تواند readerهای جدید را در زمان انتظار writer متوقف کند، اما در موج بی‌وقفهٔ writerها reader را گرسنه می‌کند. برای تضمین fairness، سیاست صف و فرض مدت ناحیهٔ بحرانی باید صریح باشد.

## ۴. Monitor و کد این مخزن

`FairReadersWritersMonitor` از `threading.Condition`، صف درخواست و حالت writer فعال/readerهای فعال استفاده می‌کند. readerهای پشت سر هم پیش از writer بعدی به شکل batch وارد می‌شوند. writer فقط وقتی وارد می‌شود که در ابتدای صف و هیچ مالک فعالی وجود نداشته باشد. readerهای صف‌شده پشت writer از او سبقت نمی‌گیرند.

| عملیات | شرط admission |
|---|---|
| خواندن | writer فعالی نباشد و writer قدیمی‌تری در صف نباشد |
| نوشتن | درخواست در ابتدای صف باشد و reader/writer فعالی نباشد |
| خروج | owner شناخته شود؛ حالت فعال پاک و waiterها بیدار شوند |

قفل deliberately non-reentrant است. upgrade از read به write رد می‌شود تا thread با نگه‌داشتن read lock منتظر خودش نماند. استفاده از context manager آزادسازی را در exception هم انجام می‌دهد.

## ۵. استدلال محدود fairness

هر درخواست در صف، درخواست‌های قبلی را نمی‌گذراند؛ readerهای متوالی پیش از writer همگی یک گروه‌اند. اگر تعداد درخواست‌های جلوتر متناهی باشد و هر ناحیهٔ بحرانی متناهی بماند، درخواست در نهایت به نوبت می‌رسد، مشروط بر این‌که OS threadهای بیدارشده را اجرا کند. این استدلال دربارهٔ صف monitor است، نه تضمین زمان واقعی یا deadline.

## ۶. آزمون و بازتولید

```bash
python -m pip install -e .
python -m unittest tests.test_readers_writers -v
python -m unittest discover -s tests -v
```

چهار تست بررسی می‌کنند که دو reader می‌توانند هم‌زمان داخل باشند، writer با reader یا writer دیگری هم‌پوشانی نداشته باشد، درخواست writer جلوتر از reader بعدی اجرا شود، و release/upgrade نامعتبر رد شود. آزمون‌های thread اجرای ممکن را پوشش می‌دهند؛ اثبات رسمی روی همهٔ زمان‌بندی‌های سیستم‌عامل نیستند.

## ۷. راهنمای شکل‌ها

- `figures/readers-writers-state.svg`: دو حالت مجاز روی دادهٔ مشترک را کنار هم می‌گذارد؛ readerها می‌توانند group باشند و writer باید انحصاری باشد.
- `figures/fifo-monitor-admission.svg`: صف `R1, R2, W1, R3` و ترتیب پذیرش را نشان می‌دهد؛ R1 و R2 با هم، سپس W1، سپس R3.

## ۸. جمع‌بندی و منابع

Dekker/Peterson ابزارهای دوشرکت‌کننده‌ای برای mutual exclusion هستند. Semaphore primitive عمومی و انعطاف‌پذیر است، ولی ترتیب wait/signal و fairness باید دقیق طراحی شود. Monitor state را کپسوله می‌کند و امکان پیاده‌سازی صف را می‌دهد، اما policyهای fairness آن را framework اعمال می‌کند. منبع ثبت‌شده در branch اولیه برای readers-writers: Courtois, Heymans, and Parnas, “Concurrent Control with Readers and Writers,” CACM 1971, DOI `10.1145/362759.362813`. منبع Peterson ثبت‌شده در branch: Peterson, “Myths About the Mutual Exclusion Problem,” IPL 1981, DOI `10.1016/0020-0190(81)90106-X`.

</div>
