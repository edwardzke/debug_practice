# Round 1 Solutions — Course Selection & Project Staffing (SPOILERS)

4 bugs (they break Tests 1 and 2) plus 1 function to implement (Test 3). Reference fix: `round1.patch`.

**Triage tip:** Test 1 only covers simple projects, so it can only fail because of the ordering and
capacity logic in `assignment.py`. Fix that first. Test 2 then adds the prerequisite path
(`find_eligible_contributors` → `Project.required_course_ids` → `Contributor`). Print the actual vs
expected dict for each project and compare them one project at a time.

---

## Bug 1 — Priority sorted ascending (`assignment.py`, `sort_projects_by_priority`)
**Symptom (Test 1):** Copper Lantern (priority 3) gets the first contributors instead of Galaxy Velvet (8).
- **Hint 1:** Print the project names in the order `sort_projects_by_priority` returns them.
- **Fix:** `sorted(projects, key=lambda p: p.priority, reverse=True)`.

## Bug 2 — Headcount check is `>= 0` (`assignment.py`, `assign_contributors`)
**Symptom (Test 1):** Every project ends up with one person more than its headcount.
- **Hint 1:** When `available_headcount()` returns 0, should anyone else be added?
- **Fix:** `if project.available_headcount() > 0:`.

## Bug 3 — Completion status not checked (`assignment.py`, `find_eligible_contributors`)
**Symptom (Test 2, visible once Bug 4 is fixed):** Ava Chen joins Midnight Orchid although her Medical
Terminology status is `in_progress`. Elif's Thai course is also only `in_progress`.
- **Hint 1:** Open `data/contributor_courses.csv`. Which statuses besides `completed` appear?
- **Hint 2:** `Contributor` has a method marked correct that nobody calls...
- **Fix:** `if all(contributor.has_completed(course_id) for course_id in required):`.
- **Why:** `course_id in contributor.course_status` only means "has a record for the course", not "completed it".

## Bug 4 — Course ID read from the class variable (`models.py`, `Project.required_course_ids`)
**Symptom (Test 2):** Every project with prerequisites gets nobody, or (while Bug 3 is still there) the
wrong people. `required_course_ids()` returns `{''}`.
- **Hint 1:** Print `project.required_course_ids()` for Midnight Orchid.
- **Hint 2:** Look closely at the capitalization: `Course.course_id` vs `course.course_id`.
- **Fix:** `{course.course_id for course in self.required_courses}`.
- **Why:** `Course.course_id` is the *class* attribute (default `""`), not the attribute set on each instance in `__init__`.
  The loop variable is never used, which is a lint-level clue.

## Test 3 — Implement `most_needed_course` (`analysis.py`)
**Approach:** For each course (in file order):
1. Build *copies* of the contributors with that course marked `completed`. Don't mutate the
   real objects; the test checks for that.
2. Run `assign_contributors(projects, copies)`. It resets projects at the start, so repeated runs are safe.
3. Score the result as `(count_filled_projects(...), total assigned)`. Keep the best, and use a strict `>` so ties keep the earlier course.
4. Return the course **name**, not its id.

**Expected answer:** `LiDAR Annotation`. It lets Femi fill the last Silver Quokka slot, for 5 full projects; every other course gives 4.
**Trap:** The course required by the most projects (Intro to Data Labeling) is *not* the answer.

Reference implementation: see the `analysis.py` hunk in `round1.patch`.
