import pytest

from taskqueue import Labeler, Task, TaskStatus


def test_task_defaults():
    t = Task("t1")
    assert t.priority == 0
    assert t.status is TaskStatus.PENDING
    assert t.attempts == 0
    assert t.tags == []


def test_add_tag_is_idempotent():
    t = Task("t1")
    t.add_tag("lidar")
    t.add_tag("lidar")
    assert t.tags == ["lidar"]


def test_tags_are_independent_between_tasks():
    a = Task("a")
    b = Task("b")
    a.add_tag("medical")
    assert b.tags == []


def test_task_copies_tag_list():
    tags = ["lidar"]
    t = Task("t1", tags=tags)
    t.add_tag("night")
    assert tags == ["lidar"]


def test_labeler_rejects_zero_capacity():
    with pytest.raises(ValueError):
        Labeler("l1", capacity=0)


def test_labeler_capacity_limit():
    l = Labeler("l1", capacity=2)
    assert l.has_capacity()
    l.active_tasks.add("a")
    assert l.has_capacity()
    l.active_tasks.add("b")
    assert not l.has_capacity()


def test_can_handle_requires_all_skills():
    l = Labeler("l1", skills={"lidar"})
    assert l.can_handle(Task("t1"))
    assert l.can_handle(Task("t2", tags=["lidar"]))
    assert not l.can_handle(Task("t3", tags=["lidar", "medical"]))
