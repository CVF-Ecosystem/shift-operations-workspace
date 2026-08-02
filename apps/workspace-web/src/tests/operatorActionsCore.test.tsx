import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ShiftActions } from '../features/operator-actions/ShiftActions';
import { MessageEventActions } from '../features/operator-actions/MessageEventActions';
import { TaskActions } from '../features/operator-actions/TaskActions';
import { setToken } from '../features/authentication/session';
import type { Task } from '../types/operations';

const jsonResponse = (status: number, body: unknown): Response =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

describe('operator core actions components', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    sessionStorage.clear();
    setToken('test-token');
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => vi.unstubAllGlobals());

  it('ShiftActions renders form and submits create shift to API', async () => {
    const onShiftCreated = vi.fn();
    const onRefresh = vi.fn();
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { shift_id: 's-new', name: 'Alpha', starts_at: '2026-08-01T08:00', ends_at: '2026-08-01T16:00', status: 'OPEN', version: 1 }));

    render(<ShiftActions selectedShift={null} onShiftCreated={onShiftCreated} onRefresh={onRefresh} />);

    await userEvent.type(screen.getByLabelText('Shift name'), 'Alpha');
    await userEvent.type(screen.getByLabelText('Starts at'), '2026-08-01T08:00');
    await userEvent.type(screen.getByLabelText('Ends at'), '2026-08-01T16:00');
    await userEvent.click(screen.getByRole('button', { name: 'Create shift' }));

    await waitFor(() => expect(onShiftCreated).toHaveBeenCalledWith(expect.objectContaining({ shift_id: 's-new' })));
  });

  it('MessageEventActions sends message without passing sender or source from caller', async () => {
    const onRefresh = vi.fn();
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { message_id: 'm-1' }));

    render(<MessageEventActions shiftId="s-1" messages={[]} onRefresh={onRefresh} />);

    await userEvent.type(screen.getByLabelText('Message text'), 'Radio check');
    await userEvent.click(screen.getByRole('button', { name: 'Send message' }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/messages'),
      expect.objectContaining({
        body: JSON.stringify({ shift_id: 's-1', text: 'Radio check' })
      })
    ));
    expect(onRefresh).toHaveBeenCalled();
  });

  it('TaskActions creates R2 task via intent first without rendering payload digest', async () => {
    const onRefresh = vi.fn();
    fetchMock
      .mockResolvedValueOnce(jsonResponse(201, { intent_id: 'intent-999', payload_digest: 'SECRET_DIGEST_HASH_DO_NOT_SHOW', risk_class: 'R2', created_at: '2026-08-01T00:00:00Z' }))
      .mockResolvedValueOnce(jsonResponse(200, { task_id: 't-1', title: 'High risk task', status: 'OPEN' }));

    render(<TaskActions shiftId="s-1" tasks={[]} onRefresh={onRefresh} />);

    await userEvent.type(screen.getByLabelText('Title'), 'High risk task');
    await userEvent.selectOptions(screen.getByLabelText('Risk class'), 'R2');
    await userEvent.click(screen.getByRole('button', { name: 'Create task' }));

    await waitFor(() => expect(onRefresh).toHaveBeenCalled());
    expect(document.body.innerHTML).not.toContain('SECRET_DIGEST_HASH_DO_NOT_SHOW');
  });

  it('TaskActions offers only the backend-legal target states for a DONE (terminal) task: none (WO C3C-BUILD-REV-F4)', async () => {
    const doneTask: Task = {
      task_id: 't-done', shift_id: 's-1', title: 'Finished task', description: null, status: 'DONE',
      owner_id: null, due_at: null, risk_class: 'R1', state: 'CONFIRMED', evidence: [], version: 1, created_at: '2026-08-01T00:00:00Z'
    };
    render(<TaskActions shiftId="s-1" tasks={[doneTask]} onRefresh={vi.fn()} />);
    expect(screen.queryByLabelText('Target status for Finished task')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Update' })).not.toBeInTheDocument();
  });

  it('TaskActions offers only the backend-legal target states for an OPEN task', async () => {
    const openTask: Task = {
      task_id: 't-open', shift_id: 's-1', title: 'New task', description: null, status: 'OPEN',
      owner_id: null, due_at: null, risk_class: 'R1', state: 'CONFIRMED', evidence: [], version: 1, created_at: '2026-08-01T00:00:00Z'
    };
    render(<TaskActions shiftId="s-1" tasks={[openTask]} onRefresh={vi.fn()} />);
    const options = Array.from(screen.getByLabelText('Target status for New task').querySelectorAll('option')).map((o) => o.value);
    expect(options).toStrictEqual(['IN_PROGRESS', 'BLOCKED', 'CANCELLED', 'CARRY_OVER']);
  });
});
