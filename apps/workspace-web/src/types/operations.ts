// P2C-MUTATION-FULL-UI-C3D: these operational domain types are now shared by
// both the operator surface (features/operator-actions) and the supervisor
// surface (features/supervisor-actions). Staffing-only types live separately
// in types/supervisorContracts.ts and never merge into this file.
export type ShiftStatus = 'OPEN' | 'HANDOVER_PENDING' | 'CLOSED' | 'FROZEN';

export type DataState =
  | 'RAW'
  | 'NORMALIZED'
  | 'PROPOSED'
  | 'CONFIRMED'
  | 'REJECTED'
  | 'CORRECTED'
  | 'FROZEN';

export type RiskClass = 'R0' | 'R1' | 'R2' | 'R3' | 'R4';

export type TaskStatus = 'OPEN' | 'IN_PROGRESS' | 'BLOCKED' | 'DONE' | 'CARRY_OVER' | 'CANCELLED';

export type CustomerRequestStatus =
  | 'NEW'
  | 'ACKNOWLEDGED'
  | 'IN_PROGRESS'
  | 'WAITING'
  | 'RESOLVED'
  | 'CLOSED';

export type IncidentStatus = 'REPORTED' | 'ACKNOWLEDGED' | 'MITIGATING' | 'RESOLVED' | 'CLOSED';

export type HandoverStatus = 'DRAFT' | 'REVIEWED' | 'ACKNOWLEDGED';

export interface EvidenceRef {
  evidence_id: string;
  source_type: string;
  source_id: string;
  sha256: string | null;
}

export interface Shift {
  shift_id: string;
  name: string;
  starts_at: string;
  ends_at: string;
  status: ShiftStatus;
  version: number;
  created_at: string;
}

export interface OperationalEvent {
  event_id: string;
  shift_id: string;
  event_type: string;
  title: string;
  description: string | null;
  risk_class: RiskClass;
  state: DataState;
  starts_at: string | null;
  ends_at: string | null;
  owner_id: string | null;
  evidence: EvidenceRef[];
  version: number;
}

export interface Task {
  task_id: string;
  shift_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  owner_id: string | null;
  due_at: string | null;
  risk_class: RiskClass;
  state: DataState;
  evidence: EvidenceRef[];
  version: number;
  created_at: string;
}

// P2C-MUTATION-FULL-UI-C3C (SPEC R18): task creation intent response — the
// server returns intent_id and risk_class for the caller to retain (ephemeral
// React state only). payload_digest is present in the API response but MUST
// NOT be rendered or persisted in the UI per SPEC R18/WO C3C-WO-REV-F4.
export interface TaskCreationIntentResponse {
  intent_id: string;
  payload_digest: string;
  risk_class: string;
  created_at: string;
}

export interface CustomerRequest {
  request_id: string;
  customer_id: string;
  shift_id: string | null;
  summary: string;
  details: string | null;
  status: CustomerRequestStatus;
  source_message_id: string | null;
  received_at: string;
  promised_at: string | null;
  owner_id: string | null;
  version: number;
}

export interface Incident {
  incident_id: string;
  shift_id: string;
  risk_class: RiskClass;
  summary: string;
  description: string | null;
  status: IncidentStatus;
  owner_id: string | null;
  evidence: EvidenceRef[];
  version: number;
  created_at: string;
}

export interface HandoverItem {
  item_id: string;
  handover_id: string;
  source_record_type: string;
  source_record_id: string;
  source_digest: string;
  summary: string;
  owner_id: string | null;
  due_at: string | null;
  risk_class: RiskClass;
  evidence: EvidenceRef[];
}

export interface Handover {
  handover_id: string;
  from_shift_id: string;
  to_shift_id: string;
  status: HandoverStatus;
  items: HandoverItem[];
  created_by: string;
  reviewed_by: string | null;
  reviewed_at: string | null;
  received_by: string | null;
  acknowledged_at: string | null;
  version: number;
  created_at: string;
  acknowledged: boolean;
}

export interface OpenWorkResponse {
  shift_id: string;
  tasks: Task[];
  customer_requests: CustomerRequest[];
  incidents: Incident[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}
