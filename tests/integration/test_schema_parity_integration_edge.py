import json
from pathlib import Path
from integration_edge.storage import tables

ROOT=Path(__file__).resolve().parents[2]

def test_migration_and_sqlalchemy_table_names_match():
    sql=(ROOT/"database/migrations/010_integration_edge.sql").read_text()
    names={table.name for table in tables.metadata.tables.values()}
    assert names=={"edge_raw_envelopes","edge_ingress_reservations","edge_quarantines","edge_external_proposals","edge_rate_counters","edge_outbound_attempts"}
    assert all(f"CREATE TABLE IF NOT EXISTS {name}" in sql for name in names)
    assert "messages" not in names and "operational_events" not in names

def test_receipt_schema_outcomes_equal_matrices():
    ingress=json.loads((ROOT/"contracts/channel/edge-ingress.schema.json").read_text()); outbound=json.loads((ROOT/"contracts/channel/edge-outbound.schema.json").read_text())
    im=json.loads((ROOT/"docs/cvf/invariants/p4c-ingress-terminal-outcomes.json").read_text()); om=json.loads((ROOT/"docs/cvf/invariants/p4c-outbound-terminal-outcomes.json").read_text())
    ingress_refs={ref["$ref"].split("/")[-1] for ref in ingress["oneOf"]}
    outbound_refs={ref["$ref"].split("/")[-1] for ref in outbound["oneOf"]}
    assert {x["outcomeId"] for x in im["outcomes"]}<=ingress_refs
    assert {x["outcomeId"] for x in om["outcomes"]}<=outbound_refs
