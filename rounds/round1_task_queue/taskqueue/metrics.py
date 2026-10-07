"""Operational metrics for the labeling dashboard."""

from __future__ import annotations

from typing import Iterable

from .models import Labeler, Task
from .scheduler import Scheduler


def throughput_per_hour(
    completed: Iterable[Task], window_start: float, window_end: float
) -> float:
    """Completed tasks per hour within ``[window_start, window_end)`` (seconds)."""
    if window_end <= window_start:
        raise ValueError("window_end must be after window_start")
    count = sum(
        1
        for t in completed
        if t.completed_at is not None and window_start <= t.completed_at < window_end
    )
    hours = (window_end - window_start) / 3600
    return count // hours


def average_handle_time(completed: Iterable[Task]) -> float | None:
    """Mean seconds between creation and completion, or None if nothing completed."""
    durations = [
        t.completed_at - t.created_at for t in completed if t.completed_at is not None
    ]
    if not durations:
        return None
    return sum(durations) / len(durations)


def labeler_utilization(labelers: Iterable[Labeler]) -> dict[str, float]:
    """Fraction of each labeler's capacity currently in use (0.0 - 1.0)."""
    return {l.labeler_id: len(l.active_tasks) / l.capacity for l in labelers}


def summary(scheduler: Scheduler) -> dict[str, object]:
    return {
        "pending": len(scheduler.queue),
        "in_flight": len(scheduler.in_flight),
        "completed": len(scheduler.completed),
        "failed": len(scheduler.failed),
        "utilization": labeler_utilization(scheduler.labelers.values()),
    }
