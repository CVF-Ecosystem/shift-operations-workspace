import { useCallback, useEffect, useRef, useState } from 'react';
import { ApiError } from '../../services/api';
import { readProactiveSource } from '../../services/proactiveSourceApi';
import { getPrincipalUserId, getToken, subscribeSessionChange } from '../authentication/session';
import { projectSourceReceipt } from './sourceReceipt';
import type { SourceView, SourceWindow } from '../../types/proactiveSource';

export type ReadState = 'idle' | 'loading' | 'auth' | 'forbidden' | 'network' | 'invalid' | 'unavailable' | 'ready';
type Inputs = { start: string; end: string; asOf: string };
const EMPTY: Inputs = { start: '', end: '', asOf: '' };

/** datetime-local has no zone; these exact calendar components are UTC. */
export function utcInput(value: string): string | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?$/.exec(value);
  if (!match) return null;
  const [, y, m, d, h, min, sec = '00'] = match;
  if (+y === 0) return null;
  const date = new Date(0);
  date.setUTCFullYear(+y, +m - 1, +d);
  date.setUTCHours(+h, +min, +sec, 0);
  if (!Number.isFinite(date.getTime()) || date.getUTCFullYear() !== +y || date.getUTCMonth() + 1 !== +m ||
      date.getUTCDate() !== +d || date.getUTCHours() !== +h || date.getUTCMinutes() !== +min ||
      date.getUTCSeconds() !== +sec) return null;
  return date.toISOString().replace('.000Z', 'Z');
}

export function sourceWindow(inputs: Inputs): SourceWindow | null {
  const query_start = utcInput(inputs.start);
  const query_end = utcInput(inputs.end);
  const run_as_of = utcInput(inputs.asOf);
  if (!query_start || !query_end || !run_as_of ||
      !(query_start < query_end && query_end <= run_as_of)) return null;
  return { query_start, query_end, run_as_of };
}

export function useProactiveSourceRead() {
  const [inputs, setInputs] = useState<Inputs>(EMPTY);
  const [state, setState] = useState<ReadState>('idle');
  const [view, setView] = useState<SourceView | null>(null);
  const controller = useRef<AbortController | null>(null);
  const nonce = useRef(0);
  const mounted = useRef(true);

  const invalidate = useCallback(() => {
    nonce.current += 1;
    controller.current?.abort();
    controller.current = null;
    if (mounted.current) { setView(null); setState('idle'); }
  }, []);

  useEffect(() => {
    mounted.current = true;
    const unsubscribe = subscribeSessionChange(() => {
      invalidate();
      setInputs(EMPTY);
    });
    return () => {
      mounted.current = false;
      nonce.current += 1;
      controller.current?.abort();
      unsubscribe();
    };
  }, [invalidate]);

  const change = useCallback((field: keyof Inputs, value: string) => {
    invalidate();
    setInputs((current) => ({ ...current, [field]: value }));
  }, [invalidate]);

  const submit = useCallback(async () => {
    invalidate();
    const window = sourceWindow(inputs);
    if (!window) { setState('invalid'); return; }
    const token = getToken();
    const principal = getPrincipalUserId();
    if (!token || !principal) { setState('auth'); return; }
    const request = new AbortController();
    controller.current = request;
    const current = nonce.current;
    setState('loading');
    const fresh = () => mounted.current && nonce.current === current && !request.signal.aborted &&
      getToken() === token && getPrincipalUserId() === principal;
    try {
      const raw = await readProactiveSource(window, token, principal, request.signal);
      if (!fresh()) return;
      const projected = await projectSourceReceipt(raw, principal, window);
      if (!fresh()) return;
      if (projected) { setView(projected); setState('ready'); }
      else setState('unavailable');
    } catch (cause) {
      if (!fresh()) return;
      const kind = cause instanceof ApiError ? cause.kind : 'server';
      setState(kind === 'unauthorized' ? 'auth' : kind === 'forbidden' ? 'forbidden' :
        kind === 'network' ? 'network' : kind === 'invalid' ? 'invalid' : 'unavailable');
    } finally {
      if (controller.current === request) controller.current = null;
    }
  }, [inputs, invalidate]);

  return { inputs, state, view, change, submit };
}
