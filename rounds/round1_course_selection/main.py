"""Run all three tasks against the CSVs in data/ and print the results."""

from pprint import pprint

from analysis import most_needed_course
from assignment import assign_all_projects, assign_simple_projects
from loader import load_all


def main() -> None:
    courses, contributors, projects = load_all()

    print("Test 1/3 - simple projects:")
    pprint(assign_simple_projects(projects, contributors))

    print("\nTest 2/3 - all projects:")
    pprint(assign_all_projects(projects, contributors))

    print("\nTest 3/3 - most needed course:")
    try:
        print(most_needed_course(courses, contributors, projects))
    except NotImplementedError:
        print("(not implemented yet)")


if __name__ == "__main__":
    main()
