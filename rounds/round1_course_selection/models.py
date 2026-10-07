"""Domain models for the course selection / project staffing system.

Contributors (students) complete courses. Projects may list prerequisite
courses; a contributor may only join a project once they have *completed*
every prerequisite.
"""

from __future__ import annotations

COMPLETED = "completed"


class Course:
    course_id: str = ""
    course_name: str = ""

    # NOTE: This function is correct and does not need to be modified.
    def __init__(self, course_id: str, course_name: str) -> None:
        self.course_id = course_id
        self.course_name = course_name

    def __repr__(self) -> str:
        return f"Course({self.course_id!r}, {self.course_name!r})"


class Contributor:
    # NOTE: This function is correct and does not need to be modified.
    def __init__(self, contributor_id: str, name: str) -> None:
        self.contributor_id = contributor_id
        self.name = name
        # course_id -> status ("completed", "in_progress", "dropped", ...)
        self.course_status: dict[str, str] = {}

    # NOTE: This function is correct and does not need to be modified.
    def record_course(self, course_id: str, status: str) -> None:
        self.course_status[course_id] = status.strip().lower()

    # NOTE: This function is correct and does not need to be modified.
    def has_completed(self, course_id: str) -> bool:
        return self.course_status.get(course_id) == COMPLETED

    def __repr__(self) -> str:
        return f"Contributor({self.contributor_id!r}, {self.name!r})"


class Project:
    # NOTE: This function is correct and does not need to be modified.
    def __init__(self, project_id: str, name: str, priority: int, headcount: int) -> None:
        self.project_id = project_id
        self.name = name
        self.priority = priority
        self.headcount = headcount
        self.required_courses: list[Course] = []
        self.assigned: list[Contributor] = []

    # NOTE: This function is correct and does not need to be modified.
    def add_required_course(self, course: Course) -> None:
        self.required_courses.append(course)

    def required_course_ids(self) -> set[str]:
        """IDs of every prerequisite course for this project."""
        return {Course.course_id for course in self.required_courses}

    def is_simple(self) -> bool:
        """A simple project has no prerequisite courses."""
        return not self.required_courses

    # NOTE: This function is correct and does not need to be modified.
    def available_headcount(self) -> int:
        return self.headcount - len(self.assigned)

    # NOTE: This function is correct and does not need to be modified.
    def assign(self, contributor: Contributor) -> None:
        self.assigned.append(contributor)

    # NOTE: This function is correct and does not need to be modified.
    def reset(self) -> None:
        self.assigned = []

    def __repr__(self) -> str:
        return (
            f"Project({self.name!r}, priority={self.priority}, "
            f"{len(self.assigned)}/{self.headcount})"
        )
