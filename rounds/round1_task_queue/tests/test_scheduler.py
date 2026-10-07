import pytest

from taskqueue import Labeler, Scheduler, SchedulerError, Task, TaskStatus


def make_scheduler(clock, labelers=None, **kwargs):
    labelers = labelers or [Labeler("alice", capacity=2), Labeler("bob", capacity=1)]
    return Scheduler(labelers, clock=clock, **kwargs)


def test_assign_gives_most_urgent_task(clock):
    s = make_scheduler(clock)
    s.submit(Task("routine", priority=1))
    s.submit(Task("urgent", priority=9))
    task = s.assign_next("alice")
    assert task.task_id == "urgent"
    assert task.status is TaskStatus.ASSIGNED
    assert task.assigned_to == "alice"
    assert task.attempts == 1
    assert "urgent" in s.labelers["alice"].active_tasks


def test_assign_unknown_labeler(clock):
    s = make_scheduler(clock)
    with pytest.raises(SchedulerError):
        s.assign_next("mallory")


def test_assign_respects_capacity(clock):
    s = make_scheduler(clock)
    for i in range(5):
        s.submit(Task(f"t{i}"))
    assert s.assign_next("bob") is not None
    assert s.assign_next("bob") is None
    assert len(s.labelers["bob"].active_tasks) == 1
    assert len(s.queue) == 4


def test_assign_skips_tasks_labeler_cannot_handle(clock):
    s = make_scheduler(clock, labelers=[Labeler("alice", skills={"lidar"})])
    s.submit(Task("med", priority=9, tags=["medical"]))
    s.submit(Task("pc", priority=1, tags=["lidar"]))
    task = s.assign_next("alice")
    assert task.task_id == "pc"
    assert "med" in s.queue


def test_untagged_tasks_go_to_anyone(clock):
    s = make_scheduler(clock, labelers=[Labeler("alice"), Labeler("bob")])
    special = Task("special")
    special.add_tag("medical")
    s.submit(special)
    s.submit(Task("plain"))
    assert s.assign_next("bob").task_id == "plain"


def test_complete_releases_capacity(clock):
    s = make_scheduler(clock)
    s.submit(Task("a"))
    s.submit(Task("b"))
    s.assign_next("bob")
    clock.advance(30)
    done = s.complete("a", "bob")
    assert done.status is TaskStatus.COMPLETED
    assert done.completed_at == clock.now
    assert s.assign_next("bob").task_id == "b"


def test_complete_by_wrong_labeler(clock):
    s = make_scheduler(clock)
    s.submit(Task("a"))
    s.assign_next("alice")
    with pytest.raises(SchedulerError):
        s.complete("a", "bob")
    assert "a" in s.in_flight


def test_nothing_expires_before_timeout(clock):
    s = make_scheduler(clock, timeout_s=60)
    s.submit(Task("a"))
    s.assign_next("alice")
    clock.advance(59.9)
    assert s.expire_stale() == []
    assert "a" in s.in_flight


def test_expired_tasks_are_requeued(clock):
    s = make_scheduler(clock, timeout_s=60)
    s.submit(Task("a"))
    s.submit(Task("b"))
    s.assign_next("alice")
    s.assign_next("alice")
    clock.advance(120)
    expired = s.expire_stale()
    assert sorted(t.task_id for t in expired) == ["a", "b"]
    assert s.in_flight == {}
    assert s.labelers["alice"].active_tasks == set()
    assert len(s.queue) == 2
    assert all(t.status is TaskStatus.PENDING for t in expired)


def test_task_expires_exactly_at_timeout(clock):
    s = make_scheduler(clock, timeout_s=60)
    s.submit(Task("a"))
    s.assign_next("alice")
    clock.advance(60)
    expired = s.expire_stale()
    assert [t.task_id for t in expired] == ["a"]


def test_task_fails_after_max_attempts(clock):
    s = make_scheduler(clock, timeout_s=10, max_attempts=2)
    s.submit(Task("flaky"))
    for _ in range(2):
        assert s.assign_next("alice").task_id == "flaky"
        clock.advance(15)
        s.expire_stale()
    assert [t.task_id for t in s.failed] == ["flaky"]
    assert s.failed[0].status is TaskStatus.FAILED
    assert len(s.queue) == 0
