// P2C-MUTATION-FULL-UI-C3C (SPEC R18/R20, WO C3C-BUILD-REREV-F1/F3): internal
// message and event create forms. Event type is a bounded domain-lock-valid
// choice, not free text - the backend rejects any other value with 422.
// useMutationControl now owns the post-success/conflict refresh.
import { useCallback, useState } from 'react';
import { operatorApi } from '../../services/operatorApi';
import { useMutationControl } from './useMutationControl';
import { MutationFeedback } from './MutationFeedback';
import { OPERATIONAL_EVENT_TYPES, type Message, type OperationalEventType } from '../../types/backendContracts';
import type { RiskClass } from '../../types/operations';

const RISK_CLASSES: RiskClass[] = ['R0', 'R1', 'R2', 'R3'];

interface MessageEventActionsProps {
  shiftId: string;
  messages: Message[];
  onRefresh: () => Promise<void>;
}

export function MessageEventActions({ shiftId, messages, onRefresh }: MessageEventActionsProps) {
  const [msgText, setMsgText] = useState('');
  const [eventTitle, setEventTitle] = useState('');
  const [eventType, setEventType] = useState<OperationalEventType>(OPERATIONAL_EVENT_TYPES[0]);
  const [eventRisk, setEventRisk] = useState<RiskClass>('R1');

  const doMessage = useCallback(async () => {
    await operatorApi.createMessage(shiftId, msgText.trim());
    setMsgText('');
  }, [shiftId, msgText]);

  const doEvent = useCallback(async () => {
    await operatorApi.createEvent(shiftId, eventType, eventTitle.trim(), eventRisk);
    setEventTitle('');
  }, [shiftId, eventType, eventTitle, eventRisk]);

  const msgControl = useMutationControl(doMessage, onRefresh);
  const evtControl = useMutationControl(doEvent, onRefresh);
  const msgDisabled = msgControl.isSubmitting || msgControl.isLockedOut;
  const evtDisabled = evtControl.isSubmitting || evtControl.isLockedOut;

  const handleMsgSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!msgText.trim()) return;
    await msgControl.submit();
  };

  const handleEvtSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!eventTitle.trim()) return;
    await evtControl.submit();
  };

  return (
    <div className="action-group">
      <form aria-label="Append message" className="action-form" onSubmit={handleMsgSubmit}>
        <h3 className="form-legend">Internal Messages</h3>
        {messages.length > 0 && (
          <ul className="message-list" aria-label="Message list">
            {messages.map((m) => (
              <li key={m.message_id} className="message-list__item">
                <span className="message-list__sender">{m.sender_id}: </span>
                <span className="message-list__text">{m.text}</span>
              </li>
            ))}
          </ul>
        )}
        <label htmlFor="msg-text" className="form-label">Message text</label>
        <textarea
          id="msg-text"
          value={msgText}
          onChange={(e) => { setMsgText(e.target.value); msgControl.reset(); }}
          required
          disabled={msgDisabled}
          rows={2}
          maxLength={2000}
          aria-describedby={msgControl.feedbackId}
          className="form-input form-input--textarea"
        />
        <button
          type="submit"
          disabled={msgDisabled || !msgText.trim()}
          aria-busy={msgControl.isSubmitting}
          className="form-btn form-btn--primary"
        >
          {msgControl.isSubmitting ? 'Sending…' : 'Send message'}
        </button>
        <MutationFeedback
          id={msgControl.feedbackId}
          state={msgControl.state}
          onRefreshAndUnlock={() => void msgControl.refreshAndUnlock()}
        />
      </form>

      <form aria-label="Create event" className="action-form" onSubmit={handleEvtSubmit} style={{ marginTop: '16px' }}>
        <h3 className="form-legend">Create Event</h3>
        <label htmlFor="event-title" className="form-label">Title</label>
        <input
          id="event-title"
          type="text"
          value={eventTitle}
          onChange={(e) => { setEventTitle(e.target.value); evtControl.reset(); }}
          required
          disabled={evtDisabled}
          maxLength={200}
          aria-describedby={evtControl.feedbackId}
          className="form-input"
        />
        <label htmlFor="event-type" className="form-label">Event type</label>
        <select
          id="event-type"
          value={eventType}
          onChange={(e) => { setEventType(e.target.value as OperationalEventType); evtControl.reset(); }}
          disabled={evtDisabled}
          className="form-input"
        >
          {OPERATIONAL_EVENT_TYPES.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        <label htmlFor="event-risk" className="form-label">Risk class</label>
        <select
          id="event-risk"
          value={eventRisk}
          onChange={(e) => { setEventRisk(e.target.value as RiskClass); evtControl.reset(); }}
          disabled={evtDisabled}
          className="form-input"
        >
          {RISK_CLASSES.map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
        <button
          type="submit"
          disabled={evtDisabled || !eventTitle.trim()}
          aria-busy={evtControl.isSubmitting}
          className="form-btn form-btn--primary"
        >
          {evtControl.isSubmitting ? 'Creating…' : 'Create event'}
        </button>
        <MutationFeedback
          id={evtControl.feedbackId}
          state={evtControl.state}
          onRefreshAndUnlock={() => void evtControl.refreshAndUnlock()}
        />
      </form>
    </div>
  );
}
