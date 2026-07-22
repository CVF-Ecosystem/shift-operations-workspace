"""evidence_links read/write helpers, shared by event and task persistence.

Split out of sql_ledger.py to keep that file under the file-size guard.
Evidence is collected once, at record creation, and never rewritten by later
state changes (confirm/correct/transition) - it documents what was known when
the record was made. Previously this had nowhere to persist at all
(EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md Critical Finding #2).
"""

from __future__ import annotations

from sqlalchemy import insert, select

from operations_ledger import _rows
from operations_ledger.tables import evidence_links


def insert_evidence(conn, evidence_refs, *, record_type: str, record_id) -> None:
    for ref in evidence_refs:
        conn.execute(
            insert(evidence_links).values(
                **_rows.evidence_link_row(ref, record_type=record_type, record_id=record_id)
            )
        )


def evidence_for(conn, models, *, record_type: str, record_id) -> list:
    rows = conn.execute(
        select(evidence_links).where(
            evidence_links.c.record_type == record_type,
            evidence_links.c.record_id == record_id,
        )
    ).mappings().all()
    return [_rows.row_to_evidence_ref(models, r) for r in rows]
