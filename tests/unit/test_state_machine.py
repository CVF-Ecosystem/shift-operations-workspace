from workspace_api.domain.lifecycle import assert_transition
from workspace_api.domain.models import DataState

def test_confirmed_can_freeze():
    assert_transition(DataState.CONFIRMED, DataState.FROZEN)
