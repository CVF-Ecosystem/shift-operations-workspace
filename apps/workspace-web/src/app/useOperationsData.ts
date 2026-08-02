// P2C-MUTATION-FULL-UI-C3C (SPEC R18/R19/WO C3C-BUILD-REREREV-F1): dedicated
// read coordinator hook. `refresh()` is a real Promise<void> that resolves
// ONLY when this specific invocation's reads actually committed into state
// for the current selected shift. If a newer load/refresh/shift-change
// supersedes this invocation before it commits, or the shift is cleared out
// from under it, `refresh()` REJECTS - it never reports false success. The
// shift-change useEffect uses the same `load()` but silently ignores a
// superseded/cancelled outcome, since a newer effect run already owns the
// canonical state. Stale-response suppression via requestToken and
// AbortSignal cancellation on shift change are preserved.
//
// P2C-MUTATION-FULL-UI-C3D (SPEC R3): `events` now retains the COMPLETE
// selected-shift event collection (including unconfirmed) so supervisor
// confirm/correction target selection can see every event and its current
// stored version. Only the derived `confirmedEvents` projection stays
// timeline-visible; existing C3c timeline behavior does not regress.
import { useCallback, useEffect, useRef, useState } from 'react';
import { api, ApiError, type ApiErrorKind } from '../services/api';
import { operatorApi, type ReportEntry } from '../services/operatorApi';
import type { CustomerRequest, Handover, Incident, OpenWorkResponse, OperationalEvent, Task } from '../types/operations';
import type { Message } from '../types/backendContracts';

export interface OperationsDataState {
  events: OperationalEvent[];
  confirmedEvents: OperationalEvent[];
  openWork: OpenWorkResponse | null;
  incidents: Incident[];
  handovers: Handover[];
  messages: Message[];
  tasks: Task[];
  customerRequests: CustomerRequest[];
  capabilities: string[];
  reports: ReportEntry[];
  loading: boolean;
  errorKind: ApiErrorKind | null;
  refresh: () => Promise<void>;
}

const EMPTY_DATA = {
  events: [] as OperationalEvent[],
  confirmedEvents: [] as OperationalEvent[],
  openWork: null as OpenWorkResponse | null,
  incidents: [] as Incident[],
  handovers: [] as Handover[],
  messages: [] as Message[],
  tasks: [] as Task[],
  customerRequests: [] as CustomerRequest[],
  capabilities: [] as string[],
  reports: [] as ReportEntry[]
};

class Superseded extends Error {}

export function useOperationsData(
  selectedShiftId: string | null,
  handleFailure: (cause: unknown) => ApiErrorKind
): OperationsDataState {
  const [data, setData] = useState(EMPTY_DATA);
  const [loading, setLoading] = useState(false);
  const [errorKind, setErrorKind] = useState<ApiErrorKind | null>(null);
  const requestToken = useRef(0);

  // Returns true only if THIS invocation's reads committed into state.
  // Throws Superseded if a newer load/refresh/shift-change won the race
  // before this one could commit - callers that need to know whether their
  // own refresh actually landed a fresh read must not treat return-without-
  // throwing as ambiguous; every non-committing path throws.
  const load = useCallback(
    async (shiftId: string, signal: AbortSignal): Promise<void> => {
      const token = ++requestToken.current;
      setLoading(true);
      setErrorKind(null);

      let results: Awaited<ReturnType<typeof loadAll>>;
      try {
        results = await loadAll(shiftId, signal);
      } catch (cause) {
        if (requestToken.current !== token) throw new Superseded('refresh superseded before failure was observed');
        if (cause instanceof ApiError && cause.kind === 'cancelled') throw new Superseded('refresh cancelled by a newer request');
        setErrorKind(handleFailure(cause));
        throw cause;
      } finally {
        if (requestToken.current === token) setLoading(false);
      }

      if (requestToken.current !== token) throw new Superseded('refresh superseded before it could commit');
      const [events, openWork, incidents, handovers, messages, tasks, customerRequests, capRes, reports] = results;
      setData({
        // C3D SPEC R3: retain the complete collection for supervisor target
        // selection; the timeline stays confirmed-only via the derived
        // projection below (unchanged C3c behavior).
        events,
        confirmedEvents: events.filter((e) => e.state === 'CONFIRMED'),
        openWork,
        incidents,
        handovers,
        messages,
        tasks,
        customerRequests,
        capabilities: capRes.actions,
        reports
      });
    },
    [handleFailure]
  );

  useEffect(() => {
    if (!selectedShiftId) {
      requestToken.current += 1;
      setData(EMPTY_DATA);
      setErrorKind(null);
      setLoading(false);
      return;
    }
    const controller = new AbortController();
    // The effect owns background-load semantics: a superseded/cancelled
    // outcome here means a newer effect run (or refresh()) already owns
    // committing state, so it is correctly ignored, not surfaced as an error.
    load(selectedShiftId, controller.signal).catch((cause) => {
      if (cause instanceof Superseded) return;
    });
    return () => controller.abort();
  }, [selectedShiftId, load]);

  const refresh = useCallback(async (): Promise<void> => {
    if (!selectedShiftId) throw new Superseded('no shift selected');
    const controller = new AbortController();
    // Unlike the effect, a mutation-owned refresh() call must never resolve
    // successfully unless THIS invocation's own reads committed - callers
    // (useMutationControl) rely on that to prove a genuine fresh read landed
    // before unlocking. Superseded propagates as a real rejection.
    await load(selectedShiftId, controller.signal);
  }, [selectedShiftId, load]);

  return { ...data, loading, errorKind, refresh };
}

function loadAll(shiftId: string, signal: AbortSignal) {
  return Promise.all([
    api.listEvents(shiftId, signal),
    api.getOpenWork(shiftId, signal),
    api.listIncidents(shiftId, signal),
    api.listHandovers(shiftId, signal),
    api.listMessages(shiftId, signal),
    api.listTasks(shiftId, signal),
    api.listCustomerRequests(shiftId, signal),
    operatorApi.getCapabilities(shiftId, signal),
    operatorApi.listReports(shiftId, signal)
  ]);
}
