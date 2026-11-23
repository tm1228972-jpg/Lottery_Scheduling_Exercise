"""Regenerate the repository's SVG diagrams, data CSVs, and data PNGs.

The code outputs are deterministic for the fixed seeds below. SVG and CSV
creation uses the Python standard library and project simulator; PNG rendering
uses the optional Pillow dependency documented in ``pyproject.toml``.
"""

from __future__ import annotations

from collections import Counter
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lottery_lab import (
    DiningPhilosophers,
    LotteryScheduler,
    PeriodicTask,
    Process,
    hyperperiod,
    rm_utilization_bound,
    simulate_schedule,
    utilization,
)  # noqa: E402

NAVY = "#14243A"
INK = "#25364B"
TEAL = "#168C8C"
BLUE = "#4776A8"
GOLD = "#F2B84B"
CORAL = "#DF6B63"
PALE = "#F3F6FA"
MUTED = "#64748B"
WHITE = "#FFFFFF"
FONT = "Inter, DejaVu Sans, Arial, sans-serif"

EX1 = ROOT / "assignments/01-lottery-introduction"
EX3 = ROOT / "assignments/03-edf-rm-three-processes"
EX8 = ROOT / "assignments/08-lottery-dining-philosophers"


def svg_document(
    title: str,
    width: int,
    height: int,
    body: str,
    description: str = "Educational diagram for the Lottery Scheduling Exercise.",
) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{title}</title>
<desc id="desc">{description}</desc>
<defs>
  <marker id="arrow" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto"><path d="M1,1 L10,6 L1,11" fill="none" stroke="{MUTED}" stroke-width="1.8"/></marker>
  <filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="#14243A" flood-opacity="0.10"/></filter>
