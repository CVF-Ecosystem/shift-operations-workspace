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

// P2C-MUTATION-FULL-UI-C3C (WO C3C-BUILD-REV-F2): the real GET
// /shifts/{id}/capabilities shape. There is no `capabilities` field on the
// backend response - advisory UI gating MUST read `actions`.
export interface CapabilitiesResponse {
  shift_id: string;
  actions: string[];
  reasons: string[];
}

// SPEC: the backend's exact fixed OperationalEvent.event_type domain-lock
// allowlist (packages/cvf-runtime domain_lock._EVENT_TYPE_DOMAIN). Any other
// value is rejected 422 server-side; the UI MUST offer only this bounded set.
export const OPERATIONAL_EVENT_TYPES = [
  'equipment_downtime',
  'equipment_restored',
  'vessel_status',
  'production_update',
  'yard_status',
  'incident',
  'customer_request',
  'handover',
  'shift_update',
  'end_shift_report'
] as const;

export type OperationalEventType = (typeof OPERATIONAL_EVENT_TYPES)[number];

// The exact backend ReportStatus/ReportType enums (report_models.py). The
// backend never uses REVIEW_REQUESTED - only IN_REVIEW.
export type ReportStatus = 'DRAFT' | 'IN_REVIEW' | 'APPROVED' | 'FROZEN';
export type ReportType = 'END_SHIFT';

// WO C3C-BUILD-REREV-F3: feature-owned DTOs mirroring
// operations_domain.report_models.ReportSourceRef/ReportSection exactly -
// not a monolithic generated client, just the two real nested shapes the
// browser reads. source_manifest entries are per-record digest/version
// refs; source_version is null for unversioned record types (Correction,
// CustomerRequest) and required for the rest.
export type ReportRecordType = 'OperationalEvent' | 'Correction' | 'Task' | 'CustomerRequest' | 'Incident' | 'Handover';

export interface ReportSourceRef {
  record_type: ReportRecordType;
  record_id: string;
  source_version: number | null;
  source_digest: string;
}

// section_type is the exact bounded set from report_models._SECTION_ORDER.
// `records` stays list[Record<string, unknown>] because the backend itself
// types it as list[dict] (heterogeneous per record type) - only the two
// fields it actually validates on every record (record_type/record_id) are
// pulled into the DTO; inventing a closed per-field shape here would overclaim
// a contract the backend does not enforce.
export type ReportSectionType = 'operational_events' | 'corrections' | 'tasks' | 'customer_requests' | 'incidents' | 'handovers';

export interface ReportSectionRecord {
  record_type: ReportRecordType;
  record_id: string;
  [field: string]: unknown;
}

export interface ReportSection {
  section_type: ReportSectionType;
  records: ReportSectionRecord[];
}

export interface ReportResponse {
  report_id: string;
  shift_id: string;
  report_type: ReportType;
  version: number;
  status: ReportStatus;
  is_current: boolean;
  sections: ReportSection[];
  source_manifest: ReportSourceRef[];
  snapshot_digest: string;
  generated_from_cutoff: string;
  created_at: string;
}
