"""Loads the CSV files in ``data/`` into model objects."""

from __future__ import annotations

import csv
from pathlib import Path

from models import Contributor, Course, Project

DATA_DIR = Path(__file__).resolve().parent / "data"


# NOTE: This function is correct and does not need to be modified.
def read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return [{k.strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(fh)]


# NOTE: This function is correct and does not need to be modified.
def load_courses(data_dir: Path = DATA_DIR) -> dict[str, Course]:
    """course_id -> Course, in file order."""
    return {
        row["course_id"]: Course(row["course_id"], row["course_name"])
        for row in read_csv(data_dir / "courses.csv")
    }


# NOTE: This function is correct and does not need to be modified.
def load_contributors(data_dir: Path = DATA_DIR) -> list[Contributor]:
    """Contributors in file order, with their course statuses attached."""
    contributors = [
        Contributor(row["contributor_id"], row["name"])
        for row in read_csv(data_dir / "contributors.csv")
    ]
    by_id = {c.contributor_id: c for c in contributors}
    for row in read_csv(data_dir / "contributor_courses.csv"):
        by_id[row["contributor_id"]].record_course(row["course_id"], row["status"])
    return contributors


# NOTE: This function is correct and does not need to be modified.
def load_projects(courses: dict[str, Course], data_dir: Path = DATA_DIR) -> list[Project]:
    """Projects in file order, with their prerequisite courses attached."""
    projects = [
        Project(row["project_id"], row["project_name"], int(row["priority"]), int(row["headcount"]))
        for row in read_csv(data_dir / "projects.csv")
    ]
    by_id = {p.project_id: p for p in projects}
    for row in read_csv(data_dir / "project_requirements.csv"):
        by_id[row["project_id"]].add_required_course(courses[row["course_id"]])
    return projects


# NOTE: This function is correct and does not need to be modified.
def load_all(data_dir: Path = DATA_DIR) -> tuple[dict[str, Course], list[Contributor], list[Project]]:
    courses = load_courses(data_dir)
    return courses, load_contributors(data_dir), load_projects(courses, data_dir)
