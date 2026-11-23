"""Build an editable 10-slide bilingual seminar deck for Exercise 6.

Optional dependency: python-pptx. The deck embeds only charts generated from
this repository's committed simulator/CSV data.
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assignments/06-lottery-seminar/slides/lottery-scheduling-seminar.pptx"
NAVY = RGBColor(20, 36, 58)
INK = RGBColor(37, 54, 75)
TEAL = RGBColor(22, 140, 140)
BLUE = RGBColor(71, 118, 168)
GOLD = RGBColor(242, 184, 75)
CORAL = RGBColor(223, 107, 99)
MUTED = RGBColor(100, 116, 139)
PALE = RGBColor(244, 247, 250)
WHITE = RGBColor(255, 255, 255)

SLIDES = [
    ("Lottery Scheduling", "زمان‌بندی لاتاری", "Proportional CPU share", "سهم نسبی پردازنده", [
        "A bilingual introduction to Lottery Scheduling and its limits.", "A comparison with EDF and Rate Monotonic scheduling.", "Claims and charts are tied to the repository code and data.",
    ], [
        "معرفی دوزبانهٔ الگوریتم لاتاری و محدودیت‌های آن.", "مقایسه با EDF و Rate Monotonic.", "ادعاها و نمودارها به کد و دادهٔ مخزن متصل‌اند.",
    ]),
    ("Scheduling objective", "هدف زمان‌بندی", "Share and deadline are different contracts.", "سهم و مهلت دو قرارداد متفاوت‌اند.", [
        "Proportional share asks how CPU is divided over time.", "Real-time analysis asks whether jobs finish by their deadlines.", "Average allocation does not imply a per-job guarantee.",
    ], [
        "سهم نسبی می‌پرسد CPU در طول زمان چگونه تقسیم می‌شود.", "تحلیل بلادرنگ می‌پرسد کارها به‌موقع تمام می‌شوند یا نه.", "میانگین تخصیص، تضمین برای یک job نیست.",
    ]),
    ("Lottery mechanism", "سازوکار لاتاری", "Tickets → uniform draw → process", "بلیت ← قرعهٔ یکنواخت ← پردازه", [
        "Give each ready process a positive ticket count.", "Draw an integer from 1 through the total ticket count.", "The cumulative ticket interval identifies the winner.",
    ], [
        "به هر پردازهٔ آماده تعداد مثبت بلیت می‌دهیم.", "یک عدد یکنواخت از ۱ تا مجموع بلیت‌ها می‌کشیم.", "بازهٔ تجمعی بلیت‌ها پردازهٔ برنده را مشخص می‌کند.",
    ]),
    ("Probability model", "مدل احتمالاتی", "pᵢ = tᵢ/T; E[Xᵢ] = n pᵢ", "احتمال هر draw برابر tᵢ/T است", [
        "For a fixed ready set, ticket share is the per-draw probability.", "Across independent draws, counts vary around their expectation.", "A finite trace need not match its theoretical ratio exactly.",
    ], [
        "برای مجموعهٔ آمادهٔ ثابت، سهم بلیت احتمال هر draw است.", "در قرعه‌های مستقل، شمار انتخاب حول انتظار تغییر می‌کند.", "trace محدود لازم نیست دقیقاً با نسبت نظری برابر باشد.",
    ]),
    ("Ticket abstractions", "مفاهیم بلیت", "Transfer · inflation · currency", "انتقال · افزایش · واحد پول", [
        "Transfer temporarily lends tickets across a dependency.", "Inflation changes a claim and requires authorization.", "Currencies represent hierarchical claims; not implemented here.",
    ], [
        "انتقال، بلیت را موقتاً در یک وابستگی قرض می‌دهد.", "افزایش بلیت سهم را عوض می‌کند و مجوز می‌خواهد.", "currency سهم سلسله‌مراتبی را می‌سازد؛ اینجا پیاده نشده است.",
    ]),
    ("EDF and RM", "EDF و RM", "Dynamic deadline vs fixed period priority", "اولویت پویای مهلت در برابر دورهٔ ثابت", [
        "EDF selects the ready job with earliest absolute deadline.", "RM assigns higher fixed priority to shorter-period tasks.", "Their utilization results require ideal model assumptions.",
    ], [
        "EDF کار آماده با زودترین مهلت مطلق را انتخاب می‌کند.", "RM به taskهای با دورهٔ کوتاه‌تر اولویت ثابت بالاتر می‌دهد.", "نتایج استفادهٔ پردازنده به فرض‌های مدل وابسته‌اند.",
    ]),
    ("Guarantee boundaries", "مرز تضمین‌ها", "EDF: U ≤ 1; RM: sufficient bound", "EDF: U≤۱؛ RM: حد کافی", [
        "EDF's classic condition assumes implicit deadlines on one CPU.", "Liu–Layland's RM utilization bound is sufficient, not necessary.", "Exceeding the RM bound does not prove unschedulability.",
    ], [
        "شرط کلاسیک EDF برای deadline ضمنی و یک پردازنده است.", "حد استفادهٔ RM کافی است، نه لازم.", "عبور از حد RM، ناممکن‌بودن زمان‌بندی را ثابت نمی‌کند.",
    ]),
    ("Program output", "خروجی برنامه", "Actual seeded Lottery and EDF/RM traces", "traceهای واقعیِ اجرای seeded", [
        "50,000 Lottery draws; weights 1, 2, 4; seed 20261123.", "The right chart is the supplied three-task EDF/RM schedule.", "These are model outputs, not a hardware benchmark.",
    ], [
        "۵۰٬۰۰۰ قرعهٔ لاتاری؛ وزن ۱، ۲، ۴؛ seed برابر ۲۰۲۶۱۱۲۳.", "نمودار دوم، زمان‌بندی سه task موجود برای EDF/RM است.", "این خروجی مدل است، نه benchmark سخت‌افزاری.",
    ]),
    ("Limits and responsible use", "محدودیت و کاربرد مسئولانه", "State assumptions before making a guarantee", "پیش از تضمین، فرض‌ها را مشخص کنید", [
        "The sample does not include blocking, jitter, or context-switch cost.", "Lottery alone offers no finite waiting bound or hard deadline.", "Choose the policy that matches the workload contract.",
    ], [
        "نمونه blocking، jitter و هزینهٔ تعویض را ندارد.", "لاتاری به‌تنهایی حد انتظار یا مهلت سخت ندارد.", "سیاست را بر اساس قرارداد workload انتخاب کنید.",
    ]),
    ("Takeaways and questions", "جمع‌بندی و پرسش", "Share? Deadline? Fairness?", "سهم؟ مهلت؟ انصاف؟", [
        "What changes when a process doubles its tickets?", "Why can a short trace differ from expected share?", "What assumptions underlie EDF/RM results?",
    ], [
        "اگر بلیت پردازه دو برابر شود چه تغییری رخ می‌دهد؟", "چرا trace کوتاه با سهم مورد انتظار فرق می‌کند؟", "نتایج EDF و RM چه فرض‌هایی لازم دارند؟",
    ]),
]


def set_rtl(paragraph) -> None:
    paragraph.alignment = PP_ALIGN.RIGHT
    p_pr = paragraph._p.get_or_add_pPr()
    p_pr.set("rtl", "1")


def set_run_font(run, size: int, bold: bool = False, color: RGBColor = INK, name: str = "Arial") -> None:
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def add_text(slide, x, y, w, h, text, size=18, bold=False, color=INK, rtl=False, align=None):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.03)
    tf.margin_bottom = Inches(0.03)
    paragraph = tf.paragraphs[0]
    if rtl:
        set_rtl(paragraph)
    elif align is not None:
        paragraph.alignment = align
    run = paragraph.add_run()
    run.text = text
    set_run_font(run, size, bold, color, "Arial")
    return shape


def add_panel(slide, x, y, w, h, color):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = WHITE
    shape.line.color.rgb = color
    shape.line.width = Pt(1.5)
    return shape


def main() -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    lottery_chart = ROOT / "assignments/01-lottery-introduction/docs/figures/lottery-frequency.png"
    gantt_chart = ROOT / "assignments/03-edf-rm-three-processes/docs/figures/edf-rm-gantt.png"

    for idx, (en_title, fa_title, en_sub, fa_sub, en_points, fa_points) in enumerate(SLIDES):
        slide = prs.slides.add_slide(blank)
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = PALE
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.12))
        bar.fill.solid()
        bar.fill.fore_color.rgb = TEAL
        bar.line.fill.background()
        add_text(slide, 0.55, 0.35, 6.1, 0.55, en_title, size=25, bold=True, color=NAVY)
        add_text(slide, 6.7, 0.35, 6.1, 0.55, fa_title, size=25, bold=True, color=NAVY, rtl=True)
        add_text(slide, 0.62, 0.98, 5.95, 0.45, en_sub, size=15, color=MUTED)
        add_text(slide, 6.75, 0.98, 5.95, 0.45, fa_sub, size=15, color=MUTED, rtl=True)
        slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.63), Inches(1.55), Inches(0.02), Inches(4.95)).fill.solid()
        divider = slide.shapes[-1]
        divider.fill.fore_color.rgb = RGBColor(217, 226, 236)
        divider.line.fill.background()

        if idx == 7 and lottery_chart.exists() and gantt_chart.exists():
            add_text(slide, 0.65, 1.55, 5.9, 0.34, "Lottery sample (50,000 seeded draws)", size=13, bold=True, color=NAVY)
            add_text(slide, 6.75, 1.55, 5.9, 0.34, "EDF/RM task-set trace (H=20)", size=13, bold=True, color=NAVY, rtl=True)
            slide.shapes.add_picture(str(lottery_chart), Inches(0.72), Inches(1.9), width=Inches(5.7))
            slide.shapes.add_picture(str(gantt_chart), Inches(6.82), Inches(1.9), width=Inches(5.7))
            add_text(slide, 0.68, 5.05, 5.8, 1.2, "Observed counts and seed are in the committed CSV. A seeded sample is not a benchmark.", size=15, color=INK)
            add_text(slide, 6.78, 5.05, 5.8, 1.2, "CSV و گانت از کد مخزن تولید شده‌اند؛ نمونهٔ seeded benchmark نیست.", size=15, color=INK, rtl=True)
        else:
            for row, (en_point, fa_point) in enumerate(zip(en_points, fa_points)):
                y = 1.72 + row * 1.42
                add_panel(slide, 0.62, y, 5.98, 1.13, [BLUE, TEAL, GOLD][row])
                add_panel(slide, 6.74, y, 5.98, 1.13, [BLUE, TEAL, GOLD][row])
                add_text(slide, 0.83, y + 0.14, 5.55, 0.82, en_point, size=17, color=INK)
                add_text(slide, 6.91, y + 0.14, 5.55, 0.82, fa_point, size=17, color=INK, rtl=True)

        add_text(slide, 0.62, 6.72, 7.5, 0.35, "Sources: Waldspurger & Weihl (1994) · Liu & Layland (1973) · repository-backed", size=10, color=MUTED)
        add_text(slide, 10.0, 6.72, 2.72, 0.35, f"{idx + 1:02d} / {len(SLIDES):02d}", size=11, color=MUTED, align=PP_ALIGN.RIGHT)

    prs.core_properties.title = "Lottery Scheduling: proportional share and real-time comparison"
    prs.core_properties.subject = "Bilingual seminar deck based on repository code and sources"
    prs.core_properties.author = "Lottery Scheduling Exercise"
    prs.core_properties.keywords = "Lottery Scheduling, EDF, RM, operating systems"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"Wrote {OUT.relative_to(ROOT)} with {len(prs.slides)} slides.")


if __name__ == "__main__":
    main()
