// P2C-MUTATION-FULL-UI-C3D (SPEC R2-R6/R9): exercises every supervisor
// control against the real FastAPI backend on disposable SQLite. Each
// `request` call arranges state only where the UI itself has no discovery
// path (e.g. a second operator-owned shift, a handover pair); every
// supervisor ACTION under test is driven through the real rendered UI.
import { expect, test } from '@playwright/test';
import { apiLogin, API_BASE_URL, arrangeReportApproval, createShift, loginAsOperator, loginAsSupervisor } from './operator-flow-helpers';

test.describe('Supervisor UI Workflow (R2-R6 closeout verticals)', () => {
  test('assigns and revokes staffing, and self-revoke clears the stale operational subtree', async ({ page }) => {
    await loginAsSupervisor(page);
    await createShift(page, 'Staffing Shift', '2026-08-02T08:00', '2026-08-02T16:00');
    const shiftId = await page.locator('.shift-selector select').inputValue();

    await page.selectOption('#staffing-shift', { label: `Staffing Shift (OPEN)` });
    await page.selectOption('#staffing-user', { label: 'sup1 (shift_supervisor)' });
    await page.click('form[aria-label="Assign user"] button[type="submit"]');
    const assignment = page.getByRole('list', { name: 'Assignment history' }).getByRole('listitem').filter({ hasText: 'sup1' });
    await expect(assignment).toContainText('ACTIVE');
    // Self-revoke clears the selected operational subtree (C3D-WO-REV-F4).
    await assignment.getByRole('button', { name: 'Revoke' }).click();
    await expect(page.locator('.shift-selector select')).toHaveValue('');
    await expect(page.locator('.shift-selector select option', { hasText: 'Staffing Shift' })).toHaveCount(0);
    expect(shiftId).toBeTruthy();
  });

  test('confirms an unconfirmed event using the complete event collection, not only the confirmed timeline', async ({ page, request }) => {
    await loginAsSupervisor(page);
    await createShift(page, 'Event Confirm Shift', '2026-08-02T08:00', '2026-08-02T16:00');
    const shiftId = await page.locator('.shift-selector select').inputValue();

    // Arrangement only: create a raw (unconfirmed) event directly via the
    // real API, since C3d has no operator event-create UI in this test file.
    const supToken = await apiLogin(request, 'sup1', 'sup1-devpass');
    const headers = { Authorization: `Bearer ${supToken}` };
    const createRes = await request.post(`${API_BASE_URL}/events`, {
      headers, data: { shift_id: shiftId, event_type: 'shift_update', title: 'Unconfirmed relay note', risk_class: 'R0' }
    });
    expect(createRes.ok()).toBe(true);

    await page.reload();
    await page.waitForSelector('main.operations-console', { timeout: 10000 });
    await page.selectOption('.shift-selector select', { label: 'Event Confirm Shift · OPEN' });

    // The timeline (confirmed-only projection) must not show it yet, while
    // the supervisor Event confirm list does (SPEC R3: complete collection).
    await expect(page.locator('.shift-timeline')).not.toContainText('Unconfirmed relay note');
    const eventItem = page.locator('[aria-label="Event confirm and correct"] .incident-list__item', { hasText: 'Unconfirmed relay note' });
    await expect(eventItem).toBeVisible();

    await eventItem.locator('[aria-label^="Confirm event"] button[type="submit"]').click();
    await expect(page.locator('.shift-timeline')).toContainText('Unconfirmed relay note');
  });

  test('acknowledges an incident, unblocking the operator transition', async ({ page }) => {
    await loginAsOperator(page);
    await createShift(page, 'Ack Shift', '2026-08-02T08:00', '2026-08-02T16:00');
    await page.fill('#inc-summary', 'Pressure alarm');
    await page.selectOption('#inc-risk', 'R1');
    await page.click('form[aria-label="Report incident"] button[type="submit"]');
    await expect(page.locator('.incident-list__item')).toContainText('Pressure alarm');
    const shiftId = await page.locator('.shift-selector select').inputValue();

    const supPage = await page.context().newPage();
    await loginAsSupervisor(supPage);
    // Assign self so operational reads/capabilities are ACTIVE-scoped.
    const supToken2 = await supPage.context().request.post(`${API_BASE_URL}/auth/login`, { data: { username: 'sup1', password: 'sup1-devpass' } });
    const { access_token } = await supToken2.json();
    await supPage.context().request.post(`${API_BASE_URL}/shifts/${shiftId}/assignments`, {
      headers: { Authorization: `Bearer ${access_token}` }, data: { user_id: 'sup1' }
    });
    await supPage.reload();
    await supPage.waitForSelector('main.operations-console', { timeout: 10000 });
    await supPage.selectOption('.shift-selector select', { label: 'Ack Shift · OPEN' });

    const incItem = supPage.locator('[aria-label="Incident and handover"] .incident-list__item', { hasText: 'Pressure alarm' });
    await incItem.locator('button:has-text("Acknowledge")').click();
    await expect(incItem).toHaveCount(0);
    await supPage.close();

    await page.reload();
    await page.waitForSelector('main.operations-console', { timeout: 10000 });
    await page.selectOption('.shift-selector select', { label: 'Ack Shift · OPEN' });
    await expect(page.locator('[aria-label="Target status for Pressure alarm"]')).toBeVisible();
  });

  test('handover acknowledge is refused without destination assignment, then succeeds after a real destination assignment', async ({ page, request }) => {
    await loginAsSupervisor(page);
    await createShift(page, 'HO From Shift', '2026-08-02T08:00', '2026-08-02T16:00');
    const fromId = await page.locator('.shift-selector select').inputValue();
    const supToken = await apiLogin(request, 'sup1', 'sup1-devpass');
    const headers = { Authorization: `Bearer ${supToken}` };
    const opToken = await apiLogin(request, 'op1', 'op1-devpass');
    const toRes = await request.post(`${API_BASE_URL}/shifts`, {
      headers: { Authorization: `Bearer ${opToken}` },
      params: { name: 'HO To Shift', starts_at: '2026-08-03T08:00:00Z', ends_at: '2026-08-03T16:00:00Z' }
    });
    expect(toRes.ok()).toBe(true);
    const toId = (await toRes.json()).shift_id as string;
    const hoRes = await request.post(`${API_BASE_URL}/handovers`, { headers, data: { from_shift_id: fromId, to_shift_id: toId } });
    expect(hoRes.ok()).toBe(true);

    await page.reload();
    await page.waitForSelector('main.operations-console', { timeout: 10000 });
    await page.selectOption('.shift-selector select', { label: 'HO From Shift · OPEN' });
    const reviewItem = page.locator('[aria-label="Incident and handover"] .incident-list__item', { hasText: `${fromId} → ${toId}` });
    await reviewItem.locator('button:has-text("Review")').click();
    await expect(reviewItem.getByRole('button', { name: 'Review' })).toHaveCount(0);

    // Source-only discovery remains truthful; backend checks destination.
    const ackItem = page.locator('[aria-label="Incident and handover"] .incident-list__item', { hasText: `${fromId} → ${toId}` });
    await ackItem.locator('button:has-text("Acknowledge")').click();
    await expect(page.locator('.mutation-feedback--error')).toContainText('The requested record was not found');

    // A distinct receiver with real source+destination assignments succeeds.
    for (const shiftId of [fromId, toId]) {
      const assigned = await request.post(`${API_BASE_URL}/shifts/${shiftId}/assignments`, { headers, data: { user_id: 'sup2' } });
      expect(assigned.ok()).toBe(true);
    }
    await page.getByRole('button', { name: 'Sign out' }).click();
    await loginAsSupervisor(page, 'sup2', 'sup2-devpass');
    await page.selectOption('.shift-selector select', { label: 'HO From Shift · OPEN' });
    const ackItem2 = page.locator('[aria-label="Incident and handover"] .incident-list__item', { hasText: `${fromId} → ${toId}` });
    await ackItem2.locator('button:has-text("Acknowledge")').click();
    await expect(ackItem2).toHaveCount(0);
  });

  test('freeze sends only expected_version, is refused pre-CLOSED, and succeeds after close plus a report approval, with retired override fields absent', async ({ page, request }) => {
    await loginAsSupervisor(page);
    await createShift(page, 'Freeze Shift', '2026-08-02T08:00', '2026-08-02T16:00');
    const shiftId = await page.locator('.shift-selector select').inputValue();

    await expect(page.locator('button:has-text("Freeze shift")')).toBeDisabled();

    const supToken = await apiLogin(request, 'sup1', 'sup1-devpass');
    const headers = { Authorization: `Bearer ${supToken}` };
    const closeRes = await request.post(`${API_BASE_URL}/shifts/${shiftId}/close`, { headers, data: { expected_version: 1 } });
    expect(closeRes.ok()).toBe(true);
    const genRes = await request.post(`${API_BASE_URL}/reports`, { headers, data: { shift_id: shiftId } });
    expect(genRes.ok()).toBe(true);
    const report = await genRes.json();
    const submitRes = await request.post(`${API_BASE_URL}/reports/${report.report_id}/submit-review`, {
      headers, data: { expected_version: report.version, expected_status: report.status }
    });
    expect(submitRes.ok()).toBe(true);
    await arrangeReportApproval(request, supToken, shiftId, report.report_id);

    await page.reload();
    await page.waitForSelector('main.operations-console', { timeout: 10000 });
    await page.selectOption('.shift-selector select', { label: 'Freeze Shift · CLOSED' });

    let capturedBody: string | null = null;
    await page.route('**/freeze', async (route) => {
      capturedBody = route.request().postData();
      await route.continue();
    });
    await page.click('button:has-text("Approve report")');
    await page.click('button:has-text("Freeze shift")');
    await expect(page.locator('.mutation-feedback--error')).toHaveCount(0);

    expect(capturedBody).not.toBeNull();
    const parsed = JSON.parse(capturedBody as unknown as string);
    expect(Object.keys(parsed)).toStrictEqual(['expected_version']);
    expect(parsed).not.toHaveProperty('override_unimplemented_prerequisites');
    expect(parsed).not.toHaveProperty('override_reason');
  });

  test('revokes an approved report via successor creation with a required reason - no fake status mutation', async ({ page, request }) => {
    await loginAsSupervisor(page);
    await createShift(page, 'Revoke Shift', '2026-08-02T08:00', '2026-08-02T16:00');
    const shiftId = await page.locator('.shift-selector select').inputValue();

    const supToken = await apiLogin(request, 'sup1', 'sup1-devpass');
    const headers = { Authorization: `Bearer ${supToken}` };
    await request.post(`${API_BASE_URL}/shifts/${shiftId}/close`, { headers, data: { expected_version: 1 } });
    const genRes = await request.post(`${API_BASE_URL}/reports`, { headers, data: { shift_id: shiftId } });
    const report = await genRes.json();
    await request.post(`${API_BASE_URL}/reports/${report.report_id}/submit-review`, {
      headers, data: { expected_version: report.version, expected_status: report.status }
    });
    await arrangeReportApproval(request, supToken, shiftId, report.report_id);

    await page.reload();
    await page.waitForSelector('main.operations-console', { timeout: 10000 });
    await page.selectOption('.shift-selector select', { label: 'Revoke Shift · CLOSED' });
    await page.click('button:has-text("Approve report")');
    await expect(page.locator('button:has-text("Revoke approval")')).toBeVisible();

    const revokeBtn = page.getByRole('button', { name: /Revoke approval/ });
    await expect(revokeBtn).toBeDisabled();
    await page.fill('#revoke-reason', 'Section data was incomplete');
    await revokeBtn.click();
    await expect(page.locator('.mutation-feedback--error')).toHaveCount(0);
    await expect(page.getByText('Report status is DRAFT; no supervisor action available.')).toBeVisible();
  });
});
