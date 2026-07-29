import type { ApiErrorKind } from '../../services/api';
import { AsyncState } from '../../components/AsyncState';
import type { Shift } from '../../types/operations';

export interface ShiftSelectorProps {
  shifts: Shift[];
  selectedShiftId: string | null;
  loading: boolean;
  errorKind: ApiErrorKind | null;
  onSelect: (shiftId: string) => void;
}

export function ShiftSelector({ shifts, selectedShiftId, loading, errorKind, onSelect }: ShiftSelectorProps) {
  return (
    <section aria-label="Shift selection" className="shift-selector">
      <label htmlFor="shift-select">Shift</label>
      <AsyncState loading={loading} errorKind={errorKind} isEmpty={shifts.length === 0} emptyLabel="No shifts available.">
        <select
          id="shift-select"
          value={selectedShiftId ?? ''}
          onChange={(event) => onSelect(event.target.value)}
        >
          <option value="" disabled>
            Select a shift
          </option>
          {shifts.map((shift) => (
            <option key={shift.shift_id} value={shift.shift_id}>
              {shift.name} · {shift.status}
            </option>
          ))}
        </select>
      </AsyncState>
    </section>
  );
}
