// P2C-MUTATION-FULL-UI-C3D (SPEC R4): approval receipt creation for the
// exact five POST-supported pairs. Payload is exactly record_type/record_id/
// action. Capabilities are advisory only - absence of `approval.create` from
// the capability list MUST NOT suppress these controls (C3D-WO-REV-F1);
// POST /approvals remains authoritative. No digest/approver identity/receipt
// id is rendered or retained. A successful/idempotent response triggers a
// fresh operational read, plus a sanitized readiness read for the four pairs
// readiness supports (event.correct performs only the operational refresh).
import { useCallback, useState } from 'react';
import { supervisorApi } from '../../services/supervisorApi';
import { useMutationControl } from '../operator-actions/useMutationControl';
import { MutationFeedback } from '../operator-actions/MutationFeedback';
import type { OperationalEvent, Incident } from '../../types/operations';
import type { ReportEntry } from '../../services/operatorApi';
import type { ApprovalAction, ApprovalRecordType } from '../../types/supervisorContracts';

interface ApprovalActionsProps {
  events: OperationalEvent[];
  incidents: Incident[];
  reports: ReportEntry[];
  onRefresh: () => Promise<void>;
}

const PAIRS: { recordType: ApprovalRecordType; action: ApprovalAction; label: string }[] = [
  { recordType: 'OperationalEvent', action: 'event.confirm', label: 'Event confirm' },
  { recordType: 'OperationalEvent', action: 'event.correct', label: 'Event correct' },
  { recordType: 'Task', action: 'task.create', label: 'Task create (by intent id)' },
  { recordType: 'Incident', action: 'incident.acknowledge', label: 'Incident acknowledge' },
  { recordType: 'Report', action: 'report.approve', label: 'Report approve' }
];

export function ApprovalActions({ events, incidents, reports, onRefresh }: ApprovalActionsProps) {
  const [pairIndex, setPairIndex] = useState(0);
  const [recordId, setRecordId] = useState('');
  const pair = PAIRS[pairIndex];

  const targets = pair.recordType === 'OperationalEvent' ? events
    : pair.recordType === 'Incident' ? incidents
    : pair.recordType === 'Report' ? reports
    : null;

  const doCreate = useCallback(async () => {
    if (!recordId.trim()) return;
    await supervisorApi.createApproval({ record_type: pair.recordType, action: pair.action, record_id: recordId.trim() });
    if (pair.action !== 'event.correct') {
      await supervisorApi.getApprovalReadiness({ record_type: pair.recordType, record_id: recordId.trim(), action: pair.action });
    }
  }, [pair, recordId]);

  const control = useMutationControl(doCreate, onRefresh);
  const disabled = control.isSubmitting || control.isLockedOut;

  return (
    <div className="action-group">
      <form
        aria-label="Create approval receipt"
        className="action-form"
        onSubmit={async (e) => { e.preventDefault(); await control.submit(); }}
      >
        <h3 className="form-legend">Approval receipt</h3>
        <label htmlFor="approval-pair" className="form-label">Target pair</label>
        <select
          id="approval-pair"
          value={pairIndex}
          onChange={(e) => { setPairIndex(Number(e.target.value)); setRecordId(''); control.reset(); }}
          disabled={disabled}
          className="form-input"
        >
          {PAIRS.map((p, i) => (
            <option key={p.action} value={i}>{p.label}</option>
          ))}
        </select>

        {targets ? (
          <>
            <label htmlFor="approval-record" className="form-label">Record</label>
            <select
              id="approval-record"
              value={recordId}
              onChange={(e) => { setRecordId(e.target.value); control.reset(); }}
              disabled={disabled}
              aria-describedby={control.feedbackId}
              className="form-input"
            >
              <option value="">Select…</option>
              {targets.map((t: OperationalEvent | Incident | ReportEntry) => {
                const id = 'event_id' in t ? t.event_id : 'incident_id' in t ? t.incident_id : t.report_id;
                const label = 'title' in t ? t.title : 'summary' in t ? t.summary : `Report ${t.version}`;
                return <option key={id} value={id}>{label}</option>;
              })}
            </select>
          </>
        ) : (
          <>
            <label htmlFor="approval-intent-id" className="form-label">Stored task-creation intent id</label>
            <input
              id="approval-intent-id"
              type="text"
              value={recordId}
              onChange={(e) => { setRecordId(e.target.value); control.reset(); }}
              disabled={disabled}
              aria-describedby={control.feedbackId}
              className="form-input"
              placeholder="intent_id"
            />
          </>
        )}

        <button
          type="submit"
          disabled={disabled || !recordId.trim()}
          aria-busy={control.isSubmitting}
          className="form-btn form-btn--primary"
        >
          {control.isSubmitting ? 'Creating…' : 'Create approval receipt'}
        </button>
        <MutationFeedback
          id={control.feedbackId}
          state={control.state}
          onRefreshAndUnlock={() => void control.refreshAndUnlock()}
        />
      </form>
    </div>
  );
}
