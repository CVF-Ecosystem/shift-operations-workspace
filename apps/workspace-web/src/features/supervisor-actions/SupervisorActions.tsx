// P2C-MUTATION-FULL-UI-C3D (SPEC R2-R6, D6): SupervisorActions main
// coordinator. Collects feature-owned subcomponents for staffing, event
// confirm/correct, approval receipts, incident/handover, and Report/freeze.
// Staffing is always rendered (works even with no selected operational
// shift); the operational sections additionally require staffingAvailable.
//
// staffingAvailable is a real server-derived signal (useSupervisorData
// clears it on a genuine 403 from GET /staffing/shifts|users, D1 "server
// decides authority" - never a client role-ranking guess), not an advisory
// capability hint. Gating the whole operational subtree on it is therefore
// distinct from C3D-WO-REV-F1 (which forbids hiding controls because the
// advisory `approval.create` action is merely absent from a capability
// list): here the presence of the supervisor-only staffing surface itself
// is the truthful signal that this principal holds shift_supervisor-or-
// higher authority at all. Every individual action inside these
// subcomponents still sends the request and lets the backend's real
// authoritative response (401/403/404/409/422) govern the outcome.
import { StaffingActions } from './StaffingActions';
import { EventActions } from './EventActions';
import { ApprovalActions } from './ApprovalActions';
import { IncidentHandoverActions } from './IncidentHandoverActions';
import { ReportFreezeActions } from './ReportFreezeActions';
import type { SupervisorActionsProps } from './types';

export function SupervisorActions({
  selectedShiftId,
  selectedShift,
  events,
  incidents,
  handovers,
  reports,
  staffingShifts,
  staffingUsers,
  staffingAvailable,
  onStaffingRefresh,
  onOperationalRefresh
}: SupervisorActionsProps) {
  return (
    <div className="supervisor-actions">
      <section aria-label="Staffing" className="action-section">
        <StaffingActions
          staffingShifts={staffingShifts}
          staffingUsers={staffingUsers}
          staffingAvailable={staffingAvailable}
          onStaffingRefresh={onStaffingRefresh}
        />
      </section>

      {staffingAvailable && selectedShiftId && selectedShift && (
        <>
          <section aria-label="Event confirm and correct" className="action-section">
            <EventActions selectedShift={selectedShift} events={events} onRefresh={onOperationalRefresh} />
          </section>

          <section aria-label="Approval receipts" className="action-section">
            <ApprovalActions events={events} incidents={incidents} reports={reports} onRefresh={onOperationalRefresh} />
          </section>

          <section aria-label="Incident and handover" className="action-section">
            <IncidentHandoverActions incidents={incidents} handovers={handovers} onRefresh={onOperationalRefresh} />
          </section>

          <section aria-label="Report and freeze" className="action-section">
            <ReportFreezeActions selectedShift={selectedShift} reports={reports} onRefresh={onOperationalRefresh} />
          </section>
        </>
      )}
    </div>
  );
}
