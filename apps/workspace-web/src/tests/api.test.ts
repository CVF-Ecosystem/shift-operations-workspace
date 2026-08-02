import { createElement } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { api, ApiError, login } from '../services/api';
import { getToken, setToken } from '../features/authentication/session';
import { AsyncState } from '../components/AsyncState';

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

describe('api client', () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('injects a bearer header only when a token exists', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    fetchMock.mockResolvedValueOnce(jsonResponse(200, []));
    await api.listShifts();
    expect(fetchMock.mock.calls[0][1]?.headers).toStrictEqual({});

    setToken('secret-token-value');
    fetchMock.mockResolvedValueOnce(jsonResponse(200, []));
    await api.listShifts();
    const headers = fetchMock.mock.calls[1][1]?.headers as Record<string, string>;
    expect(headers.Authorization).toBe('Bearer secret-token-value');
  });

  it('maps HTTP 401 to an unauthorized ApiError', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    fetchMock.mockResolvedValueOnce(jsonResponse(401, { detail: 'Invalid username or password' }));
    await expect(api.listShifts()).rejects.toMatchObject({ kind: 'unauthorized' } satisfies Partial<ApiError>);
  });

  it('maps HTTP 403, 404, 409, 422 and 5xx to distinct controlled kinds', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    const cases: Array<[number, string]> = [
      [403, 'forbidden'],
      [404, 'not_found'],
      [409, 'conflict'],
      [422, 'invalid'],
      [500, 'server']
    ];
    for (const [status, kind] of cases) {
      fetchMock.mockResolvedValueOnce(jsonResponse(status, { detail: 'x' }));
      await expect(api.listShifts()).rejects.toMatchObject({ kind });
    }
  });

  it('maps an ambiguous transport failure to outcome_unknown without leaking the raw cause', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    fetchMock.mockRejectedValueOnce(new TypeError('Failed to fetch'));
    const failure = await api.listShifts().catch((cause: unknown) => cause);
    expect(failure).toBeInstanceOf(ApiError);
    expect((failure as ApiError).kind).toBe('outcome_unknown');
    expect((failure as ApiError).message).not.toContain('TypeError');
  });

  it('never renders a raw transport object as the error message', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    const rawTransportError = { stack: 'Error: boom\n at internal', code: 'ECONNRESET' };
    fetchMock.mockRejectedValueOnce(rawTransportError);
    const failure = await api.listShifts().catch((cause: unknown) => cause);
    expect(failure).toBeInstanceOf(ApiError);
    expect((failure as ApiError).kind).toBe('outcome_unknown');
    expect((failure as ApiError).message).toBe('Unable to confirm the request outcome; refresh before retrying');
  });

  it('clears the tab-scoped session on HTTP 401', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    setToken('secret-token-value');
    fetchMock.mockResolvedValueOnce(jsonResponse(401, { detail: 'token expired' }));
    await expect(api.listShifts()).rejects.toMatchObject({ kind: 'unauthorized' });
    expect(getToken()).toBeNull();
  });

  it('surfaces the sanitized detail field from a 4xx body, not the whole response', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    fetchMock.mockResolvedValueOnce(jsonResponse(422, { detail: 'password must not exceed 72 UTF-8 bytes' }));
    const failure = await api.listShifts().catch((cause: unknown) => cause);
    expect((failure as ApiError).message).toBe('password must not exceed 72 UTF-8 bytes');
  });

  it('maps a server-side domain-lock rejection of an out-of-scope event_type to the controlled invalid kind with its detail intact (WO C3C-BUILD-REV-F2)', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    fetchMock.mockResolvedValueOnce(
      jsonResponse(422, { detail: "event_type 'not_a_real_type' is outside the permitted domain-lock scope" })
    );
    const failure = await api.listShifts().catch((cause: unknown) => cause);
    expect(failure).toBeInstanceOf(ApiError);
    expect((failure as ApiError).kind).toBe('invalid');
    expect((failure as ApiError).message).toBe("event_type 'not_a_real_type' is outside the permitted domain-lock scope");
  });

  it('login stores no token on failure and returns a token response on success', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    fetchMock.mockResolvedValueOnce(jsonResponse(401, { detail: 'Invalid username or password' }));
    await expect(login('user', 'wrong')).rejects.toMatchObject({ kind: 'unauthorized' });
    expect(getToken()).toBeNull();

    fetchMock.mockResolvedValueOnce(jsonResponse(200, { access_token: 'abc.def.ghi', token_type: 'bearer', expires_in: 3600 }));
    const response = await login('user', 'right');
    expect(response.access_token).toBe('abc.def.ghi');
  });

  it('AsyncState renders the exact sanitized outcome_unknown message (R38)', () => {
    render(createElement(AsyncState, { loading: false, errorKind: 'outcome_unknown', isEmpty: false, children: null }));
    expect(screen.getByRole('alert')).toHaveTextContent(
      'The outcome of this request could not be confirmed. Refresh before trying again.'
    );
  });

  it('supports request cancellation via AbortSignal for stale-response suppression', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    const controller = new AbortController();
    fetchMock.mockImplementationOnce((_url: string, init?: RequestInit) => {
      expect(init?.signal).toBe(controller.signal);
      controller.abort();
      return Promise.reject(new DOMException('Aborted', 'AbortError'));
    });
    const failure = await api.listShifts(controller.signal).catch((cause: unknown) => cause);
    expect(failure).toBeInstanceOf(ApiError);
    expect((failure as ApiError).kind).toBe('cancelled');
  });
});
