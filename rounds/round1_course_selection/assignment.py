"""Assigns contributors to projects.

Rules:
  * Projects are processed in descending order of priority
    (higher number = higher priority).
  * Within a project, contributors are considered in their input order
    (first come, first served).
  * A contributor may join at most one project.
  * A project never exceeds its headcount.
  * A contributor may only join a project if they have completed every
    prerequisite course for it.
"""

from __future__ import annotations

from models import Contributor, Project


def sort_projects_by_priority(projects: list[Project]) -> list[Project]:
    return sorted(projects, key=lambda p: p.priority)


def find_eligible_contributors(
    project: Project, contributors: list[Contributor], assigned_ids: set[str]
) -> list[Contributor]:
    """Unassigned contributors (in input order) who satisfy the project's prerequisites."""
    required = project.required_course_ids()
    eligible = []
    for contributor in contributors:
        if contributor.contributor_id in assigned_ids:
            continue
        if all(course_id in contributor.course_status for course_id in required):
            eligible.append(contributor)
    return eligible


def assign_contributors(
    projects: list[Project], contributors: list[Contributor]
) -> dict[str, list[str]]:
    """Run the assignment. Returns project name -> assigned contributor names."""
    for project in projects:
        project.reset()

    assigned_ids: set[str] = set()
    result: dict[str, list[str]] = {}
    for project in sort_projects_by_priority(projects):
        for contributor in find_eligible_contributors(project, contributors, assigned_ids):
            if project.available_headcount() >= 0:
                project.assign(contributor)
                assigned_ids.add(contributor.contributor_id)
        result[project.name] = [c.name for c in project.assigned]
    return result


# NOTE: This function is correct and does not need to be modified.
def format_result(assignments: dict[str, list[str]]) -> dict[str, dict[str, list[str]]]:
    return {"project_assignments": assignments}


# NOTE: This function is correct and does not need to be modified.
def assign_simple_projects(projects: list[Project], contributors: list[Contributor]) -> dict:
    """Assign contributors to simple projects only (no prerequisite courses)."""
    simple = [p for p in projects if p.is_simple()]
    return format_result(assign_contributors(simple, contributors))


# NOTE: This function is correct and does not need to be modified.
def assign_all_projects(projects: list[Project], contributors: list[Contributor]) -> dict:
    """Assign contributors across every project, including ones with prerequisites."""
    return format_result(assign_contributors(projects, contributors))
