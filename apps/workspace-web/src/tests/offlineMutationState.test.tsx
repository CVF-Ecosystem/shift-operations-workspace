import { beforeEach, describe, expect, it } from 'vitest';
import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { OfflineQueuePanel } from '../offline/OfflineQueuePanel';
import { ConnectivityRuntime } from '../offline/ConnectivityRuntime';
import { enqueueTransition, queueItems, resetQueueForTests, updateItem } from '../offline/queue';
import { setPrincipalUserId, setToken } from '../features/authentication/session';
import { registerRefreshOwner } from '../offline/refreshBridge';
import { resetRefreshCoordinatorForTests } from '../offline/refreshCoordinator';

const ID = '123e4567-e89b-42d3-a456-426614174000';

describe('offline queue disclosure and controls', () => {
  beforeEach(() => {
    localStorage.clear(); sessionStorage.clear(); resetQueueForTests(); resetRefreshCoordinatorForTests();
    setPrincipalUserId('actor');
    vi.spyOn(window.navigator, 'onLine', 'get').mockReturnValue(true);
    Object.defineProperty(document, 'visibilityState', { configurable: true, value: 'visible' });
  });

  it('renders bounded metadata and requires confirmation before discard', async () => {
    expect(() => enqueueTransition('customer_request.transition', ID, 'ACKNOWLEDGED', 1)).toThrow();
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(true);
    render(<OfflineQueuePanel />);
    expect(screen.getByRole('listitem')).toHaveTextContent('customer_request.transition · …14174000 → ACKNOWLEDGED');
    expect(document.body.innerHTML).not.toContain('actor');
    await userEvent.click(screen.getByRole('button', { name: 'Discard' }));
    expect(confirm).toHaveBeenCalled();
    expect(screen.queryByRole('heading', { name: 'Offline actions' })).not.toBeInTheDocument();
  });

  it('updates accessible queue counts when state changes without changing queue length', async () => {
    setToken('test-token');
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({
      user_id: 'actor', role: 'operator', expires_at: '2026-08-03T00:00:00Z'
    }), { status: 200, headers: { 'Content-Type': 'application/json' } })));
    render(<ConnectivityRuntime onSignedOut={vi.fn()}><div>console</div></ConnectivityRuntime>);
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('connected'));
    act(() => { expect(() => enqueueTransition('task.transition', ID, 'IN_PROGRESS', 1)).toThrow(); });
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('1 pending'));
    const id = queueItems()[0].clientOperationId;
    act(() => updateItem(id, (item) => ({ ...item, state: 'blocked', lastErrorKind: 'conflict' })));
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('1 blocked'));
    expect(screen.getByRole('status')).not.toHaveTextContent('1 pending');
  });

  it('stops the current polling callback after replay 401 before any composite refresh', async () => {
    setToken('test-token');
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ user_id: 'actor', role: 'operator', expires_at: '2026-08-03T00:00:00Z' }), { status: 200, headers: { 'Content-Type': 'application/json' } }))
      .mockResolvedValueOnce(new Response('{"detail":"expired"}', { status: 401, headers: { 'Content-Type': 'application/json' } }));
    vi.stubGlobal('fetch', fetchMock);
    const refresh = vi.fn().mockResolvedValue(undefined);
    const unregister = registerRefreshOwner(refresh);
    const signedOut = vi.fn();
    render(<ConnectivityRuntime onSignedOut={signedOut}><div>console</div></ConnectivityRuntime>);
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('connected'));
    act(() => { expect(() => enqueueTransition('task.transition', ID, 'IN_PROGRESS', 1)).toThrow(); });
    act(() => window.dispatchEvent(new Event('online')));
    await waitFor(() => expect(signedOut).toHaveBeenCalledTimes(1));
    expect(refresh).not.toHaveBeenCalled();
    expect(fetchMock).toHaveBeenCalledTimes(2);
    setPrincipalUserId('actor');
    expect(queueItems()[0]).toMatchObject({ state: 'blocked', lastErrorKind: 'unauthorized' });
    unregister();
  });
});
