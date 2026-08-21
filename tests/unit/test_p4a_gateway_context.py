"""P4-A SPEC R5/R10/R11 - context admission and dispatched-facts binding.

NOT GOVERNANCE PROOF: mechanical admission tests. The R13 live run is the
governance proof that these refusals produce zero provider attempts in practice.
"""

from __future__ import annotations

import pytest

from ai_gateway.context import (
    assert_context_admissible,
    assert_context_digest_matches,
    assert_provider_identity_matches,
    canonicalize_endpoint_origin,
)
from ai_gateway.errors import (
    ContextDigestMismatchError,
    ContextInadmissibleError,
    EndpointOriginError,
    NoEvidenceError,
    ProviderIdentityMismatchError,
)
from ai_gateway.models import Classification, ContextFacts, GatewayRequest, Placement, digest_of

DIGEST = "a" * 64


def _facts(**overrides) -> ContextFacts:
    base = dict(
        classification=Classification.PUBLIC,
        redaction_applied=True,
        minimization_proven=False,
        evidence_count=1,
        estimated_input_tokens=10,
        context_digest=DIGEST,
    )
    base.update(overrides)
    return ContextFacts(**base)


class TestEvidence:
    def test_zero_evidence_refused_for_every_placement(self):
        for placement in Placement:
            with pytest.raises(NoEvidenceError):
                assert_context_admissible(_facts(evidence_count=0), placement)


class TestPublicExternal:
    def test_public_with_redaction_admitted(self):
        assert_context_admissible(_facts(), Placement.EXTERNAL)

    def test_public_without_redaction_refused(self):
        with pytest.raises(ContextInadmissibleError):
            assert_context_admissible(_facts(redaction_applied=False), Placement.EXTERNAL)


class TestInternalExternal:
    def test_internal_without_minimization_refused(self):
        """The exact P4-A1 handoff shape: NOT_PROVEN minimization fails closed."""
        facts = _facts(classification=Classification.INTERNAL, minimization_proven=False)
        with pytest.raises(ContextInadmissibleError):
            assert_context_admissible(facts, Placement.EXTERNAL)

    def test_internal_without_redaction_refused(self):
        facts = _facts(
            classification=Classification.INTERNAL,
            redaction_applied=False,
            minimization_proven=True,
        )
        with pytest.raises(ContextInadmissibleError):
            assert_context_admissible(facts, Placement.EXTERNAL)

    def test_internal_with_proven_minimization_admitted(self):
        facts = _facts(classification=Classification.INTERNAL, minimization_proven=True)
        assert_context_admissible(facts, Placement.EXTERNAL)


class TestForbiddenClassifications:
    def test_confidential_refused_externally(self):
        facts = _facts(classification=Classification.CONFIDENTIAL, minimization_proven=True)
        with pytest.raises(ContextInadmissibleError):
            assert_context_admissible(facts, Placement.EXTERNAL)

    def test_restricted_refused_externally(self):
        facts = _facts(classification=Classification.RESTRICTED, minimization_proven=True)
        with pytest.raises(ContextInadmissibleError):
            assert_context_admissible(facts, Placement.EXTERNAL)

    def test_confidential_allowed_for_local_admission(self):
        """Admission defers to the placement gate for non-external targets."""
        facts = _facts(classification=Classification.CONFIDENTIAL, redaction_applied=False)
        assert_context_admissible(facts, Placement.LOCAL)
        assert_context_admissible(facts, Placement.ENTERPRISE)


class TestNonExternalPlacements:
    def test_local_does_not_require_redaction(self):
        assert_context_admissible(_facts(redaction_applied=False), Placement.LOCAL)

    def test_enterprise_does_not_require_minimization(self):
        facts = _facts(classification=Classification.INTERNAL, minimization_proven=False)
        assert_context_admissible(facts, Placement.ENTERPRISE)


