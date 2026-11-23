<div dir="rtl" align="right">

# تمرین ۵ — کلیپ Lottery Scheduling و مقایسه با EDF/RM

## فایل کلیپ

[دریافت MP4](outputs/lottery-scheduling-comparison.mp4) — ویدئوی آموزشی بی‌صدا با زیرنویس‌های روی تصویر به دو زبان، ۱۲ بخش، ۱۲۸۰×۷۲۰، H.264، مدت تأییدشدهٔ **۱۳۲ ثانیه (۲ دقیقه و ۱۲ ثانیه)**. بین بخش‌ها تصویر سیاه/صفحهٔ خالی اضافه نشده است. کلیپ در بخش گانت از خروجی واقعی EDF/RM تمرین ۳ استفاده می‌کند.

**محدودیت صریح:** فایل صوتی/راوی روی کلیپ قرار نگرفته است. متن گویندگی فارسی و انگلیسی همراه آن آمده تا ارائه‌دهنده بتواند روی کلیپ بخواند یا بعداً صدای تأییدشده اضافه کند.

## محتوای ۱۲ بخش

1. هدف مقایسه و تفاوت قرارداد زمان‌بندی
2. سهم نسبی در برابر مهلت کار
3. رابطهٔ ticket و احتمال Lottery
4. یک draw و نگاشت بازهٔ تجمعی
5. نوسان نمونه و نبود bound برای Lottery
6. EDF و اولویت deadline مطلق
7. RM و اولویت ثابت بر اساس دوره
8. task set واقعی موجود در شاخهٔ تمرین ۳
9. گانت EDF/RM تولیدشده از simulator
10. مقایسهٔ تضمین‌های سه روش
11. اهمیت فرض‌ها و سربارها
12. جمع‌بندی و دستور بازتولید

## ساخت مجدد

```bash
python -m pip install -e ".[media]"
python tools/generate_figures.py
python tools/build_exercise5_video.py
```

اسکریپت `tools/build_exercise5_video.py` از Pillow، imageio-ffmpeg و شکل‌دهی bidi برای نوشتهٔ فارسی استفاده می‌کند. متن گویندگی: [`docs/narration-fa.md`](docs/narration-fa.md) و [`docs/narration-en.md`](docs/narration-en.md).

</div>
