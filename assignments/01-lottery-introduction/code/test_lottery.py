"""Behavioural tests for lottery_sim.py.

Run:  python3 -m pytest test_lottery.py -q      (or: python3 test_lottery.py)
"""
from __future__ import annotations

import random
import statistics
import unittest

from lottery_sim import (
    Client,
    LotteryScheduler,
    convergence,
    load_control,
    share_experiment,
    waiting_experiment,
)


class TestSelection(unittest.TestCase):
    def test_probability_matches_tickets(self):
        clients = [Client("A", 300), Client("B", 100)]
        s = LotteryScheduler(clients, compensation=False, rng=random.Random(11))
        s.run(40_000)
        share_a = s.wins["A"] / s.total_wins
        self.assertAlmostEqual(share_a, 0.75, delta=0.01)

    def test_zero_ticket_client_never_wins_alone(self):
        s = LotteryScheduler([Client("A", 10), Client("B", 0)],
                             compensation=False, rng=random.Random(3))
        s.run(5_000)
        self.assertEqual(s.wins["B"], 0)

    def test_all_zero_tickets_rejected(self):
        with self.assertRaises(ValueError):
            LotteryScheduler([Client("A", 0)], compensation=False)

    def test_negative_tickets_rejected(self):
        with self.assertRaises(ValueError):
            Client("A", -1)

    def test_deterministic_for_same_seed(self):
        def run_once():
            s = LotteryScheduler([Client("A", 1), Client("B", 1), Client("C", 2)],
                                 rng=random.Random(99))
            return s.run(500)

        self.assertEqual(run_once(), run_once())

    def test_total_wins_equals_steps(self):
        s = LotteryScheduler([Client("A", 5), Client("B", 7)], rng=random.Random(5))
        history = s.run(1000)
        self.assertEqual(len(history), 1000)
        self.assertEqual(sum(s.wins.values()), 1000)


class TestCompensation(unittest.TestCase):
    def test_compensation_reduces_share_error(self):
        plain = share_experiment(seed=2, trials=40, steps=400, compensation=False)
        comp = share_experiment(seed=2, trials=40, steps=400, compensation=True)
        self.assertLess(comp["mean_deviation"], plain["mean_deviation"])

    def test_weights_stay_non_negative(self):
        s = LotteryScheduler([Client("A", 100), Client("B", 100)], compensation=True,
                             rng=random.Random(1))
        for _ in range(2000):
            s.step()
            self.assertTrue(all(w >= 0 for w in s.weights()))


class TestStatistics(unittest.TestCase):
    def test_waiting_experiment_shapes(self):
        res = waiting_experiment(seed=4)
        self.assertEqual(len(res["rows"]), res["jobs"])
        self.assertLessEqual(res["wait_median"], res["wait_mean"])
        self.assertGreaterEqual(res["wait_max"], res["wait_median"])
        self.assertGreater(res["makespan"], 0)

    def test_convergence_monotone_trend(self):
        rows = convergence(seed=8)["rows"]
        plain = {r["n"]: r["error"] for r in rows if not r["compensated"]}
        comp = {r["n"]: r["error"] for r in rows if r["compensated"]}
        self.assertLessEqual(max(comp.values()), max(plain.values()) * 1.2)

    def test_load_control_decreases(self):
        rows = load_control(seed=3)["rows"]
        shares = [r["interactive_share"] for r in rows]
        self.assertEqual(shares, sorted(shares, reverse=True))

    def test_expected_share_math(self):
        res = share_experiment(seed=1, trials=5, tickets=(1, 2, 5))
        self.assertAlmostEqual(sum(res["expected"]), 1.0, places=9)
        self.assertAlmostEqual(res["expected"][2], 0.625, places=9)


if __name__ == "__main__":
    unittest.main(verbosity=2)
