// P2C-MUTATION-FULL-UI-C3B1 (SPEC R11/R15/R35-R37): feature-owned DTOs for
// the new browser reads/readiness contract. Message has no existing frontend
// type (unlike Task/CustomerRequest, which stay in types/operations.ts);
// ReadinessResponse mirrors the backend's sanitized shape exactly - no
// payload digest, receipt id, approver identity or credential field exists
// here because the backend never sends one.

export type MessageSource = string;

export type MessageState =
  | 'RAW'
  | 'NORMALIZED'
  | 'PROPOSED'
  | 'CONFIRMED'
  | 'REJECTED'
  | 'CORRECTED'
  | 'FROZEN';

export interface Message {
  message_id: string;
  shift_id: string;
  source: MessageSource;
  sender_id: string;
  text: string;
  state: MessageState;
  created_at: string;
  evidence: unknown[];
}

// SPEC R35: the exact four canonical readiness pairs C3b1 supports.
export type ReadinessRecordType = 'OperationalEvent' | 'Task' | 'Incident' | 'Report';
export type ReadinessAction =
  | 'event.confirm'
  | 'task.create'
  | 'incident.acknowledge'
  | 'report.approve';

export interface ReadinessQuery {
  record_type: ReadinessRecordType;
  record_id: string;
  action: ReadinessAction;
}

export interface ReadinessResponse {
  record_type: string;
  record_id: string;
  action: string;
  target_version: number;
  risk_class: string;
  ready: boolean;
  required_roles: string[];
  satisfied_roles: string[];
}
