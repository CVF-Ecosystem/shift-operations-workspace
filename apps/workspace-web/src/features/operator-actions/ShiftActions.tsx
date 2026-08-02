// P2C-MUTATION-FULL-UI-C3C (SPEC R18/R20, WO C3C-BUILD-REREV-F1): shift
// create and close actions. Both controls resolve refresh through the real
// Promise<void> onRefresh - useMutationControl awaits it after success and
// auto-runs it once on conflict.
import { useCallback, useState } from 'react';
import { operatorApi } from '../../services/operatorApi';
import { useMutationControl } from './useMutationControl';
import { MutationFeedback } from './MutationFeedback';
import type { Shift } from '../../types/operations';

interface ShiftActionsProps {
  selectedShift: Shift | null;
  onShiftCreated: (shift: Shift) => void;
  onRefresh: () => Promise<void>;
}

export function ShiftActions({ selectedShift, onShiftCreated, onRefresh }: ShiftActionsProps) {
  const [name, setName] = useState('');
  const [startsAt, setStartsAt] = useState('');
  const [endsAt, setEndsAt] = useState('');

  const doCreate = useCallback(async () => {
    const shift = await operatorApi.createShift(name.trim(), startsAt, endsAt);
    onShiftCreated(shift);
  }, [name, startsAt, endsAt, onShiftCreated]);

  const doClose = useCallback(async () => {
    if (!selectedShift) return;
    await operatorApi.closeShift(selectedShift.shift_id, selectedShift.version);
  }, [selectedShift]);

  const createControl = useMutationControl(doCreate, onRefresh);
  const closeControl = useMutationControl(doClose, onRefresh);
  const createDisabled = createControl.isSubmitting || createControl.isLockedOut;
  const closeDisabled = closeControl.isSubmitting || closeControl.isLockedOut;

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !startsAt || !endsAt) return;
    await createControl.submit();
    if (!createControl.isLockedOut) {
      setName('');
      setStartsAt('');
      setEndsAt('');
    }
  };

  const canClose = selectedShift && (selectedShift.status === 'OPEN' || selectedShift.status === 'HANDOVER_PENDING');

  return (
    <div className="action-group">
      <form aria-label="Create shift" className="create-shift-form" onSubmit={handleCreateSubmit}>
        <fieldset disabled={createDisabled} style={{ border: 0, padding: 0 }}>
          <legend className="form-legend">Create Shift</legend>
          <label htmlFor="create-shift-name" className="form-label">Shift name</label>
          <input
            id="create-shift-name"
            type="text"
            value={name}
            onChange={(e) => { setName(e.target.value); createControl.reset(); }}
            required
            maxLength={120}
            aria-describedby={createControl.feedbackId}
            className="form-input"
          />
          <label htmlFor="create-shift-starts" className="form-label">Starts at</label>
          <input
            id="create-shift-starts"
            type="datetime-local"
            value={startsAt}
            onChange={(e) => { setStartsAt(e.target.value); createControl.reset(); }}
            required
            className="form-input"
          />
          <label htmlFor="create-shift-ends" className="form-label">Ends at</label>
          <input
            id="create-shift-ends"
            type="datetime-local"
            value={endsAt}
            onChange={(e) => { setEndsAt(e.target.value); createControl.reset(); }}
            required
            className="form-input"
          />
          <button
            type="submit"
            disabled={createDisabled || !name.trim() || !startsAt || !endsAt}
            aria-busy={createControl.isSubmitting}
            className="form-btn form-btn--primary"
          >
            {createControl.isSubmitting ? 'Creating…' : 'Create shift'}
          </button>
        </fieldset>
        <MutationFeedback
          id={createControl.feedbackId}
          state={createControl.state}
          onRefreshAndUnlock={() => void createControl.refreshAndUnlock()}
        />
      </form>

      {canClose && (
        <div className="close-shift-control" style={{ marginTop: '16px' }}>
          <button
            type="button"
            onClick={() => void closeControl.submit()}
            disabled={closeDisabled}
            aria-busy={closeControl.isSubmitting}
            aria-describedby={closeControl.feedbackId}
            className="form-btn form-btn--danger"
            aria-label={`Close shift ${selectedShift.name}`}
          >
            {closeControl.isSubmitting ? 'Closing…' : 'Close shift'}
          </button>
          <MutationFeedback
            id={closeControl.feedbackId}
            state={closeControl.state}
            onRefreshAndUnlock={() => void closeControl.refreshAndUnlock()}
          />
        </div>
      )}
    </div>
  );
}
