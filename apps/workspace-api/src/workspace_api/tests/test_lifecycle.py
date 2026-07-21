from workspace_api.domain.lifecycle import assert_transition
from workspace_api.domain.models import DataState

def test_valid_transition():
    assert_transition(DataState.RAW, DataState.NORMALIZED)

def test_invalid_transition():
    try:
        assert_transition(DataState.RAW, DataState.CONFIRMED)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")
