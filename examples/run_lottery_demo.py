"""Run a small seeded weighted-lottery example from the repository root."""

from collections import Counter

from lottery_lab import LotteryScheduler, Process


def main() -> None:
    processes = [Process("interactive", 6), Process("batch", 3), Process("background", 1)]
    scheduler = LotteryScheduler(processes, seed=20261123)
    trace = scheduler.run(20)
    counts = Counter(draw.process.name for draw in trace)

    print("Lottery Scheduling — seeded 20-draw teaching example")
    print("Tickets: " + ", ".join(f"{p.name}={p.tickets}" for p in processes))
    for index, draw in enumerate(trace, start=1):
        print(f"{index:02d}. ticket {draw.winning_ticket:02d}/{draw.total_tickets:02d} -> {draw.process.name}")
    print("Observed counts:")
    for process in processes:
        print(
            f"  {process.name:12s} {counts[process.name]:2d}/20 "
            f"(theoretical share {scheduler.expected_share(process.name):.0%})"
        )
    print("Note: this short trace illustrates selection; it is not a statistical guarantee or benchmark.")


if __name__ == "__main__":
    main()
