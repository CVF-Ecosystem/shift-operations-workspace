// P2C-MUTATION-FULL-UI-C3D (SPEC R3/R5): supervisor Event confirm/correct.
// Uses the COMPLETE selected-shift event collection (unconfirmed included)
// so an unconfirmed event is a legal confirm target. Confirm is legal while
// state is not already CONFIRMED/FROZEN. Correct is legal only once the
// selected Shift is FROZEN, and requires a prior OperationalEvent/
// event.correct approval receipt at the event's current version - the
// receipt is created via ApprovalActions before this control can succeed;
// this component sends only reason + expected_version, never a digest.
import { useCallback, useState } from 'react';
import { supervisorApi } from '../../services/supervisorApi';
import { useMutationControl } from '../operator-actions/useMutationControl';
import { MutationFeedback } from '../operator-actions/MutationFeedback';
import type { OperationalEvent, Shift } from '../../types/operations';

interface EventActionsProps {
  selectedShift: Shift | null;
  events: OperationalEvent[];
  onRefresh: () => Promise<void>;
}

export function EventActions({ selectedShift, events, onRefresh }: EventActionsProps) {
  const isFrozen = selectedShift?.status === 'FROZEN';

  if (events.length === 0) {
    return (
      <div className="action-group">
        <p>No events for this shift yet.</p>
      </div>
    );
  }

  return (
    <div className="action-group">
      <h3 className="form-legend">Event confirm / correct</h3>
      <ul className="incident-list" aria-label="Event list">
        {events.map((event) => (
          <EventItem key={event.event_id} event={event} isFrozen={isFrozen} onRefresh={onRefresh} />
        ))}
      </ul>
    </div>
  );
}

function EventItem({ event, isFrozen, onRefresh }: { event: OperationalEvent; isFrozen: boolean; onRefresh: () => Promise<void> }) {
  const [reason, setReason] = useState('');
  const canConfirm = event.state !== 'CONFIRMED' && event.state !== 'FROZEN';
  const canCorrect = isFrozen && (event.state === 'CONFIRMED' || event.state === 'CORRECTED' || event.state === 'FROZEN');

  const doConfirm = useCallback(async () => {
    await supervisorApi.confirmEvent(event.event_id, event.version);
  }, [event.event_id, event.version]);

  const doCorrect = useCallback(async () => {
    if (!reason.trim()) return;
    await supervisorApi.correctEvent(event.event_id, { reason: reason.trim(), expected_version: event.version });
    setReason('');
  }, [event.event_id, event.version, reason]);

  const confirmControl = useMutationControl(doConfirm, onRefresh);
  const correctControl = useMutationControl(doCorrect, onRefresh);
  const confirmDisabled = confirmControl.isSubmitting || confirmControl.isLockedOut;
  const correctDisabled = correctControl.isSubmitting || correctControl.isLockedOut;

  return (
    <li className="incident-list__item">
      <span className="incident-list__summary">{event.title}</span>
      <span className="incident-list__status status-badge">{event.state}</span>

      {canConfirm && (
        <form
          aria-label={`Confirm event ${event.title}`}
          className="action-form action-form--inline"
          onSubmit={async (e) => { e.preventDefault(); await confirmControl.submit(); }}
        >
          <button type="submit" disabled={confirmDisabled} aria-busy={confirmControl.isSubmitting} className="form-btn form-btn--small">
            {confirmControl.isSubmitting ? 'Confirming…' : 'Confirm'}
          </button>
          <MutationFeedback
            id={confirmControl.feedbackId}
            state={confirmControl.state}
            onRefreshAndUnlock={() => void confirmControl.refreshAndUnlock()}
          />
        </form>
      )}

      {canCorrect && (
        <form
          aria-label={`Correct event ${event.title}`}
          className="action-form action-form--inline"
          onSubmit={async (e) => { e.preventDefault(); await correctControl.submit(); }}
        >
          <label htmlFor={`correct-reason-${event.event_id}`} className="form-label">Reason</label>
          <input
            id={`correct-reason-${event.event_id}`}
            type="text"
            value={reason}
            onChange={(e) => { setReason(e.target.value); correctControl.reset(); }}
            required
            disabled={correctDisabled}
            maxLength={500}
            aria-describedby={correctControl.feedbackId}
            className="form-input form-input--inline"
          />
          <button type="submit" disabled={correctDisabled || !reason.trim()} aria-busy={correctControl.isSubmitting} className="form-btn form-btn--small">
            {correctControl.isSubmitting ? 'Correcting…' : 'Correct'}
          </button>
          <MutationFeedback
            id={correctControl.feedbackId}
            state={correctControl.state}
            onRefreshAndUnlock={() => void correctControl.refreshAndUnlock()}
          />
        </form>
      )}
    </li>
  );
}
