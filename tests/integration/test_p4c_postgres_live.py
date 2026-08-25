import os
import pytest
from sqlalchemy import create_engine,text

@pytest.mark.skipif(not os.getenv("P4C_POSTGRES_URL"),reason="requires disposable local PostgreSQL runner")
def test_migration_created_postgres_constraints_and_cleanup():
    engine=create_engine(os.environ["P4C_POSTGRES_URL"])
    with engine.begin() as conn:
        names={row[0] for row in conn.execute(text("select tablename from pg_tables where schemaname=current_schema()"))}
        assert {"edge_raw_envelopes","edge_ingress_reservations","edge_quarantines","edge_external_proposals","edge_rate_counters","edge_service_nonces","edge_outbound_attempts"}<=names
        constraints={row[0] for row in conn.execute(text("select constraint_name from information_schema.table_constraints where table_name='edge_raw_envelopes'"))}
        assert "uq_edge_raw_key_nonce" in constraints
    engine.dispose()
