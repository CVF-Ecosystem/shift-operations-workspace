import { useEffect, useState } from 'react';
import { api } from '../services/api';

type Health = { status: string; mode: string };

export function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [message, setMessage] = useState('');
  const [feed, setFeed] = useState<string[]>([
    '06:00 · Ca ngày đã sẵn sàng',
    '06:05 · Operations Ledger đang hoạt động ở chế độ NO_AI'
  ]);

  useEffect(() => { api.health().then(setHealth).catch(() => setHealth({ status: 'offline', mode: 'degraded' })); }, []);

  function submit() {
    const text = message.trim();
    if (!text) return;
    setFeed((items) => [...items, `${new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })} · ${text}`]);
    setMessage('');
  }

  return (
    <main className="shell">
      <header><div><strong>Shift Operations Workspace</strong><span>Mobile PWA / Desktop Web</span></div><small>{health?.status ?? 'checking'} · {health?.mode ?? '...'}</small></header>
      <section className="toolbar"><button>Sự cố</button><button>Sản lượng</button><button>Thiết bị</button><button>Khách hàng</button><button>Công việc tồn</button></section>
      <section className="feed">{feed.map((item, index) => <article key={index}>{item}</article>)}</section>
      <footer><input value={message} onChange={(e) => setMessage(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && submit()} placeholder="Nhập cập nhật vận hành..."/><button onClick={submit}>Gửi</button></footer>
    </main>
  );
}
