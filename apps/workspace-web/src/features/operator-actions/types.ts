// P2C-MUTATION-FULL-UI-C3C: Feature types for operator actions
import type { CustomerRequest, CustomerRequestStatus, Handover, Incident, IncidentStatus, Shift, Task, TaskStatus } from '../../types/operations';
import type { Message } from '../../types/backendContracts';
import type { ReportEntry } from '../../services/operatorApi';

// WO C3C-BUILD-REV-F4: legal target states mirrored exactly from the
// canonical backend lifecycle tables (packages/operations-domain/lifecycle.py).
// The UI must never offer a transition the backend would reject.
export const TASK_LIFECYCLE: Record<TaskStatus, TaskStatus[]> = {
  OPEN: ['IN_PROGRESS', 'BLOCKED', 'CANCELLED', 'CARRY_OVER'],
  IN_PROGRESS: ['BLOCKED', 'DONE', 'CANCELLED', 'CARRY_OVER'],
  BLOCKED: ['IN_PROGRESS', 'CANCELLED', 'CARRY_OVER'],
  CARRY_OVER: ['OPEN', 'IN_PROGRESS', 'CANCELLED'],
  DONE: [],
  CANCELLED: []
};

export const CUSTOMER_REQUEST_LIFECYCLE: Record<CustomerRequestStatus, CustomerRequestStatus[]> = {
  NEW: ['ACKNOWLEDGED'],
  ACKNOWLEDGED: ['IN_PROGRESS'],
  IN_PROGRESS: ['WAITING', 'RESOLVED'],
  WAITING: ['IN_PROGRESS'],
  RESOLVED: ['CLOSED'],
  CLOSED: []
};

// Operator-permitted subset only: REPORTED->ACKNOWLEDGED is a C3d supervisor
// action (IncidentService.acknowledge, role shift_supervisor). Operators may
// transition ACKNOWLEDGED->MITIGATING/RESOLVED and RESOLVED->CLOSED.
export const OPERATOR_INCIDENT_LIFECYCLE: Record<IncidentStatus, IncidentStatus[]> = {
  REPORTED: [],
  ACKNOWLEDGED: ['MITIGATING', 'RESOLVED'],
  MITIGATING: ['RESOLVED'],
  RESOLVED: ['CLOSED'],
  CLOSED: []
};

export interface OperatorActionsProps {
  selectedShiftId: string | null;
  selectedShift: Shift | null;
  shifts: Shift[];
  messages: Message[];
  tasks: Task[];
  customerRequests: CustomerRequest[];
  incidents: Incident[];
  handovers: Handover[];
  reports: ReportEntry[];
  capabilities: string[];
  onShiftCreated: (shift: Shift) => void;
  onRefresh: () => Promise<void>;
}
