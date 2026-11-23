#!/usr/bin/env python3
"""Hand-solution workbook for Assignment 3 (EDF and RM on paper).

The point of this assignment is that a human draws the schedule on paper. This module
does **not** simulate: it reads a *hand-written* answer in a tiny plain-text markup
(the same layout a student would draw), renders it, and then checks it against the
theory (exact response-time analysis for RM, processor demand for EDF).

Markup
------
    # Task set: three processes
    task P1 T=10 C=3
    task P2 T=15 C=4
    task P3 T=30 C=6

    # Hand-drawn schedule, one row per process, one char per tick.
    # '#' = the process runs, '.' = it does not.  The row may be shorter than the
    # horizon (it is padded with '.'), and '|' is accepted as a visual ruler.
    draw RM
    P1  ###.......###.......###.......
    P2  ...####.......####.......####
    P3  ......######........######...
    end

    # Hand calculations, checked against the analyser.
    calc U 0.767
    calc R(P3) 14
    calc dbf_ok yes

Run:  python3 workbook.py            # verify the shipped answers, write data/
      python3 workbook.py --check    # exit 1 on a wrong answer
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "data")

# --------------------------------------------------------------------------- model


@dataclass
class Task:
    name: str
    period: int
    wcet: int
    deadline: int | None = None

    def __post_init__(self):
        if self.wcet <= 0:
            raise ValueError(f"{self.name}: C must be positive")
        if self.wcet > self.period:
            raise ValueError(f"{self.name}: C={self.wcet} exceeds T={self.period}")
        if self.deadline is None:
            self.deadline = self.period

    @property
    def utilisation(self) -> float:
        return self.wcet / self.period

    def jobs_in(self, horizon: int) -> list[int]:
        """Release times of this task inside [0, horizon)."""
        return list(range(0, horizon, self.period))


def hyperperiod(tasks: list[Task]) -> int:
    h = 1
    for t in tasks:
        h = h * t.period // math.gcd(h, t.period)
    return h


def utilisation(tasks: list[Task]) -> float:
    return sum(t.utilisation for t in tasks)


def rm_bound(n: int) -> float:
    return n * (2 ** (1 / n) - 1)


# --------------------------------------------------------------------------- theory


def response_time(tasks: list[Task], task: Task, limit: int = 10_000) -> int | None:
    """Exact worst-case response time by fixed-point iteration (RM priority order).

    Returns None when the iteration does not converge below the deadline.
    """
    order = sorted(range(len(tasks)), key=lambda i: tasks[i].period)
    idx = order.index(tasks.index(task))
    higher = [tasks[order[i]] for i in range(idx)]
    r = task.wcet
    for _ in range(1000):
        interference = sum(math.ceil(r / h.period) * h.wcet for h in higher)
        nxt = task.wcet + interference
        if nxt == r:
            return r if r <= task.deadline else None
        if nxt > limit:
            return None
        r = nxt
    return None


def rta_table(tasks: list[Task]) -> dict[str, dict]:
    out = {}
    for t in sorted(tasks, key=lambda x: x.period):
        r = response_time(tasks, t)
        out[t.name] = {"C": t.wcet, "T": t.period, "R": r, "feasible": r is not None}
    return out


def dbf(tasks: list[Task], L: int) -> int:
    """Processor demand bound for a window of length L."""
    total = 0
    for t in tasks:
        d = t.deadline
        if L >= d:
            total += ((L - d) // t.period + 1) * t.wcet
    return total


def edf_feasible(tasks: list[Task], horizon: int | None = None) -> bool:
    """Exact EDF test for D <= T: check the demand bound at every deadline point."""
    horizon = horizon or hyperperiod(tasks)
    points = sorted({k * t.period + t.deadline for t in tasks
                     for k in range(0, horizon // t.period + 1)})
    return all(dbf(tasks, L) <= L for L in points if L <= horizon)


def max_demand_deficit(tasks: list[Task]) -> tuple[int, int]:
    """The tightest point (L, dbf(L)-L); a positive deficit means infeasible."""
    horizon = hyperperiod(tasks)
    worst = (0, -10 ** 9)
    for L in range(1, horizon + 1):
        d = dbf(tasks, L) - L
        if d > worst[1]:
            worst = (L, d)
    return worst


# --------------------------------------------------------------------------- markup


@dataclass
class HandSchedule:
    algorithm: str
    rows: dict[str, str] = field(default_factory=dict)
    horizon: int = 0
    expect: str = "ok"      # "ok" = no deadline may be missed, "miss" = a miss is the point


@dataclass
class Workbook:
    title: str = ""
    tasks: list[Task] = field(default_factory=list)
    schedules: list[HandSchedule] = field(default_factory=list)
    calcs: dict[str, str] = field(default_factory=dict)


def parse_workbook(text: str) -> Workbook:
    wb = Workbook()
    current: HandSchedule | None = None
    for raw in text.splitlines():
        # '#' marks a running tick in the drawing, so comments use ';'
        stripped = raw.strip()
        if not stripped or stripped.startswith(";"):
            continue
        line = raw.split(";", 1)[0].rstrip()
        if not line.strip():
            continue
        parts = line.split()
        head = parts[0].lower()
        if head == "title":
            wb.title = line[len("title"):].strip()
        elif head == "task":
            m = re.match(r"task\s+(\S+)\s+T=(\d+)\s+C=(\d+)(?:\s+D=(\d+))?", line.strip())
            if not m:
                raise ValueError(f"bad task line: {raw!r}")
            wb.tasks.append(Task(m.group(1), int(m.group(2)), int(m.group(3)),
                                 int(m.group(4)) if m.group(4) else None))
        elif head == "draw":
            flags = [p for p in parts[2:] if p.startswith("expect=")]
            current = HandSchedule(
                algorithm=parts[1].lower(),
                expect=(flags[0].split("=", 1)[1] if flags else "ok"),
            )
            wb.schedules.append(current)
        elif head == "end":
            if current is not None and current.rows:
                current.horizon = max(len(v) for v in current.rows.values())
            current = None
        elif head == "calc":
            wb.calcs[parts[1]] = " ".join(parts[2:])
        elif current is not None and len(parts) >= 2 and parts[0].upper().startswith("P"):
            current.rows[parts[0]] = parts[1].replace("|", "")
    if not wb.tasks:
        raise ValueError("workbook has no tasks")
    # The horizon of a drawing covers at least one full hyperperiod so that every job
    # in the first period is checked, even if the student drew fewer characters.
    h = hyperperiod(wb.tasks)
    for hs in wb.schedules:
        if max((len(v) for v in hs.rows.values()), default=0) < h:
            hs.horizon = h
    return wb


def load(path: str) -> Workbook:
    with open(path, encoding="utf-8") as f:
        return parse_workbook(f.read())


# --------------------------------------------------------------------------- checking

RUN = "#"


def check_schedule(wb: Workbook, hs: HandSchedule) -> list[str]:
    """Validate a hand-drawn schedule against the task model.

    Checks: every row is long enough, no two processes run in the same tick, no process
    runs more than it is allowed to, and every job completes before its deadline.
    """
    problems: list[str] = []
    horizon = hs.horizon
    names = [t.name for t in wb.tasks]
    missing = [n for n in names if n not in hs.rows]
    if missing:
        problems.append(f"missing rows: {', '.join(missing)}")
        return problems

    # 1) shape: every row must cover the horizon; pad short rows with '.'
    for n in names:
        row = hs.rows[n]
        if len(row) < horizon:
            hs.rows[n] = row + "." * (horizon - len(row))
        bad = set(hs.rows[n]) - {RUN, "."}
        if bad:
            problems.append(f"{n}: unknown symbols {sorted(bad)}")

    # 2) at most one process per tick
    for tick in range(horizon):
        running = [n for n in names if hs.rows[n][tick] == RUN]
        if len(running) > 1:
            problems.append(f"tick {tick}: {len(running)} processes run at once ({', '.join(running)})")
        if not running and tick < horizon:
            pass  # idle ticks are legal

    # 3) budget and deadline check per job
    misses = []
    for t in wb.tasks:
        row = hs.rows[t.name]
        for release in range(0, horizon, t.period):
            end = min(horizon, release + t.deadline)
            served = sum(1 for k in range(release, end) if row[k] == RUN)
            if served < t.wcet:
                misses.append((t.name, release, served, t.wcet))

    # 4) the drawing must agree with the declared intent
    if hs.expect == "ok" and misses:
        for name, release, served, need in misses:
            problems.append(
                f"{name}: job released at {release} got {served}/{need} ticks before its deadline")
    elif hs.expect == "miss" and not misses:
        problems.append("declared expect=miss, but every job met its deadline")

    # 5) a process may never receive more service than it can use
    for t in wb.tasks:
        served = hs.rows[t.name].count(RUN)
        allowed = len(t.jobs_in(horizon)) * t.wcet
        if served > allowed:
            problems.append(f"{t.name}: {served} ticks drawn but only {allowed} are usable")
    return problems


def check_calcs(wb: Workbook) -> list[str]:
    """Compare the hand-entered numbers with the analyser's own results."""
    problems: list[str] = []
    u = utilisation(wb.tasks)
    table = rta_table(wb.tasks)

    def close(a: float, b: float, tol=5e-3) -> bool:
        return abs(a - b) <= tol

    for key, value in wb.calcs.items():
        v = value.strip()
        if key == "U":
            try:
                got = float(v.replace("٫", ".").replace(",", "."))
            except ValueError:
                problems.append(f"U: cannot read {v!r}")
                continue
            if not close(got, u):
                problems.append(f"U: wrote {got:.3f}, analyser says {u:.3f}")
        elif key.startswith("R(") and key.endswith(")"):
            name = key[2:-1]
            row = table.get(name)
            if row is None:
                problems.append(f"{key}: unknown task")
                continue
            try:
                got = int(v)
            except ValueError:
                problems.append(f"{key}: cannot read {v!r}")
                continue
            want = row["R"]
            if want is None:
                problems.append(f"{key}: wrote {got}, but the task is not schedulable")
            elif got != want:
                problems.append(f"{key}: wrote {got}, analyser says {want}")
        elif key == "dbf_ok":
            want = edf_feasible(wb.tasks)
            got = v.lower() in ("yes", "true", "1", "بله")
            if got != want:
                problems.append(f"dbf_ok: wrote {v}, analyser says {'yes' if want else 'no'}")
        elif key == "rm_bound":
            try:
                got = float(v)
            except ValueError:
                problems.append(f"rm_bound: cannot read {v!r}")
                continue
            want = rm_bound(len(wb.tasks))
            if not close(got, want):
                problems.append(f"rm_bound: wrote {got:.3f}, formula gives {want:.3f}")
        else:
            problems.append(f"{key}: unknown calculation")
    return problems


