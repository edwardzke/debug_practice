"""Test 1/3: Simple Projects Assignment Test.

Assign all contributors to simple projects only (projects with no required
prereq courses).

  * Each contributor can only be assigned to one project.
  * Projects have a headcount limit that must not be exceeded.
  * Contributors are assigned in the order they appear (first come, first served).
  * Projects are processed in descending order of priority (higher number = higher priority).
"""

from assignment import assign_simple_projects
from loader import load_all

EXPECTED = {
    "project_assignments": {
        "Galaxy Velvet": ["Ava Chen", "Ben Okafor", "Carla Diaz"],
        "Tangerine Jubilant": ["Dev Patel", "Elif Yilmaz"],
        "Copper Lantern": ["Femi Adeyemi", "Grace Kim"],
    }
}


def test_simple_projects_assignment():
    _, contributors, projects = load_all()
    assert assign_simple_projects(projects, contributors) == EXPECTED
