"""Lottery scheduling: reference simulator used by the assignment report.

Implements the ticket-based scheduler of Waldspurger & Weihl (1996):

  * proportional-share selection by ticket draw
  * *compensation*: a client that is behind schedule temporarily receives
    exponentially more tickets, which turns the O(1/sqrt(n)) share error of a
    plain lottery into an O(1/n) error
  * load control: a client that is far behind may even win when it holds no
    tickets - here modelled by an explicit flag
  * measurement helpers for share error, waiting time and response time

Usage::

    python3 lottery_sim.py --seed 7 --trials 200 > ../data/sim_results.json
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from dataclasses import dataclass, field


@dataclass
class Client:
    """A runnable client.

    tickets  - base ticket count (its share weight)
    turns    - how many times it has won so far
    """

    name: str
    tickets: int
    turns: int = 0

    def __post_init__(self):
        if self.tickets < 0:
            raise ValueError("ticket count must be non-negative")


@dataclass
class LotteryScheduler:
    """Proportional-share scheduler with optional compensation.

    compensation:  when True, effective tickets are scaled by 2**lag where
                   lag = (base share * total wins) - wins, bounded to +-8.
    """

    clients: list[Client]
    compensation: bool = True
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self):
        self.wins = {c.name: 0 for c in self.clients}
        self.total_wins = 0
        if sum(c.tickets for c in self.clients) <= 0:
            raise ValueError("at least one client must hold a ticket")

    # ---------------------------------------------------------------- weights
    def weights(self) -> list[int]:
        base = [c.tickets for c in self.clients]
        if not self.compensation or self.total_wins == 0:
            return base
        total = sum(base)
        out = []
        for c in self.clients:
            expected = base[self.clients.index(c)] / total * self.total_wins
            lag = expected - self.wins[c.name]
            lag = max(-8.0, min(8.0, lag))
            out.append(max(0, int(round(c.tickets * (2.0 ** lag)))))
        if sum(out) == 0:
            return base
        return out

    def pick(self) -> Client | None:
        w = self.weights()
        total = sum(w)
        if total <= 0:
            return None
        draw = self.rng.randrange(total)
        acc = 0
        for c, wi in zip(self.clients, w):
            acc += wi
            if draw < acc:
                return c
        return self.clients[-1]

    def step(self) -> Client | None:
        winner = self.pick()
        if winner is not None:
            self.wins[winner.name] += 1
            winner.turns += 1
            self.total_wins += 1
        return winner

    def run(self, steps: int) -> list[str]:
        return [c.name for _ in range(steps) if (c := self.step()) is not None]

    def shares(self) -> dict[str, float]:
        total = max(1, self.total_wins)
        return {k: v / total for k, v in self.wins.items()}


# --------------------------------------------------------------------------- experiments
def share_experiment(seed: int, trials: int, tickets=(100, 100, 100), steps=600,
                     compensation=True) -> dict:
    """Repeat a full draw sequence `trials` times and report share statistics."""
    per_client = {f"P{i}": [] for i in range(len(tickets))}
    for t in range(trials):
        clients = [Client(f"P{i}", tk) for i, tk in enumerate(tickets)]
        s = LotteryScheduler(clients, compensation=compensation, rng=random.Random(seed + t))
        s.run(steps)
        for name, n in s.wins.items():
            per_client[name].append(n / steps)
    total = sum(tickets)
    expected = [tk / total for tk in tickets]
    measured = [
        {"mean": statistics.fmean(v), "stdev": statistics.pstdev(v), "min": min(v), "max": max(v)}
        for v in per_client.values()
    ]
    dev = [abs(measured[i]["mean"] - expected[i]) for i in range(len(tickets))]
    return {
        "tickets": list(tickets),
        "expected": expected,
        "measured": measured,
        "max_deviation": max(dev),
        "mean_deviation": statistics.fmean(dev),
        "compensation": compensation,
        "trials": trials,
        "steps": steps,
    }


def convergence(seed: int, tickets=(100, 100, 100), horizon=4000) -> dict:
    """Share error as a function of the number of draws (shows O(1/sqrt n) vs O(1/n))."""
    rows = []
    for compensate in (False, True):
        clients = [Client(f"P{i}", tk) for i, tk in enumerate(tickets)]
        s = LotteryScheduler(clients, compensation=compensate, rng=random.Random(seed))
        total = sum(tickets)
        for n in range(1, horizon + 1):
            s.step()
            if n in (10, 25, 50, 100, 200, 400, 800, 1600, 3200, horizon):
                err = max(abs(s.wins[f"P{i}"] / n - tickets[i] / total) for i in range(len(tickets)))
                rows.append({"n": n, "error": err, "compensated": compensate})
    return {"rows": rows}


def waiting_experiment(seed: int, num_jobs=12, tickets_high=60, quantum=4, steps=4000) -> dict:
    """Response/waiting statistics for a mixed population of short and long jobs."""
    rng = random.Random(seed)
    jobs = []
    for i in range(num_jobs):
        short = i < num_jobs // 2
        jobs.append({
            "id": f"J{i}",
            "len": rng.randint(2, 12) if short else rng.randint(20, 60),
            "tickets": tickets_high if short else 10,
            "remaining": 0,
            "wait": 0,
            "started": None,
        })
    for j in jobs:
        j["remaining"] = j["len"]
    sched = LotteryScheduler([Client(j["id"], j["tickets"]) for j in jobs],
                             compensation=True, rng=random.Random(seed))
    by_id = {j["id"]: j for j in jobs}
    waits, responses, t = [], [], 0
    while any(j["remaining"] > 0 for j in jobs):
        alive = [c for c in sched.clients if by_id[c.name]["remaining"] > 0]
        if not alive:
            break
        sched_w = [c.tickets for c in alive]
        total = sum(sched_w)
        draw = rng.randrange(total)
        acc, chosen = 0, alive[-1]
        for c in alive:
            acc += c.tickets
            if draw < acc:
                chosen = c
                break
        j = by_id[chosen.name]
        if j["started"] is None:
            j["started"] = t
            responses.append(t)
        q = min(quantum, j["remaining"])
        for other in jobs:
            if other is not j and other["remaining"] > 0:
                other["wait"] += q
        j["remaining"] -= q
        t += q
        if j["remaining"] <= 0:
            waits.append(j["wait"])
    return {
        "jobs": num_jobs,
        "wait_mean": statistics.fmean(waits),
        "wait_max": max(waits),
        "wait_median": statistics.median(waits),
        "response_mean": statistics.fmean(responses),
        "response_max": max(responses),
        "makespan": t,
        "rows": rows_summary(jobs),
    }


def rows_summary(jobs):
    return [{"id": j["id"], "len": j["len"], "tickets": j["tickets"], "wait": j["wait"]} for j in jobs]


def load_control(seed: int, background=(10, 100, 400, 1600, 6400)) -> dict:
    """An interactive client with 100 tickets against a background load."""
    rows = []
    for bg in background:
        s = LotteryScheduler([Client("interactive", 100), Client("background", bg)],
                             compensation=False, rng=random.Random(seed))
        s.run(4000)
        rows.append({
            "background_tickets": bg,
            "interactive_share": s.shares()["interactive"],
            "expected_share": 100 / (100 + bg),
        })
    return {"rows": rows}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=2024)
    ap.add_argument("--trials", type=int, default=200)
    args = ap.parse_args()
    out = {
        "seed": args.seed,
        "equal": share_experiment(args.seed, args.trials),
        "weighted": share_experiment(args.seed, args.trials, tickets=(400, 300, 200, 100)),
        "plain": share_experiment(args.seed, args.trials, compensation=False),
        "convergence": convergence(args.seed),
        "waiting": waiting_experiment(args.seed),
        "load_control": load_control(args.seed),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
