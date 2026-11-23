import unittest

from lottery_lab import DiningPhilosophers


class DiningPhilosophersTests(unittest.TestCase):
    def test_validates_model_parameters(self):
        with self.assertRaises(ValueError):
            DiningPhilosophers(philosophers=2)
        with self.assertRaises(ValueError):
            DiningPhilosophers(philosophers=4, tickets=[1, 2])
        with self.assertRaises(ValueError):
            DiningPhilosophers(philosophers=3, tickets=[1, 0, 1])
        with self.assertRaises(ValueError):
            DiningPhilosophers(philosophers=3, max_wait_rounds=0)

    def test_no_two_adjacent_philosophers_eat_in_one_round(self):
        count = 7
        simulation = DiningPhilosophers(
            philosophers=count,
            tickets=[1, 2, 3, 4, 5, 6, 7],
            seed=9,
        )
        for event in simulation.run(100):
            for position, first in enumerate(event.eaters):
                for second in event.eaters[position + 1 :]:
                    distance = (first - second) % count
                    self.assertNotIn(distance, (1, count - 1))

    def test_each_round_is_a_maximal_safe_set(self):
        simulation = DiningPhilosophers(philosophers=5, seed=3)
        for event in simulation.run(10):
            eaters = set(event.eaters)
            for philosopher in range(5):
                if philosopher in eaters:
                    continue
                left = (philosopher - 1) % 5
                right = (philosopher + 1) % 5
                self.assertTrue(left in eaters or right in eaters)

    def test_age_override_serves_every_philosopher_and_bounds_wait_in_model(self):
        count = 5
        threshold = 2
        simulation = DiningPhilosophers(
            philosophers=count,
            tickets=[1, 2, 3, 4, 5],
            seed=4,
            max_wait_rounds=threshold,
        )
        trace = simulation.run(80)
        self.assertTrue(all(meals > 0 for meals in simulation.meal_counts))
        self.assertLessEqual(max(simulation.wait_ages), threshold + count - 1)
        self.assertTrue(any(event.forced_priority is not None for event in trace))

    def test_seed_makes_simulation_reproducible(self):
        kwargs = dict(philosophers=5, tickets=[1, 2, 3, 4, 5], seed=17, max_wait_rounds=3)
        first = DiningPhilosophers(**kwargs).run(25)
        second = DiningPhilosophers(**kwargs).run(25)
        self.assertEqual(first, second)

    def test_round_count_validation_and_state_continuation(self):
        simulation = DiningPhilosophers(philosophers=3, seed=1)
        self.assertEqual(simulation.run(0), ())
        with self.assertRaises(ValueError):
            simulation.run(-1)
        with self.assertRaises(TypeError):
            simulation.run(2.5)
        first = simulation.run(2)
        second = simulation.run(1)
        self.assertEqual(first[-1].round_number, 2)
        self.assertEqual(second[0].round_number, 3)


if __name__ == "__main__":
    unittest.main()
