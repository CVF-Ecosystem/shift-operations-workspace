import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReportActions } from '../features/operator-actions/ReportActions';
import { setToken } from '../features/authentication/session';
import type { ReportEntry } from '../services/operatorApi';
import type { ReportExportFormat, ReportExportView } from '../services/reportExport';

const currentReportId = '123e4567-e89b-12d3-a456-426614174000';
const historicalReportId = '223e4567-e89b-12d3-a456-426614174001';
const originalCreateObjectURL = Object.getOwnPropertyDescriptor(URL, 'createObjectURL');
const originalRevokeObjectURL = Object.getOwnPropertyDescriptor(URL, 'revokeObjectURL');
const originalOnline = Object.getOwnPropertyDescriptor(navigator, 'onLine');

function makeReport(reportId: string, version: number, isCurrent: boolean, status: ReportEntry['status']): ReportEntry {
  return {
    report_id: reportId,
    shift_id: 'shift-1',
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

function exportResponse(reportId: string, version: number, format: ReportExportFormat, view: ReportExportView): Response {
  const contentType = format === 'pdf'
    ? 'application/pdf'
    : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
  const bytes = format === 'pdf' ? [0x25, 0x50, 0x44, 0x46, 0x00, 0xff] : [0x50, 0x4b, 0x03, 0x04, 0x00, 0xff];
  return new Response(new Uint8Array(bytes), {
    status: 200,
    headers: {
      'Content-Type': contentType,
      'Content-Disposition': `attachment; filename="report-${reportId}-v${version}-${view}.${format}"`
    }
  });
}

function errorResponse(status: number, detail: unknown): Response {
  return new Response(JSON.stringify({ detail }), { status, headers: { 'Content-Type': 'application/json' } });
}

describe('report download controls', () => {
  let fetchMock: ReturnType<typeof vi.fn>;
  let createObjectURL: ReturnType<typeof vi.fn>;
  let revokeObjectURL: ReturnType<typeof vi.fn>;
  let clickedFilenames: string[];

  beforeEach(() => {
    sessionStorage.clear();
    setToken('report-download-test-token');
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    createObjectURL = vi.fn((_blob: Blob) => 'blob:report-export');
    revokeObjectURL = vi.fn();
    Object.defineProperty(URL, 'createObjectURL', { configurable: true, writable: true, value: createObjectURL });
    Object.defineProperty(URL, 'revokeObjectURL', { configurable: true, writable: true, value: revokeObjectURL });
    clickedFilenames = [];
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (this: HTMLAnchorElement) {
      clickedFilenames.push(this.download);
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    sessionStorage.clear();
    if (originalCreateObjectURL) Object.defineProperty(URL, 'createObjectURL', originalCreateObjectURL);
    else Reflect.deleteProperty(URL, 'createObjectURL');
    if (originalRevokeObjectURL) Object.defineProperty(URL, 'revokeObjectURL', originalRevokeObjectURL);
    else Reflect.deleteProperty(URL, 'revokeObjectURL');
    if (originalOnline) Object.defineProperty(navigator, 'onLine', originalOnline);
    else Reflect.deleteProperty(navigator, 'onLine');
  });

  it('offers all views/formats for current and historical versions and downloads literal authenticated bytes', async () => {
    const current = makeReport(currentReportId, 3, true, 'DRAFT');
    const historical = makeReport(historicalReportId, 2, false, 'APPROVED');
    fetchMock.mockResolvedValueOnce(exportResponse(historicalReportId, 2, 'xlsx', 'incident-report'));

    render(<ReportActions shiftId="shift-1" reports={[current, historical]} onRefresh={vi.fn().mockResolvedValue(undefined)} />);

    expect(screen.getByText('Historical report snapshot; this version is not current.')).toBeInTheDocument();
    expect(screen.getByText('Version 2 · Status: APPROVED · Historical version')).toBeInTheDocument();
    expect(screen.getAllByRole('option')).toHaveLength(12);
    expect(clickedFilenames).toEqual([]);
    expect(createObjectURL).not.toHaveBeenCalled();

    await userEvent.selectOptions(screen.getByRole('combobox', { name: 'View for report version 2' }), 'incident-report');
    await userEvent.selectOptions(screen.getByRole('combobox', { name: 'Format for report version 2' }), 'xlsx');
    await userEvent.click(screen.getByRole('button', { name: 'Download report version 2' }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    const [url, options] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe(`http://localhost:8000/reports/${historicalReportId}/export?format=xlsx&view=incident-report`);
    expect(options.method).toBe('GET');
    expect(options.headers).toEqual({ Authorization: 'Bearer report-download-test-token' });
    expect(options.signal).toBeInstanceOf(AbortSignal);
    expect(createObjectURL).toHaveBeenCalledTimes(1);
    const receivedBlob = createObjectURL.mock.calls[0][0] as Blob;
    expect(Array.from(new Uint8Array(await receivedBlob.arrayBuffer()))).toEqual([0x50, 0x4b, 0x03, 0x04, 0x00, 0xff]);
    expect(clickedFilenames).toEqual([`report-${historicalReportId}-v2-incident-report.xlsx`]);
    expect(await screen.findByRole('status')).toHaveTextContent('Download started for report version 2.');
    await waitFor(() => expect(revokeObjectURL).toHaveBeenCalledWith('blob:report-export'));
  });

  it('clears the tab session on 401 and never treats the JSON error body as a file', async () => {
    fetchMock.mockResolvedValueOnce(errorResponse(401, 'Bearer token is invalid'));
    render(<ReportActions shiftId="shift-1" reports={[makeReport(currentReportId, 1, true, 'DRAFT')]} onRefresh={vi.fn().mockResolvedValue(undefined)} />);

    await userEvent.click(screen.getByRole('button', { name: 'Download report version 1' }));

    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Your session has expired. Please sign in again.');
    expect(alert).not.toHaveTextContent('Bearer token is invalid');
    expect(sessionStorage.getItem('shiftops.session.token')).toBeNull();
    expect(createObjectURL).not.toHaveBeenCalled();
    expect(clickedFilenames).toEqual([]);
  });

  it('maps 503 EXPORT_BUSY to an explicit retry and only downloads after a new user action', async () => {
    fetchMock
      .mockResolvedValueOnce(errorResponse(503, { code: 'EXPORT_BUSY', message: 'private worker detail' }))
      .mockResolvedValueOnce(exportResponse(currentReportId, 1, 'pdf', 'shift-summary'));
    render(<ReportActions shiftId="shift-1" reports={[makeReport(currentReportId, 1, true, 'DRAFT')]} onRefresh={vi.fn().mockResolvedValue(undefined)} />);

    const download = screen.getByRole('button', { name: 'Download report version 1' });
    await userEvent.click(download);
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Report export is busy. Choose Download again to retry.');
    expect(alert).not.toHaveTextContent('private worker detail');
    expect(createObjectURL).not.toHaveBeenCalled();

    await userEvent.click(download);
    expect(await screen.findByRole('status')).toHaveTextContent('Download started for report version 1.');
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(createObjectURL).toHaveBeenCalledTimes(1);
  });

  it('uses the exact safe filename when CORS hides Content-Disposition', async () => {
    fetchMock.mockResolvedValueOnce(new Response(new Uint8Array([0x25, 0x50, 0x44, 0x46]), {
      status: 200,
      headers: { 'Content-Type': 'application/pdf' }
    }));
    render(<ReportActions shiftId="shift-1" reports={[makeReport(currentReportId, 1, true, 'DRAFT')]} onRefresh={vi.fn().mockResolvedValue(undefined)} />);

    await userEvent.click(screen.getByRole('button', { name: 'Download report version 1' }));

    expect(await screen.findByRole('status')).toHaveTextContent('Download started for report version 1.');
    expect(clickedFilenames).toEqual([`report-${currentReportId}-v1-shift-summary.pdf`]);
  });

  it('aborts an in-flight request without creating a file or reporting success', async () => {
    fetchMock.mockImplementation((_url: string, init: RequestInit) => new Promise<Response>((_resolve, reject) => {
      init.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
    }));
    render(<ReportActions shiftId="shift-1" reports={[makeReport(currentReportId, 1, true, 'DRAFT')]} onRefresh={vi.fn().mockResolvedValue(undefined)} />);

    await userEvent.click(screen.getByRole('button', { name: 'Download report version 1' }));
    await userEvent.click(await screen.findByRole('button', { name: 'Cancel download for report version 1' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('Download cancelled.');
    expect(screen.queryByText(/Download started/)).not.toBeInTheDocument();
    expect(createObjectURL).not.toHaveBeenCalled();
    expect(clickedFilenames).toEqual([]);
  });

  it('refuses an offline or unsafe-filename response without creating an object URL', async () => {
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: false });
    render(<ReportActions shiftId="shift-1" reports={[makeReport(currentReportId, 1, true, 'DRAFT')]} onRefresh={vi.fn().mockResolvedValue(undefined)} />);
    await userEvent.click(screen.getByRole('button', { name: 'Download report version 1' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('You are offline. Reconnect before downloading this report.');
    expect(fetchMock).not.toHaveBeenCalled();
    expect(createObjectURL).not.toHaveBeenCalled();

    Object.defineProperty(navigator, 'onLine', { configurable: true, value: true });
    fetchMock.mockResolvedValueOnce(new Response(new Uint8Array([0x25, 0x50, 0x44, 0x46]), {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="report-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa-v1-shift-summary.pdf"'
      }
    }));
    await userEvent.click(screen.getByRole('button', { name: 'Download report version 1' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('The report could not be downloaded. Choose Download to try again.');
    expect(createObjectURL).not.toHaveBeenCalled();
    expect(clickedFilenames).toEqual([]);
  });

});
