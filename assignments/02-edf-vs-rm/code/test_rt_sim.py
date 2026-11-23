"""Verification tests for the real-time simulator (Assignment 2).

Run:  python3 test_rt_sim.py
"""
from __future__ import annotations

import math
import unittest

from rt_sim import (Task, hyperperiod, lcm, random_taskset, rta, simulate,
                    utilisation_bounds)


class TestModel(unittest.TestCase):
    def test_invalid_wcet(self):
        with self.assertRaises(ValueError):
            Task("T1", 10, 0)
        with self.assertRaises(ValueError):
            Task("T1", 10, 11)

    def test_default_deadline_equals_period(self):
        t = Task("T1", 20, 5)
        self.assertEqual(t.deadline, 20)

    def test_hyperperiod(self):
        ts = [Task("A", 10, 2), Task("B", 15, 3), Task("C", 30, 4)]
        self.assertEqual(hyperperiod(ts), 30)
        self.assertEqual(lcm(0, 5), 0)

    def test_utilisation(self):
        ts = [Task("A", 10, 2), Task("B", 20, 5)]
        self.assertAlmostEqual(sum(t.utilisation for t in ts), 0.45)


class TestTheory(unittest.TestCase):
    def test_rm_bound_formula(self):
        ts = [Task(f"T{i+1}", 10 * (i + 1), 1) for i in range(4)]
        b = utilisation_bounds(ts)
        self.assertAlmostEqual(b["rm_bound"], 4 * (2 ** 0.25 - 1), places=6)

    def test_rm_bound_limit_is_ln2(self):
        n = 10 ** 7
        self.assertAlmostEqual(n * (2 ** (1 / n) - 1), math.log(2), places=6)

    def test_rta_feasible_set(self):
        ts = [Task("T1", 10, 2), Task("T2", 15, 3), Task("T3", 30, 7)]
        self.assertTrue(rta(ts)["feasible"])

    def test_rta_infeasible_set(self):
        ts = [Task("T1", 10, 6), Task("T2", 12, 6)]
        self.assertFalse(rta(ts)["feasible"])


class TestSimulatorAgreesWithRTA(unittest.TestCase):
    def test_rm_matches_rta_on_random_sets(self):
        """Whenever RTA says schedulable, RM simulation must miss no deadline."""
        mismatches = 0
        for seed in range(12):
            ts = random_taskset(seed, 4, 0.75)
            if not ts:
                continue
            if rta(ts)["feasible"]:
                h = min(hyperperiod(ts), 1500)
                if simulate(ts, "rm", h)["total_misses"] != 0:
                    mismatches += 1
        self.assertEqual(mismatches, 0)

    def test_edf_no_miss_below_utilisation_one(self):
        ts = [Task("T1", 10, 3), Task("T2", 15, 4), Task("T3", 30, 8)]
        self.assertLessEqual(sum(t.utilisation for t in ts), 1.0)
        self.assertEqual(simulate(ts, "edf", hyperperiod(ts))["total_misses"], 0)

    def test_rm_can_miss_above_bound(self):
        # utilisation 1.05 exceeds what any algorithm can schedule, so a miss is certain;
        # note that 0.95 with two tasks is still feasible despite being above the bound.
        ts = [Task("T1", 10, 6), Task("T2", 20, 9)]
        self.assertGreater(simulate(ts, "rm", hyperperiod(ts))["total_misses"], 0)
        self.assertFalse(rta(ts)["feasible"])

    def test_above_bound_can_still_be_feasible(self):
        # 0.95 > 0.828 (n=2 bound) yet response-time analysis proves it schedulable
        ts = [Task("T1", 10, 5), Task("T2", 20, 9)]
        self.assertGreater(utilisation_bounds(ts)["utilisation"], utilisation_bounds(ts)["rm_bound"])
        self.assertTrue(rta(ts)["feasible"])
        self.assertEqual(simulate(ts, "rm", hyperperiod(ts))["total_misses"], 0)

    def test_determinism(self):
        ts = [Task("T1", 10, 2), Task("T2", 15, 3)]
        a = simulate(ts, "edf", 60, trace=True)["timeline"]
        b = simulate(ts, "edf", 60, trace=True)["timeline"]
        self.assertEqual(a, b)

    def test_timeline_length(self):
        ts = [Task("T1", 10, 2), Task("T2", 15, 3)]
        self.assertEqual(len(simulate(ts, "edf", 90, trace=True)["timeline"]), 90)


if __name__ == "__main__":
    unittest.main(verbosity=2)
