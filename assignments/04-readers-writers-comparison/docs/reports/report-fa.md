<div dir="rtl" align="right">

# تمرین ۴ — Dekker، Peterson، Semaphore و Monitor (پیش‌نویس پژوهشی کوتاه)

> **وضعیت:** این گزارش کاریِ مبتنی بر منبع، بسیار کوتاه‌تر از نسخهٔ نهایی حدوداً ۴۰صفحه‌ای فارسی/انگلیسی درخواستی است. برای پرکردن صفحه متن تکراری افزوده نشده است. متادیتای منابع و ادعاهای ارجاع‌شده در ۲۳ نوامبر ۲۰۲۶ بررسی شده‌اند؛ حسابرسی در [یادداشت منابع](../../../../docs/research-source-audit.md) است. Word/PDF خروجی‌های آزمایشی‌اند.

## چکیده

انحصار متقابل از وضعیت مشترک حفاظت می‌کند، اما سازوکار اخذ قفل بر پیشرفت، انتظار، مصرف CPU و نوع برنامهٔ قابل بیان اثر دارد. الگوریتم‌های نرم‌افزاری کلاسیک Dekker و Peterson با flagهای نیت و متغیر turn دو شرکت‌کننده را هماهنگ می‌کنند. Semaphore عملیات اتمی wait/signal می‌دهد؛ monitor دادهٔ مشترک و رویه‌های synchronization را کپسوله می‌کند. در مسئلهٔ خوانندگان و نویسندگان، چند reader می‌توانند هم‌زمان کار کنند ولی writer باید تنها باشد. نام «semaphore» یا «monitor» به‌تنهایی fairness را تضمین نمی‌کند؛ اولویت reader/writer، ترتیب بیدارسازی و سیاست صف بر گرسنگی اثر می‌گذارند. این گزارش فرض‌ها و تضمین‌ها را مقایسه می‌کند و سپس monitor پایتونیِ FIFO-by-phase مخزن را توضیح می‌دهد، بی‌آنکه آن را اثباتی برای تمام interleavingها معرفی کند.

## ۱. پرسش‌های درستی در هم‌زمانی

یک طراحی synchronization باید مشخص کند کدام ویژگی را فراهم می‌کند:

- **انحصار متقابل (ایمنی):** هم‌پوشانی ممنوعِ ناحیه‌های بحرانی رخ ندهد.
- **پیشرفت:** اگر درخواست وجود دارد و ناحیهٔ بحرانی می‌تواند آزاد شود، دست‌کم درخواست مجاز پیش برود؛ سیستم همه را بی‌دلیل معطل نکند.
- **انتظار محدود / سبقت محدود:** پس از درخواست ورود یک فرایند، تعداد ورودهای بعدی که می‌توانند از آن جلو بزنند کران داشته باشد.
- **آزادی از گرسنگی:** هر درخواستِ پیوسته‌منتظر، تحت فرض‌های زمان‌بندی و مدت critical section نهایتاً وارد شود.
- **کران زمانی:** سقف صریح بر حسب ثانیه یا tick. آزادی از گرسنگی به‌تنهایی کران زمانی بلادرنگ نمی‌دهد.

این‌ها ویژگی‌های یکسانی نیستند. قفل می‌تواند انحصار متقابل داشته باشد ولی ناعادلانه باشد. صف منصفانه ممکن است تعداد سبقت را محدود کند، اما اگر مدت critical section یا تأخیر اجرای سیستم‌عامل کران نداشته باشد، deadline زمانی نمی‌دهد. تست‌ها باگ را آشکار می‌کنند، اما همهٔ اجراهای ممکن را اثبات نمی‌کنند.

## ۲. مسئلهٔ خوانندگان و نویسندگان و سیاست سرویس

در مسئلهٔ کلاسیک، چند reader چون داده را تغییر نمی‌دهند می‌توانند هم‌زمان به منبع دسترسی داشته باشند؛ writer به دسترسی انحصاری نیاز دارد. Courtois، Heymans و Parnas دو صورت مسئله با هدف‌های مختلف تعریف کردند: کمینه‌کردن تأخیر reader یا فراهم‌کردن امکان نوشتن هرچه زودتر [۱]. این هدف‌ها می‌توانند به دو کلاس متفاوت اولویت بدهند. تحلیل بعدی مبادلهٔ گرسنگی را صریح می‌کند: با ورود پیوستهٔ reader، سیاست reader-preference می‌تواند writer را نامحدود معطل کند؛ با جریان مداوم writer، writer-preference می‌تواند reader را عقب بیندازد [۲].

