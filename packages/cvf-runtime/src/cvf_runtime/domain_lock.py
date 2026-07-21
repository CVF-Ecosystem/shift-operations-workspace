"""Domain lock.

CVF control: ``domain_lock``. Work must stay inside the domains the profile
allows (domain-lock.yaml). Anything outside is refused and routed, never
silently accepted. This is the code form of "giới hạn trong các domain đã cho
phép; out_of_scope_behavior: refuse_and_route".
"""

from __future__ import annotations

from cvf_runtime.errors import CvfDenied
from cvf_runtime.policy_loader import CvfProfile

# Maps concrete operational event types to a governed domain. Event types not
# listed here resolve to no domain and are refused by the gate, which is the
# safe (fail-closed) default.
_EVENT_TYPE_DOMAIN: dict[str, str] = {
    "equipment_downtime": "equipment_incident",
    "equipment_restored": "equipment_incident",
    "vessel_status": "vessel_operation",
    "production_update": "vessel_operation",
    "yard_status": "yard_operation",
    "incident": "equipment_incident",
    "customer_request": "customer_request",
    "handover": "shift_handover",
    "shift_update": "shift_operation",
    "end_shift_report": "end_shift_reporting",
}


def domain_for_event_type(event_type: str) -> str | None:
    return _EVENT_TYPE_DOMAIN.get(event_type)


def assert_domain_allowed(profile: CvfProfile, domain: str | None) -> None:
    """Raise :class:`CvfDenied` if ``domain`` is not an allowed domain."""
    allowed = set(profile.domain_lock.get("allowed_domains", []))
    if domain is None or domain not in allowed:
        raise CvfDenied(
            control="domain_lock",
            reason=(
                f"domain {domain!r} is out of scope; "
                f"{profile.domain_lock.get('out_of_scope_behavior', 'refuse_and_route')}"
            ),
            http_status=422,
        )


def assert_event_type_in_scope(profile: CvfProfile, event_type: str) -> None:
    """Convenience: resolve an event type to its domain and enforce the lock."""
    assert_domain_allowed(profile, domain_for_event_type(event_type))
