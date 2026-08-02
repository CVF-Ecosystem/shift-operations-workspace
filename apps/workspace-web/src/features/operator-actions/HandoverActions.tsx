// P2C-MUTATION-FULL-UI-C3C (SPEC R18/R20, WO C3C-BUILD-REV-F4): Create
// handover action. Destination selection is reconciled whenever fromShiftId
// or the available destination set changes, so a stale or self-target
// selection can never be submitted (backend also rejects from==to and a
// non-OPEN destination, but the UI must not offer it in the first place).
import { useCallback, useEffect, useState } from 'react';
import { operatorApi } from '../../services/operatorApi';
import { useMutationControl } from './useMutationControl';
import { MutationFeedback } from './MutationFeedback';
import type { Shift } from '../../types/operations';

interface HandoverActionsProps {
  fromShiftId: string;
  shifts: Shift[];
  onRefresh: () => Promise<void>;
}

export function HandoverActions({ fromShiftId, shifts, onRefresh }: HandoverActionsProps) {
  const destinations = shifts.filter((s) => s.shift_id !== fromShiftId && s.status === 'OPEN');
  const [toShiftId, setToShiftId] = useState(destinations[0]?.shift_id ?? '');

  useEffect(() => {
    if (!destinations.some((s) => s.shift_id === toShiftId)) {
      setToShiftId(destinations[0]?.shift_id ?? '');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fromShiftId, destinations.map((s) => s.shift_id).join(',')]);

  const doCreate = useCallback(async () => {
    if (!toShiftId || toShiftId === fromShiftId) return;
    await operatorApi.createHandover(fromShiftId, toShiftId);
  }, [fromShiftId, toShiftId]);

  const control = useMutationControl(doCreate, onRefresh);
  const disabled = control.isSubmitting || control.isLockedOut;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!toShiftId || toShiftId === fromShiftId) return;
    await control.submit();
  };

  if (destinations.length === 0) {
    return (
      <div className="action-group">
        <h3 className="form-legend">Create Handover</h3>
        <p className="async-state async-state--empty">No destination shifts available for handover.</p>
      </div>
    );
  }

  return (
    <div className="action-group">
      <form aria-label="Create handover" className="action-form" onSubmit={handleSubmit}>
        <h3 className="form-legend">Create Handover</h3>
        <label htmlFor="handover-to-shift" className="form-label">Destination shift</label>
        <select
          id="handover-to-shift"
          value={toShiftId}
          onChange={(e) => { setToShiftId(e.target.value); control.reset(); }}
          disabled={disabled}
          aria-describedby={control.feedbackId}
          className="form-input"
        >
          {destinations.map((s) => (
            <option key={s.shift_id} value={s.shift_id}>{s.name}</option>
          ))}
        </select>
        <button
          type="submit"
          disabled={disabled || !toShiftId}
          aria-busy={control.isSubmitting}
          className="form-btn form-btn--primary"
        >
          {control.isSubmitting ? 'Creating…' : 'Create handover'}
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
