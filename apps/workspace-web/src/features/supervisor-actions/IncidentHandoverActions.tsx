// P2C-MUTATION-FULL-UI-C3D (SPEC R5): supervisor Incident acknowledge and
// Handover review/acknowledge. Destination assignment for acknowledge is
// enforced server-side only - the UI never claims destination-wide discovery
// and reuses the existing source-shift handover list.
import { useCallback } from 'react';
import { supervisorApi } from '../../services/supervisorApi';
import { useMutationControl } from '../operator-actions/useMutationControl';
import { MutationFeedback } from '../operator-actions/MutationFeedback';
import type { Handover, Incident } from '../../types/operations';

interface IncidentHandoverActionsProps {
  incidents: Incident[];
  handovers: Handover[];
  onRefresh: () => Promise<void>;
}

export function IncidentHandoverActions({ incidents, handovers, onRefresh }: IncidentHandoverActionsProps) {
  const reportedIncidents = incidents.filter((i) => i.status === 'REPORTED');
  const draftHandovers = handovers.filter((h) => h.status === 'DRAFT');
  const reviewedHandovers = handovers.filter((h) => h.status === 'REVIEWED');

  return (
    <div className="action-group">
      <h3 className="form-legend">Incident acknowledge</h3>
      {reportedIncidents.length === 0 && <p>No incidents awaiting acknowledgement.</p>}
      <ul className="incident-list" aria-label="Incidents awaiting acknowledgement">
        {reportedIncidents.map((inc) => (
          <IncidentAckItem key={inc.incident_id} incident={inc} onRefresh={onRefresh} />
        ))}
      </ul>

      <h3 className="form-legend">Handover review</h3>
      {draftHandovers.length === 0 && <p>No handovers awaiting review.</p>}
      <ul className="incident-list" aria-label="Handovers awaiting review">
        {draftHandovers.map((h) => (
          <HandoverStepItem key={h.handover_id} handover={h} step="review" onRefresh={onRefresh} />
        ))}
      </ul>

      <h3 className="form-legend">Handover acknowledge</h3>
      {reviewedHandovers.length === 0 && <p>No handovers awaiting acknowledgement.</p>}
      <ul className="incident-list" aria-label="Handovers awaiting acknowledgement">
        {reviewedHandovers.map((h) => (
          <HandoverStepItem key={h.handover_id} handover={h} step="acknowledge" onRefresh={onRefresh} />
        ))}
      </ul>
    </div>
  );
}

function IncidentAckItem({ incident, onRefresh }: { incident: Incident; onRefresh: () => Promise<void> }) {
  const doAck = useCallback(async () => {
    await supervisorApi.acknowledgeIncident(incident.incident_id, { expected_version: incident.version });
  }, [incident.incident_id, incident.version]);
  const control = useMutationControl(doAck, onRefresh);
  const disabled = control.isSubmitting || control.isLockedOut;

  return (
    <li className="incident-list__item">
      <span className="incident-list__summary">{incident.summary}</span>
      <form
        aria-label={`Acknowledge incident ${incident.summary}`}
        className="action-form action-form--inline"
        onSubmit={async (e) => { e.preventDefault(); await control.submit(); }}
      >
        <button type="submit" disabled={disabled} aria-busy={control.isSubmitting} className="form-btn form-btn--small">
          {control.isSubmitting ? 'Acknowledging…' : 'Acknowledge'}
        </button>
        <MutationFeedback id={control.feedbackId} state={control.state} onRefreshAndUnlock={() => void control.refreshAndUnlock()} />
      </form>
    </li>
  );
}

function HandoverStepItem({
  handover,
  step,
  onRefresh
}: {
  handover: Handover;
  step: 'review' | 'acknowledge';
  onRefresh: () => Promise<void>;
}) {
  const doStep = useCallback(async () => {
    const payload = { expected_version: handover.version };
    if (step === 'review') await supervisorApi.reviewHandover(handover.handover_id, payload);
    else await supervisorApi.acknowledgeHandover(handover.handover_id, payload);
  }, [handover.handover_id, handover.version, step]);
  const control = useMutationControl(doStep, onRefresh);
  const disabled = control.isSubmitting || control.isLockedOut;

  return (
    <li className="incident-list__item">
      <span className="incident-list__summary">{handover.from_shift_id} → {handover.to_shift_id}</span>
      <span className="incident-list__status status-badge">{handover.status}</span>
      <form
        aria-label={`${step === 'review' ? 'Review' : 'Acknowledge'} handover ${handover.handover_id}`}
        className="action-form action-form--inline"
        onSubmit={async (e) => { e.preventDefault(); await control.submit(); }}
      >
        <button type="submit" disabled={disabled} aria-busy={control.isSubmitting} className="form-btn form-btn--small">
          {control.isSubmitting ? 'Saving…' : step === 'review' ? 'Review' : 'Acknowledge'}
        </button>
        <MutationFeedback id={control.feedbackId} state={control.state} onRefreshAndUnlock={() => void control.refreshAndUnlock()} />
      </form>
    </li>
  );
}
