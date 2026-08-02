import { expect, test } from '@playwright/test';
import { arrangeTask, queueStorage } from './p2d-offline-realtime-helpers';
import { API_BASE_URL, apiLogin, createShift, loginAsOperator, loginAsSupervisor } from './operator-flow-helpers';

test.describe('P2-D bounded offline and polling evidence', () => {
  test('offline transition stages with zero POST, then reconnect replays once and cleans queue', async ({ page, context }) => {
    const item = await arrangeTask(page, 'P2D Offline');
    let transitionPosts = 0;
    let confirmingTaskGets = 0;
    await page.route('**/tasks/*/transition', async (route) => {
      if (route.request().method() === 'POST') transitionPosts += 1;
      await route.continue();
    });
    page.on('response', (response) => {
      if (response.request().method() === 'GET' && new URL(response.url()).pathname === '/tasks') confirmingTaskGets += 1;
    });
    await context.setOffline(true);
    await item.getByRole('button', { name: 'Update' }).click();
    await expect(page.getByText('Queued on this device.')).toBeVisible();
    expect(transitionPosts).toBe(0);
    expect(await queueStorage(page)).toHaveLength(1);
    await context.setOffline(false);
    await expect.poll(() => transitionPosts).toBe(1);
    await expect.poll(() => confirmingTaskGets).toBeGreaterThan(0);
    await expect(item).toContainText('IN_PROGRESS');
    await expect.poll(async () => (await queueStorage(page)).length).toBe(0);
  });

  test('online request losing transport remains outcome-unknown, unqueued and unretried', async ({ page }) => {
    await arrangeTask(page, 'P2D Ambiguous');
    const form = page.getByRole('form', { name: 'Append message' });
    await form.getByLabel('Message text').fill('ambiguous message');
    let posts = 0;
    await page.route('**/messages', async (route) => {
      if (route.request().method() === 'POST') posts += 1;
      await route.abort('connectionreset');
    });
    expect(await page.evaluate(() => navigator.onLine)).toBe(true);
    await form.getByRole('button', { name: 'Send message' }).click();
    await expect(form.locator('.mutation-feedback--locked')).toBeVisible();
    expect(await queueStorage(page)).toHaveLength(0);
    await page.waitForTimeout(1000);
    expect(posts).toBe(1);
  });

  test('service worker serves truthful offline navigation and never caches API traffic', async ({ page, context }) => {
    await arrangeTask(page, 'P2D Cache');
    await page.evaluate(() => navigator.serviceWorker.ready);
    const cached = await page.evaluate(async () => {
      const keys = await caches.keys();
      const requests = await Promise.all(keys.map(async (key) => (await caches.open(key)).keys()));
      return requests.flat().map((request) => request.url);
    });
    expect(cached.some((url) => url.endsWith('/offline.html'))).toBe(true);
    expect(cached.some((url) => url.includes('/api/') || url.includes('/auth/'))).toBe(false);
    await expect(page.getByRole('status').filter({ hasText: 'Polling sync:' })).not.toContainText(/push|WebSocket|SSE|exactly-once/i);
    await context.setOffline(true);
    await page.goto('/offline-navigation-proof');
    await expect(page.getByRole('heading', { name: 'Đang ngoại tuyến' })).toBeVisible();
    await expect(page.locator('main')).toContainText('Không có dữ liệu API nào được cache');
  });

  test('a stale replay blocks FIFO and never dispatches the later item', async ({ page, context, request }) => {
    const item = await arrangeTask(page, 'P2D Conflict');
    await context.setOffline(true);
    await item.getByRole('button', { name: 'Update' }).click();
    await item.getByRole('button', { name: 'Update' }).click();
    const queued = await queueStorage(page) as Array<{ recordId: string; expectedVersion: number }>;
    expect(queued).toHaveLength(2);
    const token = await apiLogin(request, 'op1', 'op1-devpass');
    const external = await request.post(`${API_BASE_URL}/tasks/${queued[0].recordId}/transition`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { target_status: 'IN_PROGRESS', expected_version: queued[0].expectedVersion }
    });
    expect(external.ok()).toBe(true);
    let replayPosts = 0;
    await page.route('**/tasks/*/transition', async (route) => { replayPosts += 1; await route.continue(); });
    await context.setOffline(false);
    await expect.poll(async () => (await queueStorage(page) as Array<{ state: string }>)[0]?.state).toBe('blocked');
    const after = await queueStorage(page) as Array<{ state: string }>;
    expect(after.map((entry) => entry.state)).toEqual(['blocked', 'pending']);
    expect(replayPosts).toBe(1);
  });

  test('another assigned actor appears through polling and assignment loss clears selection', async ({ page, request }) => {
    await loginAsSupervisor(page);
    await createShift(page, 'P2D Polling', '2026-08-05T08:00', '2026-08-05T16:00');
    const shiftId = await page.locator('.shift-selector select').inputValue();
    const form = page.getByRole('form', { name: 'Create task' });
    await form.getByLabel('Title').fill('Polling task');
    await form.getByRole('button', { name: 'Create task' }).click();
    const sup1 = await apiLogin(request, 'sup1', 'sup1-devpass');
    const sup2 = await apiLogin(request, 'sup2', 'sup2-devpass');
    const h1 = { Authorization: `Bearer ${sup1}` };
    const h2 = { Authorization: `Bearer ${sup2}` };
    expect((await request.post(`${API_BASE_URL}/shifts/${shiftId}/assignments`, { headers: h1, data: { user_id: 'sup2' } })).ok()).toBe(true);
    const tasks = await (await request.get(`${API_BASE_URL}/tasks`, { headers: h2, params: { shift_id: shiftId } })).json();
    expect((await request.post(`${API_BASE_URL}/tasks/${tasks[0].task_id}/transition`, { headers: h2, data: { target_status: 'IN_PROGRESS', expected_version: tasks[0].version } })).ok()).toBe(true);
    await expect(page.locator('.task-list__item', { hasText: 'Polling task' })).toContainText('IN_PROGRESS', { timeout: 12000 });
    const assignments = await (await request.get(`${API_BASE_URL}/shifts/${shiftId}/assignments`, { headers: h1 })).json();
    const own = assignments.find((entry: { user_id: string }) => entry.user_id === 'sup1');
    expect((await request.post(`${API_BASE_URL}/shifts/${shiftId}/assignments/${own.assignment_id}/revoke`, { headers: h1, data: { expected_version: own.version } })).ok()).toBe(true);
    await page.evaluate(() => window.dispatchEvent(new Event('online')));
    await expect(page.locator('.shift-selector select')).toHaveCount(0, { timeout: 12000 });
    await expect(page.getByText('No shifts available.')).toBeVisible();
    await expect(page.getByText('Polling task')).toHaveCount(0);
  });

  test('same-actor tabs racing one CAS produce one 200 and a visibly blocked 409 loser', async ({ page, context }) => {
    await arrangeTask(page, 'P2D Two Tab');
    const second = await context.newPage();
    await loginAsOperator(second);
    await second.selectOption('.shift-selector select', { label: 'P2D Two Tab · OPEN' });
    const firstItem = page.locator('.task-list__item', { hasText: 'P2D Two Tab task' });
    const secondItem = second.locator('.task-list__item', { hasText: 'P2D Two Tab task' });
    await expect(secondItem).toBeVisible();
    const statuses: number[] = [];
    let started = 0;
    let release!: () => void;
    const bothStarted = new Promise<void>((resolve) => { release = resolve; });
    let releaseWinner!: () => void;
    const winnerCommitted = new Promise<void>((resolve) => { releaseWinner = resolve; });
    await context.route('**/tasks/*/transition', async (route) => {
      if (route.request().method() !== 'POST') { await route.continue(); return; }
      started += 1;
      const order = started;
      if (started === 2) release();
      await bothStarted;
      if (order === 2) await winnerCommitted;
      const response = await route.fetch();
      statuses.push(response.status());
      if (order === 1) releaseWinner();
      await route.fulfill({ response });
    });
    await Promise.all([
      firstItem.getByRole('button', { name: 'Update' }).click(),
      secondItem.getByRole('button', { name: 'Update' }).click()
    ]);
    expect(started).toBe(2);
    await expect.poll(() => statuses.length).toBe(2);
    expect([...statuses].sort()).toEqual([200, 409]);
    await expect.poll(async () => {
      const texts = await Promise.all([page, second].map((target) => target.locator('.mutation-feedback--conflict').allTextContents()));
      return texts.flat().some((text) => text.includes('This record changed elsewhere.'));
    }).toBe(true);
    await second.close();
  });
});
