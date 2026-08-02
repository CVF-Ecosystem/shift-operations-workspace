import { ApiError } from '../services/api';
import { transitionCustomerRequestOnline, transitionIncidentOnline, transitionTaskOnline } from '../services/operatorApi';
import { getPrincipalUserId } from '../features/authentication/session';
import { markAppliedStale, queueItems, updateActorItem } from './queue';
import { refreshCurrentConsole } from './refreshBridge';
import { serializeRefresh } from './refreshCoordinator';
import type { BlockedErrorKind, OfflineCommand } from './types';

let replaying = false;

export async function recoverAndReplay(): Promise<boolean> {
  if (replaying || !navigator.onLine || document.visibilityState !== 'visible') return getPrincipalUserId() !== null;
  const actor = getPrincipalUserId();
  if (!actor) return false;
  recoverCrashItems(actor);
  replaying = true;
  try {
    while (true) {
      const first = queueItems()[0];
      if (!first || !('schemaVersion' in first) || first.state !== 'pending' || first.actorUserId !== actor) return true;
      const head = first;
      updateActorItem(actor, head.clientOperationId, (item) => ({ ...item, state: 'replaying', lastErrorKind: null }));
      try {
        await dispatch(head);
      } catch (cause) {
        fail(actor, head.clientOperationId, cause);
        return !(cause instanceof ApiError && cause.kind === 'unauthorized');
      }
      markAppliedStale(actor, head);
      try {
        await serializeRefresh(refreshCurrentConsole);
        updateActorItem(actor, head.clientOperationId, () => null);
      } catch {
        return true;
      }
    }
  } finally {
    replaying = false;
  }
}

export async function resolveAppliedStale(): Promise<void> {
  const actor = getPrincipalUserId();
  if (!actor) return;
  await serializeRefresh(refreshCurrentConsole);
  for (const item of queueItems()) {
    if ('schemaVersion' in item && item.state === 'applied_stale') updateActorItem(actor, item.clientOperationId, () => null);
  }
}

function recoverCrashItems(actor: string): void {
  for (const item of queueItems()) {
    if ('schemaVersion' in item && item.state === 'replaying') {
      updateActorItem(actor, item.clientOperationId, (current) => ({ ...current, state: 'outcome_unknown', lastErrorKind: 'outcome_unknown' }));
    }
  }
}

async function dispatch(command: OfflineCommand): Promise<void> {
  if (command.commandType === 'task.transition') {
    await transitionTaskOnline(command.recordId, command.targetStatus, command.expectedVersion);
  } else if (command.commandType === 'customer_request.transition') {
    await transitionCustomerRequestOnline(command.recordId, command.targetStatus, command.expectedVersion);
  } else {
    await transitionIncidentOnline(command.recordId, command.targetStatus, command.expectedVersion);
  }
}

function fail(actor: string, id: string, cause: unknown): void {
  if (cause instanceof ApiError && cause.kind === 'outcome_unknown') {
    updateActorItem(actor, id, (item) => ({ ...item, state: 'outcome_unknown', lastErrorKind: 'outcome_unknown' }));
    return;
  }
  const kind: BlockedErrorKind = cause instanceof ApiError && isBlocked(cause.kind) ? cause.kind : 'server';
  updateActorItem(actor, id, (item) => ({ ...item, state: 'blocked', lastErrorKind: kind }));
}

function isBlocked(kind: string): kind is BlockedErrorKind {
  return ['conflict', 'forbidden', 'not_found', 'invalid', 'unauthorized', 'server'].includes(kind);
}

export function resetReplayForTests(): void { replaying = false; }
