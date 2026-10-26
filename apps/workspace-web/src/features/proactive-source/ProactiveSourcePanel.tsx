import { SOURCE_REASON_LABELS } from '../../types/proactiveSource';
import { useProactiveSourceRead } from './useProactiveSourceRead';

const MESSAGE = {
  idle: 'Nhập ba thời điểm UTC rồi chọn Xem nguồn dữ liệu.',
  loading: 'Đang đọc nguồn dữ liệu…',
  auth: 'Cần đăng nhập và xác minh người dùng.',
  forbidden: 'Không có quyền xem nguồn dữ liệu.',
  network: 'Không kết nối được nguồn dữ liệu.',
  invalid: 'Khoảng thời gian UTC không hợp lệ.',
  unavailable: 'Không thể xác minh nguồn dữ liệu.'
} as const;

export function ProactiveSourcePanel() {
  const { inputs, state, view, change, submit } = useProactiveSourceRead();
  return <section className="proactive-source" aria-labelledby="proactive-source-title">
    <h2 id="proactive-source-title">Kiểm tra nguồn dữ liệu</h2>
    <p>Nhập khoảng thời gian và mốc dữ liệu theo UTC.</p>
    <form onSubmit={(event) => { event.preventDefault(); void submit(); }}>
      <label>Bắt đầu UTC <input type="datetime-local" step="1" value={inputs.start}
        onChange={(event) => change('start', event.target.value)} /></label>
      <label>Kết thúc UTC <input type="datetime-local" step="1" value={inputs.end}
        onChange={(event) => change('end', event.target.value)} /></label>
      <label>Thời điểm đọc UTC <input type="datetime-local" step="1" value={inputs.asOf}
        onChange={(event) => change('asOf', event.target.value)} /></label>
      <button type="submit">Xem nguồn dữ liệu</button>
    </form>
    <div role="status" aria-live="polite">
      {state !== 'ready' ? MESSAGE[state] : view?.outcome === 'SOURCE_REFUSED' ?
        <>Nguồn dữ liệu từ chối: {SOURCE_REASON_LABELS[view.reason]}</> :
        view?.outcome === 'SOURCE_READY' ? <>
          <strong>Dữ liệu thử nghiệm</strong>
          <dl>
            <dt>Bắt đầu UTC</dt><dd>{view.window.query_start}</dd>
            <dt>Kết thúc UTC</dt><dd>{view.window.query_end}</dd>
            <dt>Thời điểm đọc UTC</dt><dd>{view.window.run_as_of}</dd>
            <dt>Số ca đủ điều kiện</dt><dd>{view.eligibleCount}</dd>
            <dt>Số ca được chọn</dt><dd>{view.selectedCount}</dd>
            <dt>Số phiên bản ứng viên</dt><dd>{view.candidateVersionCount}</dd>
            <dt>Số tham chiếu sự cố tối đa</dt><dd>{view.maxSnapshotIncidentRefs}</dd>
          </dl>
        </> : MESSAGE.unavailable}
    </div>
  </section>;
}
