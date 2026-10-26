import { ApiError, request, requestBinary } from './api';
import type { ReportEntry } from './operatorApi';

export type ReportExportFormat = 'pdf' | 'xlsx';

export const REPORT_EXPORT_VIEWS = [
  'shift-summary',
  'customer-report',
  'incident-report',
  'handover-report'
] as const;

export type ReportExportView = (typeof REPORT_EXPORT_VIEWS)[number];

export interface ReportExportResult {
  blob: Blob;
  filename: string;
}

export async function fetchHistoricalReports(shiftId: string, signal?: AbortSignal): Promise<ReportEntry[]> {
  const reports = await request<ReportEntry[]>('/reports', {
    query: { shift_id: shiftId, include_history: true },
    signal
  });
  return reports.filter((report) => !report.is_current).sort((left, right) => right.version - left.version);
}

const MIME_TYPES: Record<ReportExportFormat, string> = {
  pdf: 'application/pdf',
  xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
};

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const FILENAME_PATTERN = /^attachment;\s*filename="report-([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})-v([1-9]\d*)-(shift-summary|customer-report|incident-report|handover-report)\.(pdf|xlsx)"$/i;

export async function fetchReportExport(
  reportId: string,
  version: number,
  format: ReportExportFormat,
  view: ReportExportView,
  signal?: AbortSignal
): Promise<ReportExportResult> {
  if (!UUID_PATTERN.test(reportId) || !Number.isSafeInteger(version) || version < 1) {
    throw new ApiError('invalid', 'The report version is not available for download.');
  }

  const response = await requestBinary(`/reports/${encodeURIComponent(reportId)}/export`, {
    query: { format, view },
    signal
  });
  const mediaType = response.contentType?.split(';', 1)[0]?.trim().toLowerCase();
  if (mediaType !== MIME_TYPES[format]) {
    throw new ApiError('server', 'The server returned an invalid report file.');
  }

  const filename = `report-${reportId}-v${version}-${view}.${format}`;
  if (response.contentDisposition !== null) {
    const match = FILENAME_PATTERN.exec(response.contentDisposition);
    if (
      !match ||
      match[1].toLowerCase() !== reportId.toLowerCase() ||
      Number(match[2]) !== version ||
      match[3].toLowerCase() !== view ||
      match[4].toLowerCase() !== format
    ) {
      throw new ApiError('server', 'The server returned an invalid report filename.');
    }
  }

  return { blob: response.blob, filename };
}
