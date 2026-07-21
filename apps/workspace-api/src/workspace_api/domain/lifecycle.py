from .models import DataState

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
