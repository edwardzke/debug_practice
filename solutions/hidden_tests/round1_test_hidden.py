"""Hidden test for the BRIEF.md bug report (fractional throughput)."""
from taskqueue import Task
from taskqueue.metrics import throughput_per_hour


def test_throughput_is_fractional():
    tasks = []
    for i in range(3):
        t = Task(f"t{i}", created_at=0)
        t.completed_at = 100 * (i + 1)
        tasks.append(t)
    assert throughput_per_hour(tasks, 0, 7200) == 1.5
