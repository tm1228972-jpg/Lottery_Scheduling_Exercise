<div dir="rtl" align="right">

# گزارش تمرین ۵ — کلیپ مقایسهٔ Lottery Scheduling، EDF و RM

## مشخصات فایل

کلیپ `outputs/lottery-scheduling-comparison.mp4` با کد مولد مخزن تولید شده است: H.264، اندازهٔ ۱۲۸۰×۷۲۰، نرخ ۱۰ frame/s، ۱۲ بخش دوزبانه و مدت بررسی‌شدهٔ ۱۳۲ ثانیه (۲:۱۲). کلیپ بی‌صداست؛ زیرنویس فارسی و انگلیسی در خود تصویر است و متن گویندگی جداگانه ارائه شده. هیچ ادعای voice-over وجود ندارد.

## محتوای ارائه

کلیپ از مسئلهٔ اصلی شروع می‌کند: سهم نسبی با deadline یکی نیست. سپس تعریف ticket، رابطهٔ `pᵢ=tᵢ/T`، نوسان نمونهٔ محدود، انتخاب EDF بر اساس deadline مطلق و RM بر اساس period را نشان می‌دهد. بخش task set از گزارش remote تمرین ۳ استفاده می‌کند و گانت واقعی تولیدشده از کد را نمایش می‌دهد. بخش پایانی فرض‌های theorem و محدودیت‌ها را یادآوری می‌کند.

## مقایسهٔ علمی

| الگوریتم | قانون انتخاب | ضمانت در فرض‌های مدل |
|---|---|---|
| Lottery | بلیت تصادفی از مجموعهٔ آماده | سهم نظری `tᵢ/T`؛ بدون deadline سخت یا bound انتظار متناهی |
| EDF | زودترین deadline مطلق | `U≤1` برای implicit deadlines و تک‌پردازندهٔ ایده‌آل |
| RM | period کوتاه‌تر، اولویت ثابت | حد Liu–Layland کافی است، نه لازم |

این کلیپ «از همهٔ جنبه‌های واقعی سیستم» benchmark ارائه نمی‌دهد؛ overhead، blocking، jitter، multicore و workload واقعی شبیه‌سازی نشده‌اند. این محدودیت‌ها روی خود کلیپ و در متن گویندگی گفته شده‌اند.

## بازتولید و راستی‌آزمایی

```bash
python -m pip install -e ".[media]"
python tools/generate_figures.py
python tools/build_exercise5_video.py
```

مدت و تعداد frame با `imageio_ffmpeg.count_frames_and_secs` بررسی شد: `1320` frame و `132.0` ثانیه. کد slideها در `tools/build_exercise5_video.py` و گانت ورودی در تمرین ۳ است. منابع در [فهرست منابع](../../references.md) آمده‌اند و متادیتا/ادعاهای اصلی در [یادداشت حسابرسی](../../../../docs/research-source-audit.md) بررسی شده‌اند.

</div>
