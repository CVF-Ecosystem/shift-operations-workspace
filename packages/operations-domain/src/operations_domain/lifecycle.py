"""Canonical lifecycle guards for the operational domain.

Moved here with the enums they govern (tranche
P1B-OPERATIONS-DOMAIN-EXTRACTION). Leaving them in the application package
would have forced `operations_domain` consumers to import back into
`workspace_api` to obtain the invariants of `operations_domain`'s own enums -
the inverted dependency this tranche exists to remove.

`workspace_api.domain.lifecycle` re-exports these same function objects; it
does not redefine them.
"""

from .models import CustomerRequestStatus, DataState, HandoverStatus, IncidentStatus, ReportStatus, TaskStatus

_ALLOWED: dict[DataState, set[DataState]] = {
    DataState.RAW: {DataState.NORMALIZED, DataState.REJECTED},
    DataState.NORMALIZED: {DataState.PROPOSED, DataState.REJECTED},
    DataState.PROPOSED: {DataState.CONFIRMED, DataState.REJECTED},
    DataState.CONFIRMED: {DataState.CORRECTED, DataState.FROZEN},
    DataState.CORRECTED: {DataState.FROZEN},
    DataState.REJECTED: set(),
    DataState.FROZEN: set(),
}

def assert_transition(current: DataState, target: DataState) -> None:
    if target not in _ALLOWED[current]:
        raise ValueError(f"Invalid data-state transition: {current} -> {target}")


# Task status lifecycle (separate from the RAW..FROZEN data-state machine).
_ALLOWED_TASK: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.OPEN: {TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.CANCELLED, TaskStatus.CARRY_OVER},
    TaskStatus.IN_PROGRESS: {TaskStatus.BLOCKED, TaskStatus.DONE, TaskStatus.CANCELLED, TaskStatus.CARRY_OVER},
    TaskStatus.BLOCKED: {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED, TaskStatus.CARRY_OVER},
    TaskStatus.CARRY_OVER: {TaskStatus.OPEN, TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
    TaskStatus.DONE: set(),
    TaskStatus.CANCELLED: set(),
}


def assert_task_transition(current: TaskStatus, target: TaskStatus) -> None:
    if target not in _ALLOWED_TASK[current]:
        raise ValueError(f"Invalid task-status transition: {current} -> {target}")


# Customer-request status lifecycle (fourth domain vertical, P2-A). NEW is the
# only entry state (matches CustomerRequestStatus default). WAITING cannot go
# directly to CLOSED: a request that is waiting (e.g. on the customer or a
# third party) must first be marked RESOLVED so there is an explicit record
# that the underlying issue was actually addressed, not just abandoned while
# waiting. CLOSED is terminal (closing is the final administrative step after
# resolution, matching Task's DONE/CANCELLED terminal pattern).
_ALLOWED_CUSTOMER_REQUEST: dict[CustomerRequestStatus, set[CustomerRequestStatus]] = {
    CustomerRequestStatus.NEW: {CustomerRequestStatus.ACKNOWLEDGED},
    CustomerRequestStatus.ACKNOWLEDGED: {CustomerRequestStatus.IN_PROGRESS},
    CustomerRequestStatus.IN_PROGRESS: {
        CustomerRequestStatus.WAITING,
        CustomerRequestStatus.RESOLVED,
    },
    CustomerRequestStatus.WAITING: {CustomerRequestStatus.IN_PROGRESS},
    CustomerRequestStatus.RESOLVED: {CustomerRequestStatus.CLOSED},
    CustomerRequestStatus.CLOSED: set(),
}


def assert_customer_request_transition(
    current: CustomerRequestStatus, target: CustomerRequestStatus
) -> None:
    if target not in _ALLOWED_CUSTOMER_REQUEST[current]:
        raise ValueError(
            f"Invalid customer-request-status transition: {current} -> {target}"
        )


# Incident status lifecycle (fifth domain vertical, P2-A). This is the FULL
# graph, including REPORTED -> ACKNOWLEDGED: the restriction that ONLY the
# dedicated acknowledgement action (not the generic incident.transition
# action) may perform that specific move is enforced by IncidentService, not
# here (SPEC R2/R9) - the same separation TaskService uses between
# create_task/create_creation_intent and the plain lifecycle guard. CLOSED is
# terminal; ACKNOWLEDGED may skip MITIGATING and go straight to RESOLVED.
_ALLOWED_INCIDENT: dict[IncidentStatus, set[IncidentStatus]] = {
    IncidentStatus.REPORTED: {IncidentStatus.ACKNOWLEDGED},
    IncidentStatus.ACKNOWLEDGED: {IncidentStatus.MITIGATING, IncidentStatus.RESOLVED},
    IncidentStatus.MITIGATING: {IncidentStatus.RESOLVED},
    IncidentStatus.RESOLVED: {IncidentStatus.CLOSED},
    IncidentStatus.CLOSED: set(),
}


def assert_incident_transition(current: IncidentStatus, target: IncidentStatus) -> None:
    if target not in _ALLOWED_INCIDENT[current]:
        raise ValueError(f"Invalid incident-status transition: {current} -> {target}")


# Handover status lifecycle (P2A-HANDOVER-VERTICAL). Linear and terminal:
# DRAFT -> REVIEWED -> ACKNOWLEDGED. There is no path back to DRAFT - a stale
# or drifted handover is recovered by creating a new draft, never by mutating
# an existing one (ADR section 3.3).
_ALLOWED_HANDOVER: dict[HandoverStatus, set[HandoverStatus]] = {
    HandoverStatus.DRAFT: {HandoverStatus.REVIEWED},
    HandoverStatus.REVIEWED: {HandoverStatus.ACKNOWLEDGED},
    HandoverStatus.ACKNOWLEDGED: set(),
}


def assert_handover_transition(current: HandoverStatus, target: HandoverStatus) -> None:
    if target not in _ALLOWED_HANDOVER[current]:
        raise ValueError(f"Invalid handover-status transition: {current} -> {target}")


# Report status lifecycle (P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE).
# Forward-only: DRAFT -> IN_REVIEW -> APPROVED -> FROZEN. FROZEN is terminal.
# Only the current version may transition (enforced by ReportService, not
# here - same separation IncidentService uses for its acknowledge action).
_ALLOWED_REPORT: dict[ReportStatus, set[ReportStatus]] = {
    ReportStatus.DRAFT: {ReportStatus.IN_REVIEW},
    ReportStatus.IN_REVIEW: {ReportStatus.APPROVED},
    ReportStatus.APPROVED: {ReportStatus.FROZEN},
    ReportStatus.FROZEN: set(),
}


def assert_report_transition(current: ReportStatus, target: ReportStatus) -> None:
    if target not in _ALLOWED_REPORT[current]:
        raise ValueError(f"Invalid report-status transition: {current} -> {target}")
