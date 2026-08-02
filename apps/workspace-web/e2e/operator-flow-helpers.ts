import type { APIRequestContext, Page } from '@playwright/test';

// The harness (scripts/testing/run_c3c_web_evidence.py) sets VITE_API_URL on
// the whole subprocess environment before invoking both `vite build` and
// `playwright test`, so it is readable here directly - the built app baked
// it in at build time for the browser, and this process reads the same
// value for direct-to-API test arrangement calls (page.request/API context
// use the frontend origin by default via playwright.config.ts baseURL).
export const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';

export async function loginAsOperator(page: Page, username = 'op1', password = 'op1-devpass') {
  await page.goto('/');
  await page.fill('#username', username);
  await page.fill('#password', password);
  await page.click('button[type="submit"]');
  await page.waitForSelector('main.operations-console', { timeout: 10000 });
}

// P2C-MUTATION-FULL-UI-C3D: sup1/sup2/sup3 are the shift_supervisor seed
// users (scripts/seed_dev_users.py). Login itself is identical to operator
// login - the C3d supervisor surface is gated by the real GET
// /staffing/shifts|users 403/200 response, not a separate login path.
export async function loginAsSupervisor(page: Page, username = 'sup1', password = 'sup1-devpass') {
  await loginAsOperator(page, username, password);
  await page.waitForSelector('.supervisor-actions', { timeout: 10000 });
}

export async function createShift(page: Page, name: string, startsAt: string, endsAt: string) {
  await page.fill('#create-shift-name', name);
  await page.fill('#create-shift-starts', startsAt);
  await page.fill('#create-shift-ends', endsAt);
  await page.click('.create-shift-form button[type="submit"]');
  await page.waitForSelector('.shift-selector select', { timeout: 10000 });
  await page.selectOption('.shift-selector select', { label: `${name} · OPEN` });
}

// Real API arrangement helper (not a mock): obtains a genuine bearer token
// for the fixed dev seed users via the real POST /auth/login route.
export async function apiLogin(request: APIRequestContext, username: string, password: string): Promise<string> {
  const res = await request.post(`${API_BASE_URL}/auth/login`, { data: { username, password } });
  if (!res.ok()) throw new Error(`apiLogin failed for ${username}: ${res.status()}`);
  const body = (await res.json()) as { access_token: string };
  return body.access_token;
}

export async function arrangeReportApproval(
  request: APIRequestContext, assigningToken: string, shiftId: string, reportId: string
) {
  const sup2Token = await apiLogin(request, 'sup2', 'sup2-devpass');
  const assign = await request.post(`${API_BASE_URL}/shifts/${shiftId}/assignments`, {
    headers: { Authorization: `Bearer ${assigningToken}` }, data: { user_id: 'sup2' }
  });
  if (!assign.ok()) throw new Error(`sup2 assignment failed: ${assign.status()}`);
  const receipt = await request.post(`${API_BASE_URL}/approvals`, {
    headers: { Authorization: `Bearer ${sup2Token}` },
    data: { record_type: 'Report', record_id: reportId, action: 'report.approve' }
  });
  if (!receipt.ok()) throw new Error(`report approval receipt failed: ${receipt.status()}`);
}

