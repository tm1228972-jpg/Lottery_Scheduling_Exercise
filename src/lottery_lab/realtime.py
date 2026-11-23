"""Discrete-time EDF and Rate-Monotonic reference schedulers.

The simulator is intended for small integer-valued task sets and instructional
traces. It is preemptive at integer time boundaries, runs on one processor,
assumes zero scheduling/context-switch cost, and uses a stable deterministic
tie-break. It is not a general real-time analysis package.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import lcm
from typing import Literal, Sequence

Policy = Literal["EDF", "RM"]


@dataclass(frozen=True, slots=True)
class PeriodicTask:
    """Periodic task with integer execution, period, and relative deadline."""

    name: str
    execution: int
    period: int
    deadline: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("task name must be a non-empty string")
        for field_name, value in (("execution", self.execution), ("period", self.period)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{field_name} must be an integer")
            if value <= 0:
                raise ValueError(f"{field_name} must be positive")
        deadline = self.period if self.deadline is None else self.deadline
        if isinstance(deadline, bool) or not isinstance(deadline, int):
            raise TypeError("deadline must be an integer")
        if deadline <= 0:
            raise ValueError("deadline must be positive")
        object.__setattr__(self, "deadline", deadline)


@dataclass(frozen=True, slots=True)
class ScheduleSegment:
    """A maximal half-open interval assigned to one job (or idle)."""

    start: int
    end: int
    task_name: str | None
    job_number: int | None = None
    absolute_deadline: int | None = None


@dataclass(frozen=True, slots=True)
class DeadlineMiss:
    """A job with remaining execution at or after its absolute deadline."""

    task_name: str
    job_number: int
    absolute_deadline: int
    remaining_execution: int


@dataclass(frozen=True, slots=True)
class ScheduleResult:
    policy: Policy
    horizon: int
    segments: tuple[ScheduleSegment, ...]
    misses: tuple[DeadlineMiss, ...]

    @property
    def schedulable_in_horizon(self) -> bool:
        return not self.misses


@dataclass(slots=True)
class _Job:
    task_index: int
    task: PeriodicTask
    number: int
    release: int
    deadline: int
    remaining: int
    miss_recorded: bool = False


def hyperperiod(tasks: Sequence[PeriodicTask]) -> int:
    """Return the least common multiple of task periods."""

    task_values = _validate_tasks(tasks)
    return lcm(*(task.period for task in task_values))


def utilization(tasks: Sequence[PeriodicTask]) -> float:
    """Return total execution utilization Σ Cᵢ/Tᵢ."""

    task_values = _validate_tasks(tasks)
    return sum(task.execution / task.period for task in task_values)


def rm_utilization_bound(task_count: int) -> float:
    """Liu–Layland sufficient bound for n independent periodic RM tasks."""

    if isinstance(task_count, bool) or not isinstance(task_count, int):
        raise TypeError("task_count must be an integer")
    if task_count < 1:
        raise ValueError("task_count must be positive")
    return task_count * (2 ** (1 / task_count) - 1)


def simulate_schedule(
    tasks: Sequence[PeriodicTask],
    policy: Policy,
    horizon: int | None = None,
) -> ScheduleResult:
    """Simulate preemptive EDF or RM with unit time steps and zero overhead.

    Releases occur at integer multiples of each task's period, starting at 0.
    The returned segments cover ``[0, horizon)`` exactly. At time ``t`` the
    scheduler selects from jobs released by ``t`` that still have work. A job
    is late when it has remaining execution at its absolute deadline.
    """

    task_values = _validate_tasks(tasks)
    if policy not in ("EDF", "RM"):
        raise ValueError("policy must be 'EDF' or 'RM'")
    if horizon is None:
        horizon_value = lcm(*(task.period for task in task_values))
    else:
        if isinstance(horizon, bool) or not isinstance(horizon, int):
            raise TypeError("horizon must be an integer or None")
        if horizon <= 0:
            raise ValueError("horizon must be positive")
        horizon_value = horizon

    jobs: list[_Job] = []
    segments: list[ScheduleSegment] = []
    misses: list[DeadlineMiss] = []
    next_release = [0] * len(task_values)
    release_number = [0] * len(task_values)

    def record_misses(at_time: int) -> None:
        for job in jobs:
            if not job.miss_recorded and job.remaining > 0 and job.deadline <= at_time:
                job.miss_recorded = True
                misses.append(
                    DeadlineMiss(job.task.name, job.number, job.deadline, job.remaining)
                )

    for time in range(horizon_value):
        record_misses(time)
        for task_index, task in enumerate(task_values):
            if next_release[task_index] == time:
                release_number[task_index] += 1
                jobs.append(
                    _Job(
                        task_index=task_index,
                        task=task,
                        number=release_number[task_index],
                        release=time,
                        deadline=time + int(task.deadline),
                        remaining=task.execution,
                    )
                )
                next_release[task_index] += task.period

        ready = [job for job in jobs if job.release <= time and job.remaining > 0]
        if not ready:
            _append_segment(segments, ScheduleSegment(time, time + 1, None))
        else:
            if policy == "EDF":
                chosen = min(
                    ready,
                    key=lambda job: (job.deadline, job.release, job.task_index, job.number),
                )
            else:
                chosen = min(
                    ready,
                    key=lambda job: (job.task.period, job.task_index, job.release, job.number),
                )
            _append_segment(
                segments,
                ScheduleSegment(
                    time,
                    time + 1,
                    chosen.task.name,
                    chosen.number,
                    chosen.deadline,
                ),
            )
            chosen.remaining -= 1
        record_misses(time + 1)

    return ScheduleResult(policy, horizon_value, tuple(segments), tuple(misses))


def _append_segment(segments: list[ScheduleSegment], segment: ScheduleSegment) -> None:
    if segments:
        previous = segments[-1]
        if (
            previous.end == segment.start
            and previous.task_name == segment.task_name
            and previous.job_number == segment.job_number
            and previous.absolute_deadline == segment.absolute_deadline
        ):
            segments[-1] = ScheduleSegment(
                previous.start,
                segment.end,
                previous.task_name,
                previous.job_number,
                previous.absolute_deadline,
            )
            return
    segments.append(segment)


def _validate_tasks(tasks: Sequence[PeriodicTask]) -> tuple[PeriodicTask, ...]:
    values = tuple(tasks)
    if not values:
        raise ValueError("at least one task is required")
    if any(not isinstance(task, PeriodicTask) for task in values):
        raise TypeError("tasks must contain PeriodicTask objects")
    names = [task.name for task in values]
    if len(set(names)) != len(names):
        raise ValueError("task names must be unique")
    return values
