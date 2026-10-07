# Round 1 — Course Selection & Project Staffing

This is a student course-selection management system. Contributors (students)
take courses, and projects need people. Some projects require prerequisite
courses. The code reads the CSV files in `data/`, then works out which
contributors can join which projects.

**Files**
- `models.py` — `Course`, `Contributor`, `Project`
- `loader.py` — reads the CSVs into model objects
- `assignment.py` — the assignment algorithm (its rules are in the module docstring)
- `analysis.py` — the "most needed course" analysis
- `main.py` — runs all three tasks and prints the results (`python main.py`)
- `data/*.csv` — courses, contributors, contributor course statuses, projects, project prerequisites

Functions marked `# NOTE: This function is correct and does not need to be modified.`
are correct, so trust them. Anything else is fair game. Don't edit the tests.

## The 3 graded tests (`tests/`)

**Test 1/3 — Simple Projects Assignment.** Assign all contributors to simple
projects only (projects with no required prereq courses). Each contributor
joins at most one project, headcount limits are never exceeded, contributors
are taken first come, first served, and projects are processed in descending
priority (a higher number means higher priority).

**Test 2/3 — All Projects Assignment.** The same rules across *all* projects,
plus: a contributor can only join a project if they've completed all of its
required courses. The output must exactly match `EXPECTED_ASSIGNMENTS`.

**Test 3/3 — Most Needed Course.** Implement `most_needed_course` in
`analysis.py`. It should return the course which, if every contributor were
assumed to have completed it, would let the most projects be filled with the
most contributors. The exact scoring and tie-break rules are in its docstring.

Output format for Tests 1 and 2:
```python
{'project_assignments': {'Galaxy Velvet': [...], 'Tangerine Jubilant': [...], ...}}
```

Suggested order: get Test 1 green, then Test 2 (it relies on the same code
plus the prerequisite logic), then Test 3, which depends on a correct
assignment.

Talk through your reasoning out loud as you go.

Run tests: `python ../../practice.py check 1` (from here) or `python -m pytest -q`.
