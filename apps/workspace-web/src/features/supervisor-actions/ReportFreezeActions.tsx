// P2C-MUTATION-FULL-UI-C3D (SPEC R5/R6): Report approve, approval revocation
// via successor creation only (no fake revoke endpoint), and Shift freeze.
// Freeze sends only expected_version - the retired override fields never
// appear in this DTO, control or request body.
import { useCallback, useState } from 'react';
import { supervisorApi } from '../../services/supervisorApi';
import { useMutationControl } from '../operator-actions/useMutationControl';
import { MutationFeedback } from '../operator-actions/MutationFeedback';
import type { Shift } from '../../types/operations';
import type { ReportEntry } from '../../services/operatorApi';

interface ReportFreezeActionsProps {
  selectedShift: Shift | null;
  reports: ReportEntry[];
  onRefresh: () => Promise<void>;
}

export function ReportFreezeActions({ selectedShift, reports, onRefresh }: ReportFreezeActionsProps) {
  const currentReport = reports.find((r) => r.is_current) ?? null;

  return (
    <div className="action-group">
      <h3 className="form-legend">Report approval</h3>
      {!currentReport && <p>No current report for this shift.</p>}
      {currentReport && currentReport.status === 'IN_REVIEW' && (
        <ReportApproveForm report={currentReport} onRefresh={onRefresh} />
      )}
      {currentReport && currentReport.status === 'APPROVED' && (
        <ReportRevokeForm report={currentReport} onRefresh={onRefresh} />
      )}
      {currentReport && currentReport.status !== 'IN_REVIEW' && currentReport.status !== 'APPROVED' && (
        <p role="status" className="approval-notice">Report status is {currentReport.status}; no supervisor action available.</p>
      )}

      <h3 className="form-legend">Shift freeze</h3>
      {selectedShift && <FreezeForm shift={selectedShift} onRefresh={onRefresh} />}
    </div>
  );
}

function ReportApproveForm({ report, onRefresh }: { report: ReportEntry; onRefresh: () => Promise<void> }) {
  const doApprove = useCallback(async () => {
    await supervisorApi.approveReport(report.report_id, { expected_version: report.version, expected_status: report.status });
  }, [report.report_id, report.version, report.status]);
  const control = useMutationControl(doApprove, onRefresh);
  const disabled = control.isSubmitting || control.isLockedOut;

  return (
    <form aria-label="Approve report" className="action-form action-form--inline" onSubmit={async (e) => { e.preventDefault(); await control.submit(); }}>
      <button type="submit" disabled={disabled} aria-busy={control.isSubmitting} className="form-btn form-btn--primary">
        {control.isSubmitting ? 'Approving…' : 'Approve report'}
      </button>
      <MutationFeedback id={control.feedbackId} state={control.state} onRefreshAndUnlock={() => void control.refreshAndUnlock()} />
    </form>
  );
}

function ReportRevokeForm({ report, onRefresh }: { report: ReportEntry; onRefresh: () => Promise<void> }) {
  const [reason, setReason] = useState('');
  const doRevoke = useCallback(async () => {
    if (!reason.trim()) return;
    await supervisorApi.createReportVersion(report.report_id, {
      reason: reason.trim(),
      expected_version: report.version,
      expected_status: report.status
    });
    setReason('');
  }, [report.report_id, report.version, report.status, reason]);
  const control = useMutationControl(doRevoke, onRefresh);
  const disabled = control.isSubmitting || control.isLockedOut;

  return (
    <form aria-label="Revoke report approval" className="action-form" onSubmit={async (e) => { e.preventDefault(); await control.submit(); }}>
      <label htmlFor="revoke-reason" className="form-label">Revocation reason</label>
      <input
        id="revoke-reason"
        type="text"
        value={reason}
        onChange={(e) => { setReason(e.target.value); control.reset(); }}
        required
        disabled={disabled}
        maxLength={500}
        aria-describedby={control.feedbackId}
        className="form-input"
      />
      <button type="submit" disabled={disabled || !reason.trim()} aria-busy={control.isSubmitting} className="form-btn form-btn--primary">
        {control.isSubmitting ? 'Revoking…' : 'Revoke approval (new successor)'}
      </button>
      <MutationFeedback id={control.feedbackId} state={control.state} onRefreshAndUnlock={() => void control.refreshAndUnlock()} />
    </form>
  );
}

function FreezeForm({ shift, onRefresh }: { shift: Shift; onRefresh: () => Promise<void> }) {
  const doFreeze = useCallback(async () => {
    await supervisorApi.freezeShift(shift.shift_id, { expected_version: shift.version });
  }, [shift.shift_id, shift.version]);
  const control = useMutationControl(doFreeze, onRefresh);
  const disabled = control.isSubmitting || control.isLockedOut || shift.status !== 'CLOSED';

  return (
    <form aria-label="Freeze shift" className="action-form action-form--inline" onSubmit={async (e) => { e.preventDefault(); await control.submit(); }}>
      <button type="submit" disabled={disabled} aria-busy={control.isSubmitting} className="form-btn form-btn--primary">
        {control.isSubmitting ? 'Freezing…' : 'Freeze shift'}
      </button>
      {shift.status !== 'CLOSED' && <p role="status" className="approval-notice">Shift must be CLOSED before it can be frozen.</p>}
      <MutationFeedback id={control.feedbackId} state={control.state} onRefreshAndUnlock={() => void control.refreshAndUnlock()} />
    </form>
  );
}
