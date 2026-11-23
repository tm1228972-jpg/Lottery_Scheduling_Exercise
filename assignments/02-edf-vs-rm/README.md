# تمرین ۲ — مقایسه کامل زمان‌بندی EDF و RM

<div dir="rtl">

**درس:** سیستم‌های عامل · **موضوع:** مقایسه کامل Rate-Monotonic و Earliest-Deadline-First
**نسخه دوزبانه:** فارسی و انگلیسی · **وضعیت:** کامل و بازتولیدپذیر

</div>

## English summary

**Assignment 2 — A complete comparison of Rate-Monotonic (RM) and
Earliest-Deadline-First (EDF) scheduling.** A bilingual (Persian / English)
technical report built on a real tick-level simulator: two theorems are proved,
a worked example is solved by hand, four experiment families are run on real
data, nine comparison axes are tabulated, and the whole simulator plus its test
suite are reproduced in the appendices. Every number is produced by the code in
`code/`.

---

## ۱. این تمرین چه چیزی را تحویل می‌دهد؟

| بخش | مسیر | توضیح |
|---|---|---|
| گزارش فارسی (PDF) | `report/out/02_report_fa.pdf` | ۴۰ صفحه، راست‌به‌چپ، فونت وزیرمتن |
| گزارش انگلیسی (PDF) | `report/out/02_report_en.pdf` | ۴۰ صفحه، چپ‌به‌راست |
| گزارش فارسی (Word) | `report/out/02_report_fa.docx` | با پاراگراف‌های راست‌به‌چپ واقعی |
| گزارش انگلیسی (Word) | `report/out/02_report_en.docx` | با فیلد فهرست مطالب Word |
| اسلاید ارائه | `report/out/slides_fa/slide_*.png` | اسلایدهای ۱۶:۹ بدون فاصله |
| شبیه‌ساز بلادرنگ | `code/rt_sim.py` | ۲۲۰ خط، بدون وابستگی خارجی |
| آزمون‌ها | `code/test_rt_sim.py` | ۱۴ آزمون، همه موفق |
| داده‌های خام | `data/rt_results.json` | خروجی واقعی جاروب ۴۴۰ مجموعه |
| ۲۴ شکل | `figures/*_fa.png`, `figures/*_en.png` | ۱۲ شکل در دو زبان با برچسب‌های بومی |
| گزارش اعتبارسنجی | `report/out/validation.json` | ۱۳ بررسی خودکار معیارهای تمرین |

## ۲. ساختار پوشه‌ها

```
02-edf-vs-rm/
├── README.md                ← همین فایل
├── code/
│   ├── rt_sim.py            ← شبیه‌ساز تیک‌محور + RTA + جاروب
│   └── test_rt_sim.py       ← ۱۴ آزمون واحد
├── data/
│   ├── rt_results.json      ← خروجی JSON (بذر ۷)
│   └── test_output.txt      ← سند اجرای آزمون‌ها
├── figures/
│   ├── generate.py          ← تولید ۱۲ شکل در دو زبان
│   └── fig01..fig12_{fa,en}.png
└── report/
    ├── content.py           ← محتوای دوزبانه (منبع یگانه)
    ├── build.py             ← سازنده همه خروجی‌ها
    └── out/                 ← PDF، Word، اسلاید، validation.json
```

## ۳. چگونگی انجام تمرین (مراحل)

1. **مطالعه نظریه** — قضیه لیو و لیلند (۱۹۷۳) برای کران RM و برهان تبادل برای
   بهینگی EDF.
2. **مدل‌سازی** — تعریف مدل کار دوره‌ای $(T_i, C_i, D_i)$، محاسبه بهره‌وری و
   ابردوره.
3. **پیاده‌سازی** — شبیه‌ساز تیک‌محور با سه سیاست RM، EDF و FCFS و تحلیل دقیق
   زمان پاسخ (RTA) برای اعتبارسنجی خروجی.
4. **آزمون** — ۱۴ آزمون واحد شامل تطبیق RM با RTA روی ۱۲ بذر تصادفی.
5. **آزمایش** — مجموعه نمونه، جاروب بهره‌وری (۴۴۰ مجموعه)، اضافه‌بار و رفتار
   پردازنده.
6. **مقایسه** — نه محور مقایسه، جدول‌های تئوری/عملی و قاعده تصمیم.
7. **نگارش و ساخت** — یک منبع محتوا، دو خروجی زبانی، اسکن خودکار شکاف صفحه.

## ۴. نمودارها و شکل‌ها

