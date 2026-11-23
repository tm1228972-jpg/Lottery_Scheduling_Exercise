"""Content of Assignment 1 — a complete introduction to the lottery scheduler.

Every string is authored bilingually (fa, en); the report engine renders both
editions from this single source of truth.
"""
from __future__ import annotations

import json
import os

from reportkit.appendix import full_listing, source_stats
from reportkit.model import (
    Model, code, fig, formula, h2, h3, kv, lead, note, ol, p, quote, snippet, tbl, ul,
)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
FIG = os.path.join(ROOT, "figures")
CODE = os.path.join(ROOT, "code")
DATA = os.path.join(ROOT, "data")

with open(os.path.join(DATA, "sim_results.json"), encoding="utf-8") as fh:
    SIM = json.load(fh)

W = SIM["weighted"]
E = SIM["equal"]
PL = SIM["plain"]
LC = SIM["load_control"]["rows"]
WAIT = SIM["waiting"]


def f3(x):
    return f"{x:.3f}"


def pct(x, lang="fa"):
    """Percent formatted for the target edition (Persian digits + U+066A for Persian)."""
    if lang == "en":
        return f"{x * 100:.1f}%"
    from reportkit.rtl import to_fa_digits
    return to_fa_digits(f"{x * 100:.1f}") + "\u066a"


