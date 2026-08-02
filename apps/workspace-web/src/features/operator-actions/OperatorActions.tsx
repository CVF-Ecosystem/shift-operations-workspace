// P2C-MUTATION-FULL-UI-C3C (SPEC R18/D6): OperatorActions main coordinator component.
// Collects feature-owned subcomponents for shift, message/event, task, customer request,
// incident, handover, and report actions.
import { ShiftActions } from './ShiftActions';
import { MessageEventActions } from './MessageEventActions';
import { TaskActions } from './TaskActions';
import { CustomerRequestActions } from './CustomerRequestActions';
import { IncidentActions } from './IncidentActions';
import { HandoverActions } from './HandoverActions';
import { ReportActions } from './ReportActions';
import type { OperatorActionsProps } from './types';

export function OperatorActions({
  selectedShiftId,
  selectedShift,
  shifts,
  messages,
  tasks,
  customerRequests,
  incidents,
  handovers,
  reports,
  onShiftCreated,
  onRefresh
}: OperatorActionsProps) {
  return (
    <div className="operator-actions">
      <section aria-label="Shift actions" className="action-section">
        <ShiftActions selectedShift={selectedShift} onShiftCreated={onShiftCreated} onRefresh={onRefresh} />
      </section>

      {selectedShiftId && selectedShift && (
        <>
          <section aria-label="Messages and events" className="action-section">
            <MessageEventActions shiftId={selectedShiftId} messages={messages} onRefresh={onRefresh} />
          </section>

          <section aria-label="Tasks" className="action-section">
            <TaskActions shiftId={selectedShiftId} tasks={tasks} onRefresh={onRefresh} />
          </section>

          <section aria-label="Customer requests" className="action-section">
            <CustomerRequestActions shiftId={selectedShiftId} customerRequests={customerRequests} onRefresh={onRefresh} />
          </section>

          <section aria-label="Incidents" className="action-section">
            <IncidentActions shiftId={selectedShiftId} incidents={incidents} onRefresh={onRefresh} />
          </section>

          <section aria-label="Handovers" className="action-section">
            <HandoverActions fromShiftId={selectedShiftId} shifts={shifts} onRefresh={onRefresh} />
          </section>

          <section aria-label="Reports" className="action-section">
            <ReportActions shiftId={selectedShiftId} reports={reports} onRefresh={onRefresh} />
          </section>
        </>
      )}
    </div>
  );
}
