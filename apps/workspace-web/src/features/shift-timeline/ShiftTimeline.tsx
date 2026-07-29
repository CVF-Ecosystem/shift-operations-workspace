import type { ApiErrorKind } from '../../services/api';
import { AsyncState } from '../../components/AsyncState';
import type { OperationalEvent } from '../../types/operations';

export interface ShiftTimelineProps {
  events: OperationalEvent[];
  loading: boolean;
  errorKind: ApiErrorKind | null;
}

function formatTime(value: string | null): string {
  if (!value) return 'Unscheduled';
  return new Date(value).toLocaleString();
}

export function ShiftTimeline({ events, loading, errorKind }: ShiftTimelineProps) {
  // Only CONFIRMED events reach this component's data source; the API
  // response is trusted as the confirmed-fact boundary (SPEC R10) and is
  // never re-filtered or re-derived here.
  return (
    <section aria-label="Shift timeline" className="shift-timeline">
      <h2>Timeline</h2>
      <AsyncState loading={loading} errorKind={errorKind} isEmpty={events.length === 0} emptyLabel="No confirmed events yet.">
        <ol>
          {events.map((event) => (
            <li key={event.event_id}>
              <time dateTime={event.starts_at ?? undefined}>{formatTime(event.starts_at)}</time>
              <strong>{event.title}</strong>
              <span className="risk-tag">{event.risk_class}</span>
              {event.description && <p>{event.description}</p>}
            </li>
          ))}
        </ol>
      </AsyncState>
    </section>
  );
}
