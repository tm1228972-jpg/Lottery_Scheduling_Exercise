"""EDF vs Rate-Monotonic: a real-time scheduling simulator (Assignment 2).

The simulator is deterministic (tick-based) and produces everything the report
needs: utilisation tests, a feasibility check by exhaustive simulation, response
times, deadline misses under overload, and a full schedule trace for plotting.

    python3 rt_sim.py --seed 7 > ../data/rt_results.json
"""
from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass, field


@dataclass
class Task:
    name: str
    period: int
    wcet: int
    deadline: int = 0          # 0 -> equal to the period
    criticality: int = 1       # 1: hard, 2: soft (used by overload experiments)

    def __post_init__(self):
        if self.deadline == 0:
            self.deadline = self.period
        if not (0 < self.wcet <= self.period):
            raise ValueError(f"{self.name}: WCET must satisfy 0 < C <= T")
        if self.deadline > self.period:
            raise ValueError(f"{self.name}: the model assumes D <= T")

    @property
    def utilisation(self) -> float:
        return self.wcet / self.period

    @property
    def density(self) -> float:
        return self.wcet / self.deadline


def lcm(a: int, b: int) -> int:
    return abs(a * b) // math.gcd(a, b) if a and b else 0


def hyperperiod(tasks) -> int:
    h = 1
    for t in tasks:
        h = lcm(h, t.period)
    return h


# --------------------------------------------------------------------- schedulers
def simulate(tasks, algorithm: str, horizon: int, trace: bool = False) -> dict:
    """Tick-level fixed-priority / EDF simulation.

    algorithm: "rm" | "edf" | "fcfs"
    Returns per-task statistics plus an optional per-tick trace.
    """
    jobs = []          # list of dicts: task, release, remaining, deadline, done_at
    meta = {t.name: t for t in tasks}
    for t in tasks:
        r = 0
        while r < horizon:
            jobs.append({"task": t.name, "release": r, "remaining": t.wcet,
                         "deadline": r + t.deadline, "done_at": None})
            r += t.period
    timeline = []
    misses = {t.name: 0 for t in tasks}
    wait = {t.name: [] for t in tasks}
    resp = {t.name: [] for t in tasks}
    completed = 0
    for now in range(horizon):
        # a job is executable only strictly inside its window: release <= t < deadline
        ready = [j for j in jobs if j["release"] <= now < j["deadline"] and j["remaining"] > 0]
        if not ready:
            timeline.append("idle")
            continue
        if algorithm == "edf":
            chosen = min(ready, key=lambda j: (j["deadline"], j["release"], j["task"]))
        elif algorithm == "rm":
            chosen = min(ready, key=lambda j: (meta[j["task"]].period, j["release"], j["task"]))
        elif algorithm == "fcfs":
            chosen = min(ready, key=lambda j: (j["release"], j["task"]))
        else:
            raise ValueError(algorithm)
        chosen["remaining"] -= 1
        timeline.append(chosen["task"])
        if chosen["remaining"] == 0:
            chosen["done_at"] = now + 1
            completed += 1
            resp[chosen["task"]].append(now + 1 - chosen["release"])
            wait[chosen["task"]].append(now + 1 - chosen["release"] - meta[chosen["task"]].wcet)
            if chosen["done_at"] > chosen["deadline"]:
                misses[chosen["task"]] += 1
    # a deadline miss is counted once per job: the job was not finished at its deadline
    for j in jobs:
        if j["deadline"] <= horizon and j["remaining"] > 0:
            if not any(k["task"] == j["task"] and k["release"] == j["release"]
                       and k["done_at"] is not None and k["done_at"] > j["deadline"] for k in jobs):
                misses[j["task"]] += 1
    total_misses = sum(misses.values())
    util = sum(t.utilisation for t in tasks)
    return {
        "algorithm": algorithm,
        "utilisation": util,
        "total_misses": total_misses,
        "misses": misses,
        "response_mean": {k: (sum(v) / len(v) if v else 0.0) for k, v in resp.items()},
        "response_max": {k: (max(v) if v else 0.0) for k, v in resp.items()},
        "completed": completed,
        "timeline": timeline if trace else None,
    }


