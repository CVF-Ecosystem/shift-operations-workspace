// P2C-MUTATION-FULL-UI-C3C (SPEC R20, WO C3C-BUILD-REV-F3): sanitized
// mutation feedback. Renders only fixed messages keyed by ApiErrorKind -
// never raw transport/backend detail text. Moves focus to itself on failure
// so keyboard/screen-reader users land on the bounded explanation.
import { useEffect, useRef } from 'react';
import type { ApiErrorKind } from '../../services/api';
import type { MutationControlState } from './useMutationControl';

const ERROR_MESSAGES: Record<ApiErrorKind, string> = {
  network: 'Cannot reach the server. Check your connection and try again.',
  unauthorized: 'Your session has expired. Please sign in again.',
  forbidden: 'Action not permitted. Check your role or approval prerequisites.',
  not_found: 'The requested record was not found.',
  invalid: 'The request could not be processed. Check the entered values.',
  server: 'Something went wrong on the server. Try again shortly.',
  cancelled: 'Request was cancelled.',
  conflict: 'This record changed elsewhere.',
  outcome_unknown: 'The outcome of this request could not be confirmed. Refresh before trying again.'
};

interface MutationFeedbackProps {
  id?: string;
  state: MutationControlState;
  onRefreshAndUnlock?: () => void;
}

export function MutationFeedback({ id, state, onRefreshAndUnlock }: MutationFeedbackProps) {
  const ref = useRef<HTMLParagraphElement>(null);
  const isFailure =
    state.status === 'locked_out' || state.status === 'conflict' ||
    state.status === 'conflict_resolved' || state.status === 'error' || state.status === 'stale';

  useEffect(() => {
    if (isFailure) ref.current?.focus();
  }, [isFailure, state.status]);

  if (state.status === 'idle' || state.status === 'submitting' || state.status === 'success') {
    return null;
  }

  if (state.status === 'queued') {
    return <p id={id} role="status" aria-live="polite" className="mutation-feedback mutation-feedback--queued">Queued on this device. It will be checked against your identity, permission and recorded version after reconnect.</p>;
  }

  if (state.status === 'stale') {
    return (
      <p id={id} ref={ref} role="status" tabIndex={-1} aria-live="polite" className="mutation-feedback mutation-feedback--stale">
        Saved. The view could not be confirmed as current. Refresh before another action.{' '}
        {onRefreshAndUnlock && (
          <button type="button" onClick={onRefreshAndUnlock} className="mutation-feedback__refresh-btn">
            Refresh
          </button>
        )}
      </p>
    );
  }

  if (state.status === 'locked_out') {
    return (
      <p id={id} ref={ref} role="alert" tabIndex={-1} className="mutation-feedback mutation-feedback--locked">
        {ERROR_MESSAGES.outcome_unknown}{' '}
        {onRefreshAndUnlock && (
          <button type="button" onClick={onRefreshAndUnlock} className="mutation-feedback__refresh-btn">
            Refresh
          </button>
        )}
      </p>
    );
  }

  if (state.status === 'conflict') {
    return (
      <p id={id} ref={ref} role="alert" tabIndex={-1} className="mutation-feedback mutation-feedback--conflict">
        {ERROR_MESSAGES.conflict}{' '}
        {onRefreshAndUnlock && (
          <button type="button" onClick={onRefreshAndUnlock} className="mutation-feedback__refresh-btn">
            Refresh and try again
          </button>
        )}
      </p>
    );
  }

  if (state.status === 'conflict_resolved') {
    return (
      <p id={id} ref={ref} role="alert" tabIndex={-1} className="mutation-feedback mutation-feedback--conflict">
        {ERROR_MESSAGES.conflict} Refreshed with the latest values - review before trying again.
      </p>
    );
  }

  return (
    <p id={id} ref={ref} role="alert" tabIndex={-1} className="mutation-feedback mutation-feedback--error">
      {ERROR_MESSAGES[state.kind]}
    </p>
  );
}
