"""Tests for the Assignment 3 hand-solution workbook and its checker.

Run:  python3 test_workbook.py
"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workbook import (Task, analyse, check_calcs, check_schedule, dbf, edf_feasible,
                      hyperperiod, load, max_demand_deficit, parse_workbook,
                      response_time, rm_bound, rta_table, utilisation)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))


def tset_a():
    return [Task("P1", 4, 1), Task("P2", 6, 2), Task("P3", 8, 3)]


class TestModel(unittest.TestCase):
    def test_task_validation(self):
        with self.assertRaises(ValueError):
            Task("X", 10, 0)
        with self.assertRaises(ValueError):
            Task("X", 10, 11)

    def test_default_deadline(self):
        self.assertEqual(Task("X", 20, 5).deadline, 20)

    def test_hyperperiod(self):
        self.assertEqual(hyperperiod(tset_a()), 24)
        self.assertEqual(hyperperiod([Task("A", 10, 1), Task("B", 15, 1)]), 30)

    def test_utilisation(self):
        self.assertAlmostEqual(utilisation(tset_a()), 0.9583333, places=6)


class TestTheory(unittest.TestCase):
    def test_rm_bound(self):
        self.assertAlmostEqual(rm_bound(1), 1.0)
        self.assertAlmostEqual(rm_bound(3), 3 * (2 ** (1 / 3) - 1), places=9)
        self.assertAlmostEqual(rm_bound(4), 0.756828, places=6)

    def test_response_times(self):
        tab = rta_table(tset_a())
        self.assertEqual(tab["P1"]["R"], 1)
        self.assertEqual(tab["P2"]["R"], 3)
        self.assertIsNone(tab["P3"]["R"])

    def test_response_time_infeasible(self):
        ts = [Task("A", 10, 6), Task("B", 12, 6)]
        self.assertIsNone(response_time(ts, ts[1]))

    def test_dbf(self):
        ts = tset_a()
        self.assertEqual(dbf(ts, 0), 0)
        self.assertEqual(dbf(ts, 1), 0)          # nothing is due yet at L = 1
        self.assertEqual(dbf(ts, 4), 1)           # P1's first deadline
        self.assertTrue(all(dbf(ts, L) <= L for L in range(1, 25)))

    def test_edf_feasible_above_rm_bound(self):
        """The whole point of the assignment: feasible for EDF, not for RM."""
        ts = tset_a()
        self.assertGreater(utilisation(ts), rm_bound(3))
        self.assertTrue(edf_feasible(ts))
        self.assertFalse(all(r["feasible"] for r in rta_table(ts).values()))

    def test_edf_infeasible(self):
        ts = [Task("A", 4, 2), Task("B", 4, 3)]
        self.assertFalse(edf_feasible(ts))

    def test_worst_deficit_positive_when_infeasible(self):
        ts = [Task("A", 4, 2), Task("B", 4, 3)]
        L, d = max_demand_deficit(ts)
        self.assertGreater(d, 0)


class TestMarkup(unittest.TestCase):
    def test_parse_minimal(self):
        text = """
        task P1 T=4 C=1
        task P2 T=6 C=2
        draw edf
        P1  #...
        P2  .##.
        end
        calc U 0.5
        """
        wb = parse_workbook(text)
        self.assertEqual(len(wb.tasks), 2)
        self.assertEqual(wb.schedules[0].algorithm, "edf")
        # the checked horizon is always at least one hyperperiod (LCM(4,6) = 12)
        self.assertEqual(wb.schedules[0].horizon, 12)
        self.assertEqual(wb.calcs["U"], "0.5")

    def test_comments_and_blank_lines(self):
        text = "; a comment\n\ntask P1 T=4 C=1\n; another\n"
        wb = parse_workbook(text)
        self.assertEqual(wb.tasks[0].name, "P1")

    def test_hash_is_a_run_marker_not_a_comment(self):
        text = "task P1 T=4 C=1\ndraw rm\nP1  #.#.\nend\n"
        wb = parse_workbook(text)
        self.assertEqual(wb.schedules[0].rows["P1"], "#.#.")

    def test_pipes_are_ignored(self):
        text = "task P1 T=4 C=1\ndraw rm\nP1  #.|#.\nend\n"
        wb = parse_workbook(text)
        self.assertEqual(wb.schedules[0].rows["P1"], "#.#.")

    def test_expect_miss_flag(self):
        text = "task P1 T=4 C=1\ndraw rm expect=miss\nP1  #...\nend\n"
        wb = parse_workbook(text)
        self.assertEqual(wb.schedules[0].expect, "miss")

    def test_empty_workbook_rejected(self):
        with self.assertRaises(ValueError):
            parse_workbook("title only\n")


class TestChecker(unittest.TestCase):
    def test_correct_schedule_passes(self):
        text = ("task P1 T=4 C=1\ndraw rm\nP1  #...#...#...#...#...#...\nend\n")
        wb = parse_workbook(text)
        self.assertEqual(check_schedule(wb, wb.schedules[0]), [])

    def test_collision_detected(self):
        text = ("task P1 T=4 C=1\ntask P2 T=4 C=1\n"
                "draw rm\nP1  #...\nP2  #...\nend\n")
        wb = parse_workbook(text)
        problems = check_schedule(wb, wb.schedules[0])
        self.assertTrue(any("processes run at once" in p for p in problems))

    def test_missed_deadline_detected(self):
        # P1 needs 2 ticks per job; the drawing only gives it 1 before the first deadline.
        text = ("task P1 T=4 C=2\n"
                "draw rm\nP1  #..........\nend\n")
        wb = parse_workbook(text)
        problems = check_schedule(wb, wb.schedules[0])
        self.assertTrue(any("job released at 0 got 1/2" in p for p in problems))

    def test_declared_miss_is_accepted(self):
        text = ("task P1 T=4 C=3\ndraw rm expect=miss\nP1  #..#......\nend\n")
        wb = parse_workbook(text)
        self.assertEqual(check_schedule(wb, wb.schedules[0]), [])

    def test_declared_miss_but_perfect_is_flagged(self):
        # A single job that finishes inside its own period: nothing can be missed.
        text = ("task P1 T=4 C=1\n"
                "draw rm expect=miss\nP1  #.\nend\n")
        wb = parse_workbook(text)
        hs = wb.schedules[0]
        hs.horizon = 4                      # only one job exists in this window
        problems = check_schedule(wb, hs)
        self.assertTrue(any("every job met its deadline" in p for p in problems))

    def test_impossible_service_detected(self):
        """A process cannot run more ticks than its jobs can consume."""
        text = ("task P1 T=4 C=1\ndraw rm expect=miss\nP1  #################\nend\n")
        wb = parse_workbook(text)
        problems = check_schedule(wb, wb.schedules[0])
        self.assertTrue(any("only" in p and "usable" in p for p in problems))

    def test_short_row_is_padded(self):
        text = ("task P1 T=4 C=1\ntask P2 T=4 C=1\n"
                "draw rm\nP1  #.........\nP2  .#........\nend\n")
        wb = parse_workbook(text)
        hs = wb.schedules[0]
        self.assertEqual(len(hs.rows["P1"]), len(hs.rows["P2"]))

    def test_unknown_symbol(self):
        text = "task P1 T=4 C=1\ndraw rm\nP1  #X..\nend\n"
        wb = parse_workbook(text)
        problems = check_schedule(wb, wb.schedules[0])
        self.assertTrue(any("unknown symbols" in p for p in problems))

    def test_missing_row(self):
        text = ("task P1 T=4 C=1\ntask P2 T=4 C=1\n"
                "draw rm\nP1  #...\nend\n")
        wb = parse_workbook(text)
        problems = check_schedule(wb, wb.schedules[0])
        self.assertTrue(any("missing rows" in p for p in problems))


class TestHandCalcs(unittest.TestCase):
    def test_wrong_utilisation_flagged(self):
        wb = parse_workbook("task P1 T=4 C=1\ncalc U 0.9\n")
        problems = check_calcs(wb)
        self.assertTrue(any("U: wrote" in p for p in problems))

    def test_correct_utilisation_accepted(self):
        wb = parse_workbook("task P1 T=4 C=1\ncalc U 0.25\n")
        self.assertEqual(check_calcs(wb), [])

    def test_wrong_response_time_flagged(self):
        wb = parse_workbook("task P1 T=4 C=1\ncalc R(P1) 9\n")
        problems = check_calcs(wb)
        self.assertTrue(any("R(P1)" in p for p in problems))

    def test_persian_decimal_separator(self):
        wb = parse_workbook("task P1 T=4 C=1\ncalc U ۰٫۲۵\n")
        self.assertEqual(check_calcs(wb), [])

    def test_unknown_calc_flagged(self):
        wb = parse_workbook("task P1 T=4 C=1\ncalc nonsense 1\n")
        problems = check_calcs(wb)
        self.assertTrue(any("unknown calculation" in p for p in problems))


class TestShippedAnswer(unittest.TestCase):
    """The answer shipped in data/paper_work.txt must verify cleanly."""

    def test_shipped_workbook_ok(self):
        wb = load(os.path.join(ROOT, "data", "paper_work.txt"))
        rep = analyse(wb)
        self.assertTrue(rep["ok"], msg=str(rep["calc_problems"]) +
                        str([s["problems"] for s in rep["schedules"]]))
        self.assertEqual(len(wb.tasks), 3)
        self.assertEqual(rep["hyperperiod"], 24)
        self.assertFalse(rep["rm_feasible"])
        self.assertTrue(rep["edf_feasible"])

    def test_shipped_schedules_are_complete(self):
        wb = load(os.path.join(ROOT, "data", "paper_work.txt"))
        for hs in wb.schedules:
            self.assertEqual(sorted(hs.rows), sorted(t.name for t in wb.tasks))
            self.assertEqual(hs.horizon, 24, msg=f"{hs.algorithm} horizon")

    def test_rm_answer_is_minimal(self):
        """RM must serve P3 only twice before its first deadline - that IS the finding."""
        wb = load(os.path.join(ROOT, "data", "paper_work.txt"))
        rm = next(s for s in wb.schedules if s.algorithm == "rm")
        self.assertEqual(rm.expect, "miss")
        self.assertEqual(rm.rows["P3"][:8].count("#"), 2)


class TestIndependentCrossCheck(unittest.TestCase):
    """The sheet must equal what a simulator with no shared code produces."""

    def test_matches_assignment2_simulator(self):
        sys.path.insert(0, os.path.join(ROOT, "..", "02-edf-vs-rm", "code"))
        import rt_sim

        wb = load(os.path.join(ROOT, "data", "paper_work.txt"))
        H = hyperperiod(wb.tasks)
        tasks = [rt_sim.Task(t.name, t.period, t.wcet, t.deadline) for t in wb.tasks]
        for alg in ("rm", "edf"):
            timeline = rt_sim.simulate(tasks, alg, H, trace=True)["timeline"]
            hand = next(s.rows for s in wb.schedules if s.algorithm == alg)
            for t in wb.tasks:
                sim = "".join("#" if n == t.name else "." for n in timeline)
                self.assertEqual(sim, hand[t.name], msg=f"{alg}/{t.name}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