def rta(tasks, order=None) -> dict:
    """Exact worst-case response-time analysis for fixed-priority tasks."""
    order = order or sorted(range(len(tasks)), key=lambda i: tasks[i].period)
    response, feasible = {}, True
    for idx, i in enumerate(order):
        t = tasks[i]
        higher = [tasks[j] for j in order[:idx]]
        R = t.wcet
        for _ in range(200):
            interference = sum(math.ceil(R / h.period) * h.wcet for h in higher)
            new = t.wcet + interference
            if new == R:
                break
            R = new
            if R > t.deadline:
                break
        response[t.name] = R
        if R > t.deadline:
            feasible = False
    return {"response": response, "feasible": feasible, "order": [tasks[i].name for i in order]}


def utilisation_bounds(tasks) -> dict:
    n = len(tasks)
    rm_bound = n * (2 ** (1 / n) - 1) if n else 0
    return {
        "utilisation": sum(t.utilisation for t in tasks),
        "rm_bound": rm_bound,
        "density": sum(t.density for t in tasks),
        "edf_sufficient": sum(t.utilisation for t in tasks) <= 1.0,
    }


# --------------------------------------------------------------------- experiments
def random_taskset(seed: int, n: int, target_util: float, min_period=10, max_period=60) -> list[Task]:
    rng = random.Random(seed)
    tasks, total = [], 0.0
    for i in range(n):
        period = rng.randint(min_period, max_period)
        remaining = target_util - total
        if remaining <= 0:
            break
        share = remaining / (n - i)
        wcet = max(1, min(period, round(share * period)))
        total += wcet / period
        tasks.append(Task(f"T{i + 1}", period, wcet))
    return tasks


def utilisation_sweep(seed: int, runs=40, n=4) -> dict:
    """Measure miss rate of RM and EDF as utilisation grows past the bounds."""
    rows = []
    for u in (0.5, 0.6, 0.69, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.05):
        rm_miss = edf_miss = 0
        for r in range(runs):
            tasks = random_taskset(seed + r, n, u)
            if not tasks:
                continue
            h = min(hyperperiod(tasks), 4000)
            rm_miss += simulate(tasks, "rm", h)["total_misses"]
            edf_miss += simulate(tasks, "edf", h)["total_misses"]
        rows.append({"utilisation": u, "rm_misses": rm_miss, "edf_misses": edf_miss, "runs": runs})
    return {"rows": rows}


def overload_experiment(seed: int) -> dict:
    """Push utilisation above 1.0 and watch what each algorithm sacrifices."""
    tasks = [
        Task("T1", 10, 3), Task("T2", 15, 4), Task("T3", 20, 5), Task("T4", 30, 9),
    ]
    base = simulate(tasks, "edf", hyperperiod(tasks))
    heavy = [Task(t.name, t.period, min(t.period, t.wcet + (2 if t.name in ("T1", "T4") else 0)))
             for t in tasks]
    return {
        "base_utilisation": sum(t.utilisation for t in tasks),
        "heavy_utilisation": sum(t.utilisation for t in heavy),
        "rm": simulate(heavy, "rm", hyperperiod(heavy)),
        "edf": simulate(heavy, "edf", hyperperiod(heavy)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    sample = [Task("T1", 10, 2), Task("T2", 15, 3), Task("T3", 30, 7), Task("T4", 40, 9)]
    out = {
        "sample": {
            "tasks": [t.__dict__ for t in sample],
            "hyperperiod": hyperperiod(sample),
            "bounds": utilisation_bounds(sample),
            "rta": rta(sample),
            "rm": simulate(sample, "rm", hyperperiod(sample), trace=True),
            "edf": simulate(sample, "edf", hyperperiod(sample), trace=True),
            "fcfs": simulate(sample, "fcfs", hyperperiod(sample), trace=True),
        },
        "sweep": utilisation_sweep(args.seed),
        "overload": overload_experiment(args.seed),
    }
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
