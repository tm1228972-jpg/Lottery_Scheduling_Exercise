"""Weighted lottery scheduling as a reproducible, single-machine model."""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Process:
    """A runnable process with a positive number of lottery tickets."""

    name: str
    tickets: int

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("process name must be a non-empty string")
        if isinstance(self.tickets, bool) or not isinstance(self.tickets, int):
            raise TypeError("tickets must be an integer")
        if self.tickets <= 0:
            raise ValueError("tickets must be positive")


@dataclass(frozen=True, slots=True)
class Draw:
    """The result of one draw; ticket numbers are one-based and inclusive."""

    winning_ticket: int
    total_tickets: int
    process: Process


class LotteryScheduler:
    """Choose one process in proportion to its ticket count.

    A process with ``t`` tickets in a pool of ``T`` tickets has probability
    ``t / T`` of winning any one independent draw. The class models dispatch
    choices only: a real scheduler would also need to define time slices,
    blocking, wakeups, ticket changes, and machine-level concurrency.
    """

    def __init__(self, processes: Iterable[Process], seed: int | None = None) -> None:
        self._processes = tuple(processes)
        if not self._processes:
            raise ValueError("at least one process is required")
        if any(not isinstance(process, Process) for process in self._processes):
            raise TypeError("processes must contain Process objects")
        names = [process.name for process in self._processes]
        if len(set(names)) != len(names):
            raise ValueError("process names must be unique")
        self._total_tickets = sum(process.tickets for process in self._processes)
        self._rng = random.Random(seed)

    @property
    def processes(self) -> tuple[Process, ...]:
        """The immutable process set in input order."""

        return self._processes

    @property
    def total_tickets(self) -> int:
        """The total number of tickets in the pool."""

        return self._total_tickets

    def draw(self) -> Draw:
        """Draw one ticket and return its owner."""

        winning_ticket = self._rng.randint(1, self._total_tickets)
        cumulative = 0
        for process in self._processes:
            cumulative += process.tickets
            if winning_ticket <= cumulative:
                return Draw(winning_ticket, self._total_tickets, process)
        # The cumulative intervals partition [1, total_tickets]; reaching this
        # line would mean the implementation or its invariants were changed.
        raise RuntimeError("ticket pool did not contain the winning ticket")

    def run(self, draws: int) -> tuple[Draw, ...]:
        """Run ``draws`` dispatch choices and return their full trace."""

        if isinstance(draws, bool) or not isinstance(draws, int):
            raise TypeError("draws must be an integer")
        if draws < 0:
            raise ValueError("draws cannot be negative")
        return tuple(self.draw() for _ in range(draws))

    def expected_share(self, process_name: str) -> float:
        """Return a process's theoretical share of independent draws."""

        for process in self._processes:
            if process.name == process_name:
                return process.tickets / self._total_tickets
        raise KeyError(process_name)
