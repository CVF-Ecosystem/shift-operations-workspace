export type SourceReason =
  | 'ACCESS_DENIED' | 'INVALID_WINDOW' | 'TIME_AMBIGUOUS'
  | 'COVERAGE_UNKNOWN' | 'SCOPE_INCOMPLETE' | 'SNAPSHOT_UNAVAILABLE'
  | 'INVALID_LINEAGE' | 'INCOMPATIBLE_POLICY' | 'SOURCE_UNAVAILABLE';

export interface SourceWindow {
  query_start: string;
  query_end: string;
  run_as_of: string;
}

export type SourceView =
  | { outcome: 'SOURCE_REFUSED'; reason: SourceReason }
  | { outcome: 'SOURCE_READY'; coverage: 'SYNTHETIC_FIXTURE'; window: SourceWindow;
      eligibleCount: number; selectedCount: number; candidateVersionCount: number;
      maxSnapshotIncidentRefs: number };

export const SOURCE_REASON_LABELS: Record<SourceReason, string> = {
  ACCESS_DENIED: 'Không có quyền xem nguồn dữ liệu.',
  INVALID_WINDOW: 'Khoảng thời gian không hợp lệ.',
  TIME_AMBIGUOUS: 'Thời gian không rõ múi giờ.',
  COVERAGE_UNKNOWN: 'Chưa xác định được phạm vi dữ liệu.',
  SCOPE_INCOMPLETE: 'Phạm vi dữ liệu chưa đầy đủ.',
  SNAPSHOT_UNAVAILABLE: 'Chưa có bản chụp dữ liệu.',
  INVALID_LINEAGE: 'Nguồn gốc dữ liệu không hợp lệ.',
  INCOMPATIBLE_POLICY: 'Chính sách dữ liệu không tương thích.',
  SOURCE_UNAVAILABLE: 'Nguồn dữ liệu chưa khả dụng.'
};
