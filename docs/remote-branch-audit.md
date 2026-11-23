# ممیزی شاخه‌های تمرین موجود روی GitHub

تاریخ بررسی: **2026-11-23**
مخزن: `tm1228972-jpg/Lottery_Scheduling_Exercise`
شاخه‌های زیر با `git ls-remote` شناسایی و برای خواندن در `origin/<branch>` fetch شدند. محتوای شاخه‌ها فقط خوانده شد؛ هیچ‌یک checkout یا ویرایش نشدند.

## یافتهٔ مشترک

هر شش شاخهٔ نام‌برده‌شده در README اصلی واقعاً روی remote وجود دارند و در زمان بررسی هرکدام سه فایل ریشه‌ای Markdown داشتند: `README.md`، `report.md` و `references.md`. در tree این شاخه‌ها پوشهٔ `docs/`، فایل منبع مستقل، آزمون، تصویر/نمودار، خروجی آزمایش، Word یا PDF پیدا نشد. برخی از `report.md`ها فرمول، جدول یا snippet کد درون Markdown دارند؛ این با فایل اجرای مستقل یا مجموعهٔ آزمون برابر نیست.

README هر شاخه عبارت «bilingual study report» را به‌کار می‌برد، اما گزارش‌های خوانده‌شده عمدتاً انگلیسی و همراه یک خلاصهٔ کوتاه انگلیسی‌اند؛ متن فارسی وجود ندارد. فهرست پنج‌منبعی در تمام شاخه‌ها تکرار شده و شامل منابعی از موضوع‌های دیگر نیز هست. ارتباط و جزئیات ارجاع‌ها باید پیش از استفادهٔ دانشگاهی جداگانه بازبینی شود.

## یافته به تفکیک شاخه

| شاخه / commit کوتاه | محتوای واقعی | نقص قابل اثبات از فایل‌ها |
|---|---|---|
| [`assignment-01-lottery-introduction`](https://github.com/tm1228972-jpg/Lottery_Scheduling_Exercise/tree/assignment-01-lottery-introduction) · `1b752aa` | تعریف Lottery Scheduling، نسبت نظری `tᵢ/T`، مراحل انتخاب، مثال بلیت‌های `10,20,30`، چند مزیت و محدودیت | فاقد Python source، آزمون، داده/نمودار، متن فارسی و `docs/`; مثال فقط تحلیل نظری است و خروجی آزمایش ذخیره نشده. |
| [`assignment-02-edf-rm-comparison`](https://github.com/tm1228972-jpg/Lottery_Scheduling_Exercise/tree/assignment-02-edf-rm-comparison) · `cdcd2d2` | توضیح EDF و RM، utilization، شرط EDF در مدل تک‌پردازندهٔ preemptive و bound کافی Liu–Layland برای RM | فاقد مقایسهٔ جدول‌دار با Lottery، task set، شبیه‌سازی/نمودار، کد و فارسی. متن درست قید می‌کند که عبور از bound کافی، ناممکن‌بودن زمان‌بندی را ثابت نمی‌کند. |
| [`assignment-03-edf-rm-three-processes`](https://github.com/tm1228972-jpg/Lottery_Scheduling_Exercise/tree/assignment-03-edf-rm-three-processes) · `702c94d` | task set مشخص: `(C,T=D)=(1,4),(1,5),(2,10)`، فرض release هم‌زمان و تک‌پردازندهٔ preemptive، utilization `0.65`، hyperperiod `20` و bound کافی RM برای سه task | محاسبهٔ جمع utilization و مقایسه با bound سازگار است، اما گزارش خودش Gantt کامل تا `t=20` را کار نهایی می‌داند؛ Gantt/تحلیل releaseها، کد، آزمون و نمودار تحویل‌شده در tree نیستند. |
| [`assignment-04-readers-writers-synchronization`](https://github.com/tm1228972-jpg/Lottery_Scheduling_Exercise/tree/assignment-04-readers-writers-synchronization) · `635f59a` | خلاصهٔ Readers–Writers و جدول Dekker/Peterson/Semaphore/Monitor؛ به starvation نویسنده در readers-preference اشاره می‌کند | فاقد شبه‌کد یا اجرای reader/writer، آزمون هم‌زمانی، نمودار، فارسی و تفکیک/تحلیل سناریوهای fairness. |
| [`assignment-05-lottery-implementation`](https://github.com/tm1228972-jpg/Lottery_Scheduling_Exercise/tree/assignment-05-lottery-implementation) · `1a66735` | در `report.md` snippet پایتون `lottery_winner` و یک حلقهٔ ۶۰٬۰۰۰ انتخاب seeded آمده؛ خود متن محدودیت‌های شبیه‌ساز را بیان می‌کند | کد در فایل `.py` مستقل نیست، خروجی counts ضمیمه نشده، تست‌ها و نمودار/CSV ندارند. اعتبارسنجی نام و نوع ticket، تست‌های مرزی و مستندسازی اجرای بازتولیدپذیر کامل نیست. |
| [`assignment-06-lottery-seminar`](https://github.com/tm1228972-jpg/Lottery_Scheduling_Exercise/tree/assignment-06-lottery-seminar) · `21243a7` | خلاصهٔ Lottery Scheduling و چهار پرسش برای seminar | فایل اسلاید، ویدئو/کلیپ، متن ارائه، ساختار زمانی seminar یا نمودار در tree نیست. |

## تفسیر و مرز ممیزی

- «فاقد» یعنی در tree همین commitهای remote دیده نشد؛ این نتیجه دربارهٔ فایل‌های خارج Git یا نسخهٔ جدیدتر پس از زمان بررسی ادعایی ندارد.
- گزارشی دربارهٔ اجرای کدهای مستقل ارائه نشده، چون چنین فایل‌هایی در شاخه‌ها نبودند. Snippet موجود در شاخهٔ 5 به‌عنوان متن خوانده شد، نه به‌عنوان مجموعهٔ تست‌شده.
- نام شاخهٔ هفتم در README و remote branchهای خوانده‌شده دیده نشد. درخواست کاربر آن را مشخص نمی‌کند؛ بنابراین موضوعش حدس زده نشده.
- کار فعلی در شاخهٔ فعال `arena/4447560a-lottery-scheduling-exercise` می‌ماند. این یادداشت audit است و تغییرات را به شاخه‌های assignment اعمال نمی‌کند.
