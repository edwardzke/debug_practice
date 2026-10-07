"""Assigns queued tasks to labelers and recycles tasks that time out."""

from __future__ import annotations

import time
from typing import Callable, Iterable

from .models import Labeler, Task, TaskStatus
from .queue import TaskQueue


class SchedulerError(Exception):
    pass


class Scheduler:
    """Hands out tasks to labelers.

    * A labeler only receives tasks whose tags they have the skills for.
    * A labeler never holds more than ``capacity`` tasks.
    * A task is *stale* once it has been held for ``timeout_s`` seconds or
      more without being completed. Stale tasks are returned to the queue,
      unless they have already been attempted ``max_attempts`` times, in
      which case they are marked FAILED.
    """

    def __init__(
        self,
        labelers: Iterable[Labeler],
        queue: TaskQueue | None = None,
        timeout_s: float = 300.0,
        max_attempts: int = 3,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.queue = queue if queue is not None else TaskQueue()
        self.labelers = {l.labeler_id: l for l in labelers}
        self.timeout_s = timeout_s
        self.max_attempts = max_attempts
        self.clock = clock
        self.in_flight: dict[str, Task] = {}
        self.completed: list[Task] = []
        self.failed: list[Task] = []

    def submit(self, task: Task) -> None:
        task.status = TaskStatus.PENDING
        self.queue.push(task)

    def _labeler(self, labeler_id: str) -> Labeler:
        try:
            return self.labelers[labeler_id]
        except KeyError:
            raise SchedulerError(f"unknown labeler {labeler_id!r}") from None

    def assign_next(self, labeler_id: str) -> Task | None:
        """Give ``labeler_id`` the most urgent task they are able to work on."""
        labeler = self._labeler(labeler_id)
        if not labeler.has_capacity():
            return None

        skipped: list[Task] = []
        chosen: Task | None = None
        while (task := self.queue.pop()) is not None:
            if labeler.can_handle(task):
                chosen = task
                break
            skipped.append(task)
        for task in skipped:
            self.queue.push(task)

        if chosen is None:
            return None

        chosen.status = TaskStatus.ASSIGNED
        chosen.assigned_to = labeler_id
        chosen.assigned_at = self.clock()
        chosen.attempts += 1
        labeler.active_tasks.add(chosen.task_id)
        self.in_flight[chosen.task_id] = chosen
        return chosen

    def complete(self, task_id: str, labeler_id: str) -> Task:
        task = self.in_flight.get(task_id)
        if task is None:
            raise SchedulerError(f"task {task_id!r} is not in flight")
        if task.assigned_to != labeler_id:
            raise SchedulerError(
                f"task {task_id!r} is assigned to {task.assigned_to!r}, not {labeler_id!r}"
            )
        del self.in_flight[task_id]
        self._labeler(labeler_id).active_tasks.discard(task_id)
        task.status = TaskStatus.COMPLETED
        task.completed_at = self.clock()
        self.completed.append(task)
        return task

    def expire_stale(self) -> list[Task]:
        """Reclaim stale tasks. Returns the tasks that were reclaimed."""
        now = self.clock()
        expired: list[Task] = []
        for task_id, task in self.in_flight.items():
            assert task.assigned_at is not None
            if now - task.assigned_at > self.timeout_s:
                del self.in_flight[task_id]
                if task.assigned_to is not None:
                    self._labeler(task.assigned_to).active_tasks.discard(task_id)
                task.assigned_to = None
                task.assigned_at = None
                if task.attempts >= self.max_attempts:
                    task.status = TaskStatus.FAILED
                    self.failed.append(task)
                else:
                    self.submit(task)
                expired.append(task)
        return expired
