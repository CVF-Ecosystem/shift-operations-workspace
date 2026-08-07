import json
from pathlib import Path
from typing import Annotated

from pydantic import Field, TypeAdapter

from retrieval_contracts.contract_models import RetrievalNonAdmissionV1, RetrievalReadyV1

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "packages" / "retrieval-contracts" / "contracts" / "retrieval_contract.schema.json"
ResultUnion = Annotated[
    RetrievalReadyV1 | RetrievalNonAdmissionV1,
    Field(discriminator="kind"),
]


def generated_schema_bytes() -> bytes:
    schema = TypeAdapter(ResultUnion).json_schema()
    return (json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def test_committed_schema_matches_fresh_generation_byte_for_byte() -> None:
    assert SCHEMA.read_bytes() == generated_schema_bytes()


def test_result_union_is_discriminated_and_closed() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["discriminator"]["propertyName"] == "kind"
    assert set(schema["discriminator"]["mapping"]) == {"NOT_ADMITTED", "RETRIEVAL_READY"}
    for definition in schema["$defs"].values():
        if definition.get("type") == "object":
            assert definition.get("additionalProperties") is False
