import copy

import pytest
from pydantic import ValidationError

from channel_adapters.conformance import emit_adapter_result
from channel_sdk import AdapterDeliveryResultV1
from channel_sdk.invariants import adapter_result_matrix


def test_emitter_has_one_matrix_derived_positive_per_outcome():
    matrix = adapter_result_matrix()
    statuses = [item["outcomeId"] for item in matrix["outcomes"]]
    samples = [emit_adapter_result(status).model_dump(exclude_none=True) for status in statuses]
    assert [sample["status"] for sample in samples] == statuses
    assert all(isinstance(AdapterDeliveryResultV1(**sample), AdapterDeliveryResultV1) for sample in samples)


def test_each_positive_rejects_missing_extra_and_attempt_mutations():
    for outcome in adapter_result_matrix()["outcomes"]:
        sample = emit_adapter_result(outcome["outcomeId"]).model_dump(exclude_none=True)
        mutations = []
        missing = copy.deepcopy(sample)
        missing.pop(next(iter(missing)))
        mutations.append(missing)
        mutations.append(sample | {"unexpected": True})
        mutations.append(sample | {"transport_attempted": not sample["transport_attempted"]})
        for value in mutations:
            with pytest.raises(ValidationError):
                AdapterDeliveryResultV1(**value)
