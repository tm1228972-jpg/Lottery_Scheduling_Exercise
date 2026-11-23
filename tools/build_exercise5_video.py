"""Build a silent bilingual 2m12s explainer clip for Exercise 5.

Requires the optional `media` dependencies from pyproject.toml. Persian captions
are reshaped and bidi-ordered before rasterization; the video uses a continuous
frame stream (no blank/black inter-slide gaps) and includes the generated EDF/RM
Gantt chart. A separate narration script is provided for a human presenter.
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402
import arabic_reshaper  # noqa: E402
from bidi.algorithm import get_display  # noqa: E402
import imageio_ffmpeg  # noqa: E402

WIDTH, HEIGHT = 1280, 720
FPS = 10
SLIDE_SECONDS = 11
SLIDE_COUNT = 12
DURATION = SLIDE_SECONDS * SLIDE_COUNT  # 132 s = 2m12s
FRAME_COUNT = FPS * DURATION
NAVY = "#14243A"
INK = "#25364B"
TEAL = "#168C8C"
BLUE = "#4776A8"
GOLD = "#F2B84B"
CORAL = "#DF6B63"
MUTED = "#64748B"
PALE = "#F4F7FA"
WHITE = "#FFFFFF"
FONT_REGULAR = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FONT_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

SLIDES = [
    {
        "en": "Lottery Scheduling, EDF and RM",
        "fa": "زمان‌بندی لاتاری، EDF و RM",
        "subtitle_en": "A compact comparison of proportional share and real-time deadlines",
        "subtitle_fa": "مقایسهٔ سهم نسبی پردازنده با مهلت‌های بلادرنگ",
        "points": [
            ("Three policies solve different scheduling goals.", "سه سیاست، هدف‌های متفاوت زمان‌بندی را دنبال می‌کنند."),
            ("Lottery distributes expected CPU share.", "لاتاری سهم مورد انتظار CPU را توزیع می‌کند."),
            ("EDF and RM prioritize deadline-constrained jobs.", "EDF و RM کارهای دارای مهلت را اولویت‌بندی می‌کنند."),
        ],
    },
    {
        "en": "Start with the objective",
        "fa": "ابتدا هدف زمان‌بندی را مشخص کنیم",
        "subtitle_en": "Share, deadline satisfaction, and fairness are not interchangeable",
        "subtitle_fa": "سهم، رعایت مهلت و انصاف مفاهیم یکسانی نیستند",
        "points": [
            ("Proportional share asks: how much CPU does each process receive over time?", "سهم نسبی می‌پرسد: هر پردازه در طول زمان چه مقدار CPU می‌گیرد؟"),
            ("Real-time scheduling asks: does each job finish by its deadline?", "زمان‌بندی بلادرنگ می‌پرسد: هر کار پیش از مهلتش تمام می‌شود؟"),
            ("A high average share does not prove a deadline guarantee.", "سهم میانگین زیاد، تضمین رعایت مهلت را ثابت نمی‌کند."),
        ],
    },
    {
        "en": "Lottery: tickets encode weight",
        "fa": "لاتاری: بلیت‌ها وزن نسبی را نشان می‌دهند",
        "subtitle_en": "If process i has tᵢ tickets out of T, P(i) = tᵢ / T per draw",
        "subtitle_fa": "اگر پردازه i از مجموع T، تعداد tᵢ بلیت داشته باشد، احتمال هر قرعه tᵢ/T است",
        "points": [
            ("Example: weights 1, 2, 4 give expected shares 1/7, 2/7, 4/7.", "نمونه: وزن‌های ۱، ۲ و ۴ سهم نظری ۱/۷، ۲/۷ و ۴/۷ می‌دهند."),
            ("A uniform ticket draw selects one ready process.", "قرعهٔ یکنواخت یک پردازهٔ آماده را انتخاب می‌کند."),
            ("A finite sample need not match the expected ratio exactly.", "نمونهٔ محدود الزاماً دقیقاً با نسبت نظری برابر نیست."),
        ],
    },
    {
        "en": "One lottery dispatch",
        "fa": "یک نوبت انتخاب در لاتاری",
        "subtitle_en": "Ready set → ticket intervals → random ticket → winner",
        "subtitle_fa": "مجموعهٔ آماده ← بازه‌های بلیت ← قرعهٔ تصادفی ← برنده",
        "points": [
            ("Sum positive ticket counts to get T.", "تعداد بلیت‌های مثبت را جمع می‌کنیم تا T به دست آید."),
            ("Draw an integer uniformly from 1 through T.", "یک عدد صحیح یکنواخت از ۱ تا T انتخاب می‌کنیم."),
            ("Map the number to its cumulative ticket interval.", "عدد را به بازهٔ تجمعی پردازهٔ مالک نگاشت می‌کنیم."),
        ],
    },
    {
        "en": "Lottery is probabilistic, not a deadline test",
        "fa": "لاتاری احتمالاتی است، نه آزمون رعایت مهلت",
        "subtitle_en": "Positive tickets imply a nonzero chance, not a finite worst-case wait",
        "subtitle_fa": "بلیت مثبت یعنی احتمال غیرصفر، نه کران قطعی انتظار",
        "points": [
            ("With a fixed chance p, no win in k independent draws has probability (1−p)^k.", "با احتمال ثابت p، احتمال نبردن در k قرعهٔ مستقل (۱−p)^k است."),
            ("That probability decreases but is nonzero at every finite k.", "این احتمال کاهش می‌یابد، اما برای هر k متناهی غیرصفر است."),
            ("Lottery alone cannot guarantee a hard deadline.", "لاتاری به‌تنهایی مهلت سخت را تضمین نمی‌کند."),
        ],
    },
    {
        "en": "EDF: earliest absolute deadline first",
        "fa": "EDF: ابتدا نزدیک‌ترین مهلت مطلق",
        "subtitle_en": "Dynamic priority is based on each ready job’s absolute deadline",
        "subtitle_fa": "اولویت پویا بر پایهٔ مهلت مطلق هر کار آماده تعیین می‌شود",
        "points": [
            ("The ready job with the smallest absolute deadline runs next.", "کار آماده با کوچک‌ترین مهلت مطلق در نوبت بعد اجرا می‌شود."),
            ("Under ideal uniprocessor assumptions and Dᵢ=Tᵢ, U≤1 is the EDF test.", "با فرض تک‌پردازندهٔ ایده‌آل و Dᵢ=Tᵢ، شرط EDF برابر U≤1 است."),
            ("Blocking and overhead can invalidate the ideal-model conclusion.", "blocking و سربار می‌توانند نتیجهٔ مدل ایده‌آل را تغییر دهند."),
        ],
    },
    {
        "en": "RM: fixed priority by period",
        "fa": "RM: اولویت ثابت بر اساس دوره",
        "subtitle_en": "Shorter-period tasks receive higher fixed priority",
        "subtitle_fa": "کارهای با دورهٔ کوتاه‌تر، اولویت ثابت بالاتری دارند",
        "points": [
            ("The Liu–Layland utilization bound is sufficient, not necessary.", "حد استفادهٔ Liu–Layland کافی است، نه لازم."),
            ("For n tasks: U ≤ n(2^(1/n)−1) guarantees schedulability under assumptions.", "برای n کار، این حد با فرض‌های مدل، زمان‌پذیری را تضمین می‌کند."),
            ("Exceeding the bound alone does not prove failure.", "عبور از حد به‌تنهایی شکست زمان‌بندی را ثابت نمی‌کند."),
        ],
    },
    {
        "en": "Use the supplied task set",
        "fa": "از task set موجود در گزارش استفاده می‌کنیم",
        "subtitle_en": "P1=(C=1,T=D=4), P2=(1,5), P3=(2,10)",
        "subtitle_fa": "P1=(C=۱,T=D=۴)، P2=(۱،۵)، P3=(۲،۱۰)",
        "points": [
            ("Utilization U = 1/4 + 1/5 + 2/10 = 0.65.", "استفادهٔ پردازنده U برابر ۰٫۶۵ است."),
            ("Hyperperiod H = lcm(4,5,10) = 20.", "ابر‌دوره H برابر ۲۰ است."),
            ("RM’s n=3 sufficient bound is about 0.780.", "حد کافی RM برای n=۳ تقریباً ۰٫۷۸۰ است."),
        ],
    },
    {
        "en": "EDF and RM trace through t = 20",
        "fa": "ردیابی EDF و RM تا t=۲۰",
        "subtitle_en": "The repository simulator generated this Gantt chart from the supplied tasks",
        "subtitle_fa": "نمودار گانت از شبیه‌ساز مخزن و همان taskها تولید شده است",
        "points": [
            ("Both policies meet all deadlines in this one hyperperiod.", "هر دو سیاست در این ابر‌دوره همهٔ مهلت‌ها را رعایت می‌کنند."),
            ("The traces match here only; one example does not prove equivalence.", "traceها فقط در این مثال یکسان‌اند؛ برابری کلی ثابت نمی‌شود."),
        ],
        "chart": True,
    },
    {
        "en": "Compare the guarantees, not just the names",
        "fa": "تضمین‌ها را مقایسه کنیم، نه فقط نام‌ها را",
        "subtitle_en": "Choose according to the scheduling contract",
        "subtitle_fa": "انتخاب الگوریتم باید بر اساس قرارداد زمان‌بندی باشد",
        "points": [
            ("Lottery: weighted share in expectation; no hard deadline guarantee.", "لاتاری: سهم وزن‌دار در انتظار؛ بدون تضمین مهلت سخت."),
            ("EDF: dynamic deadline priority; ideal implicit-deadline test U≤1.", "EDF: اولویت پویای مهلت؛ آزمون ایده‌آل U≤۱ برای D=T."),
            ("RM: fixed period priority; a simple sufficient utilization bound.", "RM: اولویت ثابت دوره؛ حد کافی سادهٔ استفاده از CPU."),
        ],
    },
    {
        "en": "Assumptions define the theorem",
        "fa": "فرض‌ها محدودهٔ اعتبار قضیه را تعیین می‌کنند",
        "subtitle_en": "Ideal schedulability results do not include every system cost",
        "subtitle_fa": "نتیجهٔ ایده‌آل همهٔ هزینه‌های یک سیستم واقعی را پوشش نمی‌دهد",
        "points": [
            ("The comparison assumes one preemptive processor and zero overhead.", "مقایسه، یک پردازندهٔ پیش‌دستانه و سربار صفر را فرض می‌کند."),
            ("Shared-resource blocking and release jitter need extra analysis.", "blocking منابع مشترک و jitter آزادسازی به تحلیل جدا نیاز دارند."),
            ("Use the workload model before claiming a guarantee.", "پیش از ادعای تضمین، مدل workload را مشخص کنید."),
        ],
    },
    {
        "en": "Reproduce and cite",
        "fa": "بازتولید و ارجاع به منابع",
        "subtitle_en": "Repository outputs and checked primary sources",
        "subtitle_fa": "خروجی‌های مخزن و منابع اولیهٔ بررسی‌شده",
        "points": [
            ("Waldspurger & Weihl, OSDI 1994; Liu & Layland, JACM 1973.", "Waldspurger و Weihl، ۱۹۹۴؛ Liu و Layland، JACM، ۱۹۷۳."),
            ("Run: python tools/generate_figures.py", "اجرا: python tools/generate_figures.py"),
            ("Tests: python -m unittest discover -s tests -v. See references.md.", "آزمون: python -m unittest discover -s tests -v؛ منابع: references.md."),
        ],
    },
]


def shape_persian(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))


def load_fonts():
    regular_path = FONT_REGULAR if FONT_REGULAR.exists() else None
    bold_path = FONT_BOLD if FONT_BOLD.exists() else regular_path
    if regular_path is None:
        return (ImageFont.load_default(),) * 4
    return (
        ImageFont.truetype(str(regular_path), 20),
        ImageFont.truetype(str(bold_path), 30),
        ImageFont.truetype(str(regular_path), 16),
        ImageFont.truetype(str(bold_path), 22),
    )


def wrap_words(text: str, font: ImageFont.FreeTypeFont, max_width: int, rtl: bool = False) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        measured = shape_persian(candidate) if rtl else candidate
        if current and font.getlength(measured) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_slide(index: int, slide: dict, fonts, gantt: Image.Image | None) -> Image.Image:
    body_font, title_font, small_font, bullet_font = fonts
    image = Image.new("RGB", (WIDTH, HEIGHT), PALE)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 13), fill=TEAL)
    draw.text((65, 42), slide["en"], font=title_font, fill=NAVY)
    draw.text((1215, 88), shape_persian(slide["fa"]), font=title_font, fill=NAVY, anchor="rt")
    draw.text((65, 137), slide["subtitle_en"], font=small_font, fill=MUTED)
    draw.text((1215, 165), shape_persian(slide["subtitle_fa"]), font=small_font, fill=MUTED, anchor="rt")

    if slide.get("chart") and gantt is not None:
        chart = gantt.copy().convert("RGB")
        chart.thumbnail((1120, 280), Image.Resampling.LANCZOS)
        chart_x = (WIDTH - chart.width) // 2
        chart_y = 205
        image.paste(chart, (chart_x, chart_y))
        draw = ImageDraw.Draw(image)
        bullets_y = 505
    else:
        bullets_y = 235

    for row, (en, fa) in enumerate(slide["points"]):
        y = bullets_y + row * 90
        draw.rounded_rectangle((60, y, WIDTH - 60, y + 70), radius=14, fill=WHITE, outline="#DCE4EC", width=2)
        draw.ellipse((82, y + 24, 101, y + 43), fill=(GOLD if row == 1 else TEAL))
        en_lines = wrap_words(en, bullet_font, 470)
        fa_lines = wrap_words(fa, bullet_font, 525, rtl=True)
        for line_i, line in enumerate(en_lines[:2]):
            draw.text((122, y + 14 + line_i * 25), line, font=bullet_font, fill=INK)
        for line_i, line in enumerate(fa_lines[:2]):
            draw.text((WIDTH - 82, y + 14 + line_i * 25), shape_persian(line), font=bullet_font, fill=INK, anchor="rt")

    draw.line((60, HEIGHT - 45, WIDTH - 60, HEIGHT - 45), fill="#D9E2EC", width=2)
    draw.text((65, HEIGHT - 34), "LOTTERY  •  EDF  •  RM", font=small_font, fill=MUTED)
    draw.text((1215, HEIGHT - 34), shape_persian(f"بخش {index + 1} از {SLIDE_COUNT}  •  کلیپ بی‌صدا، زیرنویس دوزبانه"), font=small_font, fill=MUTED, anchor="rt")
    return image


def main() -> None:
    output = ROOT / "assignments/05-lottery-scheduling-clip/outputs/lottery-scheduling-comparison.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    fonts = load_fonts()
    gantt_path = ROOT / "assignments/03-edf-rm-three-processes/docs/figures/edf-rm-gantt.png"
    gantt = Image.open(gantt_path).convert("RGB") if gantt_path.exists() else None

    writer = imageio_ffmpeg.write_frames(
        str(output),
        (WIDTH, HEIGHT),
        fps=FPS,
        codec="libx264",
        quality=8,
        pix_fmt_in="rgb24",
        pix_fmt_out="yuv420p",
        output_params=["-movflags", "+faststart"],
        ffmpeg_log_level="error",
    )
    writer.send(None)
    for index, slide in enumerate(SLIDES):
        frame = draw_slide(index, slide, fonts, gantt)
        raw = frame.tobytes()
        for _ in range(FPS * SLIDE_SECONDS):
            writer.send(raw)
    writer.close()
    if gantt is not None:
        gantt.close()
    print(f"Wrote {output.relative_to(ROOT)}: {SLIDE_COUNT} bilingual slides, {DURATION} seconds, no audio.")


if __name__ == "__main__":
    main()
