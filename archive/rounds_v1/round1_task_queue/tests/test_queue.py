from taskqueue import Task, TaskQueue


def test_empty_queue():
    q = TaskQueue()
    assert len(q) == 0
    assert q.pop() is None
    assert q.peek() is None


def test_higher_priority_pops_first():
    q = TaskQueue()
    q.push(Task("low", priority=1))
    q.push(Task("high", priority=10))
    q.push(Task("mid", priority=5))
    assert [q.pop().task_id for _ in range(3)] == ["high", "mid", "low"]


def test_equal_priority_is_oldest_first():
    q = TaskQueue()
    q.push(Task("newer", priority=3, created_at=20.0))
    q.push(Task("older", priority=3, created_at=10.0))
    assert q.pop().task_id == "older"


def test_exact_ties_are_fifo():
    q = TaskQueue()
    for i in range(5):
        q.push(Task(f"t{i}", priority=1, created_at=0.0))
    assert [q.pop().task_id for _ in range(5)] == ["t0", "t1", "t2", "t3", "t4"]


def test_remove_by_id():
    q = TaskQueue()
    q.push(Task("a", priority=1))
    q.push(Task("b", priority=2))
    removed = q.remove("b")
    assert removed is not None and removed.task_id == "b"
    assert len(q) == 1
    assert "b" not in q
    assert q.pop().task_id == "a"
    assert q.pop() is None


def test_remove_missing_returns_none():
    assert TaskQueue().remove("nope") is None


def test_peek_does_not_consume():
    q = TaskQueue()
    q.push(Task("a", priority=1))
    q.push(Task("b", priority=9))
    assert q.peek().task_id == "b"
    assert len(q) == 2
    assert q.pop().task_id == "b"


def test_repush_updates_priority():
    q = TaskQueue()
    t = Task("a", priority=1)
    q.push(t)
    q.push(Task("b", priority=5))
    t.priority = 10
    q.push(t)
    assert len(q) == 2
    assert q.pop().task_id == "a"
