import oracle from '../../../../tests/fixtures/p5a2_source_api_oracle.json';
import mutations from '../../../../tests/fixtures/p5a2_source_ui_mutations.json';
import type { SourceWindow } from '../types/proactiveSource';

export const ACTOR = 'PUBLIC_ACTOR';
export const positives = oracle.cases.map((item) => ({
  name: item.case,
  receipt: item.expected_receipt,
  window: {
    query_start: item.expected_receipt.query_start,
    query_end: item.expected_receipt.query_end,
    run_as_of: item.expected_receipt.run_as_of
  } as SourceWindow
}));

export const refusalSamples = mutations.refusedSamples;
export const mutationCases = mutations.mutations;

export function mutatedReceipt(mutation: typeof mutationCases[number]): Record<string, unknown> {
  const base = mutation.shapeId === 'P5A2_SOURCE_READY' ? positives[0].receipt : mutations.refusedSample;
  const copy: Record<string, unknown> = { ...base };
  for (const key of mutation.delete) delete copy[key];
  return { ...copy, ...mutation.set };
}

export function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}
