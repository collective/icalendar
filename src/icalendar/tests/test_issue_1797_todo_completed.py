from datetime import datetime, timezone


def test_todo_completed(todos):
    todo = todos["issue_1797_completed"]

    assert todo.COMPLETED == datetime(
        2007, 5, 1, tzinfo=timezone.utc
    )
