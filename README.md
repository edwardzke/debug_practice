# Debugging Round Practice

A timed replica of the Scale AI intern debugging round: a student course-selection management
system made of several Python files plus CSV data, three graded tests, and some functions marked
as correct.

| # | Round | What you do |
|---|-------|-------------|
| 1 | `round1_course_selection` | Fix the assignment logic so Tests 1 & 2 pass, then implement Test 3 (most needed course) |

The earlier general-purpose warm-up rounds (task queue, service utils, annotation pipeline) are
kept in `archive/` in case you want extra reps. They aren't run by `practice.py`.

## Setup (once)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Running a round
```bash
python practice.py start 1             # copies a fresh buggy round to workspace/round1, starts a 45-min timer
python practice.py start 1 --minutes 60
python practice.py check 1             # run the 3 tests, show N/3 passing and elapsed time
python practice.py check 1 -k test_2   # extra args go to pytest
python practice.py reset 1             # throw away workspace/round1 to try again later
```
Edit files **only in `workspace/round1/`**. `rounds/` holds the pristine buggy copy. In the
round folder, `python main.py` prints what each task currently produces.

### Using an IDE (VSCodium / Cursor)
Open **`workspace/round1`** as the folder, not the repo root, so `solutions/` stays out of view and
pytest picks up the round's `pytest.ini`. Set the interpreter to `../../.venv/bin/python`.
In Cursor, turn off Cursor Tab, Chat, and codebase indexing while practicing.

## Rules to simulate the interview
- Don't open `solutions/` until time is up (or you're stuck; the hints are tiered, so read one line at a time).
- Trust the functions marked `This function is correct`. Don't edit the tests.
- **Talk out loud** (or record yourself). Interviewers grade your process as much as the fixes.
- Use whatever you'd have in an interview: `pytest -x`, `print`, `breakpoint()`, a REPL, `python main.py`.

## A process that works
1. **Survey (3–5 min):** Read the BRIEF, skim each file, and look at the CSVs. Note which functions are marked correct; the bugs are elsewhere.
2. **Diff the output:** Print actual vs expected and compare one project at a time. Each difference points to a rule (priority order, headcount, prerequisites).
3. **One bug at a time:** Form a hypothesis, check it with the smallest experiment, fix it, and **re-run all tests**.
4. **Test 3 last:** It builds on correct assignment logic. Read its docstring carefully: scoring, tie-break, and "don't mutate the input" all matter.
5. **Narrate:** "I expect X because the spec says Y; I see Z; so the bug is between here and here."

## After a round
Read `solutions/round1.md`. For each bug you missed, write down which signal you overlooked.

## Maintainer
`python practice.py verify all` checks that the pristine round fails and that
`solutions/round1.patch` turns all three tests green.
