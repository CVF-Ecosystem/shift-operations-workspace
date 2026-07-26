from operations_domain.lifecycle import assert_incident_transition, assert_transition
from operations_domain.models import DataState, IncidentStatus

def test_valid_transition():
    assert_transition(DataState.RAW, DataState.NORMALIZED)

def test_invalid_transition():
    try:
        assert_transition(DataState.RAW, DataState.CONFIRMED)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")

def test_valid_incident_transition():
    assert_incident_transition(IncidentStatus.ACKNOWLEDGED, IncidentStatus.RESOLVED)

def test_invalid_incident_transition():
    try:
        assert_incident_transition(IncidentStatus.CLOSED, IncidentStatus.REPORTED)
    except ValueError:
        return
    raise AssertionError("Expected ValueError")
