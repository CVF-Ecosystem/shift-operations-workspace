export type SyncState = 'connecting' | 'offline' | 'syncing' | 'connected' | 'stale';

interface ConnectionStatusProps {
  state: SyncState;
  lastSuccess: Date | null;
  pending: number;
  blocked: number;
  ambiguous: number;
  appliedStale: number;
}

export function ConnectionStatus(props: ConnectionStatusProps) {
  const summary = [
    `Polling sync: ${label(props.state)}`,
    props.lastSuccess ? `last success ${props.lastSuccess.toLocaleTimeString()}` : 'no successful refresh yet',
    props.pending ? `${props.pending} pending` : null,
    props.blocked ? `${props.blocked} blocked` : null,
    props.ambiguous ? `${props.ambiguous} outcome unknown` : null,
    props.appliedStale ? `${props.appliedStale} known applied, view stale` : null
  ].filter(Boolean).join(' · ');
  return <div role="status" aria-live="polite" className={`connection-status connection-status--${props.state}`}>{summary}</div>;
}

function label(state: SyncState): string {
  if (state === 'offline') return 'offline';
  if (state === 'syncing') return 'syncing';
  if (state === 'stale') return 'stale or refresh failed';
  if (state === 'connected') return 'connected';
  return 'connecting';
}
