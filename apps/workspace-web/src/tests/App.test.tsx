import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from '../app/App';
import { setToken } from '../features/authentication/session';

const jsonResponse = (status: number, body: unknown): Response =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

const shift = (id: string, name: string) => ({ shift_id: id, name, starts_at: '2026-07-29T00:00:00Z', ends_at: '2026-07-29T08:00:00Z', status: 'OPEN', version: 1, created_at: '2026-07-29T00:00:00Z' });
const event = (id: string, shiftId: string, title: string, state = 'CONFIRMED') => ({ event_id: id, shift_id: shiftId, event_type: 'x', title, description: null, risk_class: 'R1', state, starts_at: null, ends_at: null, owner_id: null, evidence: [], version: 1 });
const task = (title: string) => ({ task_id: 't1', shift_id: 's1', title, description: null, status: 'OPEN', owner_id: null, due_at: null, risk_class: 'R1', state: 'CONFIRMED', evidence: [], version: 1, created_at: '2026-07-29T00:00:00Z' });
const customerRequest = (summary: string) => ({ request_id: 'c1', customer_id: 'cust-1', shift_id: 's1', summary, details: null, status: 'NEW', source_message_id: null, received_at: '2026-07-29T00:00:00Z', promised_at: null, owner_id: null });
const incident = (summary: string, status = 'REPORTED', riskClass = 'R2') => ({ incident_id: 'i1', shift_id: 's1', risk_class: riskClass, summary, description: null, status, owner_id: null, evidence: [], version: 1, created_at: '2026-07-29T00:00:00Z' });
const handover = (status: string) => ({ handover_id: 'h1', from_shift_id: 's1', to_shift_id: 's2', status, items: [], created_by: 'u1', reviewed_by: 'u2', reviewed_at: '2026-07-29T07:00:00Z', received_by: null, acknowledged_at: null, version: 1, created_at: '2026-07-29T00:00:00Z', acknowledged: false });

const SHIFTS = [shift('s1', 'Day shift'), shift('s2', 'Night shift')];
const emptyOpenWork = (id: string) => ({ shift_id: id, tasks: [], customer_requests: [], incidents: [] });

type ReadOverrides = { events?: Record<string, unknown[]>; openWork?: Record<string, unknown>; incidents?: unknown[]; handovers?: unknown[]; deferShiftId?: string };

function mockReads(fetchMock: ReturnType<typeof vi.fn>, overrides: ReadOverrides = {}) {
  const pending = new Map<string, (value: Response) => void>();
  const defer = overrides.deferShiftId;
  fetchMock.mockImplementation((url: string) => {
    if (url.includes('/shifts') && !url.includes('open-work')) return Promise.resolve(jsonResponse(200, SHIFTS));
    if (defer && url.includes(`/events?shift_id=${defer}`)) return new Promise<Response>((r) => pending.set(defer, r));
    if (defer && url.includes(`/shifts/${defer}/open-work`)) return new Promise<Response>((r) => pending.set(`${defer}-open-work`, r));
    if (url.includes('/events')) {
      const shiftId = new URL(url, 'http://x').searchParams.get('shift_id') ?? 's1';
      return Promise.resolve(jsonResponse(200, overrides.events?.[shiftId] ?? []));
    }
    if (url.includes('open-work')) {
      const shiftId = url.split('/shifts/')[1]?.split('/')[0] ?? 's1';
      return Promise.resolve(jsonResponse(200, overrides.openWork?.[shiftId] ?? emptyOpenWork(shiftId)));
    }
    if (url.includes('/incidents')) return Promise.resolve(jsonResponse(200, overrides.incidents ?? []));
    if (url.includes('/handovers')) return Promise.resolve(jsonResponse(200, overrides.handovers ?? []));
    return Promise.resolve(jsonResponse(404, { detail: 'not found' }));
  });
  return pending;
}

let fetchMock: ReturnType<typeof vi.fn>;

