import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from integration_edge import IngressReceipt,emit_ingress_terminal_receipt

def test_receipt_closed_and_forbidden_absent():
    value=emit_ingress_terminal_receipt("ROUTED",raw_envelope_id="e",preauth_count=1,postauth_count=1,route_attempts=1)
    assert value.model_dump(exclude_none=True)=={"outcome":"ROUTED","raw_envelope_id":"e","preauth_count":1,"postauth_count":1,"route_attempts":1}
    with pytest.raises(ValidationError):IngressReceipt(outcome="ROUTED",raw_envelope_id="e",preauth_count=1,postauth_count=1,route_attempts=1,unknown=True)

def test_contract_schemas_are_closed():
    root=Path(__file__).resolve().parents[2]
    for name in ("service-assertion.schema.json","edge-ingress.schema.json","edge-outbound.schema.json"):
        schema=json.loads((root/"contracts/channel"/name).read_text())
        objects=[schema,*schema.get("$defs",{}).values()]
        assert all(value.get("additionalProperties") is False for value in objects if value.get("type")=="object")
