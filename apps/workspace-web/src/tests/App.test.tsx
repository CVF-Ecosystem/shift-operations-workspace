import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from '../app/App';
import { setToken } from '../features/authentication/session';

const jsonResponse = (status: number, body: unknown): Response =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

const shift = (id: string, name: string) => ({ shift_id: id, name, starts_at: '2026-07-29T00:00:00Z', ends_at: '2026-07-29T08:00:00Z', status: 'OPEN', version: 1, created_at: '2026-07-29T00:00:00Z' });
const event = (id: string, shiftId: string, title: string, state = 'CONFIRMED') => ({ event_id: id, shift_id: shiftId, event_type: 'x', title, description: null, risk_class: 'R1', state, starts_at: null, ends_at: null, owner_id: null, evidence: [], version: 1 });
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
    if (url.includes('/messages')) return Promise.resolve(jsonResponse(200, []));
    if (url.includes('/tasks') && !url.includes('creation-intents')) return Promise.resolve(jsonResponse(200, []));
    if (url.includes('/customer-requests')) return Promise.resolve(jsonResponse(200, []));
    if (url.includes('/capabilities')) return Promise.resolve(jsonResponse(200, { shift_id: 's1', actions: [], reasons: [] }));
    if (url.includes('/reports')) return Promise.resolve(jsonResponse(200, []));
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
  beforeEach(() => { sessionStorage.clear(); fetchMock = vi.fn(); vi.stubGlobal('fetch', fetchMock); });
  afterEach(() => vi.unstubAllGlobals());

  it('shows a pending login state, rejects invalid credentials without echoing them, then stores the token only in sessionStorage', async () => {
    render(<App />);
    expect(screen.getByRole('form', { name: 'Sign in' })).toBeInTheDocument();
    fetchMock.mockResolvedValueOnce(jsonResponse(401, { detail: 'Invalid username or password' }));
    await userEvent.type(screen.getByLabelText('Username'), 'alice');
    await userEvent.type(screen.getByLabelText('Password'), 'wrong-pass');
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Invalid username or password.');
    expect(document.body.innerHTML).not.toContain('wrong-pass');

    fetchMock.mockResolvedValueOnce(jsonResponse(200, { access_token: 'jwt.value.here', token_type: 'bearer', expires_in: 3600 }));
    mockReads(fetchMock);
    await userEvent.clear(screen.getByLabelText('Password'));
    await userEvent.type(screen.getByLabelText('Password'), 'correct-pass');
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    await waitFor(() => expect(screen.getByLabelText('Shift')).toBeInTheDocument());
    expect(sessionStorage.getItem('shiftops.session.token')).toBe('jwt.value.here');
    expect(localStorage.getItem('shiftops.session.token')).toBeNull();
    expect(Object.keys(localStorage)).toHaveLength(0);
  });

  it('restores session on mount, and logout clears token and returns to login', async () => {
    await signInWithSession();
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

  it('shows connecting then connected, and a controlled error/connection-issue state on an ambiguous read failure', async () => {
    setToken('existing-token');
    let resolveShifts!: (value: Response) => void;
    fetchMock.mockReturnValueOnce(new Promise<Response>((r) => (resolveShifts = r)));
    render(<App />);
    expect(await screen.findByText(/Connecting…/)).toBeInTheDocument();
    resolveShifts(jsonResponse(200, SHIFTS));
    mockReads(fetchMock);
    await waitFor(() => expect(screen.getByText(/Connected/)).toBeInTheDocument());

    fetchMock.mockRejectedValue(new TypeError('Failed to fetch'));
    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's1');
    const alerts = (await screen.findAllByRole('alert')).map((a) => a.textContent);
    expect(alerts).toContain('The outcome of this request could not be confirmed. Refresh before trying again.');
    expect(screen.getByText(/Connection issue/)).toBeInTheDocument();
  });

  it('shows a loading state while shift detail is in flight, renders grouped incident/handover summaries, and suppresses a stale response from a since-abandoned shift', async () => {
    const readOverrides = { incidents: [incident('Line down', 'ACKNOWLEDGED', 'R3')], handovers: [handover('REVIEWED')] };
    const pending = await signInWithSession({ deferShiftId: 's1', ...readOverrides });
    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's1');
    expect((await screen.findAllByText('Loading…')).length).toBeGreaterThan(0);

    mockReads(fetchMock, { events: { s2: [event('e2', 's2', 'Night event')] }, ...readOverrides });
    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's2');
    await screen.findByText('Night event');

    pending.get('s1')?.(jsonResponse(200, [event('e1', 's1', 'Stale day event')]));
    pending.get('s1-open-work')?.(jsonResponse(200, emptyOpenWork('s1')));
    await waitFor(() => expect(screen.getByText('Night event')).toBeInTheDocument());
    expect(screen.queryByText('Stale day event')).not.toBeInTheDocument();
    expect(within(screen.getByLabelText('Incident summary')).getByText('R3: 1')).toBeInTheDocument();
    expect(within(screen.getByLabelText('Handover summary')).getByText('REVIEWED')).toBeInTheDocument();
  });

  it('a superseded refresh never falsely unlocks a locked control (WO C3C-BUILD-REREREV-F1)', async () => {
    // Refresh click 1 (A) hangs; click 2 (B) is the CURRENT attempt and
    // fails. A's later resolution is superseded and must never unlock.
    await signInWithSession();
    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's1');
    await screen.findByRole('form', { name: 'Append message' });

    const msgForm = screen.getByRole('form', { name: 'Append message' });
    fetchMock.mockRejectedValueOnce(new TypeError('Failed to fetch')); // POST /messages
    await userEvent.type(within(msgForm).getByLabelText('Message text'), 'radio check');
    await userEvent.click(within(msgForm).getByRole('button', { name: 'Send message' }));
    await within(msgForm).findByText(/could not be confirmed/);

    let resolveA!: (v: Response) => void;
    fetchMock.mockReturnValueOnce(new Promise<Response>((r) => (resolveA = r))); // A: /events hangs
    await userEvent.click(within(msgForm).getByRole('button', { name: 'Refresh' }));
    fetchMock.mockRejectedValueOnce(new TypeError('Failed to fetch')); // B: current attempt fails
    await userEvent.click(within(msgForm).getByRole('button', { name: 'Refresh' }));
    await waitFor(() => expect(within(msgForm).getByText(/could not be confirmed/)).toBeInTheDocument());

    await act(async () => { resolveA(jsonResponse(200, [])); await Promise.resolve(); }); // A resolves late, superseded by B
    expect(within(msgForm).getByText(/could not be confirmed/)).toBeInTheDocument();
    expect(within(msgForm).getByRole('button', { name: 'Send message' })).toBeDisabled();
  });

  it('switching shifts resets the operator mutation subtree: no carried-over lock, and a retained task intent is never reused (WO C3C-BUILD-REREREV-F2)', async () => {
    // s1: R2 task retains an intent_id, then hits outcome_unknown; s2 must
    // be a fresh mount - no carried lock/title/intent.
    const intent = (id: string) => jsonResponse(201, { intent_id: id, payload_digest: 'x', risk_class: 'R2', created_at: '2026-08-01T00:00:00Z' });
    await signInWithSession();
    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's1');
    let taskForm = await screen.findByRole('form', { name: 'Create task' });

    fetchMock.mockResolvedValueOnce(intent('s1-intent'));
    fetchMock.mockRejectedValueOnce(new TypeError('Failed to fetch'));
    await userEvent.type(within(taskForm).getByLabelText('Title'), 'S1 task');
    await userEvent.selectOptions(within(taskForm).getByLabelText('Risk class'), 'R2');
    await userEvent.click(within(taskForm).getByRole('button', { name: 'Create task' }));
    await screen.findByText(/could not be confirmed/);
    expect(within(taskForm).getByRole('button', { name: 'Create task' })).toBeDisabled();

    mockReads(fetchMock);
    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's2');
    taskForm = await screen.findByRole('form', { name: 'Create task' });

    expect(screen.queryByText(/could not be confirmed/)).not.toBeInTheDocument();
    expect(within(taskForm).getByLabelText('Title')).toHaveValue('');
    expect(within(taskForm).getByRole('button', { name: 'Create task' })).toBeDisabled(); // empty title, not locked

    fetchMock.mockResolvedValueOnce(intent('s2-intent')); // fresh intent for s2, never reuses s1's
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { task_id: 't-s2', title: 'S2 task', status: 'OPEN' }));
    await userEvent.type(within(taskForm).getByLabelText('Title'), 'S2 task');
    await userEvent.selectOptions(within(taskForm).getByLabelText('Risk class'), 'R2');
    await userEvent.click(within(taskForm).getByRole('button', { name: 'Create task' }));

    // s2 must obtain a FRESH intent (second creation-intents POST, task POST
    // carries s2-intent) - proving s1's retained intent state did not leak.
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/tasks'),
      expect.objectContaining({ body: expect.stringContaining('"intent_id":"s2-intent"') })
    ));
    const intentCalls = fetchMock.mock.calls.filter((c) => String(c[0]).includes('creation-intents'));
    expect(intentCalls).toHaveLength(2); // one for s1, one fresh for s2

    // Operator mutation controls render on s2 too; zero supervisor controls.
    expect(screen.getByRole('form', { name: 'Create event' })).toBeInTheDocument();
    for (const t of ['Confirm event', 'Freeze shift', 'Acknowledge incident']) expect(screen.queryByRole('button', { name: t })).not.toBeInTheDocument();
  });
});
