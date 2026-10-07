"""Priority queue of pending tasks."""

from __future__ import annotations

import heapq
import itertools
from typing import Any

from .models import Task

_REMOVED = object()


class TaskQueue:
    """Priority queue of tasks.

    Ordering rules:
      * higher ``priority`` comes out first;
      * among equal priorities, the task with the earliest ``created_at`` wins;
      * among exact ties, insertion order (FIFO) wins.

    Tasks can be removed by id in O(1) (lazy deletion).
    """

    def __init__(self) -> None:
        self._heap: list[list[Any]] = []
        self._entries: dict[str, list[Any]] = {}
        self._counter = itertools.count()

    def push(self, task: Task) -> None:
        if task.task_id in self._entries:
            self.remove(task.task_id)
        entry = [task.priority, task.created_at, next(self._counter), task]
        self._entries[task.task_id] = entry
        heapq.heappush(self._heap, entry)

    def remove(self, task_id: str) -> Task | None:
        entry = self._entries.pop(task_id, None)
        if entry is None:
            return None
        task = entry[-1]
        entry[-1] = _REMOVED
        return task

    def pop(self) -> Task | None:
        while self._heap:
            entry = heapq.heappop(self._heap)
            task = entry[-1]
            if task is not _REMOVED:
                del self._entries[task.task_id]
                return task
        return None

    def peek(self) -> Task | None:
        while self._heap and self._heap[0][-1] is _REMOVED:
            heapq.heappop(self._heap)
        return self._heap[0][-1] if self._heap else None

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, task_id: object) -> bool:
        return task_id in self._entries
