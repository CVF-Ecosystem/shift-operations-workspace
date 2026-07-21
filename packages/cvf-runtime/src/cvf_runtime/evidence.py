"""Evidence gate.

CVF control: ``evidence``. Enforces evidence-policy.yaml: an event cannot be
confirmed as official operational fact unless it carries at least the minimum
number of evidence links its risk class requires (R2>=1, R3>=1, R4>=2).

This is the code form of the architecture rule "raw message does not
automatically become a confirmed fact" and "prohibit_unlinked_official_fact".
"""

from __future__ import annotations

from cvf_runtime.errors import CvfDenied
from cvf_runtime.policy_loader import CvfProfile
from cvf_runtime.risk import requirement_for


def assert_evidence_sufficient(
    *, profile: CvfProfile, risk_class: str, evidence_count: int
) -> None:
    """Raise :class:`CvfDenied` if evidence is below the required minimum."""
    requirement = requirement_for(profile, risk_class)
    if evidence_count < requirement.min_evidence:
        raise CvfDenied(
            control="evidence",
            reason=(
                f"{risk_class} requires at least {requirement.min_evidence} "
                f"evidence link(s); found {evidence_count}"
            ),
            http_status=409,
        )
