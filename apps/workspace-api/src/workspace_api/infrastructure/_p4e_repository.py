"""In-memory P4-E storage mixin (completion-review F8/AC-05: InMemory
parity alongside ``_P4eStoreMixin``'s SQLite/PostgreSQL implementation).
Same method surface, same CAS/uniqueness/lineage semantics, reusing the
identical backend-agnostic decision functions from
``operations_ledger.p4e_records`` so both backends can never silently
diverge on exhaustion boundary, lineage digest, or row shape."""

from __future__ import annotations

from threading import RLock
from uuid import uuid4

from operations_ledger import p4e_records


class _InMemoryP4eRepositoryMixin:
    def _p4e_init(self) -> None:
        self._p4e_lock = RLock()
        self._p4e_observations: dict[str, object] = {}
        self._p4e_mappings: dict[str, object] = {}
        self._p4e_bindings: dict[str, object] = {}
        self._p4e_proposals: dict[str, dict] = {}
        self._p4e_work: dict[str, dict] = {}
        self._p4e_decisions: dict[str, dict] = {}
        self._p4e_receipts: dict[str, dict] = {}

    # --- identity_mapping.ports.IdentityMappingRepositoryPort ---

    def add_observation(self, observation, *, unit=None):
        with self._p4e_lock:
            for existing in self._p4e_observations.values():
                if (existing.external_key_digest == observation.external_key_digest
                        and existing.raw_envelope_id == observation.raw_envelope_id):
                    raise ValueError(f"duplicate observation lineage: {observation.observation_id}")
            self._p4e_observations[observation.observation_id] = observation
        return observation

    def list_observations(self, *, unit=None) -> list:
        with self._p4e_lock:
            return list(self._p4e_observations.values())

    def get_observation(self, observation_id: str, *, unit=None):
        with self._p4e_lock:
            if observation_id not in self._p4e_observations:
                raise KeyError(observation_id)
            return self._p4e_observations[observation_id]

    def get_current_mapping(self, external_key_digest: str, *, unit=None):
        with self._p4e_lock:
            current = [m for m in self._p4e_mappings.values()
                       if m.external_key_digest == external_key_digest and m.status == "CONFIRMED"
                       and self._p4e_is_current_mapping(m)]
        if len(current) == 0:
            return None
        if len(current) > 1:
            raise ValueError(f"multiple current mappings for key digest {external_key_digest}")
        return current[0]

    def _p4e_is_current_mapping(self, mapping) -> bool:
        return mapping.status == "CONFIRMED" and not any(
            other.predecessor_mapping_id == mapping.mapping_id for other in self._p4e_mappings.values()
        )

    def get_mapping(self, mapping_id: str, *, unit=None):
        with self._p4e_lock:
            if mapping_id not in self._p4e_mappings:
                raise KeyError(mapping_id)
            return self._p4e_mappings[mapping_id]

    def propose_mapping(self, mapping, *, unit=None):
        with self._p4e_lock:
            self._p4e_mappings[mapping.mapping_id] = mapping
        return mapping

    def _p4e_cas_mapping(self, mapping_id, *, expected_version, updates: dict):
        with self._p4e_lock:
            current = self._p4e_mappings.get(mapping_id)
            if current is None:
                raise KeyError(mapping_id)
            if current.version != expected_version:
                raise ValueError(f"stale mapping version: expected {expected_version}")
            updated = current.model_copy(update={
                **updates, "version": expected_version + 1, "updated_at": self._p4e_clock(),
            })
            self._p4e_mappings[mapping_id] = updated
            return updated

    def confirm_mapping(self, mapping_id, *, expected_version, confirmer_id, predecessor_mapping_id=None, unit=None):
        with self._p4e_lock:
            target = self._p4e_mappings.get(mapping_id)
            if target is None:
                raise KeyError(mapping_id)
            conflict = self.get_current_mapping(target.external_key_digest)
            if conflict is not None and conflict.mapping_id != mapping_id:
                raise ValueError("current mapping conflict: another mapping is already current")
            if predecessor_mapping_id is not None:
                predecessor = self._p4e_mappings.get(predecessor_mapping_id)
                if predecessor is None or predecessor.status != "CONFIRMED":
                    raise ValueError(f"predecessor is not confirmed-current: {predecessor_mapping_id}")
                self._p4e_mappings[predecessor_mapping_id] = predecessor.model_copy(update={
                    "status": "REVOKED", "revoker_id": confirmer_id, "updated_at": self._p4e_clock(),
                })
            return self._p4e_cas_mapping(
                mapping_id, expected_version=expected_version,
                updates={"status": "CONFIRMED", "confirmer_id": confirmer_id},
            )

    def reject_mapping(self, mapping_id, *, expected_version, rejector_id, unit=None):
        return self._p4e_cas_mapping(
            mapping_id, expected_version=expected_version,
            updates={"status": "REJECTED", "rejector_id": rejector_id},
        )

    def revoke_mapping(self, mapping_id, *, expected_version, revoker_id, unit=None):
        return self._p4e_cas_mapping(
            mapping_id, expected_version=expected_version,
            updates={"status": "REVOKED", "revoker_id": revoker_id},
        )

    def privacy_delete_mapping(self, mapping_id, *, expected_version, unit=None):
        """completion-review F8: NULL, not a sentinel string - matches the
        SQL backend's real nullable foreign-key semantics exactly."""
        return self._p4e_cas_mapping(
            mapping_id, expected_version=expected_version,
            updates={"status": "REVOKED", "target_user_id": None},
        )

    # --- conversation_routing.ports.RouteBindingRepositoryPort ---

    def get_binding(self, binding_id: str, *, unit=None):
        with self._p4e_lock:
            if binding_id not in self._p4e_bindings:
                raise KeyError(binding_id)
            return self._p4e_bindings[binding_id]

    def get_current_binding(self, mapping_id: str, *, unit=None):
        with self._p4e_lock:
            current = [b for b in self._p4e_bindings.values()
                       if b.mapping_id == mapping_id and b.status == "ACTIVE"]
        if len(current) == 0:
            return None
        if len(current) > 1:
            raise ValueError(f"multiple current bindings for mapping {mapping_id}")
        return current[0]

    def create_binding(self, binding, *, unit=None):
        with self._p4e_lock:
            if self.get_current_binding(binding.mapping_id) is not None:
                raise ValueError(f"current binding conflict for mapping {binding.mapping_id}")
            self._p4e_bindings[binding.binding_id] = binding
        return binding

    def replace_binding(
        self, old_binding_id: str, successor, *, expected_binding_version: int, unit=None,
    ):
        """SPEC R13: revoke-then-insert, same order as the SQL backend, so
        the old binding vacates the current-binding slot before the
        successor's own uniqueness is checked (F8 parity bug found by
        ``test_p4e_inmemory_parity.py``: checking the conflict before
        revoking always self-collided against the row being replaced)."""
        with self._p4e_lock:
            old = self._p4e_bindings.get(old_binding_id)
            if (old is None or old.status != "ACTIVE"
                    or old.version != expected_binding_version):
                raise ValueError(f"stale binding version or non-current binding: {old_binding_id}")
            self._p4e_bindings[old_binding_id] = old.model_copy(
                update={
                    "status": "REVOKED",
                    "successor_binding_id": successor.binding_id,
                    "version": expected_binding_version + 1,
                }
            )
            if self.get_current_binding(successor.mapping_id) is not None:
                raise ValueError(f"current binding conflict for mapping {successor.mapping_id}")
            self._p4e_bindings[successor.binding_id] = successor
        return successor

    # --- durable proposal admission (SPEC R10/R11) ---

    def add_p4e_proposal(self, proposal: dict, *, unit=None):
        lineage_digest = p4e_records.proposal_lineage_digest(proposal)
        with self._p4e_lock:
            for existing in self._p4e_proposals.values():
                if existing["idempotency_key"] == proposal["idempotency_key"]:
                    if existing["lineage_digest"] != lineage_digest:
                        raise ValueError("lineage collision: idempotency key reused with changed lineage")
                    return dict(existing), True
                if existing["envelope_id"] == proposal["envelope_id"]:
                    raise ValueError("lineage collision: proposal/envelope identity reused")
            stored = dict(proposal, lineage_digest=lineage_digest)
            self._p4e_proposals[proposal["proposal_id"]] = stored
            if proposal.get("sender_evidence"):
                observation_row = p4e_records.observation_from_sender_evidence(
                    str(uuid4()), proposal["sender_evidence"]
                )
                for existing in self._p4e_observations.values():
                    if (existing.external_key_digest == observation_row["external_key_digest"]
                            and existing.raw_envelope_id == observation_row["raw_envelope_id"]):
                        raise ValueError("duplicate observation lineage on proposal admission")
                from identity_mapping import SenderObservationV1

                obs = SenderObservationV1(**observation_row)
                self._p4e_observations[obs.observation_id] = obs
            work_item_id = str(uuid4())
            self._p4e_work[proposal["proposal_id"]] = {
                "work_item_id": work_item_id, "proposal_id": proposal["proposal_id"],
                "state": "PENDING", "attempt_count": 0, "claim_token": None,
                "claimed_at": None, "version": 1, "lineage_digest": lineage_digest,
            }
        return dict(stored), False

    def get_p4e_proposal(self, proposal_id: str, *, unit=None) -> dict:
        with self._p4e_lock:
            if proposal_id not in self._p4e_proposals:
                raise KeyError(proposal_id)
            return dict(self._p4e_proposals[proposal_id])

    def claim_placement_work(self, proposal_id: str, *, expected_lineage_digest: str, unit=None):
        with self._p4e_lock:
            row = self._p4e_work.get(proposal_id)
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
            row["state"] = "CLAIMED"
            row["claim_token"] = str(uuid4())
            row["claimed_at"] = self._p4e_clock()
            row["attempt_count"] = row["attempt_count"] + 1
            row["version"] = row["version"] + 1
            return dict(row)

    def complete_placement_work(
        self, proposal_id: str, decision: dict, *, expected_version: int, claim_token: str,
        expected_lineage_digest: str, unit=None,
    ):
        """completion-rereview R3: identical CAS-owned semantics as the SQL
        backend - state/version/token/lineage must all match the exact
        claim, or this is a closed conflict, never a silent completion."""
        with self._p4e_lock:
            work = self._p4e_work.get(proposal_id)
            if (work is None or work["state"] != "CLAIMED" or work["version"] != expected_version
                    or work["claim_token"] != claim_token or work["lineage_digest"] != expected_lineage_digest):
                raise ValueError(f"stale claim ownership: proposal {proposal_id} is not held by this claim")
            work["state"] = "COMPLETE"
            work["version"] = expected_version + 1
            self._p4e_decisions[proposal_id] = dict(decision)

    def rollback_placement_work(
        self, proposal_id: str, *, expected_version: int, claim_token: str,
        expected_lineage_digest: str, unit=None,
    ):
        """completion-rereview R3: rollback is CAS-owned by the exact claim
        too; clears claim ownership so the next real claim starts clean."""
        with self._p4e_lock:
            work = self._p4e_work.get(proposal_id)
            if (work is None or work["state"] != "CLAIMED" or work["version"] != expected_version
                    or work["claim_token"] != claim_token
                    or work["lineage_digest"] != expected_lineage_digest):
                raise ValueError(f"stale claim ownership: proposal {proposal_id} is not held by this claim")
            work["state"] = "PENDING"
            work["claim_token"] = None
            work["claimed_at"] = None
            work["version"] = expected_version + 1

    def complete_unclaimed_placement_work(
        self, proposal_id: str, decision: dict, *, expected_version: int,
        expected_lineage_digest: str, unit=None,
    ):
        """Complete only the exact unclaimed work row previously observed."""
        with self._p4e_lock:
            work = self._p4e_work.get(proposal_id)
            if (work is None or work["state"] == "CLAIMED" or work["version"] != expected_version
                    or work["lineage_digest"] != expected_lineage_digest):
                raise ValueError(f"stale claim ownership: proposal {proposal_id} is not held by this claim")
            work["state"] = "COMPLETE"
            work["version"] = expected_version + 1
            self._p4e_decisions[proposal_id] = dict(decision)

    # --- idempotent action receipts (SPEC R9) ---

    def get_action_receipt(self, idempotency_key: str, *, unit=None) -> dict | None:
        with self._p4e_lock:
            row = self._p4e_receipts.get(idempotency_key)
            return dict(row) if row is not None else None

    def put_action_receipt(self, idempotency_key: str, action: str, payload_digest: str, receipt: dict, *, unit=None):
        with self._p4e_lock:
            if idempotency_key in self._p4e_receipts:
                return
            self._p4e_receipts[idempotency_key] = {
                "idempotency_key": idempotency_key, "action": action,
                "payload_digest": payload_digest, "receipt": receipt,
            }
