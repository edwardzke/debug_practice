"""Course-demand analysis built on top of the assignment logic."""

from __future__ import annotations

from assignment import assign_contributors
from models import COMPLETED, Contributor, Course, Project


# NOTE: This function is correct and does not need to be modified.
def count_filled_projects(assignments: dict[str, list[str]], projects: list[Project]) -> int:
    """Number of projects whose assigned list has reached the project's full headcount."""
    headcount = {p.name: p.headcount for p in projects}
    return sum(1 for name, people in assignments.items() if len(people) >= headcount[name])


def most_needed_course(
    courses: dict[str, Course], contributors: list[Contributor], projects: list[Project]
) -> str:
    """Return the *name* of the most needed course.

    For each course, imagine that every contributor had completed it (on top
    of the courses they actually completed) and run the full assignment
    across all projects. Score that scenario as

        (number of projects filled to full headcount, total contributors assigned)

    The most needed course is the one with the highest score (compare the
    first number, then the second). If two courses tie, pick the one that
    appears first in ``courses`` (file order).

    Must not change the real contributors' course records.
    """
    raise NotImplementedError
