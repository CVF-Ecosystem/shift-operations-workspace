import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReportActions } from '../features/operator-actions/ReportActions';
import { setToken } from '../features/authentication/session';
import type { ReportEntry } from '../services/operatorApi';

const currentReportId = '123e4567-e89b-12d3-a456-426614174000';
const historicalReportId = '223e4567-e89b-12d3-a456-426614174001';

function makeReport(
  reportId: string,
  version: number,
  isCurrent: boolean,
  status: ReportEntry['status'],
  shiftId = 'shift-1'
): ReportEntry {
  return {
    report_id: reportId,
    shift_id: shiftId,
    report_type: 'END_SHIFT',
    version,
    status,
    is_current: isCurrent,
    sections: [],
    source_manifest: [],
    snapshot_digest: 'a'.repeat(64),
    generated_from_cutoff: '2026-08-01T00:00:00Z',
    created_at: '2026-08-01T00:00:00Z'
  };
}

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

function errorResponse(status: number, detail: unknown): Response {
  return jsonResponse(status, { detail });
}

describe('report download history', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    sessionStorage.clear();
    setToken('report-download-test-token');
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    sessionStorage.clear();
  });

  it('loads noncurrent versions only after the explicit history action with the exact query', async () => {
    const current = makeReport(currentReportId, 2, true, 'DRAFT');
    const historical = makeReport(historicalReportId, 1, false, 'APPROVED');
    fetchMock.mockResolvedValueOnce(jsonResponse(200, [current, historical]));
    render(<ReportActions shiftId="shift-1" reports={[current]} onRefresh={vi.fn().mockResolvedValue(undefined)} />);

    expect(fetchMock).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: 'Download report version 2' })).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Show historical report versions' }));

    expect(await screen.findByRole('button', { name: 'Download report version 1' })).toBeInTheDocument();
    expect(screen.getByText('Historical report snapshot; this version is not current.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create new version' })).toBeInTheDocument();
    const [url, options] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('http://localhost:8000/reports?shift_id=shift-1&include_history=true');
    expect(options.method).toBe('GET');
    expect(options.headers).toEqual({ Authorization: 'Bearer report-download-test-token' });
    expect(options.signal).toBeInstanceOf(AbortSignal);
    expect(screen.getByRole('button', { name: 'Hide historical report versions' })).toHaveAttribute('aria-expanded', 'true');
  });

  it('shows bounded history-load errors and lets the operator retry explicitly', async () => {
    fetchMock
      .mockResolvedValueOnce(errorResponse(500, { code: 'INTERNAL', message: 'private stack detail' }))
      .mockResolvedValueOnce(jsonResponse(200, []));
    render(<ReportActions shiftId="shift-1" reports={[makeReport(currentReportId, 1, true, 'DRAFT')]} onRefresh={vi.fn().mockResolvedValue(undefined)} />);

    await userEvent.click(screen.getByRole('button', { name: 'Show historical report versions' }));
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Historical report versions could not be loaded. Choose Retry to try again.');
    expect(alert).not.toHaveTextContent('private stack detail');
    await userEvent.click(screen.getByRole('button', { name: 'Retry loading historical report versions' }));
    expect(await screen.findByRole('status')).toHaveTextContent('No historical report versions.');
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it('aborts and resets history state when the shift or current report changes', async () => {
    const signals: AbortSignal[] = [];
    fetchMock.mockImplementation((_url: string, init: RequestInit) => new Promise<Response>((_resolve, reject) => {
      const signal = init.signal as AbortSignal;
      signals.push(signal);
      signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')), { once: true });
    }));
    const currentV2 = makeReport(currentReportId, 2, true, 'DRAFT');
    const currentV3 = makeReport(currentReportId, 3, true, 'DRAFT', 'shift-2');
    const onRefresh = vi.fn().mockResolvedValue(undefined);
    const { rerender } = render(<ReportActions shiftId="shift-1" reports={[currentV2]} onRefresh={onRefresh} />);

    await userEvent.click(screen.getByRole('button', { name: 'Show historical report versions' }));
    await waitFor(() => expect(signals).toHaveLength(1));
    rerender(<ReportActions shiftId="shift-2" reports={[makeReport(currentReportId, 2, true, 'DRAFT', 'shift-2')]} onRefresh={onRefresh} />);
    await waitFor(() => expect(signals[0].aborted).toBe(true));
    expect(screen.getByRole('button', { name: 'Show historical report versions' })).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: 'Show historical report versions' }));
    await waitFor(() => expect(signals).toHaveLength(2));
    rerender(<ReportActions shiftId="shift-2" reports={[currentV3]} onRefresh={onRefresh} />);
    await waitFor(() => expect(signals[1].aborted).toBe(true));
    expect(screen.getByRole('button', { name: 'Show historical report versions' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Download report version 3' })).toBeInTheDocument();
    expect(screen.queryByText('Loading historical report versions…')).not.toBeInTheDocument();
  });
});
