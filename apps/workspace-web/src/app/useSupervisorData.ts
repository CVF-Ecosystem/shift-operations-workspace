// P2C-MUTATION-FULL-UI-C3D (SPEC R2, ADR D1): dedicated staffing-only read
// coordinator, deliberately separate from useOperationsData. A 403 on either
// staffing read means "no staffing surface" - it clears staffing state
// without touching operational state and without any client-side role
// ranking. Mirrors useOperationsData's stale-response suppression via
// requestToken and a real rejecting refresh() Promise.
import { useCallback, useEffect, useRef, useState } from 'react';
import { ApiError, type ApiErrorKind } from '../services/api';
import { supervisorApi } from '../services/supervisorApi';
import type { StaffingShift, StaffingUser } from '../types/supervisorContracts';

export interface SupervisorDataState {
  staffingShifts: StaffingShift[];
  staffingUsers: StaffingUser[];
  available: boolean;
  loading: boolean;
  errorKind: ApiErrorKind | null;
  refresh: () => Promise<void>;
}

const EMPTY_DATA = {
  staffingShifts: [] as StaffingShift[],
  staffingUsers: [] as StaffingUser[]
};

class Superseded extends Error {}

export function useSupervisorData(handleFailure: (cause: unknown) => ApiErrorKind): SupervisorDataState {
  const [data, setData] = useState(EMPTY_DATA);
  const [available, setAvailable] = useState(false);
  const [loading, setLoading] = useState(true);
  const [errorKind, setErrorKind] = useState<ApiErrorKind | null>(null);
  const requestToken = useRef(0);

  const load = useCallback(async (): Promise<void> => {
    const token = ++requestToken.current;
    setLoading(true);
    setErrorKind(null);
    try {
      const [staffingShifts, staffingUsers] = await Promise.all([
        supervisorApi.listStaffingShifts(),
        supervisorApi.listStaffingUsers()
      ]);
      if (requestToken.current !== token) throw new Superseded('staffing refresh superseded before it could commit');
      setData({ staffingShifts, staffingUsers });
      setAvailable(true);
    } catch (cause) {
      if (requestToken.current !== token) throw new Superseded('staffing refresh superseded before failure was observed');
      if (cause instanceof ApiError && cause.kind === 'forbidden') {
        // D1: a 403 on the staffing exception means no staffing surface for
        // this principal - hide it without inventing client role ranking and
        // without treating it as an operational-state error.
        setData(EMPTY_DATA);
        setAvailable(false);
        throw new Superseded('staffing forbidden, not a refresh failure');
      }
      setErrorKind(handleFailure(cause));
      throw cause;
    } finally {
      if (requestToken.current === token) setLoading(false);
    }
  }, [handleFailure]);

  useEffect(() => {
    load().catch((cause) => {
      if (cause instanceof Superseded) return;
    });
  }, [load]);

  const refresh = useCallback(async (): Promise<void> => {
    await load();
  }, [load]);

  return { ...data, available, loading, errorKind, refresh };
}
