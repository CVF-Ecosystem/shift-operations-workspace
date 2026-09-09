"""SQL P4-E storage mixin. Split out of ``sql_ledger.py`` for the file-size
guard, mirroring ``_report_store.py``/``_handover_store.py``. Uses write-time
CAS/unique-current as sole authority - never a prior SELECT."""

from __future__ import annotations

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError

from operations_ledger import p4e_records
from operations_ledger.tables import (
    external_identity_observations, identity_mappings, p4e_action_receipts, route_bindings,
)


class _P4eStoreMixin:
    # --- identity_mapping.ports.IdentityMappingRepositoryPort ---

    def add_observation(self, observation, *, unit=None):
        with self._open(unit) as c:
            try:
                c.execute(insert(external_identity_observations).values(
                    **p4e_records.observation_row(observation)
                ))
            except IntegrityError as exc:
                raise ValueError(f"duplicate observation lineage: {observation.observation_id}") from exc
        return observation

    def list_observations(self, *, unit=None) -> list:
        """SPEC R17: required observation-listing - selector metadata and
        received time only (R5), never token/raw sender/candidate."""
        with self._open(unit) as c:
            rows = c.execute(select(external_identity_observations)).mappings().all()
        return [p4e_records.row_to_observation(dict(r)) for r in rows]

    def get_observation(self, observation_id: str, *, unit=None):
        with self._open(unit) as c:
            row = c.execute(
                select(external_identity_observations).where(
                    external_identity_observations.c.observation_id == observation_id
                )
            ).mappings().first()
        if row is None:
            raise KeyError(observation_id)
        return p4e_records.row_to_observation(row)

    def get_current_mapping(self, external_key_digest: str, *, unit=None):
        with self._open(unit) as c:
            rows = c.execute(
                select(identity_mappings).where(
                    identity_mappings.c.external_key_digest == external_key_digest,
                    identity_mappings.c.is_current.is_(True),
                )
            ).mappings().all()
        if len(rows) == 0:
            return None
        if len(rows) > 1:
            raise ValueError(f"multiple current mappings for key digest {external_key_digest}")
        return p4e_records.row_to_mapping(rows[0])

    def get_mapping(self, mapping_id: str, *, unit=None):
        with self._open(unit) as c:
            row = c.execute(
                select(identity_mappings).where(identity_mappings.c.mapping_id == mapping_id)
            ).mappings().first()
        if row is None:
            raise KeyError(mapping_id)
        return p4e_records.row_to_mapping(row)

    def propose_mapping(self, mapping, *, unit=None):
        """SPEC R6: not current until confirmed; confirm is the real check."""
        with self._open(unit) as c:
            c.execute(insert(identity_mappings).values(
                **p4e_records.mapping_row(mapping, is_current=False)
            ))
        return mapping

    def _cas_mapping_transition(self, mapping_id, *, expected_version, values, unit):
        with self._open(unit) as c:
            new_version = expected_version + 1
            result = c.execute(
                update(identity_mappings)
                .where(
                    identity_mappings.c.mapping_id == mapping_id,
                    identity_mappings.c.version == expected_version,
                )
                .values(version=new_version, updated_at=self._p4e_clock(), **values)
            )
            if result.rowcount == 0:
                raise ValueError(f"stale mapping version: expected {expected_version}")
            row = c.execute(
                select(identity_mappings).where(identity_mappings.c.mapping_id == mapping_id)
            ).mappings().first()
        return p4e_records.row_to_mapping(row)

    def confirm_mapping(self, mapping_id, *, expected_version, confirmer_id, predecessor_mapping_id=None, unit=None):
        """SPEC R6/section 4: unique-current via the UPDATE's own index; a
        set ``predecessor_mapping_id`` is revoked in the SAME transaction."""
        try:
            with self._open(unit) as c:
                if predecessor_mapping_id is not None:
                    revoked = c.execute(
                        update(identity_mappings)
                        .where(
                            identity_mappings.c.mapping_id == predecessor_mapping_id,
                            identity_mappings.c.status == "CONFIRMED",
                        )
                        .values(status="REVOKED", is_current=False,
                                revoker_id=confirmer_id, updated_at=self._p4e_clock())
                    )
                    if revoked.rowcount == 0:
                        raise ValueError(f"predecessor is not confirmed-current: {predecessor_mapping_id}")
                return self._cas_mapping_transition(
                    mapping_id, expected_version=expected_version,
                    values={"status": "CONFIRMED", "confirmer_id": confirmer_id, "is_current": True},
                    unit=c,
                )
        except IntegrityError as exc:
            raise ValueError("current mapping conflict: another mapping is already current") from exc

    def reject_mapping(self, mapping_id, *, expected_version, rejector_id, unit=None):
        return self._cas_mapping_transition(
            mapping_id, expected_version=expected_version,
            values={"status": "REJECTED", "rejector_id": rejector_id, "is_current": False},
            unit=unit,
        )

    def revoke_mapping(self, mapping_id, *, expected_version, revoker_id, unit=None):
        return self._cas_mapping_transition(
            mapping_id, expected_version=expected_version,
            values={"status": "REVOKED", "revoker_id": revoker_id, "is_current": False},
            unit=unit,
        )

    def privacy_delete_mapping(self, mapping_id, *, expected_version, unit=None):
        """SPEC R19: clears display/actor fields; digest-only lineage stays.
        completion-review F8: NULL, not a sentinel string - target_user_id
        is a real foreign key to users.user_id on both backends."""
        return self._cas_mapping_transition(
            mapping_id, expected_version=expected_version,
            values={"status": "REVOKED", "is_current": False, "target_user_id": None},
            unit=unit,
        )

    # --- conversation_routing.ports.RouteBindingRepositoryPort ---

    def get_binding(self, binding_id: str, *, unit=None):
        with self._open(unit) as c:
            row = c.execute(
                select(route_bindings).where(route_bindings.c.binding_id == binding_id)
            ).mappings().first()
        if row is None:
            raise KeyError(binding_id)
        return p4e_records.row_to_binding(row)

    def get_current_binding(self, mapping_id: str, *, unit=None):
        with self._open(unit) as c:
            rows = c.execute(
                select(route_bindings).where(
                    route_bindings.c.mapping_id == mapping_id,
                    route_bindings.c.is_current.is_(True),
                )
            ).mappings().all()
        if len(rows) == 0:
            return None
        if len(rows) > 1:
            raise ValueError(f"multiple current bindings for mapping {mapping_id}")
        return p4e_records.row_to_binding(rows[0])

    def create_binding(self, binding, *, unit=None):
        with self._open(unit) as c:
            try:
                c.execute(insert(route_bindings).values(
                    **p4e_records.binding_row(binding, is_current=True)
                ))
            except IntegrityError as exc:
                raise ValueError(f"current binding conflict for mapping {binding.mapping_id}") from exc
        return binding

    def replace_binding(
        self, old_binding_id: str, successor, *, expected_binding_version: int, unit=None,
    ):
        """Write-time CAS revokes the exact old version and creates its successor."""
        with self._open(unit) as c:
            result = c.execute(
                update(route_bindings)
                .where(
                    route_bindings.c.binding_id == old_binding_id,
                    route_bindings.c.is_current.is_(True),
                    route_bindings.c.status == "ACTIVE",
                    route_bindings.c.version == expected_binding_version,
                )
                .values(
                    status="REVOKED", is_current=False,
                    successor_binding_id=successor.binding_id,
                    version=expected_binding_version + 1,
                )
            )
            if result.rowcount == 0:
                raise ValueError(f"stale binding version or non-current binding: {old_binding_id}")
            try:
                c.execute(insert(route_bindings).values(
                    **p4e_records.binding_row(successor, is_current=True)
                ))
            except IntegrityError as exc:
                raise ValueError(f"current binding conflict for mapping {successor.mapping_id}") from exc
        return successor

    # --- idempotent action receipts (SPEC R9) ---

    def get_action_receipt(self, idempotency_key: str, *, unit=None) -> dict | None:
        with self._open(unit) as c:
            row = c.execute(
                select(p4e_action_receipts).where(p4e_action_receipts.c.idempotency_key == idempotency_key)
            ).mappings().first()
        return dict(row) if row is not None else None

    def put_action_receipt(self, idempotency_key: str, action: str, payload_digest: str, receipt: dict, *, unit=None):
        with self._open(unit) as c:
            try:
                c.execute(insert(p4e_action_receipts).values(
                    idempotency_key=idempotency_key, action=action,
                    payload_digest=payload_digest, receipt=receipt,
                ))
            except IntegrityError:
                pass
