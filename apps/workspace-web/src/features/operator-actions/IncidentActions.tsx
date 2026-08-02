// P2C-MUTATION-FULL-UI-C3C (WO C3C-BUILD-REV-F4/REREV-F1/F3): Incident
// reporting and operator transitions. REPORTED->ACKNOWLEDGED is a C3d
// supervisor-only action; operators wait for it, then may transition
// ACKNOWLEDGED->MITIGATING/RESOLVED and RESOLVED->CLOSED. useMutationControl
// owns post-success/conflict refresh.
import { useCallback, useState } from 'react';
import { operatorApi } from '../../services/operatorApi';
import { useMutationControl } from './useMutationControl';
import { MutationFeedback } from './MutationFeedback';
import { OPERATOR_INCIDENT_LIFECYCLE } from './types';
import type { Incident, IncidentStatus, RiskClass } from '../../types/operations';

const RISK_CLASSES: RiskClass[] = ['R0', 'R1', 'R2', 'R3'];

interface IncidentActionsProps {
  shiftId: string;
  incidents: Incident[];
  onRefresh: () => Promise<void>;
}

export function IncidentActions({ shiftId, incidents, onRefresh }: IncidentActionsProps) {
  const [summary, setSummary] = useState('');
  const [riskClass, setRiskClass] = useState<RiskClass>('R1');
  const [description, setDescription] = useState('');

  const doReport = useCallback(async () => {
    await operatorApi.reportIncident(shiftId, summary.trim(), riskClass, description.trim() || undefined);
    setSummary('');
    setDescription('');
    setRiskClass('R1');
  }, [shiftId, summary, riskClass, description]);

  const reportControl = useMutationControl(doReport, onRefresh);
  const reportDisabled = reportControl.isSubmitting || reportControl.isLockedOut;

  const handleReportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!summary.trim()) return;
    await reportControl.submit();
  };

  return (
    <div className="action-group">
      <form aria-label="Report incident" className="action-form" onSubmit={handleReportSubmit}>
        <h3 className="form-legend">Report Incident</h3>
        <label htmlFor="inc-summary" className="form-label">Summary</label>
        <input
          id="inc-summary"
          type="text"
          value={summary}
          onChange={(e) => { setSummary(e.target.value); reportControl.reset(); }}
          required
          disabled={reportDisabled}
          maxLength={300}
          aria-describedby={reportControl.feedbackId}
          className="form-input"
        />
        <label htmlFor="inc-risk" className="form-label">Risk class</label>
        <select
          id="inc-risk"
          value={riskClass}
          onChange={(e) => { setRiskClass(e.target.value as RiskClass); reportControl.reset(); }}
          disabled={reportDisabled}
          className="form-input"
        >
          {RISK_CLASSES.map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
        <label htmlFor="inc-desc" className="form-label">Description (optional)</label>
        <textarea
          id="inc-desc"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={reportDisabled}
          rows={2}
          maxLength={1000}
          className="form-input form-input--textarea"
        />
        <button
          type="submit"
          disabled={reportDisabled || !summary.trim()}
          aria-busy={reportControl.isSubmitting}
          className="form-btn form-btn--primary"
        >
          {reportControl.isSubmitting ? 'Reporting…' : 'Report incident'}
        </button>
        <MutationFeedback
          id={reportControl.feedbackId}
          state={reportControl.state}
          onRefreshAndUnlock={() => void reportControl.refreshAndUnlock()}
        />
      </form>

      {incidents.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <h3 className="form-legend">Incident Transitions</h3>
          <ul className="incident-list" aria-label="Incident list">
            {incidents.map((inc) => (
              <IncidentItem key={inc.incident_id} incident={inc} onRefresh={onRefresh} />
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function IncidentItem({ incident, onRefresh }: { incident: Incident; onRefresh: () => Promise<void> }) {
  const legalTargets = OPERATOR_INCIDENT_LIFECYCLE[incident.status];
  const [targetStatus, setTargetStatus] = useState<IncidentStatus | ''>(legalTargets[0] ?? '');

  const doTransition = useCallback(async () => {
    if (!targetStatus) return;
    await operatorApi.transitionIncident(incident.incident_id, targetStatus, incident.version);
  }, [incident.incident_id, incident.version, targetStatus]);

  const control = useMutationControl(doTransition, onRefresh);
  const disabled = control.isSubmitting || control.isLockedOut;

  return (
    <li className="incident-list__item">
      <span className="incident-list__summary">{incident.summary}</span>
      <span className="incident-list__status status-badge">{incident.status}</span>
      {incident.status === 'REPORTED' && (
        <p role="status" aria-live="polite" className="approval-notice">
          Waiting for supervisor acknowledgement before operator actions become available.
        </p>
      )}
      {legalTargets.length > 0 && (
        <form
          aria-label={`Transition incident ${incident.summary}`}
          className="action-form action-form--inline"
          onSubmit={async (e) => { e.preventDefault(); await control.submit(); }}
        >
          <select
            aria-label={`Target status for ${incident.summary}`}
            value={targetStatus}
            onChange={(e) => { setTargetStatus(e.target.value as IncidentStatus); control.reset(); }}
            disabled={disabled}
            aria-describedby={control.feedbackId}
            className="form-input form-input--inline"
          >
            {legalTargets.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <button
            type="submit"
            disabled={disabled}
            aria-busy={control.isSubmitting}
            className="form-btn form-btn--small"
          >
            {control.isSubmitting ? 'Saving…' : 'Update'}
          </button>
          <MutationFeedback
            id={control.feedbackId}
            state={control.state}
            onRefreshAndUnlock={() => void control.refreshAndUnlock()}
          />
        </form>
      )}
    </li>
  );
}
