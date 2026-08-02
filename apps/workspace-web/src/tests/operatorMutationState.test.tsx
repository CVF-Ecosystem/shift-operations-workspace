// WO C3C-BUILD-REREV-F1: proves the real Promise-returning refresh contract
// - unresolved refresh never unlocks, rejected refresh stays locked, a
// conflict auto-starts exactly one refresh, and outcome_unknown never
// auto-refreshes. Also covers one-in-flight, fixed sanitized messages and
// aria-describedby/focus association (WO C3C-BUILD-REV-F3).
import { describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useMutationControl } from '../features/operator-actions/useMutationControl';
import { MutationFeedback } from '../features/operator-actions/MutationFeedback';
import { ApiError } from '../services/api';
import { OfflineQueuedError } from '../offline/queue';

function TestComponent({ action, refresh }: { action: () => Promise<void>; refresh: () => Promise<void> }) {
  const { state, submit, feedbackId, refreshAndUnlock, isLockedOut } = useMutationControl(action, refresh);
  return (
    <div>
      <input aria-describedby={feedbackId} />
      <button
        type="button"
        onClick={() => void submit()}
        aria-describedby={feedbackId}
        disabled={state.status === 'submitting' || isLockedOut}
      >
        {state.status === 'submitting' ? 'Submitting…' : 'Submit'}
      </button>
      <MutationFeedback id={feedbackId} state={state} onRefreshAndUnlock={() => void refreshAndUnlock()} />
    </div>
  );
}

