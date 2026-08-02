// P2C-MUTATION-FULL-UI-C3C (SPEC R19, WO C3C-BUILD-REREREV-F1): one-in-
// flight-submit-per-control hook against a real Promise<void> refresh that
// REJECTS if the underlying read was superseded/cancelled before it
// committed (see useOperationsData.ts) - this hook never treats such a
// rejection as proof of a fresh read. Success awaits refresh before
// resolving; if that refresh is itself superseded (e.g. the operator
// switched shifts mid-flight), the state becomes locked 'stale', not a false
// 'success' or a misleading generic 'server error'. The mutation itself did
// succeed, but another submit is unsafe until a manual fresh read succeeds.
// Conflict automatically runs exactly one refresh: only a refresh that
// genuinely committed unlocks the control (kept as 'conflict_resolved');
// failure/supersession leaves it locked with an explicit manual retry
// action. outcome_unknown NEVER auto-refreshes or auto-retries - only an
// explicit operator-triggered refresh that itself genuinely commits can
// unlock it; a superseded manual refresh leaves it locked too.
import { useCallback, useId, useRef, useState } from 'react';
import { ApiError, type ApiErrorKind } from '../../services/api';
import { OfflineQueuedError } from '../../offline/queue';

export type MutationControlState =
  | { status: 'idle' }
  | { status: 'submitting' }
  | { status: 'success' }
  | { status: 'queued'; clientOperationId: string }
  | { status: 'stale'; locked: true }
  | { status: 'conflict'; locked: true }
  | { status: 'conflict_resolved'; locked: false }
  | { status: 'error'; kind: ApiErrorKind; locked: false }
  | { status: 'locked_out'; locked: true };

export function useMutationControl<TArgs extends unknown[]>(
  fn: (...args: TArgs) => Promise<void>,
  refresh: () => Promise<void>
) {
  const [state, setState] = useState<MutationControlState>({ status: 'idle' });
  const inFlight = useRef(false);
  const refreshInFlight = useRef(false);
  const feedbackId = useId();

  const submit = useCallback(
    async (...args: TArgs) => {
      if (inFlight.current) return;
      inFlight.current = true;
      setState({ status: 'submitting' });
      try {
        await fn(...args);
        try {
          await refresh();
        } catch {
          // The mutation itself succeeded; only this control's own
          // confirming read was superseded/cancelled - never claim
          // 'success' (unverified) nor a false generic 'server' error. Keep
          // repeat mutation disabled until an explicit fresh read succeeds.
          inFlight.current = false;
          setState({ status: 'stale', locked: true });
          return;
        }
        inFlight.current = false;
        setState({ status: 'success' });
      } catch (cause) {
        inFlight.current = false;
        if (cause instanceof OfflineQueuedError) {
          setState({ status: 'queued', clientOperationId: cause.clientOperationId });
        } else if (cause instanceof ApiError) {
          if (cause.kind === 'outcome_unknown') {
            // Never auto-refresh here: an ambiguous transport outcome must
            // wait for an explicit operator-triggered refresh, never a
            // hook-initiated one, or a real duplicate-effect mutation could
            // be masked as safe before the operator ever sees it.
            setState({ status: 'locked_out', locked: true });
          } else if (cause.kind === 'conflict') {
            setState({ status: 'conflict', locked: true });
            void refresh().then(
              // Successful auto-refresh unlocks for retry but keeps the
              // conflict visible - the operator must see fresh
              // versions/status before choosing to resubmit, never a silent
              // reset back to idle. A superseded/cancelled/failed refresh
              // leaves the control locked (bare rejection, no branch here).
              () => setState((prev) => (prev.status === 'conflict' ? { status: 'conflict_resolved', locked: false } : prev)),
              () => {} // failed or superseded auto-refresh: remain locked, offer manual retry
            );
          } else {
            setState({ status: 'error', kind: cause.kind, locked: false });
          }
        } else {
          setState({ status: 'error', kind: 'server', locked: false });
        }
      }
    },
    [fn, refresh]
  );

  const reset = useCallback(() => {
    if (!inFlight.current && !isLocked(state)) setState({ status: 'idle' });
  }, [state]);

  const manualRefreshAndUnlock = useCallback(async (): Promise<void> => {
    if (refreshInFlight.current) return;
    refreshInFlight.current = true;
    try {
      await refresh();
      setState({ status: 'idle' });
    } catch {
      // A failed or superseded refresh MUST leave the control locked - only
      // a refresh that genuinely committed a current read may unlock it.
    } finally { refreshInFlight.current = false; }
  }, [refresh]);

  const isSubmitting = state.status === 'submitting';
  const isLockedOut = isLocked(state);

  return { state, submit, reset, refreshAndUnlock: manualRefreshAndUnlock, isSubmitting, isLockedOut, feedbackId };
}

function isLocked(state: MutationControlState): boolean {
  return state.status === 'locked_out' || state.status === 'conflict' || state.status === 'stale';
}
