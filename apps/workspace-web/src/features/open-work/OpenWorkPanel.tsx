import type { ApiErrorKind } from '../../services/api';
import { AsyncState } from '../../components/AsyncState';
import type { OpenWorkResponse } from '../../types/operations';

export interface OpenWorkPanelProps {
  openWork: OpenWorkResponse | null;
  loading: boolean;
  errorKind: ApiErrorKind | null;
}

export function OpenWorkPanel({ openWork, loading, errorKind }: OpenWorkPanelProps) {
  const total = openWork ? openWork.tasks.length + openWork.customer_requests.length + openWork.incidents.length : 0;

  return (
    <section aria-label="Open work" className="open-work-panel">
      <h2>Open work</h2>
      <AsyncState loading={loading} errorKind={errorKind} isEmpty={total === 0} emptyLabel="No open work for this shift.">
        <div className="open-work-panel__group">
          <h3>Tasks ({openWork?.tasks.length ?? 0})</h3>
          <ul>
            {openWork?.tasks.map((task) => (
              <li key={task.task_id}>
                <strong>{task.title}</strong> <span>{task.status}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="open-work-panel__group">
          <h3>Customer requests ({openWork?.customer_requests.length ?? 0})</h3>
          <ul>
            {openWork?.customer_requests.map((request) => (
              <li key={request.request_id}>
                <strong>{request.summary}</strong> <span>{request.status}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="open-work-panel__group">
          <h3>Incidents ({openWork?.incidents.length ?? 0})</h3>
          <ul>
            {openWork?.incidents.map((incident) => (
              <li key={incident.incident_id}>
                <strong>{incident.summary}</strong> <span>{incident.status}</span>
              </li>
            ))}
          </ul>
        </div>
      </AsyncState>
    </section>
  );
}
