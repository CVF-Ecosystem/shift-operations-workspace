import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
// @ts-expect-error Browser tsconfig omits Node types; Vitest runs on the installed Node runtime.
import { webcrypto } from 'node:crypto';
import { ProactiveSourcePanel } from '../features/proactive-source/ProactiveSourcePanel';
import { clearSession, setPrincipalUserId, setToken } from '../features/authentication/session';
import { ACTOR, jsonResponse, positives } from './proactiveSourceTestData';

async function fill() {
  await userEvent.type(screen.getByLabelText('Bắt đầu UTC'), '2026-01-01T00:00');
  await userEvent.type(screen.getByLabelText('Kết thúc UTC'), '2026-01-02T12:00');
  await userEvent.type(screen.getByLabelText('Thời điểm đọc UTC'), '2026-01-02T12:00');
}

describe('source request lifecycle', () => {
  beforeEach(() => { sessionStorage.clear(); setToken('source-token'); setPrincipalUserId(ACTOR); vi.stubGlobal('crypto', webcrypto); });
  afterEach(() => vi.unstubAllGlobals());

  it('invalidates a late success on input edit even if fetch ignores abort', async () => {
    let finish!: (response: Response) => void;
    const fetchMock = vi.fn((_url: string, _init: RequestInit) =>
      new Promise<Response>((resolve) => { finish = resolve; }));
    vi.stubGlobal('fetch', fetchMock);
    render(<ProactiveSourcePanel />);
    await fill(); await userEvent.click(screen.getByRole('button', { name: 'Xem nguồn dữ liệu' }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    await userEvent.clear(screen.getByLabelText('Kết thúc UTC'));
    finish(jsonResponse(200, positives[0].receipt));
    await waitFor(() => expect(screen.getByRole('status')).not.toHaveTextContent('Dữ liệu thử nghiệm'));
  });

  it('invalidates a late error on resubmit and session replacement', async () => {
    const pending: Array<(response: Response) => void> = [];
    const fetchMock = vi.fn((_url: string, _init: RequestInit) =>
      new Promise<Response>((resolve) => { pending.push(resolve); }));
    vi.stubGlobal('fetch', fetchMock);
    render(<ProactiveSourcePanel />);
    await fill();
    await userEvent.click(screen.getByRole('button', { name: 'Xem nguồn dữ liệu' }));
    await userEvent.click(screen.getByRole('button', { name: 'Xem nguồn dữ liệu' }));
    expect(fetchMock).toHaveBeenCalledTimes(2);
    pending[0](jsonResponse(500, { detail: 'PRIVATE_SERVER_DETAIL' }));
    expect(screen.getByRole('status')).toHaveTextContent('Đang đọc');
    act(() => setToken('replacement'));
    pending[1](jsonResponse(200, positives[0].receipt));
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Nhập ba'));
    expect(document.body.innerHTML).not.toContain('PRIVATE_SERVER_DETAIL');
    expect(document.body.innerHTML).not.toContain('Dữ liệu thử nghiệm');
  });

  it('clears retained output on termination', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, positives[0].receipt));
    vi.stubGlobal('fetch', fetchMock);
    const { unmount } = render(<ProactiveSourcePanel />);
    await fill(); await userEvent.click(screen.getByRole('button', { name: 'Xem nguồn dữ liệu' }));
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Dữ liệu thử nghiệm'));
    act(() => clearSession());
    expect(screen.getByRole('status')).not.toHaveTextContent('Dữ liệu thử nghiệm');
    unmount();
  });

  it('aborts on unmount and ignores a late 401 even when fetch ignores abort', async () => {
    let finish!: (response: Response) => void;
    const fetchMock = vi.fn((_url: string, _init: RequestInit) =>
      new Promise<Response>((resolve) => { finish = resolve; }));
    vi.stubGlobal('fetch', fetchMock);
    const { unmount } = render(<ProactiveSourcePanel />);
    await fill(); await userEvent.click(screen.getByRole('button', { name: 'Xem nguồn dữ liệu' }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    const signal = fetchMock.mock.calls[0][1].signal as AbortSignal;
    expect(signal.aborted).toBe(false);
    unmount();
    expect(signal.aborted).toBe(true);
    setToken('replacement');
    finish(jsonResponse(401, { detail: 'PRIVATE_SERVER_DETAIL' }));
    await Promise.resolve();
    expect(sessionStorage.getItem('shiftops.session.token')).toBe('replacement');
    expect(document.body.innerHTML).not.toContain('PRIVATE_SERVER_DETAIL');
  });
});
