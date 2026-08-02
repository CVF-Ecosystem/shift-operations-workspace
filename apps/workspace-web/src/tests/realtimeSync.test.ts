import { afterEach, describe, expect, it, vi } from 'vitest';
import { pollingIntervalSeconds, startPolling } from '../offline/realtime';
import { resetRefreshCoordinatorForTests, serializeRefresh } from '../offline/refreshCoordinator';

describe('foreground polling contract', () => {
  afterEach(() => { vi.useRealTimers(); resetRefreshCoordinatorForTests(); });

  it('validates the interval boundary', () => {
    expect(pollingIntervalSeconds('5')).toBe(5);
    expect(pollingIntervalSeconds('60')).toBe(60);
    expect(pollingIntervalSeconds('4')).toBe(15);
    expect(pollingIntervalSeconds('x')).toBe(15);
  });

  it('never overlaps and immediately refreshes on online recovery', async () => {
    vi.useFakeTimers();
    Object.defineProperty(document, 'visibilityState', { configurable: true, value: 'visible' });
    vi.spyOn(window.navigator, 'onLine', 'get').mockReturnValue(true);
    let resolve!: () => void;
    const refresh = vi.fn(() => new Promise<void>((done) => { resolve = done; }));
    const stop = startPolling({ refresh, onSyncing: vi.fn(), onSuccess: vi.fn(), onError: vi.fn() });
    window.dispatchEvent(new Event('online'));
    window.dispatchEvent(new Event('online'));
    expect(refresh).toHaveBeenCalledTimes(1);
    resolve(); await Promise.resolve();
    stop();
  });

  it('serializes staffing, polling, mutation and queue owners FIFO without overlap', async () => {
    const order: string[] = [];
    let release!: () => void;
    const held = new Promise<void>((resolve) => { release = resolve; });
    const staffing = serializeRefresh(async () => { order.push('staffing:start'); await held; order.push('staffing:end'); });
    const polling = serializeRefresh(async () => { order.push('polling'); });
    const mutation = serializeRefresh(async () => { order.push('mutation'); });
    const queue = serializeRefresh(async () => { order.push('queue'); });
    await vi.waitFor(() => expect(order).toEqual(['staffing:start']));
    release();
    await Promise.all([staffing, polling, mutation, queue]);
    expect(order).toEqual(['staffing:start', 'staffing:end', 'polling', 'mutation', 'queue']);
  });

  it('returns the real shared settlement and does not swallow owner rejection', async () => {
    const failure = new Error('staffing refresh failed');
    const rejected = serializeRefresh(() => Promise.reject(failure));
    const following = serializeRefresh(() => Promise.resolve());
    await expect(rejected).rejects.toBe(failure);
    await expect(following).resolves.toBeUndefined();
  });
});
