import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReportActions } from '../features/operator-actions/ReportActions';
import { setToken } from '../features/authentication/session';
import type { ReportEntry } from '../services/operatorApi';
import type { ReportSection, ReportSourceRef } from '../types/backendContracts';

const jsonResponse = (status: number, body: unknown): Response =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

// WO C3C-BUILD-REREV-F3: a real-shaped section/manifest entry, not a
// {title: string} placeholder - proves the DTO round-trips the actual
// backend ReportSection/ReportSourceRef contract (section_type/records,
// record_type/record_id/source_version/source_digest).
const realSection: ReportSection = {
  section_type: 'tasks',
  records: [{ record_type: 'Task', record_id: 't-1', title: 'Check meter', status: 'OPEN' }]
};
const realManifestEntry: ReportSourceRef = {
  record_type: 'Task', record_id: 't-1', source_version: 1, source_digest: 'a'.repeat(64)
};

describe('operator report actions component', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    sessionStorage.clear();
    setToken('test-token');
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => vi.unstubAllGlobals());

  it('renders report panel with real-shaped sections/manifest, submits to IN_REVIEW, never renders snapshot_digest', async () => {
    const onRefresh = vi.fn().mockResolvedValue(undefined);
    const report: ReportEntry = {
      report_id: 'r-1', shift_id: 's-1', report_type: 'END_SHIFT', version: 1, status: 'DRAFT', is_current: true,
      sections: [realSection], source_manifest: [realManifestEntry], snapshot_digest: 'SECRET_SNAPSHOT_DIGEST_HASH',
      generated_from_cutoff: '2026-08-01T00:00:00Z', created_at: '2026-08-01T00:00:00Z'
    };

    render(<ReportActions shiftId="s-1" reports={[report]} onRefresh={onRefresh} />);

    expect(screen.getByText('DRAFT')).toBeInTheDocument();
    expect(screen.getAllByText('1')).toHaveLength(2); // version and sections.length both 1
    expect(document.body.innerHTML).not.toContain('SECRET_SNAPSHOT_DIGEST_HASH');

    fetchMock.mockResolvedValueOnce(jsonResponse(200, { ...report, status: 'IN_REVIEW' }));
    await userEvent.click(screen.getByRole('button', { name: 'Submit for review' }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/reports/r-1/submit-review'),
      expect.objectContaining({ body: JSON.stringify({ expected_version: 1, expected_status: 'DRAFT' }) })
    ));
    expect(onRefresh).toHaveBeenCalled();
  });

  it('offers Generate report only when no current report exists, and successor-version once one does (WO C3C-BUILD-REV-F4)', async () => {
    const onRefresh = vi.fn().mockResolvedValue(undefined);
    const { unmount } = render(<ReportActions shiftId="s-1" reports={[]} onRefresh={onRefresh} />);
    expect(screen.getByRole('button', { name: 'Generate report' })).toBeInTheDocument();
    unmount();

    const report: ReportEntry = {
      report_id: 'r-2', shift_id: 's-1', report_type: 'END_SHIFT', version: 1, status: 'DRAFT', is_current: true,
      sections: [], source_manifest: [], snapshot_digest: 'x',
      generated_from_cutoff: '2026-08-01T00:00:00Z', created_at: '2026-08-01T00:00:00Z'
    };
    render(<ReportActions shiftId="s-1" reports={[report]} onRefresh={onRefresh} />);
    expect(screen.queryByRole('button', { name: 'Generate report' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Regenerate report' })).not.toBeInTheDocument();

    fetchMock.mockResolvedValueOnce(jsonResponse(200, { ...report, version: 2 }));
    await userEvent.click(screen.getByRole('button', { name: 'Create new version' }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/reports/r-2/versions'),
      expect.objectContaining({ body: JSON.stringify({ expected_version: 1, expected_status: 'DRAFT' }) })
    ));
  });

  it.each([
    ['DRAFT', true, true],
    ['IN_REVIEW', true, false],
    ['APPROVED', false, false],
    ['FROZEN', false, false]
  ] as const)('renders only backend-legal operator controls for %s', (status, canVersion, canSubmit) => {
    const report: ReportEntry = {
      report_id: `r-${status}`, shift_id: 's-1', report_type: 'END_SHIFT', version: 1, status, is_current: true,
      sections: [], source_manifest: [], snapshot_digest: 'x',
      generated_from_cutoff: '2026-08-01T00:00:00Z', created_at: '2026-08-01T00:00:00Z'
    };
    render(<ReportActions shiftId="s-1" reports={[report]} onRefresh={vi.fn().mockResolvedValue(undefined)} />);
    expect(screen.queryByRole('button', { name: 'Create new version' }) !== null).toBe(canVersion);
    expect(screen.queryByRole('button', { name: 'Submit for review' }) !== null).toBe(canSubmit);
    expect(screen.queryByRole('button', { name: 'Generate report' })).not.toBeInTheDocument();
  });

  it('disables version and submit buttons while either is in-flight (shared Report lock, WO C3C-BUILD-REV-F3)', async () => {
    const onRefresh = vi.fn().mockResolvedValue(undefined);
    const report: ReportEntry = {
      report_id: 'r-3', shift_id: 's-1', report_type: 'END_SHIFT', version: 1, status: 'DRAFT', is_current: true,
      sections: [], source_manifest: [], snapshot_digest: 'x',
      generated_from_cutoff: '2026-08-01T00:00:00Z', created_at: '2026-08-01T00:00:00Z'
    };
    let resolveVersion!: (value: Response) => void;
    fetchMock.mockReturnValueOnce(new Promise<Response>((r) => (resolveVersion = r)));

    render(<ReportActions shiftId="s-1" reports={[report]} onRefresh={onRefresh} />);
    await userEvent.click(screen.getByRole('button', { name: 'Create new version' }));

    expect(screen.getByRole('button', { name: 'Versioning…' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Submit for review' })).toBeDisabled();

    resolveVersion(jsonResponse(200, { ...report, version: 2 }));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Create new version' })).not.toBeDisabled());
  });
});