سیاست سوم می‌تواند برای هر دو کلاس پیشرفت بخواهد، اما تضمین آن به قاعدهٔ admission/صف و فرض‌های مربوط به thread و مدت critical section وابسته است. عبارت «قفل readers-writers» به‌تنهایی مشخصات کامل سیاست نیست. باید گفته شود کدام کلاس از کدام کلاس سبقت می‌گیرد، readerها batch می‌شوند یا نه، و پیشرفت بر چه فرض زمان‌بندی استوار است.

## ۳. الگوریتم دوفرایندی Dekker

الگوریتم Dekker یک راه‌حل کلاسیک نرم‌افزاری برای انحصار متقابل دو فرایند است. با `flag[0]` و `flag[1]` اولیهٔ false، هر فرایند قصد ورود را اعلام می‌کند. اگر هر دو بخواهند وارد شوند، متغیر مشترک `turn` تعارض را حل می‌کند؛ فرایندی که نوبتش نیست موقتاً flag خود را پایین می‌آورد و پس از تغییر turn دوباره تلاش می‌کند.

```text
process i, where j = 1 - i:
    repeat:
        flag[i] ← true
        while flag[j]:
            if turn = j:
                flag[i] ← false
                while turn = j:
                    busy_wait
                flag[i] ← true
        critical_section
        turn ← j
        flag[i] ← false
        remainder_section
```

در فرض textbook یعنی خواندن/نوشتن اتمی متغیر مشترک، مشاهده‌پذیری sequentially consistent و رعایت protocol توسط دو شرکت‌کننده، flagها ورود هم‌زمان را منع می‌کنند و `turn` حالت درخواست هم‌زمان را حل می‌کند. اگر فقط یک فرایند درخواست کند، دیگری مانع نمی‌شود؛ با خروج نیز تقدم جابه‌جا می‌شود. منطق retry تو در تو از Peterson پیچیده‌تر است و الگوریتم busy-wait می‌کند. این شبه‌کد تحلیلی است، نه کدی که این مخزن اجرا کند.

## ۴. الگوریتم دوفرایندی Peterson

الگوریتم Peterson برای هر فرایند یک flag نیت و یک متغیر `turn` دارد:

```text
process i, where j = 1 - i:
    flag[i] ← true
    turn ← j
    while flag[j] and turn = j:
        busy_wait
    critical_section
    flag[i] ← false
    remainder_section
```

برای دو فرایند تحت مدل ایده‌آل atomic و sequentially consistent، شرط ورود مانع عبور هم‌زمان هر دو از حلقه می‌شود. اگر هر دو flag بالا باشند، `turn` تعیین می‌کند کدام‌یک صبر کند؛ اگر فقط یک flag بالا باشد، پرچم طرف دیگر false است و درخواست‌کننده می‌تواند وارد شود. این الگوریتم برای آموزش mutual exclusion، progress و bounded bypass مفید است، اما راه‌حل مستقیم هر تعداد reader و writer نیست.

مدل حافظه بخشی از proof است. کامپایلر یا پردازنده می‌تواند load/store معمولی را جابه‌جا یا به تأخیر بیندازد؛ برهان متغیرهای atomic و سازگار با sequential consistency، ترجمهٔ literal با متغیرهای عادی را خودبه‌خود معتبر نمی‌کند. Ridge یک پیاده‌سازی Peterson را بررسی و نسخهٔ اصلاح‌شده برای حافظهٔ ضعیف ارائه می‌کند؛ بنابراین semantics پیاده‌سازی اهمیت دارد [۶]. این مخزن Dekker یا Peterson را به شکل قفل Python پیاده‌سازی نکرده است.

## ۵. Semaphore

Semaphore شیئی شبیه شمارنده با عملیات اتمی wait و signal است که معمولاً `P/V` یا `wait/signal` نامیده می‌شوند. Dijkstra بر indivisible بودن این عملیات تأکید می‌کند [۳]. **Semaphore دودویی** یک permit دارد؛ **شمارشی** تعداد نامنفی permitهای موجود را نمایش می‌دهد. پیاده‌سازی ممکن است thread را هنگام نبود permit block کند؛ ولی خود واژهٔ semaphore ترتیب FIFO را مشخص نمی‌کند.

الگوی رایج reader-preference از mutex برای محافظت `read_count` استفاده می‌کند. اولین reader روی semaphore منبع wait می‌کند؛ هر reader شمارنده را در حالت محافظت‌شده زیاد می‌کند و آخرین reader منبع را signal می‌کند. writerها روی همان منبع منتظرند. این روش readerهای هم‌زمان را مجاز می‌کند، ولی readerهای تازه می‌توانند به batch فعال بپیوندند و writer منتظر را عقب بیندازند. برعکس‌کردن دروازه به نفع writer می‌تواند reader را عقب بیندازد. Kawash این دو صورت را بررسی و الگوریتم سومی با semaphore و پیشرفت هر دو کلاس، همراه با بررسی SPIN، ارائه می‌کند [۲].

