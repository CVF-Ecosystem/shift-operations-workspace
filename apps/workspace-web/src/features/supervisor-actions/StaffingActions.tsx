// P2C-MUTATION-FULL-UI-C3D (SPEC R2, ADR D1): staffing control plane. Lists
// shifts/active users via the supervisor-only exception, shows ACTIVE/REVOKED
// assignment history for a chosen staffing shift, assigns a selected active
// user_id, and revokes only with the stored assignment id/version. Success
// refreshes both staffing state and the ordinary assignment-scoped shift list
// (never fetches operational records through this exception).
import { useCallback, useEffect, useRef, useState } from 'react';
import { supervisorApi } from '../../services/supervisorApi';
import { ApiError } from '../../services/api';
import { useMutationControl } from '../operator-actions/useMutationControl';
import { MutationFeedback } from '../operator-actions/MutationFeedback';
import type { ShiftAssignment, StaffingShift, StaffingUser } from '../../types/supervisorContracts';

interface StaffingActionsProps {
  staffingShifts: StaffingShift[];
  staffingUsers: StaffingUser[];
  staffingAvailable: boolean;
  onStaffingRefresh: () => Promise<void>;
}

export function StaffingActions({ staffingShifts, staffingUsers, staffingAvailable, onStaffingRefresh }: StaffingActionsProps) {
  const [targetShiftId, setTargetShiftId] = useState<string>('');
  const [assignments, setAssignments] = useState<ShiftAssignment[]>([]);
  const [assignmentsError, setAssignmentsError] = useState<string | null>(null);
  const [selectedUserId, setSelectedUserId] = useState<string>('');
  const assignmentRequestToken = useRef(0);
  const latestTargetShiftId = useRef('');

  const loadAssignments = useCallback(async () => {
    const shiftId = targetShiftId;
    const token = ++assignmentRequestToken.current;
    if (!shiftId) {
      setAssignments([]);
      setAssignmentsError(null);
      return;
    }
    try {
      const result = await supervisorApi.listAssignments(shiftId);
      if (assignmentRequestToken.current !== token || latestTargetShiftId.current !== shiftId) return;
      setAssignments(result);
      setAssignmentsError(null);
    } catch (cause) {
      if (assignmentRequestToken.current !== token || latestTargetShiftId.current !== shiftId) return;
      setAssignments([]);
      setAssignmentsError(cause instanceof ApiError ? cause.kind : 'server');
    }
  }, [targetShiftId]);

  useEffect(() => {
    void loadAssignments();
  }, [loadAssignments]);

  const refreshAssignmentsAndStaffing = useCallback(async () => {
    await Promise.all([loadAssignments(), onStaffingRefresh()]);
  }, [loadAssignments, onStaffingRefresh]);

  const doAssign = useCallback(async () => {
    if (!targetShiftId || !selectedUserId) return;
    await supervisorApi.assignUser(targetShiftId, selectedUserId);
    setSelectedUserId('');
  }, [targetShiftId, selectedUserId]);

  const assignControl = useMutationControl(doAssign, refreshAssignmentsAndStaffing);
  const assignDisabled = assignControl.isSubmitting || assignControl.isLockedOut;

  if (!staffingAvailable) {
    return (
      <div className="action-group">
        <p role="status" className="approval-notice">Staffing control is unavailable for your current role.</p>
      </div>
    );
  }

  return (
    <div className="action-group" key={targetShiftId || 'no-staffing-shift'}>
      <form aria-label="Choose staffing shift" className="action-form" onSubmit={(e) => e.preventDefault()}>
        <h3 className="form-legend">Staffing</h3>
        <label htmlFor="staffing-shift" className="form-label">Shift</label>
        <select
          id="staffing-shift"
          value={targetShiftId}
          onChange={(e) => {
            latestTargetShiftId.current = e.target.value;
            assignmentRequestToken.current += 1;
            setTargetShiftId(e.target.value); setSelectedUserId(''); assignControl.reset();
          }}
          className="form-input"
        >
          <option value="">Select a shift…</option>
          {staffingShifts.map((s) => (
            <option key={s.shift_id} value={s.shift_id}>{s.name} ({s.status})</option>
          ))}
        </select>
      </form>

      {targetShiftId && (
        <>
          <form
            aria-label="Assign user"
            className="action-form action-form--inline"
            onSubmit={async (e) => { e.preventDefault(); await assignControl.submit(); }}
          >
            <label htmlFor="staffing-user" className="form-label">Active user</label>
            <select
              id="staffing-user"
              value={selectedUserId}
              onChange={(e) => { setSelectedUserId(e.target.value); assignControl.reset(); }}
              disabled={assignDisabled}
              aria-describedby={assignControl.feedbackId}
              className="form-input form-input--inline"
            >
              <option value="">Select a user…</option>
              {staffingUsers.map((u) => (
                <option key={u.user_id} value={u.user_id}>{u.username} ({u.role})</option>
              ))}
            </select>
            <button
              type="submit"
              disabled={assignDisabled || !selectedUserId}
              aria-busy={assignControl.isSubmitting}
              className="form-btn form-btn--primary"
            >
              {assignControl.isSubmitting ? 'Assigning…' : 'Assign'}
            </button>
            <MutationFeedback
              id={assignControl.feedbackId}
              state={assignControl.state}
              onRefreshAndUnlock={() => void assignControl.refreshAndUnlock()}
            />
          </form>

          <h4 className="form-legend">Assignment history</h4>
          {assignmentsError && <p role="alert" className="mutation-feedback mutation-feedback--error">Could not load assignment history.</p>}
          {!assignmentsError && assignments.length === 0 && <p>No assignments yet.</p>}
          {!assignmentsError && assignments.length > 0 && (
            <ul className="incident-list" aria-label="Assignment history">
              {assignments.map((a) => (
                <AssignmentItem
                  key={a.assignment_id}
                  assignment={a}
                  shiftId={targetShiftId}
                  onRefresh={refreshAssignmentsAndStaffing}
                />
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}

function AssignmentItem({
  assignment,
  shiftId,
  onRefresh
}: {
  assignment: ShiftAssignment;
  shiftId: string;
  onRefresh: () => Promise<void>;
}) {
  const doRevoke = async () => {
    await supervisorApi.revokeAssignment(shiftId, assignment.assignment_id, assignment.version);
  };
  const control = useMutationControl(doRevoke, onRefresh);
  const disabled = control.isSubmitting || control.isLockedOut;

  return (
    <li className="incident-list__item">
      <span className="incident-list__summary">{assignment.user_id}</span>
      <span className="incident-list__status status-badge">{assignment.status}</span>
      {assignment.status === 'ACTIVE' && (
        <form
          aria-label={`Revoke assignment for ${assignment.user_id}`}
          className="action-form action-form--inline"
          onSubmit={async (e) => { e.preventDefault(); await control.submit(); }}
        >
          <button
            type="submit"
            disabled={disabled}
            aria-busy={control.isSubmitting}
            className="form-btn form-btn--small"
          >
            {control.isSubmitting ? 'Revoking…' : 'Revoke'}
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
