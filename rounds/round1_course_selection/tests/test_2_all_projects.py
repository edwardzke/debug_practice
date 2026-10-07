"""Test 2/3: All Projects Assignment Test.

Test contributor assignment across all projects, including those with
required prereq courses.

  * A contributor can only be assigned to a project if they've completed all required courses.
  * Each contributor can only join one project.
  * Projects must not exceed their headcount.
  * Projects are handled in descending priority order.
  * Contributors are assigned in the fixed input order.
"""

from assignment import assign_all_projects
from loader import load_all

EXPECTED_ASSIGNMENTS = {
    "project_assignments": {
        "Midnight Orchid": ["Ben Okafor", "Elif Yilmaz"],
        "Galaxy Velvet": ["Ava Chen", "Carla Diaz", "Dev Patel"],
        "Amber Falcon": ["Grace Kim", "Kenji Sato"],
        "Silver Quokka": ["Isha Rao", "Lena Novak"],
        "Tangerine Jubilant": ["Femi Adeyemi", "Hugo Martin"],
        "Polar Sonnet": [],
        "Copper Lantern": ["Jonas Berg"],
    }
}


def test_all_projects_assignment():
    _, contributors, projects = load_all()
    assert assign_all_projects(projects, contributors) == EXPECTED_ASSIGNMENTS
