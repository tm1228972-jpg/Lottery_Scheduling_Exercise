"""Dining-philosophers model combining lottery selection and safe admission.

This is a synchronous, discrete-round simulation. At the beginning of each
round every philosopher is hungry. A central arbiter atomically assigns both
forks to an independent set of philosophers; meals finish at the end of that
round. This explicit model is intentionally smaller than a real concurrent
program, but it makes the safety and fairness assumptions inspectable.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Sequence


@dataclass(frozen=True, slots=True)
class PhilosopherRound:
    """Observable result for one simulated meal round."""

    round_number: int
    eaters: tuple[int, ...]
    waiting: tuple[int, ...]
    forced_priority: int | None
    wait_ages: tuple[int, ...]


class DiningPhilosophers:
    """Schedule philosopher meals with atomic fork admission.

    Lottery mode picks among currently eligible philosophers using positive
    ticket weights. If ``max_wait_rounds`` is set, an age-based override grants
    the oldest waiting philosopher first once the threshold is reached. The
    override is a deterministic fairness mechanism layered on top of lottery
    selection; it is not a property of lottery scheduling by itself.

    Deadlock is excluded by the model because no philosopher can hold just one
    fork while waiting: the arbiter grants both adjacent forks atomically, and
    every meal finishes within its round. The fairness bound also depends on
    these finite-round and finite-philosopher assumptions.
    """

    def __init__(
        self,
        philosophers: int = 5,
        tickets: Sequence[int] | None = None,
        seed: int | None = None,
        max_wait_rounds: int | None = None,
    ) -> None:
        if isinstance(philosophers, bool) or not isinstance(philosophers, int):
            raise TypeError("philosophers must be an integer")
        if philosophers < 3:
            raise ValueError("the circular dining-philosophers model needs at least 3 philosophers")

        if tickets is None:
            ticket_values = (1,) * philosophers
        else:
            ticket_values = tuple(tickets)
            if len(ticket_values) != philosophers:
                raise ValueError("tickets must contain one value per philosopher")
            for value in ticket_values:
                if isinstance(value, bool) or not isinstance(value, int):
                    raise TypeError("each ticket count must be an integer")
                if value <= 0:
                    raise ValueError("each ticket count must be positive")

        if max_wait_rounds is not None:
            if isinstance(max_wait_rounds, bool) or not isinstance(max_wait_rounds, int):
                raise TypeError("max_wait_rounds must be an integer or None")
            if max_wait_rounds < 1:
                raise ValueError("max_wait_rounds must be at least 1")

        self._count = philosophers
        self._tickets = ticket_values
        self._rng = random.Random(seed)
        self._max_wait_rounds = max_wait_rounds
        self._wait_ages = [0] * philosophers
        self._meal_counts = [0] * philosophers
        self._round_number = 0

    @property
    def meal_counts(self) -> tuple[int, ...]:
        """Number of completed meals for each philosopher so far."""

        return tuple(self._meal_counts)

    @property
    def wait_ages(self) -> tuple[int, ...]:
        """Consecutive rounds not served, in philosopher order."""

        return tuple(self._wait_ages)

    def run(self, rounds: int) -> tuple[PhilosopherRound, ...]:
        """Simulate a number of rounds and return an immutable event trace."""

        if isinstance(rounds, bool) or not isinstance(rounds, int):
            raise TypeError("rounds must be an integer")
        if rounds < 0:
            raise ValueError("rounds cannot be negative")

        trace: list[PhilosopherRound] = []
        for _ in range(rounds):
            self._round_number += 1
            eaters: list[int] = []
            forced_priority: int | None = None

            # Aged requests are considered before lottery winners. Because the
            # round begins with all forks free, this oldest request can be
            # granted atomically; lottery then fills any non-conflicting seats.
            if self._max_wait_rounds is not None:
                aged = [
                    i for i, age in enumerate(self._wait_ages)
                    if age >= self._max_wait_rounds
                ]
                if aged:
                    forced_priority = max(aged, key=lambda i: (self._wait_ages[i], -i))
                    eaters.append(forced_priority)

            while True:
                eligible = [
                    i for i in range(self._count)
                    if i not in eaters
                    and all(not self._adjacent(i, other) for other in eaters)
                ]
                if not eligible:
                    break
                eaters.append(self._weighted_choice(eligible))

            eater_set = set(eaters)
            waiting = tuple(i for i in range(self._count) if i not in eater_set)
            for i in range(self._count):
                if i in eater_set:
                    self._meal_counts[i] += 1
                    self._wait_ages[i] = 0
                else:
                    self._wait_ages[i] += 1

            # Safety assertion for this teaching model: adjacent philosophers
            # share a fork and may never be admitted in the same round.
            if any(self._adjacent(a, b) for pos, a in enumerate(eaters) for b in eaters[pos + 1 :]):
                raise RuntimeError("arbiter admitted adjacent philosophers")

            trace.append(
                PhilosopherRound(
                    round_number=self._round_number,
                    eaters=tuple(sorted(eaters)),
                    waiting=waiting,
                    forced_priority=forced_priority,
                    wait_ages=tuple(self._wait_ages),
                )
            )
        return tuple(trace)

    def _adjacent(self, left: int, right: int) -> bool:
        distance = (left - right) % self._count
        return distance in (1, self._count - 1)

    def _weighted_choice(self, candidates: Sequence[int]) -> int:
        total = sum(self._tickets[i] for i in candidates)
        ticket = self._rng.randint(1, total)
        cumulative = 0
        for philosopher in candidates:
            cumulative += self._tickets[philosopher]
            if ticket <= cumulative:
                return philosopher
        raise RuntimeError("eligible philosophers did not contain the winning ticket")