Semaphoreها توان بیان بالایی دارند و می‌توانند به‌جای busy-wait از blocking استفاده کنند. از سوی دیگر ترتیب را به برنامه‌نویس می‌سپارند: جفت‌نشدن wait/signal، مقداردهی اشتباه، signal روی شرط نادرست یا تکیه به سیاست صف اعلام‌نشده می‌تواند deadlock، هم‌پوشانی ناایمن، توقف پیشرفت یا starvation ایجاد کند.

## ۶. Monitor و condition variable

Monitor وضعیت مشترک را همراه رویه‌هایی که روی آن کار می‌کنند گروه‌بندی می‌کند. تحت قاعدهٔ انحصار monitor، در هر لحظه حداکثر یک thread رویهٔ monitor را اجرا می‌کند؛ condition variable به رویه اجازه می‌دهد تا برقرارشدن predicate منتظر بماند. مقالهٔ Hoare monitor را به‌عنوان ساختار سیستم‌عامل توسعه می‌دهد، synchronization و پیاده‌سازی semaphore-based را بررسی می‌کند و مثال reader/writer دارد [۴].

معنای condition variable مهم است. در مدل Hoare-style با signal-and-urgent-wait، پس از signal پردازهٔ بیدارشده فوراً کنترل monitor را می‌گیرد. در پیاده‌سازی Mesa-style، signal فقط waiter را runnable می‌کند و signaler ادامه می‌دهد؛ waiter بعداً monitor را دوباره می‌گیرد و باید predicate را در حلقه بررسی کند. بنابراین کد باید روی شرطی مانند `while active_writer or earlier_writer_waiting: condition.wait()` منتظر بماند و نباید فرض کند بیدارشدن به معنای مجازشدن ورود است. Monitor invariant و state را کپسوله می‌کند، اما سیاست notification و صف ورود همچنان fairness را تعیین می‌کند.

## ۷. مقایسه

| سازوکار | دامنه | سبک انتظار | فرض‌های درستی | مسئلهٔ انصاف/گرسنگی |
|---|---|---|---|---|
| Dekker | دقیقاً دو شرکت‌کننده | busy-wait | متغیر مشترک اتمی؛ sequential consistency؛ رعایت پروتکل | در مدل کلاسیک turn درخواست هم‌زمان را حل می‌کند؛ کران زمان واقعی ندارد؛ CPU مصرف می‌کند |
| Peterson | دقیقاً دو شرکت‌کننده | busy-wait | متغیر مشترک اتمی؛ فرض ترتیب/مدل حافظه | bypass در مدل textbook محدود است؛ ترجمهٔ ساده با حافظهٔ ضعیف ممکن است شکست بخورد |
| Semaphore | عمومی برای permit/منبع | معمولاً blocking و وابسته به پیاده‌سازی | wait/signal اتمی، مقداردهی و جفت‌شدن صحیح | انصاف تابع صف و بیدارسازی است؛ اولویت reader/writer می‌تواند کلاس دیگر را گرسنه کند |
| Monitor | کپسوله‌سازی state عمومی | انتظار/blocking روی شرط | invariant صحیح، predicate loop و signal درست | تمرکز سیاست ساده‌تر است؛ admission FIFO خودکار نیست |

جدول دامنهٔ الگوریتم را از توان primitive جدا می‌کند. Dekker و Peterson mutual exclusion دوفرایندی‌اند؛ سرویس چندreader/یکwriter به طراحی سطح بالاتر نیاز دارد. Semaphore و monitor می‌توانند آن را بسازند، ولی سیاست سرویس باید روشن باشد.

## ۸. Monitor و سیاست ورود مخزن

`FairReadersWritersMonitor` یک صف درخواست FIFO دارد که state آن با condition محافظت می‌شود. readerهای متوالی که پیش از writer بعدی صف شده‌اند می‌توانند به‌صورت batch وارد شوند؛ readerی که پس از writer صف شود از او عبور نمی‌کند. writer پس از اتمام درخواست‌های پیشین و readerهای فعال وارد می‌شود. این سیاست مانع سبقت بی‌نهایت readerهای تازه از writer صف‌شده می‌شود، در عین حفظ خواندن هم‌زمان در یک batch.