# --------------------------------------------------------------------------- reporting


def analyse(wb: Workbook) -> dict:
    tasks = wb.tasks
    u = utilisation(tasks)
    bound = rm_bound(len(tasks))
    table = rta_table(tasks)
    feasible_rm = all(r["feasible"] for r in table.values())
    worst = max_demand_deficit(tasks)
    report = {
        "tasks": [{"name": t.name, "T": t.period, "C": t.wcet, "D": t.deadline,
                   "U": round(t.utilisation, 6)} for t in tasks],
        "hyperperiod": hyperperiod(tasks),
        "utilisation": round(u, 6),
        "rm_bound": round(bound, 6),
        "above_bound": u > bound,
        "rta": table,
        "rm_feasible": feasible_rm,
        "edf_feasible": edf_feasible(tasks),
        "worst_deficit": {"L": worst[0], "deficit": worst[1]},
        "schedules": [],
    }
    for hs in wb.schedules:
        problems = check_schedule(wb, hs)
        served = {n: hs.rows[n].count(RUN) for n in hs.rows}
        report["schedules"].append({
            "algorithm": hs.algorithm,
            "horizon": hs.horizon,
            "expect": hs.expect,
            "rows": {n: hs.rows[n] for n in hs.rows},
            "problems": problems,
            "ok": not problems,
            "served": served,
        })
    report["calc_problems"] = check_calcs(wb)
    report["ok"] = (not report["calc_problems"]
                    and all(s["ok"] for s in report["schedules"]))
    return report


