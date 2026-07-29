import type { ApiErrorKind } from '../../services/api';
import { AsyncState } from '../../components/AsyncState';
import type { Incident } from '../../types/operations';

export interface IncidentSummaryProps {
  incidents: Incident[];
  loading: boolean;
  errorKind: ApiErrorKind | null;
}

function countBy<T extends string>(items: Incident[], select: (incident: Incident) => T): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const item of items) {
    const key = select(item);
    counts[key] = (counts[key] ?? 0) + 1;
  }
  return counts;
}

export function IncidentSummary({ incidents, loading, errorKind }: IncidentSummaryProps) {
  const byStatus = countBy(incidents, (incident) => incident.status);
  const byRisk = countBy(incidents, (incident) => incident.risk_class);

  return (
    <section aria-label="Incident summary" className="incident-summary">
      <h2>Incidents</h2>
      <AsyncState loading={loading} errorKind={errorKind} isEmpty={incidents.length === 0} emptyLabel="No incidents for this shift.">
        <div className="incident-summary__counts">
          <div>
            <h3>By status</h3>
            <ul>
              {Object.entries(byStatus).map(([status, count]) => (
                <li key={status}>
                  {status}: {count}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3>By risk class</h3>
            <ul>
              {Object.entries(byRisk).map(([risk, count]) => (
                <li key={risk}>
                  {risk}: {count}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </AsyncState>
    </section>
  );
}
