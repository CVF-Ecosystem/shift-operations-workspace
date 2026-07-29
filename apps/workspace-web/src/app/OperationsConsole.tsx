import { useCallback, useEffect, useRef, useState } from 'react';
import { api, ApiError, type ApiErrorKind } from '../services/api';
import { clearSession } from '../features/authentication/session';
import { ShiftSelector } from '../features/shift-selection/ShiftSelector';
import { ShiftTimeline } from '../features/shift-timeline/ShiftTimeline';
import { OpenWorkPanel } from '../features/open-work/OpenWorkPanel';
import { IncidentSummary } from '../features/incident-room/IncidentSummary';
import { HandoverSummary } from '../features/shift-handover/HandoverSummary';
import type { Handover, Incident, OpenWorkResponse, OperationalEvent, Shift } from '../types/operations';

export interface OperationsConsoleProps {
  onSignedOut: () => void;
}

interface ShiftDetail {
  events: OperationalEvent[];
  openWork: OpenWorkResponse | null;
  incidents: Incident[];
  handovers: Handover[];
}

const EMPTY_DETAIL: ShiftDetail = { events: [], openWork: null, incidents: [], handovers: [] };

type ConnectionState = 'connecting' | 'offline' | 'error' | 'connected';

const CONNECTION_LABEL: Record<ConnectionState, string> = {
  connecting: 'Connecting…',
  offline: 'Offline',
  error: 'Connection issue',
  connected: 'Connected'
};

function deriveConnectionState(loading: boolean, errorKind: ApiErrorKind | null): ConnectionState {
  if (loading) return 'connecting';
  if (errorKind === 'network') return 'offline';
  if (errorKind) return 'error';
  return 'connected';
}

export function OperationsConsole({ onSignedOut }: OperationsConsoleProps) {
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [shiftsLoading, setShiftsLoading] = useState(true);
  const [shiftsError, setShiftsError] = useState<ApiErrorKind | null>(null);

  const [selectedShiftId, setSelectedShiftId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ShiftDetail>(EMPTY_DETAIL);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<ApiErrorKind | null>(null);

  const requestToken = useRef(0);

  const signOut = useCallback(() => {
    clearSession();
    onSignedOut();
  }, [onSignedOut]);

  const handleFailure = useCallback(
    (cause: unknown): ApiErrorKind => {
      if (cause instanceof ApiError) {
        if (cause.kind === 'unauthorized') signOut();
        return cause.kind;
      }
      return 'server';
    },
    [signOut]
  );

  useEffect(() => {
    let cancelled = false;
    setShiftsLoading(true);
    setShiftsError(null);
    api
      .listShifts()
      .then((result) => {
        if (cancelled) return;
        setShifts(result);
      })
      .catch((cause) => {
        if (cancelled) return;
        setShiftsError(handleFailure(cause));
      })
      .finally(() => {
        if (!cancelled) setShiftsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [handleFailure]);

  useEffect(() => {
    if (!selectedShiftId) {
      setDetail(EMPTY_DETAIL);
      return;
    }

    // Stale-response suppression: only the latest request's resolution is
    // allowed to commit state, so switching shifts quickly cannot let an
    // earlier in-flight response overwrite a later one.
    const token = ++requestToken.current;
    const controller = new AbortController();
    setDetailLoading(true);
    setDetailError(null);

    Promise.all([
      api.listEvents(selectedShiftId, controller.signal),
      api.getOpenWork(selectedShiftId, controller.signal),
      api.listIncidents(selectedShiftId, controller.signal),
      api.listHandovers(selectedShiftId, controller.signal)
    ])
      .then(([events, openWork, incidents, handovers]) => {
        if (requestToken.current !== token) return;
        setDetail({
          events: events.filter((event) => event.state === 'CONFIRMED'),
          openWork,
          incidents,
          handovers
        });
      })
      .catch((cause) => {
        if (requestToken.current !== token) return;
        if (cause instanceof ApiError && cause.kind === 'cancelled') return;
        setDetailError(handleFailure(cause));
      })
      .finally(() => {
        if (requestToken.current === token) setDetailLoading(false);
      });

    return () => {
      controller.abort();
    };
  }, [selectedShiftId, handleFailure]);

  const connectionState = deriveConnectionState(shiftsLoading || detailLoading, shiftsError ?? detailError);

  return (
    <main className="operations-console">
      <header>
        <strong>Operations Console</strong>
        <span role="status" aria-live="polite" className={`connection-indicator connection-indicator--${connectionState}`}>
          <span aria-hidden="true" className="connection-indicator__dot" />
          Session: signed in · {CONNECTION_LABEL[connectionState]}
        </span>
        <button type="button" onClick={signOut}>
          Sign out
        </button>
      </header>
      <ShiftSelector
        shifts={shifts}
        selectedShiftId={selectedShiftId}
        loading={shiftsLoading}
        errorKind={shiftsError}
        onSelect={setSelectedShiftId}
      />
      {selectedShiftId && (
        <div className="operations-console__panels">
          <ShiftTimeline events={detail.events} loading={detailLoading} errorKind={detailError} />
          <OpenWorkPanel openWork={detail.openWork} loading={detailLoading} errorKind={detailError} />
          <IncidentSummary incidents={detail.incidents} loading={detailLoading} errorKind={detailError} />
          <HandoverSummary handovers={detail.handovers} loading={detailLoading} errorKind={detailError} />
        </div>
      )}
    </main>
  );
}
