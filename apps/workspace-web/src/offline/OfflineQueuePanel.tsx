import { useEffect, useState } from 'react';
import { discardItem, queueItems, subscribeQueue } from './queue';
import { resolveAppliedStale } from './sync';

export function OfflineQueuePanel() {
  const [, redraw] = useState(0);
  useEffect(() => subscribeQueue(() => redraw((value) => value + 1)), []);
  const items = queueItems();
  if (!items.length) return null;
  return (
    <section className="offline-queue" aria-labelledby="offline-queue-title">
      <h2 id="offline-queue-title">Offline actions</h2>
      <p>Only recorded transitions are staged. Backend permission and version checks still apply on reconnect.</p>
      <ol>
        {items.map((item) => (
          <li key={item.clientOperationId}>
            {'commandType' in item ? (
              <><strong>{item.commandType}</strong> · …{item.recordId.slice(-8)} → {item.targetStatus} · {age(item.createdAt)} · {displayState(item.state)}</>
            ) : <><strong>Invalid offline item</strong> · {item.reason}</>}
            {'state' in item && item.state === 'applied_stale' && (
              <button type="button" onClick={() => void resolveAppliedStale()}>Refresh view</button>
            )}
            <button type="button" onClick={() => { if (confirm('Discard this offline action?')) discardItem(item.clientOperationId); }}>Discard</button>
          </li>
        ))}
      </ol>
    </section>
  );
}

function age(createdAt: string): string {
  const minutes = Math.max(0, Math.floor((Date.now() - Date.parse(createdAt)) / 60_000));
  return minutes < 1 ? 'just now' : `${minutes}m old`;
}

function displayState(state: string): string {
  return state === 'applied_stale' ? 'known applied; view stale' : state.replace('_', ' ');
}
