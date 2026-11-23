<div dir="rtl" align="right">

# راهنمای تمرین ۲ — تحلیل Lottery، EDF و RM

## دامنهٔ مقایسه

این مقایسه ابتدا هدف هر الگوریتم را جدا می‌کند. Lottery یک الگوریتم proportional-share است؛ EDF و RM در مدل کلاسیک برای زمان‌بندی taskهای دوره‌ای با deadline بررسی می‌شوند. این‌ها صرفاً سه «روش انتخاب پردازه» با تضمین‌های قابل‌جایگزینی نیستند. مقایسه فقط با ذکر workload، مدل پردازنده، preemption، deadline و سربار معنا دارد.

## فرمول‌ها و شروط

برای Lottery با `tᵢ` بلیت از مجموع `T`:

`P(i wins one draw) = tᵢ/T`.

در `k` draw مستقل با chance ثابت `p`, احتمال عدم انتخاب `(1-p)^k`; برای `k` محدود این مقدار مثبت است. در نتیجه بلیت مثبت، تضمین bounded waiting نیست.

برای taskهای مستقل، پیش‌دستانه، تک‌پردازنده‌ای و با deadline برابر period:

`U = Σ Cᵢ/Tᵢ`.

EDF در مدل implicit-deadline با `U≤1` schedulable است. RM bound کافی Liu–Layland برای `n` task برابر `n(2^(1/n)-1)` است. در RM، عبور از bound فقط تضمین ساده را از بین می‌برد؛ آزمون response-time دقیق‌تری مانند `Rᵢ=Cᵢ+Σ_{j∈hp(i)}ceil(Rᵢ/Tⱼ)Cⱼ` لازم می‌شود. این رابطه نیز به مدل و priority set وابسته است.

## مقایسهٔ عملی و overload

Lottery سهم CPU را به وزن ticket گره می‌زند، نه به absolute deadline. EDF deadline را در هر لحظه دوباره رتبه‌بندی می‌کند؛ workload بیش از ظرفیت می‌تواند deadline miss ایجاد کند. RM ثابت است؛ کارهای با اولویت بالاتر می‌توانند سرویس بیشتری بگیرند و response کارهای پایین‌تر افزایش یابد. «missed deadline»، «low average share» و «starvation» معیارهای یکسانی نیستند.

در task set ثبت‌شدهٔ تمرین ۳، `U=0.65`، `n=3` و bound کافی RM حدود `0.780` است؛ هر دو simulator deadline miss صفر دادند. این مورد فقط یک سناریوی task-set است. در branchهای موجود، وزن ticket برای این taskها مشخص نیست؛ بنابراین ادعای عددی برای Lottery ساخته نشده است.

## پیاده‌سازی و نمودارها

دو شکل در `figures/` مفاهیم را مقایسه می‌کنند، نه benchmark را: `policy-goals.svg` هدف انتخاب و `guarantee-boundaries.svg` مرز تضمین‌ها را نشان می‌دهد. نمودار واقعی EDF/RM برای task set موجود در `../../03-edf-rm-three-processes/docs/figures/` است.

نمونه‌کد Lottery در `src/lottery_lab/lottery.py` و مدل EDF/RM در `src/lottery_lab/realtime.py` است. آزمون‌های زمان‌بندی، task set و deadline miss را پوشش می‌دهند. محدودیت‌ها: integer tick، zero overhead و مدل تک‌پردازنده‌ای؛ no blocking/jitter.

## بازتولید و منابع

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python tools/generate_figures.py
```

فهرست منابع در [`../references.md`](../references.md) به مقالهٔ Lottery Scheduling، مقالهٔ Liu–Layland و تحلیل response-time ارجاع می‌دهد. متادیتا و ادعاهای اصلی در [`../../../docs/research-source-audit.md`](../../../docs/research-source-audit.md) در ۲۳ نوامبر ۲۰۲۶ بررسی شده‌اند.

</div>
