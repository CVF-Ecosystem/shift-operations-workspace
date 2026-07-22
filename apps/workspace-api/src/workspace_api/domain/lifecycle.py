from .models import DataState, TaskStatus

_ALLOWED: dict[DataState, set[DataState]] = {
    DataState.RAW: {DataState.NORMALIZED, DataState.REJECTED},
    DataState.NORMALIZED: {DataState.PROPOSED, DataState.REJECTED},
    DataState.PROPOSED: {DataState.CONFIRMED, DataState.REJECTED},
    DataState.CONFIRMED: {DataState.CORRECTED, DataState.FROZEN},
    DataState.CORRECTED: {DataState.FROZEN},
    DataState.REJECTED: set(),
    DataState.FROZEN: set(),
}

def assert_transition(current: DataState, target: DataState) -> None:
    if target not in _ALLOWED[current]:
        raise ValueError(f"Invalid data-state transition: {current} -> {target}")


# Task status lifecycle (separate from the RAW..FROZEN data-state machine).
_ALLOWED_TASK: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.OPEN: {TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.CANCELLED, TaskStatus.CARRY_OVER},
    TaskStatus.IN_PROGRESS: {TaskStatus.BLOCKED, TaskStatus.DONE, TaskStatus.CANCELLED, TaskStatus.CARRY_OVER},
    TaskStatus.BLOCKED: {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED, TaskStatus.CARRY_OVER},
    TaskStatus.CARRY_OVER: {TaskStatus.OPEN, TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
    TaskStatus.DONE: set(),
    TaskStatus.CANCELLED: set(),
}


def assert_task_transition(current: TaskStatus, target: TaskStatus) -> None:
    if target not in _ALLOWED_TASK[current]:
        raise ValueError(f"Invalid task-status transition: {current} -> {target}")
