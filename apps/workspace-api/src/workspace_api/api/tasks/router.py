from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict

from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger import Ledger

from workspace_api.application.task_service import TaskService
from workspace_api.dependencies import get_ledger, get_principal
from operations_domain.models import EvidenceRef, RiskClass, Task, TaskCreationIntent, TaskStatus

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskCreationIntentCreateResponse(BaseModel):
    """POST /tasks/creation-intents 201 response — SPEC §5.4.

    Returns only: intent_id, payload_digest, risk_class, created_at.
    shift_id, payload_snapshot, and created_by are not exposed on creation.
    """

    intent_id: UUID
    payload_digest: str
    risk_class: str
    created_at: datetime


class TaskCreationIntentGetResponse(BaseModel):
    """GET /tasks/creation-intents/{intent_id} 200 response — SPEC §5.4.

    Returns: intent_id, payload_snapshot, payload_digest, risk_class,
    created_by, created_at. shift_id is not exposed.
    """

    intent_id: UUID
    payload_snapshot: dict[str, Any]
    payload_digest: str
    risk_class: str
    created_by: str
    created_at: datetime


class TaskInput(BaseModel):
    # P2B-APPROVER-IDENTITY-RECONCILIATION (R7.1/R9.3): approvals are no
    # longer caller-supplied; extra="forbid" turns a stray legacy `approvals`
    # field into a 422. `intent_id` is required for a risk class that needs
    # approval (R2+) and must be omitted otherwise (R9.3).
    model_config = ConfigDict(extra="forbid")
    shift_id: UUID
    title: str
    description: str | None = None
    owner_id: str | None = None
    risk_class: RiskClass = RiskClass.R1
    # Previously missing: an R2+ task submitted with evidence over HTTP was
    # silently accepted by Pydantic (extra field ignored) and the service saw
    # zero evidence, always refusing (EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md
    # High Finding #4.1 / Critical Finding #2's Task half).
    evidence: list[EvidenceRef] = []
    intent_id: UUID | None = None


class TaskCreationIntentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    shift_id: UUID
    title: str
    description: str | None = None
    owner_id: str | None = None
    risk_class: RiskClass
    evidence: list[EvidenceRef] = []


class TransitionInput(BaseModel):
    target_status: TaskStatus


def _task_like(payload) -> Task:
    return Task(
        shift_id=payload.shift_id,
        title=payload.title,
        description=payload.description,
        owner_id=payload.owner_id,
        risk_class=payload.risk_class,
        evidence=payload.evidence,
    )


@router.post("/creation-intents", response_model=TaskCreationIntentCreateResponse, status_code=201)
def create_creation_intent(
    payload: TaskCreationIntentInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        intent = TaskService(ledger).create_creation_intent(_task_like(payload), principal)
        return TaskCreationIntentCreateResponse.model_validate(intent, from_attributes=True)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Operational resource not found") from exc


@router.get("/creation-intents/{intent_id}", response_model=TaskCreationIntentGetResponse)
def get_creation_intent(
    intent_id: UUID,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        intent = TaskService(ledger).get_creation_intent(intent_id, principal)
        return TaskCreationIntentGetResponse.model_validate(intent, from_attributes=True)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Operational resource not found") from exc


@router.post("", response_model=Task)
def create_task(
    payload: TaskInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    task = _task_like(payload)
    try:
        return TaskService(ledger).create_task(task, principal, intent_id=payload.intent_id)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Operational resource not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{task_id}/transition", response_model=Task)
def transition_task(
    task_id: UUID,
    payload: TransitionInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    try:
        return TaskService(ledger).transition(task_id, principal, payload.target_status)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Operational resource not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
