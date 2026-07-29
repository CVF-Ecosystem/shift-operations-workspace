import type { ReactNode } from 'react';
import type { ApiErrorKind } from '../services/api';

const MESSAGES: Record<ApiErrorKind, string> = {
  network: 'Cannot reach the server. Check your connection and try again.',
  unauthorized: 'Your session has expired. Please sign in again.',
  forbidden: 'You do not have permission to view this.',
  not_found: 'The requested record was not found.',
  conflict: 'This record changed elsewhere. Reload and try again.',
  invalid: 'The request could not be processed.',
  server: 'Something went wrong on the server. Try again shortly.',
  cancelled: 'Request was cancelled.'
};

export interface AsyncStateProps {
  loading: boolean;
  errorKind: ApiErrorKind | null;
  isEmpty: boolean;
  emptyLabel?: string;
  children: ReactNode;
}

export function AsyncState({ loading, errorKind, isEmpty, emptyLabel, children }: AsyncStateProps) {
  if (loading) {
    return (
      <p role="status" aria-live="polite" className="async-state async-state--loading">
        Loading…
      </p>
    );
  }

  if (errorKind) {
    return (
      <p role="alert" className="async-state async-state--error">
        {MESSAGES[errorKind]}
      </p>
    );
  }

  if (isEmpty) {
    return (
      <p role="status" className="async-state async-state--empty">
        {emptyLabel ?? 'Nothing to show.'}
      </p>
    );
  }

  return <>{children}</>;
}
