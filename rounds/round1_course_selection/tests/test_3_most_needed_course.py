"""Test 3/3: Most Needed Course Test.

Find the most needed course. Defined as: if all contributors were assumed to
have completed this course, it would allow the maximum number of projects to
be filled with the maximum number of contributors. Return the name of that
course. (Exact scoring and tie-break rules: see analysis.most_needed_course.)
"""

from analysis import most_needed_course
from loader import load_all

EXPECTED_COURSE = "LiDAR Annotation"


def test_most_needed_course():
    courses, contributors, projects = load_all()
    before = {c.contributor_id: dict(c.course_status) for c in contributors}

    assert most_needed_course(courses, contributors, projects) == EXPECTED_COURSE

    after = {c.contributor_id: dict(c.course_status) for c in contributors}
    assert after == before, "most_needed_course must not modify the real contributors"