| شکل | محتوا | فایل |
|---|---|---|
| ۱ | نمودار گانت برنامه‌ریزی تمرین | `fig01_gantt_{fa,en}.png` |
| ۲ | فلوچارت تصمیم EDF در هر تیک | `fig02_flowchart_{fa,en}.png` |
| ۳–۵ | زمان‌بندی واقعی RM / EDF / FCFS روی مجموعه نمونه | `fig03..fig05_*` |
| ۶ | نرخ از دست رفتن مهلت برحسب بهره‌وری | `fig06_sweep_{fa,en}.png` |
| ۷ | بهره‌وری پردازنده در ابردوره | `fig07_utilisation_{fa,en}.png` |
| ۸ | بیشترین زمان پاسخ هر کار | `fig08_response_{fa,en}.png` |
| ۹ | توزیع شکست در اضافه‌بار | `fig09_overload_{fa,en}.png` |
| ۱۰ | کران RM برحسب تعداد کار | `fig10_bound_{fa,en}.png` |
| ۱۱ | معماری شبیه‌ساز | `fig11_architecture_{fa,en}.png` |
| ۱۲ | نقشه حرارتی شکست هشت مجموعه | `fig12_miss_heat_{fa,en}.png` |

## ۵. بازتولید کامل

```bash
cd assignments/02-edf-vs-rm/code
python3 test_rt_sim.py            # ۱۴ آزمون، باید OK بدهد
python3 rt_sim.py --seed 7        # بازتولید data/rt_results.json (~۲ دقیقه)

cd ../
python3 figures/generate.py       # تولید ۲۴ شکل (~۸ ثانیه)
python3 report/build.py           # ساخت PDF/DOCX/اسلاید + اعتبارسنجی
```

`solve` برای بازسازی فقط یکی از خروجی‌ها:

```bash
python3 report/build.py --skip-slides        # بدون اسلاید
python3 report/build.py --only pdf           # فقط PDF
```

## ۶. اعداد کلیدی (بذر ۷)

| سنجه | مقدار |
|---|---|
| بهره‌وری مجموعه نمونه | ۰٫۸۵۸ (بالاتر از کران RM = ۰٫۷۵۷) |
| ابردوره | ۱۲۰ تیک |
| شکست مهلت: RM / EDF / FCFS | ۰ / ۰ / ۱ |
| بیشترین زمان پاسخ T4: RM / EDF | ۲۸ / ۲۸ تیک |
| جاروب در U = ۱٫۰ | ۱۴۴۹ شکست RM، ۳۸۵ شکست EDF |
| اضافه‌بار (U = ۱٫۳۸۳) | ۳ شکست RM، ۵ شکست EDF |
| زمان اجرای جاروب کامل | حدود ۱۲۶ ثانیه |

## ۷. چک‌لیست معیارهای تمرین

- [x] گزارش PDF فارسی بیش از ۴۰ صفحه — **۴۰ صفحه**
- [x] گزارش PDF انگلیسی بیش از ۴۰ صفحه — **۴۰ صفحه**
- [x] خروجی Word در هر دو زبان — با RTL واقعی در نسخه فارسی
- [x] فهرست مطالب، شکل‌ها و جدول‌های شماره‌دار — ۳۲ ارجاع شکل، ۴۳ جدول
- [x] نمودار گانت — شکل ۱
- [x] اسلاید ارائه — ۳۷ اسلاید بدون فاصله
- [x] کد واقعی و اجراشده — ۲۲۰ خط شبیه‌ساز، ۱۴ آزمون موفق
- [x] متن تمیز و راست‌به‌چپ — بدون آینه‌شدگی، نقطه‌گذاری اصلاح‌شده

## ۸. اعتبارسنجی خودکار

`report/out/validation.json` نتیجه ۱۳ بررسی را نگه می‌دارد. برای بررسی
شکاف صفحه‌ها:

```bash
python3 tools/gapscan.py report/out/02_report_fa.pdf report/out/02_report_en.pdf
```

## ۹. صداقت و محدودیت‌ها

- شبیه‌ساز **تیک‌محور** است و هزینه‌های ریزمعماری (حافظه نهان، انشعاب) را مدل
  نمی‌کند.
- سربار جابه‌جایی زمینه صفر فرض شده است.
- تولید مجموعه‌ها با بذر ثابت انجام می‌شود؛ اعداد بازتولیدپذیرند اما بازه
  اطمینان آماری گزارش نشده‌اند.
- اعداد جدول تطبیق پایتون/C در تمرین ۱ از فایل‌های واقعی خوانده شده‌اند؛ در این
  تمرین تنها یک پیاده‌سازی وجود دارد و اعتبارسنجی از طریق RTA انجام می‌شود.
- صفحه‌آرایی: شکاف انتهای فصل‌ها حداکثر حدود ۳۰٪ است؛ شکاف‌های بزرگ‌تر با
  `gapscan.py` قابل شناسایی و رفع‌اند.
