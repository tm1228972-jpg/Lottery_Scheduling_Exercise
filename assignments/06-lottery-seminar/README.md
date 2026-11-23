<div dir="rtl" align="right">

# تمرین ۶ — مقاله و سمینار Lottery Scheduling

## محتوای آماده‌شده

- مقالهٔ فنی فارسی: [`docs/article-fa.md`](docs/article-fa.md)
- مقالهٔ فنی انگلیسی: [`docs/article-en.md`](docs/article-en.md)
- خروجی آزمایشی Word/PDF مقاله: `docs/reports/article-{fa,en}.{docx,pdf}` (پیش‌نویس کوتاه، نه نسخهٔ نهایی)
- برنامهٔ زمان‌بندی سمینار: [`docs/seminar-agenda.md`](docs/seminar-agenda.md)
- یادداشت گوینده برای هر اسلاید: [`docs/seminar-speaker-notes.md`](docs/seminar-speaker-notes.md)
- اسلاید دوزبانهٔ قابل ویرایش: [`slides/lottery-scheduling-seminar.pptx`](slides/lottery-scheduling-seminar.pptx)

مقاله از تعریف الگوریتم، نسبت احتمال، انتظار/واریانس در مدل ثابت، سازوکار ticket transfer/inflation/currency، مقایسهٔ EDF/RM، خروجی ۵۰٬۰۰۰ draw واقعی این مخزن، فرض‌ها، محدودیت‌ها و پرسش‌های سمینار استفاده می‌کند. خروجی آزمایش دقیق در `assignments/01-lottery-introduction/outputs/lottery-frequency.csv` است.

## ارائهٔ سمینار

Deck شامل ۱۰ اسلاید دوزبانه است. برنامهٔ نمونهٔ ۱۵ دقیقه‌ای در agenda قرار دارد؛ زمان و قالب باید با آیین‌نامهٔ واقعی درس تطبیق داده شود، چون تصویر ارسالی فقط عنوان «مقاله و سمینار» را نشان می‌دهد و شیوه‌نامهٔ کامل ارائه را ندارد.

برای بازسازی deck:

```bash
python -m pip install -e ".[seminar]"
python tools/build_seminar_deck.py
```

</div>
