import { describe, expect, it } from 'vitest';
import manifestSource from '../../public/manifest.webmanifest?raw';
import offlineSource from '../../public/offline.html?raw';
import workerSource from '../../public/sw.js?raw';

describe('PWA navigation-only contract', () => {
  it('owns a real icon and truthful fallback', () => {
    const manifest = JSON.parse(manifestSource);
    expect(manifest.icons).toEqual([expect.objectContaining({ src: '/icons/app-icon.svg' })]);
    expect(offlineSource).toContain('Không có dữ liệu API nào được cache');
    expect(offlineSource).not.toContain('Cập nhật sẽ được lưu tạm');
  });

  it('intercepts navigation only and never writes API responses', () => {
    expect(workerSource).toContain("request.mode !== 'navigate'");
    expect(workerSource).toContain("request.method !== 'GET'");
    expect(workerSource).not.toMatch(/cache\.put|caches\.match\(request\)/);
  });
});
