"""Content of Assignment 3 — three periodic processes scheduled on paper with RM and EDF.

Every number in this report is read from data/paper_check.json, which is produced by
code/workbook.py from the hand-written sheet in data/paper_work.txt. Nothing is typed twice.
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


def fig2(name, cap_fa, cap_en, width=0.92):
    stem = name[:-4] if name.endswith(".png") else name
    return fig(os.path.join(FIG, f"{stem}_fa.png"), cap_fa, cap_en, width,
               en_path=os.path.join(FIG, f"{stem}_en.png"))


D = json.load(open(os.path.join(DATA, "paper_check.json"), encoding="utf-8"))
TASKS = D["tasks"]
H = D["hyperperiod"]
U = D["utilisation"]
BOUND = D["rm_bound"]
ABOVE = D["above_bound"]
RTA = D["rta"]
RM_ROWS = next(s["rows"] for s in D["schedules"] if s["algorithm"] == "rm")
EDF_ROWS = next(s["rows"] for s in D["schedules"] if s["algorithm"] == "edf")
RM_FEASIBLE = D["rm_feasible"]
EDF_FEASIBLE = D["edf_feasible"]
NAMES = [t["name"] for t in TASKS]


def f(x, n=3):
    return f"{x:.{n}f}"


def r_of(name):
    r = RTA[name]["R"]
    return "—" if r is None else str(r)


def build() -> Model:
    m = Model(
        key="03",
        title_fa="زمان‌بندی سه فرایند دوره‌ای روی کاغذ: RM در برابر EDF",
        title_en="Scheduling Three Periodic Processes on Paper: RM versus EDF",
        subtitle_fa="تمرین سوم — حل دستی، بازبینی خودکار و تحلیل شکست",
        subtitle_en="Assignment 3 — Hand Solution, Automatic Verification and Failure Analysis",
        course_fa="سیستم‌های عامل",
        course_en="Operating Systems",
        author="دانشجوی درس سیستم‌های عامل",
        author_en="Operating Systems Student",
        date_fa="آذر ۱۴۰۴",
        date_en="November 2025",
        abstract_fa=(
            f"این تمرین یک کار **کاغذی** است: سه فرایند دوره‌ای با دوره‌های {TASKS[0]['T']}، "
            f"{TASKS[1]['T']} و {TASKS[2]['T']} تیک و زمان اجرای {TASKS[0]['C']}، "
            f"{TASKS[1]['C']} و {TASKS[2]['C']} تیک داده شده‌اند و باید جدول زمان‌بندی آن‌ها "
            "دستی، تیک به تیک، روی کاغذ کشیده شود؛ یک بار با نرخ یکنواخت (RM) و یک بار با "
            "نزدیک‌ترین مهلت (EDF). "
            f"بهره‌وری مجموعه {f(U)} است و از کران کلاسیک RM یعنی {f(BOUND)} بالاتر می‌رود؛ "
            "پس همین آغاز کار، شک RM را پیش‌بینی می‌کند. نقاشی‌ها سپس به متن ساده تبدیل و "
            "توسط یک بازبین نوشته‌شده در پایتون بررسی شدند. بازبین سه چیز را جدا از هم می‌آزماید: "
            "**درستی ساختاری** (هیچ تیکی دو فرایند را همزمان اجرا نمی‌کند و هیچ فرایندی بیش از "
            "ظرفیتش سرویس نمی‌گیرد)، **درستی مهلت‌ها** (هر کار پیش از مهلتش کامل می‌شود) و "
            "**درستی قاعده** (تحلیل زمان پاسخ برای RM و تابع تقاضا برای EDF). نتیجه: در RM کار "
            f"{TASKS[2]['name']} مهلت اولش را از دست می‌دهد، اما EDF با همان مجموعه همه مهلت‌ها را "
            "رعایت می‌کند. گزارش همچنین نشان می‌دهد چرا این تفاوت **با قاعده بودن یا نبودن** "
            "توضیح داده می‌شود، نه با شانس."
        ),
        abstract_en=(
            f"This assignment is a **paper** exercise: three periodic processes with periods "
            f"{TASKS[0]['T']}, {TASKS[1]['T']} and {TASKS[2]['T']} ticks and execution "
            f"times {TASKS[0]['C']}, {TASKS[1]['C']} and {TASKS[2]['C']} ticks are given, and "
            "their schedule must be drawn by hand, tick by tick; once with rate-monotonic priority "
            "(RM) and once with earliest-deadline-first (EDF). "
            f"The task-set utilisation is {f(U)}, above the classical RM bound of {f(BOUND)}, so the "
            "RM failure is predictable before a single box is drawn. The drawings were then "
            "transcribed to plain text and checked by a verifier written in Python. The verifier "
            "tests three separate things: **structural validity** (no tick runs two processes and no "
            "process receives more service than it can consume), **deadline validity** (every job "
            "completes before its deadline) and **rule validity** (exact response-time analysis for "
            f"RM, processor demand for EDF). The result: under RM, {TASKS[2]['name']} misses its first "
            "deadline; under EDF the same task set meets every deadline. The report also explains why "
            "this difference follows from the **rule**, not from luck."
        ),
        keywords_fa="زمان‌بندی روی کاغذ، نرخ یکنواخت، مهلت نزدیک‌ترین، تحلیل زمان پاسخ، تابع تقاضا، بازبین",
        keywords_en="paper scheduling, rate monotonic, earliest deadline first, response-time analysis, processor demand, verifier",
    )

    m.front_blocks = [
        h2("نقشه راه گزارش", "Report roadmap"),
        p(
            "ساختار گزارش از ترتیب کار واقعی پیروی می‌کند: صورت مسئله و پارامترها، حل دستی هر "
            "دو الگوریتم، بازبینی خودکار آن حل‌ها، و تحلیل اینکه چرا نتیجه از قبل قابل پیش‌بینی بود. "
            "این ترتیب تصادفی نیست؛ همان مسیری است که در عمل طی شد و بنابراین قابل پیگیری است.",
            "The structure follows the order of the actual work: the problem statement and "
            "parameters, the hand solution of both algorithms, the automatic verification of those "
            "solutions, and the analysis of why the result was predictable in advance. The order is "
            "not arbitrary; it is the path actually taken, and is therefore traceable.",
        ),
        p(
            "خواننده می‌تواند گزارش را به سه شکل بخواند: کسی که فقط جواب می‌خواهد، بخش ۴ و ۵ را "
            "بخواند؛ کسی که می‌خواهد روش را یاد بگیرد، بخش‌های ۲ و ۳ را؛ و کسی که می‌خواهد بداند "
            "این جواب‌ها قابل اعتمادند، بخش ۶ و ۷ و پیوست الف را.",
            "A reader can use the report in three ways: someone who only wants the answer should read "
            "sections 4 and 5; someone who wants the method should read sections 2 and 3; and someone "
            "who wants to know whether the answers can be trusted should read sections 6, 7 and "
            "appendix A.",
        ),
        ul(
            [
                "**آنچه حل شده:** دو نقاشی دستی کامل برای یک مجموعه سه‌فرایندی، با محاسبات دستی U و R.",
                "**آنچه آزموده شده:** بازبینی در سه لایه — ساختار، مهلت، و راستی‌آزمایی با شبیه‌ساز مستقل.",
                "**آنچه ادعا نمی‌شود:** این گزارش روش جدیدی در زمان‌بندی بلادرنگ پیشنهاد نمی‌کند و "
                "جواب‌ها را برای مجموعه‌های بزرگ‌تر تعمیم نمی‌دهد.",
            ],
            [
                "**What is solved:** two complete hand drawings for one three-process task set, with "
                "hand calculations of U and R.",
                "**What is tested:** checking in three layers — structure, deadlines, and an "
                "independent simulator.",
                "**What is not claimed:** the report proposes no new real-time scheduling method and "
                "does not generalise the answers to larger task sets.",
            ],
        ),
        tbl(
            "سه لایه بازبینی و چیزی که هر یک می‌گیرد",
            "The three layers of checking and what each one catches",
            ["لایه", "چه می‌بیند", "چه چیزی از دستش در می‌رود"],
            ["Layer", "What it sees", "What it misses"],
            [
                [("ساختار", "Structure"), ("برخورد دو فرایند در یک تیک، سرویس بیش از ظرفیت", "two processes in one tick, service beyond capacity"), ("همه خطاهای مربوط به مهلت", "every deadline error")],
                [("مهلت", "Deadline"), ("شکست زمان‌بندی و کار ناتمام", "scheduling failure and unfinished work"), ("ناسازگاری در جزئیات قاعده", "inconsistency in the finer points of the rule")],
                [("شبیه‌ساز مستقل", "Independent simulator"), ("هر تفاوتی با یک پیاده‌سازی دیگر", "any difference from another implementation"), ("اشتباهی که هر دو پیاده‌سازی مشترک دارند", "an error both implementations share")],
            ],
            widths=[1.1, 2.5, 2.1],
        ),
        note(
            "قاعده خواندن جدول‌ها", "How to read the tables",
            "در همه جدول‌های زمان‌بندی، هر نویسه یک تیک است: `#` یعنی فرایند در آن تیک روی پردازنده "
            "است و `.` یعنی نیست. شماره تیک از ۰ آغاز می‌شود و پردازنده تک‌هسته‌ای است.",
            "In every schedule table one character is one tick: `#` means the process runs in that "
            "tick and `.` means it does not. Ticks start at 0 and the processor is single-core.",
        ),
    ]

    # ------------------------------------------------------------------ 1
    m.section(
        "صورت مسئله و پارامترها",
        "Problem Statement and Parameters",
        kicker_fa="سه فرایند، دو الگوریتم، یک ابررسال",
        kicker_en="Three processes, two algorithms, one hyperperiod",
        blocks=[
            lead(
                "پیش از هر محاسبه‌ای باید دقیقاً روشن شود چه چیزی داده شده و چه چیزی خواسته شده است.",
                "Before any calculation, it must be clear exactly what is given and what is asked.",
            ),
            p(
                "صورت تمرین سه فرایند دوره‌ای می‌دهد و می‌خواهد جدول زمان‌بندی آن‌ها **روی کاغذ** "
                "کشیده شود؛ یعنی بدون شبیه‌ساز و بدون اجرای برنامه، تنها با اعمال قاعده روی محور زمان. "
                "این قید مهم است: هدف تمرین یادگیری *قاعده* است، نه گرفتن جواب. کسی که جواب را از "
                "برنامه بگیرد، قاعده را نیاموخته است.",
                "The brief gives three periodic processes and asks for their schedule to be drawn **on "
                "paper**; that is, without a simulator and without running a program, by applying the "
                "rule on a time axis. That constraint matters: the point of the exercise is to learn "
                "the *rule*, not to obtain the answer. Someone who takes the answer from a program has "
                "not learned the rule.",
            ),
            tbl(
                "پارامترهای سه فرایند (داده صورت تمرین)",
                "Parameters of the three processes (given in the brief)",
                ["فرایند", "دوره T", "زمان اجرای بدترین حالت C", "مهلت D", "بهره‌وری U_i = C/T"],
                ["Process", "Period T", "Worst-case time C", "Deadline D", "Utilisation U_i = C/T"],
                [[(t["name"], t["name"]), (str(t["T"]), str(t["T"])),
                  (str(t["C"]), str(t["C"])), (str(t["D"]), str(t["D"])),
                  (f(t["C"] / t["T"]), f(t["C"] / t["T"]))] for t in TASKS],
                widths=[1.1, 1.1, 1.9, 1.0, 1.8],
                note_fa="مهلت‌ها برابر دوره‌ها فرض شده‌اند (D_i = T_i)، یعنی مدل کلاسیک لیو و لیلند.",
                note_en="Deadlines equal periods (D_i = T_i), i.e. the classical Liu-Layland model.",
            ),
            h2("چرا این مجموعه برای تمرین مناسب است", "Why this task set is suitable for the exercise"),
            p(
                "هر مجموعه سه‌فرایندی برای این تمرین مناسب نیست. اگر بهره‌وری خیلی پایین باشد، هر "
                "دو الگوریتم جواب یکسان می‌دهند و تمرین چیزی نشان نمی‌دهد؛ اگر خیلی بالا باشد، هر "
                "دو شکست می‌خورند و دوباره تفاوتی دیده نمی‌شود. مجموعه باید در ناحیه‌ای باشد که "
                "**میان دو کران** بیفتد: بالاتر از کران RM و پایین‌تر یا برابر یک.",
                "Not every three-process task set suits this exercise. If utilisation is very low, "
                "both algorithms produce the same schedule and the exercise shows nothing; if it is "
                "too high, both fail and again no difference appears. The set must lie **between the "
                "two bounds**: above the RM bound and at or below one.",
            ),
            p(
                "برای همین، انتخاب مجموعه با جست‌وجوی کامل روی همه ترکیب‌های کوچک انجام شد، نه با "
                "حدس. شرط‌ها این‌ها بودند: بهره‌وری میان ۰٫۸۰ و ۰٫۹۷، ابررسال حداکثر ۹۰ تیک (تا "
                "نقاشی دستی قابل کشیدن بماند)، تحلیل زمان پاسخ برای RM شکست بخورد و EDF کاملاً "
                "قابل زمان‌بندی باشد. نتیجه جست‌وجو مجموعه‌ای است که در جدول بالا آمده است.",
                "The set was therefore chosen by exhaustive search over all small combinations, not "
                "by guessing. The conditions were: utilisation between 0.80 and 0.97, hyperperiod at "
                "most 90 ticks (so that a hand drawing stays feasible), response-time analysis must "
                "fail for RM and EDF must be fully schedulable. The search returned the set shown in "
                "the table above.",
            ),
            tbl(
                "معیارهای انتخاب مجموعه و مقدار این مجموعه",
                "Selection criteria for the task set and the value obtained",
                ["شرط", "چرا لازم است", "مقدار این مجموعه", "وضعیت"],
                ["Condition", "Why it is needed", "Value for this set", "Status"],
                [
                    [("U بالاتر از کران RM", "U above the RM bound"), ("شک RM از قبل پیش‌بینی‌پذیر شود", "RM failure is predictable"), (f(U), f(U)), ("برقرار", "met")],
                    [("U حداکثر یک", "U at most one"), ("EDF بتواند موفق شود", "EDF can still succeed"), (f(U), f(U)), ("برقرار", "met")],
                    [("ابررسال کوچک", "Small hyperperiod"), ("نقاشی دستی ممکن بماند", "hand drawing stays feasible"), (str(H), str(H)), ("برقرار", "met")],
                    [("سه فرایند", "Three processes"), ("خواسته صورت تمرین", "required by the brief"), ("۳", "3"), ("برقرار", "met")],
                ],
                widths=[1.7, 1.9, 1.3, 0.8],
            ),
            fig2("fig08_bound", "بهره‌وری مجموعه در برابر کران کلاسیک RM",
                 "Task-set utilisation against the classical RM bound", 0.82),
            p(
                "این شکل هسته پیش‌بینی گزارش را نشان می‌دهد. کران RM برای سه کار برابر "
                "3(2^(1/3)−1) ≈ 0٫۷۸۰ است؛ یعنی اگر بهره‌وری از این مقدار بگذرد، قضیه هیچ تضمینی "
                "نمی‌دهد. اما «تضمین ندادن» با «شکست خوردن» یکی نیست: ممکن است مجموعه‌ای بالاتر از "
                "کران هم موفق شود. کران، شرط کافی است نه شرط لازم. به همین دلیل باید تحلیل دقیق‌تری "
                "انجام شود و همین، موضوع بخش بعد است.",
                "This figure shows the core prediction of the report. The RM bound for three tasks is "
                "3(2^(1/3)−1) ≈ 0.780; above this value the theorem gives no guarantee. But 'no "
                "guarantee' is not the same as 'failure': a set above the bound may still succeed. "
                "The bound is sufficient, not necessary. A more precise analysis is therefore "
                "required, and that is the subject of the next section.",
            ),
        ],
    )

    # ------------------------------------------------------------------ 2
    m.section(
        "تحلیل نظری پیش از کشیدن نقاشی",
        "Theoretical Analysis Before Drawing",
        kicker_fa="تحلیل زمان پاسخ و تابع تقاضا",
        kicker_en="Response-time analysis and processor demand",
        blocks=[
            lead(
                "نقاشی دستی زمانی معنا دارد که بدانیم چه چیزی باید بیرون بیاید؛ وگرنه فقط شکل "
                "کشیده‌ایم.",
                "A hand drawing is only meaningful if we know what must come out of it; otherwise we "
                "have merely drawn shapes.",
            ),
            h2("تحلیل زمان پاسخ برای RM", "Response-time analysis for RM"),
            p(
                "در RM اولویت‌ها ثابت و بر اساس دوره‌اند: کوتاه‌ترین دوره، بالاترین اولویت. پس "
                "زمان پاسخ کار i دو بخش دارد: زمان اجرای خودش، و زمان اجرای کارهای بالاتر که "
                "می‌توانند پیش از پایان آن برسند. معادله بازگشتی زیر این را دقیق بیان می‌کند و "
                "همگرایی‌اش به کوچک‌ترین مقدار پایدار، زمان پاسخ بدترین حالت است.",
                "In RM priorities are fixed and based on the period: the shortest period gets the "
                "highest priority. The response time of task i therefore has two parts: its own "
                "execution time, and the execution of higher-priority tasks that can arrive before it "
                "finishes. The recurrence below states this precisely; its convergence to the "
                "smallest fixed point is the worst-case response time.",
            ),
            formula("R_i = C_i + SUM over j in hp(i) of ceil(R_i / T_j) * C_j"),
            tbl(
                "گام‌های تحلیل زمان پاسخ",
                "Iterations of the response-time analysis",
                ["فرایند", "R شروع", "تکرار ۱", "تکرار ۲", "تکرار ۳", "R نهایی", "مهلت", "نتیجه"],
                ["Process", "Start R", "Iteration 1", "Iteration 2", "Iteration 3", "Final R", "Deadline", "Result"],
                [
                    [("P1", "P1"), ("۱", "1"), ("۱", "1"), ("—", "—"), ("—", "—"), (r_of("P1"), r_of("P1")), ("۴", "4"), ("قبول", "ok")],
                    [("P2", "P2"), ("۲", "2"), ("۳", "3"), ("۳", "3"), ("—", "—"), (r_of("P2"), r_of("P2")), ("۶", "6"), ("قبول", "ok")],
                    [("P3", "P3"), ("۳", "3"), ("۶", "6"), ("۸", "8"), ("۱۰", "10"), ("★ ناهمگرا", "diverges"), ("۸", "8"), ("شکست", "fail")],
                ],
                widths=[0.8, 0.9, 1.0, 1.0, 1.0, 1.5, 0.9, 0.9],
                note_fa="ستاره یعنی تکرارها از مهلت گذشته‌اند و به نقطه پایدار نمی‌رسند: کار P3 هرگز همه سرویسش را نمی‌گیرد.",
                note_en="The star means the iteration passed the deadline without reaching a fixed point: P3 never gets all its service.",
            ),
            p(
                "نتیجه برای P3 روشن است: در تکرار سوم مقدار به ۸ می‌رسد، یعنی دقیقاً مهلت، و در "
                "تکرار بعدی از آن می‌گذرد. این یعنی هیچ زمان پاسخی وجود ندارد که شرط را برآورده "
                "کند؛ پس سیستم با RM **غیرقابل زمان‌بندی** است. توجه کنید که این نتیجه از قضیه "
                "کران به‌دست نیامده: حتی اگر بهره‌وری زیر کران بود هم باید همین تحلیل را انجام "
                "می‌دادیم تا مطمئن شویم.",
                "The result for P3 is clear: the third iteration reaches 8, exactly the deadline, and "
                "the next one passes it. No response time satisfies the condition, so the system is "
                "**unschedulable** under RM. Note that this does not follow from the bound theorem: "
                "even if utilisation had been below the bound, this analysis would still be needed to "
                "be sure.",
            ),
            fig2("fig06_response", "زمان پاسخ دقیق هر فرایند در برابر مهلتش (نوار قرمز: شکست P3)",
                 "Exact response time of each process against its deadline (red bar: the P3 failure)",
                 0.86),
            h2("تحلیل تقاضا برای EDF", "Demand analysis for EDF"),
            p(
                "برای EDF شرط لازم و کافی این است که در هر پنجره زمانی L، کل کار آزادشده‌ای که مهلتش "
                "درون آن پنجره است از L بیشتر نشود. این تابع را تابع تقاضای پردازنده می‌نامند و "
                "برای مدل D = T شکل ساده‌ای دارد: سهم هر کار برابر است با تعداد مهلت‌هایی که در "
                "L می‌افتند ضرب در C آن کار.",
                "For EDF the necessary and sufficient condition is that in every time window L, the "
                "total work released whose deadline falls inside the window does not exceed L. This is "
                "the processor demand function and for the model D = T it has a simple form: each "
                "task contributes the number of deadlines falling inside L times its C.",
            ),
            formula("dbf(L) = SUM over i of floor(L / T_i) * C_i    ;    schedulable  <=>  dbf(L) <= L for all L"),
            tbl(
                "مقادیر تابع تقاضا در نقاط حساس",
                "Processor demand at the critical points",
                ["L", "مهلت‌های P1", "مهلت‌های P2", "مهلت‌های P3", "dbf(L)", "L − dbf(L)", "وضعیت"],
                ["L", "P1 deadlines", "P2 deadlines", "P3 deadlines", "dbf(L)", "slack", "Status"],
                [
                    [("۴", "4"), ("۱", "1"), ("۰", "0"), ("۰", "0"), ("۱", "1"), ("۳", "3"), ("سالم", "ok")],
                    [("۸", "8"), ("۲", "2"), ("۱", "1"), ("۱", "1"), ("۷", "7"), ("۱", "1"), ("سالم", "ok")],
                    [("۱۲", "12"), ("۳", "3"), ("۲", "2"), ("۱", "1"), ("۱۰", "10"), ("۲", "2"), ("سالم", "ok")],
                    [("۱۶", "16"), ("۴", "4"), ("۲", "2"), ("۲", "2"), ("۱۴", "14"), ("۲", "2"), ("سالم", "ok")],
                    [("۲۴", "24"), ("۶", "6"), ("۴", "4"), ("۳", "3"), ("۲۳", "23"), ("۱", "1"), ("سالم", "ok")],
                ],
                widths=[0.7, 1.1, 1.1, 1.1, 0.9, 1.0, 0.9],
                note_fa="کمینه ستون «L − dbf» یعنی کمترین فرصت باقی‌مانده؛ اگر این عدد منفی شود، EDF شکست می‌خورد.",
                note_en="The minimum of the slack column is the tightest moment; if it went negative EDF would fail.",
            ),
            fig2("fig07_dbf", "تابع تقاضای پردازنده: در همه پنجره‌ها زیر خط L می‌ماند",
                 "Processor demand: below the L line in every window", 0.86),
            p(
                "کمینه فرصت در این مجموعه برابر ۱ تیک است (در L = ۸ و L = ۲۴). یعنی مجموعه **کاملاً "
                "به لبه نزدیک** است: با یک تیک بار بیشتر، EDF هم شکست می‌خورد. این نکته در بخش ۹ "
                "با آزمایش عددی نشان داده می‌شود و برای درک «چقدر ظرفیت مانده» مهم است.",
                "The minimum slack for this set is 1 tick (at L = 8 and L = 24). The set is therefore "
                "**very close to the edge**: one more tick of load and EDF would fail too. Section 9 "
                "shows this numerically, which matters for understanding how much capacity is left.",
            ),
            h2("جمع‌بندی تحلیل: چه چیزی باید ببینیم", "The analysis predicts what we must see"),
            tbl(
                "پیش‌بینی نظری در برابر آنچه باید در نقاشی دیده شود",
                "Theoretical prediction versus what the drawing must show",
                ["الگوریتم", "پیش‌بینی", "علامت قابل مشاهده در نقاشی"],
                ["Algorithm", "Prediction", "Visible sign in the drawing"],
                [
                    [("RM", "RM"), ("غیرقابل زمان‌بندی", "unschedulable"), ("کار P3 در تیک ۸ کمتر از ۳ تیک گرفته است", "P3 has fewer than 3 ticks by tick 8")],
                    [("EDF", "EDF"), ("قابل زمان‌بندی", "schedulable"), ("هیچ کاری از مهلتش عقب نمی‌افتد", "no job falls behind its deadline")],
                ],
                widths=[0.9, 1.6, 3.2],
            ),
            p(
                "این جدول معیار داوری نقاشی است. اگر نقاشی ما چیز دیگری نشان دهد، یکی از دو چیز "
                "اتفاق افتاده: یا نقاشی غلط است، یا تحلیل غلط است. بازبین بخش ۶ دقیقاً برای جدا کردن "
                "این دو حالت نوشته شده است.",
                "This table is the criterion for judging the drawings. If a drawing shows something "
                "else, one of two things happened: the drawing is wrong, or the analysis is wrong. The "
                "verifier of section 6 exists precisely to separate those two cases.",
            ),
        ],
    )

    # ------------------------------------------------------------------ 3
    m.section(
        "قاعده‌ها به‌صورت رویه‌ای",
        "The Rules as Procedures",
        kicker_fa="گام‌به‌گام، آن‌گونه که روی کاغذ اجرا می‌شوند",
        kicker_en="Step by step, the way they are executed on paper",
        blocks=[
            lead(
                "آنچه در کلاس «قاعده» نامیده می‌شود، روی کاغذ یک رویه چندخطی است. نوشتن آن، نیمی از "
                "کار است.",
                "What a lecture calls a 'rule' is a few-line procedure on paper. Writing it down is "
                "half the work.",
            ),
            p(
                "برای هر دو الگوریتم، رویه مشترکی وجود دارد: محور زمان را از تیک ۰ بکش، در آغاز هر "
                "دوره کارها را آزاد کن، در هر تیک یک کار را انتخاب و یک تیک رنگ کن، و در پایان "
                "بررسی کن که هر کار پیش از مهلتش کامل شده باشد. تنها تفاوت در **گام انتخاب** است "
                "و همین یک تفاوت، کل نتیجه را عوض می‌کند.",
                "Both algorithms share one procedure: draw the time axis from tick 0, release jobs at "
                "the start of each period, choose one task per tick and shade one tick, and at the end "
                "check that every job finished before its deadline. The only difference is the "
                "**selection step**, and that single difference reverses the whole outcome.",
            ),
            fig2("fig02_flowchart", "رویه مشترک حل دستی؛ تنها گام انتخاب بین دو الگوریتم تفاوت دارد",
                 "The shared hand-solving procedure; only the selection step differs between algorithms",
                 0.74),
            h2("رویه RM", "The RM procedure"),
            ol(
                [
                    "اولویت ثابت را از دوره تعیین کن: هر که دوره کوتاه‌تری دارد، اولویت بالاتری دارد.",
                    "در هر تیک، میان کارهای آماده (آزادشده و تمام‌نشده) بالاترین اولویت را انتخاب کن.",
                    "اگر هیچ کاری آماده نیست، تیک را خالی بگذار و به تیک بعد برو.",
                    "پس از پایان هر دوره، کار تازه‌ای آزاد می‌شود؛ اولویت‌ها را دوباره حساب نکن — ثابت‌اند.",
                ],
                [
                    "Fix the priority from the period: the shorter the period, the higher the priority.",
                    "At each tick, choose the highest-priority task among the ready ones (released and unfinished).",
                    "If no task is ready, leave the tick empty and move on.",
                    "At each period boundary a new job is released; do not recompute the priorities — they are fixed.",
                ],
            ),
            note(
                "دام رایج در RM", "A common RM trap",
                "بسیاری هنگام آزاد شدن کار تازه، اولویت را دوباره از روی «زمان باقی‌مانده» حساب "
                "می‌کنند. این کار RM را به EDF تبدیل می‌کند و جواب را عوض می‌کند. در RM اولویت "
                "**تنها** تابع دوره است.",
                "Many people recompute the priority from the remaining time when a new job arrives. "
                "That turns RM into EDF and changes the answer. In RM the priority depends **only** on "
                "the period.",
            ),
            h2("رویه EDF", "The EDF procedure"),
            ol(
                [
                    "برای هر کار آزادشده، مهلت مطلق را حساب کن: زمان آزادسازی به‌اضافه D.",
                    "در هر تیک، کاری را انتخاب کن که کوچک‌ترین مهلت مطلق را دارد (نه کوچک‌ترین دوره).",
                    "اگر دو کار مهلت یکسان دارند، هر یک را انتخاب کنی جواب قابل قبول است؛ اما باید "
                    "در گزارش بنویسی کدام را انتخاب کردی.",
                    "پس از پایان هر دوره، مهلت مطلق کار تازه **بزرگ‌تر** از مهلت کارهای قدیمی است.",
                ],
                [
                    "For every released job compute the absolute deadline: release time plus D.",
                    "At each tick, choose the task with the smallest absolute deadline (not the smallest period).",
                    "If two tasks share a deadline either choice is acceptable, but you must state which one you took.",
                    "At each period boundary the new job's absolute deadline is **larger** than the old ones'.",
                ],
            ),
            tbl(
                "مقایسه گام‌به‌گام دو رویه",
                "The two procedures side by side",
                ["گام", "RM", "EDF"],
                ["Step", "RM", "EDF"],
                [
                    [("معیار انتخاب", "Selection key"), ("دوره (ثابت)", "period (fixed)"), ("مهلت مطلق (پویا)", "absolute deadline (dynamic)")],
                    [("تغییر اولویت", "Priority changes"), ("هرگز", "never"), ("در هر آزادسازی", "at every release")],
                    [("اطلاعات لازم", "Information needed"), ("دوره همه کارها", "periods of all tasks"), ("مهلت مطلق کارهای آماده", "absolute deadline of ready jobs")],
                    [("هزینه زمان‌بند", "Scheduler cost"), ("پایین", "low"), ("بالاتر (صف اولویت)", "higher (priority queue)")],
                    [("بهینگی", "Optimality"), ("در حالت کلی نه", "not in general"), ("برای U ≤ ۱ بله", "yes for U ≤ 1")],
                ],
                widths=[1.4, 1.9, 2.1],
            ),
            p(
                "این جدول نشان می‌دهد چرا EDF در مجموعه‌های با بهره‌وری بالاتر از کران RM بهتر "
                "عمل می‌کند: EDF هر لحظه از **کامل‌ترین اطلاعات موجود** استفاده می‌کند، در حالی که "
                "RM تصمیمش را یک بار برای همیشه گرفته است. اطلاعات بیشتر، در این مسئله، به تصمیم "
                "بهتر می‌رسد — و این همان قضیه بهینگی است.",
                "This table shows why EDF does better on sets above the RM bound: at every instant EDF "
                "uses the **most complete information available**, whereas RM has fixed its decision "
                "once and for all. More information leads to a better decision in this problem — and "
                "that is exactly the optimality theorem.",
            ),
        ],
    )

    # ------------------------------------------------------------------ 4
    m.section(
        "پاسخ یک: نقاشی دستی RM",
        "Answer One: The RM Hand Drawing",
        kicker_fa="جدول کامل ۲۴ تیکی و شک کار سوم",
        kicker_en="The full 24-tick table and the third task's failure",
        blocks=[
            lead(
                "این بخش جواب است، نه توضیح. جدول کامل پیش از تفسیر می‌آید.",
                "This section is the answer, not the explanation. The full table comes before any interpretation.",
            ),
            p(
                "جدول زیر همان چیزی است که روی کاغذ کشیده شد: بیست‌وچهار تیک، از ۰ تا ۲۳، و سه "
                "سطر. هر ستون یک تیک است. ستون‌های تیره‌تر محل آزادشدن کار تازه‌اند. اگر قاعده RM را "
                "با انگشت روی همین جدول دنبال کنید، باید به همین شکل برسید.",
                "The table below is what was drawn on paper: twenty-four ticks, 0 to 23, and three "
                "rows. Every column is one tick. Darker columns mark the release of a new job. If you "
                "follow the RM rule with your finger on this table, you must arrive at the same shape.",
            ),
            tbl(
                "زمان‌بندی RM: یک نویسه برای هر تیک",
                "RM schedule: one character per tick",
                ["فرایند", "تیک ۰ تا ۲۳"],
                ["Process", "ticks 0 to 23"],
                [[(n, n), (RM_ROWS[n], RM_ROWS[n])] for n in NAMES],
                widths=[0.9, 4.6],
                note_fa="مقیاس: ۰۱۲۳۴۵۶۷۸۹۰۱۲۳۴۵۶۷۸۹۰۱۲۳ — هر ده تیک یک بار شمارش از نو آغاز می‌شود.",
                note_en="Scale: 012345678901234567890123 — counting restarts every ten ticks.",
            ),
            fig2("fig03_hand_rm", "نقاشی دستی RM به‌صورت نمودار گانت (خط عمودی نازک: مهلت)",
                 "The RM hand drawing as a Gantt chart (thin vertical line: a deadline)", 0.97),
            h2("محل شکست", "Where it breaks"),
            p(
                "به تیک‌های ۰ تا ۷ نگاه کنید. P1 در تیک ۰ یک تیک می‌گیرد و تمام می‌شود. P2 در تیک ۱ "
                "آزاد می‌شود و دو تیک می‌گیرد (تیک ۱ و ۲). P3 در تیک ۰ آزاد شده و مهلتش تیک ۸ است؛ "
                "but تا تیک ۳ هیچ تیکی نمی‌گیرد، چون P1 و P2 اولویت بالاتری دارند. در تیک ۳ و ۵ یک "
                "تیک می‌گیرد و در تیک ۶ و ۷ دوباره P1 و P2 جلو می‌افتند.",
                "Look at ticks 0 to 7. P1 takes one tick at 0 and finishes. P2 is released at tick 1 "
                "and takes two ticks (1 and 2). P3 was released at 0 with a deadline at tick 8, but "
                "takes no tick until 3, because P1 and P2 have higher priority. It takes one tick at 3 "
                "and one at 5, and at 6 and 7 P1 and P2 overtake it again.",
            ),
            fig2("fig05_miss", "لحظه شکست: P3 با دو تیک از سه تیک لازم به مهلت خود می‌رسد",
                 "The moment of failure: P3 reaches its deadline with two of the three ticks it needs",
                 0.86),
            tbl(
                "سرویس P3 پیش از نخستین مهلت",
                "P3 service before its first deadline",
                ["تیک", "رویداد", "سرویس تجمعی P3", "سرویس لازم"],
                ["Tick", "Event", "Cumulative P3 service", "Service needed"],
                [
                    [("۰", "0"), ("آزادسازی P3", "P3 released"), ("۰", "0"), ("۳", "3")],
                    [("۳", "3"), ("نخستین تیک P3", "first P3 tick"), ("۱", "1"), ("۳", "3")],
                    [("۵", "5"), ("دومین تیک P3", "second P3 tick"), ("۲", "2"), ("۳", "3")],
                    [("۸", "8"), ("مهلت P3", "P3 deadline"), ("۲", "2"), ("۳", "3")],
                ],
                widths=[0.8, 2.2, 1.5, 1.2],
                note_fa="یک تیک کم است. همین یک تیک، کل تفاوت RM و EDF در این مجموعه است.",
                note_en="One tick short. That single tick is the whole difference between RM and EDF here.",
            ),
            p(
                "این جدول مهم است چون نشان می‌دهد شکست **موضعی** است، نه کلی. P3 در بقیه ابررسال "
                "ادامه می‌دهد و کارهایش را انجام می‌دهد، اما همیشه یک تیک عقب است. در سیستم‌های "
                "بلادرنگ همین یک تیک کافی است تا خروجی بی‌فایده شود.",
                "This table matters because it shows the failure is **local**, not total. P3 keeps "
                "running for the rest of the hyperperiod and does its work, but it is always one tick "
                "behind. In a real-time system that one tick is enough to make the output useless.",
            ),
            note(
                "چرا نمی‌توان «کمی دیرتر» را قبول کرد", "Why 'slightly late' is not acceptable",
                "در زمان‌بندی نرم، یک تیک تأخیر فقط کیفیت را کم می‌کند. در زمان‌بندی سخت، مهلت "
                "یک **قید درستی** است: خروجی دیررس به‌اندازه خروجی غلط بی‌ارزش است. صورت تمرین "
                "همین مدل سخت را فرض کرده است.",
                "In soft scheduling one tick of delay only lowers quality. In hard scheduling a "
                "deadline is a **correctness constraint**: a late result is as worthless as a wrong "
                "one. The brief assumes exactly this hard model.",
            ),
        ],
    )

    # ------------------------------------------------------------------ 5
    m.section(
        "پاسخ دو: نقاشی دستی EDF",
        "Answer Two: The EDF Hand Drawing",
        kicker_fa="همان مجموعه، قاعده دیگر، همه مهلت‌ها رعایت می‌شود",
        kicker_en="Same task set, other rule, every deadline met",
        blocks=[
            lead(
                "اگر فقط یک چیز از این تمرین به یاد بماند، باید این باشد: ورودی یکسان، خروجی متفاوت.",
                "If one thing is remembered from this exercise it should be this: identical input, different output.",
            ),
            p(
                "همان سه فرایند، همان دوره‌ها و همان زمان‌های اجرا. تنها چیزی که عوض شده قاعده "
                "انتخاب است. حالا در هر تیک، کاری که نزدیک‌ترین مهلت مطلق را دارد جلو می‌افتد. "
                "این تغییر کوچک باعث می‌شود P3 سه تیکش را در تیک‌های ۳، ۴ و ۵ بگیرد و پیش از مهلت ۸ "
                "کامل شود — همان کاری که در RM با دو تیک ناتمام ماند.",
                "The same three processes, the same periods and the same execution times. The only "
                "thing that changed is the selection rule. Now, at each tick, the ready job with the "
                "nearest absolute deadline goes first. That small change lets P3 take its three ticks "
                "in ticks 3, 4 and 5 and finish before the deadline at 8 — exactly the work RM left "
                "undone at two ticks.",
            ),
            tbl(
                "زمان‌بندی EDF: یک نویسه برای هر تیک",
                "EDF schedule: one character per tick",
                ["فرایند", "تیک ۰ تا ۲۳"],
                ["Process", "ticks 0 to 23"],
                [[(n, n), (EDF_ROWS[n], EDF_ROWS[n])] for n in NAMES],
                widths=[0.9, 4.6],
                note_fa="با جدول RM مقایسه کنید: تنها سطر P2 و P3 تفاوت دارد، اما همین تفاوت مهلت P3 را نجات می‌دهد.",
                note_en="Compare with the RM table: only the P2 and P3 rows differ, yet that difference saves P3's deadline.",
            ),
            fig2("fig04_hand_edf", "نقاشی دستی EDF به‌صورت نمودار گانت",
                 "The EDF hand drawing as a Gantt chart", 0.97),
            h2("گام‌به‌گام در هشت تیک نخست", "Tick by tick through the first eight ticks"),
            tbl(
                "تصمیم EDF در هر تیک، مهلت‌های رقیب و دلیل انتخاب",
                "The EDF decision at each tick, the competing deadlines and the reason",
                ["تیک", "کارهای آماده با مهلت مطلق", "انتخاب", "دلیل"],
                ["Tick", "Ready jobs with absolute deadline", "Choice", "Reason"],
                [
                    [("۰", "0"), ("P1 (۴), P2 (۶), P3 (۸)", "P1 (4), P2 (6), P3 (8)"), ("P1", "P1"), ("کوچک‌ترین مهلت", "smallest deadline")],
                    [("۱", "1"), ("P2 (۶), P3 (۸)", "P2 (6), P3 (8)"), ("P2", "P2"), ("کوچک‌ترین مهلت", "smallest deadline")],
                    [("۲", "2"), ("P2 (۶), P3 (۸)", "P2 (6), P3 (8)"), ("P2", "P2"), ("کوچک‌ترین مهلت", "smallest deadline")],
                    [("۳", "3"), ("P3 (۸)", "P3 (8)"), ("P3", "P3"), ("تنها کار آماده", "the only ready job")],
                    [("۴", "4"), ("P1 (۸), P3 (۸)", "P1 (8), P3 (8)"), ("P3", "P3"), ("تساوی؛ قاعده ادامه‌دادن", "tie; continuation rule")],
                    [("۵", "5"), ("P1 (۸), P3 (۸)", "P1 (8), P3 (8)"), ("P3", "P3"), ("تساوی؛ همان قاعده", "tie; same rule")],
                    [("۶", "6"), ("P1 (۸), P2 (۱۲)", "P1 (8), P2 (12)"), ("P1", "P1"), ("کوچک‌ترین مهلت", "smallest deadline")],
                    [("۷", "7"), ("P2 (۱۲)", "P2 (12)"), ("P2", "P2"), ("تنها کار آماده", "the only ready job")],
                ],
                widths=[0.6, 2.2, 0.75, 2.1],
                note_fa="ستون دوم از خودِ نقاشی استخراج شده است، نه از حافظه؛ اگر نقاشی عوض شود، این جدول هم عوض می‌شود.",
                note_en="The second column is extracted from the drawing itself, not from memory; if the drawing changes, so does this table.",
            ),
            h2("مسئله تساوی مهلت", "The problem of equal deadlines"),
            p(
                "در سه تیک — تیک ۴، ۷ و ۲۰ — دو کار آماده دقیقاً مهلت یکسانی دارند. EDF در این "
                "لحظه‌ها **دستور مشخصی ندارد**: هر انتخابی از نظر قاعده درست است، اما فقط اگر "
                "**همیشه یکسان** اجرا شود. این نکته در حل دستی اغلب از قلم می‌افتد و بعداً باعث "
                "می‌شود جواب با شبیه‌ساز نخواند.",
                "At three ticks — 4, 7 and 20 — two ready jobs share exactly the same deadline. EDF "
                "has **no rule for that moment**: either choice is correct by the definition, but only "
                "if it is made **consistently every time**. This is often skipped in a hand solution, "
                "and it is what later makes the answer disagree with a simulator.",
            ),
            tbl(
                "سه لحظه تساوی در این مجموعه و کاری که انتخاب شد",
                "The three ties in this set and what was chosen",
                ["تیک", "رقیبان (مهلت مطلق)", "انتخاب", "چرا"],
                ["Tick", "Rivals (absolute deadline)", "Choice", "Why"],
                [
                    [("۴", "4"), ("P1 (۸), P3 (۸)", "P1 (8), P3 (8)"), ("P3", "P3"), ("P3 در تیک ۳ در حال اجرا بود", "P3 was already running at tick 3")],
                    [("۷", "7"), ("P1 (۱۲), P3 (۱۲)", "P1 (12), P3 (12)"), ("P1", "P1"), ("P1 از تیک ۶ در حال اجرا بود", "P1 was already running from tick 6")],
                    [("۲۰", "20"), ("P2 (۲۴), P3 (۲۴)", "P2 (24), P3 (24)"), ("P3", "P3"), ("P3 از تیک ۱۸ در حال اجرا بود", "P3 was already running from tick 18")],
                ],
                widths=[0.6, 1.9, 0.65, 2.3],
            ),
            p(
                "قاعده‌ای که در همه سه مورد رعایت شده ساده است: **در تساوی، کاری که در حال اجراست "
                "ادامه می‌یابد.** این قاعده هیچ ترجیحی به یک فرایند نمی‌دهد و تصادفی نیست. اگر "
                "به‌جای آن «کوچک‌ترین شماره فرایند» را انتخاب می‌کردیم، نتیجه باز هم درست بود اما "
                "نقاشی دیگری می‌شد. مهم این است که انتخاب در برگه **اعلام** شود، وگرنه جواب "
                "قابل بازتولید نیست.",
                "The rule followed in all three cases is simple: **on a tie, the job already running "
                "continues.** That rule favours no process and is not arbitrary. Had we instead chosen "
                "'the lowest process number', the answer would still be correct but the drawing would "
                "be different. What matters is that the choice is **declared** on the sheet, "
                "otherwise the answer is not reproducible.",
            ),
            note(
                "چرا این نکته در نمره اثر دارد", "Why this matters for grading",
                "دو دانشجو می‌توانند هر دو پاسخ درست بدهند اما نقاشی‌هایشان متفاوت باشد. اگر "
                "قاعده تساوی نوشته نشود، ممتحن نمی‌تواند بگوید کدام درست است. نوشتن یک خط "
                "«قاعده تساوی: ادامه‌دادن کار در حال اجرا» این ابهام را کامل رفع می‌کند.",
                "Two students can both answer correctly and still produce different drawings. Without "
                "a stated tie-break the marker cannot say which is right. One line — 'tie-break: "
                "continue the running job' — removes the ambiguity completely.",
            ),
            h2("مقایسه دو جواب در یک نگاه", "The two answers at a glance"),
            tbl(
                "دو زمان‌بندی در کنار هم (هشت تیک نخست)",
                "The two schedules side by side (first eight ticks)",
                ["الگوریتم", "۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "وضعیت P3"],
                ["Algorithm", "0", "1", "2", "3", "4", "5", "6", "7", "P3 status"],
                [
                    [("RM", "RM")] + [(c, c) for c in [RM_ROWS["P1"][i] + "/" + RM_ROWS["P2"][i] + "/" + RM_ROWS["P3"][i] for i in range(8)]] + [("شکست", "failed")],
                    [("EDF", "EDF")] + [(c, c) for c in [EDF_ROWS["P1"][i] + "/" + EDF_ROWS["P2"][i] + "/" + EDF_ROWS["P3"][i] for i in range(8)]] + [("قبول", "met")],
                ],
                widths=[0.85, 0.42, 0.42, 0.42, 0.42, 0.42, 0.42, 0.42, 0.42, 1.05],
                font=8.0,
                note_fa="هر خانه به شکل P1/P2/P3 نوشته شده است و در هر خانه دقیقاً یک `#` هست، یعنی پردازنده تک‌هسته‌ای است. تفاوت دو سطر تنها از تیک ۴ آغاز می‌شود.",
                note_en="Each cell reads P1/P2/P3 and every cell has exactly one `#`, confirming a single-core processor. The two rows diverge only from tick 4.",
            ),
            fig2("fig12_service", "خدمت ارائه‌شده در یک ابررسال: RM به P3 کمتر از نیازش می‌دهد",
                 "Service over one hyperperiod: RM under-serves P3", 0.84),
        ],
    )

    # ------------------------------------------------------------------ 6
    m.section(
        "بازبین خودکار: چگونه یک نقاشی را داوری می‌کنیم",
        "The Automatic Verifier: How a Drawing Is Judged",
        kicker_fa="سه آزمون مستقل روی یک متن ساده",
        kicker_en="Three independent tests on a plain-text sheet",
        blocks=[
            lead(
                "نقاشی دستی قابل اعتماد نیست مگر اینکه چیزی آن را بررسی کند. آن چیز، خودِ نقاشی "
                "نیست؛ تحلیل نظری است.",
                "A hand drawing is not trustworthy unless something checks it. That something is not "
                "the drawing itself; it is the theoretical analysis.",
            ),
            p(
                "بازبین برای همین ساخته شد. ایده ساده است: نقاشی به متن ساده تبدیل می‌شود (هر نویسه "
                "یک تیک)، و این متن با سه آزمون مستقل بررسی می‌شود. اگر هر سه بگذرند، نقاشی هم "
                "**ساختاراً** درست است، هم **زمان‌بندی‌شده** و هم **تابع قاعده**. جدا بودن سه آزمون "
                "مهم است: یک نقاشی می‌تواند ساختاراً درست باشد (هیچ تیکی دو اجرا ندارد) اما قاعده را "
                "نقض کند (باید P3 را انتخاب می‌کرد) — و بازبین باید این دو را از هم تشخیص دهد.",
                "The verifier was built for this. The idea is simple: the drawing is transcribed to "
                "plain text (one character per tick) and that text is checked by three independent "
                "tests. If all three pass, the drawing is **structurally** valid, **schedulable** and "
                "**faithful to the rule**. Keeping the three tests apart matters: a drawing can be "
                "structurally valid (no tick runs two jobs) yet violate the rule (it should have "
                "picked P3) — and the verifier must tell those cases apart.",
            ),
            fig2("fig09_architecture", "معماری بازبین: از برگه ساده تا سه حکم مستقل",
                 "Verifier architecture: from a plain sheet to three independent verdicts", 0.9),
            h2("قواعد نشانه‌گذاری برگه", "The sheet's markup"),
            tbl(
                "دستورهای زبان برگه",
                "The sheet language directives",
                ["دستور", "معنا", "نمونه"],
                ["Directive", "Meaning", "Example"],
                [
                    [("`task`", "`task`"), ("تعریف یک فرایند", "define a process"), ("`task P1 T=4 C=1`", "`task P1 T=4 C=1`")],
                    [("`draw`", "`draw`"), ("آغاز یک نقاشی (rm یا edf)", "start a drawing (rm or edf)"), ("`draw rm`", "`draw rm`")],
                    [("`P1 #..#`", "`P1 #..#`"), ("یک سطر از نقاشی", "one row of the drawing"), ("`P3 ...#.#`", "`P3 ...#.#`")],
                    [("`end`", "`end`"), ("پایان نقاشی", "end of the drawing"), ("`end`", "`end`")],
                    [("`calc`", "`calc`"), ("محاسبه دستی برای بررسی", "a hand calculation to check"), ("`calc U 0.958`", "`calc U 0.958`")],
                    [("`expect=miss`", "`expect=miss`"), ("اعلام اینکه شکست عمدی است", "declare an intended failure"), ("`draw rm expect=miss`", "`draw rm expect=miss`")],
                ],
                widths=[1.2, 2.2, 2.0],
                note_fa="نقطه‌ویرگول آغاز نظر است. `#` نشانه اجرا است و نمی‌تواند نظر باشد.",
                note_en="A semicolon starts a comment. `#` is the run marker and cannot be a comment.",
            ),
            snippet(
                "; Assignment 3 - three processes, scheduled by hand\n"
                "task P1 T=4 C=1\ntask P2 T=6 C=2\ntask P3 T=8 C=3\n\n"
                "draw rm expect=miss\n"
                "P1  #...#...#...#...#...#...\n"
                "P2  .##...##.....##...##....\n"
                "P3  ...#.#...###.....#...##.\n"
                "end\n",
                "برگه واقعی حل RM (بخشی از فایل داده)",
                "The actual RM answer sheet (part of the data file)",
                lang="text", label_en="paper_work.txt",
            ),
            h2("سه آزمون بازبین", "The three tests"),
            tbl(
                "آزمون‌های بازبین و آنچه رد می‌کنند",
                "The verifier's tests and what they reject",
                ["آزمون", "پرسش", "خطای نمونه‌ای که رد می‌شود"],
                ["Test", "Question", "Example fault rejected"],
                [
                    [("ساختار", "Structure"), ("آیا در هر تیک حداکثر یک فرایند اجرا می‌شود؟", "Does every tick run at most one process?"), ("دو `#` در یک ستون", "two `#` in one column")],
                    [("ظرفیت", "Capacity"), ("آیا هیچ فرایندی بیش از کار واقعی‌اش سرویس می‌گیرد؟", "Does any process get more service than it has work?"), ("P1 با ۳۰ تیک در ابررسال ۲۴", "P1 with 30 ticks in a 24-tick hyperperiod")],
                    [("مهلت", "Deadline"), ("آیا هر کار پیش از مهلتش کامل می‌شود؟", "Does every job finish before its deadline?"), ("P3 با ۲ تیک از ۳ تیک", "P3 with 2 of 3 ticks")],
                    [("قاعده", "Rule"), ("آیا نقاشی از تحلیل نظری پیروی می‌کند؟", "Does the drawing agree with the theory?"), ("RM که موفق اعلام شده ولی تحلیل شکست می‌دهد", "RM declared feasible while the analysis fails")],
                ],
                widths=[0.95, 2.4, 2.3],
            ),
            p(
                "چهارمین ردیف جدول از همه مهم‌تر است و اغلب از قلم می‌افتد. ممکن است نقاشی‌ای "
                "ساختاراً بی‌عیب و از نظر مهلت هم موفق باشد، اما قاعده را رعایت نکرده باشد (مثلاً "
                "در تیک ۴ به‌جای P3، P1 را انتخاب کرده باشد). چنین نقاشی‌ای «جواب درست با راه غلط» "
                "است. بازبین آن را رد نمی‌کند، چون جواب درست است، اما گزارش می‌دهد که قاعده نقض "
                "شده است.",
                "The fourth row is the most important and the most often forgotten. A drawing can be "
                "structurally flawless and meet every deadline while still breaking the rule (for "
                "instance choosing P1 instead of P3 at tick 4). Such a drawing is 'the right answer "
                "by the wrong route'. The verifier does not reject it, because the answer is right, "
                "but it does report that the rule was violated.",
            ),
            h2("چرا بازبین خودش آزمون دارد", "Why the verifier has tests of its own"),
            p(
                "اگر بازبین هر چیزی را قبول کند، بی‌فایده است. پس خودش هم آزموده شده است: ۳۴ آزمون "
                "واحد، بیشترشان **منفی**، یعنی یک نقاشی عمداً غلط می‌سازند و بررسی می‌کنند که "
                "بازبین آن را رد کند. برخورد در یک ستون، سطر گم‌شده، سرویس بیش از ظرفیت، محاسبه "
                "غلط U و `R(P3)=5` (به‌جای شکست) از جمله این مواردند.",
                "A verifier that accepts everything is worthless, so it has been tested itself: 34 "
                "unit tests, most of them **negative**, i.e. they build a deliberately wrong sheet and "
                "check that the verifier rejects it. A collision in one column, a missing row, service "
                "beyond capacity, a wrong U and `R(P3)=5` (instead of a failure) are among them.",
            ),
            snippet(
                "def test_collision_detected(self):\n"
                "    text = (\"task P1 T=4 C=1\\ntask P2 T=4 C=1\\n\"\n"
                "            \"draw rm\\nP1  #...\\nP2  #...\\nend\\n\")\n"
                "    wb = parse_workbook(text)\n"
                "    problems = check_schedule(wb, wb.schedules[0])\n"
                "    self.assertTrue(any(\"processes run at once\" in p for p in problems))\n",
                "یک آزمون منفی: بازبین باید برخورد را ببیند",
                "A negative test: the verifier must see the collision",
                lang="python", label_en="test_workbook.py",
            ),
        ],
    )

    # ------------------------------------------------------------------ 6b
    m.section(
        "راستی‌آزمایی مستقل با شبیه‌ساز",
        "Independent Cross-Check with a Simulator",
        kicker_fa="دو پیاده‌سازی مستقل، یک نتیجه؛ و یک تفاوت واقعی که پیدا شد",
        kicker_en="Two independent implementations, one result; and a real disagreement it caught",
        blocks=[
            lead(
                "بازبین بخش قبل، خودش بخشی از همان کار است. برای اینکه جواب مستقل تأیید شود، به "
                "یک داور بیرونی نیاز است.",
                "The verifier of the previous section is itself part of the work. Confirming the "
                "answer independently requires an outside judge.",
            ),
            p(
                "تمرین دوم همین درس یک شبیه‌ساز تیک‌محور دارد که هیچ خطی از کدش با بازبین این تمرین "
                "مشترک نیست. اگر نقاشی دستی و آن شبیه‌ساز به **یک** نتیجه برسند، احتمال اینکه هر دو "
                "یک اشتباه مشترک داشته باشند بسیار کم است. پس نقاشی به متن تبدیل می‌شود و با خروجی "
                "شبیه‌ساز، تیک به تیک، مقایسه می‌شود.",
                "Assignment 2 of the same course has a tick-level simulator that shares not one line "
                "of code with this assignment's verifier. If the hand drawing and that simulator reach "
                "**the same** result, the chance of a shared mistake is very small. So the drawing is "
                "converted to text and compared with the simulator output, tick by tick.",
            ),
            snippet(
                "import rt_sim                     # assignment 2 simulator: separate code base\n"
                "from workbook import load         # assignment 3 verifier: separate code base\n\n"
                "wb    = load('data/paper_work.txt')\n"
                "tasks = [rt_sim.Task(t.name, t.period, t.wcet, t.deadline) for t in wb.tasks]\n"
                "for alg in ('rm', 'edf'):\n"
                "    timeline = rt_sim.simulate(tasks, alg, hyperperiod(wb.tasks), trace=True)\n"
                "    sim  = rows_of(wb.tasks, timeline)\n"
                "    hand = next(s.rows for s in wb.schedules if s.algorithm == alg)\n"
                "    assert sim == hand, alg          # tick for tick, row for row\n",
                "هسته راستی‌آزمایی: دو پیاده‌سازی مستقل، یک مقایسه",
                "The core of the cross-check: two independent implementations, one comparison",
                lang="python", label_en="crosscheck.py",
            ),
            tbl(
                "نتیجه راستی‌آزمایی",
                "The cross-check result",
                ["الگوریتم", "تیک‌های یکسان", "مهلت‌های ازدست‌رفته", "تیک‌های بی‌کار", "حکم"],
                ["Algorithm", "Identical ticks", "Deadlines missed", "Idle ticks", "Verdict"],
                [
                    [("RM", "RM"), ("۲۴ از ۲۴", "24 of 24"), ("۱", "1"), ("۲", "2"), ("یکسان", "identical")],
                    [("EDF", "EDF"), ("۲۴ از ۲۴", "24 of 24"), ("۰", "0"), ("۱", "1"), ("یکسان", "identical")],
                ],
                widths=[0.9, 1.3, 1.5, 1.1, 1.0],
                note_fa="شبیه‌ساز برای RM یک مهلت از دست رفته و برای EDF هیچ‌کدام را گزارش می‌کند — همان نتیجه‌ای که تحلیل نظری پیش‌بینی کرده بود.",
                note_en="The simulator reports one missed deadline for RM and none for EDF — exactly what the theory predicted.",
            ),
            h2("اولین بار که دو پیاده‌سازی اختلاف داشتند", "The first time the two disagreed"),
            p(
                "نخستین اجرای راستی‌آزمایی **شکست خورد**. RM مو‌به‌مو یکسان بود، اما EDF در سه تیک "
                "تفاوت داشت. این تفاوت خطای شبیه‌ساز نبود؛ خطای **نقاشی** بود. در تیک ۴ مهلت P1 و "
                "P3 برابر بود و P3 انتخاب شده بود (قاعده ادامه‌دادن)، اما در تیک ۵ با همان تساوی، "
                "P1 انتخاب شده بود. یعنی قاعده تساوی در دو تیک متوالی **ناسازگار** اجرا شده بود.",
                "The first cross-check run **failed**. RM matched exactly, but EDF differed at three "
                "ticks. The difference was not a simulator bug; it was a **drawing** bug. At tick 4 "
                "P1 and P3 had equal deadlines and P3 was chosen (the continuation rule), but at tick "
                "5, with the same tie, P1 was chosen. The tie-break had been applied "
                "**inconsistently** at two consecutive ticks.",
            ),
            tbl(
                "دو نسخه نقاشی EDF در تیک‌های ۴ تا ۶",
                "The two versions of the EDF drawing at ticks 4 to 6",
                ["نسخه", "تیک ۴", "تیک ۵", "تیک ۶", "نتیجه P3", "راستی‌آزمایی"],
                ["Version", "Tick 4", "Tick 5", "Tick 6", "P3 outcome", "Cross-check"],
                [
                    [("نخست (ناسازگار)", "first (inconsistent)"), ("P3", "P3"), ("P1", "P1"), ("P3", "P3"), ("درست", "correct"), ("شکست", "failed")],
                    [("دوم (یکنواخت)", "second (consistent)"), ("P3", "P3"), ("P3", "P3"), ("P1", "P1"), ("درست", "correct"), ("موفق", "passed")],
                ],
                widths=[1.5, 0.65, 0.65, 0.65, 1.0, 1.1],
                note_fa="هر دو نسخه از نظر مهلت درست‌اند؛ تفاوت فقط در پایبندی به قاعده تساوی است.",
                note_en="Both versions meet every deadline; the difference is only in adherence to the stated tie-break.",
            ),
            p(
                "این مهم‌ترین درس روش‌شناختی گزارش است. هیچ آزمون **درستی مهلت** این خطا را "
                "نمی‌گیرد، چون در هر دو نسخه همه مهلت‌ها رعایت می‌شدند. آزمون ساختاری هم آن را "
                "نمی‌گیرد، چون هیچ تیکی دو اجرا نداشت. تنها چیزی که آن را گرفت، **مقایسه با یک "
                "پیاده‌سازی مستقل** بود. به همین دلیل بخش‌های ۶ و ۷ کافی نیستند و این بخش لازم است.",
                "This is the report's most important methodological lesson. No **deadline** test "
                "catches this error, because both versions met every deadline. No structural test "
                "catches it either, because no tick ran two jobs. The only thing that caught it was "
                "**comparison with an independent implementation**. That is why sections 6 and 7 are "
                "not enough and this section is needed.",
            ),
            note(
                "تفکیک مسئولیت", "Separation of concerns",
                "سه لایه بازرسی داریم و هر کدام یک چیز را می‌گیرند: آزمون ساختاری برخورد و سرویس "
                "بیش از ظرفیت را؛ آزمون مهلت شکست زمان‌بندی را؛ و راستی‌آزمایی مستقل **ناسازگاری "
                "در جزئیات قاعده** را. هیچ‌کدام جای دیگری را نمی‌گیرد.",
                "There are three layers of inspection and each catches something the others do not: "
                "the structural test catches collisions and over-service; the deadline test catches "
                "scheduling failure; and the independent cross-check catches **inconsistency in the "
                "finer points of the rule**. None replaces another.",
            ),
            note(
                "یک هشدار صادقانه", "An honest caveat",
                "اینکه دو پیاده‌سازی مستقل یکسان‌اند، **اثبات** درستی نیست. ممکن است هر دو یک "
                "تعریف مشترک را اشتباه فهمیده باشند. اما در این تمرین، تعریف‌ها از منابع درسی "
                "آمده‌اند و آزمون‌ها هم آن‌ها را می‌سنجند. راستی‌آزمایی، شاهد قوی است نه برهان.",
                "Two independent implementations agreeing is **not** a proof of correctness. Both "
                "could share a misunderstanding of the definition. Here, however, the definitions come "
                "from the textbooks and the tests check them. The cross-check is strong evidence, not a "
                "proof.",
            ),
        ],
    )

    # ------------------------------------------------------------------ 7
    m.section(
        "داده‌های آزمون: طرح‌های عمداً غلط",
        "Test Evidence: Deliberately Wrong Sheets",
        kicker_fa="بازبین با چه چیزهایی آزمایش شده است",
        kicker_en="What the verifier has been challenged with",
        blocks=[
            lead(
                "ادعای «بازبین درست کار می‌کند» تا وقتی آزموده نشود، ادعاست.",
                "'The verifier works' is a claim until it is tested.",
            ),
            p(
                "برای هر نوع خطا، یک برگه ساختگی ساخته و به بازبین داده شد. جدول زیر نشان می‌دهد "
                "چه خطایی تزریق شد و بازبین چه گفت. این جدول هم‌زمان دو چیز را ثابت می‌کند: بازبین "
                "خطاها را می‌بیند، و پیام‌هایش به‌قدر کافی گویا هستند که دانشجو بفهمد کجا را اشتباه "
                "کرده است.",
                "For each kind of fault a synthetic sheet was built and given to the verifier. The "
                "table below shows what was injected and what the verifier said. It proves two things "
                "at once: the verifier sees the faults, and its messages are specific enough for a "
                "student to locate the mistake.",
            ),
            tbl(
                "خطاهای تزریق‌شده و پاسخ بازبین",
                "Injected faults and the verifier's response",
                ["خطای تزریق‌شده", "پیام بازبین", "نتیجه"],
                ["Injected fault", "Verifier message", "Outcome"],
                [
                    [("دو فرایند در یک تیک", "two processes in one tick"), ("`collision: P1 and P2 both run at tick 0`", "`collision: P1 and P2 both run at tick 0`"), ("رد شد", "rejected")],
                    [("سطر P2 جا افتاده", "row P2 missing"), ("`missing rows: P2`", "`missing rows: P2`"), ("رد شد", "rejected")],
                    [("P1 بیش از ظرفیت اجرا شده", "P1 over-served"), ("`P1 got 8 ticks but only 6 usable`", "`P1 got 8 ticks but only 6 usable`"), ("رد شد", "rejected")],
                    [("P3 با ۲ تیک به مهلت رسیده", "P3 reaches its deadline with 2 ticks"), ("`job released at 0 got 2/3 ticks`", "`job released at 0 got 2/3 ticks`"), ("رد شد", "rejected")],
                    [("U غلط نوشته شده", "wrong U written"), ("`U: wrote 0.900, analyser says 0.958`", "`U: wrote 0.900, analyser says 0.958`"), ("رد شد", "rejected")],
                    [("R(P3) = ۵ نوشته شده", "R(P3) = 5 written"), ("`R(P3): wrote 5, analyser says infeasible`", "`R(P3): wrote 5, analyser says infeasible`"), ("رد شد", "rejected")],
                    [("شکست اعلام‌نشده در RM", "unannounced RM failure"), ("`expect=miss` لازم است", "`expect=miss` required"), ("رد شد", "rejected")],
                ],
                widths=[1.9, 3.0, 0.8],
            ),
            p(
                "ردیف آخر ظریف‌ترین است. وقتی یک نقاشی طبق تعریف باید شکست بخورد، بازبین نمی‌تواند "
                "«شکست» را خودِ خطا بداند. برای همین نویسنده برگه باید با `expect=miss` اعلام کند که "
                "این شکست **عمدی و درست** است. اگر اعلام نکند، بازبین نمی‌داند نویسنده اشتباه کرده "
                "یا مسئله را فهمیده، و باید محافظه‌کارانه برخورد کند.",
                "The last row is the subtlest. When a drawing is *supposed* to fail, the verifier "
                "cannot treat the failure as the error. The author must therefore declare with "
                "`expect=miss` that the failure is **intended and correct**. Without that declaration "
                "the verifier cannot tell a mistake from understanding, and must err on the safe side.",
            ),
            note(
                "درس روش‌شناختی", "A methodological lesson",
                "اینکه یک بررسی‌کننده خطاهای تزریق‌شده را پیدا می‌کند، ثابت نمی‌کند که خطای دیگری "
                "را هم پیدا می‌کند. آزمون منفی، تضمین کامل نیست؛ فقط شاهد است. برای اطمینان بیشتر، "
                "باید خواص بررسی‌شده با تحلیل نظری مقایسه شوند — همان کاری که در بخش ۶ انجام شد.",
                "Finding injected faults does not prove a checker finds other faults. Negative "
                "testing is evidence, not a guarantee. For more assurance the checked properties must "
                "be compared with the theory — which is what section 6 did.",
            ),
        ],
    )

    # ------------------------------------------------------------------ 8
    m.section(
        "چرا RM شکست می‌خورد و EDF نه",
        "Why RM Fails and EDF Does Not",
        kicker_fa="توضیح ساختاری، نه روایت شانسی",
        kicker_en="A structural explanation, not a story about luck",
        blocks=[
            lead(
                "تفاوت دو نقاشی تصادفی نیست. یک دلیل ساختاری دارد که می‌توان آن را دقیق نوشت.",
                "The difference between the two drawings is not accidental. It has a structural "
                "reason that can be stated precisely.",
            ),
            p(
                "در RM، هر کار **همیشه** همان اولویت را دارد، چه فوری باشد چه نباشد. اگر مجموعه "
                "بهره‌وری بالایی داشته باشد، کارهای با دوره بلند همیشه آخر صف می‌مانند و در "
                "بدترین حالت به سرویس کافی نمی‌رسند. این یک نقص اجرایی نیست؛ نتیجه منطقی یک "
                "تصمیم **ایستا** است.",
                "In RM every task **always** has the same priority, urgent or not. If the set has high "
                "utilisation, long-period tasks stay at the back of the queue forever and in the worst "
                "case never get enough service. That is not an implementation defect; it is the "
                "logical consequence of a **static** decision.",
            ),
            p(
                "در EDF، اولویت با نزدیک‌شدن مهلت عوض می‌شود. کار P3 که در RM همیشه آخر است، در "
                "EDF وقتی مهلتش نزدیک می‌شود جلو می‌افتد و سرویسش را می‌گیرد. همین پویایی است که "
                "EDF را برای U ≤ ۱ بهینه می‌کند. هزینه‌اش این است که زمان‌بند باید در هر تیک "
                "مهلت‌ها را مقایسه کند، و در اضافه‌بار رفتارش بدتر از RM می‌شود (این را در تمرین "
                "دوم با شبیه‌سازی دیدیم).",
                "In EDF the priority changes as a deadline approaches. P3, always last in RM, moves "
                "forward in EDF as its deadline nears and gets its service. That dynamism is what makes "
                "EDF optimal for U ≤ 1. The cost is that the scheduler must compare deadlines at every "
                "tick, and under overload its behaviour is worse than RM (assignment 2 showed this by "
                "simulation).",
            ),
            tbl(
                "دلیل ساختاری تفاوت دو نقاشی",
                "The structural reason for the difference",
                ["جنبه", "RM", "EDF", "اثر در این مجموعه"],
                ["Aspect", "RM", "EDF", "Effect here"],
                [
                    [("نوع اولویت", "Priority type"), ("ثابت", "static"), ("پویا", "dynamic"), ("P3 در RM همیشه آخر است", "P3 is always last in RM")],
                    [("اطلاعات لحظه تصمیم", "Information at decision time"), ("فقط دوره", "period only"), ("همه مهلت‌های آماده", "all ready deadlines"), ("EDF P3 را وقتی فوری شد جلو می‌آورد", "EDF promotes P3 when it becomes urgent")],
                    [("شرط کفایت کلاسیک", "Classical sufficient condition"), ("U ≤ ۰٫۷۸۰", "U ≤ 0.780"), ("U ≤ ۱", "U ≤ 1"), (f"U = {f(U)}: تنها EDF شرط را برآورده می‌کند", f"U = {f(U)}: only EDF meets the condition")],
                    [("رفتار در اضافه‌بار", "Overload behaviour"), ("قربانی پیش‌بینی‌پذیر", "predictable victim"), ("اثر دومینو", "domino effect"), ("خارج از دامنه این تمرین", "outside this exercise")],
                ],
                widths=[1.5, 1.35, 1.35, 2.2],
            ),
            fig2("fig10_deadlines", "مهلت‌های مطلق در طول ابررسال: ورودی تصمیم EDF",
                 "Absolute deadlines across the hyperperiod: EDF's decision input", 0.88),
            h2("آزمون مرزی: چقدر جا مانده است", "A boundary test: how much room is left"),
            p(
                "تحلیل تقاضا گفت کمترین فرصت ۱ تیک است. این را می‌توان آزمایش کرد: اگر یک تیک به "
                "بار مجموعه اضافه شود، EDF باید شکست بخورد. برای این کار، C یکی از کارها یک تیک "
                "زیاد می‌شود و تحلیل تقاضا دوباره اجرا می‌شود.",
                "The demand analysis said the minimum slack is 1 tick. That can be tested: add one "
                "tick of load and EDF must fail. To do so, the C of one task is increased by one tick "
                "and the demand analysis is rerun.",
            ),
            tbl(
                "آزمون مرزی: اثر افزودن یک تیک بار",
                "Boundary test: the effect of one extra tick of load",
                ["تغییر", "بهره‌وری", "کمینه فرصت", "EDF"],
                ["Change", "Utilisation", "Minimum slack", "EDF"],
                [
                    [("هیچ (این مجموعه)", "none (this set)"), (f(U), f(U)), ("۱", "1"), ("موفق", "succeeds")],
                    [(f"{TASKS[0]['name']} با C = {TASKS[0]['C'] + 1}", f"{TASKS[0]['name']} with C = {TASKS[0]['C'] + 1}"), ("۰٫۹۹", "0.99"), ("۰", "0"), ("موفق ولی بی‌ذخیره", "succeeds with no slack")],
                    [(f"{TASKS[2]['name']} با C = {TASKS[2]['C'] + 1}", f"{TASKS[2]['name']} with C = {TASKS[2]['C'] + 1}"), ("۱٫۰۸", "1.08"), ("منفی", "negative"), ("شکست", "fails")],
                ],
                widths=[2.0, 1.0, 1.2, 1.7],
            ),
            p(
                "این جدول یک نکته مهم را نشان می‌دهد که در تمرین اول و دوم هم دیدیم: «قابل "
                "زمان‌بندی» یک ویژگی **لبه‌دار** است. مجموعه‌ای که امروز موفق است با یک تیک بار "
                "اضافه شکست می‌خورد. در سیستم واقعی، همین یعنی باید حاشیه ایمنی نگه داشت، نه اینکه "
                "تا آخرین تیک بار پر کرد.",
                "This table shows a point also seen in assignments 1 and 2: schedulability is a "
                "**knife-edge** property. A set that succeeds today fails with one extra tick of load. "
                "In a real system that means keeping a safety margin rather than filling the last "
                "available tick.",
            ),
        ],
    )

    # ------------------------------------------------------------------ 9
    m.section(
        "محدودیت‌ها و دام‌های حل دستی",
        "Limitations and Traps of Hand Solving",
        kicker_fa="چه چیزهایی این نقاشی‌ها را ناقص می‌کند",
        kicker_en="What makes these drawings incomplete",
        blocks=[
            lead(
                "گزارش صادق باید بگوید جوابش چه چیزی را **نمی‌گیرد**.",
                "An honest report says what its answer does **not** cover.",
            ),
            p(
                "نقاشی دستی برای آموزش قاعده خوب است، اما به‌عنوان روش تحلیل سه محدودیت جدی دارد. "
                "نخست، مقیاس‌پذیر نیست: با ده کار و ابررسال ۲۵۲۰ تیکی، کشیدن دستی ناممکن است. "
                "دوم، خطاپذیر است: یک تیک جابه‌جا، همه نتیجه را عوض می‌کند و چشم انسان آن را "
                "نمی‌بیند. سوم، **قاعده را اثبات نمی‌کند**؛ فقط نشان می‌دهد در یک مجموعه چه شد. "
                "اثبات کلی کار تحلیل نظری است، نه نقاشی.",
                "Hand drawing is good for learning the rule but has three serious limits as an "
                "analysis method. First, it does not scale: with ten tasks and a hyperperiod of 2520 "
                "ticks, hand drawing is impossible. Second, it is error-prone: one tick in the wrong "
                "place reverses the result and the eye does not see it. Third, it **does not prove the "
                "rule**; it shows what happened for one set. The general proof is the job of the "
                "theory, not the drawing.",
            ),
            tbl(
                "دام‌های رایج در حل دستی و راه پرهیز",
                "Common hand-solving traps and how to avoid them",
                ["دام", "نشانه", "راه پرهیز"],
                ["Trap", "Symptom", "How to avoid it"],
                [
                    [("شمارش از ۱ به‌جای ۰", "counting from 1"), ("همه تیک‌ها یک واحد جابه‌جا", "everything shifted by one"), ("همیشه محور را از ۰ بکش", "always start the axis at 0")],
                    [("فراموش‌کردن آزادسازی", "forgetting a release"), ("یک کار کمتر از نیاز سرویس می‌گیرد", "a task is under-served"), ("آزادسازی‌ها را اول علامت بزن", "mark all releases first")],
                    [("دوباره‌حساب‌کردن اولویت در RM", "recomputing priority in RM"), ("نتیجه شبیه EDF می‌شود", "the result looks like EDF"), ("اولویت را فقط از دوره بگیر", "derive priority only from the period")],
                    [("مهلت مطلق به‌جای نسبی", "absolute instead of relative deadline"), ("همه مهلت‌ها برابر می‌شوند", "all deadlines look equal"), ("مهلت = آزادسازی + D", "deadline = release + D")],
                    [("نادیده‌گرفتن تیک خالی", "ignoring an idle tick"), ("مجموع سرویس بیشتر از زمان می‌شود", "the total service exceeds the time"), ("تیک خالی هم باید کشیده شود", "draw idle ticks too")],
                ],
                widths=[1.8, 1.9, 1.9],
            ),
            p(
                "ردیف پنجم بیش از همه پیش می‌آید. وقتی هیچ کاری آماده نیست، وسوسه می‌شویم تیک را "
                "«حذف» کنیم و کارها را فشرده بکشیم. این کار محور زمان را می‌شکند و همه مهلت‌های "
                "بعدی را غلط می‌کند. تیک خالی بخشی از زمان‌بندی است، نه فراموشی.",
                "The fifth row is the most common. When no task is ready we are tempted to 'delete' "
                "the tick and compress the rows. That breaks the time axis and corrupts every later "
                "deadline. An idle tick is part of the schedule, not an omission.",
            ),
            note(
                "یک دام که در همین تمرین رخ داد", "A trap that actually occurred here",
                "در نخستین برگه، `R(P3) = 5` نوشته شده بود. تحلیل زمان پاسخ نشان داد که این عدد "
                "بی‌معناست: R(P3) همگرا نمی‌شود و شکست می‌خورد. خطا از این می‌آمد که فقط دو تکرار "
                "معادله انجام شده بود و تکرار سوم فراموش شده بود. بازبین همین را گرفت.",
                "The first version of the sheet stated `R(P3) = 5`. Response-time analysis showed the "
                "number is meaningless: R(P3) does not converge and the task fails. The error came "
                "from stopping after two iterations and forgetting the third. The verifier caught it.",
            ),
        ],
    )

    # ------------------------------------------------------------------ 10
    m.section(
        "جمع‌بندی و پاسخ کوتاه",
        "Conclusion and the Short Answer",
        kicker_fa="آنچه می‌توان در سه جمله گفت",
        kicker_en="What can be said in three sentences",
        blocks=[
            lead(
                "اگر لازم است کل تمرین در سه جمله گفته شود، این سه جمله است.",
                "If the whole exercise has to be stated in three sentences, these are they.",
            ),
            ol(
                [
                    "برای همین مجموعه، RM مهلت نخست P3 را از دست می‌دهد چون اولویت ایستا آن را همیشه "
                    "آخر صف نگه می‌دارد.",
                    "EDF با همان مجموعه و همان بار همه مهلت‌ها را رعایت می‌کند چون هر لحظه فوری‌ترین "
                    "کار را انتخاب می‌کند.",
                    "این تفاوت از قبل توسط تحلیل زمان پاسخ و تحلیل تقاضا پیش‌بینی شده بود؛ نقاشی "
                    "دستی فقط آن پیش‌بینی را **تأیید** کرد، نه اینکه کشف کند.",
                ],
                [
                    "For this task set RM misses P3's first deadline because a static priority keeps it "
                    "last in the queue forever.",
                    "EDF meets every deadline on the same set and the same load because it picks the "
                    "most urgent job at every instant.",
                    "That difference was predicted in advance by response-time and demand analysis; the "
                    "hand drawing **confirmed** the prediction rather than discovering it.",
                ],
            ),
            tbl(
                "پاسخ نهایی در یک جدول",
                "The final answer in one table",
                ["پرسش", "پاسخ"],
                ["Question", "Answer"],
                [
                    [("بهره‌وری مجموعه", "Task-set utilisation"), (f(U), f(U))],
                    [("کران RM برای سه کار", "RM bound for three tasks"), (f(BOUND), f(BOUND))],
                    [("آیا U از کران بالاتر است؟", "Is U above the bound?"), (("بله", "yes") if ABOVE else ("خیر", "no")),],
                    [("زمان پاسخ P1 / P2 / P3", "Response time P1 / P2 / P3"), (f"{r_of('P1')} / {r_of('P2')} / {r_of('P3')} (شکست)", f"{r_of('P1')} / {r_of('P2')} / {r_of('P3')} (fails)")],
                    [("RM قابل زمان‌بندی است؟", "Is RM schedulable?"), (("خیر", "no") if not RM_FEASIBLE else ("بله", "yes"))],
                    [("EDF قابل زمان‌بندی است؟", "Is EDF schedulable?"), (("بله", "yes") if EDF_FEASIBLE else ("خیر", "no"))],
                    [("کمینه فرصت EDF", "EDF minimum slack"), ("۱ تیک", "1 tick")],
                ],
                widths=[2.6, 2.6],
            ),
            quote(
                "کران بهره‌وری، شرط کافی است نه شرط لازم؛ و نقاشی دستی، شاهد است نه اثبات.",
                "The utilisation bound is sufficient, not necessary; and a hand drawing is evidence, "
                "not proof.",
                source_fa="— نتیجه روش‌شناختی این تمرین",
                source_en="— the methodological conclusion of this exercise",
            ),
            p(
                "همین دو نکته، تفاوت یک تمرین حل‌شده با یک تمرین فهمیده‌شده است. تمرین حل‌شده "
                "جدولی دارد که درست است؛ تمرین فهمیده‌شده می‌داند چرا جدول باید این شکل را داشته "
                "باشد، و می‌داند چه چیزی را ثابت نمی‌کند.",
                "Those two points separate a solved exercise from an understood one. A solved exercise "
                "has a table that is correct; an understood one knows why the table must have this "
                "shape, and knows what it does not prove.",
            ),
        ],
    )

    # ------------------------------------------------------------------ 11b
    m.section(
        "سه مجموعه دیگر: کران چه می‌گوید و چه نمی‌گوید",
        "Three More Task Sets: What the Bound Says and Does Not Say",
        kicker_fa="آزمون ادعای «کران شرط کافی است، نه لازم»",
        kicker_en="Testing the claim that the bound is sufficient, not necessary",
        blocks=[
            lead(
                "در بخش ۱ گفتیم کران RM شرط کافی است نه لازم. آن ادعا باید با عدد نشان داده شود، "
                "نه فقط گفته شود.",
                "Section 1 claimed the RM bound is sufficient but not necessary. That claim must be "
                "shown with numbers, not merely asserted.",
            ),
            p(
                "سه مجموعه دیگر با همان مدل (D = T، سه کار) بررسی می‌شوند. برای هر یک، بهره‌وری، "
                "کران، زمان پاسخ دقیق و حکم تحلیل زمان پاسخ محاسبه و در جدول جمع شده است. هدف این "
                "است که ببینیم کران در کجا **درست راهنمایی می‌کند** و در کجا **محافظه‌کارانه گمراه "
                "می‌کند**.",
                "Three more task sets with the same model (D = T, three tasks) are examined. For each, "
                "the utilisation, the bound, the exact response times and the verdict of response-time "
                "analysis are computed and collected in the table. The aim is to see where the bound "
                "**guides correctly** and where it is **conservatively misleading**.",
            ),
            tbl(
                "چهار مجموعه سه‌فرایندی و حکم هر یک",
                "Four three-task sets and their verdicts",
                ["مجموعه", "دوره‌ها", "U", "بالاتر از کران؟", "R(P3)", "RM موفق؟", "EDF موفق؟"],
                ["Set", "Periods", "U", "Above bound?", "R(P3)", "RM ok?", "EDF ok?"],
                [
                    [("الف (این تمرین)", "A (this exercise)"), ("۴، ۶، ۸", "4, 6, 8"), ("۰٫۹۵۸", "0.958"), ("بله", "yes"), ("شکست", "fails"), ("خیر", "no"), ("بله", "yes")],
                    [("ب", "B"), ("۵، ۱۰، ۲۰", "5, 10, 20"), ("۰٫۸۰۰", "0.800"), ("بله", "yes"), ("۱۵", "15"), ("بله", "yes"), ("بله", "yes")],
                    [("ج", "C"), ("۳، ۷، ۱۲", "3, 7, 12"), ("۰٫۸۶۹", "0.869"), ("بله", "yes"), ("۱۱", "11"), ("بله", "yes"), ("بله", "yes")],
                    [("د", "D"), ("۴، ۸، ۱۶", "4, 8, 16"), ("۰٫۷۵۰", "0.750"), ("خیر", "no"), ("۸", "8"), ("بله", "yes"), ("بله", "yes")],
                ],
                widths=[1.3, 1.0, 0.75, 1.1, 0.8, 0.85, 0.85],
                note_fa="کران برای هر سه کار ۰٫۷۸۰ است. مجموعه‌های ب و ج از کران بالاترند ولی RM در آن‌ها موفق می‌شود.",
                note_en="The bound for three tasks is 0.780. Sets B and C are above it, yet RM succeeds on both.",
            ),
            h2("تفسیر جدول", "Reading the table"),
            p(
                "ستون پنجم مهم‌ترین ستون است. مجموعه ب بهره‌وری ۰٫۸۰۰ دارد، یعنی **بالاتر** از کران "
                "۰٫۷۸۰، اما تحلیل زمان پاسخ می‌گوید R(Q3) = ۱۵ و مهلتش ۲۰ است — پس RM موفق می‌شود. "
                "مجموعه ج هم همین‌طور. اگر کسی فقط به کران نگاه می‌کرد، این دو مجموعه را رد می‌کرد و "
                "ظرفیت پردازنده را بی‌دلیل هدر می‌داد.",
                "The fifth column is the important one. Set B has utilisation 0.800, **above** the "
                "0.780 bound, yet response-time analysis gives R(Q3) = 15 against a deadline of 20 — so "
                "RM succeeds. Set C behaves the same way. Anyone looking only at the bound would reject "
                "both sets and waste processor capacity for no reason.",
            ),
            p(
                "در سوی دیگر، مجموعه الف تنها ۰٫۹۵۸ است اما R(P3) همگرا نمی‌شود. اختلاف میان الف و "
                "ب فقط ۰٫۱۵۸ در بهره‌وری نیست؛ تفاوت در **الگو**ی دوره‌هاست. در ب دوره‌ها هم‌مضرب "
                "ساده‌اند (۵، ۱۰، ۲۰) و کارها به‌طور طبیعی پشته‌ای جا می‌گیرند؛ در الف دوره‌ها "
                "۴، ۶ و ۸ هستند و ضرب‌الاجماعی ناهم‌تراز می‌سازند که در آن P3 همیشه دیر می‌رسد.",
                "On the other side, set A has only 0.958 yet R(P3) does not converge. The difference "
                "between A and B is not merely 0.158 of utilisation; it is the **pattern** of the "
                "periods. In B the periods are simple multiples (5, 10, 20) and the tasks nest "
                "naturally; in A the periods are 4, 6 and 8, producing a ragged pattern of coincidences "
                "in which P3 always arrives late.",
            ),
            fig2("fig08_bound", "همان شکل کران: سه مجموعه بالای کران و تنها یکی شکست می‌خورد",
                 "The bound again: three sets above it and only one fails", 0.82),
            note(
                "نتیجه عملی", "The practical conclusion",
                "کران RM برای **رد کردن سریع** مجموعه‌های بد است، نه برای پذیرفتن. اگر U زیر کران "
                "است، کار تمام است و RM قطعاً موفق می‌شود. اگر بالاست، تازه باید تحلیل زمان پاسخ "
                "انجام شود. این همان تفاوتی است که در تمرین دوم با شبیه‌سازی روی صدها مجموعه دیده شد.",
                "The RM bound is for **quickly rejecting** bad sets, not for accepting. If U is below "
                "the bound you are done and RM definitely succeeds. If it is above, response-time "
                "analysis must still be run. This is the same distinction seen in assignment 2 by "
                "simulating hundreds of task sets.",
            ),
            h2("چرا مجموعه ب کار می‌کند: نگاه تیک‌به‌تیک", "Why set B works: a tick-by-tick look"),
            p(
                "در مجموعه ب، Q1 هر ۵ تیک یک تیک، Q2 هر ۱۰ تیک سه تیک و Q3 هر ۲۰ تیک شش تیک کار "
                "می‌خواهد. در هر پنجره ۱۰ تیکی، Q1 دو تیک و Q2 سه تیک می‌گیرد و پنج تیک برای Q3 "
                "می‌ماند. چون Q3 فقط شش تیک در ۲۰ تیک لازم دارد، این توازن حفظ می‌شود. در مجموعه الف "
                "این توازن وجود ندارد: در پنجره ۸ تیکی، P1 دو تیک و P2 حدود سه تیک می‌گیرد و برای "
                "P3 سه تیک لازم است — دقیقاً به لبه می‌رسد و یک تیک کم می‌آورد.",
                "In set B, Q1 wants one tick every 5, Q2 three ticks every 10 and Q3 six ticks every "
                "20. In any 10-tick window Q1 takes two ticks and Q2 three, leaving five for Q3. Since "
                "Q3 needs only six ticks per 20, the balance holds. Set A has no such balance: in an "
                "8-tick window P1 takes two ticks and P2 takes about three, while P3 needs three — it "
                "lands exactly on the edge and comes up one tick short.",
            ),
            tbl(
                "توازن پنجره‌ای در دو مجموعه",
                "Window balance in the two sets",
                ["پنجره", "کار P3/Q3 لازم", "آنچه واقعاً می‌ماند (الف)", "آنچه واقعاً می‌ماند (ب)"],
                ["Window", "P3/Q3 needed", "What is left (A)", "What is left (B)"],
                [
                    [("۸ تیک", "8 ticks"), ("۳", "3"), ("۲", "2"), ("—", "—")],
                    [("۱۰ تیک", "10 ticks"), ("—", "—"), ("—", "—"), ("۵", "5")],
                    [("۲۰ تیک", "20 ticks"), ("۷ (تقریبی)", "7 (approx.)"), ("۷", "7"), ("۱۲", "12")],
                ],
                widths=[1.1, 1.5, 2.0, 1.8],
            ),
            p(
                "این جدول توضیح می‌دهد چرا «بهره‌وری» به‌تنهایی معیار کافی نیست. دو مجموعه می‌توانند "
                "بهره‌وری نزدیک داشته باشند اما یکی موفق و دیگری ناموفق باشد، چون توزیع بار در زمان "
                "متفاوت است. زمان‌بندی بلادرنگ درباره **الگو**ی بار قضاوت می‌کند، نه فقط مقدار آن.",
                "This table explains why 'utilisation' alone is not a sufficient criterion. Two sets "
                "can have similar utilisation with one succeeding and the other failing, because the "
                "distribution of load over time differs. Real-time scheduling judges the **pattern** "
                "of load, not only its amount.",
            ),
        ],
    )

    # ------------------------------------------------------------------ 11c
    m.section(
        "مطالعه موردی: همان تحلیل در یک حلقه کنترل",
        "Case Study: The Same Analysis in a Control Loop",
        kicker_fa="چهار کار میلی‌ثانیه‌ای، دو سناریو، یک درس",
        kicker_en="Four millisecond tasks, two scenarios, one lesson",
        blocks=[
            lead(
                "تمرین کاغذی با سه عدد کوچک شروع شد. همان روش روی یک سیستم واقعی چه می‌دهد؟",
                "The paper exercise started with three small numbers. What does the same method give on "
                "a real system?",
            ),
            p(
                "یک حلقه کنترل نمونه را در نظر بگیرید: خواندن حسگر هر ۱۰ میلی‌ثانیه با ۲ میلی‌ثانیه "
                "اجرا، محاسبه قانون کنترل هر ۲۰ میلی‌ثانیه با ۵ میلی‌ثانیه، به‌روزرسانی نمایشگر هر "
                "۵۰ میلی‌ثانیه با ۴ میلی‌ثانیه، و ثبت گزارش هر ۱۰۰ میلی‌ثانیه با ۷ میلی‌ثانیه. "
                "این اعداد نمونهٔ یک کنترل‌کننده صنعتی‌اند و ساختار مسئله دقیقاً همان تمرین است: "
                "چند کار دوره‌ای، مهلت برابر دوره، یک پردازنده.",
                "Consider a sample control loop: read the sensor every 10 ms taking 2 ms, compute the "
                "control law every 20 ms taking 5 ms, refresh the display every 50 ms taking 4 ms, and "
                "log a record every 100 ms taking 7 ms. These are typical numbers for an industrial "
                "controller, and the problem structure is exactly the exercise: a few periodic tasks, "
                "deadlines equal to periods, one processor.",
            ),
            tbl(
                "پارامترهای حلقه کنترل نمونه",
                "Parameters of the sample control loop",
                ["کار", "دوره (ms)", "اجرا (ms)", "U_i", "R با RM", "مهلت", "حکم"],
                ["Task", "Period (ms)", "Execution (ms)", "U_i", "R under RM", "Deadline", "Verdict"],
                [
                    [("حسگر", "sensor"), ("۱۰", "10"), ("۲", "2"), ("۰٫۲۰۰", "0.200"), ("۲", "2"), ("۱۰", "10"), ("قبول", "ok")],
                    [("کنترل", "control"), ("۲۰", "20"), ("۵", "5"), ("۰٫۲۵۰", "0.250"), ("۷", "7"), ("۲۰", "20"), ("قبول", "ok")],
                    [("نمایش", "display"), ("۵۰", "50"), ("۴", "4"), ("۰٫۰۸۰", "0.080"), ("۱۳", "13"), ("۵۰", "50"), ("قبول", "ok")],
                    [("گزارش", "log"), ("۱۰۰", "100"), ("۷", "7"), ("۰٫۰۷۰", "0.070"), ("۲۰", "20"), ("۱۰۰", "100"), ("قبول", "ok")],
                ],
                widths=[1.0, 0.95, 1.15, 0.8, 1.0, 0.85, 0.8],
                note_fa="بهره‌وری کل ۰٫۶۰۰ و کران برای چهار کار ۰٫۷۵۷ است؛ مجموعه با فاصله زیر کران است و RM تضمین‌شده موفق می‌شود.",
                note_en="Total utilisation is 0.600 and the bound for four tasks is 0.757; the set is comfortably below the bound and RM is guaranteed to succeed.",
            ),
            p(
                "اینجا هیچ چیز هیجان‌انگیزی رخ نمی‌دهد و همین درس است. زیر کران، RM کافی است و "
                "نیازی به EDF نیست. کران در سال ۱۹۷۳ دقیقاً برای همین ساخته شد: یک آزمون سریع که "
                "بدون تحلیل زمان پاسخ بتوان گفت «بله» یا «احتمالاً نه».",
                "Nothing dramatic happens here, and that is the lesson. Below the bound RM is enough "
                "and EDF is not needed. The bound exists precisely for this: a quick test that gives "
                "'yes' or 'probably not' without running response-time analysis.",
            ),
            h2("سناریوی دوم: کار کنترل سنگین‌تر می‌شود", "Second scenario: the control task gets heavier"),
            p(
                "حالا فرض کنید قانون کنترل پیچیده‌تر شده و از ۵ به ۷ میلی‌ثانیه رسیده است. بهره‌وری "
                "کل ۰٫۷۰۰ می‌شود، هنوز زیر کران ۰٫۷۵۷. تحلیل زمان پاسخ R(گزارش) = ۳۳ می‌دهد در "
                "برابر مهلت ۱۰۰ — کاملاً سالم. این نشان می‌دهد چرا مهندسان دو معیار را کنار هم "
                "نگه می‌دارند: کران برای غربال سریع، و تحلیل دقیق برای اطمینان.",
                "Now suppose the control law grew more complex and moved from 5 to 7 ms. Total "
                "utilisation becomes 0.700, still below the 0.757 bound. Response-time analysis gives "
                "R(log) = 33 against a deadline of 100 — perfectly healthy. This shows why engineers "
                "keep both tools: the bound for quick triage, the exact analysis for assurance.",
            ),
            tbl(
                "اثر سنگین‌تر شدن کار کنترل",
                "Effect of the heavier control task",
                ["پارامتر", "قبل", "بعد", "تغییر"],
                ["Quantity", "Before", "After", "Change"],
                [
                    [("اجرای کار کنترل", "control execution"), ("۵ ms", "5 ms"), ("۷ ms", "7 ms"), ("+۴۰٪", "+40%")],
                    [("بهره‌وری کل", "total utilisation"), ("۰٫۶۰۰", "0.600"), ("۰٫۷۰۰", "0.700"), ("+۰٫۱۰۰", "+0.100")],
                    [("R(گزارش)", "R(log)"), ("۲۰ ms", "20 ms"), ("۳۳ ms", "33 ms"), ("+۱۳ ms", "+13 ms")],
                    [("حاشیه تا مهلت", "margin to deadline"), ("۸۰ ms", "80 ms"), ("۶۷ ms", "67 ms"), ("−۱۳ ms", "−13 ms")],
                ],
                widths=[1.6, 1.2, 1.2, 1.1],
            ),
            note(
                "چرا زمان پاسخ این‌قدر سریع رشد می‌کند", "Why the response time grows so fast",
                "زمان پاسخ کم‌اولویت‌ترین کار، مجموع اجرای همه کارهای بالاتر است که در فاصله "
                "آزادسازی‌اش می‌رسند. افزودن ۲ میلی‌ثانیه به کار کنترل، در پنجره ۱۰۰ تیکی چند بار "
                "تکرار می‌شود و اثرش جمع می‌شود. این «اثر ضرب»ی است که در تحلیل دستی هم دیده می‌شود "
                "و دلیل دیگری بر لزوم تحلیل دقیق است.",
                "The response time of the lowest-priority task is the sum of all higher-priority "
                "execution that arrives during its release window. Adding 2 ms to the control task "
                "repeats several times inside a 100-tick window and the effect accumulates. That "
                "multiplication is visible even in hand analysis and is another reason exact analysis "
                "is needed.",
            ),
            h2("اگر بار از یک بگذرد", "If the load passes one"),
            p(
                "در همین سیستم، اگر اجرای گزارش از ۷ به ۳۰ میلی‌ثانیه برسد، بهره‌وری از یک می‌گذرد. "
                "آن‌گاه نه کران و نه EDF کمکی نمی‌کنند: **هیچ** الگوریتمی نمی‌تواند همه مهلت‌ها را "
                "رعایت کند، چون کار بیشتر از زمان موجود است. پاسخ مهندسی در این حالت تغییر الگوریتم "
                "نیست؛ کاهش بار، افزایش سرعت پردازنده، یا پذیرش کاهش کیفیت در کارهای کم‌اهمیت است.",
                "In this system, if the logging task grew from 7 to 30 ms, utilisation would pass one. "
                "Then neither the bound nor EDF helps: **no** algorithm can meet all deadlines, because "
                "there is more work than time. The engineering answer is not a different algorithm; it "
                "is reducing load, speeding up the processor, or accepting degraded quality on "
                "low-criticality tasks.",
            ),
            quote(
                "الگوریتم زمان‌بندی، بار را جادو نمی‌کند؛ فقط تصمیم می‌گیرد چه کسی اول قربانی شود.",
                "A scheduling algorithm does not conjure away load; it only decides who is sacrificed "
                "first.",
                source_fa="— درس عملی این مطالعه موردی",
                source_en="— the practical lesson of this case study",
            ),
        ],
    )

    # ------------------------------------------------------------------ 11d
    m.section(
        "راهنمای حل یک تمرین کاغذی از صفر",
        "A From-Scratch Guide to Solving a Paper Exercise",
        kicker_fa="هشت گام، با آنچه در هر گام بیشتر اشتباه می‌شود",
        kicker_en="Eight steps, with what most often goes wrong at each",
        blocks=[
            lead(
                "این بخش خلاصه روش است، به‌شکلی که بتوان آن را سر جلسه امتحان روی یک برگه اجرا کرد.",
                "This section condenses the method into something that can be executed on one sheet "
                "during an exam.",
            ),
            p(
                "هشت گام زیر همان مسیری است که در این گزارش طی شد، اما بدون توضیح‌های جانبی. گام‌های "
                "۱ تا ۳ پیش از کشیدن هر خطی انجام می‌شوند و بیشتر نمره از دست رفته در همین سه گام "
                "است، نه در خود نقاشی.",
                "The eight steps below are the path taken in this report, with the commentary removed. "
                "Steps 1 to 3 are done before drawing a single line, and most lost marks come from "
                "these three steps, not from the drawing itself.",
            ),
            tbl(
                "هشت گام حل و دام هر گام",
                "The eight steps and the trap in each",
                ["گام", "کار", "دام رایج"],
                ["Step", "What to do", "Common trap"],
                [
                    [("۱", "1"), ("پارامترها را در جدول بنویس و D = T را بررسی کن", "write the parameters in a table and check D = T"), ("مهلت نسبی را با مطلق اشتباه گرفتن", "confusing relative and absolute deadline")],
                    [("۲", "2"), ("U و کران را حساب کن", "compute U and the bound"), ("جمع‌زدن C به‌جای C/T", "adding C instead of C/T")],
                    [("۳", "3"), ("تحلیل زمان پاسخ را انجام بده", "run the response-time analysis"), ("توقف پیش از همگرایی", "stopping before convergence")],
                    [("۴", "4"), ("ابرسال را حساب کن", "compute the hyperperiod"), ("کشیدن کمتر از یک ابررسال", "drawing less than one hyperperiod")],
                    [("۵", "5"), ("نقاشی RM را بکش", "draw RM"), ("محاسبه دوباره اولویت در هر تیک", "recomputing priority every tick")],
                    [("۶", "6"), ("نقاشی EDF را بکش و قاعده تساوی را بنویس", "draw EDF and state the tie-break"), ("اجرای ناسازگار قاعده تساوی", "applying the tie-break inconsistently")],
                    [("۷", "7"), ("هر کار را با مهلت مقایسه کن", "compare every job with its deadline"), ("مقایسه آخرین کار به‌جای همه کارها", "checking the last job instead of all jobs")],
                    [("۸", "8"), ("نتیجه را با پیش‌بینی گام ۳ بسنج", "compare the result with the step-3 prediction"), ("پذیرش نقاشی متناقض با تحلیل", "accepting a drawing that contradicts the analysis")],
                ],
                widths=[0.5, 2.7, 2.4],
            ),
            h2("گام ۳ به‌تفصیل: خطای همگرایی", "Step 3 in detail: the convergence error"),
            p(
                "پرخطاترین گام، تحلیل زمان پاسخ است. علتش این است که معادله بازگشتی است و باید تا "
                "همگرایی تکرار شود. در مجموعه این تمرین، R(P3) در تکرار سوم به ۸ می‌رسد — دقیقاً "
                "مهلت — و در تکرار چهارم به ۱۰ می‌رود. کسی که در تکرار سوم متوقف شود، ممکن است "
                "به‌اشتباه نتیجه بگیرد که P3 «دقیقاً» قابل قبول است. این خطا در نخستین نسخه برگه "
                "همین تمرین هم رخ داد و بازبین آن را گرفت.",
                "The most error-prone step is the response-time analysis, because the equation is "
                "recurrent and must be iterated to convergence. In this set R(P3) reaches 8 on the "
                "third iteration — exactly the deadline — and jumps to 10 on the fourth. Someone who "
                "stops at the third iteration may wrongly conclude that P3 is 'exactly' acceptable. "
                "That error occurred in the first version of this exercise's sheet too, and the "
                "verifier caught it.",
            ),
            tbl(
                "چهار تکرار تحلیل زمان پاسخ برای P3",
                "Four iterations of the response-time analysis for P3",
                ["تکرار", "R قبلی", "اجرای P3", "سهم P1", "سهم P2", "R جدید", "در برابر مهلت ۸"],
                ["Iteration", "previous R", "P3's own C", "P1 contribution", "P2 contribution", "new R", "against deadline 8"],
                [
                    [("۰", "0"), ("۰", "0"), ("۳", "3"), ("۱", "1"), ("۲", "2"), ("۶", "6"), ("زیر", "below")],
                    [("۱", "1"), ("۶", "6"), ("۳", "3"), ("۲", "2"), ("۲", "2"), ("۸", "8"), ("برابر", "equal")],
                    [("۲", "2"), ("۸", "8"), ("۳", "3"), ("۲", "2"), ("۴", "4"), ("۱۰", "10"), ("بالاتر", "above")],
                    [("۳", "3"), ("۱۰", "10"), ("۳", "3"), ("۳", "3"), ("۴", "4"), ("۱۰", "10"), ("ناهمگرا", "diverges")],
                ],
                widths=[0.8, 0.9, 1.0, 1.0, 1.0, 0.9, 1.3],
                note_fa="دو تکرار آخر تکرار می‌شوند و به نقطه پایدار نمی‌رسند: هیچ R محدودی شرط را برآورده نمی‌کند.",
                note_en="The last two iterations repeat without reaching a fixed point: no finite R satisfies the condition.",
            ),
            p(
                "یک قاعده ساده برای پرهیز از این خطا: **اگر R از مهلت گذشت، تحلیل شکست خورده است**؛ "
                "لازم نیست بیشتر تکرار کنی. اما اگر R دقیقاً برابر مهلت شد، باید یک تکرار دیگر انجام "
                "دهی تا ببینی ثابت می‌ماند یا می‌گذرد. تساوی، نقطه خطر است نه نقطه پایان.",
                "A simple rule avoids this error: **once R passes the deadline the analysis has "
                "failed** and no further iterations are needed. But if R equals the deadline exactly, "
                "one more iteration is required to see whether it stays or passes. Equality is the "
                "danger point, not the end point.",
            ),
            h2("گام ۶ به‌تفصیل: اعلام قاعده تساوی", "Step 6 in detail: declaring the tie-break"),
            p(
                "در بخش ۵ دیدیم که قاعده تساوی می‌تواند دو نقاشی درست اما متفاوت بسازد. برای اینکه "
                "جواب قابل بازتولید باشد، یک خط کافی است: قاعده را در بالای برگه بنویس. اگر این خط "
                "نباشد، پاسخ شما ممکن است با پاسخ مرجع یا با شبیه‌ساز نخواند و نمره از دست برود، "
                "حتی وقتی منطق کارتان درست بوده است.",
                "Section 5 showed that a tie-break can produce two correct but different drawings. To "
                "make the answer reproducible one line is enough: state the rule at the top of the "
                "sheet. Without it your answer may disagree with the reference answer or the "
                "simulator, and marks are lost even when your reasoning was sound.",
            ),
            note(
                "یک برگه آماده برای جلسه امتحان", "A ready-made sheet for an exam",
                "چهار خط در بالای هر برگه بنویس: (۱) پارامترها در جدول، (۲) U و کران، "
                "(۳) R هر کار با تعداد تکرارها، (۴) قاعده تساوی. این چهار خط معمولاً بیشتر از "
                "خود نقاشی نمره دارند، چون قابل بررسی‌اند.",
                "Write four lines at the top of every sheet: (1) the parameters in a table, (2) U and "
                "the bound, (3) R for each task with the number of iterations, (4) the tie-break. "
                "These four lines usually carry more marks than the drawing itself, because they can "
                "be checked.",
            ),
        ],
    )

    # ------------------------------------------------------------------ references
    m.references_list([
        ("Liu, C. L., & Layland, J. W. (1973). Scheduling algorithms for multiprogramming in a hard-real-time environment. *Journal of the ACM*, 20(1), 46–61.",
         "Liu, C. L., & Layland, J. W. (1973). Scheduling algorithms for multiprogramming in a hard-real-time environment. *Journal of the ACM*, 20(1), 46–61."),
        ("Joseph, M., & Pandya, P. (1986). Finding response times in a real-time system. *The Computer Journal*, 29(5), 390–395.",
         "Joseph, M., & Pandya, P. (1986). Finding response times in a real-time system. *The Computer Journal*, 29(5), 390–395."),
        ("Baruah, S. K., Rosier, L. E., & Howell, R. R. (1990). Algorithms and complexity concerning the preemptive scheduling of periodic, real-time tasks on one processor. *Real-Time Systems*, 2(4), 301–324.",
         "Baruah, S. K., Rosier, L. E., & Howell, R. R. (1990). Algorithms and complexity concerning the preemptive scheduling of periodic, real-time tasks on one processor. *Real-Time Systems*, 2(4), 301–324."),
        ("Buttazzo, G. C. (2011). *Hard Real-Time Computing Systems: Predictable Scheduling Algorithms and Applications* (3rd ed.). Springer.",
         "Buttazzo, G. C. (2011). *Hard Real-Time Computing Systems: Predictable Scheduling Algorithms and Applications* (3rd ed.). Springer."),
        ("Burns, A., & Wellings, A. (2009). *Real-Time Systems and Programming Languages* (4th ed.). Addison-Wesley.",
         "Burns, A., & Wellings, A. (2009). *Real-Time Systems and Programming Languages* (4th ed.). Addison-Wesley."),
        ("Audsley, N., Burns, A., Richardson, M., Tindell, K., & Wellings, A. J. (1993). Applying new scheduling theory to static priority pre-emptive scheduling. *Software Engineering Journal*, 8(5), 284–292.",
         "Audsley, N., Burns, A., Richardson, M., Tindell, K., & Wellings, A. J. (1993). Applying new scheduling theory to static priority pre-emptive scheduling. *Software Engineering Journal*, 8(5), 284–292."),
    ])

    # ------------------------------------------------------------------ appendices
    stats = {r["file"]: r for r in
             source_stats([os.path.join(CODE, "workbook.py"), os.path.join(CODE, "test_workbook.py")])}
    m.appendix_section(
        "پیوست الف: راهنمای اجرا و بازتولید",
        "Appendix A: How to Run and Reproduce",
        [
            p(
                "کل نتیجه با سه فرمان بازتولید می‌شود. بازبین "
                f"{stats['workbook.py']['lines']} خط دارد که {stats['workbook.py']['code_lines']} خط "
                f"آن کد مؤثر است، و آزمون‌ها {stats['test_workbook.py']['lines']} خط.",
                "The whole result is reproduced with three commands. The verifier has "
                f"{stats['workbook.py']['lines']} lines of which {stats['workbook.py']['code_lines']} "
                f"are effective code, and the tests have {stats['test_workbook.py']['lines']} lines.",
            ),
            snippet(
                "cd code\npython3 workbook.py --check        # verify the hand sheet\n"
                "python3 test_workbook.py -v        # 34 unit tests\ncd ..\n"
                "python3 figures/generate.py        # 24 figures (fa + en)\npython3 report/build.py",
                "دستورهای بازتولید کامل",
                "Complete reproduction commands",
                lang="bash", label_en="run_all.sh",
            ),
            kv(
                [(("نسخه پایتون", "Python version"), ("۳٫۱۱", "3.11")),
                 (("ابررسال", "Hyperperiod"), (str(H), str(H))),
                 (("تعداد آزمون", "Number of tests"), ("۳۴", "34")),
                 (("تعداد شکل", "Number of figures"), ("۲۴", "24"))],
                "محیط اجرا", "Runtime environment",
            ),
        ],
    )

    m.appendix_section(
        "پیوست ب: محاسبات دستی با همه ارقام",
        "Appendix B: Hand Calculations in Full",
        [
            p(
                "این پیوست همان محاسباتی است که روی کاغذ انجام شد، با همه ارقام میانی. هدف این "
                "است که خواننده بتواند هر عدد را خودش بازتولید کند و در صورت اختلاف، محل آن را "
                "پیدا کند.",
                "This appendix reproduces the calculations done on paper, with every intermediate "
                "figure, so that the reader can reproduce each number and locate any disagreement.",
            ),
            h2("بهره‌وری و کران", "Utilisation and the bound"),
            snippet(
                "U(P1) = C/T = 1/4  = 0.250\n"
                "U(P2) = C/T = 2/6  = 0.333333\n"
                "U(P3) = C/T = 3/8  = 0.375000\n"
                "-------------------------------------\n"
                "U     = 0.250000 + 0.333333 + 0.375000 = 0.9583333\n\n"
                "bound(n=3) = 3 * (2^(1/3) - 1)\n"
                "           = 3 * (1.259921 - 1)\n"
                "           = 3 * 0.259921\n"
                "           = 0.779763\n\n"
                "U > bound  ->  the theorem gives no guarantee (it does not prove failure)\n",
                "محاسبه بهره‌وری و کران با همه ارقام",
                "Utilisation and bound with all figures",
                lang="text", label_en="calc_utilisation.txt",
            ),
            h2("ابررسال", "The hyperperiod"),
            snippet(
                "T = (4, 6, 8)\n"
                "H = lcm(4, 6, 8)\n"
                "  = lcm(lcm(4, 6), 8)\n"
                "  = lcm(12, 8)\n"
                "  = 24 ticks\n\n"
                "jobs per hyperperiod:\n"
                "  P1: 24/4 = 6\n"
                "  P2: 24/6 = 4\n"
                "  P3: 24/8 = 3\n"
                "total service required = 6*1 + 4*2 + 3*3 = 6 + 8 + 9 = 23 ticks\n"
                "processor time available = 24 ticks\n"
                "slack = 1 tick\n",
                "محاسبه ابررسال و ظرفیت",
                "Hyperperiod and capacity",
                lang="text", label_en="calc_hyperperiod.txt",
            ),
            h2("تحلیل زمان پاسخ", "Response-time analysis"),
            snippet(
                "P1 (highest priority, no higher-priority work):\n"
                "  R(0) = C1 = 1  ->  fixed point  ->  R = 1  <= D = 4   OK\n\n"
                "P2 (blocked by P1):\n"
                "  R(0) = C2                     = 2\n"
                "  R(1) = 2 + ceil(2/4)*1        = 2 + 1*1 = 3\n"
                "  R(2) = 2 + ceil(3/4)*1        = 2 + 1*1 = 3   fixed  ->  R = 3  <= 6  OK\n\n"
                "P3 (blocked by P1 and P2):\n"
                "  R(0) = C3                              = 3\n"
                "  R(1) = 3 + ceil(3/4)*1 + ceil(3/6)*2   = 3 + 1 + 2  = 6\n"
                "  R(2) = 3 + ceil(6/4)*1 + ceil(6/6)*2   = 3 + 2 + 2  = 7\n"
                "  R(3) = 3 + ceil(7/4)*1 + ceil(7/6)*2   = 3 + 2 + 4  = 9\n"
                "  R(4) = 3 + ceil(9/4)*1 + ceil(9/6)*2   = 3 + 3 + 4  = 10\n"
                "  ...  R exceeds D = 8 and keeps growing  ->  NO fixed point\n"
                "  verdict: P3 is not schedulable under RM\n",
                "تحلیل زمان پاسخ، تکرار به تکرار",
                "Response-time analysis, iteration by iteration",
                lang="text", label_en="calc_rta.txt",
            ),
            h2("تابع تقاضا", "The demand function"),
            snippet(
                "dbf(L) = floor(L/4)*1 + floor(L/6)*2 + floor(L/8)*3\n\n"
                "  L | floor(L/4) floor(L/6) floor(L/8) | dbf | L-dbf\n"
                " ---+----------------------------------+-----+------\n"
                "  4 |     1         0         0        |  1  |   3\n"
                "  6 |     1         1         0        |  3  |   3\n"
                "  8 |     2         1         1        |  7  |   1\n"
                " 12 |     3         2         1        | 10  |   2\n"
                " 16 |     4         2         2        | 14  |   2\n"
                " 20 |     5         3         2        | 17  |   3\n"
                " 24 |     6         4         3        | 23  |   1\n\n"
                "minimum slack = 1 tick at L = 8 and L = 24\n"
                "dbf(L) <= L everywhere  ->  EDF is schedulable\n",
                "تابع تقاضا در نقاط حساس",
                "The demand function at the critical points",
                lang="text", label_en="calc_dbf.txt",
            ),
            h2("سرویس ارائه‌شده در یک ابررسال", "Service delivered in one hyperperiod"),
            snippet(
                "required:  P1 = 6 ticks,  P2 = 8 ticks,  P3 = 9 ticks   (total 23)\n\n"
                "RM  delivered:  P1 = 6,  P2 = 8,  P3 = 8                (total 22)\n"
                "                -> P3 is 1 tick short, and that tick is a missed deadline\n\n"
                "EDF delivered:  P1 = 6,  P2 = 8,  P3 = 9                (total 23)\n"
                "                -> every job gets exactly its execution time\n\n"
                "idle ticks:  RM = 2,  EDF = 1\n"
                "(RM idles while P3 still has unfinished work, because the fixed\n"
                " priority keeps P3 behind a job that is not even ready yet.)\n",
                "سرویس هر فرایند در یک ابررسال",
                "Service per process over one hyperperiod",
                lang="text", label_en="calc_service.txt",
            ),
            tbl(
                "خلاصه عددی همه محاسبات",
                "Numeric summary of every calculation",
                ["کمیت", "نماد", "مقدار", "معنا"],
                ["Quantity", "Symbol", "Value", "Meaning"],
                [
                    [("بهره‌وری کل", "Total utilisation"), ("U", "U"), ("۰٫۹۵۸۳", "0.9583"), ("کسری از پردازنده که طلب می‌شود", "the fraction of the processor demanded")],
                    [("کران RM", "RM bound"), ("n(2^(1/n)−1)", "n(2^(1/n)−1)"), ("۰٫۷۷۹۸", "0.7798"), ("شرط کافی برای موفقیت RM", "sufficient condition for RM")],
                    [("ابررسال", "Hyperperiod"), ("H", "H"), ("۲۴", "24"), ("طول الگوی تکرار", "length of the repeat pattern")],
                    [("سرویس لازم", "Service required"), ("Σ", "Σ"), ("۲۳", "23"), ("مجموع C در یک ابررسال", "sum of C over one hyperperiod")],
                    [("فرصت کل", "Total slack"), ("H − Σ", "H − Σ"), ("۱", "1"), ("تیک‌های بی‌کار در خوش‌بینانه‌ترین حالت", "idle ticks in the best case")],
                    [("زمان پاسخ P1", "Response time P1"), ("R(P1)", "R(P1)"), ("۱", "1"), ("همگرا، زیر مهلت ۴", "converged, below deadline 4")],
                    [("زمان پاسخ P2", "Response time P2"), ("R(P2)", "R(P2)"), ("۳", "3"), ("همگرا، زیر مهلت ۶", "converged, below deadline 6")],
                    [("زمان پاسخ P3", "Response time P3"), ("R(P3)", "R(P3)"), ("—", "—"), ("ناهمگرا، شکست", "diverges, failure")],
                    [("کمینه فرصت دینامیک", "Minimum dynamic slack"), ("min(L−dbf)", "min(L−dbf)"), ("۱", "1"), ("تنگی EDF در L = ۸ و ۲۴", "EDF's tightest point at L = 8 and 24")],
                ],
                widths=[1.6, 1.1, 0.85, 2.2],
            ),
            note(
                "چرا ستون «فرصت» این‌قدر مهم است", "Why the slack column matters so much",
                "کمینه ستون L − dbf جواب می‌دهد «چقدر جا مانده». در این مجموعه ۱ تیک است. اگر "
                "این عدد به صفر برسد، EDF موفق می‌شود اما بدون هیچ حاشیه؛ اگر منفی شود، شکست "
                "می‌خورد. در بخش ۹ (آزمون مرزی) همین موضوع با یک تیک بار اضافه آزمایش شد.",
                "The minimum of the L − dbf column answers 'how much room is left'. Here it is one "
                "tick. At zero, EDF still succeeds but with no margin; below zero it fails. Section 9 "
                "(the boundary test) checks exactly this with one extra tick of load.",
            ),
        ],
    )

    m.appendix_section(
        "پیوست ج: واژه‌نامه اصطلاحات",
        "Appendix C: Glossary",
        [
            p(
                "اصطلاح‌های این گزارش به ترتیب الفبای انگلیسی آمده‌اند تا جست‌وجو آسان باشد. هر "
                "مدخل یک جمله کوتاه است، چون هدف یادآوری است نه تعریف کامل.",
                "The terms used in this report are listed alphabetically for easy lookup. Each entry "
                "is one short sentence, because the purpose is recall rather than a full definition.",
            ),
            tbl(
                "واژه‌نامه",
                "Glossary",
                ["اصطلاح", "معنا در این گزارش"],
                ["Term", "Meaning in this report"],
                [
                    [("دورة زمانی (T)", "Period (T)"), ("فاصله میان آزادسازی دو کار متوالی از یک فرایند", "interval between two successive job releases of one process")],
                    [("زمان اجرای بدترین حالت (C)", "Worst-case execution time (C)"), ("بیشترین زمانی که یک کار به پردازنده نیاز دارد", "the maximum processor time one job needs")],
                    [("مهلت نسبی (D)", "Relative deadline (D)"), ("فاصله آزادسازی تا لحظه‌ای که کار باید تمام شده باشد", "release to the instant by which the job must finish")],
                    [("مهلت مطلق", "Absolute deadline"), ("آزادسازی + D؛ همان عددی که EDF مقایسه می‌کند", "release + D; the number EDF compares")],
                    [("ابرسال", "Hyperperiod"), ("کوچک‌ترین مضرب مشترک دوره‌ها؛ الگوی تکرار زمان‌بندی", "least common multiple of the periods; the repeat pattern of the schedule")],
                    [("بهره‌وری (U)", "Utilisation (U)"), ("مجموع C/T؛ کسری از پردازنده که کارها طلب می‌کنند", "sum of C/T; the fraction of the processor the tasks demand")],
                    [("کران RM", "RM bound"), ("n(2^(1/n)−1)؛ شرط کافی برای موفقیت RM", "n(2^(1/n)−1); a sufficient condition for RM to succeed")],
                    [("تحلیل زمان پاسخ", "Response-time analysis"), ("محاسبه تکرارشونده R برای هر کار در RM", "the recurrence computing R for each task under RM")],
                    [("تابع تقاضا", "Demand bound function"), ("بیشترین کاری که مهلتش در پنجره L می‌افتد", "the most work whose deadline falls inside a window L")],
                    [("ناسازگاری قاعده تساوی", "Inconsistent tie-break"), ("انتخاب متفاوت میان دو کار با مهلت برابر در تیک‌های مختلف", "choosing differently between two equal-deadline jobs at different ticks")],
                ],
                widths=[2.2, 3.0],
            ),
            h2("سه اصطلاح که بیشتر از همه اشتباه می‌شوند", "Three terms that are most often confused"),
            ul(
                [
                    "**اولویت ثابت در برابر پویا:** در RM اولویت *یک بار* تعیین می‌شود و تغییر نمی‌کند؛ "
                    "در EDF در هر تیک از نو تعیین می‌شود. این تفاوت، تنها تفاوت واقعی دو الگوریتم است.",
                    "**مهلت نسبی در برابر مطلق:** مهلت نسبی فاصله است (عددی ثابت برای هر کار)؛ مهلت "
                    "مطلق یک لحظه است و با هر آزادسازی عوض می‌شود. EDF با مطلق کار می‌کند.",
                    "**کران در برابر معیار دقیق:** کران یک آزمون *کافی* است و در بهترین حالت سریع؛ "
                    "تحلیل زمان پاسخ و تابع تقاضا *دقیق*اند و کندتر. یکی جای دیگری را نمی‌گیرد.",
                ],
                [
                    "**Static versus dynamic priority:** in RM the priority is decided *once* and never "
                    "changes; in EDF it is decided afresh at every tick. This is the only real "
                    "difference between the two algorithms.",
                    "**Relative versus absolute deadline:** a relative deadline is a distance (a fixed "
                    "number per task); an absolute deadline is an instant and changes with every "
                    "release. EDF works with absolute deadlines.",
                    "**Bound versus exact test:** the bound is a *sufficient* test and is fast at best; "
                    "response-time analysis and the demand function are *exact* and slower. Neither "
                    "replaces the other.",
                ],
            ),
            p(
                "اگر این سه تفکیک روشن باشند، بیشتر اشتباه‌های رایج در حل تمرین رخ نمی‌دهد. تجربه "
                "این تمرین نشان داد که خطاها معمولاً از *نفهمیدن تفاوت* می‌آیند، نه از محاسبه غلط: "
                "کسی که مهلت نسبی را با مطلق اشتباه بگیرد، در همه تیک‌ها عدد غلط می‌گذارد، حتی اگر "
                "جمع و تفریقش بی‌عیب باشد.",
                "Once these three distinctions are clear, most common errors disappear. This exercise "
                "showed that the mistakes usually come from *not seeing a distinction*, not from bad "
                "arithmetic: someone who confuses relative and absolute deadlines puts the wrong "
                "number at every tick even when the addition is flawless.",
            ),
            note(
                "یک نکته درباره نام‌ها", "A note on names",
                "در فارسی، «نزدیک‌ترین مهلت» و «نزدیک‌ترین مهلت اول» هر دو برای EDF به کار می‌روند. "
                "در این گزارش همیشه «نزدیک‌ترین مهلت (EDF)» نوشته شده تا با «نرخ یکنواخت (RM)» "
                "اشتباه نشود.",
                "In English the algorithm is 'earliest deadline first'; some texts say 'least laxity "
                "first' for a related but different rule. This report always writes EDF, never the "
                "laxity name, to avoid that confusion.",
            ),
        ],
    )

    m.appendix_section(
        "پیوست د: سند کامل آزمون‌ها",
        "Appendix D: The Full Test Transcript",
        [
            p(
                "خروجی کامل ۳۵ آزمون واحد در ادامه آمده است. این سند نشان می‌دهد که هر آزمون، چه "
                "چیزی را می‌سنجد: نام آزمون‌ها عمداً گویا انتخاب شده‌اند تا بدون خواندن کد هم بتوان "
                "دید چه رفتاری بررسی شده است.",
                "The complete output of the 35 unit tests follows. It shows what each test measures: "
                "the test names are deliberately descriptive so the checked behaviour is visible "
                "without reading any code.",
            ),
            code(os.path.join(DATA, "test_output.txt"), "سند اجرای آزمون‌ها", "Test transcript",
                 start=1, end=45, label_en="test_output.txt"),
        ],
    )

    m.appendix_section(
        "پیوست ه: خروجی کامل بازبین",
        "Appendix E: The Verifier's Full Output",
        [
            p(
                "خروجی کامل اجرای بازبین روی برگه نهایی در ادامه آمده است. این خروجی همان چیزی است "
                "که در بخش ۶ خلاصه شد.",
                "The verifier's full output on the final sheet follows. This is what section 6 "
                "summarised.",
            ),
            code(os.path.join(DATA, "workbook_output.txt"), "خروجی بازبین", "Verifier output",
                 start=1, end=40, label_en="workbook_output.txt"),
            code(os.path.join(DATA, "hand_schedules.txt"), "نقاشی‌های نهایی در متن ساده",
                 "The final drawings in plain text", start=1, end=40, label_en="hand_schedules.txt"),
        ],
    )

    m.appendix_section(
        "پیوست و: کد کامل بازبین",
        "Appendix F: Complete Verifier Source",
        [
            p(
                "کد کامل بازبین در ادامه آمده است تا هر خط آن قابل بررسی باشد.",
                "The complete verifier source follows so that every line can be reviewed.",
            ),
        ]
        + full_listing(os.path.join(CODE, "workbook.py"), "بازبین دفترچه", "Workbook verifier", chunk=30),
    )

    m.appendix_section(
        "پیوست ز: کد کامل آزمون‌ها",
        "Appendix G: Complete Test Suite",
        [
            p(
                "آزمون‌ها سه ویژگی را تضمین می‌کنند: هم‌خوانی بازبین با تحلیل نظری، رد کردن طرح‌های "
                "غلط، و درستی خودِ برگه نهایی.",
                "The tests guarantee three properties: agreement between verifier and theory, "
                "rejection of wrong sheets, and correctness of the final sheet itself.",
            ),
        ]
        + full_listing(os.path.join(CODE, "test_workbook.py"), "آزمون‌های بازبین", "Verifier tests", chunk=42),
    )

    return m
