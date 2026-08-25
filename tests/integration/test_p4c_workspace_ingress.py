import pytest
from workspace_api.external_ingress.models import ExternalIngressProposalInput
from workspace_api.external_ingress.repository import InMemoryExternalIngressRepository
from workspace_api.external_ingress.service import ExternalIngressService

def payload():return ExternalIngressProposalInput(envelope_id="e",channel="ch",external_id="x",candidate={"type":"note"},provenance_digest="a"*64)

def test_actor_neutral_proposal_never_creates_business_truth():
    repo=InMemoryExternalIngressRepository(); service=ExternalIngressService(repo,lambda *a,**k:True); result=service.propose(payload(),"assert")
    assert result.trust_class=="UNTRUSTED_EXTERNAL" and result.content_class=="RAW" and result.confirmed is False
    assert result.actor_id is result.assignment_id is result.approval_id is result.conversation_id is None

def test_assertion_refusal_has_zero_proposals():
    repo=InMemoryExternalIngressRepository()
    def refuse(*a,**k):raise PermissionError
    with pytest.raises(PermissionError):ExternalIngressService(repo,refuse).propose(payload(),"bad")
    assert repo.records=={}
