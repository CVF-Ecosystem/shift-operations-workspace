import json
from pathlib import Path
import pytest
from integration_edge.invariants import emit_ingress_terminal_receipt,emit_outbound_terminal_receipt

ROOT=Path(__file__).resolve().parents[2]
MATRICES=(("p4c-ingress-terminal-outcomes.json",emit_ingress_terminal_receipt),("p4c-outbound-terminal-outcomes.json",emit_outbound_terminal_receipt))

def _positive(shape):
    result={}
    for field in shape["requiredFields"]:
        domain=shape["fieldDomains"][field]
        result[field]=domain.get("const",domain.get("enum",[1 if domain["type"]=="INTEGER" else "x"])[0])
    return result

@pytest.mark.parametrize("filename,emitter",MATRICES)
def test_raw_real_emitter_positive_per_outcome(filename,emitter):
    matrix=json.loads((ROOT/"docs/cvf/invariants"/filename).read_text())
    for outcome in matrix["outcomes"]:
        raw=_positive(outcome["shapes"][0]); emitted=emitter(raw.pop("outcome"),**raw)
        assert emitted.model_dump(exclude_none=True)=={"outcome":outcome["outcomeId"],**raw}

@pytest.mark.parametrize("filename,emitter",MATRICES)
def test_matrix_mutations_rejected(filename,emitter):
    matrix=json.loads((ROOT/"docs/cvf/invariants"/filename).read_text())
    for outcome in matrix["outcomes"]:
        raw=_positive(outcome["shapes"][0]); raw.pop(outcome["shapes"][0]["requiredFields"][-1])
        with pytest.raises(Exception):emitter(raw.pop("outcome"),**raw)