describe('operator mutation state and feedback', () => {
  it('renders a bounded queued result without invoking the confirming refresh', async () => {
    const action = () => Promise.reject(new OfflineQueuedError('123e4567-e89b-42d3-a456-426614174000'));
    const refresh = vi.fn();
    render(<TestComponent action={action} refresh={refresh} />);
    await userEvent.click(screen.getByRole('button', { name: 'Submit' }));
    expect(await screen.findByRole('status')).toHaveTextContent('Queued on this device');
    expect(refresh).not.toHaveBeenCalled();
  });
  it('disables submit button while submission is in-flight (one in-flight per control)', async () => {
    let resolveAction!: () => void;
    const action = () => new Promise<void>((r) => (resolveAction = r));
    const refresh = vi.fn().mockResolvedValue(undefined);
    render(<TestComponent action={action} refresh={refresh} />);

    const btn = screen.getByRole('button', { name: 'Submit' });
    await userEvent.click(btn);
    await userEvent.click(btn); // second click while in-flight must be a no-op

    expect(screen.getByRole('button', { name: 'Submitting…' })).toBeDisabled();
    resolveAction();
    await waitFor(() => expect(screen.getByRole('button')).not.toBeDisabled());
  });

  it('success awaits the real refresh before resolving to idle - an unresolved refresh never unlocks', async () => {
    const action = () => Promise.resolve();
    let resolveRefresh!: () => void;
    const refresh = vi.fn(() => new Promise<void>((r) => (resolveRefresh = r)));
    render(<TestComponent action={action} refresh={refresh} />);

    const btn = screen.getByRole('button', { name: 'Submit' });
    await userEvent.click(btn);

    // Mutation itself resolved, but refresh is still pending - submit must
    // still read as busy/disabled, not silently flip back to idle early.
    expect(refresh).toHaveBeenCalledTimes(1);
    expect(screen.getByRole('button', { name: 'Submitting…' })).toBeDisabled();

    resolveRefresh();
    await waitFor(() => expect(screen.getByRole('button', { name: 'Submit' })).not.toBeDisabled());
  });

  it('locks a saved-but-unconfirmed mutation until a manual fresh read succeeds, without retrying the mutation', async () => {
    const action = vi.fn().mockResolvedValue(undefined);
    const refresh = vi.fn()
      .mockRejectedValueOnce(new Error('confirming refresh failed'))
      .mockRejectedValueOnce(new Error('manual refresh failed'))
      .mockResolvedValueOnce(undefined);
    render(<TestComponent action={action} refresh={refresh} />);

    await userEvent.click(screen.getByRole('button', { name: 'Submit' }));
    expect(await screen.findByRole('status')).toHaveTextContent('Saved. The view could not be confirmed as current.');
    expect(screen.getByRole('button', { name: 'Submit' })).toBeDisabled();
    await userEvent.click(screen.getByRole('button', { name: 'Refresh' }));
    expect(screen.getByRole('button', { name: 'Submit' })).toBeDisabled();
    await userEvent.click(screen.getByRole('button', { name: 'Refresh' }));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Submit' })).not.toBeDisabled());
    expect(action).toHaveBeenCalledTimes(1);
    expect(refresh).toHaveBeenCalledTimes(3);
  });

  it('locks on outcome_unknown and only unlocks after an explicit refresh succeeds - never auto-refreshes', async () => {
    const action = () => Promise.reject(new ApiError('outcome_unknown', 'boom'));
    const refresh = vi.fn().mockResolvedValue(undefined);
    render(<TestComponent action={action} refresh={refresh} />);

    await userEvent.click(screen.getByRole('button', { name: 'Submit' }));
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('The outcome of this request could not be confirmed. Refresh before trying again.');
    expect(screen.getByRole('button', { name: 'Submit' })).toBeDisabled();
    expect(document.activeElement).toBe(alert);
    // outcome_unknown must never auto-refresh on its own.
    expect(refresh).not.toHaveBeenCalled();

    await userEvent.click(screen.getByRole('button', { name: 'Refresh' }));
    expect(refresh).toHaveBeenCalledTimes(1);
    await waitFor(() => expect(screen.getByRole('button', { name: 'Submit' })).not.toBeDisabled());
  });

  it('a rejected explicit refresh after outcome_unknown leaves the control locked, offering another manual refresh', async () => {
    const action = () => Promise.reject(new ApiError('outcome_unknown', 'boom'));
    const refresh = vi.fn().mockRejectedValue(new Error('refresh also failed'));
    render(<TestComponent action={action} refresh={refresh} />);

    await userEvent.click(screen.getByRole('button', { name: 'Submit' }));
    await screen.findByRole('alert');
    await userEvent.click(screen.getByRole('button', { name: 'Refresh' }));

    expect(refresh).toHaveBeenCalledTimes(1);
    expect(screen.getByRole('button', { name: 'Submit' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Refresh' })).toBeInTheDocument();
  });

  it('a conflict automatically starts exactly one refresh; success unlocks for retry but keeps the conflict visible', async () => {
    const action = () => Promise.reject(new ApiError('conflict', 'raw backend detail must never render'));
    let resolveRefresh!: () => void;
    const refresh = vi.fn(() => new Promise<void>((r) => (resolveRefresh = r)));
    render(<TestComponent action={action} refresh={refresh} />);

    await userEvent.click(screen.getByRole('button', { name: 'Submit' }));
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('This record changed elsewhere.');
    expect(alert).not.toHaveTextContent('raw backend detail');
    // The control locks immediately and the hook itself starts the refresh -
    // no manual click required - and stays locked while it is in flight.
    expect(screen.getByRole('button', { name: 'Submit' })).toBeDisabled();
    expect(refresh).toHaveBeenCalledTimes(1);

    resolveRefresh();
    await waitFor(() => expect(screen.getByRole('button', { name: 'Submit' })).not.toBeDisabled());
    expect(refresh).toHaveBeenCalledTimes(1);
    // Conflict feedback stays visible (fresh values to review) even though unlocked.
    expect(screen.getByRole('alert')).toHaveTextContent('This record changed elsewhere.');
  });

  it('a conflict whose automatic refresh fails remains locked and offers an explicit manual retry', async () => {
    const action = () => Promise.reject(new ApiError('conflict', 'x'));
    const refresh = vi.fn().mockRejectedValue(new Error('refresh failed'));
    render(<TestComponent action={action} refresh={refresh} />);

    await userEvent.click(screen.getByRole('button', { name: 'Submit' }));
    await screen.findByRole('alert');

    await waitFor(() => expect(refresh).toHaveBeenCalledTimes(1));
    expect(screen.getByRole('button', { name: 'Submit' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Refresh and try again' })).toBeInTheDocument();
  });

  it('renders a fixed sanitized message for forbidden and never the raw kind text, associated via aria-describedby', async () => {
    const action = () => Promise.reject(new ApiError('forbidden', 'raw detail'));
    const refresh = vi.fn().mockResolvedValue(undefined);
    render(<TestComponent action={action} refresh={refresh} />);

    const btn = screen.getByRole('button', { name: 'Submit' });
    await userEvent.click(btn);

    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Action not permitted. Check your role or approval prerequisites.');
    expect(btn.getAttribute('aria-describedby')).toBe(alert.id);
    expect(document.activeElement).toBe(alert);
    expect(refresh).not.toHaveBeenCalled();
  });
});
