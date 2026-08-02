// P2C-MUTATION-FULL-UI-C3D (SPEC R2/R4/R6): exact backend contract types for
// the supervisor staffing/approval/closeout surface. Mirrors the existing
// FastAPI Pydantic models field-for-field; no client-invented field is added.
// Readiness/ReportStatus types are reused from backendContracts.ts (C3b1)
// rather than redefined, so this file never forks an existing contract.
import type { ReadinessAction, ReadinessRecordType, ReportStatus } from './backendContracts';

export type { ReportStatus };

export interface StaffingShift {
  shift_id: string;
  name: string;
  status: string;
}

export interface StaffingUser {
  user_id: string;
  username: string;
  role: string;
}

export type AssignmentStatus = 'ACTIVE' | 'REVOKED';

export interface ShiftAssignment {
  assignment_id: string;
  shift_id: string;
  user_id: string;
  assigned_by: string;
  status: AssignmentStatus;
  version: number;
  assigned_at: string;
  revoked_by: string | null;
  revoked_at: string | null;
}

// R4: the exact five POST-supported (record_type, action) pairs. event.correct
// is the one pair readiness does NOT support (D2/C3D-WO-REV-F2).
export type ApprovalRecordType = ReadinessRecordType;
export type ApprovalAction = ReadinessAction | 'event.correct';

// POST /approvals request body — exactly three caller fields
// (workspace_api/api/approvals/router.py::ApprovalCreateInput, extra="forbid").
export interface ApprovalCreateInput {
  record_type: ApprovalRecordType;
  action: ApprovalAction;
  record_id: string;
}

// POST /approvals response — SPEC R4: no payload_digest. approver_id/
// approver_role/receipt_id are present in the DTO because the backend sends
// them, but MUST NOT be rendered or retained as authority anywhere in the UI.
export interface ApprovalReceiptResponse {
  receipt_id: string;
  record_type: string;
  record_id: string;
  action: string;
  target_version: number;
  risk_class: string;
  approver_id: string;
  approver_role: string;
  created_at: string;
}

// POST /corrections/events/{event_id} — requires a prior event.correct
// approval receipt at the event's current version before this succeeds.
export interface CorrectEventInput {
  reason: string;
  expected_version: number;
}

export interface CorrectionResponse {
  correction_id: string;
  record_type: string;
  record_id: string;
  reason: string;
  requested_by: string;
  previous_version: number;
  new_version: number;
  created_at: string;
}

// POST /incidents/{id}/acknowledge
export interface AcknowledgeIncidentInput {
  expected_version: number;
}

// POST /handovers/{id}/review and /acknowledge
export interface HandoverPreconditionInput {
  expected_version: number;
}

// POST /reports/{id}/approve — status-only transition, content version
// unchanged (SPEC R13 precondition semantics).
export interface ReportPreconditionInput {
  expected_version: number;
  expected_status: ReportStatus;
}

// POST /reports/{id}/versions — successor creation is the only revocation
// path for an APPROVED report; C3d always sends a non-empty reason even
// though the backend field itself is optional (SPEC D2/R5).
export interface ReportVersionInput {
  reason: string;
  expected_version: number;
  expected_status: ReportStatus;
}

// POST /shifts/{id}/freeze — exactly one field. The retired override fields
// (override_unimplemented_prerequisites, override_reason) MUST NEVER appear
// in a supervisor DTO, DOM control or observed request body (SPEC R6).
export interface FreezeShiftInput {
  expected_version: number;
}

// GET /tasks/creation-intents/{intent_id} — proves a manually entered stored
// intent id currently resolves before the approval attempt. There is no
// task-intent list endpoint (D2); this is the only truthful existence check.
export interface TaskCreationIntentGetResponse {
  intent_id: string;
  payload_snapshot: Record<string, unknown>;
  payload_digest: string;
  risk_class: string;
  created_by: string;
  created_at: string;
}
