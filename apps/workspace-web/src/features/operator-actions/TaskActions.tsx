// P2C-MUTATION-FULL-UI-C3C (WO C3C-BUILD-REV-F4/REREV-F1/F3): Task actions.
// Payload digest is NEVER rendered/stored. Targets derive from the backend
// lifecycle table. useMutationControl owns post-success/conflict refresh.
import { useCallback, useState } from 'react';
import { operatorApi } from '../../services/operatorApi';
import { ApiError } from '../../services/api';
import { useMutationControl } from './useMutationControl';
import { MutationFeedback } from './MutationFeedback';
import { TASK_LIFECYCLE } from './types';
import type { RiskClass, Task, TaskStatus } from '../../types/operations';

const RISK_CLASSES: RiskClass[] = ['R0', 'R1', 'R2', 'R3'];

interface TaskActionsProps {
  shiftId: string;
  tasks: Task[];
  onRefresh: () => Promise<void>;
}

export function TaskActions({ shiftId, tasks, onRefresh }: TaskActionsProps) {
  const [title, setTitle] = useState('');
  const [riskClass, setRiskClass] = useState<RiskClass>('R1');
  const [description, setDescription] = useState('');
  const [intentId, setIntentId] = useState<string | null>(null);
  const [approvalNeeded, setApprovalNeeded] = useState(false);

  const doCreate = useCallback(async () => {
    const needsApproval = riskClass !== 'R0' && riskClass !== 'R1';
    let resolvedIntentId = intentId;
    setApprovalNeeded(false);

    if (needsApproval && !resolvedIntentId) {
      const intent = await operatorApi.createTaskIntent(shiftId, title.trim(), riskClass, description.trim() || undefined);
      resolvedIntentId = intent.intent_id;
      setIntentId(resolvedIntentId);
    }

    try {
      await operatorApi.createTask(shiftId, title.trim(), riskClass, resolvedIntentId ?? undefined, description.trim() || undefined);
      setTitle('');
      setDescription('');
      setRiskClass('R1');
      setIntentId(null);
    } catch (cause) {
      // Unsatisfied approval quorum for the intent is a real 409 (approval
      // gate), not 403 - the intent itself was created. Bounded safe outcome.
      if (needsApproval && cause instanceof ApiError && cause.kind === 'conflict') {
        setApprovalNeeded(true);
      }
      throw cause;
    }
  }, [shiftId, title, riskClass, description, intentId]);

  const createControl = useMutationControl(doCreate, onRefresh);
  const createDisabled = createControl.isSubmitting || createControl.isLockedOut;

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    await createControl.submit();
  };

  return (
    <div className="action-group">
      <form aria-label="Create task" className="action-form" onSubmit={handleCreateSubmit}>
        <h3 className="form-legend">Create Task</h3>
        <label htmlFor="task-title" className="form-label">Title</label>
        <input
          id="task-title"
          type="text"
          value={title}
          onChange={(e) => { setTitle(e.target.value); createControl.reset(); setIntentId(null); setApprovalNeeded(false); }}
          required
          disabled={createDisabled}
          maxLength={200}
          aria-describedby={createControl.feedbackId}
          className="form-input"
        />
        <label htmlFor="task-risk" className="form-label">Risk class</label>
        <select
          id="task-risk"
          value={riskClass}
          onChange={(e) => { setRiskClass(e.target.value as RiskClass); createControl.reset(); setIntentId(null); setApprovalNeeded(false); }}
          disabled={createDisabled}
          className="form-input"
        >
          {RISK_CLASSES.map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
        <label htmlFor="task-desc" className="form-label">Description (optional)</label>
        <textarea
          id="task-desc"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={createDisabled}
          rows={2}
          maxLength={1000}
          className="form-input form-input--textarea"
        />
        {approvalNeeded && (
          <p id={createControl.feedbackId} role="status" tabIndex={-1} className="approval-notice" aria-live="polite">
            This task requires supervisor approval. A supervisor must approve before creation can proceed.{' '}
            {createControl.isLockedOut && (
              <button type="button" onClick={() => void createControl.refreshAndUnlock()} className="mutation-feedback__refresh-btn">
                Refresh
              </button>
            )}
          </p>
        )}
        <button
          type="submit"
          disabled={createDisabled || !title.trim()}
          aria-busy={createControl.isSubmitting}
          className="form-btn form-btn--primary"
        >
          {createControl.isSubmitting ? 'Creating…' : 'Create task'}
        </button>
        {!approvalNeeded && (
          <MutationFeedback
            id={createControl.feedbackId}
            state={createControl.state}
            onRefreshAndUnlock={() => void createControl.refreshAndUnlock()}
          />
        )}
      </form>

      {tasks.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <h3 className="form-legend">Task Transitions</h3>
          <ul className="task-list" aria-label="Task list">
            {tasks.map((t) => (
              <TaskItem key={t.task_id} task={t} onRefresh={onRefresh} />
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function TaskItem({ task, onRefresh }: { task: Task; onRefresh: () => Promise<void> }) {
  const legalTargets = TASK_LIFECYCLE[task.status];
  const [targetStatus, setTargetStatus] = useState<TaskStatus | ''>(legalTargets[0] ?? '');

  const doTransition = useCallback(async () => {
    if (!targetStatus) return;
    await operatorApi.transitionTask(task.task_id, targetStatus, task.version);
  }, [task.task_id, task.version, targetStatus]);

  const control = useMutationControl(doTransition, onRefresh);
  const disabled = control.isSubmitting || control.isLockedOut;

  if (legalTargets.length === 0) {
    return (
      <li className="task-list__item">
        <span className="task-list__title">{task.title}</span>
        <span className="task-list__status status-badge">{task.status}</span>
      </li>
    );
  }

  return (
    <li className="task-list__item">
      <span className="task-list__title">{task.title}</span>
      <span className="task-list__status status-badge">{task.status}</span>
      <form
        aria-label={`Transition task ${task.title}`}
        className="action-form action-form--inline"
        onSubmit={async (e) => { e.preventDefault(); await control.submit(); }}
      >
        <select
          aria-label={`Target status for ${task.title}`}
          value={targetStatus}
          onChange={(e) => { setTargetStatus(e.target.value as TaskStatus); control.reset(); }}
          disabled={disabled}
          aria-describedby={control.feedbackId}
          className="form-input form-input--inline"
        >
          {legalTargets.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <button
          type="submit"
          disabled={disabled}
          aria-busy={control.isSubmitting}
          className="form-btn form-btn--small"
        >
          {control.isSubmitting ? 'Saving…' : 'Update'}
        </button>
        <MutationFeedback
          id={control.feedbackId}
          state={control.state}
          onRefreshAndUnlock={() => void control.refreshAndUnlock()}
        />
      </form>
    </li>
  );
}
