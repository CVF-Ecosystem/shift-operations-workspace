import { useCallback, useEffect, useState } from 'react';
import { api, ApiError, type ApiErrorKind } from '../services/api';
import { clearSession } from '../features/authentication/session';
import { ShiftSelector } from '../features/shift-selection/ShiftSelector';
import { ShiftTimeline } from '../features/shift-timeline/ShiftTimeline';
import { OpenWorkPanel } from '../features/open-work/OpenWorkPanel';
import { IncidentSummary } from '../features/incident-room/IncidentSummary';
import { HandoverSummary } from '../features/shift-handover/HandoverSummary';
import { useOperationsData } from './useOperationsData';
import { useSupervisorData } from './useSupervisorData';
import { OperatorActions } from '../features/operator-actions/OperatorActions';
import { SupervisorActions } from '../features/supervisor-actions/SupervisorActions';
import type { Shift } from '../types/operations';
import { registerRefreshOwner } from '../offline/refreshBridge';
import { serializeRefresh } from '../offline/refreshCoordinator';

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
    clearSession(false);
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
      // C3D-WO-REV-F4: if the currently selected shift is no longer in the
      // refreshed ordinary assignment-scoped list (e.g. a supervisor
      // self-revoked their own assignment), clear selection so the
      // operational hook's own effect clears retained records instead of
      // leaving a stale disclosure on screen.
      setSelectedShiftId((current) => {
        if (current && !result.some((s) => s.shift_id === current)) return null;
        return current;
      });
    } catch (cause) {
      handleFailure(cause);
      throw cause;
    }
  }, [handleFailure]);

  const dataState = useOperationsData(selectedShiftId, handleFailure);
  const supervisorState = useSupervisorData(handleFailure);
  const selectedShift = shifts.find((s) => s.shift_id === selectedShiftId) ?? null;

  const compositeRefresh = useCallback(async (): Promise<void> => {
    await Promise.all([dataState.refresh(), refreshShifts()]);
  }, [dataState, refreshShifts]);

  const refreshAll = useCallback(() => serializeRefresh(compositeRefresh), [compositeRefresh]);

  useEffect(() => registerRefreshOwner(compositeRefresh), [compositeRefresh]);

  const refreshStaffingAndShifts = useCallback(() => serializeRefresh(async () => {
    await Promise.all([supervisorState.refresh(), refreshShifts()]);
  }), [supervisorState, refreshShifts]);

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
          <ShiftTimeline events={dataState.confirmedEvents} loading={dataState.loading} errorKind={dataState.errorKind} />
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
        key={`operator-${selectedShiftId ?? 'no-shift'}`}
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
        onShiftCreated={(s) => { setSelectedShiftId(s.shift_id); void refreshStaffingAndShifts(); }}
        onRefresh={refreshAll}
      />
      <SupervisorActions
        key={`supervisor-${selectedShiftId ?? 'no-shift'}`}
        selectedShiftId={selectedShiftId}
        selectedShift={selectedShift}
        events={dataState.events}
        incidents={dataState.incidents}
        handovers={dataState.handovers}
        reports={dataState.reports}
        staffingShifts={supervisorState.staffingShifts}
        staffingUsers={supervisorState.staffingUsers}
        staffingAvailable={supervisorState.available}
        onStaffingRefresh={refreshStaffingAndShifts}
        onOperationalRefresh={refreshAll}
      />
    </main>
  );
}
