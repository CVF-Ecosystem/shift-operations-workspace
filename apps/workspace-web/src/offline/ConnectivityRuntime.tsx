import { useEffect, useState, type ReactNode } from 'react';
import { api, ApiError } from '../services/api';
import { clearSession, getPrincipalUserId, setPrincipalUserId, subscribeSessionTermination } from '../features/authentication/session';
import { ConnectionStatus, type SyncState } from '../features/connection-health/ConnectionStatus';
import { OfflineQueuePanel } from './OfflineQueuePanel';
import { queueItems, subscribeQueue } from './queue';
import { refreshCurrentConsole } from './refreshBridge';
import { serializeRefresh } from './refreshCoordinator';
import { startPolling } from './realtime';
import { recoverAndReplay } from './sync';

interface ConnectivityRuntimeProps { children: ReactNode; onSignedOut: () => void }

export function ConnectivityRuntime({ children, onSignedOut }: ConnectivityRuntimeProps) {
  const [ready, setReady] = useState(false);
  const [syncState, setSyncState] = useState<SyncState>('connecting');
  const [lastSuccess, setLastSuccess] = useState<Date | null>(null);
  const [, redraw] = useState(0);
  useEffect(() => subscribeQueue(() => redraw((value) => value + 1)), []);
  useEffect(() => subscribeSessionTermination(() => {
    setReady(false);
    setSyncState('stale');
    onSignedOut();
  }), [onSignedOut]);

  useEffect(() => {
    const controller = new AbortController();
    api.me(controller.signal).then((principal) => {
      setPrincipalUserId(principal.user_id);
      setReady(true);
      setSyncState(navigator.onLine ? 'connected' : 'offline');
    }).catch((cause) => {
      if (cause instanceof ApiError && cause.kind === 'cancelled') return;
      if (cause instanceof ApiError && cause.kind === 'unauthorized') {
        clearSession(); return;
      }
      setSyncState('stale');
    });
    return () => controller.abort();
  }, [onSignedOut]);

  useEffect(() => {
    if (!ready) return;
    const stop = startPolling({
      refresh: async () => {
        if (!(await recoverAndReplay()) || !getPrincipalUserId()) throw new Error('sync session terminated');
        await serializeRefresh(refreshCurrentConsole, true);
      },
      onSyncing: () => setSyncState('syncing'),
      onSuccess: (at) => { setLastSuccess(at); setSyncState('connected'); },
      onError: () => setSyncState(navigator.onLine ? 'stale' : 'offline')
    });
    const offline = () => setSyncState('offline');
    window.addEventListener('offline', offline);
    return () => { stop(); window.removeEventListener('offline', offline); };
  }, [ready]);

  const counts = queueItems().reduce((acc, item) => {
    if (item.state === 'pending' || item.state === 'replaying') acc.pending += 1;
    if (item.state === 'blocked') acc.blocked += 1;
    if (item.state === 'outcome_unknown') acc.ambiguous += 1;
    if (item.state === 'applied_stale') acc.appliedStale += 1;
    return acc;
  }, { pending: 0, blocked: 0, ambiguous: 0, appliedStale: 0 });

  return <><ConnectionStatus state={syncState} lastSuccess={lastSuccess} {...counts} />{ready && <OfflineQueuePanel />}{children}</>;
}
