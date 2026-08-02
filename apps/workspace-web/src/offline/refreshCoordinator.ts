let tail: Promise<void> = Promise.resolve();
let pending: Promise<void> | null = null;

export function serializeRefresh(refresh: () => Promise<void>, coalesce = false): Promise<void> {
  if (coalesce && pending) return pending;
  const run = tail.catch(() => undefined).then(refresh);
  tail = run.catch(() => undefined);
  if (coalesce) {
    pending = run;
    void run.finally(() => { if (pending === run) pending = null; });
  }
  return run;
}

export function resetRefreshCoordinatorForTests(): void {
  tail = Promise.resolve();
  pending = null;
}
