from operations_domain.lifecycle import assert_transition
from operations_domain.models import DataState

def test_confirmed_can_freeze():
    assert_transition(DataState.CONFIRMED, DataState.FROZEN)
