"""SQL P4-E proposal-admission and placement-work storage mixin (SPEC R10-
R12, transactions A/B). Split out of ``p4e_store.py`` for the file-size
guard, same reason ``_report_store.py`` is split out of ``sql_ledger.py``.
Mixed into ``SqlLedger`` alongside ``_P4eStoreMixin`` (both mixins target
the same P4-E tables; this one owns only proposal/placement-work, never
mapping/binding)."""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import insert, select, update

from operations_ledger import p4e_records
from operations_ledger.tables import p4e_placement_decisions, p4e_placement_work, p4e_proposals


class _P4eTransactionStoreMixin:
    # --- durable proposal admission (SPEC R10/R11) ---

    def add_p4e_proposal(self, proposal: dict, *, unit=None):
        """SPEC R11/F3: same key+lineage returns the ACTUAL stored row as
        replay; any changed dimension collides. Insert body lives in
        ``p4e_records.insert_proposal_admission`` (file-size guard)."""
        lineage_digest = p4e_records.proposal_lineage_digest(proposal)
        with self._open(unit) as c:
            existing = c.execute(
                select(p4e_proposals).where(p4e_proposals.c.idempotency_key == proposal["idempotency_key"])
            ).mappings().first()
            if existing is not None:
                if existing["lineage_digest"] != lineage_digest:
                    raise ValueError("lineage collision: idempotency key reused with changed lineage")
                return dict(existing), True
            p4e_records.insert_proposal_admission(c, proposal, lineage_digest, uuid4=uuid4)
            stored = c.execute(
                select(p4e_proposals).where(p4e_proposals.c.proposal_id == proposal["proposal_id"])
            ).mappings().first()
        return dict(stored), False

    def get_p4e_proposal(self, proposal_id: str, *, unit=None) -> dict:
        with self._open(unit) as c:
            row = c.execute(
                select(p4e_proposals).where(p4e_proposals.c.proposal_id == proposal_id)
            ).mappings().first()
        if row is None:
            raise KeyError(proposal_id)
        return dict(row)

    def claim_placement_work(self, proposal_id: str, *, expected_lineage_digest: str, unit=None):
        """SPEC R12/F6: claims PENDING, recovers stale CLAIMED, or returns
        an unclaimed row at the exact 3-attempt exhaustion boundary -
        decision logic lives in ``p4e_records.claimable_decision``."""
        with self._open(unit) as c:
            row = c.execute(
                select(p4e_placement_work).where(p4e_placement_work.c.proposal_id == proposal_id)
            ).mappings().first()
            if row is None:
                raise KeyError(proposal_id)
            if row["lineage_digest"] != expected_lineage_digest:
                raise ValueError(f"stale proposal lineage: proposal {proposal_id} changed before claim")
            decision = p4e_records.claimable_decision(row, now=self._p4e_clock())
            if decision != "CLAIM":
                if decision in ("EXHAUSTED", "UNKNOWN_STATE"):
                    terminal = dict(row)
                    terminal["_terminal_reason"] = decision
                    return terminal
                return None
            token = str(uuid4())
            result = c.execute(
                update(p4e_placement_work)
                .where(
                    p4e_placement_work.c.work_item_id == row["work_item_id"],
                    p4e_placement_work.c.version == row["version"],
                    p4e_placement_work.c.lineage_digest == expected_lineage_digest,
                )
                .values(state="CLAIMED", claim_token=token, claimed_at=self._p4e_clock(),
                        attempt_count=row["attempt_count"] + 1, version=row["version"] + 1)
            )
            if result.rowcount == 0:
                return None
            claimed = c.execute(
                select(p4e_placement_work).where(p4e_placement_work.c.work_item_id == row["work_item_id"])
            ).mappings().first()
        return dict(claimed)

    def complete_placement_work(
        self, proposal_id: str, decision: dict, *, expected_version: int, claim_token: str,
        expected_lineage_digest: str, unit=None,
    ):
        """completion-rereview R3: CAS-owned by the EXACT claim held -
        proposal id alone is not ownership."""
        with self._open(unit) as c:
            result = c.execute(
                update(p4e_placement_work)
                .where(
                    p4e_placement_work.c.proposal_id == proposal_id,
                    p4e_placement_work.c.state == "CLAIMED",
                    p4e_placement_work.c.version == expected_version,
                    p4e_placement_work.c.claim_token == claim_token,
                    p4e_placement_work.c.lineage_digest == expected_lineage_digest,
                )
                .values(state="COMPLETE", version=expected_version + 1)
            )
            if result.rowcount == 0:
                raise ValueError(f"stale claim ownership: proposal {proposal_id} is not held by this claim")
            c.execute(insert(p4e_placement_decisions).values(**p4e_records.decision_row(decision)))

    def rollback_placement_work(
        self, proposal_id: str, *, expected_version: int, claim_token: str,
        expected_lineage_digest: str, unit=None,
    ):
        """completion-rereview R3: rollback is CAS-owned too; clears claim
        ownership so the next real claim starts clean."""
        with self._open(unit) as c:
            result = c.execute(
                update(p4e_placement_work)
                .where(
                    p4e_placement_work.c.proposal_id == proposal_id,
                    p4e_placement_work.c.state == "CLAIMED",
                    p4e_placement_work.c.version == expected_version,
                    p4e_placement_work.c.claim_token == claim_token,
                    p4e_placement_work.c.lineage_digest == expected_lineage_digest,
                )
                .values(state="PENDING", claim_token=None, claimed_at=None, version=expected_version + 1)
            )
            if result.rowcount == 0:
                raise ValueError(f"stale claim ownership: proposal {proposal_id} is not held by this claim")

    def complete_unclaimed_placement_work(
        self, proposal_id: str, decision: dict, *, expected_version: int,
        expected_lineage_digest: str, unit=None,
    ):
        """completion-rereview R3: the EXHAUSTED/UNKNOWN_STATE path -
        ``claim_placement_work`` returns these rows WITHOUT claiming them,
        so this CASes on the observed version and lineage and can never target a
        ``CLAIMED`` row (that is ``complete_placement_work``'s CAS only)."""
        with self._open(unit) as c:
            result = c.execute(
                update(p4e_placement_work)
                .where(
                    p4e_placement_work.c.proposal_id == proposal_id,
                    p4e_placement_work.c.state != "CLAIMED",
                    p4e_placement_work.c.version == expected_version,
                    p4e_placement_work.c.lineage_digest == expected_lineage_digest,
                )
                .values(state="COMPLETE", version=expected_version + 1)
            )
            if result.rowcount == 0:
                raise ValueError(f"stale claim ownership: proposal {proposal_id} is not held by this claim")
            c.execute(insert(p4e_placement_decisions).values(**p4e_records.decision_row(decision)))
