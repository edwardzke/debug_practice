"""Core domain objects for the labeling task queue."""

from __future__ import annotations

from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    FAILED = "failed"


class Task:
    """A unit of labeling work.

    Higher ``priority`` values are more urgent. ``tags`` describe the skills a
    labeler needs in order to work on the task (e.g. ``"medical"``, ``"lidar"``).
    """

    def __init__(
        self,
        task_id: str,
        priority: int = 0,
        created_at: float = 0.0,
        tags: list[str] = [],
    ) -> None:
        self.task_id = task_id
        self.priority = priority
        self.created_at = created_at
        self.tags = tags
        self.status = TaskStatus.PENDING
        self.attempts = 0
        self.assigned_to: str | None = None
        self.assigned_at: float | None = None
        self.completed_at: float | None = None

    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)

    def __repr__(self) -> str:
        return (
            f"Task({self.task_id!r}, priority={self.priority}, "
            f"status={self.status.value}, tags={self.tags})"
        )


class Labeler:
    """A human labeler who can hold up to ``capacity`` tasks at once."""

    def __init__(
        self,
        labeler_id: str,
        capacity: int = 3,
        skills: set[str] | None = None,
    ) -> None:
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.labeler_id = labeler_id
        self.capacity = capacity
        self.skills = set(skills or ())
        self.active_tasks: set[str] = set()

    def has_capacity(self) -> bool:
        return len(self.active_tasks) <= self.capacity

    def can_handle(self, task: Task) -> bool:
        """A labeler can handle a task if they have every skill it is tagged with."""
        return all(tag in self.skills for tag in task.tags)

    def __repr__(self) -> str:
        return (
            f"Labeler({self.labeler_id!r}, "
            f"{len(self.active_tasks)}/{self.capacity} active)"
        )