// Real-API arrangement for the post-freeze correction browser path. The UI
// action under test remains correction; this helper creates only its required
// closed/frozen parent, approved Report and distinct-actor receipt.
export async function arrangeFrozenEvent(
  request: APIRequestContext, supToken: string, shiftId: string, title: string
) {
  const headers = { Authorization: `Bearer ${supToken}` };
  const eventRes = await request.post(`${API_BASE_URL}/events`, {
    headers, data: { shift_id: shiftId, event_type: 'shift_update', title, risk_class: 'R2', evidence: [{ source_type: 'message', source_id: 'frozen-event' }] }
  });
  if (!eventRes.ok()) throw new Error(`event create failed: ${eventRes.status()}`);
  const event = await eventRes.json();
  const sup2Token = await apiLogin(request, 'sup2', 'sup2-devpass');
  const sup2Headers = { Authorization: `Bearer ${sup2Token}` };
  const sourceAssignment = await request.post(`${API_BASE_URL}/shifts/${shiftId}/assignments`, {
    headers, data: { user_id: 'sup2' }
  });
  if (!sourceAssignment.ok()) throw new Error(`sup2 source assignment failed: ${sourceAssignment.status()}`);
  const confirmReceipt = await request.post(`${API_BASE_URL}/approvals`, {
    headers: sup2Headers,
    data: { record_type: 'OperationalEvent', record_id: event.event_id, action: 'event.confirm' }
  });
  if (!confirmReceipt.ok()) throw new Error(`event confirm receipt failed: ${confirmReceipt.status()}`);
  const confirmed = await request.post(`${API_BASE_URL}/events/${event.event_id}/confirm`, {
    headers, data: { expected_version: event.version }
  });
  if (!confirmed.ok()) throw new Error(`event confirm failed: ${confirmed.status()}`);
  const destinationRes = await request.post(`${API_BASE_URL}/shifts`, {
    headers,
    params: { name: `${title} destination`, starts_at: '2026-08-03T08:00:00Z', ends_at: '2026-08-03T16:00:00Z' }
  });
  if (!destinationRes.ok()) throw new Error(`destination create failed: ${destinationRes.status()}`);
  const destinationId = (await destinationRes.json()).shift_id as string;
  const destinationAssignment = await request.post(`${API_BASE_URL}/shifts/${destinationId}/assignments`, {
    headers, data: { user_id: 'sup2' }
  });
  if (!destinationAssignment.ok()) throw new Error(`sup2 destination assignment failed: ${destinationAssignment.status()}`);
  const handoverRes = await request.post(`${API_BASE_URL}/handovers`, {
    headers, data: { from_shift_id: shiftId, to_shift_id: destinationId }
  });
  if (!handoverRes.ok()) throw new Error(`handover create failed: ${handoverRes.status()}`);
  const handover = await handoverRes.json();
  const reviewed = await request.post(`${API_BASE_URL}/handovers/${handover.handover_id}/review`, {
    headers, data: { expected_version: handover.version }
  });
  if (!reviewed.ok()) throw new Error(`handover review failed: ${reviewed.status()}`);
  const acknowledged = await request.post(`${API_BASE_URL}/handovers/${handover.handover_id}/acknowledge`, {
    headers: sup2Headers, data: { expected_version: (await reviewed.json()).version }
  });
  if (!acknowledged.ok()) throw new Error(`handover acknowledge failed: ${acknowledged.status()}`);
  const close = await request.post(`${API_BASE_URL}/shifts/${shiftId}/close`, { headers, data: { expected_version: 1 } });
  if (!close.ok()) throw new Error(`shift close failed: ${close.status()}`);
  const reportRes = await request.post(`${API_BASE_URL}/reports`, { headers, data: { shift_id: shiftId } });
  if (!reportRes.ok()) throw new Error(`report generate failed: ${reportRes.status()}`);
  const report = await reportRes.json();
  const submitted = await request.post(`${API_BASE_URL}/reports/${report.report_id}/submit-review`, {
    headers, data: { expected_version: report.version, expected_status: report.status }
  });
  if (!submitted.ok()) throw new Error(`report submit failed: ${submitted.status()}`);
  const reportReceipt = await request.post(`${API_BASE_URL}/approvals`, {
    headers: sup2Headers, data: { record_type: 'Report', record_id: report.report_id, action: 'report.approve' }
  });
  if (!reportReceipt.ok()) throw new Error(`report approval receipt failed: ${reportReceipt.status()}`);
  const approved = await request.post(`${API_BASE_URL}/reports/${report.report_id}/approve`, {
    headers, data: { expected_version: report.version, expected_status: 'IN_REVIEW' }
  });
  if (!approved.ok()) throw new Error(`report approve failed: ${approved.status()}`);
  const frozen = await request.post(`${API_BASE_URL}/shifts/${shiftId}/freeze`, {
    headers, data: { expected_version: (await close.json()).version }
  });
  if (!frozen.ok()) throw new Error(`shift freeze failed: ${frozen.status()}`);
  const receipt = await request.post(`${API_BASE_URL}/approvals`, {
    headers: sup2Headers,
    data: { record_type: 'OperationalEvent', record_id: event.event_id, action: 'event.correct' }
  });
  if (!receipt.ok()) throw new Error(`event correction receipt failed: ${receipt.status()}`);
  return event;
}
