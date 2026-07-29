import type { ApiErrorKind } from '../../services/api';
import { AsyncState } from '../../components/AsyncState';
import type { Handover } from '../../types/operations';

export interface HandoverSummaryProps {
  handovers: Handover[];
  loading: boolean;
  errorKind: ApiErrorKind | null;
}

export function HandoverSummary({ handovers, loading, errorKind }: HandoverSummaryProps) {
  return (
    <section aria-label="Handover summary" className="handover-summary">
      <h2>Handover</h2>
      <AsyncState loading={loading} errorKind={errorKind} isEmpty={handovers.length === 0} emptyLabel="No handover recorded for this shift.">
        <ul>
          {handovers.map((handover) => (
            <li key={handover.handover_id}>
              <strong>{handover.status}</strong>
              <span> · {handover.items.length} item(s)</span>
              {handover.acknowledged && <span> · acknowledged</span>}
            </li>
          ))}
        </ul>
      </AsyncState>
    </section>
  );
}