async function signInWithSession(overrides?: ReadOverrides) {
  setToken('existing-token');
  const pending = mockReads(fetchMock, overrides);
  render(<App />);
  await waitFor(() => expect(screen.getByLabelText('Shift')).toBeInTheDocument());
  return pending;
}

describe('App', () => {
  beforeEach(() => {
    sessionStorage.clear();
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => vi.unstubAllGlobals());

  it('shows the login form when no session exists', () => {
    render(<App />);
    expect(screen.getByRole('form', { name: 'Sign in' })).toBeInTheDocument();
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
  });

  it('shows a pending state while the login request is in flight', async () => {
    let resolveLogin!: (value: Response) => void;
    fetchMock.mockReturnValueOnce(new Promise<Response>((r) => (resolveLogin = r)));
    render(<App />);
    await userEvent.type(screen.getByLabelText('Username'), 'alice');
    await userEvent.type(screen.getByLabelText('Password'), 'right');
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    expect(screen.getByRole('button', { name: 'Signing in…' })).toBeDisabled();
    resolveLogin(jsonResponse(200, { access_token: 't', token_type: 'bearer', expires_in: 3600 }));
    mockReads(fetchMock);
    await waitFor(() => expect(screen.getByLabelText('Shift')).toBeInTheDocument());
  });

  it('shows a generic failure message on invalid login and never echoes credentials', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(401, { detail: 'Invalid username or password' }));
    render(<App />);
    await userEvent.type(screen.getByLabelText('Username'), 'alice');
    await userEvent.type(screen.getByLabelText('Password'), 'wrong-pass');
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Invalid username or password.');
    expect(document.body.innerHTML).not.toContain('wrong-pass');
    expect(sessionStorage.getItem('shiftops.session.token')).toBeNull();
  });

  it('stores the token only in sessionStorage, never localStorage, on successful login', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { access_token: 'jwt.value.here', token_type: 'bearer', expires_in: 3600 }));
    mockReads(fetchMock);
    render(<App />);
    await userEvent.type(screen.getByLabelText('Username'), 'alice');
    await userEvent.type(screen.getByLabelText('Password'), 'correct-pass');
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    await waitFor(() => expect(screen.getByLabelText('Shift')).toBeInTheDocument());
    expect(sessionStorage.getItem('shiftops.session.token')).toBe('jwt.value.here');
    expect(localStorage.getItem('shiftops.session.token')).toBeNull();
    expect(Object.keys(localStorage)).toHaveLength(0);
  });

  it('restores session on mount, and logout clears token/state and returns to login', async () => {
    await signInWithSession();
    expect(screen.queryByRole('form', { name: 'Sign in' })).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Sign out' }));
    expect(screen.getByRole('form', { name: 'Sign in' })).toBeInTheDocument();
    expect(sessionStorage.getItem('shiftops.session.token')).toBeNull();
  });

  it('an HTTP 401 on any operational read clears the session and returns to login', async () => {
    setToken('expiring-token');
    fetchMock.mockResolvedValueOnce(jsonResponse(401, { detail: 'Invalid username or password' }));
    render(<App />);
    await waitFor(() => expect(screen.getByRole('form', { name: 'Sign in' })).toBeInTheDocument());
    expect(sessionStorage.getItem('shiftops.session.token')).toBeNull();
  });

  it('shows a connecting indicator while shifts load, then connected', async () => {
    setToken('existing-token');
    let resolveShifts!: (value: Response) => void;
    fetchMock.mockReturnValueOnce(new Promise<Response>((r) => (resolveShifts = r)));
    render(<App />);
    expect(await screen.findByText(/Connecting…/)).toBeInTheDocument();
    resolveShifts(jsonResponse(200, SHIFTS));
    mockReads(fetchMock);
    await waitFor(() => expect(screen.getByText(/Connected/)).toBeInTheDocument());
  });

  it.each([
    ['network failure', () => fetchMock.mockRejectedValue(new TypeError('Failed to fetch')), 'The outcome of this request could not be confirmed. Refresh before trying again.'],
    ['5xx read', () => fetchMock.mockResolvedValue(jsonResponse(500, { detail: 'boom' })), null]
  ])('renders a controlled error state and indicator on %s', async (_label, arrange, message) => {
    setToken('existing-token');
    arrange(); render(<App />);
    const alerts = (await screen.findAllByRole('alert')).map((a) => a.textContent);
    expect(alerts).toContain(message ?? alerts[0]);
    expect(screen.getByText(/Connection issue/)).toBeInTheDocument();
  });

  it('shows an operational loading state while shift detail is in flight', async () => {
    const pending = await signInWithSession({ deferShiftId: 's1' });
    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's1');
    expect((await screen.findAllByText('Loading…')).length).toBeGreaterThan(0);
    pending.get('s1')?.(jsonResponse(200, []));
    pending.get('s1-open-work')?.(jsonResponse(200, emptyOpenWork('s1')));
    await waitFor(() => expect(screen.queryAllByText('Loading…')).toHaveLength(0));
  });

  it('renders the empty timeline state, then only CONFIRMED events once populated', async () => {
    await signInWithSession({ events: { s1: [event('e1', 's1', 'Confirmed one'), event('e2', 's1', 'Proposed one', 'PROPOSED')] } });
    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's1');
    await screen.findByText('Confirmed one');
    expect(screen.queryByText('Proposed one')).not.toBeInTheDocument();
  });

  it('renders grouped open work, incident summary and handover summary for one shift', async () => {
    const openWork = { s1: { shift_id: 's1', tasks: [task('Check meter')], customer_requests: [customerRequest('Billing question')], incidents: [incident('Power flicker')] } };
    await signInWithSession({ openWork, incidents: [incident('Line down', 'ACKNOWLEDGED', 'R3')], handovers: [handover('REVIEWED')] });
    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's1');
    const panel = await screen.findByLabelText('Open work');
    expect(within(panel).getByText('Check meter')).toBeInTheDocument();
    expect(within(panel).getByText('Billing question')).toBeInTheDocument();
    expect(within(panel).getByText('Power flicker')).toBeInTheDocument();
    const incidentSummary = screen.getByLabelText('Incident summary');
    expect(within(incidentSummary).getByText('ACKNOWLEDGED: 1')).toBeInTheDocument();
    expect(within(incidentSummary).getByText('R3: 1')).toBeInTheDocument();
    const handoverSummary = screen.getByLabelText('Handover summary');
    expect(within(handoverSummary).getByText('REVIEWED')).toBeInTheDocument();
  });

  it('suppresses a stale response when switching shifts before the first request resolves', async () => {
    const pending = await signInWithSession({ deferShiftId: 's1' });
    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's1');
    mockReads(fetchMock, { events: { s2: [event('e2', 's2', 'Night event')] } });
    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's2');
    await screen.findByText('Night event');

    pending.get('s1')?.(jsonResponse(200, [event('e1', 's1', 'Stale day event')]));
    pending.get('s1-open-work')?.(jsonResponse(200, emptyOpenWork('s1')));
    await waitFor(() => expect(screen.getByText('Night event')).toBeInTheDocument());
    expect(screen.queryByText('Stale day event')).not.toBeInTheDocument();
  });

  it('renders no mutation controls anywhere in the authenticated console', async () => {
    await signInWithSession();
    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's1');
    await screen.findByLabelText('Shift timeline');
    const forbidden = ['create', 'confirm', 'approve', 'transition', 'close', 'freeze', 'acknowledge', 'review'];
    for (const button of screen.getAllByRole('button')) {
      const label = button.textContent?.toLowerCase() ?? '';
      for (const word of forbidden) expect(label).not.toContain(word);
    }
  });
});
