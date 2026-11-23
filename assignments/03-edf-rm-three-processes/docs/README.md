<div dir="rtl" align="right">

# راهنمای فنی تمرین ۳ — EDF و RM با سه task

## دادهٔ مسئله

task set از گزارش موجود در شاخهٔ remote همین تمرین گرفته شده است:

| Task | `Cᵢ` | `Tᵢ` | `Dᵢ` |
|---|---:|---:|---:|
| P1 | 1 | 4 | 4 |
| P2 | 1 | 5 | 5 |
| P3 | 2 | 10 | 10 |

فرض‌های گزارش اولیه: پردازه‌های مستقل، release هم‌زمان در `t=0`، پردازندهٔ تک‌هسته‌ای و preemptive، هزینهٔ تعویض صفر، deadline برابر period. در این فایل زمان گسسته و زمان اجرای صحیح فرض شده است.

## تحلیل قابلیت زمان‌بندی

مجموع استفاده از CPU:

`U = Σ Cᵢ/Tᵢ = 1/4 + 1/5 + 2/10 = 0.65`.

Hyperperiod:

`H = lcm(4,5,10)=20`.

برای RM با سه task، حد کافی Liu–Layland برابر `U_LL = 3(2^(1/3)-1) ≈ 0.779763`. چون `0.65 < 0.779763` آزمون کافی RM قابل استفاده است. این حد کافی است، نه شرط لازم؛ ردشدن از حد به‌تنهایی unschedulable بودن را ثابت نمی‌کند. برای EDF با deadlineهای implicit در مدل استاندارد تک‌پردازنده‌ای، `U≤1` شرط لازم و کافی است؛ این task set آن را دارد.

ترتیب اولویت RM ثابت است: `P1 > P2 > P3`، چون دورهٔ کوتاه‌تر اولویت بالاتر دارد. EDF در هر لحظه job آماده با کمترین absolute deadline را انتخاب می‌کند. پیاده‌سازی در صورت تساوی deadline، release زودتر و سپس ترتیب task ورودی را به‌عنوان tie-break انتخاب می‌کند.

## نتیجهٔ شبیه‌سازی روی `[0,20)`

هر دو سیاست ۱۶ بازهٔ ادغام‌شدهٔ اجرا/idle برگرداندند و در هیچ deadline miss دیده نشد. مجموع زمان‌های busy برابر `5+4+4=13` واحد از 20، یعنی 65٪ است؛ 7 واحد idle. هر job باید قبل یا در absolute deadline خود تکمیل شود. دادهٔ بازتولیدپذیر در `../outputs/edf-rm-schedule.csv` و خلاصهٔ utilization/bound در `../outputs/analysis-summary.csv` است.

### Trace فشرده

| بازه | Job | Deadline مطلق |
|---|---|---:|
| 0–1 | P1/J1 | 4 |
| 1–2 | P2/J1 | 5 |
| 2–4 | P3/J1 | 10 |
| 4–5 | P1/J2 | 8 |
| 5–6 | P2/J2 | 10 |
| 6–8 | idle | — |
| 8–9 | P1/J3 | 12 |
| 9–10 | idle | — |
| 10–11 | P2/J3 | 15 |
| 11–12 | P3/J2 | 20 |
| 12–13 | P1/J4 | 16 |
| 13–14 | P3/J2 | 20 |
| 14–15 | idle | — |
| 15–16 | P2/J4 | 20 |
| 16–17 | P1/J5 | 20 |
| 17–20 | idle | — |

EDF و RM در این ورودی یک trace واحد تولید می‌کنند. علت این برابری عمومی نیست؛ فقط زمان‌های release/deadline و اولویت‌های همین ورودی باعث آن شده است.

## راهنمای نمودار

`figures/edf-rm-gantt.png` دو lane برای EDF و RM و محور integer-time از 0 تا 20 دارد. P1/P2/P3 رنگ‌های متفاوت دارند و idle خاکستری است. هر قطعه نمایندهٔ job و بازهٔ نیمه‌باز `[start,end)` است. نمودار از همان `ScheduleResult` کد و فایل CSV تولید می‌شود، نه از دادهٔ دستی جداگانه.

## اجزای برنامه و بازتولید

- `PeriodicTask`: نام، execution، period و deadline نسبی را اعتبارسنجی می‌کند.
- `simulate_schedule`: releaseها را در مضارب period تولید، و در هر tick یک job باقیمانده را طبق EDF یا RM اجرا می‌کند؛ preemption در مرز tickها ممکن است.
- `ScheduleResult`/`ScheduleSegment`: trace و deadline missها را برمی‌گردانند.
- `hyperperiod`, `utilization`, `rm_utilization_bound`: محاسبات تحلیلی‌اند.

```bash
python -m pip install -e .
python tools/generate_figures.py
python -m unittest discover -s tests -v
```

آزمون‌ها در `tests/test_realtime.py` مقادیر مسئله، trace کامل، پوشش hyperperiod و یک ورودی overload برای تشخیص miss را بررسی می‌کنند. شبیه‌ساز، zero-overhead و integer tick را فرض می‌کند؛ برای real-time واقعی، blocking، jitter، هزینهٔ preemption، منابع مشترک و زمان اجرای غیرصحیح باید مدل شوند.

</div>
