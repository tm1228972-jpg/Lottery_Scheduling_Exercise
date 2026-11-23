"""Small, dependency-free teaching models for lottery scheduling.

This package is an educational simulator. It does not interact with an operating
system kernel or implement preemption, context switching, or real-time guarantees.
"""

from .lottery import Draw, LotteryScheduler, Process
from .philosophers import DiningPhilosophers, PhilosopherRound
from .readers_writers import FairReadersWritersMonitor
from .realtime import (
    DeadlineMiss,
    PeriodicTask,
    ScheduleResult,
    ScheduleSegment,
    hyperperiod,
    rm_utilization_bound,
    simulate_schedule,
    utilization,
)

__all__ = [
    "DeadlineMiss",
    "DiningPhilosophers",
    "Draw",
    "FairReadersWritersMonitor",
    "LotteryScheduler",
    "PeriodicTask",
    "PhilosopherRound",
    "Process",
    "ScheduleResult",
    "ScheduleSegment",
    "hyperperiod",
    "rm_utilization_bound",
    "simulate_schedule",
    "utilization",
]
