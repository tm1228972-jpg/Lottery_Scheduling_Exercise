"""Small, dependency-free teaching models for lottery scheduling.

This package is an educational simulator. It does not interact with an operating
system kernel or implement preemption, context switching, or real-time guarantees.
"""

from .lottery import Draw, LotteryScheduler, Process
from .philosophers import DiningPhilosophers, PhilosopherRound

__all__ = [
    "DiningPhilosophers",
    "Draw",
    "LotteryScheduler",
    "PhilosopherRound",
    "Process",
]
