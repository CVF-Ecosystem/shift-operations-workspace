// P2C-MUTATION-FULL-UI-C3C (WO C3C-BUILD-REV-F2/F4/REREV-F1): Report
// actions - generate, successor version, submit. snapshot_digest is NEVER
// rendered or stored. Backend status is exactly DRAFT|IN_REVIEW|APPROVED|
// FROZEN (never REVIEW_REQUESTED). "Generate" is offered only when no
// current report exists; once one exists, only successor-version creates a
// new one. All three controls share a disable lock so only one is ever
// in-flight/locked at a time. useMutationControl owns post-success/conflict
// refresh via the real Promise<void> onRefresh.
import { useCallback } from 'react';
import { operatorApi, type ReportEntry } from '../../services/operatorApi';
import { useMutationControl } from './useMutationControl';
import { MutationFeedback } from './MutationFeedback';

interface ReportActionsProps {
  shiftId: string;
  reports: ReportEntry[];
  onRefresh: () => Promise<void>;
}

export function ReportActions({ shiftId, reports, onRefresh }: ReportActionsProps) {
  const current = reports.find((r) => r.is_current) ?? null;
  const canVersion = current?.status === 'DRAFT' || current?.status === 'IN_REVIEW';
  const canSubmit = current?.status === 'DRAFT';

  const doGenerate = useCallback(async () => {
    await operatorApi.generateReport(shiftId);
  }, [shiftId]);

  const doVersion = useCallback(async () => {
    if (!current) return;
    await operatorApi.createReportVersion(current.report_id, current.version, current.status);
  }, [current]);

  const doSubmit = useCallback(async () => {
    if (!current) return;
    await operatorApi.submitReport(current.report_id, current.version, current.status);
  }, [current]);

  const genControl = useMutationControl(doGenerate, onRefresh);
  const verControl = useMutationControl(doVersion, onRefresh);
  const subControl = useMutationControl(doSubmit, onRefresh);

  const anyBusy =
    genControl.isSubmitting || verControl.isSubmitting || subControl.isSubmitting ||
    genControl.isLockedOut || verControl.isLockedOut || subControl.isLockedOut;

  return (
    <section aria-label="End-shift report" className="report-panel action-group">
      <h3 className="form-legend">End-shift Report</h3>

      {reports.length === 0 && (
        <p className="async-state async-state--empty">No report generated yet.</p>
      )}

      {current && (
        <dl className="report-meta">
          <dt>Version</dt>
          <dd>{current.version}</dd>
          <dt>Status</dt>
          <dd><span className="status-badge">{current.status}</span></dd>
          <dt>Generated</dt>
          <dd>{new Date(current.generated_from_cutoff).toLocaleString()}</dd>
          <dt>Sections</dt>
          <dd>{current.sections.length}</dd>
        </dl>
      )}

      <div className="report-actions" role="group" aria-label="Report actions">
        {!current && (
          <>
            <button
              type="button"
              onClick={() => void genControl.submit()}
              disabled={anyBusy}
              aria-busy={genControl.isSubmitting}
              aria-describedby={genControl.feedbackId}
              className="form-btn form-btn--primary"
            >
              {genControl.isSubmitting ? 'Generating…' : 'Generate report'}
            </button>
            <MutationFeedback
              id={genControl.feedbackId}
              state={genControl.state}
              onRefreshAndUnlock={() => void genControl.refreshAndUnlock()}
            />
          </>
        )}

        {canVersion && (
          <>
            <button
              type="button"
              onClick={() => void verControl.submit()}
              disabled={anyBusy}
              aria-busy={verControl.isSubmitting}
              aria-describedby={verControl.feedbackId}
              className="form-btn"
            >
              {verControl.isSubmitting ? 'Versioning…' : 'Create new version'}
            </button>
            <MutationFeedback
              id={verControl.feedbackId}
              state={verControl.state}
              onRefreshAndUnlock={() => void verControl.refreshAndUnlock()}
            />

          </>
        )}

        {canSubmit && (
          <>
            <button type="button" onClick={() => void subControl.submit()} disabled={anyBusy}
              aria-busy={subControl.isSubmitting} aria-describedby={subControl.feedbackId} className="form-btn">
              {subControl.isSubmitting ? 'Submitting…' : 'Submit for review'}
            </button>
            <MutationFeedback id={subControl.feedbackId} state={subControl.state}
              onRefreshAndUnlock={() => void subControl.refreshAndUnlock()} />
          </>
        )}

        {current && current.status === 'IN_REVIEW' && (
          <p role="status" aria-live="polite" className="approval-notice">
            Report submitted for supervisor review. Approval is a supervisor action (C3d).
          </p>
        )}
        {current && current.status === 'APPROVED' && (
          <p role="status" className="status-notice status-notice--success">Report approved.</p>
        )}
        {current && current.status === 'FROZEN' && (
          <p role="status" className="status-notice status-notice--success">Report frozen.</p>
        )}
      </div>
    </section>
  );
}