def ascii_schedule(wb: Workbook, hs: HandSchedule, width: int = 60) -> str:
    """Render the hand-drawn rows as a monospace ruler for the report."""
    out = []
    out.append(f"{hs.algorithm.upper()} hand-drawn schedule (one char = one tick)")
    head = "      " + "".join(str(i % 10) for i in range(min(width, hs.horizon)))
    out.append(head)
    for t in wb.tasks:
        row = hs.rows[t.name][:width]
        out.append(f"{t.name:5s} {row}")
    out.append("      " + "-" * min(width, hs.horizon))
    return "\n".join(out)


def main(argv: list[str]) -> int:
    wb_path = os.path.join(DATA, "paper_work.txt")
    if not os.path.exists(wb_path):
        print(f"missing {wb_path}", file=sys.stderr)
        return 2
    wb = load(wb_path)
    rep = analyse(wb)
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "paper_check.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)

    print(f"tasks: {len(wb.tasks)}   hyperperiod: {rep['hyperperiod']}   U = {rep['utilisation']:.4f}")
    print(f"RM bound: {rep['rm_bound']:.4f}   above bound: {rep['above_bound']}")
    for name, r in rep["rta"].items():
        print(f"  R({name}) = {r['R']}   deadline {r['T']}   {'OK' if r['feasible'] else 'MISS'}")
    print(f"RM feasible: {rep['rm_feasible']}   EDF feasible: {rep['edf_feasible']}")
    for s in rep["schedules"]:
        print(f"  hand-drawn {s['algorithm']}: {'OK' if s['ok'] else 'PROBLEMS'}")
        for p in s["problems"]:
            print("    -", p)
    if rep["calc_problems"]:
        print("hand calculations:")
        for p in rep["calc_problems"]:
            print("    -", p)
    else:
        print("hand calculations: all match the analyser")

    # a readable transcript for the report appendix
    lines = []
    for hs in wb.schedules:
        lines.append(ascii_schedule(wb, hs))
        lines.append("")
    with open(os.path.join(DATA, "hand_schedules.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    if "--check" in argv and not rep["ok"]:
        print("\nVERIFICATION FAILED", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
