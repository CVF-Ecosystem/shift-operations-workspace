import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { readProactiveSource } from '../services/proactiveSourceApi';
import { clearSession, getToken, setPrincipalUserId, setToken,
  subscribeSessionChange, subscribeSessionTermination } from '../features/authentication/session';
import { ACTOR, jsonResponse, positives } from './proactiveSourceTestData';

describe('source-only transport and session changes', () => {
  beforeEach(() => { sessionStorage.clear(); setToken('old-token'); setPrincipalUserId(ACTOR); });
  afterEach(() => vi.unstubAllGlobals());

  it('uses exact GET UTC query, bearer identity, no-store, no request body', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, positives[0].receipt));
    vi.stubGlobal('fetch', fetchMock);
    await readProactiveSource(positives[0].window, 'old-token', ACTOR, new AbortController().signal);
    const [url, init] = fetchMock.mock.calls[0];
    expect(new URL(url).pathname).toBe('/proactive/source');
    expect(Object.fromEntries(new URL(url).searchParams)).toEqual(positives[0].window);
    expect(init).toMatchObject({ method: 'GET', cache: 'no-store', headers: { Authorization: 'Bearer old-token' } });
    expect(init.body).toBeUndefined();
  });

  it('never lets an old 401 clear a replacement token or principal', async () => {
    let finish!: (response: Response) => void;
    vi.stubGlobal('fetch', vi.fn(() => new Promise<Response>((resolve) => { finish = resolve; })));
    const pending = readProactiveSource(positives[0].window, 'old-token', ACTOR, new AbortController().signal);
    setToken('new-token'); setPrincipalUserId('new-user');
    finish(jsonResponse(401, { detail: 'PRIVATE_SERVER_DETAIL' }));
    await expect(pending).rejects.toMatchObject({ kind: 'cancelled' });
    expect(getToken()).toBe('new-token');
  });

  it('clears a current 401, and ignores arbitrary server detail on 403/500', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(jsonResponse(403, { detail: 'PRIVATE_SERVER_DETAIL' }))
      .mockResolvedValueOnce(jsonResponse(500, { detail: 'PRIVATE_SERVER_DETAIL' }))
      .mockResolvedValueOnce(jsonResponse(401, { detail: 'PRIVATE_SERVER_DETAIL' }));
    vi.stubGlobal('fetch', fetchMock);
    for (const kind of ['forbidden', 'server', 'unauthorized']) {
      await expect(readProactiveSource(positives[0].window, 'old-token', ACTOR, new AbortController().signal))
        .rejects.toMatchObject({ kind });
    }
    expect(getToken()).toBeNull();
  });

  it('notifies only changed setters and every clear, preserves termination behavior and unsubscribe', () => {
    const changed = vi.fn(); const terminated = vi.fn();
    const off = subscribeSessionChange(changed);
    const offTermination = subscribeSessionTermination(terminated);
    setToken('old-token'); setPrincipalUserId(ACTOR);
    expect(changed).not.toHaveBeenCalled();
    setToken('replacement'); setPrincipalUserId('new-user');
    expect(changed).toHaveBeenCalledTimes(2);
    clearSession(false);
    expect(changed).toHaveBeenCalledTimes(3);
    expect(terminated).not.toHaveBeenCalled();
    setToken('again'); clearSession();
    expect(terminated).toHaveBeenCalledTimes(1);
    off(); offTermination(); clearSession();
    expect(changed).toHaveBeenCalledTimes(5);
  });
});
