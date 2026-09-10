"""``P4ePlacementProcessor`` (SPEC R10-R12): the transaction-B local
processing attempt, invoked once synchronously after transaction A commits
the admitted proposal. Split out of ``p4e_placement.py`` for the file-size
guard (completion-rereview R3's claim-owner CAS pass-through grew that
file past the 300-line hard limit)."""

from __future__ import annotations

from uuid import uuid4

from conversation_routing import ConversationRoutingService
from conversation_routing.models import PlacementDecisionReceipt
from operations_ledger import Ledger
from operations_ledger.p4e_records import proposal_lineage_digest

from workspace_api.application._p4e_target_eligibility import LedgerTargetEligibility


class P4ePlacementProcessor:
    """SPEC R10-R12: the transaction-B local processing attempt, invoked
    once synchronously after transaction A commits the admitted proposal."""

    def __init__(self, ledger: Ledger, workspace_digest: str, key_port, *, legacy_sender_evidence=False) -> None:
        self.ledger = ledger
        self.workspace_digest = workspace_digest
        self.key_port = key_port
        self.legacy_sender_evidence = legacy_sender_evidence

    def process(self, proposal_id: str) -> PlacementDecisionReceipt | None:
        """Returns the decision on success/terminal-refusal, or ``None`` if
        the work item was already complete or is not yet claimable (a
        concurrent processor holds it) - never a placement decision without
        a claimed work item."""
        with self.ledger.transaction() as unit:
            proposal = self.ledger.get_p4e_proposal(proposal_id, unit=unit)
            expected_lineage_digest = proposal_lineage_digest(proposal)
            work = self.ledger.claim_placement_work(
                proposal_id, expected_lineage_digest=expected_lineage_digest, unit=unit,
            )
            if work is None:
                return None
            # completion-review F6: claim_placement_work signals a
            # terminal (non-claimable-but-decidable) row via
            # ``_terminal_reason`` - exact 3-attempt exhaustion boundary or
            # an unknown/corrupt state, each its own closed outcome.
            # completion-rereview R3: these rows were never claimed (no
            # token/version bump), so they complete via the unclaimed CAS
            # path, CAS-bound to the exact version this call observed.
            terminal_reason = work.get("_terminal_reason")
            if terminal_reason == "UNKNOWN_STATE":
                decision = self._terminal("REFUSED", "UNKNOWN_CLAIM_STATE", proposal_id)
                self.ledger.complete_unclaimed_placement_work(
                    proposal_id, decision.model_dump(exclude_none=True),
                    expected_version=work["version"],
                    expected_lineage_digest=work["lineage_digest"], unit=unit,
                )
                return decision
            if terminal_reason == "EXHAUSTED":
                decision = self._terminal("REFUSED", "RETRY_EXHAUSTED", proposal_id)
                self.ledger.complete_unclaimed_placement_work(
                    proposal_id, decision.model_dump(exclude_none=True),
                    expected_version=work["version"],
                    expected_lineage_digest=work["lineage_digest"], unit=unit,
                )
                return decision

            # SPEC R12/completion-review F6: CAS the exact proposal-lineage
            # digest the work item was created against, against the
            # proposal's CURRENT lineage digest - a mismatch (the proposal
            # row somehow diverged from what admission recorded) is a
            # closed terminal refusal, never silently processed. This row
            # WAS claimed (it reached CLAIM, not a terminal reason above),
            # so completion is via the claim-owned CAS with the exact
            # token/version/lineage this call's own claim returned.
            if proposal_lineage_digest(proposal) != work.get("lineage_digest"):
                decision = self._terminal("REFUSED", "LINEAGE_DIGEST_MISMATCH", proposal_id)
                self.ledger.complete_placement_work(
                    proposal_id, decision.model_dump(exclude_none=True), expected_version=work["version"],
                    claim_token=work["claim_token"], expected_lineage_digest=work["lineage_digest"], unit=unit,
                )
                return decision
            external_key_digest = None
            sender_evidence = proposal.get("sender_evidence")
            if sender_evidence:
                from identity_mapping.models import ExternalIdentityKeyV1

                key = ExternalIdentityKeyV1(**{
                    k: sender_evidence[k] for k in (
                        "workspace_digest", "endpoint_id", "channel_id", "provider_account_digest",
                        "subject_kind", "extraction_policy_id", "extraction_policy_version",
                        "verification_scheme", "verification_version", "sender_token",
                        "token_key_id", "token_key_version",
                    )
                })
                external_key_digest = key.digest()

            # ConversationRoutingService's first argument is an
            # IdentityMappingReadPort (get_current_mapping only) - the
            # Ledger itself satisfies that structurally via _P4eStoreMixin,
            # so no separate identity-service instance is passed here.
            eligibility = LedgerTargetEligibility(self.ledger, self.workspace_digest, unit=unit)
            routing = ConversationRoutingService(
                self.ledger, self.ledger, eligibility,
                legacy_sender_evidence=self.legacy_sender_evidence,
            )
            try:
                decision = routing.place(proposal_id=proposal_id, external_key_digest=external_key_digest, unit=unit)
            except Exception:
                self.ledger.rollback_placement_work(
                    proposal_id, expected_version=work["version"], claim_token=work["claim_token"],
                    expected_lineage_digest=work["lineage_digest"], unit=unit,
                )
                raise
            self.ledger.complete_placement_work(
                proposal_id, decision.model_dump(exclude_none=True), expected_version=work["version"],
                claim_token=work["claim_token"], expected_lineage_digest=work["lineage_digest"], unit=unit,
            )
        return decision

    def _terminal(self, outcome, reason, proposal_id) -> PlacementDecisionReceipt:
        return PlacementDecisionReceipt(
            outcome=outcome, reason=reason, decision_id=str(uuid4()), proposal_id=proposal_id,
            decision_count=1, work_complete=True,
        )
