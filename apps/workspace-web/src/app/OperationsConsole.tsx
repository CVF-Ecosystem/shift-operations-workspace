// P2C-MUTATION-FULL-UI-C3C (SPEC R18/R19/D6): OperationsConsole is a coordinator.
// Delegates data fetching to useOperationsData and operator actions to OperatorActions.
// All mutation state is ephemeral React state (SPEC R19/AC-27).
import { useCallback, useEffect, useState } from 'react';
import { api, ApiError, type ApiErrorKind } from '../services/api';
import { clearSession } from '../features/authentication/session';
import { ShiftSelector } from '../features/shift-selection/ShiftSelector';
import { ShiftTimeline } from '../features/shift-timeline/ShiftTimeline';
import { OpenWorkPanel } from '../features/open-work/OpenWorkPanel';
import { IncidentSummary } from '../features/incident-room/IncidentSummary';
import { HandoverSummary } from '../features/shift-handover/HandoverSummary';
import { useOperationsData } from './useOperationsData';
import { OperatorActions } from '../features/operator-actions/OperatorActions';
import type { Shift } from '../types/operations';

export interface OperationsConsoleProps {
  onSignedOut: () => void;
}

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

  const refreshShifts = useCallback(async (): Promise<void> => {
    try {
      const result = await api.listShifts();
      setShifts(result);
    } catch (cause) {
      handleFailure(cause);
      throw cause;
    }
  }, [handleFailure]);

  const dataState = useOperationsData(selectedShiftId, handleFailure);
  const selectedShift = shifts.find((s) => s.shift_id === selectedShiftId) ?? null;

  const refreshAll = useCallback(async (): Promise<void> => {
    await Promise.all([dataState.refresh(), refreshShifts()]);
  }, [dataState, refreshShifts]);

  const connectionState = deriveConnectionState(
    shiftsLoading || dataState.loading,
    shiftsError ?? dataState.errorKind
  );

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
          <ShiftTimeline events={dataState.events} loading={dataState.loading} errorKind={dataState.errorKind} />
          <OpenWorkPanel openWork={dataState.openWork} loading={dataState.loading} errorKind={dataState.errorKind} />
          <IncidentSummary incidents={dataState.incidents} loading={dataState.loading} errorKind={dataState.errorKind} />
          <HandoverSummary handovers={dataState.handovers} loading={dataState.loading} errorKind={dataState.errorKind} />
        </div>
      )}
      <OperatorActions
        // WO C3C-BUILD-REREREV-F2: keying by selected shift forces React to
        // unmount/remount the whole operator mutation subtree on shift
        // change, resetting every local useState (form fields, retained
        // task intent_id, useMutationControl lock/feedback state) instead of
        // reusing component instances across a shift boundary they were
        // never scoped to.
        key={selectedShiftId ?? 'no-shift'}
        selectedShiftId={selectedShiftId}
        selectedShift={selectedShift}
        shifts={shifts}
        messages={dataState.messages}
        tasks={dataState.tasks}
        customerRequests={dataState.customerRequests}
        incidents={dataState.incidents}
        handovers={dataState.handovers}
        reports={dataState.reports}
        capabilities={dataState.capabilities}
        onShiftCreated={(s) => { setSelectedShiftId(s.shift_id); void refreshShifts(); }}
        onRefresh={refreshAll}
      />
    </main>
  );
}
