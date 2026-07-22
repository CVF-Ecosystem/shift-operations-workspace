from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from cvf_runtime.approval import Approval
from cvf_runtime.errors import CvfDenied
from cvf_runtime.identity import Principal
from operations_ledger import Ledger

from workspace_api.application.task_service import TaskService
from workspace_api.dependencies import get_ledger, get_principal
from workspace_api.domain.models import EvidenceRef, RiskClass, Task, TaskStatus

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskInput(BaseModel):
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
    approvals: list[Approval] = []


class TransitionInput(BaseModel):
    target_status: TaskStatus


@router.post("", response_model=Task)
def create_task(
    payload: TaskInput,
    principal: Principal = Depends(get_principal),
    ledger: Ledger = Depends(get_ledger),
):
    task = Task(
        shift_id=payload.shift_id,
        title=payload.title,
        description=payload.description,
        owner_id=payload.owner_id,
        risk_class=payload.risk_class,
        evidence=payload.evidence,
    )
    try:
        return TaskService(ledger).create_task(task, principal, payload.approvals)
    except CvfDenied as exc:
        raise HTTPException(status_code=exc.http_status, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Shift not found") from exc
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
        raise HTTPException(status_code=404, detail="Task not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
