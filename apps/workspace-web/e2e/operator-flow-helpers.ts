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
