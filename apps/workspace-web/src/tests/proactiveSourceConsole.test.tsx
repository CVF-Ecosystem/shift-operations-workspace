import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { OperationsConsole } from '../app/OperationsConsole';
import { setPrincipalUserId, setToken } from '../features/authentication/session';

describe('console source placement', () => {
  beforeEach(() => { sessionStorage.clear(); setToken('source-token'); setPrincipalUserId('u1'); });
  afterEach(() => vi.unstubAllGlobals());

  it('mounts after shift selector, independent of selected shift, without source auto-read', async () => {
    const fetchMock = vi.fn((url: string) => {
      if (url.includes('/shifts')) return Promise.resolve(new Response(JSON.stringify([
        { shift_id: 's1', name: 'First', starts_at: '2026-01-01T00:00:00Z',
          ends_at: '2026-01-01T08:00:00Z', status: 'OPEN', version: 1,
          created_at: '2026-01-01T00:00:00Z' }
      ]), { status: 200 }));
      return Promise.resolve(new Response('{}', { status: 403 }));
    });
    vi.stubGlobal('fetch', fetchMock);
    render(<OperationsConsole onSignedOut={vi.fn()} />);
    await waitFor(() => expect(screen.getByLabelText('Shift')).toBeInTheDocument());
    expect(screen.getByRole('heading', { name: 'Kiểm tra nguồn dữ liệu' })).toBeInTheDocument();
    expect(document.querySelector('.shift-selector')?.nextElementSibling?.className).toBe('proactive-source');
    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's1');
    expect(screen.getByRole('heading', { name: 'Kiểm tra nguồn dữ liệu' })).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([url]) => String(url).includes('/proactive/source'))).toBe(false);
  });
});