class TestContextDigestBinding:
    """P4A-REV-F3: the receipt must bind the digest of what was actually sent."""

    def test_matching_digest_accepted(self):
        context = {"note": "hello"}
        facts = _facts(context_digest=digest_of(context))
        assert_context_digest_matches(context, facts)

    def test_declared_digest_for_different_content_is_rejected(self):
        """Reviewer probe: caller declares a clean digest but sends real content."""
        declared_clean = {"note": "nothing sensitive"}
        actually_sent = {"note": "nothing sensitive", "secret": "leaked-value"}
        facts = _facts(context_digest=digest_of(declared_clean))
        with pytest.raises(ContextDigestMismatchError):
            assert_context_digest_matches(actually_sent, facts)

    def test_empty_vs_nonempty_context_is_rejected(self):
        facts = _facts(context_digest=digest_of({}))
        with pytest.raises(ContextDigestMismatchError):
            assert_context_digest_matches({"a": 1}, facts)


class TestProviderIdentityBinding:
    """P4A-REV-F3: a result must claim the provider/model actually dispatched."""

    def _request(self) -> GatewayRequest:
        from ai_gateway.models import AIMode, BudgetFacts, TerminationFacts

        return GatewayRequest(
            task_type="t",
            ai_mode=AIMode.EXTERNAL_AI,
            provider_id="real-provider",
            model_id="real-model",
            placement=Placement.EXTERNAL,
            context={},
            output_schema={"type": "object"},
            context_facts=_facts(context_digest=digest_of({})),
            budget_facts=BudgetFacts(
                per_request_token_limit=100,
                daily_budget_usd_millis=0,
                monthly_budget_usd_millis=0,
                spent_today_usd_millis=0,
                spent_month_usd_millis=0,
                estimated_cost_usd_millis=0,
            ),
            termination_facts=TerminationFacts(),
        )

    def test_matching_identity_accepted(self):
        assert_provider_identity_matches("real-provider", "real-model", self._request())

    def test_different_provider_id_rejected(self):
        """Reviewer probe: a returned result claiming another provider."""
        with pytest.raises(ProviderIdentityMismatchError):
            assert_provider_identity_matches("impersonator", "real-model", self._request())

    def test_different_model_id_rejected(self):
        with pytest.raises(ProviderIdentityMismatchError):
            assert_provider_identity_matches("real-provider", "other-model", self._request())


class TestEndpointOriginCanonicalization:
    """P4A-REV-F3: origin must reduce to bare scheme+host; unsafe input refused."""

    def test_bare_https_origin_passthrough(self):
        assert canonicalize_endpoint_origin("https://api.example.com") == "https://api.example.com"

    def test_strips_path_query_fragment(self):
        raw = "https://api.example.com/v1/chat?key=abc#frag"
        assert canonicalize_endpoint_origin(raw) == "https://api.example.com"

    def test_userinfo_bearing_origin_is_rejected_not_silently_stripped(self):
        """Reviewer probe: origin containing userinfo/credentials/secret value.

        Rejecting (rather than silently stripping) is the stricter, correct
        behavior: a caller passing credentials in an origin string is itself a
        defect that should surface, not be quietly absorbed into a receipt.
        """
        raw = "https://svc:sk-live-abcdef1234567890@internal.example.com/v1?token=sk-abcdef1234567890"
        with pytest.raises(EndpointOriginError):
            canonicalize_endpoint_origin(raw)

    def test_userinfo_only_no_path_still_rejected_as_unsafe_if_malformed(self):
        with pytest.raises(EndpointOriginError):
            canonicalize_endpoint_origin("https://user:pass@")

    def test_non_http_scheme_rejected(self):
        with pytest.raises(EndpointOriginError):
            canonicalize_endpoint_origin("ftp://files.example.com")

    def test_empty_origin_passes_through_as_empty(self):
        """A pre-dispatch refusal receipt has no endpoint yet."""
        assert canonicalize_endpoint_origin("") == ""

    def test_port_is_preserved(self):
        assert canonicalize_endpoint_origin("https://api.example.com:8443/x") == (
            "https://api.example.com:8443"
        )
