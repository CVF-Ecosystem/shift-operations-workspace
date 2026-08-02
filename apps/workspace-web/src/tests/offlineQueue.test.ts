import { beforeEach, describe, expect, it, vi } from 'vitest';
import { discardItem, enqueueTransition, queueItems, resetQueueForTests } from '../offline/queue';
import { readStored, storageKey } from '../offline/storage';
import { parseCommand } from '../offline/types';
import { setPrincipalUserId } from '../features/authentication/session';

const ID = '123e4567-e89b-42d3-a456-426614174000';

describe('strict actor-bound offline queue', () => {
  beforeEach(() => { localStorage.clear(); sessionStorage.clear(); resetQueueForTests(); setPrincipalUserId('actor/one'); vi.useRealTimers(); });

  it('persists only the exact schema and encoded actor namespace', () => {
    expect(() => enqueueTransition('task.transition', ID, 'IN_PROGRESS', 2)).toThrow();
    expect(storageKey('actor/one')).toContain('actor%2Fone');
    expect(queueItems()[0]).toMatchObject({ schemaVersion: 1, actorUserId: 'actor/one', state: 'pending', lastErrorKind: null });
  });

  it('rejects unknown keys, actor mismatch, invalid targets and state/error mismatch', () => {
    const base = { schemaVersion: 1, clientOperationId: ID, actorUserId: 'actor/one', commandType: 'incident.transition', recordId: ID, targetStatus: 'MITIGATING', expectedVersion: 1, createdAt: new Date().toISOString(), state: 'pending', lastErrorKind: null };
    expect(parseCommand(base, 'actor/one')).not.toBeNull();
    expect(parseCommand({ ...base, secret: 'x' }, 'actor/one')).toBeNull();
    expect(parseCommand(base, 'actor-two')).toBeNull();
    expect(parseCommand({ ...base, targetStatus: 'ACKNOWLEDGED' }, 'actor/one')).toBeNull();
    expect(parseCommand({ ...base, state: 'blocked', lastErrorKind: null }, 'actor/one')).toBeNull();
  });

  it('quarantines malformed/expired data without exposing raw JSON and discards it explicitly', () => {
    localStorage.setItem(storageKey('actor/one'), JSON.stringify([{ bearer: 'do-not-render' }]));
    expect(readStored('actor/one')).toEqual([{ clientOperationId: 'invalid-0', state: 'blocked', lastErrorKind: 'storage', reason: 'Invalid or expired offline item' }]);
    expect(JSON.stringify(readStored('actor/one'))).not.toContain('do-not-render');
    discardItem('invalid-0');
    expect(queueItems()).toEqual([]);
  });

  it('halts behind quarantine and discards exactly one raw item without bulk clearing', () => {
    expect(() => enqueueTransition('task.transition', ID, 'IN_PROGRESS', 2)).toThrow();
    const valid = JSON.parse(localStorage.getItem(storageKey('actor/one')) ?? '[]')[0];
    localStorage.setItem(storageKey('actor/one'), JSON.stringify([{ secret: 'first' }, valid, { secret: 'last' }]));
    expect(queueItems().map((item) => item.clientOperationId)).toEqual(['invalid-0', valid.clientOperationId, 'invalid-2']);
    discardItem('invalid-0');
    expect(queueItems().map((item) => item.clientOperationId)).toEqual([valid.clientOperationId, 'invalid-1']);
    const raw = localStorage.getItem(storageKey('actor/one')) ?? '';
    expect(raw).toContain('last');
    expect(raw).not.toContain('first');
  });

  it('refuses enqueue while quarantined data exists instead of rewriting it away', () => {
    localStorage.setItem(storageKey('actor/one'), JSON.stringify([{ secret: 'preserve-me' }]));
    expect(() => enqueueTransition('task.transition', ID, 'IN_PROGRESS', 2)).toThrow('quarantined');
    expect(localStorage.getItem(storageKey('actor/one'))).toContain('preserve-me');
  });
});