پیاده‌سازی عمداً acquisition بازگشتی و ارتقای read به write را رد می‌کند. ادعای پیشرفت فرض می‌کند critical sectionها متناهی باشند و threadهای منتظر نهایتاً زمان اجرا بگیرند. ترتیب صف تعداد درخواست‌های بعدی که می‌توانند سبقت بگیرند را محدود می‌کند؛ اما deadline دیواری نمی‌دهد، چون زمان‌بندی thread و مدت critical section در این مدل سقف ندارند. کد برای حفاظت state از `Condition` پایتون استفاده می‌کند؛ این گزارش نمی‌گوید primitiveهای زیرین Python FIFO هستند.

چهار تست، هم‌زمانی reader، exclusion reader/writer، جلوگیری از سبقت reader از writer صف‌شده و الگوهای مالکیت پشتیبانی‌نشده را بررسی می‌کنند. این‌ها regression test برای نمونه‌های انتخاب‌شده‌اند، نه model-checking proof. کد آموزشی است و بیرون context manager، خودکار امن‌بودن کد کاربر را تضمین نمی‌کند.

## ۹. انتخاب عملی و خطاهای رایج

Dekker یا Peterson را برای مطالعهٔ مسئلهٔ دو شرکت‌کننده و تحت فرض‌های حافظهٔ روشن به‌کار ببرید، نه به‌عنوان قفل تولیدی آماده. Semaphore وقتی مناسب است که permit یا wait/signal صریح با مسئله جور باشد و سیاست صف معلوم باشد. Monitor زمانی مفید است که state مشترک و invariantهای آن باید با predicateهای condition کپسوله شوند. در readers-writers مشخص کنید reader یا writer اولویت دارد، درخواست‌ها FIFO هستند یا نه، batch خوانندگان چه زمانی بسته می‌شود و پیشرفت به چه فرض‌هایی نیاز دارد.

اشتباه‌های رایج: یکی‌گرفتن mutual exclusion و fairness؛ ادعای کران زمان از starvation freedom؛ معرفی test به‌عنوان proof؛ استفاده از `if` به‌جای ارزیابی دوبارهٔ predicate؛ حذف فرض atomicity/ترتیب حافظه از الگوریتم نرم‌افزاری؛ فرض FIFO بودن همهٔ semaphoreها؛ و معرفی الگوریتم دوفرایندی به‌عنوان قفل عمومی خواننده/نویسنده.

## ۱۰. نتیجه‌گیری

Dekker و Peterson پروتکل‌های آموزشی فشرده برای دو فرایندند. Semaphore primitive عمومی اتمی است و monitor state مشترک و انتظار شرطی را کپسوله می‌کند. هیچ‌کدام از این نام‌ها به‌تنهایی سرویس منصفانهٔ reader/writer را تعیین نمی‌کند. سیاست admission و فرض‌ها تعیین می‌کنند چه کلاسی پیشرفت می‌کند و starvation ممکن است یا نه. Monitor FIFO-by-phase این مخزن نمونه‌ای از یک سیاست است؛ نه proof رسمی و نه قفل بلادرنگ.

## منابع

۱. Courtois, Pierre-Jacques, F. Heymans, and David L. Parnas. “Concurrent control with ‘readers’ and ‘writers’.” *Communications of the ACM* 14(10), 667–668, October 1971. DOI: 10.1145/362759.362813.
۲. Kawash, Jalal. “Process Synchronization with Readers and Writers Revisited.” *Journal of Computing and Information Technology* 13(1), 43–51, 2005. DOI: 10.2498/cit.2005.01.04.
۳. Dijkstra, Edsger W. “Cooperating Sequential Processes.” در *Programming Languages*, ویراستار F. Genuys, Academic Press, 1968. رونویسی آرشیوی: EWD 123.
۴. Hoare, C. A. R. “Monitors: an operating system structuring concept.” *Communications of the ACM* 17(10), 549–557, October 1974. DOI: 10.1145/355620.361161.
۵. Peterson, Gary L. “Myths about the mutual exclusion problem.” *Information Processing Letters* 12(3), 115–116, June 1981. DOI: 10.1016/0020-0190(81)90106-X.
۶. Ridge, Tom. “Operational Reasoning for Concurrent Caml Programs and Weak Memory Models.” در *Theorem Proving in Higher Order Logics (TPHOLs 2007)*، LNCS 4732، صفحات 278–293. DOI: 10.1007/978-3-540-74591-4_21.
۷. Python Software Foundation. “`threading` — Thread-based parallelism.” مستندات کتابخانهٔ استاندارد Python.

نشانی‌های کامل در [فهرست منابع](../../references.md) و حسابرسی منابع در [یادداشت حسابرسی](../../../../docs/research-source-audit.md) آمده‌اند.

</div>
