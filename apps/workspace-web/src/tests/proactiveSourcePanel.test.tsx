import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
// @ts-expect-error Browser tsconfig omits Node types; Vitest runs on the installed Node runtime.
import { webcrypto } from 'node:crypto';
import { ProactiveSourcePanel } from '../features/proactive-source/ProactiveSourcePanel';
import { setPrincipalUserId, setToken } from '../features/authentication/session';
import { ACTOR, jsonResponse, positives, refusalSamples } from './proactiveSourceTestData';
import { sourceWindow, utcInput } from '../features/proactive-source/useProactiveSourceRead';

async function fillWindow() {
  await userEvent.clear(screen.getByLabelText('Bắt đầu UTC'));
  await userEvent.clear(screen.getByLabelText('Kết thúc UTC'));
  await userEvent.clear(screen.getByLabelText('Thời điểm đọc UTC'));
  await userEvent.type(screen.getByLabelText('Bắt đầu UTC'), '2026-01-01T00:00');
  await userEvent.type(screen.getByLabelText('Kết thúc UTC'), '2026-01-02T12:00');
  await userEvent.type(screen.getByLabelText('Thời điểm đọc UTC'), '2026-01-02T12:00');
}

describe('manual source panel', () => {
  beforeEach(() => { sessionStorage.clear(); vi.stubGlobal('crypto', webcrypto); });
  afterEach(() => vi.unstubAllGlobals());

  it('has empty UTC inputs and no mount request; refuses invalid calendar and order locally', async () => {
    const fetchMock = vi.fn(); vi.stubGlobal('fetch', fetchMock);
    render(<ProactiveSourcePanel />);
    expect((screen.getByLabelText('Bắt đầu UTC') as HTMLInputElement).value).toBe('');
    expect(fetchMock).not.toHaveBeenCalled();
    expect(utcInput('2026-02-30T12:00')).toBeNull();
    expect(sourceWindow({ start: '2026-01-02T12:00', end: '2026-01-01T00:00', asOf: '2026-01-02T12:00' })).toBeNull();
    await userEvent.click(screen.getByRole('button', { name: 'Xem nguồn dữ liệu' }));
    expect(screen.getByRole('status')).toHaveTextContent('không hợp lệ');
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('requires verified principal, then shows synthetic counts without raw private fields', async () => {
    setToken('source-token');
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, positives[0].receipt));
    vi.stubGlobal('fetch', fetchMock);
    render(<ProactiveSourcePanel />);
    await fillWindow();
    await userEvent.click(screen.getByRole('button', { name: 'Xem nguồn dữ liệu' }));
    expect(screen.getByRole('status')).toHaveTextContent('xác minh người dùng');
    expect(fetchMock).not.toHaveBeenCalled();
    act(() => setPrincipalUserId(ACTOR));
    await fillWindow();
    await userEvent.click(screen.getByRole('button', { name: 'Xem nguồn dữ liệu' }));
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Dữ liệu thử nghiệm'));
    expect(screen.getByRole('status')).toHaveTextContent('36');
    expect(document.body.innerHTML).not.toContain(positives[0].receipt.scope_id);
    expect(document.body.innerHTML).not.toContain(positives[0].receipt.source_digest);
    expect(document.body.innerHTML).not.toContain('canonical_manifest');
    expect(localStorage).toHaveLength(0);
    expect(Object.keys(sessionStorage).sort()).toEqual(['shiftops.session.token', 'shiftops.session.user_id']);
    await userEvent.clear(screen.getByLabelText('Kết thúc UTC'));
    expect(screen.getByRole('status')).not.toHaveTextContent('Dữ liệu thử nghiệm');
    expect(Object.keys(sessionStorage).sort()).toEqual(['shiftops.session.token', 'shiftops.session.user_id']);
  });

  it('renders each fixed refusal without leaking arbitrary server detail', async () => {
    setToken('source-token'); setPrincipalUserId(ACTOR);
    const fetchMock = vi.fn(); vi.stubGlobal('fetch', fetchMock);
    const { unmount } = render(<ProactiveSourcePanel />);
    await fillWindow();
    for (const receipt of Object.values(refusalSamples)) {
      fetchMock.mockResolvedValueOnce(jsonResponse(200, receipt));
      await userEvent.click(screen.getByRole('button', { name: 'Xem nguồn dữ liệu' }));
      await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Nguồn dữ liệu từ chối'));
    }
    unmount();
    expect(document.body.innerHTML).not.toContain('PRIVATE_SERVER_DETAIL');
  });
});
