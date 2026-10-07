import pytest

from taskqueue import Labeler, Scheduler, Task
from taskqueue.metrics import (
    average_handle_time,
    labeler_utilization,
    summary,
    throughput_per_hour,
)


def _done(task_id, created_at, completed_at):
    t = Task(task_id, created_at=created_at)
    t.completed_at = completed_at
    return t


def test_throughput_counts_window():
    tasks = [_done("a", 0, 100), _done("b", 0, 3599), _done("c", 0, 3600)]
    assert throughput_per_hour(tasks, 0, 3600) == 2.0


def test_throughput_over_two_hours():
    tasks = [_done(f"t{i}", 0, 60 * i) for i in range(1, 5)]
    assert throughput_per_hour(tasks, 0, 7200) == 2.0


def test_throughput_rejects_empty_window():
    with pytest.raises(ValueError):
        throughput_per_hour([], 10, 10)


def test_average_handle_time():
    tasks = [_done("a", 0, 10), _done("b", 5, 25)]
    assert average_handle_time(tasks) == 15.0
    assert average_handle_time([]) is None


def test_labeler_utilization():
    full = Labeler("full", capacity=2)
    full.active_tasks.update({"a", "b"})
    idle = Labeler("idle", capacity=4)
    assert labeler_utilization([full, idle]) == {"full": 1.0, "idle": 0.0}


def test_summary(clock):
    s = Scheduler([Labeler("alice", capacity=3)], clock=clock)
    for i in range(4):
        s.submit(Task(f"t{i}"))
    s.assign_next("alice")
    s.assign_next("alice")
    s.complete("t0", "alice")
    out = summary(s)
    assert out["pending"] == 2
    assert out["in_flight"] == 1
    assert out["completed"] == 1
    assert out["failed"] == 0
    assert out["utilization"]["alice"] == pytest.approx(1 / 3)
