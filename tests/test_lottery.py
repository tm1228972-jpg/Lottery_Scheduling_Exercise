from collections import Counter
import unittest

from lottery_lab import LotteryScheduler, Process


class ProcessTests(unittest.TestCase):
    def test_rejects_invalid_process(self):
        for tickets in (0, -1):
            with self.subTest(tickets=tickets), self.assertRaises(ValueError):
                Process("P", tickets)
        with self.assertRaises(TypeError):
            Process("P", True)
        with self.assertRaises(ValueError):
            Process("  ", 1)


class LotterySchedulerTests(unittest.TestCase):
    def test_rejects_empty_or_duplicate_process_sets(self):
        with self.assertRaises(ValueError):
            LotteryScheduler([])
        with self.assertRaises(ValueError):
            LotteryScheduler([Process("P", 1), Process("P", 2)])

    def test_draw_is_inside_ticket_pool_and_matches_owner_interval(self):
        processes = [Process("A", 2), Process("B", 3)]
        scheduler = LotteryScheduler(processes, seed=11)
        for draw in scheduler.run(100):
            self.assertGreaterEqual(draw.winning_ticket, 1)
            self.assertLessEqual(draw.winning_ticket, draw.total_tickets)
            if draw.winning_ticket <= 2:
                self.assertEqual(draw.process.name, "A")
            else:
                self.assertEqual(draw.process.name, "B")

    def test_seed_makes_trace_reproducible(self):
        processes = [Process("A", 1), Process("B", 3), Process("C", 5)]
        first = LotteryScheduler(processes, seed=123).run(50)
        second = LotteryScheduler(processes, seed=123).run(50)
        self.assertEqual(first, second)

    def test_expected_shares_are_ticket_ratios(self):
        scheduler = LotteryScheduler([Process("A", 1), Process("B", 3)], seed=5)
        self.assertEqual(scheduler.expected_share("A"), 0.25)
        self.assertEqual(scheduler.expected_share("B"), 0.75)
        with self.assertRaises(KeyError):
            scheduler.expected_share("missing")

    def test_observed_share_is_close_in_a_seeded_sample(self):
        scheduler = LotteryScheduler([Process("A", 1), Process("B", 3)], seed=20261123)
        counts = Counter(draw.process.name for draw in scheduler.run(20_000))
        self.assertLess(abs(counts["A"] / 20_000 - 0.25), 0.02)

    def test_run_validates_draw_count(self):
        scheduler = LotteryScheduler([Process("A", 1)], seed=1)
        self.assertEqual(scheduler.run(0), ())
        with self.assertRaises(ValueError):
            scheduler.run(-1)
        with self.assertRaises(TypeError):
            scheduler.run(1.5)


if __name__ == "__main__":
    unittest.main()
