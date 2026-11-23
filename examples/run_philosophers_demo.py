"""Run the safe-admission dining-philosophers teaching model."""

from lottery_lab import DiningPhilosophers


def main() -> None:
    simulation = DiningPhilosophers(
        philosophers=5,
        tickets=[1, 2, 3, 4, 5],
        seed=20261123,
        max_wait_rounds=3,
    )
    trace = simulation.run(12)
    print("Dining Philosophers — lottery among safe candidates + age override")
    print("Each round grants both forks atomically; meals finish by the end of the round.")
    for event in trace:
        eaters = ", ".join(f"P{i}" for i in event.eaters)
        forced = "" if event.forced_priority is None else f"; forced P{event.forced_priority}"
        print(f"Round {event.round_number:02d}: eaters [{eaters}]{forced}; waits={event.wait_ages}")
    print("Completed meals:", simulation.meal_counts)
    print("Interpretation: safety follows from atomic admission; lottery alone has no finite wait bound.")


if __name__ == "__main__":
    main()
