import { expect, type APIRequestContext, type Page } from '@playwright/test';
import { API_BASE_URL, apiLogin, createShift, loginAsOperator } from './operator-flow-helpers';

export async function arrangeTask(page: Page, name: string) {
  await loginAsOperator(page);
  await createShift(page, name, '2026-08-04T08:00', '2026-08-04T16:00');
  const form = page.getByRole('form', { name: 'Create task' });
  await form.getByLabel('Title').fill(`${name} task`);
  await form.getByRole('button', { name: 'Create task' }).click();
  const item = page.locator('.task-list__item', { hasText: `${name} task` });
  await expect(item).toBeVisible();
  return item;
}

export async function transitionTaskDirect(request: APIRequestContext, taskId: string, version: number, target = 'IN_PROGRESS') {
  const token = await apiLogin(request, 'op1', 'op1-devpass');
  return request.post(`${API_BASE_URL}/tasks/${taskId}/transition`, {
    headers: { Authorization: `Bearer ${token}` },
    data: { target_status: target, expected_version: version }
  });
}

export async function queueStorage(page: Page): Promise<unknown[]> {
  return page.evaluate(() => {
    const key = Object.keys(localStorage).find((item) => item.startsWith('shiftops.offline.queue.v1.'));
    return key ? JSON.parse(localStorage.getItem(key) ?? '[]') : [];
  });
}
