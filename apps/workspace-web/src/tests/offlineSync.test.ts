import { beforeEach, describe, expect, it, vi } from 'vitest';
import { enqueueTransition, queueItems, resetQueueForTests, updateItem } from '../offline/queue';
import { storageKey } from '../offline/storage';
import { registerRefreshOwner } from '../offline/refreshBridge';
import { resetRefreshCoordinatorForTests } from '../offline/refreshCoordinator';
import { recoverAndReplay, resetReplayForTests } from '../offline/sync';
import { getPrincipalUserId, hasSession, setPrincipalUserId, setToken, subscribeSessionTermination } from '../features/authentication/session';

const ID = '123e4567-e89b-42d3-a456-426614174000';

describe('offline replay fail-stop', () => {
  beforeEach(() => {
    localStorage.clear(); sessionStorage.clear(); resetQueueForTests(); setPrincipalUserId('actor'); resetReplayForTests(); resetRefreshCoordinatorForTests();
    vi.spyOn(window.navigator, 'onLine', 'get').mockReturnValue(false);
    Object.defineProperty(document, 'visibilityState', { configurable: true, value: 'visible' });
  });

  it('recovers crash-left replaying as outcome_unknown without dispatch', async () => {
    expect(() => enqueueTransition('task.transition', ID, 'IN_PROGRESS', 1)).toThrow();
    const id = queueItems()[0].clientOperationId;
    updateItem(id, (item) => ({ ...item, state: 'replaying', lastErrorKind: null }));
    vi.spyOn(window.navigator, 'onLine', 'get').mockReturnValue(true);
    const fetchMock = vi.fn(); vi.stubGlobal('fetch', fetchMock);
    await recoverAndReplay();
    expect(queueItems()[0]).toMatchObject({ state: 'outcome_unknown', lastErrorKind: 'outcome_unknown' });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('marks known HTTP success applied_stale until a genuine refresh commits', async () => {
    expect(() => enqueueTransition('task.transition', ID, 'IN_PROGRESS', 1)).toThrow();
    vi.spyOn(window.navigator, 'onLine', 'get').mockReturnValue(true);
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('{}', { status: 200 })));
    const unregister = registerRefreshOwner(() => Promise.reject(new Error('refresh failed')));
    await recoverAndReplay();
    expect(queueItems()[0]).toMatchObject({ state: 'applied_stale', lastErrorKind: 'refresh_failed' });
    unregister();
  });

  it('halts at a quarantined head without dispatching a later valid command', async () => {
    expect(() => enqueueTransition('task.transition', ID, 'IN_PROGRESS', 1)).toThrow();
    const valid = JSON.parse(localStorage.getItem(storageKey('actor')) ?? '[]')[0];
    localStorage.setItem(storageKey('actor'), JSON.stringify([{ malformed: true }, valid]));
    vi.spyOn(window.navigator, 'onLine', 'get').mockReturnValue(true);
    const fetchMock = vi.fn(); vi.stubGlobal('fetch', fetchMock);
    await recoverAndReplay();
    expect(fetchMock).not.toHaveBeenCalled();
    expect(queueItems()).toHaveLength(2);
  });

  it('retains blocked unauthorized under the captured actor and terminates sync session', async () => {
    setToken('test-token');
    expect(() => enqueueTransition('task.transition', ID, 'IN_PROGRESS', 1)).toThrow();
    const terminated = vi.fn();
    const unsubscribe = subscribeSessionTermination(terminated);
    vi.spyOn(window.navigator, 'onLine', 'get').mockReturnValue(true);
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('{"detail":"expired"}', { status: 401, headers: { 'Content-Type': 'application/json' } })));
    expect(await recoverAndReplay()).toBe(false);
    expect(hasSession()).toBe(false);
    expect(getPrincipalUserId()).toBeNull();
    expect(terminated).toHaveBeenCalledTimes(1);
    setPrincipalUserId('actor');
    expect(queueItems()[0]).toMatchObject({ state: 'blocked', lastErrorKind: 'unauthorized' });
    unsubscribe();
  });

  it('keeps known success non-replayable across reload when applied write and raw cleanup both fail', async () => {
    expect(() => enqueueTransition('task.transition', ID, 'IN_PROGRESS', 1)).toThrow();
    vi.spyOn(window.navigator, 'onLine', 'get').mockReturnValue(true);
    const fetchMock = vi.fn().mockResolvedValue(new Response('{}', { status: 200 }));
    vi.stubGlobal('fetch', fetchMock);
    const original = localStorage.setItem.bind(localStorage);
    vi.spyOn(localStorage, 'setItem').mockImplementation((key, value) => {
      if (value.includes('applied_stale') || value === '[]') throw new DOMException('quota', 'QuotaExceededError');
      return original(key, value);
    });
    const unregister = registerRefreshOwner(() => Promise.reject(new Error('refresh failed')));
    await recoverAndReplay();
    expect(queueItems()[0]).toMatchObject({ state: 'applied_stale', lastErrorKind: 'refresh_failed' });
    resetQueueForTests(); // module-memory reset; session tombstone must survive like a reload
    expect(queueItems()[0]).toMatchObject({ state: 'applied_stale', lastErrorKind: 'refresh_failed' });
    await recoverAndReplay();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    unregister();
  });

  it.each([
    [403, 'forbidden'], [404, 'not_found'], [409, 'conflict'], [422, 'invalid'], [500, 'server']
  ])('halts the complete HTTP fail-stop matrix for %s as %s', async (status, kind) => {
    expect(() => enqueueTransition('task.transition', ID, 'IN_PROGRESS', 3)).toThrow();
    expect(() => enqueueTransition('task.transition', ID, 'IN_PROGRESS', 4)).toThrow();
    vi.spyOn(window.navigator, 'onLine', 'get').mockReturnValue(true);
    const fetchMock = vi.fn().mockResolvedValue(new Response('{"detail":"bounded"}', {
      status, headers: { 'Content-Type': 'application/json' }
    }));
    vi.stubGlobal('fetch', fetchMock);
    await recoverAndReplay();
    expect(queueItems().map((item) => ({ state: item.state, error: item.lastErrorKind }))).toEqual([
      { state: 'blocked', error: kind }, { state: 'pending', error: null }
    ]);
    expect((queueItems()[0] as { expectedVersion: number }).expectedVersion).toBe(3);
    await recoverAndReplay();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('halts transport-ambiguous replay without retrying or bypassing the later CAS', async () => {
    expect(() => enqueueTransition('task.transition', ID, 'IN_PROGRESS', 5)).toThrow();
    expect(() => enqueueTransition('task.transition', ID, 'IN_PROGRESS', 6)).toThrow();
    vi.spyOn(window.navigator, 'onLine', 'get').mockReturnValue(true);
    const fetchMock = vi.fn().mockRejectedValue(new TypeError('connection reset'));
    vi.stubGlobal('fetch', fetchMock);
    await recoverAndReplay();
    expect(queueItems().map((item) => ({ state: item.state, error: item.lastErrorKind }))).toEqual([
      { state: 'outcome_unknown', error: 'outcome_unknown' }, { state: 'pending', error: null }
    ]);
    expect((queueItems()[0] as { expectedVersion: number }).expectedVersion).toBe(5);
    await recoverAndReplay();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
