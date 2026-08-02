// P2C-MUTATION-FULL-UI-C3D: Feature types for supervisor actions.
import type { Handover, Incident, OperationalEvent, Shift } from '../../types/operations';
import type { ReportEntry } from '../../services/operatorApi';
import type { StaffingShift, StaffingUser } from '../../types/supervisorContracts';

// SPEC R5: exact legal supervisor target matrix. The backend remains
// authoritative for every one of these; this table only bounds which
// controls the UI renders so it never offers a transition the backend would
// reject outright.
export const SUPERVISOR_INCIDENT_ACKNOWLEDGE_FROM = 'REPORTED';
export const SUPERVISOR_HANDOVER_REVIEW_FROM = 'DRAFT';
export const SUPERVISOR_HANDOVER_ACKNOWLEDGE_FROM = 'REVIEWED';
export const SUPERVISOR_REPORT_APPROVE_FROM = 'IN_REVIEW';
export const SUPERVISOR_REPORT_REVOKE_FROM = 'APPROVED';
export const SUPERVISOR_SHIFT_FREEZE_FROM = 'CLOSED';

export interface SupervisorActionsProps {
  selectedShiftId: string | null;
  selectedShift: Shift | null;
  events: OperationalEvent[];
  incidents: Incident[];
  handovers: Handover[];
  reports: ReportEntry[];
  staffingShifts: StaffingShift[];
  staffingUsers: StaffingUser[];
  staffingAvailable: boolean;
  onStaffingRefresh: () => Promise<void>;
  onOperationalRefresh: () => Promise<void>;
}