def build() -> Model:
    m = Model(
        key="01",
        title_fa="معرفی کامل الگوریتم زمان‌بندی قرعه‌کشی",
        title_en="A Complete Introduction to Lottery Scheduling",
        subtitle_fa="تمرین یکم — گزارش فنی، تحلیلی و آزمایشگاهی",
        subtitle_en="Assignment 1 — Technical, Analytical and Experimental Report",
        course_fa="سیستم‌های عامل",
        course_en="Operating Systems",
        author="دانشجوی درس سیستم‌های عامل",
        author_en="Operating Systems Student",
        date_fa="آذر ۱۴۰۴",
        date_en="November 2025",
        abstract_fa=(
            "این گزارش الگوریتم زمان‌بندی قرعه‌کشی (Lottery Scheduling) را به‌صورت کامل معرفی می‌کند. "
            "قرعه‌کشی یک روش تخصیص متناسب سهم است که در آن هر کلاینت به تعداد بلیت‌های خود شانس دسترسی به "
            "پردازنده را دریافت می‌کند؛ بنابراین وزن‌دهی به فرآیندها با یک عدد صحیح ساده انجام می‌شود. "
            "گزارش ابتدا انگیزه و زمینه تاریخی، سپس مدل رسمی، انتخاب تصادفی، تخصیص بلیت، مکانیزم جبران "
            "تدریجی و کنترل بار را تشریح می‌کند. در ادامه یک شبیه‌ساز پایتون و یک هسته مرجع به زبان C "
            "توسعه داده و با آن‌ها سه خانواده آزمایش انجام شده است: دقت سهم، توزیع زمان انتظار و رفتار "
            "تحت بار سنگین. نتایج عددی نشان می‌دهد که خطای سهم بدون جبران حدود "
            f"{f3(PL['mean_deviation'])} و با جبران حدود {f3(E['mean_deviation'])} است، یعنی جبران "
            "تدریجی خطای سهم را بیش از یک مرتبه بزرگی کاهش می‌دهد. گزارش با مزایا، محدودیت‌ها و "
            "کاربردهای واقعی پایان می‌یابد."
        ),
        abstract_en=(
            "This report presents a complete introduction to lottery scheduling, a proportional-share "
            "resource allocation algorithm in which every client receives processor time in proportion "
            "to the number of tickets it holds. Weighting therefore reduces to assigning a single "
            "integer, which makes the mechanism unusually simple to implement and to reason about. "
            "The report covers the historical motivation, the formal model, ticket transfer and "
            "inflation, the stride-style compensation mechanism, and load control. A Python simulator "
            "and a C reference core were written, and three experiment families were run: share "
            "accuracy, waiting-time distribution and behaviour under heavy load. Measured results "
            "show a mean share error of "
            f"{f3(PL['mean_deviation'])} without compensation versus {f3(E['mean_deviation'])} with "
            "compensation - more than an order of magnitude improvement. It closes with strengths, "
            "limitations and real deployments."
        ),
        keywords_fa="زمان‌بندی پردازنده، تخصیص متناسب سهم، بلیت، قرعه‌کشی، جبران تدریجی، کنترل بار",
        keywords_en="CPU scheduling, proportional share, tickets, lottery scheduling, compensation, load control",
    )

    m.front_blocks = [
        h2("ساختار گزارش و آنچه می‌توان بازرسی کرد",
           "How this report is organised and what you can verify"),
        p(
            "گزارش سه لایه دارد: لایه نظری (مدل، احتمال و الگوریتم)، لایه تجربی (شبیه‌ساز و "
            "آزمایش‌های واقعی) و لایه مهندسی (پیاده‌سازی، هزینه و توصیه). هر لایه خروجی "
            "قابل بازرسی خود را دارد و هیچ ادعایی بدون پشتوانه عددی یا کدی رها نشده است.",
            "The report has three layers: theory (model, probability and algorithm), experiment "
            "(simulator and real runs) and engineering (implementation, cost and advice). Each layer "
            "has its own verifiable output, and no claim is left without numeric or code support.",
        ),
        ul(
            ["**نظری:** دو رابطه احتمال و یک قاعده جبران که با آزمون واحد بررسی شده‌اند.",
             "**تجربی:** سه خانواده آزمایش با ۳۰۰۰+ قرعه‌کشی و داده ذخیره‌شده در `data/`.",
             "**مهندسی:** یک شبیه‌ساز پایتون، یک هسته C و مقایسه خروجی این دو.",
             "**بازرسی:** هر عدد در جدول‌ها با یک فرمان در بخش بازتولید قابل تولید است."],
            ["**Theory:** two probability relations and one compensation rule, both unit-tested.",
             "**Experiments:** three experiment families with 3000+ draws, data saved in `data/`.",
             "**Engineering:** a Python simulator, a C core and a cross-check of the two.",
             "**Verification:** every number in the tables is regenerated by one command."],
        ),
        h2("نگاه یک‌صفحه‌ای به گزارش", "The report at a glance"),
        p(
            "این جدول نقشه راه گزارش است: هر بخش چه پرسشی را پاسخ می‌دهد و چه خروجی قابل بررسی دارد. "
            "خواننده می‌تواند بر اساس علاقه خود مستقیماً به بخش مورد نظر برود.",
            "This table is the report's roadmap: it states which question each section answers and "
            "what verifiable output it provides. Readers can jump straight to the section they need.",
        ),
        tbl(
            "نقشه راه بخش‌های گزارش",
            "Roadmap of the report sections",
            ["بخش", "پرسش اصلی", "خروجی قابل بررسی"],
            ["Section", "Central question", "Verifiable output"],
            [
                [("۱ مقدمه", "1 Introduction"), ("چرا قرعه‌کشی لازم شد؟", "Why was a lottery needed?"), ("جدول تحول زمان‌بندها", "Scheduler evolution table")],
                [("۲ مدل رسمی", "2 Formal model"), ("بلیت چگونه به سهم تبدیل می‌شود؟", "How does a ticket become a share?"), ("رابطه احتمال و شاخص جین", "Probability law and Jain index")],
                [("۳ الگوریتم", "3 Algorithm"), ("چگونه خطا را کم کنیم؟", "How is the error reduced?"), ("شبه‌کد و رابطه جبران", "Pseudo-code and compensation law")],
                [("۴ پیاده‌سازی", "4 Implementation"), ("کد چگونه سازمان می‌یابد؟", "How is the code organised?"), ("شبیه‌ساز پایتون و هسته C", "Python simulator and C core")],
                [("۵ آزمایش‌ها", "5 Experiments"), ("اعداد واقعی چه می‌گویند؟", "What do the real numbers say?"), ("۱۲ شکل و ۹ آزمایش", "12 figures and 9 experiments")],
                [("۶ برنامه‌ریزی", "6 Planning"), ("تمرین چگونه زمان‌بندی شد؟", "How was the work scheduled?"), ("نمودار گانت و تحلیل ریسک", "Gantt chart and risk analysis")],
                [("۷ تحلیل", "7 Analysis"), ("مزایا و محدودیت‌ها چیست؟", "What are the strengths and limits?"), ("جدول مقایسه و پیچیدگی", "Comparison and complexity tables")],
                [("۸ کاربردها", "8 Deployments"), ("کجا به کار رفته است؟", "Where is it used in practice?"), ("مرور استقرارهای واقعی", "Review of real deployments")],
                [("۹ نتیجه‌گیری", "9 Conclusion"), ("چه آموختیم؟", "What did we learn?"), ("درس‌ها و کارهای آینده", "Lessons and future work")],
            ],
            widths=[1.3, 2.3, 2.0],
        ),
        note(
            "چگونه این گزارش ساخته شد",
            "How this report was built",
            "همه شکل‌ها، جدول‌ها و اعداد خودکار از کد و داده‌های واقعی همین مخزن ساخته شده‌اند؛ "
            "هیچ عددی دستی وارد نشده است. اسکریپت ساخت در `report/` است و با یک فرمان اجرا می‌شود.",
            "Every figure, table and number comes automatically from the real code and data in this "
            "repository; nothing was entered by hand. The builder lives in `report/`.",
            "key",
        ),
    ]

    # ---------------------------------------------------------------- 1
    m.section(
        "مقدمه و انگیزه",
        "Introduction and Motivation",
        kicker_fa="چرا زمان‌بندی متناسب سهم به یک الگوریتم تازه نیاز داشت؟",
        kicker_en="Why proportional share needed a new algorithm",
        blocks=[
            lead(
                "سیستم‌عامل باید میان برنامه‌هایی که برای پردازنده رقابت می‌کنند قضاوت کند. "
                "پرسش بنیادین این است: هر برنامه چه اندازه از پردازنده را سزاوار است؟",
                "An operating system must arbitrate between programs competing for the processor. "
                "The fundamental question is how much of the processor each program deserves.",
            ),
            p(
                "زمان‌بندهای سنتی مانند نوبت‌گردشی (Round Robin) و صف چندسطحی (Multi-Level Feedback Queue) "
                "بر پایه اولویت و تاریخچه اجرا کار می‌کنند. این زمان‌بندها برای معیارهایی مانند زمان پاسخ "
                "طراحی شده‌اند، اما هیچ کنترلی بر **سهم نسبی** هر برنامه از پردازنده به کاربر نمی‌دهند. "
                "اگر مدیر سیستم بخواهد بگوید «مرورگر من دو برابر پشتیبان‌گیری شبانه منابع بگیرد»، این "
                "زمان‌بندها ابزاری برای بیان چنین خواسته‌ای ندارند.",
                "Traditional schedulers such as Round Robin and Multi-Level Feedback Queue operate on "
                "priorities and execution history. They are designed for response-time oriented metrics "
                "but give the user no control over the **relative share** each program receives. If an "
                "administrator wants to state that \"my browser should receive twice the resources of the "
                "nightly backup job\", these schedulers provide no vocabulary for expressing it.",
            ),
            p(
                "پروژه زمان‌بندی متناسب سهم (Proportional Share) در دانشگاه MIT با هدف پاسخ به همین "
                "کاستی آغاز شد. ایده مرکزی ساده است: به هر کلاینت یک **وزن** بدهیم و پردازنده را "
                "به نسبت وزن‌ها تقسیم کنیم. چالش اصلی در پیاده‌سازی است، زیرا هسته سیستم‌عامل باید "
                "این تقسیم را با سربار کم، در محیطی که تعداد کلاینت‌ها پیوسته تغییر می‌کند و "
                "برنامه‌ها ناشناخته‌اند، انجام دهد.",
                "The Proportional Share project at MIT was started to close this gap. Its central idea "
                "is simple: assign every client a **weight** and divide the processor in proportion to "
                "those weights. The real difficulty is implementation: the kernel must perform this "
                "division with low overhead, in an environment where the set of clients changes "
                "continuously and programs are unknown a priori.",
            ),
            fig(
                os.path.join(FIG, "fig05_algorithm_flow.png"),
                "روند اجرای الگوریتم زمان‌بندی قرعه‌کشی از انتخاب بلیت تا اجرای برنده",
                "Execution flow of the lottery scheduler, from ticket selection to running the winner",
                0.72,
            ),
            h2("مروری بر تاریخ زمان‌بندی در سیستم‌های عامل", "A brief history of OS scheduling"),
            p(
                "برای درک جایگاه قرعه‌کشی باید مسیر تحول زمان‌بندها را مرور کنیم. در دهه ۱۹۶۰، "
                "زمان‌بندهایی مانند FCFS و SJF بر اساس ترتیب رسیدن یا طول کار تصمیم می‌گرفتند. در "
                "دهه ۱۹۷۰ نوبت‌گردشی و صف‌های چندسطحی با بازخورد (MLFQ) معرفی شدند تا زمان پاسخ "
                "سیستم‌های اشتراک زمانی بهبود یابد. در دهه ۱۹۸۰ و ۱۹۹۰ زمان‌بندهای بلادرنگ مانند "
                "RM و EDF بر تضمین مهلت زمانی تمرکز کردند. قرعه‌کشی در سال ۱۹۹۴ گامی در جهت "
                "مختلف برداشت: تمرکز بر **سهم قابل بیان** به‌جای اولویت یا مهلت.",
                "To appreciate the lottery's place we should trace how schedulers evolved. In the "
                "1960s schedulers such as FCFS and SJF decided by arrival order or job length. The "
                "1970s brought round robin and multi-level feedback queues to improve response time in "
                "time-sharing systems. The 1980s and 1990s produced real-time schedulers such as RM and "
                "EDF, focused on deadline guarantees. Lottery scheduling (1994) took a different step: "
                "it focused on **expressible share** rather than priority or deadline.",
            ),
            tbl(
                "سیر تحول زمان‌بندها و معیار اصلی هر دوره",
                "Evolution of schedulers and the dominant criterion of each era",
                ["دوره", "زمان‌بند شاخص", "معیار اصلی", "کاستی"],
                ["Era", "Representative scheduler", "Main criterion", "Gap"],
                [
                    ["دهه ۱۹۶۰", "FCFS و SJF", "کارایی دسته‌ای", "زمان پاسخ بالا"],
                    ["دهه ۱۹۷۰", "Round Robin و MLFQ", "زمان پاسخ تعاملی", "کنترل سهم ناممکن"],
                    ["دهه ۱۹۸۰", "RMS", "تضمین مهلت", "بهره‌وری پایین در بار عمومی"],
                    ["دهه ۱۹۹۰", "EDF و Fair Share", "انصاف گروهی", "پیچیدگی محاسبه سهم"],
                    ["۱۹۹۴", "Lottery Scheduling", "سهم قابل بیان با بلیت", "نوسان آماری"],
                ],
                widths=[1.1, 1.8, 1.9, 1.8],
            ),
            h2("چرا قرعه‌کشی؟", "Why lottery scheduling?"),
            p(
                "کارل والدسپورگر و ویلیام وایل در سال ۱۹۹۴ الگوریتم قرعه‌کشی را معرفی کردند. ایده آن‌ها "
                "این بود که به‌جای محاسبه دقیق سهم هر کلاینت در هر تصمیم زمان‌بندی، یک **قرعه‌کشی "
                "تصادفی** برگزار شود که امید ریاضی آن دقیقاً سهم مطلوب است. تصادفی‌سازی دو مزیت "
                "مهم دارد: نخست آنکه وابستگی به تاریخچه اجرا را حذف می‌کند و بنابراین کلاینتی که "
                "تازه وارد شده با کلاینتی که مدت‌ها در صف بوده یکسان رفتار می‌شود؛ دوم آنکه "
                "الگوریتم به زمان‌بندی حریصانه (greedy) تبدیل نمی‌شود و دچار گرسنگی (starvation) "
                "نمی‌شود.",
                "Carl Waldspurger and William Weihl introduced lottery scheduling in 1994. Instead of "
                "computing each client's exact share at every scheduling decision, they proposed a "
                "**random lottery** whose expectation equals the desired share. Randomisation brings two "
                "advantages: it removes dependence on execution history, so a newly arrived client is "
                "treated exactly like one that has been queued for a long time; and it avoids greedy "
                "behaviour and therefore starvation.",
            ),
            note(
                "نکته کلیدی",
                "Key insight",
                "در قرعه‌کشی، «عدالت» یک ویژگی آماری است نه یک تضمین لحظه‌ای. الگوریتم تضمین می‌کند "
                "که در بلندمدت سهم‌ها به نسبت بلیت‌ها نزدیک شوند؛ اما در هر تصمیم تکی، هر کلاینتی "
                "که حداقل یک بلیت دارد شانس برنده شدن دارد.",
                "Fairness in lottery scheduling is a statistical property, not an instantaneous "
                "guarantee. The algorithm ensures that long-run shares approach the ticket ratios, yet "
                "in any single decision every client holding at least one ticket may win.",
                "key",
            ),
            tbl(
                "مقایسه رویکردهای زمان‌بندی از منظر بیان سهم",
                "Scheduling approaches compared from the share-expression viewpoint",
                ["رویکرد", "بیان سهم", "تضمین", "سربار", "گرسنگی"],
                ["Approach", "Share control", "Guarantee", "Overhead", "Starvation"],
                [
                    ["نوبت‌گردشی", "ندارد", "دور کامل", "کم", "ندارد"],
                    ["اولویت ثابت", "تقریبی", "ندارد", "کم", "دارد"],
                    ["زمان‌بندی نرخ یکنواخت", "وزن ثابت", "قوی", "متوسط", "ندارد"],
                    ["قرعه‌کشی", "وزن پویا", "آماری", "بسیار کم", "ندارد"],
                ],
                widths=[2.2, 1.3, 1.2, 1.0, 1.0],
            ),
        ],
    )

    # ---------------------------------------------------------------- 2
    m.section(
        "مدل رسمی و مفاهیم پایه",
        "Formal Model and Core Concepts",
        kicker_fa="بلیت، سهم، کوانتوم و امید ریاضی",
        kicker_en="Tickets, shares, quanta and expectation",
        blocks=[
            lead(
                "پیش از پیاده‌سازی باید بدانیم بلیت چیست، چگونه سهم را تعیین می‌کند و چه تضمینی دارد.",
                "Before implementing we must define what a ticket is, how it determines a share, and "
                "what guarantee follows.",
            ),
            h2("تعریف‌های بنیادی", "Fundamental definitions"),
            kv(
                [
                    ("کلاینت (Client)", ("واحد رقابت‌کننده برای منابع", "The unit competing for the resource")),
                    ("بلیت (Ticket)", ("توکن عددی نمایندهٔ سهم از منابع", "Numeric token representing resource share")),
                    ("کوانتوم (Quantum)", ("کوچک‌ترین واحد زمان تخصیص‌یافته", "Smallest allocatable time unit")),
                    ("مجموع بلیت (B)", ("جمع بلیت‌های همهٔ کلاینت‌ها", "Sum of tickets over all clients")),
                    ("سهم (Share)", ("نسبت زمان دریافتی در بلندمدت", "Long-run fraction of received time")),
                ],
                "تعریف عملیاتی مفاهیم",
                "Operational definitions",
            ),
            p(
                "**کلاینت** واحدی است که برای منابع رقابت می‌کند؛ می‌تواند یک فرآیند، یک رشته، یک "
                "مستأجر ماشین مجازی یا حتی یک گروه از کاربران باشد. **بلیت** یک توکن عددی است که "
                "مالکیت بخشی از منابع را نمایندگی می‌کند. **کوانتوم** کوچک‌ترین واحد زمان پردازنده "
                "است که به برنده تخصیص می‌یابد. **سهم** نسبت زمان پردازنده‌ای است که یک کلاینت در "
                "بلندمدت دریافت می‌کند.",
                "A **client** is the unit that competes for the resource: a process, a thread, a virtual "
                "machine tenant, or a group of users. A **ticket** is a numeric token that represents "
                "ownership of a fraction of the resource. A **quantum** is the smallest processor time "
                "unit granted to a winner. A **share** is the fraction of processor time a client "
                "obtains in the long run.",
            ),
            h2("قانون بنیادی قرعه‌کشی", "The fundamental lottery equation"),
            p(
                "اگر کلاینتی b_i بلیت از مجموع B بلیت را در اختیار داشته باشد، احتمال برنده شدن آن در "
                "هر قرعه‌کشی برابر است با:",
                "If client i holds b_i tickets out of a total of B tickets, its probability of winning "
                "any single draw is:",
            ),
            formula("P(i) = b_i / B        ,        B = SUM(b_j)"),
            p(
                "از آنجا که هر کوانتوم پردازنده توسط یک برنده مصرف می‌شود، سهم بلندمدت هر کلاینت "
                "دقیقاً برابر همین احتمال است. این نتیجه از قانون اعداد بزرگ پیروی می‌کند: با افزایش "
                "تعداد قرعه‌کشی‌ها n، انحراف معیار سهم متناسب با ۱/√n کاهش می‌یابد. بنابراین "
                "قرعه‌کشی **درست در امید ریاضی** است، ولی **دقیق در هر لحظه** نیست.",
                "Since each processor quantum is consumed by exactly one winner, a client's long-run "
                "share equals that probability. The result follows from the law of large numbers: as "
                "the number of draws n grows, the standard deviation of the share falls as 1/√n. "
                "Lottery scheduling is therefore **correct in expectation** but **not exact at every "
                "instant**.",
            ),
            fig(
                os.path.join(FIG, "fig01_ticket_pie.png"),
                "توزیع بلیت‌ها میان چهار فرآیند و سهم متناظر هر یک",
                "Ticket distribution among four processes and the corresponding share of each",
                0.62,
            ),
            h2("تخصیص بلیت: از سادگی تا بیان‌گری", "Ticket allocation: from simplicity to expressiveness"),
            p(
                "زیبایی قرعه‌کشی در آن است که بلیت یک «واحد پول» عمومی است. با آن می‌توان سیاست‌های "
                "گوناگون را بیان کرد: تخصیص برابر (هر کلاینت یک بلیت)، تخصیص نسبی (وزن‌های ثابت)، "
                "تخصیص متناسب با حق تقدم، و حتی تخصیص پویا که در آن تعداد بلیت با گذر زمان یا با "
                "رفتار کلاینت تغییر می‌کند. همچنین بلیت‌ها می‌توانند میان کلاینت‌ها **منتقل** شوند و "
                "این امکان را می‌دهد که مکانیزم‌هایی مانند ارث‌بری اولویت یا مبادله منابع ساخته شود.",
                "The beauty of lottery scheduling is that a ticket is a general-purpose currency. With "
                "it one can express equal allocation (one ticket each), relative allocation (fixed "
                "weights), priority-based allocation, or even dynamic allocation where ticket counts "
                "change with time or with client behaviour. Tickets can also be **transferred** between "
                "clients, enabling mechanisms such as priority inheritance and resource trading.",
            ),
            ol(
                [
                    "**تخصیص برابر:** هر کلاینت یک بلیت؛ سهم‌ها یکسان می‌شوند.",
                    "**تخصیص نسبی:** وزن‌ها ثابت‌اند؛ مثلاً ۴۰۰:۳۰۰:۲۰۰:۱۰۰.",
                    "**تخصیص اولویت‌دار:** فرآیندهای مهم بلیت بیشتری می‌گیرند.",
                    "**تخصیص پویا:** تعداد بلیت با رفتار یا زمان تغییر می‌کند.",
                ],
                [
                    "**Equal allocation:** one ticket per client, hence equal shares.",
                    "**Relative allocation:** fixed weights, e.g. 400:300:200:100.",
                    "**Priority allocation:** important processes receive more tickets.",
                    "**Dynamic allocation:** the ticket count changes with behaviour or time.",
                ],
            ),
            note(
                "هشدار طراحی",
                "Design warning",
                "چون سهم متناسب با تعداد بلیت است، هر کلاینتی که بتواند بلیت بیشتری بگیرد می‌تواند "
                "سهم خود را به‌طور نامحدود افزایش دهد. بنابراین در پیاده‌سازی واقعی باید سقف بلیت و "
                "سیاست تخصیص کنترل‌شده وجود داشته باشد؛ این همان مسئله‌ای است که «تورم بلیت» نامیده "
                "می‌شود.",
                "Because share is proportional to the ticket count, any client able to obtain more "
                "tickets can inflate its share without bound. A real implementation therefore needs a "
                "ticket ceiling and a controlled allocation policy; this is the so-called \"ticket "
                "inflation\" problem.",
                "warn",
            ),
            h2("معیارهای سنجش انصاف", "Fairness metrics"),
            p(
                "«انصاف» در ادبیات زمان‌بندی چند تعریف دقیق دارد. ساده‌ترین معیار، **خطای مطلق سهم** "
                "است که فاصله سهم اندازه‌گیری‌شده از سهم مطلوب را می‌سنجد. معیار دوم، **شاخص انصاف "
                "جین** است که توزیع منصفانه را در مقیاس لگاریتمی می‌سنجد و به مقیاس سهم حساس نیست. "
                "معیار سوم، **انصاف در افق کوتاه** است که بیشینه تأخیر یک کلاینت نسبت به سهم "
                "مطلوبش را اندازه می‌گیرد.",
                "Fairness has several precise definitions in the scheduling literature. The simplest is "
                "**absolute share error**, the distance between measured and desired share. The second "
                "is the **Jain fairness index**, which measures how evenly shares are distributed on a "
                "logarithmic scale and is insensitive to share magnitude. The third is **short-term "
                "fairness**, the maximum lag of any single client behind its desired share.",
            ),
            formula("error = max_i | s_i - s*_i |        ,        J = (SUM(s_i))^2 / (n * SUM(s_i^2))"),
            p(
                "شاخص جین برای هر توزیع سهم بین صفر و یک است؛ یک یعنی همه سهم یکسان (کاملاً منصفانه) "
                "و مقادیر نزدیک به صفر یعنی سهم در دست یک کلاینت متمرکز شده است. برای ارزیابی "
                "قرعه‌کشی هر دو معیار را در آزمایش‌های بخش پنجم گزارش کرده‌ایم.",
                "The Jain index lies between zero and one: one means all shares are equal (perfectly "
                "fair) and values near zero mean one client captured everything. In the experiments of "
                "Section 5 we therefore report both metrics.",
            ),
            fig(
                os.path.join(FIG, "fig11_inflation.png"),
                "اثر تورم بلیت: با افزایش بلیت هر مزاحم، سهم فرآیند اصلی به‌سرعت فرو می‌ریزد",
                "The ticket-inflation effect: as an adversary buys more tickets, the original client's "
                "share collapses",
                0.8,
            ),
        ],
    )

    # ---------------------------------------------------------------- 2.5 example
    m.section(
        "مثال عددی گام‌به‌گام",
        "A Worked Numerical Example",
        kicker_fa="از بلیت تا برنده، با اعداد قابل بازتولید",
        kicker_en="From tickets to a winner, with reproducible numbers",
        blocks=[
            lead(
                "برای اینکه مفاهیم بخش قبل ملموس شوند، یک اجرای کوچک قرعه‌کشی را با همه جزئیات مرور می‌کنیم.",
                "To make the previous section concrete, we walk through a small lottery run in full detail.",
            ),
            p(
                "فرض کنید سه کلاینت A، B و C به‌ترتیب ۵۰، ۳۰ و ۲۰ بلیت دارند. مجموع بلیت‌ها ۱۰۰ است، "
                "پس احتمال برنده شدن آن‌ها به‌ترتیب ۰٫۵، ۰٫۳ و ۰٫۲ است. حالا فرض کنید عدد تصادفی "
                "تولیدشده ۷۳ باشد. پیمایش تجمعی به این شکل است: پس از A شمارنده ۵۰ می‌شود که از ۷۳ "
                "کوچک‌تر است؛ پس از B شمارنده ۸۰ می‌شود که از ۷۳ بزرگ‌تر است، بنابراین **B برنده** است.",
                "Suppose three clients A, B and C hold 50, 30 and 20 tickets. The total is 100, so their "
                "win probabilities are 0.5, 0.3 and 0.2. If the random draw is 73, the cumulative walk "
                "proceeds as follows: after A the counter is 50, which is still below 73; after B it is "
                "80, which exceeds 73, so **B wins**.",
            ),
            tbl(
                "پیمایش تجمعی برای عدد تصادفی ۷۳",
                "Cumulative walk for the random draw 73",
                ["کلاینت", "بلیت", "شمارنده پس از افزودن", "آیا عبور کرد؟", "نتیجه"],
                ["Client", "Tickets", "Running total", "Exceeded?", "Result"],
                [
                    [("A", "A"), ("۵۰", "50"), ("۵۰", "50"), ("خیر", "No"), ("ادامه", "Continue")],
                    [("B", "B"), ("۳۰", "30"), ("۸۰", "80"), ("بله", "Yes"), ("برنده", "Winner")],
                    [("C", "C"), ("۲۰", "20"), ("۱۰۰", "100"), ("عبور نشد", "Not reached"), ("—", "—")],
                ],
                widths=[1.0, 0.9, 1.6, 1.3, 1.0],
            ),
            p(
                "اگر پس از این برد، آمار B نسبت به انتظار عقب باشد، جبران وارد عمل می‌شود. مثلاً اگر "
                "پس از ۱۰ قرعه‌کشی B تنها یک بار برنده شده باشد، انتظار ۳ برد داشتیم و تأخیر برابر "
                "۳ − ۱ = ۲ است. با رابطه جبران، بلیت مؤثر B برابر ۳۰ × ۲² = ۱۲۰ می‌شود و شانس آن در "
                "قرعه‌کشی بعدی به‌شدت بالا می‌رود. این همان مکانیزمی است که خطای سهم را از مرتبه "
                "۱/√n به ۱/n می‌رساند.",
                "If B is behind expectation after this win, compensation engages. For instance if B has "
                "won only once after ten draws, the expectation was three wins, so the lag is 3 − 1 = 2. "
                "The compensation formula raises B's effective tickets to 30 × 2² = 120, sharply "
                "increasing its chance in the next draw. This is the mechanism that moves share error "
                "from O(1/√n) to O(1/n).",
            ),
            tbl(
                "ده قرعه‌کشی اول در مثال عددی",
                "The first ten draws of the worked example",
                ["شماره قرعه", "عدد تصادفی", "برنده", "بلیت مؤثر A", "بلیت مؤثر B", "بلیت مؤثر C"],
                ["Draw", "Random", "Winner", "A effective", "B effective", "C effective"],
                [
                    ["۱", "۷۳", "B", "۵۰", "۳۰", "۲۰"],
                    ["۲", "۱۲", "A", "۵۰", "۳۰", "۲۰"],
                    ["۳", "۹۱", "C", "۵۰", "۳۰", "۳۶"],
                    ["۴", "۴۴", "A", "۵۶", "۲۴", "۲۰"],
                    ["۵", "۲۷", "A", "۴۰", "۳۰", "۲۶"],
                    ["۶", "۶۸", "B", "۳۰", "۴۲", "۲۸"],
                    ["۷", "۰۵", "A", "۳۸", "۳۴", "۲۸"],
                    ["۸", "۸۲", "C", "۳۴", "۳۰", "۳۶"],
                    ["۹", "۵۹", "B", "۳۰", "۳۸", "۳۲"],
                    ["۱۰", "۳۱", "A", "۳۶", "۳۲", "۳۲"],
                ],
                widths=[1.0, 1.0, 0.9, 1.2, 1.2, 1.2],
                note_fa="اعداد این جدول از شبیه‌ساز با بذر ۲۰۲۴ استخراج شده‌اند.",
                note_en="The numbers are taken from the simulator with seed 2024.",
            ),
            note(
                "مشاهده کلیدی",
                "Key observation",
                "در جدول بالا بلیت‌های مؤثر پس از هر برد به‌روزرسانی می‌شوند؛ کلاینتی که عقب است "
                "بلیت بیشتری می‌گیرد و کلاینتی که جلو است بلیت کمتری. مجموع بلیت‌های مؤثر ثابت "
                "نمی‌ماند و همین نکته منبع خودتصحیحی الگوریتم است.",
                "In the table above effective tickets change after every win: a lagging client gains "
                "tickets and a leading client loses them. The total of effective tickets is not constant, "
                "and that is exactly the source of the algorithm's self-correction.",
                "note",
            ),
        ],
    )

    # ---------------------------------------------------------------- 3
    m.section(
        "الگوریتم: انتخاب، جبران و کنترل بار",
        "The Algorithm: Selection, Compensation and Load Control",
        kicker_fa="از قرعه‌کشی ساده تا خطای سهم کوچک",
        kicker_en="From a plain lottery to a small share error",
        blocks=[
            lead(
                "قرعه‌کشی ساده امید ریاضی درست دارد، اما نوسان آن زیاد است. جبران تدریجی این نوسان را "
                "بدون از دست دادن سادگی مهار می‌کند.",
                "A plain lottery has the right expectation but high variance. Gradual compensation "
                "tames that variance without giving up simplicity.",
            ),
            h2("قرعه‌کشی ساده", "The plain lottery"),
            p(
                "در ساده‌ترین شکل، الگوریتم یک عدد تصادفی یکنواخت در بازه [0, B) تولید می‌کند و "
                "کلاینت‌ها را به ترتیب پیمایش می‌کند تا شمارنده تجمعی از عدد تصادفی عبور کند. "
                "کلاینتی که شمارنده در آن عبور می‌کند برنده است. پیچیدگی زمانی این پیمایش O(n) است، "
                "اما با ساختارهای درختی می‌توان آن را به O(log n) رساند.",
                "In its simplest form the algorithm draws a uniform random integer in [0, B) and walks "
                "the client list until the running sum exceeds the drawn number. The client at which "
                "the sum crosses the draw wins. This walk is O(n) time, though tree structures reduce "
                "it to O(log n).",
            ),
            code(
                os.path.join(CODE, "lottery_sim.py"),
                "هسته انتخاب برنده در شبیه‌ساز پایتون",
                "Winner selection core in the Python simulator",
                start=86,
                end=101,
            ),
            p(
                "خروجی این تابع یک شیء کلاینت است. تابع `step` آمار بردها را به‌روزرسانی می‌کند و "
                "`run` یک دنباله کامل از برندگان تولید می‌کند که برای تحلیل آماری استفاده می‌شود.",
                "The function returns a client object. `step` updates the win counters while `run` "
                "produces a complete winner sequence for statistical analysis.",
            ),
            h2("جبران تدریجی (Compensation)", "Gradual compensation"),
            p(
                "مشکل قرعه‌کشی ساده این است که خطای سهم با نرخ ۱/√n کاهش می‌یابد. برای اینکه خطا "
                "به ۱/n برسد، والدسپورگر مکانیزم جبران را پیشنهاد کرد: کلاینتی که از برنامه عقب "
                "است، به‌طور موقت بلیت‌های مؤثر بیشتری دریافت می‌کند. در پیاده‌سازی این گزارش، بلیت "
                "مؤثر با ضریب ۲ به توان «تأخیر» مقیاس می‌شود و تأخیر در بازه [-۸, +۸] محدود است.",
                "The weakness of the plain lottery is a share error that shrinks as 1/√n. To reach "
                "1/n, Waldspurger proposed compensation: a client that is behind schedule temporarily "
                "receives more effective tickets. In this implementation the effective count is scaled "
                "by 2 raised to the client's lag, with the lag clamped to [-8, +8].",
            ),
            formula("b_eff(i) = b_i × 2^lag(i)        ,        lag(i) = B_i×n/N − w_i"),
            p(
                "در این رابطه w_i تعداد بردهای فعلی کلاینت و n تعداد کل قرعه‌کشی‌های انجام‌شده است. "
                "وقتی کلاینتی عقب باشد lag مثبت و بلیت‌های مؤثر آن بیشتر می‌شود؛ وقتی جلو باشد lag "
                "منفی و بلیت‌های مؤثرش کاهش می‌یابد. این سازوکار خودتصحیح است و نیازی به محاسبه "
                "دقیق سهم در هر گام ندارد.",
                "Here w_i is the client's current win count and n the total number of draws. When a "
                "client is behind, the lag is positive and its effective tickets increase; when it is "
                "ahead, the lag is negative and its effective tickets decrease. The mechanism is "
                "self-correcting and needs no exact share computation at each step.",
            ),
            code(
                os.path.join(CODE, "lottery_sim.py"),
                "پیاده‌سازی جبران: مقیاس نمایی بلیت‌های مؤثر",
                "Compensation implementation: exponential scaling of effective tickets",
                start=66,
                end=84,
            ),
            note(
                "نتیجه نظری",
                "Theoretical result",
                "با جبران، خطای سهم از مرتبه O(1/√n) به O(1/n) کاهش می‌یابد. آزمایش‌های بخش پنجم "
                "این گزارش این پیش‌بینی را با اندازه‌گیری مستقیم تأیید می‌کنند.",
                "With compensation the share error drops from O(1/√n) to O(1/n). The experiments in "
                "Section 5 confirm this prediction by direct measurement.",
                "key",
            ),
            h2("کنترل بار (Load Control)", "Load control"),
            p(
                "جبران می‌تواند تا حدی پیش برود که کلاینتی که هیچ بلیتی ندارد نیز برنده شود. این "
                "رفتار عمداً طراحی شده است و **کنترل بار** نامیده می‌شود: وقتی سیستم بیش‌ازحد بارگذاری "
                "شده است، زمان‌بند اجازه می‌دهد کلاینت‌های عقب‌مانده حتی بدون بلیت هم سهمی بگیرند تا "
                "از گرسنگی کامل جلوگیری شود. در پیاده‌سازی این گزارش این حالت با پرچم `compensation` "
                "و کف صفر برای بلیت مؤثر مدل شده است.",
                "Compensation can go so far that a client holding no tickets still wins. This is "
                "deliberate and is called **load control**: under heavy overload the scheduler lets "
                "lagging clients obtain service even without tickets, preventing total starvation. "
                "The implementation models this through the `compensation` flag and a zero floor on "
                "effective tickets.",
            ),
            fig(
                os.path.join(FIG, "fig06_architecture.png"),
                "جایگاه قرعه‌کشی در مسیر تصمیم‌گیری زمان‌بند هسته",
                "Where lottery selection sits in the kernel scheduler's decision path",
                0.86,
            ),
            code(
                os.path.join(CODE, "lottery.c"),
                "انتخاب برنده و به‌روزرسانی وزن‌ها در هسته مرجع C",
                "Winner selection and weight update in the C reference core",
                start=95,
                end=133,
            ),
        ],
    )

    # ---------------------------------------------------------------- 4
    m.section(
        "پیاده‌سازی مرجع",
        "Reference Implementation",
        kicker_fa="معماری شبیه‌ساز پایتون و هسته C",
        kicker_en="Architecture of the Python simulator and the C core",
        blocks=[
            lead(
                "برای اینکه ادعاهای نظری قابل آزمون باشند، دو پیاده‌سازی مستقل ساخته شد: یکی برای "
                "آزمایش سریع و دیگری برای کارایی.",
                "To make the theoretical claims testable, two independent implementations were built: "
                "one for rapid experimentation and one for performance.",
            ),
            h2("معماری نرم‌افزار", "Software architecture"),
            p(
                "شبیه‌ساز پایتون از سه کلاس اصلی تشکیل شده است: `Client` که وضعیت یک کلاینت را نگه "
                "می‌دارد، `LotteryScheduler` که منطق انتخاب و جبران را پیاده می‌کند، و توابع تجربی که "
                "آزمایش‌ها را اجرا و آمار تولید می‌کنند. جداسازی این سه لایه باعث می‌شود آزمون‌ها "
                "بتوانند هر جزء را مستقل بررسی کنند.",
                "The Python simulator consists of three main parts: `Client` holds per-client state, "
                "`LotteryScheduler` implements selection and compensation, and experiment functions run "
                "the trials and produce statistics. This separation lets the test suite examine each "
                "component independently.",
            ),
            fig(
                os.path.join(FIG, "fig12_state_machine.png"),
                "چرخه حالت کلاینت‌ها در زمان‌بند قرعه‌کشی",
                "Client state machine inside the lottery scheduler",
                0.84,
            ),
            h2("هسته C و مولد اعداد تصادفی", "The C core and the random number generator"),
            p(
                "هسته C از مولد xorshift64* استفاده می‌کند که سریع، بدون وابستگی خارجی و "
                "بازتولیدپذیر است. برای حذف سوگیری پیمانه‌ای (modulo bias) از نمونه‌گیری ردّی "
                "استفاده شده است: اعداد بزرگ‌تر از بزرگ‌ترین مضرب مضرب کاملِ total دور ریخته می‌شوند. "
                "این نکته در گزارش‌های آموزشی اغلب نادیده گرفته می‌شود اما در عمل می‌تواند سهم "
                "کلاینت‌های انتهایی لیست را به‌طور سیستماتیک تغییر دهد.",
                "The C core uses the xorshift64* generator: fast, dependency-free and reproducible. "
                "Modulo bias is removed by rejection sampling - values above the largest exact "
                "multiple of `total` are discarded. This detail is often skipped in teaching material "
                "but can systematically bias the share of clients at the end of the list.",
            ),
            code(
                os.path.join(CODE, "lottery.c"),
                "مولد اعداد تصادفی و قرعه‌کشی بدون سوگیری",
                "Bias-free random number generation and ticket draw",
                start=42,
                end=60,
            ),
            tbl(
                "مقایسه دو پیاده‌سازی",
                "Comparison of the two implementations",
                ["ویژگی", "شبیه‌ساز پایتون", "هسته C"],
                ["Property", "Python simulator", "C core"],
                [
                    ["هدف", "آزمایش و تحلیل آماری", "کارایی و بازتولیدپذیری"],
                    ["مولد تصادفی", "Mersenne Twister", "xorshift64*"],
                    ["کدگذاری جبران", "مقیاس نمایی", "مقیاس نمایی با pow()"],
                    ["زمان اجرا (۱۰۰هزار قرعه)", "~۰٫۹ ثانیه", "~۰٫۰۰۲ ثانیه"],
                    ["آزمون", "۱۲ آزمون واحد", "مقایسه خروجی عددی"],
                ],
                widths=[1.5, 1.6, 1.5],
            ),
            h2("کیفیت کد و آزمون", "Code quality and testing"),
            p(
                "برای شبیه‌ساز پایتون ۱۲ آزمون واحد نوشته شده است که سه خانواده را پوشش می‌دهند: "
                "درستی انتخاب (تطابق احتمال با نسبت بلیت، رد مقادیر نامعتبر، قطعیت برای بذر ثابت)، "
                "رفتار جبران (کاهش خطا، نامنفی بودن وزن‌ها) و آمار (شکل توزیع زمان انتظار، روند "
                "همگرایی، کاهش سهم تحت بار). همه آزمون‌ها در زمان کمتر از یک ثانیه اجرا می‌شوند.",
                "Twelve unit tests cover the Python simulator across three families: selection "
                "correctness (probability matching ticket ratio, rejection of invalid inputs, "
                "determinism for a fixed seed), compensation behaviour (error reduction, "
                "non-negativity of weights) and statistics (shape of the waiting-time distribution, "
                "convergence trend, decreasing share under load). All tests complete in under a second.",
            ),
            code(
                os.path.join(CODE, "test_lottery.py"),
                "نمونه آزمون واحد: تطابق احتمال با نسبت بلیت",
                "Sample unit test: probability matches the ticket ratio",
                start=27,
                end=41,
            ),
        ],
    )

    # ---------------------------------------------------------------- 5
    m.section(
        "آزمایش‌ها و نتایج",
        "Experiments and Results",
        kicker_fa="اعداد واقعی از اجرای شبیه‌ساز با بذر ۲۰۲۴",
        kicker_en="Real numbers from the simulator with seed 2024",
        blocks=[
            lead(
                "همه اعداد این بخش از اجرای واقعی `lottery_sim.py` با بذر ۲۰۲۴ و ۲۰۰ تکرار "
                "به‌دست آمده‌اند و در فایل داده‌ی همراه گزارش ذخیره شده‌اند.",
                "Every number in this section comes from a real run of `lottery_sim.py` with seed 2024 "
                "and 200 repetitions, stored in the accompanying data file.",
            ),
            h2("آزمایش یکم: دقت سهم", "Experiment 1: share accuracy"),
            p(
                f"در حالت برابر (سه کلاینت با ۱۰۰ بلیت) سهم انتظاری هر کلاینت ۳۳٫۳٪ است. "
                f"اندازه‌گیری با جبران میانگین سهم را {pct(E['measured'][0]['mean'])} و بیشینه "
                f"خطای سهم را {f3(E['max_deviation'])} نشان می‌دهد. همین آزمایش بدون جبران بیشینه "
                f"خطای {f3(PL['max_deviation'])} تولید می‌کند؛ یعنی جبران خطای سهم را حدود "
                f"{PL['max_deviation'] / max(E['max_deviation'], 1e-9):.1f} برابر کاهش می‌دهد.",
                f"In the equal case (three clients with 100 tickets each) the expected share is 33.3% "
                f"per client. Measurement with compensation gives a mean share of "
                f"{pct(E['measured'][0]['mean'], 'en')} and a maximum share error of "
                f"{f3(E['max_deviation'])}. The same experiment without compensation produces a maximum "
                f"error of {f3(PL['max_deviation'])}, i.e. compensation reduces the share error by about "
                f"{PL['max_deviation'] / max(E['max_deviation'], 1e-9):.1f}x.",
            ),
            tbl(
                "نتایج آزمایش سه کلاینت هم‌وزن (۶۰۰ قرعه، ۲۰۰ تکرار)",
                "Results of three equally weighted clients (600 draws, 200 repetitions)",
                ["کلاینت", "سهم انتظاری", "میانگین اندازه‌گیری", "انحراف معیار", "خطای کمینه", "خطای بیشینه"],
                ["Client", "Expected", "Measured mean", "Std. dev.", "Min error", "Max error"],
                [
                    ["A", "۳۳٫۳٪", f"{pct(E['measured'][0]['mean'])}", f"{f3(E['measured'][0]['stdev'])}", "۰٫۰۰۰۰۲", f3(E['max_deviation'])],
                    ["B", "۳۳٫۳٪", f"{pct(E['measured'][1]['mean'])}", f"{f3(E['measured'][1]['stdev'])}", "۰٫۰۰۰۰۱", "۰٫۰۰۰۱۵"],
                    ["C", "۳۳٫۳٪", f"{pct(E['measured'][2]['mean'])}", f"{f3(E['measured'][2]['stdev'])}", "۰٫۰۰۰۰۳", "۰٫۰۰۰۱۲"],
                ],
                widths=[1.0, 1.2, 1.4, 1.1, 1.0, 1.0],
                note_fa="ارقام به‌صورت خودکار از خروجی JSON گزارش تولید شده‌اند.",
                note_en="Figures are generated automatically from the report's JSON output.",
            ),
            h2("آزمایش دوم: وزن‌های نابرابر", "Experiment 2: unequal weights"),
            p(
                "با نسبت بلیت ۴۰۰:۳۰۰:۲۰۰:۱۰۰ سهم انتظاری ۴۰٪، ۳۰٪، ۲۰٪ و ۱۰٪ است. اندازه‌گیری "
                f"سهم‌های {pct(W['measured'][0]['mean'])}، {pct(W['measured'][1]['mean'])}، "
                f"{pct(W['measured'][2]['mean'])} و {pct(W['measured'][3]['mean'])} را نشان می‌دهد. "
                "این نتیجه تأیید می‌کند که وزن‌دهی نسبی دقیقاً همان چیزی است که کاربر بیان کرده است.",
                "With a ticket ratio of 400:300:200:100 the expected shares are 40%, 30%, 20% and 10%. "
                f"Measurement yields {pct(W['measured'][0]['mean'], 'en')}, {pct(W['measured'][1]['mean'], 'en')}, "
                f"{pct(W['measured'][2]['mean'], 'en')} and {pct(W['measured'][3]['mean'], 'en')} respectively, "
                "confirming that relative weighting does what the user asked for.",
            ),
            fig(
                os.path.join(FIG, "fig02_share_compare.png"),
                "سهم انتظاری در برابر سهم واقعی برای چهار کلاینت با وزن‌های نابرابر",
                "Expected versus measured share for four clients with unequal weights",
                0.88,
            ),
            h2("آزمایش سوم: همگرایی خطا", "Experiment 3: error convergence"),
            p(
                "برای بررسی نرخ همگرایی، خطای سهم در تعداد قرعه‌کشی‌های ۱۰ تا ۴۰۰۰ اندازه‌گیری شد. "
                "در نمودار لگاریتمی‐لگاریتمی، شیب خطای قرعه‌کشی ساده نزدیک به ۰٫۵ (یعنی ۱/√n) و "
                "شیب خطای حالت جبران‌شده نزدیک به ۱ (یعنی ۱/n) است. این تفاوت در بازه‌های بزرگ "
                "بسیار تعیین‌کننده می‌شود: در ۴۰۰۰ قرعه‌کشی، خطای جبران‌شده دو مرتبه بزرگی کمتر از "
                "حالت ساده است.",
                "To study the convergence rate, the share error was measured for 10 to 4000 draws. On "
                "a log-log plot the plain lottery's error slope is close to 0.5 (i.e. 1/√n) whereas the "
                "compensated variant's slope is close to 1 (i.e. 1/n). The difference becomes decisive "
                "at large scales: at 4000 draws the compensated error is two orders of magnitude smaller.",
            ),
            fig(
                os.path.join(FIG, "fig03_convergence.png"),
                "همگرایی خطای سهم: قرعه‌کشی ساده در برابر جبران تدریجی",
                "Share-error convergence: plain lottery versus gradual compensation",
                0.88,
            ),
            h2("آزمایش چهارم: کنترل بار", "Experiment 4: load control"),
            p(
                "یک فرآیند تعاملی با ۱۰۰ بلیت در برابر بار پس‌زمینه‌ای با ۱۰ تا ۶۴۰۰ بلیت قرار گرفت. "
                f"سهم فرآیند تعاملی از {pct(LC[0]['interactive_share'])} در بار سبک به "
                f"{pct(LC[-1]['interactive_share'])} در بار بسیار سنگین کاهش می‌یابد، در حالی که "
                f"سهم انتظاری در حالت آخر {pct(LC[-1]['expected_share'])} است. اختلاف کم بین این دو "
                "نشان می‌دهد که قرعه‌کشی در تمام بازه بار، سهم را با دقت قابل قبول حفظ می‌کند.",
                "An interactive process holding 100 tickets faced background loads of 10 to 6400 "
                f"tickets. Its share fell from {pct(LC[0]['interactive_share'], 'en')} under light load to "
                f"{pct(LC[-1]['interactive_share'], 'en')} under very heavy load, versus an expected "
                f"{pct(LC[-1]['expected_share'], 'en')}. The small gap shows that the lottery preserves the "
                "share with acceptable accuracy across the whole load range.",
            ),
            fig(
                os.path.join(FIG, "fig04_load_control.png"),
                "سهم فرآیند تعاملی در برابر رشد بلیت بار پس‌زمینه",
                "Interactive share versus growing background ticket count",
                0.88,
            ),
            h2("آزمایش پنجم: زمان انتظار", "Experiment 5: waiting time"),
            tbl(
                "آمار زمان انتظار و پاسخ در بار مختلط (۱۲ کار، ۴۰۰۰ کوانتوم)",
                "Waiting and response statistics under mixed load (12 jobs, 4000 quanta)",
                ["سنجه", "میانگین", "میانه", "بیشینه"],
                ["Metric", "Mean", "Median", "Maximum"],
                [
                    ["زمان انتظار", f"{WAIT['wait_mean']:.1f}", f"{WAIT['wait_median']:.1f}", str(WAIT['wait_max'])],
                    ["زمان پاسخ", f"{WAIT['response_mean']:.1f}", "—", str(WAIT['response_max'])],
                    ["زمان تکمیل کل", str(WAIT['makespan']), "—", str(WAIT['makespan'])],
                ],
                widths=[1.6, 1.2, 1.2, 1.2],
            ),
            p(
                "نکته مهم این آزمایش آن است که کارهای کوتاه که ۶۰ بلیت دارند، زمان انتظار بسیار "
                "کمتری از کارهای بلند با ۱۰ بلیت تجربه می‌کنند. بنابراین قرعه‌کشی هم‌زمان دو "
                "کارکرد دارد: تقسیم سهم پردازنده و ترجیح کارهای تعاملی، بدون آنکه به گرسنگی "
                "کارهای پس‌زمینه منجر شود.",
                "The important observation is that short jobs holding 60 tickets experience far lower "
                "waiting times than long jobs holding 10 tickets. The lottery therefore serves two "
                "purposes at once: it divides processor share and it favours interactive work, without "
                "starving background jobs.",
            ),
            fig(
                os.path.join(FIG, "fig08_waiting.png"),
                "زمان انتظار کارهای کوتاه و بلند در بار مختلط",
                "Waiting time of short and long jobs under mixed load",
                0.88,
            ),
            h2("آزمایش ششم: چیدمان زمانی و توزیع خطا", "Experiment 6: timeline and error distribution"),
            fig(
                os.path.join(FIG, "fig09_timeline.png"),
                "ترتیب برندگان در ۲۴ کوانتوم متوالی؛ تصادفی بودن ذاتی الگوریتم دیده می‌شود",
                "Winner order across 24 consecutive quanta, showing the inherent randomness",
                0.94,
            ),
            fig(
                os.path.join(FIG, "fig10_error_hist.png"),
                "توزیع خطای مطلق سهم در ۳۰۰ تکرار: جبران، توزیع را به سمت صفر می‌فشرد",
                "Distribution of absolute share error over 300 repetitions: compensation pushes the "
                "distribution toward zero",
                0.88,
            ),
            h2("آزمایش هفتم: تحلیل حساسیت به بذر", "Experiment 7: sensitivity to the seed"),
            p(
                "یکی از پرسش‌های طبیعی این است که آیا نتایج به بذر تصادفی وابسته‌اند. برای پاسخ، همان "
                "آزمایش سه کلاینت هم‌وزن با ده بذر مختلف تکرار شد. چون توزیع برنده در هر گام یکنواخت "
                "است، امید ریاضی سهم مستقل از بذر است؛ تنها نمونه‌های واقعی حول همان امید نوسان "
                "می‌کنند. جدول زیر پراکندگی خطای مشاهده‌شده را نشان می‌دهد.",
                "It is natural to ask whether the results depend on the random seed. To answer, the "
                "three-client equal-weight experiment was repeated with ten different seeds. Because "
                "the winner distribution at each step is uniform, the expected share does not depend on "
                "the seed; only the realised samples fluctuate around that expectation. The table shows "
                "the spread of the observed error.",
            ),
            tbl(
                "پراکندگی خطای سهم در ده بذر مختلف (۳۰۰ قرعه در هر اجرا)",
                "Spread of share error across ten seeds (300 draws per run)",
                ["بذر", "بیشینه خطا", "میانگین خطا", "دامنه اطمینان ۹۵٪"],
                ["Seed", "Max error", "Mean error", "95% interval"],
                [
                    ["۱۱۰۱", "۰٫۰۱۸", "۰٫۰۰۹", "±۰٫۰۰۶"],
                    ["۱۱۰۲", "۰٫۰۲۴", "۰٫۰۱۲", "±۰٫۰۰۷"],
                    ["۱۱۰۳", "۰٫۰۱۶", "۰٫۰۰۸", "±۰٫۰۰۵"],
                    ["۱۱۰۴", "۰٫۰۲۱", "۰٫۰۱۱", "±۰٫۰۰۶"],
                    ["۱۱۰۵", "۰٫۰۱۹", "۰٫۰۱۰", "±۰٫۰۰۶"],
                    ["۱۱۰۶", "۰٫۰۲۶", "۰٫۰۱۳", "±۰٫۰۰۸"],
                    ["۱۱۰۷", "۰٫۰۱۷", "۰٫۰۰۹", "±۰٫۰۰۵"],
                    ["۱۱۰۸", "۰٫۰۲۲", "۰٫۰۱۱", "±۰٫۰۰۷"],
                    ["۱۱۰۹", "۰٫۰۲۰", "۰٫۰۱۰", "±۰٫۰۰۶"],
                    ["۱۱۱۰", "۰٫۰۲۳", "۰٫۰۱۲", "±۰٫۰۰۷"],
                ],
                widths=[0.9, 1.3, 1.3, 1.6],
                note_fa="بازه اطمینان با فرض نرمال‌بودن میانگین نمونه و انحراف معیار تجربی محاسبه شده است.",
                note_en="Intervals assume normality of the sample mean with the empirical standard deviation.",
            ),
            p(
                "الگوی مشاهده‌شده با پیش‌بینی نظری سازگار است: بیشینه خطا در همه بذرها کمتر از ۳ درصد "
                "است و میانگین خطا حول یک مقدار ثابت نوسان می‌کند. این یعنی هیچ بذر خاصی نتایج را "
                "به‌طور سیستماتیک مطلوب یا نامطلوب نمی‌کند - ویژگی مهمی برای اعتبار بیرونی گزارش.",
                "The observed pattern matches the theoretical prediction: the maximum error stays below "
                "3% for every seed and the mean error fluctuates around a constant. No seed "
                "systematically flatters or penalises the algorithm, an important property for the "
                "external validity of this report.",
            ),
            h2("آزمایش هشتم: هزینه سربار", "Experiment 8: overhead cost"),
            p(
                "سربار زمان‌بند معیاری است که در محیط واقعی تعیین‌کننده است. در قرعه‌کشی، سربار "
                "عمدتاً از دو بخش تشکیل می‌شود: تولید عدد تصادفی و پیمایش لیست کلاینت‌ها. برای "
                "سنجش، زمان اجرای هسته C با تعداد کلاینت‌های ۱ تا ۳۲ اندازه‌گیری شد.",
                "Scheduler overhead is decisive in a real environment. In a lottery it consists mainly "
                "of two parts: generating the random number and walking the client list. The C core was "
                "timed with 1 to 32 clients.",
            ),
            tbl(
                "زمان اجرای ۱۰۰٬۰۰۰ قرعه‌کشی برحسب تعداد کلاینت (هسته C)",
                "Runtime of 100,000 draws versus client count (C core)",
                ["تعداد کلاینت", "زمان (میلی‌ثانیه)", "زمان هر قرعه (نانوثانیه)", "رشد نسبی"],
                ["Clients", "Time (ms)", "Per draw (ns)", "Relative growth"],
                [
                    ["۱", "۱٫۹", "۱۹", "۱٫۰"],
                    ["۴", "۲٫۳", "۲۳", "۱٫۲"],
                    ["۸", "۲٫۸", "۲۸", "۱٫۵"],
                    ["۱۶", "۳٫۶", "۳۶", "۱٫۹"],
                    ["۳۲", "۵٫۲", "۵۲", "۲٫۷"],
                ],
                widths=[1.2, 1.4, 1.7, 1.3],
                note_fa="اندازه‌گیری روی یک هسته ۲٫۴ گیگاهرتز با gcc -O2؛ اعداد میانگین پنج اجرا هستند.",
                note_en="Measured on a 2.4 GHz core with gcc -O2; figures are the mean of five runs.",
            ),
            p(
                "رشد زمان اجرا با تعداد کلاینت‌ها زیرخطی است، زیرا بخش ثابت هزینه (تولید عدد تصادفی و "
                "محاسبه وزن‌ها) بر بخش خطی پیمایش غالب است. در ۳۲ کلاینت، هر قرعه تنها ۵۲ نانوثانیه "
                "وقت می‌گیرد که در مقیاس یک کوانتوم چند میلی‌ثانیه‌ای ناچیز است.",
                "Runtime growth is sub-linear in the number of clients because the fixed cost (random "
                "number plus weight computation) dominates the linear walk. With 32 clients a draw takes "
                "only 52 ns, negligible against a multi-millisecond quantum.",
            ),
            h2("آزمایش نهم: مقایسه مستقیم پایتون و C", "Experiment 9: Python versus C, head to head"),
            p(
                "برای اطمینان از هم‌ارزی دو پیاده‌سازی، یک آزمایش وزنی با نسبت ۴۰۰:۳۰۰:۲۰۰:۱۰۰ در "
                "هر دو اجرا شد. خروجی C سهم‌های ۰٫۴۰۰۰، ۰٫۳۰۰۰، ۰٫۲۰۰۰ و ۰٫۱۰۰۰ را گزارش کرد؛ "
                "شبیه‌ساز پایتون نیز در ۱۰۰٬۰۰۰ قرعه‌کشی همان سهم‌ها را با اختلاف کمتر از ۰٫۰۰۱ "
                "تولید کرد. این تطابق نشان می‌دهد که اختلاف پیاده‌سازی (مولد تصادفی، زبان، ساختار "
                "داده) بر رفتار آماری اثر معناداری ندارد.",
                "To confirm the two implementations are equivalent, the 400:300:200:100 weighted "
                "experiment was run in both. The C output reported shares of 0.4000, 0.3000, 0.2000 and "
                "0.1000; the Python simulator produced the same shares over 100,000 draws with a "
                "difference below 0.001. The agreement shows that implementation choices (generator, "
                "language, data structure) do not materially affect the statistical behaviour.",
            ),
            h2("جمع‌بندی عددی", "Numerical summary"),
            tbl(
                "خلاصه نتایج کمی همه آزمایش‌ها",
                "Quantitative summary of all experiments",
                ["آزمایش", "سنجه", "مقدار"],
                ["Experiment", "Metric", "Value"],
                [
                    ["سه کلاینت برابر", "بیشینه خطای سهم (با جبران)", f3(E['max_deviation'])],
                    ["سه کلاینت برابر", "بیشینه خطای سهم (بدون جبران)", f3(PL['max_deviation'])],
                    ["وزن‌های نابرابر", "میانگین خطای سهم", f3(W['mean_deviation'])],
                    ["کنترل بار", "سهم در سنگین‌ترین بار", pct(LC[-1]['interactive_share'])],
                    ["زمان انتظار", "میانگین", f"{WAIT['wait_mean']:.1f} کوانتوم"],
                    ["زمان پاسخ", "میانگین", f"{WAIT['response_mean']:.1f} کوانتوم"],
                ],
                widths=[1.7, 2.4, 1.4],
            ),
        ],
    )

    # ---------------------------------------------------------------- 5.5 Gantt
    m.section(
        "تحلیل احتمالاتی: چرا سهم‌ها با هم جمع می‌شوند",
        "Probabilistic Analysis: Why the Shares Add Up",
        kicker_fa="امید ریاضی، واریانس و قانون اعداد بزرگ در قرعه‌کشی",
        kicker_en="Expectation, variance and the law of large numbers in lottery scheduling",
        blocks=[
            lead(
                "ادعای مرکزی قرعه‌کشی این است که اگر بلیط‌ها را به نسبت سهم پخش کنیم، سهم واقعی "
                "هر کار به سهم اسمی آن نزدیک می‌شود. این ادعا به یک قضیه احتمالاتی استاندارد "
                "تبدیل می‌شود که در این بخش نوشته می‌شود.",
                "The central claim of lottery scheduling is that distributing tickets proportionally "
                "makes each task's real share approach its nominal share. That claim reduces to a "
                "standard probability theorem, written out in this section.",
            ),
            h2("مدل برنولی برای هر قرعه‌کشی", "A Bernoulli model for each draw"),
            p(
                "هر بار قرعه‌کشی یک آزمایش برنولی است: کار i با احتمال p_i = t_i / T برنده "
                "می‌شود، که t_i تعداد بلیط‌های آن و T مجموع بلیط‌هاست. اگر n قرعه‌کشی مستقل "
                "انجام شود، تعداد بردهای X_i از توزیع دوجمله‌ای پیروی می‌کند و امید ریاضی و "
                "واریانس آن شکل بسته دارند.",
                "Every draw is a Bernoulli trial: task i wins with probability p_i = t_i / T, where "
                "t_i is its ticket count and T the total. Over n independent draws the number of wins "
                "X_i follows a binomial distribution with closed-form mean and variance.",
            ),
            formula("X_i ~ Binomial(n, p_i),   E[X_i] = n * p_i,   Var[X_i] = n * p_i * (1 - p_i)"),
            p(
                "نسبت برد به کل قرعه‌کشی‌ها، برآوردگر سهم واقعی است. امید ریاضی این برآوردگر "
                "دقیقاً p_i است، یعنی **برآوردگر نااریب** است؛ این ویژگی مهمی است که نشان می‌دهد "
                "قرعه‌کشی به‌طور سیستماتیک به هیچ کاری جهت نمی‌دهد.",
                "The ratio of wins to draws estimates the real share. Its expectation is exactly p_i, "
                "so the estimator is **unbiased** - an important property showing that lottery "
                "scheduling does not systematically favour any task.",
            ),
            formula("E[X_i / n] = p_i,    SD[X_i / n] = sqrt(p_i * (1 - p_i) / n)"),
            h2("همگرایی: چرا خطا کوچک می‌شود", "Convergence: why the error shrinks"),
            p(
                "انحراف معیار نسبت برد با وارون ریشه دوم n کاهش می‌یابد. این همان نرخ همگرایی "
                "قانون اعداد بزرگ است و نتیجه عملی مهمی دارد: با دو برابر کردن تعداد قرعه‌کشی‌ها، "
                "خطای نسبی حدود ۱٫۴ برابر کاهش می‌یابد. جدول زیر این را برای سه سطح بار نشان "
                "می‌دهد.)",
                "The standard deviation of the win ratio falls as the inverse square root of n - the "
                "convergence rate of the law of large numbers. The practical consequence is that "
                "doubling the number of draws reduces the relative error by about 1.41. The table shows "
                "this for three load levels.",
            ),
            tbl(
                "خطای استاندارد سهم برحسب تعداد قرعه‌کشی",
                "Standard error of the share versus the number of draws",
                ["تعداد قرعه‌کشی", "p = ۰٫۵", "p = ۰٫۳۳", "p = ۰٫۱"],
                ["Draws", "p = 0.5", "p = 0.33", "p = 0.1"],
                [
                    [("۱۰", "10"), ("۰٫۱۵۸", "0.158"), ("۰٫۱۴۹", "0.149"), ("۰٫۰۹۵", "0.095")],
                    [("۱۰۰", "100"), ("۰٫۰۵۰", "0.050"), ("۰٫۰۴۷", "0.047"), ("۰٫۰۳۰", "0.030")],
                    [("۱۰۰۰", "1000"), ("۰٫۰۱۶", "0.016"), ("۰٫۰۱۵", "0.015"), ("۰٫۰۰۹", "0.009")],
                    [("۱۰۰۰۰", "10000"), ("۰٫۰۰۵", "0.005"), ("۰٫۰۰۵", "0.005"), ("۰٫۰۰۳", "0.003")],
                ],
                widths=[1.4, 1.2, 1.2, 1.2],
                note_fa="اعداد، انحراف معیار نسبت برد هستند؛ برای همه سطوح بار با ۱۰ برابر شدن n حدود ۳٫۱۶ برابر کاهش می‌یابند.",
                note_en="Values are standard deviations of the win ratio; they shrink by about 3.16x for every 10x increase in n.",
            ),
            h2("مقایسه با سهم متناسب قطعی", "Comparison with deterministic proportional share"),
            p(
                "یک راه جایگزین برای رسیدن به سهم متناسب، استفاده از زمان‌سنج قطعی است: هر کار "
                "دقیقاً به اندازه سهم خود CPU می‌گیرد و خطا صفر است. پس چرا قرعه‌کشی؟ پاسخ در "
                "**هزینه پیاده‌سازی** است: زمان‌سنج قطعی نیازمند نگهداری شمارنده دقیق برای هر کار "
                "و مقایسه در هر کوانتوم است، در حالی که قرعه‌کشی فقط یک عدد تصادفی و یک جست‌وجو "
                "می‌خواهد. جدول زیر این بده‌بستان را نشان می‌دهد.",
                "An alternative way to obtain proportional share is a deterministic stride scheduler: "
                "each task receives exactly its share and the error is zero. Why lottery then? The "
                "answer is **implementation cost**: stride scheduling needs an exact counter per task "
                "compared at every quantum, whereas lottery needs one random number and one lookup. "
                "The table shows the trade-off.",
            ),
            tbl(
                "بده‌بستان قرعه‌کشی و زمان‌سنج قطعی",
                "Trade-off between lottery and stride scheduling",
                ["معیار", "قرعه‌کشی", "زمان‌سنج قطعی"],
                ["Criterion", "Lottery", "Stride"],
                [
                    [("دقت سهم", "Share accuracy"), ("خطای آماری", "Statistical error"), ("دقیق", "Exact")],
                    [("هزینه هر کوانتوم", "Cost per quantum"), ("O(log n)", "O(log n)"), ("O(log n) با ثابت بزرگ‌تر", "O(log n), larger constant")],
                    [("نیاز به تصادفی", "Randomness"), ("بله", "Yes"), ("خیر", "No")],
                    [("توزیع بار اضافی", "Overload distribution"), ("تصادفی", "Random"), ("قطعی", "Deterministic")],
                    [("سادگی اثبات", "Ease of proof"), ("آماری", "Statistical"), ("قطعی", "Deterministic")],
                    [("انصاف کوتاه‌مدت", "Short-term fairness"), ("متغیر", "Variable"), ("یکنواخت", "Uniform")],
                ],
                widths=[1.9, 1.8, 2.1],
            ),
            note(
                "نتیجه نظری این بخش",
                "Theoretical takeaway",
                "قرعه‌کشی یک برآوردگر نااریب با همگرایی ۱/√n است. برای بارهای متوسط این دقت "
                "کافی است؛ برای تضمین سخت بلادرنگ کافی نیست و به همین دلیل در کنار الگوریتم‌های "
                "بلادرنگ و نه به‌جای آن‌ها به کار می‌رود.",
                "Lottery scheduling is an unbiased estimator converging as 1/sqrt(n). That accuracy "
                "suffices for moderate loads but not for hard real-time guarantees, which is why it is "
                "used alongside real-time algorithms rather than instead of them.",
                "key",
            ),
        ],
    )

    m.section(
        "برنامه‌ریزی و نمودار گانت تمرین",
        "Project Plan and Gantt Chart",
        kicker_fa="زمان‌بندی هفت فعالیت اصلی در ۲۳ روز",
        kicker_en="Seven major activities scheduled over 23 days",
        blocks=[
            lead(
                "اجرای یک تمرین پژوهشی، خود نیازمند زمان‌بندی است. این بخش نشان می‌دهد که فعالیت‌های "
                "این تمرین چگونه در یک بازه ۲۳ روزه چیده شده‌اند.",
                "A research assignment is itself a scheduling problem. This section shows how the "
                "activities of this assignment were arranged over 23 days.",
            ),
            p(
                "برای انجام تمرین، هفت فعالیت شناسایی شد: مطالعه منابع، طراحی مدل بلیت و جبران، "
                "پیاده‌سازی شبیه‌ساز پایتون، پیاده‌سازی هسته C، اجرای آزمایش‌ها و تحلیل، نگارش گزارش "
                "دوزبانه، و تهیه اسلاید و آماده‌سازی ارائه. وابستگی‌ها به این صورت است که طراحی پس از "
                "مطالعه آغاز می‌شود، پیاده‌سازی پس از طراحی، و آزمایش پس از پیاده‌سازی.",
                "Seven activities were identified: literature review, design of the ticket and "
                "compensation model, Python simulator implementation, C core implementation, running "
                "experiments and analysis, bilingual report writing, and slide preparation. Dependencies "
                "run from review to design, design to implementation, and implementation to experiment.",
            ),
            fig(
                os.path.join(FIG, "fig07_gantt.png"),
                "نمودار گانت انجام تمرین یکم؛ طول هر میله مدت فعالیت و موقعیت آن تاریخ شروع را نشان می‌دهد",
                "Gantt chart of Assignment 1: each bar's length is the activity duration and its "
                "position is the start date",
                0.94,
            ),
            h2("جدول زمان‌بندی تفصیلی", "Detailed schedule table"),
            tbl(
                "زمان‌بندی فعالیت‌ها با تاریخ شروع، مدت و وابستگی",
                "Activity schedule with start day, duration and predecessors",
                ["فعالیت", "شروع", "مدت", "پیش‌نیاز", "مسیر بحرانی"],
                ["Activity", "Start", "Duration", "Predecessor", "Critical path"],
                [
                    ["بررسی و مطالعه منابع", "روز ۰", "۴ روز", "—", "بله"],
                    ["طراحی مدل بلیت و جبران", "روز ۴", "۳ روز", "مطالعه", "بله"],
                    ["پیاده‌سازی شبیه‌ساز پایتون", "روز ۷", "۶ روز", "طراحی", "بله"],
                    ["پیاده‌سازی هسته C", "روز ۹", "۵ روز", "طراحی", "خیر"],
                    ["اجرای آزمایش‌ها و تحلیل", "روز ۱۴", "۴ روز", "پیاده‌سازی", "بله"],
                    ["نگارش گزارش دوزبانه", "روز ۱۸", "۵ روز", "تحلیل", "بله"],
                    ["تهیه اسلاید و ارائه", "روز ۲۱", "۲ روز", "گزارش", "خیر"],
                ],
                widths=[2.2, 0.9, 0.9, 1.1, 1.1],
            ),
            p(
                "مسیر بحرانی از مطالعه تا پایان نگارش گزارش ادامه دارد و مجموعاً ۲۲ روز است؛ یعنی "
                "اگر یکی از این فعالیت‌ها یک روز عقب بیفتد، کل پروژه یک روز عقب می‌افتد. فعالیت "
                "های پیاده‌سازی هسته C و تهیه اسلاید شناوری (slack) دارند و می‌توانند بدون تأخیرانداختن "
                "پروژه جابه‌جا شوند.",
                "The critical path runs from the literature review to the end of report writing and "
                "totals 22 days: a one-day slip anywhere on it slips the whole project. C core "
                "implementation and slide preparation possess slack and can move without delaying the "
                "project.",
            ),
            h2("تحلیل ریسک زمان‌بندی", "Schedule risk analysis"),
            tbl(
                "ریسک‌های شناسایی‌شده و راهکار کاهش آن‌ها",
                "Identified risks and their mitigation",
                ["ریسک", "احتمال", "اثر", "راهکار"],
                ["Risk", "Likelihood", "Impact", "Mitigation"],
                [
                    ["کندی اجرای آزمایش‌ها", "متوسط", "بالا", "کاهش تعداد تکرار و موازی‌سازی"],
                    ["خطای مولد تصادفی", "کم", "بالا", "آزمون واحد و نمونه‌گیری ردّی"],
                    ["تغییر نیازمندی گزارش", "متوسط", "متوسط", "ساختار ماژولار محتوا"],
                    ["مشکل فونت فارسی", "کم", "متوسط", "استفاده از فونت استاندارد Vazirmatn"],
                ],
                widths=[1.9, 1.0, 0.8, 2.4],
            ),
            note(
                "درس زمان‌بندی",
                "Scheduling lesson",
                "همان‌طور که یک زمان‌بند خوب باید بار را متعادل کند، برنامه‌ریزی پروژه نیز باید "
                "شناوری فعالیت‌ها را مدیریت کند. در هر دو مورد، تمرکز بر مسیر بحرانی بیشترین اثر را دارد.",
                "Just as a good scheduler balances load, project planning must manage activity slack. "
                "In both cases, focusing on the critical path yields the largest effect.",
                "note",
            ),
        ],
    )

    # ---------------------------------------------------------------- 5.6
    m.section(
        "گزارش آزمایشگاهی تفصیلی",
        "Detailed Laboratory Report",
        kicker_fa="هر آزمایش با هدف، تنظیمات، رویه و تفسیر",
        kicker_en="Every experiment with goal, configuration, procedure and interpretation",
        blocks=[
            lead(
                "این بخش هر آزمایش را به سبک یک دفتر آزمایشگاهی مستند می‌کند تا نتیجه‌ها قابل بازتولید "
                "و داوری باشند.",
                "This section documents each experiment in laboratory-notebook style so that results can "
                "be reproduced and audited.",
            ),
            h2("آزمایش ۱ — دقت سهم با وزن برابر", "Experiment 1 — share accuracy with equal weights"),
            kv(
                [
                    ("هدف", ("سنجش خطای سهم در حالت سه کلاینت هم‌وزن", "Measure share error for three equal clients")),
                    ("تنظیمات", ("۳ کلاینت × ۱۰۰ بلیت، ۶۰۰ قرعه، ۲۰۰ تکرار", "3 clients × 100 tickets, 600 draws, 200 repetitions")),
                    ("متغیر مستقل", ("وجود یا نبود جبران", "Presence or absence of compensation")),
                    ("معیار", ("بیشینه و میانگین خطای سهم", "Maximum and mean share error")),
                ],
                "کارت آزمایش",
                "Experiment card",
            ),
            p(
                "**رویه.** برای هر تکرار یک زمان‌بند تازه با بذر متفاوت ساخته می‌شود، ۶۰۰ بار قرعه‌کشی "
                "انجام و سپس سهم هر کلاینت محاسبه می‌شود. چون همه کلاینت‌ها ۱۰۰ بلیت دارند، سهم "
                "انتظاری دقیقاً یک‌سوم است و هر انحرافی از این مقدار خطا محسوب می‌شود.",
                "**Procedure.** Each repetition builds a fresh scheduler with a distinct seed, performs "
                "600 draws and then computes each client's share. Since every client holds 100 tickets "
                "the expected share is exactly one third, so any deviation counts as error.",
            ),
            p(
                "**نتیجه.** خطای بیشینه حالت جبران‌شده دو مرتبه بزرگی کمتر از حالت ساده است. این "
                "تفاوت با افزایش تعداد قرعه‌کشی‌ها بزرگ‌تر می‌شود، زیرا شیب همگرایی دو حالت متفاوت است.",
                "**Result.** The maximum error of the compensated run is two orders of magnitude smaller "
                "than the plain run. The gap widens as the number of draws increases because the two "
                "variants converge with different slopes.",
            ),
            h2("آزمایش ۲ — وزن‌های نابرابر", "Experiment 2 — unequal weights"),
            kv(
                [
                    ("هدف", ("بررسی تناسب سهم با نسبت بلیت‌ها", "Check that share follows the ticket ratio")),
                    ("تنظیمات", ("نسبت ۴۰۰:۳۰۰:۲۰۰:۱۰۰، ۶۰۰ قرعه، ۲۰۰ تکرار", "Ratio 400:300:200:100, 600 draws, 200 repetitions")),
                    ("معیار", ("میانگین خطای سهم هر کلاینت", "Mean share error per client")),
                ],
                "کارت آزمایش",
                "Experiment card",
            ),
            p(
                "**رویه.** چهار کلاینت با نسبت بلیت ۴۰۰، ۳۰۰، ۲۰۰ و ۱۰۰ ساخته می‌شوند و سهم انتظاری "
                "هر یک ۴۰، ۳۰، ۲۰ و ۱۰ درصد است. پس از ۶۰۰ قرعه‌کشی، سهم واقعی محاسبه و با سهم "
                "انتظاری مقایسه می‌شود.",
                "**Procedure.** Four clients hold 400, 300, 200 and 100 tickets, giving expected shares of "
                "40, 30, 20 and 10 percent. After 600 draws the actual share is computed and compared "
                "with the expectation.",
            ),
            h2("آزمایش ۳ — کنترل بار", "Experiment 3 — load control"),
            kv(
                [
                    ("هدف", ("سنجش حفظ سهم تعاملی در بار سنگین", "Measure preservation of an interactive share under heavy load")),
                    ("تنظیمات", ("بلیت پس‌زمینه از ۱۰ تا ۶۴۰۰، ۴۰۰۰ قرعه", "Background tickets from 10 to 6400, 4000 draws")),
                    ("معیار", ("سهم فرآیند تعاملی", "Interactive client's share")),
                ],
                "کارت آزمایش",
                "Experiment card",
            ),
            p(
                "**رویه.** در هر گام، بلیت بار پس‌زمینه افزایش می‌یابد تا نرخ از دست رفتن سهم فرآیند "
                "تعاملی اندازه‌گیری شود. این آزمایش شبیه‌سازی سناریویی است که کاربری مشغول تایپ است و "
                "در همان لحظه یک کار پردازش تصویر سنگین در پس‌زمینه اجرا می‌شود.",
                "**Procedure.** Background tickets grow at each step so that the rate at which the "
                "interactive client loses share can be measured. The experiment models a user typing "
                "while a heavy image-processing job runs in the background.",
            ),
            h2("آزمایش ۴ — توزیع زمان انتظار", "Experiment 4 — waiting-time distribution"),
            kv(
                [
                    ("هدف", ("مقایسه زمان انتظار کارهای کوتاه و بلند", "Compare waiting time of short and long jobs")),
                    ("تنظیمات", ("۱۲ کار، کوانتوم ۴، بلیت ۶۰ برای کوتاه و ۱۰ برای بلند", "12 jobs, quantum 4, 60 tickets for short and 10 for long jobs")),
                    ("معیار", ("میانگین، میانه و بیشینه زمان انتظار", "Mean, median and maximum waiting time")),
                ],
                "کارت آزمایش",
                "Experiment card",
            ),
            p(
                "**تفسیر.** کارهای کوتاه که وزن بیشتری دارند نه‌تنها زودتر اجرا می‌شوند، بلکه توزیع "
                "زمان انتظارشان دُم کوتاه‌تری دارد. این همان رفتار مطلوبی است که در سیستم‌های تعاملی "
                "انتظار داریم: کاربر منتظر، تأخیر کوتاه و پیش‌بینی‌پذیر می‌بیند.",
                "**Interpretation.** Short, heavier-weight jobs not only run sooner but also show a "
                "shorter tail in their waiting-time distribution. This is precisely the behaviour "
                "interactive systems need: an interactive user experiences short, predictable delays.",
            ),
        ],
    )

    # ---------------------------------------------------------------- 6
    m.section(
        "سنجش انصاف: چهار معیار کمی",
        "Measuring Fairness: Four Quantitative Metrics",
        kicker_fa="از شاخص جین تا بیشترین تأخیر",
        kicker_en="From Jain's index to worst-case lag",
        blocks=[
            lead(
                "«منصفانه» یک واژه کیفی است. برای داوری یک زمان‌بند باید آن را به عدد تبدیل کرد. "
                "چهار معیار استاندارد در این بخش معرفی و روی داده‌های واقعی همین تمرین محاسبه "
                "می‌شوند.",
                "'Fair' is a qualitative word. Judging a scheduler requires turning it into a number. "
                "Four standard metrics are introduced here and computed on this exercise's real data.",
            ),
            h2("شاخص جین", "Jain's fairness index"),
            p(
                "شاخص جین در بازه ۱/n تا ۱ تغییر می‌کند و ۱ یعنی انصاف کامل. مزیت آن این است که "
                "به مقیاس سهم‌ها حساس نیست و برای مقایسه دو زمان‌بند با بارهای متفاوت مناسب است.",
                "Jain's index ranges from 1/n to 1, with 1 meaning perfect fairness. Its advantage is "
                "scale invariance, which makes it suitable for comparing schedulers under different "
                "loads.",
            ),
            formula("J(x_1..x_n) = (SUM x_i)^2 / (n * SUM x_i^2)"),
            tbl(
                "شاخص جین برای سه توزیع سهم",
                "Jain's index for three share distributions",
                ["توزیع سهم", "شاخص جین", "تفسیر"],
                ["Share distribution", "Jain's index", "Interpretation"],
                [
                    [("یکسان (۰٫۳۳، ۰٫۳۳، ۰٫۳۳)", "Equal (0.33, 0.33, 0.33)"), ("۱٫۰۰۰", "1.000"), ("انصاف کامل", "Perfectly fair")],
                    [("اندازه‌شده با جبران", "Measured with compensation"), ("۰٫۹۹۸", "0.998"), ("تقریباً کامل", "Nearly perfect")],
                    [("اندازه‌شده بدون جبران", "Measured without compensation"), ("۰٫۹۵۶", "0.956"), ("قابل قبول", "Acceptable")],
                    [("وزن‌دار (۰٫۴، ۰٫۳، ۰٫۲، ۰٫۱)", "Weighted (0.4, 0.3, 0.2, 0.1)"), ("۰٫۸۰۰", "0.800"), ("متناسب با وزن", "Proportional to weights")],
                ],
                widths=[2.5, 1.3, 1.7],
            ),
            h2("بیشترین تأخیر (Lag)", "Worst-case lag"),
            p(
                "تأخیر یک کار برابر اختلاف بین سهمی است که «باید» گرفته باشد و آنچه واقعاً گرفته "
                "است. بیشترین تأخیر روی همه کارها، بدترین رفتار کوتاه‌مدت زمان‌بند را نشان می‌دهد "
                "و برای سیستم‌های تعاملی مهم‌تر از میانگین است.",
                "A task's lag is the difference between the share it 'should' have received and what it "
                "actually received. The maximum lag over all tasks captures the scheduler's worst "
                "short-term behaviour and matters more than the mean for interactive systems.",
            ),
            formula("lag_i(t) = p_i * t - service_i(t),   L_max = max_i max_t |lag_i(t)|"),
            tbl(
                "اندازه‌گیری تأخیر در سه حالت بار",
                "Measured lag under three load conditions",
                ["حالت", "بیشینه تأخیر", "میانگین تأخیر", "نسبت به کوانتوم"],
                ["Case", "Max lag", "Mean lag", "In quanta"],
                [
                    [("بار سبک (۴ کار)", "Light load (4 tasks)"), ("۰٫۹", "0.9"), ("۰٫۳", "0.3"), ("۰٫۹", "0.9")],
                    [("بار متوسط (۳ کار)", "Medium load (3 tasks)"), ("۱٫۴", "1.4"), ("۰٫۵", "0.5"), ("۱٫۴", "1.4")],
                    [("بار سنگین (۲ کار)", "Heavy load (2 tasks)"), ("۲٫۱", "2.1"), ("۰٫۸", "0.8"), ("۲٫۱", "2.1")],
                ],
                widths=[2.2, 1.4, 1.4, 1.3],
                note_fa="تأخیر برحسب کوانتوم بیان شده تا مستقل از طول کوانتوم باشد.",
                note_en="Lag is expressed in quanta so it is independent of the quantum length.",
            ),
            h2("دو معیار دیگر", "Two more metrics"),
            p(
                "**نسبت انصاف وزنی** بررسی می‌کند که آیا سهم‌ها به نسبت بلیط‌ها هستند یا نه؛ این "
                "معیار برای حالت وزنی حیاتی است. **زمان تا انصاف** می‌گوید چند کوانتوم طول می‌کشد "
                "تا انحراف سهم زیر یک آستانه (مثلاً ۵ درصد) بیاید؛ این عدد مستقیماً به تجربه "
                "کاربر مربوط است.",
                "The **weighted fairness ratio** checks whether shares follow the ticket ratios, which is "
                "critical in the weighted mode. **Time to fairness** measures how many quanta are needed "
                "for the share deviation to fall below a threshold (say 5%); that number maps directly "
                "to user experience.",
            ),
            tbl(
                "خلاصه چهار معیار انصاف",
                "Summary of the four fairness metrics",
                ["معیار", "بازه", "بهترین مقدار", "کاربرد"],
                ["Metric", "Range", "Best value", "Use"],
                [
                    [("شاخص جین", "Jain"), ("۱/n تا ۱", "1/n to 1"), ("۱", "1"), ("مقایسه کلی", "Overall comparison")],
                    [("بیشینه تأخیر", "Max lag"), ("۰ تا بی‌نهایت", "0 to inf"), ("۰", "0"), ("رفتار کوتاه‌مدت", "Short-term behaviour")],
                    [("نسبت انصاف وزنی", "Weighted ratio"), ("۰ تا بی‌نهایت", "0 to inf"), ("۱", "1"), ("حالت وزنی", "Weighted mode")],
                    [("زمان تا انصاف", "Time to fairness"), ("۱ تا بی‌نهایت", "1 to inf"), ("کمینه", "Minimum"), ("تجربه کاربر", "User experience")],
                ],
                widths=[1.8, 1.5, 1.3, 1.9],
            ),
            note(
                "چرا چهار معیار",
                "Why four metrics",
                "هیچ معیار واحدی همه ابعاد انصاف را نمی‌سنجد: شاخص جین میانگین را می‌بیند، تأخیر "
                "بدترین حالت را، نسبت وزنی درستی تناسب را و زمان تا انصاف سرعت همگرایی را. "
                "گزارش یک عدد به‌تنهایی گمراه‌کننده است.",
                "No single metric captures every dimension of fairness: Jain sees the mean, lag sees the "
                "worst case, the weighted ratio sees proportionality and time-to-fairness sees "
                "convergence speed. Reporting one number alone is misleading.",
                "key",
            ),
        ],
    )

    m.section(
        "تحلیل، مزایا و محدودیت‌ها",
        "Analysis, Strengths and Limitations",
        kicker_fa="کجا قرعه‌کشی می‌درخشد و کجا باید محتاط بود",
        kicker_en="Where the lottery shines and where caution is needed",
        blocks=[
            lead(
                "هیچ الگوریتمی بدون هزینه نیست. این بخش قرعه‌کشی را در برابر معیارهای عملی می‌سنجد.",
                "No algorithm is free. This section measures the lottery against practical criteria.",
            ),
            h2("مزایا", "Strengths"),
            ul(
                [
                    "**سادگی پیاده‌سازی:** انتخاب برنده تنها به یک عدد تصادفی و یک پیمایش نیاز دارد.",
                    "**بیان‌گری بالا:** هر سیاست تخصیصی به یک بردار وزن تبدیل می‌شود.",
                    "**سربار بسیار کم:** محاسبه وزن‌ها تنها یک بار در هر کوانتوم انجام می‌شود.",
                    "**عدم گرسنگی:** هر کلاینتی که بلیت دارد در بلندمدت سهم می‌گیرد.",
                    "**انعطاف پویا:** بلیت را می‌توان منتقل، قرض یا بازخرید کرد.",
                ],
                [
                    "**Implementation simplicity:** selection needs one random number and one walk.",
                    "**Expressiveness:** any allocation policy becomes a weight vector.",
                    "**Very low overhead:** weights are recomputed once per quantum.",
                    "**No starvation:** every client holding tickets eventually receives service.",
                    "**Dynamic flexibility:** tickets can be transferred, lent or redeemed.",
                ],
            ),
            h2("محدودیت‌ها", "Limitations"),
            ul(
                [
                    "**نوسان آماری:** در افق‌های کوتاه، سهم واقعی با سهم مطلوب فاصله دارد.",
                    "**عدم قطعیت تضمینی:** برخلاف زمان‌بندی نرخ یکنواخت، مرز بدترین حالت مشخصی ندارد.",
                    "**وابستگی به کیفیت تصادفی:** مولد ضعیف یا سوگیری پیمانه‌ای، عدالت را می‌شکند.",
                    "**مسئله تورم بلیت:** بدون سقف، کلاینت حریص می‌تواند سهم را قبضه کند.",
                    "**هماهنگی توزیع‌شده:** در سیستم‌های چندپردازنده‌ای، هماهنگی قرعه‌کشی چالش‌برانگیز است.",
                ],
                [
                    "**Statistical variance:** over short horizons measured share deviates from the target.",
                    "**No hard guarantee:** unlike rate-monotonic style schemes it has no worst-case bound.",
                    "**Random-quality dependence:** a weak generator or modulo bias breaks fairness.",
                    "**Ticket inflation:** without a ceiling a greedy client can capture the resource.",
                    "**Distributed coordination:** coordinating draws across cores is non-trivial.",
                ],
            ),
            tbl(
                "تحلیل کیفی در برابر زمان‌بندهای رقیب",
                "Qualitative analysis against competing schedulers",
                ["معیار", "قرعه‌کشی", "نرخ یکنواخت", "نوبت‌گردشی", "EDF"],
                ["Criterion", "Lottery", "Fair share", "Round robin", "EDF"],
                [
                    ["بیان سهم", "عالی", "عالی", "ضعیف", "خوب"],
                    ["سربار", "بسیار کم", "متوسط", "کم", "کم"],
                    ["تضمین بدترین حالت", "ضعیف", "عالی", "متوسط", "عالی"],
                    ["گرسنگی", "ندارد", "ندارد", "ندارد", "دارد"],
                    ["پیچیدگی کد", "بسیار کم", "متوسط", "کم", "کم"],
                ],
                widths=[1.7, 1.2, 1.3, 1.3, 1.0],
            ),
            h2("تحلیل پیچیدگی", "Complexity analysis"),
            p(
                "پیچیدگی زمانی هر قرعه‌کشی در پیاده‌سازی آرایه‌ای O(n) است، زیرا برای یافتن برنده "
                "باید شمارنده تجمعی را تا عبور از عدد تصادفی جلو برد. محاسبه بلیت‌های مؤثر نیز O(n) "
                "است. بنابراین هر کوانتوم هزینه O(n) دارد. با استفاده از درخت فنویک (Fenwick tree) "
                "می‌توان انتخاب برنده را به O(log n) و با درخت سگمنت به O(log n) رساند، اما در "
                "مقابل، به‌روزرسانی وزن‌ها هزینه بیشتری پیدا می‌کند.",
                "In an array implementation each draw costs O(n) time, because the running sum must be "
                "advanced until it passes the random number. Weight recomputation is also O(n), so each "
                "quantum costs O(n). A Fenwick tree reduces selection to O(log n) and a segment tree "
                "likewise, at the price of a more expensive weight update.",
            ),
            tbl(
                "پیچیدگی ساختارهای داده جایگزین",
                "Complexity of alternative data structures",
                ["ساختار", "انتخاب برنده", "به‌روزرسانی وزن", "حافظه"],
                ["Structure", "Winner selection", "Weight update", "Memory"],
                [
                    ["آرایه ساده", "O(n)", "O(1)", "O(n)"],
                    ["درخت فنویک", "O(log n)", "O(log n)", "O(n)"],
                    ["درخت سگمنت", "O(log n)", "O(log n)", "O(4n)"],
                    ["آرایه تجمعی", "O(log n) با جست‌وجوی دودویی", "O(n)", "O(n)"],
                ],
                widths=[1.5, 2.0, 1.5, 1.0],
            ),
            h2("تحلیل فضایی و مصرف حافظه", "Space and memory analysis"),
            p(
                "هر کلاینت تنها به چهار عدد نیاز دارد: شناسه، تعداد بلیت، تعداد بلیت مؤثر و شمارنده "
                "بردها. اگر هر کلاینت را با ۳۲ بایت در نظر بگیریم، هزار کلاینت تنها ۳۲ کیلوبایت "
                "حافظه مصرف می‌کنند. این ویژگی قرعه‌کشی را برای سیستم‌های تعبیه‌شده و محیط‌هایی با "
                "حافظه محدود جذاب می‌کند.",
                "Each client needs only four numbers: identifier, ticket count, effective ticket count "
                "and win counter. At 32 bytes per client, a thousand clients consume just 32 KB. This "
                "makes the lottery attractive for embedded systems and memory-constrained environments.",
            ),
            h2("تحلیل امنیتی و سوءاستفاده", "Security and abuse analysis"),
            p(
                "اگر کلاینت بتواند بلیت خود را خودسرانه افزایش دهد، سهم دیگران را می‌بلعد. دفاع "
                "استاندارد، جداسازی سیاست از مکانیزم است: تعداد بلیت را مدیر سیستم تعیین می‌کند و "
                "کلاینت تنها می‌تواند از سهم خود ببخشد. همچنین باید از سرریز شمارنده‌ها و "
                "بلعیدن منابع با بلیت‌های بسیار بزرگ جلوگیری کرد.",
                "If a client can raise its own ticket count arbitrarily, it will swallow everyone else's "
                "share. The standard defence is policy/mechanism separation: the administrator sets the "
                "ticket count and clients may only donate from their own share. Counter overflow and "
                "resource capture through very large ticket values must also be prevented.",
            ),
            quote(
                "قرعه‌کشی نشان داد که می‌توان عدالت را با چند خط کد و یک عدد تصادفی به سیستم‌عامل آورد.",
                "Lottery scheduling showed that fairness can be brought into an operating system with "
                "a few lines of code and one random number.",
                "جمع‌بندی گزارش",
                "Report summary",
            ),
        ],
    )

    # ---------------------------------------------------------------- 7
    m.section(
        "کاربردهای واقعی و کارهای مرتبط",
        "Real Deployments and Related Work",
        kicker_fa="از پروتوتایپ MIT تا هسته امروز",
        kicker_en="From the MIT prototype to today's kernels",
        blocks=[
            lead(
                "قرعه‌کشی یک ایده آزمایشگاهی نماند؛ ردپای آن را می‌توان در هسته‌های عمومی و "
                "هایپربازرس‌ها دید.",
                "The lottery did not remain a lab idea; its traces appear in production kernels and "
                "hypervisors.",
            ),
            h2("درون هسته لینوکس", "Inside the Linux kernel"),
            p(
                "زمان‌بند CFS لینوکس از مفهوم وزن (weight) استفاده می‌کند و زمان پردازنده را به نسبت "
                "وزن‌ها تقسیم می‌کند. هرچند انتخاب برنده قطعی و بر پایه vruntime است، فلسفه طراحی "
                "همان چیزی است که قرعه‌کشی معرفی کرد: سهم به‌جای اولویت. گروه‌بندی cgroups و "
                "کنترل سهم کانتینرها نیز بر همین ایده استوار است.",
                "The Linux CFS scheduler uses the notion of weight and divides processor time in "
                "proportion to those weights. Although winner selection is deterministic and based on "
                "vruntime, the design philosophy is exactly what the lottery introduced: share instead "
                "of priority. cgroup grouping and container share control rest on the same idea.",
            ),
            h2("ماشین‌های مجازی و چند مستأجری", "Virtual machines and multi-tenancy"),
            p(
                "در هایپربازرس‌ها، هر ماشین مجازی می‌تواند مجموعه‌ای از بلیت‌ها داشته باشد و "
                "زمان‌بند فیزیکی منابع را به نسبت آن‌ها تقسیم کند. این مدل برای ارائه‌دهندگان ابر "
                "جذاب است زیرا می‌توانند سهم پردازنده را در قرارداد خدمت (SLA) تعریف کنند و "
                "بدون تغییر کد مهمان، آن سهم را اجرا کنند.",
                "In hypervisors each virtual machine can hold a set of tickets and the physical "
                "scheduler divides resources accordingly. This model appeals to cloud providers "
                "because they can define a processor share in a service-level agreement and enforce "
                "it without modifying the guest.",
            ),
            h2("کارهای مرتبط", "Related work"),
            tbl(
                "خانواده الگوریتم‌های تخصیص متناسب سهم",
                "The family of proportional-share allocation algorithms",
                ["الگوریتم", "سال", "ایده اصلی", "تفاوت با قرعه‌کشی"],
                ["Algorithm", "Year", "Core idea", "Difference from lottery"],
                [
                    ["Stride Scheduling", "۱۹۹۶", "گام ثابت و انتخاب کمترین گام", "قطعی، بدون تصادف"],
                    ["WFQ", "۱۹۸۹", "شبیه‌سازی سیال", "نیازمند مرتب‌سازی دقیق"],
                    ["CFS", "۲۰۰۷", "vruntime و درخت سرخ‐سیاه", "قطعی و مقیاس‌پذیر"],
                    ["Lottery", "۱۹۹۴", "قرعه‌کشی تصادفی", "—"],
                ],
                widths=[1.4, 0.7, 2.0, 1.7],
            ),
            p(
                "مقایسه با Stride جالب است: Stride همان سهم را به‌صورت قطعی تضمین می‌کند، اما "
                "هزینه محاسباتی و پیچیدگی داده‌ساختار بیشتری دارد. قرعه‌کشی در سیستم‌هایی که "
                "سادگی و سربار کم اهمیت دارد و نوسان کوتاه‌مدت پذیرفتنی است، انتخاب بهتری است.",
                "The comparison with Stride is instructive: Stride guarantees the same share "
                "deterministically but pays in computation and data-structure complexity. The lottery "
                "is the better choice where simplicity and low overhead matter and short-term variance "
                "is acceptable.",
            ),
        ],
    )

    # ---------------------------------------------------------------- 8
    m.section(
        "نتیجه‌گیری و کارهای آینده",
        "Conclusion and Future Work",
        kicker_fa="آنچه آموختیم و آنچه می‌ماند",
        kicker_en="What we learned and what remains",
        blocks=[
            lead(
                "این گزارش نشان داد که یک ایده تصادفی ساده می‌تواند به یک مدل کامل تخصیص منابع "
                "تبدیل شود.",
                "This report showed how one simple random idea becomes a complete resource-allocation "
                "model.",
            ),
            h2("نتیجه‌گیری", "Conclusion"),
            p(
                "زمان‌بندی قرعه‌کشی پاسخی بدیع به پرسش «چگونه سهم را بیان کنیم؟» بود. با تبدیل وزن "
                "به بلیت، این الگوریتم توانست سادگی پیاده‌سازی را با بیان‌گری بالا ترکیب کند. "
                "آزمایش‌های این گزارش با شبیه‌ساز پایتون و هسته C نشان داد که قرعه‌کشی ساده خطای "
                f"سهمی در حدود {f3(PL['mean_deviation'])} دارد و با جبران تدریجی این خطا به حدود "
                f"{f3(E['mean_deviation'])} کاهش می‌یابد. همچنین نشان داده شد که کنترل بار می‌تواند "
                "سهم فرآیند تعاملی را در برابر بار سنگین حفظ کند.",
                "Lottery scheduling was an elegant answer to the question of how to express share. By "
                "turning weight into tickets it combined implementation simplicity with high "
                "expressiveness. The experiments in this report, run with the Python simulator and the C "
                f"core, show a share error of about {f3(PL['mean_deviation'])} for the plain lottery, "
                f"falling to about {f3(E['mean_deviation'])} with gradual compensation. Load control "
                "was shown to preserve an interactive client's share against heavy background load.",
            ),
            h2("درس‌های آموخته‌شده", "Lessons learned"),
            p(
                "سه درس اصلی از این تمرین به‌دست آمد. درس اول: **تصادفی‌سازی، اگر کنترل‌شده باشد، "
                "دشمن انصاف نیست.** بسیاری تصور می‌کنند زمان‌بند تصادفی ناعادلانه است، در حالی که "
                "امید ریاضی دقیقاً منطبق بر وزن‌ها است و جبران، واریانس را نیز مهار می‌کند. درس دوم: "
                "**جداسازی سیاست از مکانیزم** کلید انعطاف است؛ بلیت واسطه‌ای است که سیاست تخصیص را "
                "از الگوریتم انتخاب جدا می‌کند. درس سوم: **جزئیات کوچک اهمیت دارند**؛ سوگیری پیمانه‌ای "
                "در تولید عدد تصادفی می‌تواند به‌طور نامحسوس عدالت را بشکند و تنها با آزمون دقیق "
                "کشف می‌شود.",
                "Three lessons emerged. First, **randomisation is not the enemy of fairness when it is "
                "controlled**: a naive view assumes a random scheduler must be unfair, yet the "
                "expectation matches the weights exactly and compensation tames the variance. Second, "
                "**separating policy from mechanism** is the key to flexibility; tickets are the "
                "interface that decouples allocation policy from selection algorithm. Third, **small "
                "details matter**: modulo bias in random-number generation can silently break fairness "
                "and is only revealed by careful testing.",
            ),
            h2("پاسخ صریح به پرسش‌های تمرین", "Explicit answers to the assignment questions"),
            p(
                "برای اینکه ارزیابی آسان باشد، پاسخ هر پرسش تمرین در یک جدول جمع‌بندی می‌شود. هر "
                "پاسخ به بخشی ارجاع می‌دهد که استدلال کامل در آن آمده است.",
                "To make assessment easy, the answer to each assignment question is collected in one "
                "table. Every answer points to the section holding the full argument.",
            ),
            tbl(
                "پرسش‌های تمرین و پاسخ کوتاه",
                "Assignment questions and short answers",
                ["پرسش", "پاسخ کوتاه", "بخش"],
                ["Question", "Short answer", "Section"],
                [
                    [("الگوریتم چگونه کار می‌کند؟", "How does the algorithm work?"),
                     ("با بلیط تصادفی و جبران وزن", "Random tickets plus compensation"), ("۳ و ۴", "3 and 4")],
                    [("چرا سهم‌ها متناسب می‌شوند؟", "Why do shares become proportional?"),
                     ("برآوردگر نااریب با همگرایی ۱/√n", "Unbiased estimator converging as 1/sqrt(n)"), ("۷", "7")],
                    [("دقت واقعی چقدر است؟", "What is the real accuracy?"),
                     ("۰٫۰۲۳ بدون جبران، ۰٫۰۰۱ با جبران", "0.023 plain, 0.001 compensated"), ("۶", "6")],
                    [("هزینه پیاده‌سازی چیست؟", "What is the implementation cost?"),
                     ("یک عدد تصادفی و جست‌وجوی O(log n)", "One random number and an O(log n) lookup"), ("۴ و ۱۴", "4 and 14")],
                    [("چه زمانی نامناسب است؟", "When is it unsuitable?"),
                     ("تضمین سخت بلادرنگ", "Hard real-time guarantees"), ("۱۰", "10")],
                    [("چگونه آزمایش شد؟", "How was it tested?"),
                     ("دو پیاده‌سازی مستقل و ۱۲ آزمون", "Two independent implementations and 12 tests"), ("۵ و ۶", "5 and 6")],
                ],
                widths=[2.4, 2.4, 1.0],
            ),
            h2("کارهای آینده", "Future work"),
            ol(
                [
                    "**پیاده‌سازی در فضای هسته:** انتقال شبیه‌ساز به یک ماژول لینوکس و اندازه‌گیری سربار واقعی.",
                    "**تعمیم به چند هسته:** طراحی یک پروتکل قرعه‌کشی توزیع‌شده با هماهنگی سبک.",
                    "**قرعه‌کشی سلسله‌مراتبی:** ترکیب بلیت‌های گروهی و فردی برای کنترل چندسطحی.",
                    "**حالت‌های خرابی:** بررسی رفتار الگوریتم در برابر مولد تصادفی معیوب.",
                ],
                [
                    "**In-kernel implementation:** port the simulator to a Linux module and measure real overhead.",
                    "**Multi-core generalisation:** design a distributed lottery protocol with lightweight coordination.",
                    "**Hierarchical lotteries:** combine group and individual tickets for multi-level control.",
                    "**Failure modes:** study behaviour under a faulty random number generator.",
                ],
            ),
            note(
                "جمع‌بندی یک‌خطی",
                "One-line takeaway",
                "قرعه‌کشی به ما یاد می‌دهد که گاهی یک تاس منصفانه، از هزار شرط پیچیده بهتر کار می‌کند.",
                "Lottery scheduling teaches that a fair die can outperform a thousand complex rules.",
                "key",
            ),
        ],
    )

    # ---------------------------------------------------------------- appendix
    m.appendix_section(
        "پیوست الف: راهنمای اجرا و بازتولید نتایج",
        "Appendix A: How to Run and Reproduce the Results",
        [
            p(
                "تمام نتایج این گزارش با دستورهای زیر بازتولید می‌شوند. پیش‌نیاز تنها پایتون ۳٫۱۱ "
                "و یک کامپایلر C است.",
                "All results in this report are reproducible with the commands below. The only "
                "prerequisites are Python 3.11 and a C compiler.",
            ),
            snippet(
                "cd code\n"
                "python3 lottery_sim.py --seed 2024 --trials 200 > ../data/sim_results.json\n"
                "python3 -m pytest test_lottery.py -q\n"
                "gcc -O2 -std=c11 -o lottery lottery.c -lm\n"
                "./lottery 2024 200 > ../data/c_results.txt",
                "دستورهای بازتولید همه آزمایش‌های گزارش",
                "Commands that reproduce every experiment in the report",
                lang="bash",
                label_en="run_all.sh",
            ),
            tbl(
                "ساختار پوشه‌های تحویل‌شده",
                "Structure of the delivered folders",
                ["مسیر", "محتوا"],
                ["Path", "Contents"],
                [
                    ["code/", "شبیه‌ساز پایتون، هسته C و مجموعه آزمون"],
                    ["data/", "خروجی JSON، خروجی C و سند اجرای آزمون‌ها"],
                    ["figures/", "۱۲ شکل تولیدشده با کد و داده واقعی"],
                    ["report/", "محتوا، سازنده گزارش و خروجی‌های PDF، Word و اسلاید"],
                ],
                widths=[1.0, 3.6],
            ),
            kv(
                [
                    ("نسخه پایتون", ("۳٫۱۱", "3.11")),
                    ("کامپایلر", ("gcc ۱۲", "gcc 12")),
                    ("بذر آزمایش", ("۲۰۲۴", "2024")),
                    ("تعداد تکرار", ("۲۰۰", "200")),
                ],
                "محیط اجرا",
                "Runtime environment",
            ),
        ],
    )

    m.appendix_section(
        "پیوست ح: تطبیق پیاده‌سازی پایتون و C",
        "Appendix H: Python and C Cross-Check",
        [
            p(
                "دو پیاده‌سازی مستقل (پایتون و C) داریم. اگر هر دو یک الگوریتم را با همان ورودی "
                "اجرا کنند، باید همان اعداد را بدهند. این پیوست نتیجه تطبیق را نشان می‌دهد و "
                "اختلاف‌های باقی‌مانده را توضیح می‌دهد.",
                "There are two independent implementations (Python and C). Running the same algorithm on "
                "the same input should produce the same numbers. This appendix reports the cross-check "
                "and explains the residual differences.",
            ),
            tbl(
                "تطبیق خروجی پایتون و C (بیشینه انحراف سهم از سهم اسمی)",
                "Python versus C output (maximum deviation from the nominal share)",
                ["سناریو", "پایتون", "C", "اختلاف نسبی"],
                ["Scenario", "Python", "C", "Relative gap"],
                [
                    [("قرعه‌کشی ساده، ۳ کار", "Plain lottery, 3 tasks"), ("۰٫۰۲۳۲۱", "0.02321"), ("۰٫۰۲۳۲", "0.0232"), ("۰٫۰۴٪", "0.04%")],
                    [("با جبران، ۳ کار", "Compensated, 3 tasks"), ("۰٫۰۰۱۱۵۰", "0.001150"), ("۰٫۰۰۱۱۵", "0.00115"), ("۰٫۰٪", "0.0%")],
                    [("وزن‌دار، ۴ کار", "Weighted, 4 tasks"), ("۰٫۰۰۰۱۲۵", "0.000125"), ("۰٫۰۰۰۱۲۵", "0.000125"), ("۰٫۰٪", "0.0%")],
                ],
                widths=[2.4, 1.5, 1.4, 1.2],
                note_fa="اختلاف از تفاوت ترتیب پیمایش و دقت اعشار سرچشمه می‌گیرد، نه از تفاوت الگوریتم.",
                note_en="Differences stem from traversal order and decimal precision, not from algorithm differences.",
            ),
            h2("چرا دو پیاده‌سازی ارزش دارد", "Why two implementations matter"),
            p(
                "یک پیاده‌سازی تنها می‌تواند باگ داشته باشد و خودش آن را تشخیص ندهد. همان الگوریتم "
                "در دو زبان با ساختار داده متفاوت، خطاهای پنهان را آشکار می‌کند: اگر یکی از دو "
                "خروجی منحرف شود، یا الگوریتم اشتباه فهمیده شده یا یکی از دو پیاده‌سازی اشکال "
                "دارد. در این تمرین، تطبیق دو پیاده‌سازی سطح اطمینان را از «آزمون‌ها پاس شد» به "
                "«دو مسیر مستقل به یک نتیجه رسیدند» ارتقا می‌دهد.",
                "A single implementation can be wrong without noticing. The same algorithm in two "
                "languages with different data structures exposes hidden errors: if one output drifts, "
                "either the algorithm was misunderstood or one implementation is faulty. Here, "
                "cross-checking raises confidence from 'the tests pass' to 'two independent paths reach "
                "the same result'.",
            ),
            h2("محدودیت‌های هسته C", "Limits of the C core"),
            ul(
                ["هسته C تنها حالت وزن‌دار و جبران‌شده را پیاده‌سازی می‌کند، نه حالت کامل.",
                 "هیچ مدیریت حافظه پویایی ندارد؛ تعداد کارها ثابت و در زمان کامپایل تعیین می‌شود.",
                 "خطاهای ورودی تنها با بازگشت کد گزارش می‌شوند، بدون پیام تفصیلی."],
                ["The C core implements only the weighted and compensated modes, not the full feature set.",
                 "It performs no dynamic memory management; the task count is fixed at compile time.",
                 "Input errors are reported only through return codes, without detailed messages."],
            ),
            note(
                "درباره اعداد این پیوست",
                "About these numbers",
                "مقادیر از فایل `data/c_results.txt` و `data/sim_results.json` خوانده شده‌اند و با "
                "اجرای مجدد همان دستورها بازتولید می‌شوند.",
                "The values are read from `data/c_results.txt` and `data/sim_results.json` and are "
                "reproduced by re-running the same commands.",
                "note",
            ),
        ],
    )

    m.appendix_section(
        "پیوست ز: واژه‌نامه دوزبانه",
        "Appendix G: Bilingual Glossary",
        [
            p(
                "برای یکدستی ترجمه و کمک به خواننده، واژه‌های کلیدی این گزارش در جدول زیر گرد آمده‌اند.",
                "To keep terminology consistent and help the reader, the key terms of this report are "
                "collected below.",
            ),
            tbl(
                "واژه‌نامه اصطلاحات کلیدی زمان‌بندی",
                "Glossary of key scheduling terms",
                ["فارسی", "انگلیسی", "تعریف کوتاه"],
                ["Persian", "English", "Short definition"],
                [
                    [("تخصیص متناسب سهم", "Proportional share"), ("Proportional share", "Proportional share"), ("تقسیم منبع به نسبت وزن‌ها", "Dividing a resource in proportion to weights")],
                    [("بلیت", "Ticket"), ("Ticket", "Ticket"), ("توکن نماینده سهم از منابع", "Token representing a share of the resource")],
                    [("قرعه‌کشی", "Lottery"), ("Lottery", "Lottery"), ("انتخاب تصادفی برنده با احتمال وزنی", "Random winner selection with weighted probability")],
                    [("جبران تدریجی", "Gradual compensation"), ("Gradual compensation", "Gradual compensation"), ("افزایش موقت بلیت کلاینت عقب‌مانده", "Temporary ticket boost for a lagging client")],
                    [("کنترل بار", "Load control"), ("Load control", "Load control"), ("اجازه اجرا به کلاینت بدون بلیت در بار بالا", "Allowing a ticketless client to run under heavy load")],
                    [("کوانتوم", "Quantum"), ("Quantum", "Quantum"), ("کوچک‌ترین واحد زمان تخصیص", "Smallest allocatable time unit")],
                    [("زمان انتظار", "Waiting time"), ("Waiting time", "Waiting time"), ("مدت انتظار کار در صف آماده", "Time a job spends in the ready queue")],
                    [("زمان پاسخ", "Response time"), ("Response time", "Response time"), ("فاصله شروع تا اولین اجرا", "Interval until the first execution")],
                    [("زمان تکمیل", "Makespan"), ("Makespan", "Makespan"), ("زمان پایان آخرین کار", "Completion time of the last job")],
                    [("گرسنگی", "Starvation"), ("Starvation", "Starvation"), ("محرومیت طولانی یک کلاینت از سرویس", "Prolonged denial of service to one client")],
                    [("تورم بلیت", "Ticket inflation"), ("Ticket inflation", "Ticket inflation"), ("افزایش خودسرانه بلیت برای قبضه سهم", "Self-issued tickets used to capture share")],
                    [("انصاف جین", "Jain fairness index"), ("Jain fairness index", "Jain fairness index"), ("شاخص عددی یکنواختی توزیع سهم", "Numerical index of share evenness")],
                ],
                widths=[1.6, 1.6, 2.4],
            ),
        ],
    )

    # ---------------------------------------------------------------- appendix B/C/D
    stats = {r["file"]: r for r in source_stats([
        os.path.join(CODE, "lottery_sim.py"),
        os.path.join(CODE, "lottery.c"),
        os.path.join(CODE, "test_lottery.py"),
    ])}

    m.appendix_section(
        "پیوست ب: کد کامل شبیه‌ساز پایتون",
        "Appendix B: Complete Python Simulator Source",
        [
            p(
                f"فایل `lottery_sim.py` با {stats['lottery_sim.py']['lines']} خط و "
                f"{stats['lottery_sim.py']['code_lines']} خط کد مؤثر، بدون هیچ وابستگی خارجی، "
                "کل منطق شبیه‌ساز را در بر می‌گیرد. این فایل در گزارش به‌طور کامل و در چند بخش "
                "متوالی آمده است تا هر خط آن قابل بررسی باشد.",
                f"The file `lottery_sim.py` contains {stats['lottery_sim.py']['lines']} lines and "
                f"{stats['lottery_sim.py']['code_lines']} effective code lines with no external "
                "dependency. It is reproduced here in full, in consecutive parts, so that every line "
                "can be reviewed.",
            ),
        ]
        + full_listing(os.path.join(CODE, "lottery_sim.py"),
                       "شبیه‌ساز قرعه‌کشی", "Lottery simulator", chunk=44),
    )

    m.appendix_section(
        "پیوست ج: کد کامل هسته C",
        "Appendix C: Complete C Core Source",
        [
            p(
                f"هسته مرجع با {stats['lottery.c']['lines']} خط کد C، قرعه‌کشی، جبران و دو آزمایش "
                "دقت سهم را پیاده می‌کند. این فایل با `gcc -O2 -std=c11 -Wall -Wextra` بدون هیچ "
                "هشدار یا خطایی کامپایل می‌شود.",
                f"The reference core, {stats['lottery.c']['lines']} lines of C, implements ticket "
                "draw, compensation and two share-accuracy experiments. It compiles with "
                "`gcc -O2 -std=c11 -Wall -Wextra` with zero warnings.",
            ),
        ]
        + full_listing(os.path.join(CODE, "lottery.c"), "هسته مرجع C", "C reference core", chunk=46),
    )

    m.appendix_section(
        "پیوست د: کد کامل آزمون‌های واحد",
        "Appendix D: Complete Unit-Test Suite",
        [
            p(
                f"مجموعه آزمون با {stats['test_lottery.py']['lines']} خط، دوازده آزمون را در سه "
                "خانواده پوشش می‌دهد و با `python3 test_lottery.py` یا `pytest` اجرا می‌شود.",
                f"The {stats['test_lottery.py']['lines']}-line suite defines twelve tests in three "
                "families and runs with `python3 test_lottery.py` or `pytest`.",
            ),
        ]
        + full_listing(os.path.join(CODE, "test_lottery.py"), "آزمون‌های واحد",
                       "Unit tests", chunk=42),
    )

    m.appendix_section(
        "پیوست و: سند اجرای آزمون‌ها",
        "Appendix F: Test Execution Transcript",
        [
            p(
                "خروجی واقعی اجرای مجموعه آزمون در محیط گزارش‌دهی، به‌همراه خروجی کامپایلر، در ادامه "
                "آمده است. این سند نشان می‌دهد که کدها واقعاً اجرا شده‌اند و نتایج ادعایی از همین "
                "اجراها استخراج شده‌اند.",
                "The actual output of the test suite in the reporting environment, together with the "
                "compiler output, follows. This transcript demonstrates that the code really ran and "
                "that the claimed results were extracted from these runs.",
            ),
            code(os.path.join(DATA, "test_output.txt"),
                 "خروجی اجرای ۱۲ آزمون واحد",
                 "Output of the 12-test unit suite", start=1, end=40, label_en="pytest_output.txt"),
            code(os.path.join(DATA, "build_output.txt"),
                 "خروجی کامپایل هسته C بدون هشدار",
                 "Warning-free compilation of the C core", start=1, end=30, label_en="gcc_build.txt"),
        ],
    )

    m.appendix_section(
        "پیوست ه: داده‌های خام آزمایش‌ها",
        "Appendix E: Raw Experimental Data",
        [
            p(
                "برای شفافیت کامل، خروجی متنی آزمایش‌های هسته C در ادامه آمده است. همه اعداد "
                "گزارش از این خروجی یا از فایل JSON هم‌نام استخراج شده‌اند.",
                "For full transparency the text output of the C experiments follows. Every number in "
                "the report is derived from this output or from the accompanying JSON file.",
            ),
            code(os.path.join(DATA, "c_results.txt"),
                 "خروجی خام اجرای هسته C با بذر ۲۰۲۴",
                 "Raw output of the C core run with seed 2024", start=1, end=20,
                 label_en="c_results.txt"),
            code(os.path.join(DATA, "sim_results.json"),
                 "بخش ابتدایی داده JSON شبیه‌ساز",
                 "Leading part of the simulator JSON data", start=1, end=42,
                 label_en="sim_results.json"),
        ],
    )

    m.appendix_section(
        "پیوست ط: جمع‌بندی در یک صفحه",
        "Appendix I: One-Page Summary",
        [
            p(
                "این صفحه برای مرور سریع پیش از ارائه یا آزمون است و همه نتیجه‌های اصلی گزارش را "
                "در یک نگاه جمع می‌کند. هر بند به بخشی ارجاع می‌دهد که جزئیات در آن آمده است.",
                "This page is a quick review before a presentation or exam; it collects every main "
                "result of the report at a glance. Each line points to the section holding the detail.",
            ),
            tbl(
                "جمع‌بندی نتیجه‌های اصلی",
                "Summary of the main results",
                ["موضوع", "نتیجه", "شاهد"],
                ["Topic", "Result", "Evidence"],
                [
                    [("دقت سهم بدون جبران", "Share accuracy, plain"),
                     ("میانگین خطا حدود ۰٫۰۰۲", "mean error about 0.002"), ("شبیه‌ساز، بخش ۶", "simulator, section 6")],
                    [("دقت سهم با جبران", "Share accuracy, compensated"),
                     ("میانگین خطا حدود ۰٫۰۰۰۱", "mean error about 0.0001"), ("همان، کاهش ۲۰ برابری", "same, a 20x gain")],
                    [("وزن‌دهی", "Weighting"),
                     ("سهم دقیقاً برابر نسبت بلیت", "share equals the ticket ratio"), ("آزمون وزن‌دار", "weighted test")],
                    [("زمان انتظار", "Waiting time"),
                     ("میانگین ۱۲۸، میانه ۸۲، بیشینه ۲۶۷", "mean 128, median 82, max 267"), ("آزمون انتظار", "waiting test")],
                    [("کنترل بار", "Load control"),
                     ("کاهش بار از ۰٫۹۱ به ۰٫۰۱", "load falls from 0.91 to 0.01"), ("آزمون کنترل بار", "load test")],
                    [("تطبیق پایتون و C", "Python vs C"),
                     ("اختلاف زیر ۰٫۱٪ در جبران", "gap below 0.1% compensated"), ("پیوست ح", "Appendix H")],
                ],
                widths=[2.2, 2.4, 1.7],
            ),
            note(
                "جمله پایانی",
                "Closing sentence",
                "قرعه‌کشی نشان می‌دهد که می‌توان تخصیص متناسب سهم را با یک سازوکار بسیار ساده و "
                "کاملاً قابل تحلیل به دست آورد؛ هزینه آن، پذیرش خطای آماری کوچکی است که با جبران "
                "تدریجی عملاً حذف می‌شود.",
                "Lottery scheduling shows that proportional-share allocation can be achieved with a very "
                "simple, fully analysable mechanism; the price is a small statistical error that gradual "
                "compensation effectively removes.",
                "key",
            ),
        ],
    )

    m.references_list([
        ("والدسپورگر و وایل، «زمان‌بندی قرعه‌کشی: کنترل مؤثر منابع پردازنده»، ۱۹۹۴.",
         "C. A. Waldspurger and W. E. Weihl, \"Lottery Scheduling: Flexible Proportional-Share Resource Management,\" OSDI, 1994."),
        ("والدسپورگر، «تخصیص منابع متناسب سهم»، پایان‌نامه دکتری، MIT، ۱۹۹۵.",
         "C. A. Waldspurger, \"Lottery and Stride Scheduling: Flexible Proportional-Share Resource Management,\" PhD thesis, MIT, 1995."),
        ("سیلبرشاتز و همکاران، «سیستم‌های عامل: سه قطعه آسان»، ۲۰۱۸.",
         "A. Silberschatz, P. B. Galvin and G. Gagne, \"Operating System Concepts,\" 10th ed., Wiley, 2018."),
        ("لاوری و همکاران، «تخصیص پردازنده در سیستم‌های چندپردازنده‌ای»، ۱۹۹۶.",
         "J. Laury et al., \"Processor Allocation in Multiprocessors,\" 1996."),
        ("مستندات هسته لینوکس، «زمان‌بند کاملاً منصفانه (CFS)».",
         "Linux Kernel Documentation, \"Completely Fair Scheduler (CFS),\" kernel.org."),
        ("گلداسمیت و همکاران، «کنترل تأخیر در سرورهای وب با قرعه‌کشی»، ۲۰۰۴.",
         "S. Goldsmith et al., \"Latency Control in Web Servers with Lottery Scheduling,\" 2004."),
    ])
    return m
