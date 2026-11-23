import unittest

from lottery_lab import (
    PeriodicTask,
    hyperperiod,
    rm_utilization_bound,
    simulate_schedule,
    utilization,
)


class RealtimeSchedulerTests(unittest.TestCase):
    def setUp(self):
        self.tasks = [
            PeriodicTask("P1", execution=1, period=4),
            PeriodicTask("P2", execution=1, period=5),
            PeriodicTask("P3", execution=2, period=10),
        ]

    def test_supplied_three_task_set_parameters(self):
        self.assertEqual(hyperperiod(self.tasks), 20)
        self.assertAlmostEqual(utilization(self.tasks), 0.65)
        self.assertAlmostEqual(rm_utilization_bound(3), 0.7797631496846196)

    def test_edf_and_rm_cover_the_hyperperiod_without_misses(self):
        expected = [
            (0, 1, "P1"),
            (1, 2, "P2"),
            (2, 4, "P3"),
            (4, 5, "P1"),
            (5, 6, "P2"),
            (6, 8, None),
            (8, 9, "P1"),
            (9, 10, None),
            (10, 11, "P2"),
            (11, 12, "P3"),
            (12, 13, "P1"),
            (13, 14, "P3"),
            (14, 15, None),
            (15, 16, "P2"),
            (16, 17, "P1"),
            (17, 20, None),
        ]
        for policy in ("EDF", "RM"):
            with self.subTest(policy=policy):
                result = simulate_schedule(self.tasks, policy)
                self.assertEqual(result.horizon, 20)
                self.assertEqual(result.misses, ())
                actual = [(s.start, s.end, s.task_name) for s in result.segments]
                self.assertEqual(actual, expected)
                self.assertEqual(sum(s.end - s.start for s in result.segments), 20)

    def test_overloaded_example_records_missed_job(self):
        overloaded = [PeriodicTask("A", 2, 2), PeriodicTask("B", 1, 2)]
        result = simulate_schedule(overloaded, "RM", horizon=2)
        self.assertFalse(result.schedulable_in_horizon)
        self.assertEqual(result.misses[0].task_name, "B")
        self.assertEqual(result.misses[0].absolute_deadline, 2)

    def test_validation(self):
        with self.assertRaises(ValueError):
            PeriodicTask("bad", execution=0, period=2)
        with self.assertRaises(ValueError):
            simulate_schedule([], "EDF")
        with self.assertRaises(ValueError):
            simulate_schedule(self.tasks, "lottery")
        with self.assertRaises(ValueError):
            simulate_schedule(self.tasks, "EDF", horizon=0)
        with self.assertRaises(ValueError):
            rm_utilization_bound(0)
        with self.assertRaises(ValueError):
            hyperperiod([PeriodicTask("x", 1, 2), PeriodicTask("x", 1, 3)])


if __name__ == "__main__":
    unittest.main()
