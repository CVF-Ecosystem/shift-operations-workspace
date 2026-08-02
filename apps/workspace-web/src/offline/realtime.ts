export interface PollingCallbacks {
  refresh: () => Promise<void>;
  onSyncing: () => void;
  onSuccess: (at: Date) => void;
  onError: () => void;
}

export function pollingIntervalSeconds(raw = import.meta.env.VITE_POLL_INTERVAL_SECONDS): number {
  const value = Number(raw ?? 15);
  return Number.isInteger(value) && value >= 5 && value <= 60 ? value : 15;
}

export function startPolling(callbacks: PollingCallbacks): () => void {
  const interval = pollingIntervalSeconds() * 1000;
  let timer: number | null = null;
  let stopped = false;
  let inFlight = false;
  let failures = 0;

  const schedule = () => {
    if (stopped || timer !== null) return;
    const delay = Math.min(interval * 2 ** failures, interval * 4);
    timer = window.setTimeout(() => { timer = null; void run(); }, delay);
  };

  const eligible = () => navigator.onLine && document.visibilityState === 'visible';
  const run = async () => {
    if (stopped || inFlight || !eligible()) return;
    inFlight = true;
    callbacks.onSyncing();
    try {
      await callbacks.refresh();
      failures = 0;
      callbacks.onSuccess(new Date());
    } catch {
      failures += 1;
      callbacks.onError();
    } finally {
      inFlight = false;
      schedule();
    }
  };

  const recover = () => {
    if (!eligible()) return;
    if (timer !== null) { clearTimeout(timer); timer = null; }
    void run();
  };
  const visibility = () => { if (document.visibilityState === 'visible') recover(); };
  window.addEventListener('online', recover);
  document.addEventListener('visibilitychange', visibility);
  schedule();
  return () => {
    stopped = true;
    if (timer !== null) clearTimeout(timer);
    window.removeEventListener('online', recover);
    document.removeEventListener('visibilitychange', visibility);
  };
}