</defs>
<rect width="100%" height="100%" fill="#F8FAFC"/>
{body}
</svg>'''


def box(x: int, y: int, w: int, h: int, heading: str, sub: str, color: str = TEAL) -> str:
    return (
        f'<g filter="url(#shadow)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{WHITE}" stroke="{color}" stroke-width="2.5"/>'
        f'<rect x="{x}" y="{y}" width="10" height="{h}" rx="5" fill="{color}"/>'
        f'<text x="{x + 28}" y="{y + 42}" font-family="{FONT}" font-size="22" font-weight="700" fill="{NAVY}">{heading}</text>'
        f'<text x="{x + 28}" y="{y + 75}" font-family="{FONT}" font-size="16" fill="{MUTED}">{sub}</text></g>'
    )


def arrow(x1: int, y1: int, x2: int, y2: int, label: str | None = None) -> str:
    line = f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{MUTED}" stroke-width="2.5" marker-end="url(#arrow)"/>'
    if label:
        line += f'<text x="{(x1 + x2) / 2}" y="{(y1 + y2) / 2 - 10}" text-anchor="middle" font-family="{FONT}" font-size="14" fill="{MUTED}">{label}</text>'
    return line


def make_lottery_pipeline() -> str:
    body = f'<text x="60" y="56" font-family="{FONT}" font-size="30" font-weight="700" fill="{NAVY}">Lottery scheduling: dispatch pipeline</text>'
    body += f'<text x="60" y="88" font-family="{FONT}" font-size="17" fill="{MUTED}">A positive ticket weight gives a proportional chance at each independent draw.</text>'
    y, w, h = 180, 230, 112
    xs = [55, 345, 635, 925]
    specs = [
        ("Ready processes", "Pᵢ with positive tickets", BLUE),
        ("Ticket pool", "Disjoint intervals; T = Σ tᵢ", TEAL),
        ("Random draw", "Choose integer k ∈ [1, T]", GOLD),
        ("Dispatch winner", "Run one modeled time slice", CORAL),
    ]
    for x, (heading, sub, color) in zip(xs, specs):
        body += box(x, y, w, h, heading, sub, color)
    for source_x, target_x in zip(xs[:-1], xs[1:]):
        body += arrow(source_x + w + 5, y + h // 2, target_x - 10, y + h // 2)
    body += f'<rect x="210" y="385" width="780" height="105" rx="16" fill="#E8F2F3" stroke="#B8D9D8"/>'
    body += f'<text x="600" y="428" text-anchor="middle" font-family="{FONT}" font-size="20" font-weight="700" fill="{NAVY}">Update the ready set, then repeat</text>'
    body += f'<text x="600" y="460" text-anchor="middle" font-family="{FONT}" font-size="16" fill="{MUTED}">Blocking, completion, and ticket changes are outside this minimal model.</text>'
    body += arrow(1040, 292, 1040, 436)
    body += arrow(210, 436, 170, 436)
    body += arrow(170, 436, 170, 235)
    body += arrow(170, 235, 55, 235)
    body += f'<text x="60" y="550" font-family="{FONT}" font-size="14" fill="{MUTED}">Educational model — not an operating-system kernel scheduler.</text>'
    return svg_document("Lottery scheduling dispatch pipeline", 1200, 600, body)


def make_lottery_flow() -> str:
    body = f'<text x="60" y="58" font-family="{FONT}" font-size="30" font-weight="700" fill="{NAVY}">One lottery dispatch: control flow</text>'
    body += f'<text x="60" y="90" font-family="{FONT}" font-size="17" fill="{MUTED}">The implementation uses cumulative ticket intervals and a seeded pseudo-random generator.</text>'
    nodes = [
        (85, 155, 300, 90, "1 · Validate ready set", "At least one process; ticket count &gt; 0", BLUE),
        (455, 155, 300, 90, "2 · Compute T", "T = sum of runnable ticket counts", TEAL),
        (825, 155, 300, 90, "3 · Draw k", "Uniform integer from 1 through T", GOLD),
        (825, 340, 300, 90, "4 · Map interval", "First cumulative total ≥ k", CORAL),
        (455, 340, 300, 90, "5 · Dispatch owner", "Return winner and draw trace", BLUE),
        (85, 340, 300, 90, "6 · Next decision", "Repeat when another choice is needed", TEAL),
    ]
    for x, y, w, h, heading, sub, color in nodes:
        body += box(x, y, w, h, heading, sub, color)
    body += arrow(385, 200, 455, 200)
    body += arrow(755, 200, 825, 200)
    body += arrow(975, 245, 975, 340)
    body += arrow(825, 385, 755, 385)
    body += arrow(455, 385, 385, 385)
    body += f'<rect x="80" y="485" width="1045" height="60" rx="14" fill="#FFF5DF" stroke="#EED69E"/>'
    body += f'<text x="602" y="523" text-anchor="middle" font-family="{FONT}" font-size="17" fill="{INK}">A ticket ratio is an expectation over repeated draws, not a promise about any finite prefix.</text>'
    return svg_document("Lottery scheduling control flow", 1200, 590, body)


def make_atomic_admission() -> str:
    body = f'<text x="55" y="55" font-family="{FONT}" font-size="30" font-weight="700" fill="{NAVY}">Dining philosophers: safe atomic admission</text>'
    body += f'<text x="55" y="88" font-family="{FONT}" font-size="17" fill="{MUTED}">The arbiter reserves both neighboring forks at once; no process waits while holding one fork.</text>'
    body += f'<rect x="390" y="190" width="420" height="215" rx="24" fill="#EAF3F4" stroke="{TEAL}" stroke-width="3" filter="url(#shadow)"/>'
    body += f'<text x="600" y="238" text-anchor="middle" font-family="{FONT}" font-size="24" font-weight="700" fill="{NAVY}">Central arbiter</text>'
    body += f'<text x="600" y="274" text-anchor="middle" font-family="{FONT}" font-size="17" fill="{INK}">check both forks → grant atomically</text>'
    body += f'<text x="600" y="307" text-anchor="middle" font-family="{FONT}" font-size="16" fill="{MUTED}">lottery among safe candidates</text>'
    body += f'<text x="600" y="348" text-anchor="middle" font-family="{FONT}" font-size="16" fill="{INK}">release both when the finite meal ends</text>'
    # Philosopher request cards and fork labels.
    cards = [(65, 160, "P0", "requests F4 + F0"), (65, 360, "P1", "requests F0 + F1"), (930, 160, "P2", "requests F1 + F2"), (930, 360, "P3", "requests F2 + F3")]
    for x, y, name, sub in cards:
        body += f'<rect x="{x}" y="{y}" width="210" height="88" rx="16" fill="{WHITE}" stroke="{BLUE}" stroke-width="2.5"/>'
        body += f'<text x="{x + 105}" y="{y + 34}" text-anchor="middle" font-family="{FONT}" font-size="22" font-weight="700" fill="{NAVY}">{name}</text>'
        body += f'<text x="{x + 105}" y="{y + 63}" text-anchor="middle" font-family="{FONT}" font-size="14" fill="{MUTED}">{sub}</text>'
    body += arrow(275, 204, 390, 235, "request")
    body += arrow(275, 404, 390, 350, "request")
    body += arrow(810, 235, 930, 204, "grant / release")
    body += arrow(810, 350, 930, 404, "grant / release")
    body += f'<text x="600" y="485" text-anchor="middle" font-family="{FONT}" font-size="17" font-weight="700" fill="{CORAL}">This prevents circular wait in the modeled admission path; lottery alone does not.</text>'
    body += f'<text x="600" y="522" text-anchor="middle" font-family="{FONT}" font-size="15" fill="{MUTED}">The diagram shows four sample philosophers; the simulator defaults to five.</text>'
    return svg_document("Dining philosophers atomic admission", 1200, 570, body)


def make_aging_flow() -> str:
    body = f'<text x="55" y="55" font-family="{FONT}" font-size="30" font-weight="700" fill="{NAVY}">Lottery + age override: one round</text>'
    body += f'<text x="55" y="88" font-family="{FONT}" font-size="17" fill="{MUTED}">Safety comes from the arbiter; a deterministic wait-age override supplies the modeled fairness policy.</text>'
    body += box(60, 160, 260, 100, "Start round", "All philosophers hungry; forks free", BLUE)
    body += '<path d="M320 210 L390 210" stroke="#64748B" stroke-width="2.5" marker-end="url(#arrow)"/>'
    body += f'<polygon points="500,140 610,210 500,280 390,210" fill="#FFF5DF" stroke="{GOLD}" stroke-width="2.5"/>'
    body += f'<text x="500" y="204" text-anchor="middle" font-family="{FONT}" font-size="17" font-weight="700" fill="{NAVY}">Any age ≥</text><text x="500" y="229" text-anchor="middle" font-family="{FONT}" font-size="17" font-weight="700" fill="{NAVY}">threshold?</text>'
    body += box(700, 130, 255, 92, "Yes · oldest wait", "Grant this philosopher first", CORAL)
    body += box(700, 270, 255, 92, "No · lottery", "Choose weighted safe candidate", TEAL)
    body += f'<path d="M610 195 L700 176" stroke="{MUTED}" stroke-width="2.5" marker-end="url(#arrow)"/><text x="656" y="172" font-family="{FONT}" font-size="14" fill="{MUTED}">yes</text>'
    body += f'<path d="M500 280 L500 316 L700 316" fill="none" stroke="{MUTED}" stroke-width="2.5" marker-end="url(#arrow)"/><text x="519" y="306" font-family="{FONT}" font-size="14" fill="{MUTED}">no</text>'
    body += box(1000, 190, 160, 110, "Atomic grant", "Reserve both forks", BLUE)
    body += '<path d="M955 176 L1000 220" stroke="#64748B" stroke-width="2.5" marker-end="url(#arrow)"/><path d="M955 316 L1000 270" stroke="#64748B" stroke-width="2.5" marker-end="url(#arrow)"/>'
    body += f'<rect x="120" y="410" width="960" height="92" rx="18" fill="#EDF5F5" stroke="#B7D4D4"/>'
    body += f'<text x="600" y="449" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="{NAVY}">Finite meal → release both forks → reset served age; increment others</text>'
    body += f'<text x="600" y="480" text-anchor="middle" font-family="{FONT}" font-size="15" fill="{MUTED}">With finite philosophers and finite rounds, the threshold override bounds bypasses in this model.</text>'
    body += '<path d="M1080 300 L1080 455 L1080 455" fill="none" stroke="#64748B" stroke-width="2.5" marker-end="url(#arrow)"/>'
    return svg_document("Lottery aging override flow", 1200, 550, body)


def _load_fonts():
    try:
        from PIL import ImageFont
    except ImportError as error:
        raise SystemExit("PNG generation requires Pillow; install the optional docs dependency with `python -m pip install 'Pillow>=10,<12'`.") from error
    regular_candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    ]
    bold_candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
    ]
    regular_path = next((path for path in regular_candidates if path.exists()), None)
    bold_path = next((path for path in bold_candidates if path.exists()), regular_path)
    if regular_path is None:
        return (ImageFont.load_default(),) * 4
    return (
        ImageFont.truetype(str(regular_path), 17),
        ImageFont.truetype(str(bold_path), 21),
        ImageFont.truetype(str(regular_path), 14),
        ImageFont.truetype(str(bold_path), 30),
    )


def render_frequency_png(png_path: Path, processes: list[Process], observed: Counter, draws: int, seed: int) -> None:
    from PIL import Image, ImageDraw

    regular, bold, small, title_font = _load_fonts()
    image = Image.new("RGB", (1200, 620), "#F8FAFC")
    draw = ImageDraw.Draw(image)
    draw.text((60, 38), "Lottery draws: expected vs observed share", font=title_font, fill=NAVY)
    draw.text((60, 88), f"{draws:,} seeded draws · seed {seed} · produced by LotteryScheduler", font=regular, fill=MUTED)
    draw.text((60, 119), "Finite sample only — not a guarantee or a performance benchmark.", font=small, fill=MUTED)

    left, top, plot_w, row_h = 270, 205, 800, 95
    for tick in range(0, 101, 20):
        x = left + plot_w * tick / 100
        draw.line((x, 175, x, top + row_h * 3 - 20), fill="#D9E1EA", width=1)
        draw.text((x - 14, 154), f"{tick}%", font=small, fill=MUTED)
    total_tickets = sum(process.tickets for process in processes)
    for row, process in enumerate(processes):
        y = top + row * row_h
        expected = process.tickets / total_tickets * 100
        actual = observed[process.name] / draws * 100
        draw.text((65, y + 3), process.name, font=bold, fill=NAVY)
        draw.text((65, y + 33), f"{process.tickets} ticket(s)", font=small, fill=MUTED)
        draw.rounded_rectangle((left, y, left + plot_w, y + 50), radius=10, fill="#E9EEF4")
        bar_end = left + plot_w * actual / 100
        draw.rounded_rectangle((left, y, bar_end, y + 50), radius=10, fill=TEAL)
        expected_x = left + plot_w * expected / 100
        draw.line((expected_x, y - 8, expected_x, y + 58), fill=CORAL, width=4)
        label = f"{actual:.2f}% observed · {expected:.2f}% expected"
        label_x = min(bar_end + 12, 840)
        draw.text((label_x, y + 14), label, font=small, fill=NAVY)
    draw.rounded_rectangle((65, 548, 84, 567), radius=3, fill=TEAL)
    draw.text((94, 548), "Observed sample", font=small, fill=INK)
    draw.line((260, 548, 260, 568), fill=CORAL, width=4)
    draw.text((274, 548), "Theoretical ticket ratio", font=small, fill=INK)
    image.save(png_path, format="PNG", optimize=True)


def render_philosopher_png(png_path: Path, trace, rounds: int, seed: int) -> None:
    from PIL import Image, ImageDraw

    regular, bold, small, title_font = _load_fonts()
    count = len(trace[0].wait_ages) if trace else 5
    image = Image.new("RGB", (1200, 590), "#F8FAFC")
    draw = ImageDraw.Draw(image)
    draw.text((55, 38), "Dining-philosophers simulation: meal Gantt chart", font=title_font, fill=NAVY)
    draw.text((55, 87), f"{rounds} rounds · {count} philosophers · seed {seed} · age threshold 3", font=regular, fill=MUTED)
    draw.text((55, 118), "Filled cell = one meal in that round; adjacent philosophers are never admitted together.", font=small, fill=MUTED)

    left, top, cell_w, cell_h = 175, 170, 45, 58
    for column in range(rounds):
        draw.text((left + column * cell_w + 13, 148), str(column + 1), font=small, fill=MUTED)
    for philosopher in range(count):
        y = top + philosopher * cell_h
        draw.text((70, y + 14), f"P{philosopher}", font=bold, fill=NAVY)
        draw.rounded_rectangle((left - 5, y - 5, left + cell_w * rounds + 5, y + cell_h - 9), radius=6, fill="#F1F4F8")
        for event in trace:
            if philosopher in event.eaters:
                x = left + (event.round_number - 1) * cell_w
                color = CORAL if event.forced_priority == philosopher else TEAL
                draw.rounded_rectangle((x + 2, y + 2, x + cell_w - 2, y + cell_h - 16), radius=7, fill=color)
                draw.text((x + 7, y + 17), "meal", font=small, fill=WHITE)
    draw.rounded_rectangle((170, 528, 189, 547), radius=3, fill=TEAL)
    draw.text((198, 528), "Lottery admission", font=small, fill=INK)
    draw.rounded_rectangle((385, 528, 404, 547), radius=3, fill=CORAL)
    draw.text((413, 528), "Age-override admission", font=small, fill=INK)
    draw.text((710, 528), "Model time is round-based, not seconds.", font=small, fill=MUTED)
    image.save(png_path, format="PNG", optimize=True)


def make_data_charts() -> None:
    # The counts below are generated by the actual project implementation.
    processes = [Process("P1", 1), Process("P2", 2), Process("P3", 4)]
    draw_count = 50_000
    seed = 20261123
    scheduler = LotteryScheduler(processes, seed=seed)
    observed = Counter(draw.process.name for draw in scheduler.run(draw_count))
    out = EX1 / "outputs"
    figures = EX1 / "docs/figures"
    out.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    csv_path = out / "lottery-frequency.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["process", "tickets", "expected_share", "draws", "observed_share", "seed"])
        for process in processes:
            count = observed[process.name]
            writer.writerow([
                process.name,
                process.tickets,
                f"{scheduler.expected_share(process.name):.8f}",
                count,
                f"{count / draw_count:.8f}",
                seed,
            ])

    width, height = 1200, 620
    left, top, plot_w, row_h = 270, 205, 800, 95
    body = f'<text x="60" y="55" font-family="{FONT}" font-size="30" font-weight="700" fill="{NAVY}">Lottery draws: theoretical share vs observed sample</text>'
    body += f'<text x="60" y="91" font-family="{FONT}" font-size="17" fill="{MUTED}">{draw_count:,} draws · seed {seed} · generated by lottery_lab.LotteryScheduler</text>'
    body += f'<text x="60" y="121" font-family="{FONT}" font-size="15" fill="{MUTED}">Observed frequency is a finite sample, not a guarantee or performance benchmark.</text>'
    for tick in range(0, 101, 20):
        x = left + plot_w * tick / 100
        body += f'<line x1="{x}" y1="175" x2="{x}" y2="{top + row_h * 3 - 20}" stroke="#D9E1EA" stroke-width="1"/>'
        body += f'<text x="{x}" y="160" text-anchor="middle" font-family="{FONT}" font-size="14" fill="{MUTED}">{tick}%</text>'
    for row, process in enumerate(processes):
        y = top + row * row_h
        expected = scheduler.expected_share(process.name) * 100
        actual = observed[process.name] / draw_count * 100
        body += f'<text x="65" y="{y + 22}" font-family="{FONT}" font-size="21" font-weight="700" fill="{NAVY}">{process.name}</text>'
        body += f'<text x="65" y="{y + 49}" font-family="{FONT}" font-size="15" fill="{MUTED}">{process.tickets} ticket(s)</text>'
        body += f'<rect x="{left}" y="{y}" width="{plot_w}" height="50" rx="10" fill="#E9EEF4"/>'
        body += f'<rect x="{left}" y="{y}" width="{plot_w * actual / 100:.2f}" height="50" rx="10" fill="{TEAL}"/>'
        expected_x = left + plot_w * expected / 100
        body += f'<line x1="{expected_x}" y1="{y - 8}" x2="{expected_x}" y2="{y + 58}" stroke="{CORAL}" stroke-width="4"/>'
        body += f'<text x="{left + plot_w * actual / 100 + 12}" y="{y + 32}" font-family="{FONT}" font-size="16" font-weight="700" fill="{NAVY}">{actual:.2f}% observed · {expected:.2f}% expected</text>'
    body += f'<rect x="65" y="{height - 72}" width="18" height="18" rx="3" fill="{TEAL}"/><text x="92" y="{height - 57}" font-family="{FONT}" font-size="15" fill="{INK}">Observed sample</text>'
    body += f'<line x1="260" y1="{height - 63}" x2="260" y2="{height - 43}" stroke="{CORAL}" stroke-width="4"/><text x="274" y="{height - 57}" font-family="{FONT}" font-size="15" fill="{INK}">Theoretical ticket ratio</text>'
    svg_path = figures / "lottery-frequency.svg"
    svg_path.write_text(svg_document("Lottery theoretical and observed share", width, height, body), encoding="utf-8")
    render_frequency_png(figures / "lottery-frequency.png", processes, observed, draw_count, seed)

    # Real trace for the age-override model; each highlighted cell is a meal
    # admitted by the executable simulator during that discrete round.
    simulator = DiningPhilosophers(
        philosophers=5,
        tickets=[1, 2, 3, 4, 5],
        seed=seed,
        max_wait_rounds=3,
    )
    trace = simulator.run(20)
    out8 = EX8 / "outputs"
    fig8 = EX8 / "docs/figures"
    out8.mkdir(parents=True, exist_ok=True)
    fig8.mkdir(parents=True, exist_ok=True)
    csv_path = out8 / "philosopher-rounds.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["round", "eaters", "waiting", "forced_priority", "wait_ages_after_round"])
        for event in trace:
            writer.writerow([
                event.round_number,
                ";".join(f"P{i}" for i in event.eaters),
                ";".join(f"P{i}" for i in event.waiting),
                "" if event.forced_priority is None else f"P{event.forced_priority}",
                ";".join(map(str, event.wait_ages)),
            ])

    width, height = 1200, 590
    left, top, cell_w, cell_h = 175, 170, 45, 58
    body = f'<text x="55" y="55" font-family="{FONT}" font-size="30" font-weight="700" fill="{NAVY}">Dining-philosophers simulation: meal Gantt chart</text>'
    body += f'<text x="55" y="91" font-family="{FONT}" font-size="17" fill="{MUTED}">20 rounds · 5 philosophers · seed {seed} · age threshold 3 · generated from executable simulator</text>'
    body += f'<text x="55" y="121" font-family="{FONT}" font-size="15" fill="{MUTED}">A filled cell means that philosopher ate in the round; adjacent filled cells in one column are forbidden.</text>'
    for column in range(20):
        x = left + column * cell_w
        body += f'<text x="{x + cell_w / 2}" y="151" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{MUTED}">{column + 1}</text>'
    for p in range(5):
        y = top + p * cell_h
        body += f'<text x="70" y="{y + 31}" font-family="{FONT}" font-size="18" font-weight="700" fill="{NAVY}">P{p}</text>'
        body += f'<rect x="{left - 5}" y="{y - 5}" width="{cell_w * 20 + 10}" height="{cell_h}" rx="6" fill="#F1F4F8"/>'
        for event in trace:
            x = left + (event.round_number - 1) * cell_w
            if p in event.eaters:
                fill = CORAL if event.forced_priority == p else TEAL
                body += f'<rect x="{x + 2}" y="{y + 2}" width="{cell_w - 4}" height="{cell_h - 14}" rx="7" fill="{fill}"/>'
                body += f'<text x="{x + cell_w / 2}" y="{y + 29}" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="700" fill="{WHITE}">meal</text>'
    body += f'<rect x="170" y="{height - 75}" width="18" height="18" rx="3" fill="{TEAL}"/><text x="198" y="{height - 60}" font-family="{FONT}" font-size="15" fill="{INK}">Lottery admission</text>'
    body += f'<rect x="385" y="{height - 75}" width="18" height="18" rx="3" fill="{CORAL}"/><text x="413" y="{height - 60}" font-family="{FONT}" font-size="15" fill="{INK}">Age-override admission</text>'
    body += f'<text x="710" y="{height - 60}" font-family="{FONT}" font-size="14" fill="{MUTED}">Model time is round-based, not seconds.</text>'
    svg_path = fig8 / "philosopher-gantt.svg"
    svg_path.write_text(svg_document("Dining philosophers simulation Gantt chart", width, height, body), encoding="utf-8")
    render_philosopher_png(fig8 / "philosopher-gantt.png", trace, 20, seed)


def make_realtime_schedule_artifacts() -> None:
    """Generate EDF/RM schedule data and a Gantt chart from the branch task set."""
    tasks = [
        PeriodicTask("P1", execution=1, period=4),
        PeriodicTask("P2", execution=1, period=5),
        PeriodicTask("P3", execution=2, period=10),
    ]
    horizon = hyperperiod(tasks)
    results = [simulate_schedule(tasks, policy, horizon) for policy in ("EDF", "RM")]
    output_dir = EX3 / "outputs"
    figure_dir = EX3 / "docs/figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    with (output_dir / "edf-rm-schedule.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["policy", "start", "end", "task", "job_number", "absolute_deadline"])
        for result in results:
            for segment in result.segments:
                writer.writerow([
                    result.policy,
                    segment.start,
                    segment.end,
                    segment.task_name or "IDLE",
                    "" if segment.job_number is None else segment.job_number,
                    "" if segment.absolute_deadline is None else segment.absolute_deadline,
                ])
    with (output_dir / "analysis-summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["hyperperiod", "utilization", "rm_sufficient_bound", "edf_misses", "rm_misses"])
        writer.writerow([
            horizon,
            f"{utilization(tasks):.8f}",
            f"{rm_utilization_bound(len(tasks)):.8f}",
            len(results[0].misses),
            len(results[1].misses),
        ])

    colors = {"P1": BLUE, "P2": TEAL, "P3": GOLD, None: "#CBD5E1"}
    width, height = 1280, 550
    left, plot_width = 180, 980
    lane_y = {"EDF": 220, "RM": 330}
    lane_h = 58
    body = f'<text x="55" y="55" font-family="{FONT}" font-size="30" font-weight="700" fill="{NAVY}">EDF and RM schedule · supplied three-task set</text>'
    body += f'<text x="55" y="91" font-family="{FONT}" font-size="17" fill="{MUTED}">H={horizon} · U={utilization(tasks):.2f} · RM sufficient bound={rm_utilization_bound(3):.3f} · no deadline misses</text>'
    body += f'<text x="55" y="121" font-family="{FONT}" font-size="15" fill="{MUTED}">Preemptive uniprocessor · integer time · implicit deadlines · zero context-switch cost</text>'
    for tick in range(horizon + 1):
        x = left + plot_width * tick / horizon
        body += f'<line x1="{x:.1f}" y1="185" x2="{x:.1f}" y2="405" stroke="#D9E1EA" stroke-width="1"/>'
        body += f'<text x="{x:.1f}" y="175" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{MUTED}">{tick}</text>'
    for result in results:
        y = lane_y[result.policy]
        body += f'<text x="125" y="{y + 36}" text-anchor="end" font-family="{FONT}" font-size="20" font-weight="700" fill="{NAVY}">{result.policy}</text>'
        for segment in result.segments:
            x = left + plot_width * segment.start / horizon
            seg_width = plot_width * (segment.end - segment.start) / horizon
            color = colors[segment.task_name]
            body += f'<rect x="{x:.1f}" y="{y}" width="{seg_width:.1f}" height="{lane_h}" fill="{color}" stroke="#FFFFFF" stroke-width="2"/>'
            if segment.task_name:
                label = f"{segment.task_name} J{segment.job_number}"
                text_color = NAVY if segment.task_name == "P3" else WHITE
                body += f'<text x="{x + seg_width / 2:.1f}" y="{y + 36}" text-anchor="middle" font-family="{FONT}" font-size="14" font-weight="700" fill="{text_color}">{label}</text>'
            elif segment.end - segment.start >= 2:
                body += f'<text x="{x + seg_width / 2:.1f}" y="{y + 36}" text-anchor="middle" font-family="{FONT}" font-size="14" fill="{INK}">idle</text>'
    body += f'<rect x="55" y="455" width="1170" height="58" rx="14" fill="#F1F5F9"/>'
    legend_x = 85
    for task_name in ("P1", "P2", "P3", None):
        label = "Idle" if task_name is None else task_name
        color = colors[task_name]
        body += f'<rect x="{legend_x}" y="475" width="20" height="18" rx="3" fill="{color}"/>'
        body += f'<text x="{legend_x + 28}" y="490" font-family="{FONT}" font-size="15" fill="{INK}">{label}</text>'
        legend_x += 150
    svg_path = figure_dir / "edf-rm-gantt.svg"
    svg_path.write_text(
        svg_document(
            "EDF and RM Gantt schedule for three tasks",
            width,
            height,
            body,
            "Actual schedule produced by the repository simulator for the periodic task set documented in Exercise 3.",
        ),
        encoding="utf-8",
    )

    from PIL import Image, ImageDraw
    regular, bold, small, title_font = _load_fonts()
    image = Image.new("RGB", (width, height), "#F8FAFC")
    draw = ImageDraw.Draw(image)
    draw.text((55, 38), "EDF and RM schedule · supplied three-task set", font=title_font, fill=NAVY)
    draw.text((55, 82), f"H={horizon} · U={utilization(tasks):.2f} · RM sufficient bound={rm_utilization_bound(3):.3f} · no deadline misses", font=regular, fill=MUTED)
    draw.text((55, 114), "Preemptive uniprocessor · integer time · implicit deadlines · zero context-switch cost", font=small, fill=MUTED)
    for tick in range(horizon + 1):
        x = left + plot_width * tick / horizon
        draw.line((x, 185, x, 405), fill="#D9E1EA", width=1)
        draw.text((x - 5, 165), str(tick), font=small, fill=MUTED)
    for result in results:
        y = lane_y[result.policy]
        draw.text((65, y + 15), result.policy, font=bold, fill=NAVY)
        for segment in result.segments:
            x1 = left + plot_width * segment.start / horizon
            x2 = left + plot_width * segment.end / horizon
            color = colors[segment.task_name]
            draw.rectangle((x1, y, x2, y + lane_h), fill=color, outline=WHITE, width=2)
            if segment.task_name:
                label = f"{segment.task_name} J{segment.job_number}"
                draw.text((x1 + 4, y + 19), label, font=small, fill=NAVY if segment.task_name == "P3" else WHITE)
            elif segment.end - segment.start >= 2:
                draw.text((x1 + (x2 - x1) / 2 - 16, y + 19), "idle", font=small, fill=INK)
    draw.rounded_rectangle((55, 455, 1225, 513), radius=14, fill="#F1F5F9")
    legend_x = 85
    for task_name in ("P1", "P2", "P3", None):
        label = "Idle" if task_name is None else task_name
        color = colors[task_name]
        draw.rounded_rectangle((legend_x, 475, legend_x + 20, 493), radius=3, fill=color)
        draw.text((legend_x + 28, 474), label, font=small, fill=INK)
        legend_x += 150
    image.save(figure_dir / "edf-rm-gantt.png", format="PNG", optimize=True)


def main() -> None:
    (EX1 / "docs/figures").mkdir(parents=True, exist_ok=True)
    (EX3 / "docs/figures").mkdir(parents=True, exist_ok=True)
    (EX8 / "docs/figures").mkdir(parents=True, exist_ok=True)
    outputs = {
        EX1 / "docs/figures/lottery-pipeline.svg": make_lottery_pipeline(),
        EX1 / "docs/figures/lottery-control-flow.svg": make_lottery_flow(),
        EX8 / "docs/figures/atomic-fork-admission.svg": make_atomic_admission(),
        EX8 / "docs/figures/lottery-aging-flow.svg": make_aging_flow(),
    }
    for path, contents in outputs.items():
        path.write_text(contents, encoding="utf-8")
    make_realtime_schedule_artifacts()
    make_data_charts()
    print("Generated structural diagrams and three data-backed schedule/frequency chart sets with CSV sources.")


if __name__ == "__main__":
    main()
