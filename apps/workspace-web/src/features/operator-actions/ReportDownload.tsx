import { useEffect, useRef, useState } from 'react';
import { ApiError, BinaryApiError } from '../../services/api';
import { fetchReportExport, REPORT_EXPORT_VIEWS, type ReportExportFormat, type ReportExportView } from '../../services/reportExport';
import type { ReportEntry } from '../../services/operatorApi';

interface ReportDownloadProps {
  report: ReportEntry;
}

type Feedback =
  | { status: 'idle' }
  | { status: 'busy'; message: string }
  | { status: 'success' | 'error'; message: string };

function revokeObjectUrl(ref: { current: string | null }) {
  const currentUrl = ref.current;
  if (!currentUrl) return;
  ref.current = null;
  URL.revokeObjectURL(currentUrl);
}

function safeErrorMessage(error: unknown): string {
  if (error instanceof BinaryApiError) {
    if (error.code === 'EXPORT_BUSY') return 'Report export is busy. Choose Download again to retry.';
    if (error.code === 'EXPORT_INVALID_PARAMETER') return 'This report view or format is not available.';
    if (error.code === 'EXPORT_INVALID_SNAPSHOT') return 'This report version could not be exported safely.';
    if (error.code === 'EXPORT_UNSUPPORTED_TEXT') return 'This report contains text that cannot be exported safely.';
    if (error.code === 'EXPORT_LIMIT_EXCEEDED') return 'This report exceeds the export limits.';
    if (error.kind === 'unauthorized') return 'Your session has expired. Please sign in again.';
    if (error.kind === 'forbidden') return 'You do not have access to this report.';
    if (error.kind === 'not_found') return 'This report version is no longer available.';
    if (error.kind === 'cancelled') return 'Download cancelled.';
    if (error.kind === 'network') return 'Could not reach the server. Check your connection and try again.';
    if (error.kind === 'invalid') return 'The report could not be exported with these options.';
    return 'The report could not be downloaded. Choose Download to try again.';
  }
  if (error instanceof ApiError && error.kind === 'invalid') {
    return 'The report version is not available for download.';
  }
  return 'The report could not be downloaded. Choose Download to try again.';
}

export function ReportDownload({ report }: ReportDownloadProps) {
  const [format, setFormat] = useState<ReportExportFormat>('pdf');
  const [view, setView] = useState<ReportExportView>('shift-summary');
  const [feedback, setFeedback] = useState<Feedback>({ status: 'idle' });
  const abortRef = useRef<AbortController | null>(null);
  const objectUrlRef = useRef<string | null>(null);
  const mountedRef = useRef(true);
  const busy = feedback.status === 'busy';
  const feedbackId = `report-download-feedback-${report.version}`;
  const reportLabel = `report version ${report.version}`;

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      abortRef.current?.abort();
      revokeObjectUrl(objectUrlRef);
    };
  }, []);

  async function startDownload() {
    if (busy || abortRef.current) return;
    revokeObjectUrl(objectUrlRef);
    if (typeof navigator !== 'undefined' && navigator.onLine === false) {
      setFeedback({ status: 'error', message: 'You are offline. Reconnect before downloading this report.' });
      return;
    }

    const controller = new AbortController();
    abortRef.current = controller;
    setFeedback({ status: 'busy', message: `Preparing ${format.toUpperCase()} for ${reportLabel}.` });
    let createdUrl: string | null = null;

    try {
      const file = await fetchReportExport(report.report_id, report.version, format, view, controller.signal);
      if (!mountedRef.current) return;
      if (controller.signal.aborted) {
        setFeedback({ status: 'error', message: 'Download cancelled.' });
        return;
      }

      createdUrl = URL.createObjectURL(file.blob);
      objectUrlRef.current = createdUrl;
      const anchor = document.createElement('a');
      anchor.href = createdUrl;
      anchor.download = file.filename;
      anchor.rel = 'noopener';
      document.body.appendChild(anchor);
      try {
        // This is only reached from the user's explicit Download button action.
        anchor.click();
      } finally {
        anchor.remove();
      }

      if (!mountedRef.current) return;
      setFeedback({ status: 'success', message: `Download started for ${reportLabel}.` });
      const downloadedUrl = createdUrl;
      window.setTimeout(() => {
        if (objectUrlRef.current === downloadedUrl) revokeObjectUrl(objectUrlRef);
      }, 0);
      createdUrl = null;
    } catch (error) {
      if (createdUrl && objectUrlRef.current === createdUrl) revokeObjectUrl(objectUrlRef);
      if (mountedRef.current) setFeedback({ status: 'error', message: safeErrorMessage(error) });
    } finally {
      if (abortRef.current === controller) abortRef.current = null;
    }
  }

  function cancelDownload() {
    abortRef.current?.abort();
  }

  return (
    <div className="report-download" role="group" aria-label={`Download controls for ${reportLabel}`}>
      <p className="report-download__metadata">
        Version {report.version} · Status: {report.status} · {report.is_current ? 'Current version' : 'Historical version'}
      </p>
      {!report.is_current && (
        <p className="async-state async-state--empty" role="note">
          Historical report snapshot; this version is not current.
        </p>
      )}

      <label>
        View
        <select
          aria-label={`View for report version ${report.version}`}
          value={view}
          onChange={(event) => setView(event.target.value as ReportExportView)}
          disabled={busy}
        >
          {REPORT_EXPORT_VIEWS.map((item) => (
            <option key={item} value={item}>{item}</option>
          ))}
        </select>
      </label>

      <label>
        Format
        <select
          aria-label={`Format for report version ${report.version}`}
          value={format}
          onChange={(event) => setFormat(event.target.value as ReportExportFormat)}
          disabled={busy}
        >
          <option value="pdf">PDF</option>
          <option value="xlsx">Excel (.xlsx)</option>
        </select>
      </label>

      <button
        type="button"
        onClick={() => void startDownload()}
        disabled={busy}
        aria-busy={busy}
        aria-describedby={feedback.status === 'idle' ? undefined : feedbackId}
        className="form-btn"
        aria-label={`Download report version ${report.version}`}
      >
        {busy ? `Preparing ${format.toUpperCase()}…` : `Download ${format.toUpperCase()}`}
      </button>

      {busy && (
        <button
          type="button"
          onClick={cancelDownload}
          className="form-btn form-btn--small"
          aria-label={`Cancel download for report version ${report.version}`}
        >
          Cancel
        </button>
      )}

      {feedback.status === 'busy' && (
        <p id={feedbackId} role="status" aria-live="polite" aria-atomic="true">
          {feedback.message}
        </p>
      )}
      {feedback.status === 'success' && (
        <p id={feedbackId} role="status" aria-live="polite" aria-atomic="true">
          {feedback.message}
        </p>
      )}
      {feedback.status === 'error' && (
        <p id={feedbackId} role="alert" aria-live="assertive" aria-atomic="true">
          {feedback.message}
        </p>
      )}
    </div>
  );
}
