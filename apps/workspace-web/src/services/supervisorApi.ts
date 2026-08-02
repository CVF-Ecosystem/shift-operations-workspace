// P2C-MUTATION-FULL-UI-C3D (SPEC R2-R6, WO section 3.1): supervisorApi wraps
// the existing typed request primitive from api.ts for every C3d supervisor
// route. It never forks auth, error mapping, query encoding or retry logic -
// every call is a thin typed pass-through to an existing FastAPI route.
import { request } from './api';
import type { Handover, Incident, OperationalEvent, Shift } from '../types/operations';
import type { ReadinessQuery, ReadinessResponse, ReportResponse } from '../types/backendContracts';
import type {
  AcknowledgeIncidentInput,
  ApprovalCreateInput,
  ApprovalReceiptResponse,
  CorrectEventInput,
  CorrectionResponse,
  FreezeShiftInput,
  HandoverPreconditionInput,
  ReportPreconditionInput,
  ReportVersionInput,
  ShiftAssignment,
  StaffingShift,
  StaffingUser,
  TaskCreationIntentGetResponse
} from '../types/supervisorContracts';

export const supervisorApi = {
  // R2: staffing control plane.
  listStaffingShifts: (signal?: AbortSignal) => request<StaffingShift[]>('/staffing/shifts', { signal }),

  listStaffingUsers: (signal?: AbortSignal) => request<StaffingUser[]>('/staffing/users', { signal }),

  listAssignments: (shiftId: string, signal?: AbortSignal) =>
    request<ShiftAssignment[]>(`/shifts/${encodeURIComponent(shiftId)}/assignments`, { signal }),

  assignUser: (shiftId: string, userId: string) =>
    request<ShiftAssignment>(`/shifts/${encodeURIComponent(shiftId)}/assignments`, {
      method: 'POST',
      body: { user_id: userId }
    }),

  revokeAssignment: (shiftId: string, assignmentId: string, expectedVersion: number) =>
    request<ShiftAssignment>(
      `/shifts/${encodeURIComponent(shiftId)}/assignments/${encodeURIComponent(assignmentId)}/revoke`,
      { method: 'POST', body: { expected_version: expectedVersion } }
    ),

  // R3: event confirm re-uses the existing operational precondition shape.
  confirmEvent: (eventId: string, expectedVersion: number) =>
    request<OperationalEvent>(`/events/${encodeURIComponent(eventId)}/confirm`, {
      method: 'POST',
      body: { expected_version: expectedVersion }
    }),

  correctEvent: (eventId: string, payload: CorrectEventInput) =>
    request<CorrectionResponse>(`/corrections/events/${encodeURIComponent(eventId)}`, {
      method: 'POST',
      body: payload
    }),

  // R4: the exact three-field approval payload for all five supported pairs.
  createApproval: (payload: ApprovalCreateInput) =>
    request<ApprovalReceiptResponse>('/approvals', { method: 'POST', body: payload }),

  getApprovalReadiness: (query: ReadinessQuery, signal?: AbortSignal) =>
    request<ReadinessResponse>('/approvals/readiness', {
      query: { record_type: query.record_type, record_id: query.record_id, action: query.action },
      signal
    }),

  // R5: incident acknowledge.
  acknowledgeIncident: (incidentId: string, payload: AcknowledgeIncidentInput) =>
    request<Incident>(`/incidents/${encodeURIComponent(incidentId)}/acknowledge`, {
      method: 'POST',
      body: payload
    }),

  // R5: handover review/acknowledge. Destination assignment is enforced
  // server-side only; the UI never claims destination-wide discovery.
  reviewHandover: (handoverId: string, payload: HandoverPreconditionInput) =>
    request<Handover>(`/handovers/${encodeURIComponent(handoverId)}/review`, {
      method: 'POST',
      body: payload
    }),

  acknowledgeHandover: (handoverId: string, payload: HandoverPreconditionInput) =>
    request<Handover>(`/handovers/${encodeURIComponent(handoverId)}/acknowledge`, {
      method: 'POST',
      body: payload
    }),

  // R5: Report approve, and revocation via successor creation only.
  approveReport: (reportId: string, payload: ReportPreconditionInput) =>
    request<ReportResponse>(`/reports/${encodeURIComponent(reportId)}/approve`, {
      method: 'POST',
      body: payload
    }),

  createReportVersion: (reportId: string, payload: ReportVersionInput) =>
    request<ReportResponse>(`/reports/${encodeURIComponent(reportId)}/versions`, {
      method: 'POST',
      body: payload
    }),

  // R6: freeze sends only expected_version; no retired override field exists
  // in this payload type or anywhere downstream of it.
  freezeShift: (shiftId: string, payload: FreezeShiftInput) =>
    request<Shift>(`/shifts/${encodeURIComponent(shiftId)}/freeze`, {
      method: 'POST',
      body: payload
    }),

  // Task-creation-intent approval target: a manual stored intent id is only
  // an identifier; the backend remains the sole source for existence/scope/
  // digest/risk (D2). No list endpoint exists, so this is the only truthful
  // existence check before the approval attempt.
  getTaskCreationIntent: (intentId: string, signal?: AbortSignal) =>
    request<TaskCreationIntentGetResponse>(`/tasks/creation-intents/${encodeURIComponent(intentId)}`, { signal })
};
