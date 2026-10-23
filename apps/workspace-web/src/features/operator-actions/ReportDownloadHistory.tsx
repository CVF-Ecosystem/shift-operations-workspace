import { useEffect, useId, useRef, useState } from 'react';
import { ApiError } from '../../services/api';
import { fetchHistoricalReports } from '../../services/reportExport';
import type { ReportEntry } from '../../services/operatorApi';
import { ReportDownload } from './ReportDownload';

interface ReportDownloadHistoryProps {
  shiftId: string;
}

function historyErrorMessage(error: unknown): string {
  if (error instanceof ApiError && error.kind === 'unauthorized') return 'Your session has expired. Please sign in again.';
  if (error instanceof ApiError && error.kind === 'forbidden') return 'You do not have access to these report versions.';
  if (error instanceof ApiError && (error.kind === 'network' || error.kind === 'outcome_unknown')) {
    return 'Could not load historical report versions. Check your connection and try again.';
  }
  return 'Historical report versions could not be loaded. Choose Retry to try again.';
}

export function ReportDownloadHistory({ shiftId }: ReportDownloadHistoryProps) {
  const historyId = useId();
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [reports, setReports] = useState<ReportEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cancelled, setCancelled] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      abortRef.current?.abort();
    };
  }, []);

  async function loadHistory() {
    if (loading || abortRef.current) return;
    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(true);
    setError(null);
    setCancelled(false);
    try {
      const entries = await fetchHistoricalReports(shiftId, controller.signal);
      if (!mountedRef.current) return;
      if (controller.signal.aborted) {
        setCancelled(true);
        return;
      }
      setReports(entries);
      setLoaded(true);
    } catch (requestError) {
      if (!mountedRef.current) return;
      if (controller.signal.aborted || (requestError instanceof ApiError && requestError.kind === 'cancelled')) {
        setCancelled(true);
      } else {
        setError(historyErrorMessage(requestError));
      }
    } finally {
      if (abortRef.current === controller) abortRef.current = null;
      if (mountedRef.current) setLoading(false);
    }
  }

  function toggleHistory() {
    if (loading) return;
    if (expanded) {
      setExpanded(false);
      return;
    }
    setExpanded(true);
    if (!loaded) void loadHistory();
  }

  return (
    <div className="report-download-history">
      <button
        type="button"
        className="form-btn"
        onClick={toggleHistory}
        disabled={loading}
        aria-expanded={expanded}
        aria-controls={historyId}
      >
        {expanded ? 'Hide historical report versions' : 'Show historical report versions'}
      </button>

      <div id={historyId} hidden={!expanded}>
        {loading && (
          <>
            <p role="status" aria-live="polite">Loading historical report versions…</p>
            <button
              type="button"
              className="form-btn form-btn--small"
              aria-label="Cancel loading historical report versions"
              onClick={() => abortRef.current?.abort()}
            >
              Cancel loading
            </button>
          </>
        )}
        {cancelled && !loading && (
          <p role="status" aria-live="polite">
            Historical report loading was cancelled.{' '}
            <button
              type="button"
              className="form-btn form-btn--small"
              aria-label="Retry loading historical report versions"
              onClick={() => void loadHistory()}
            >
              Retry
            </button>
          </p>
        )}
        {error && !loading && (
          <p role="alert" aria-live="assertive">
            {error}{' '}
            <button
              type="button"
              className="form-btn form-btn--small"
              aria-label="Retry loading historical report versions"
              onClick={() => void loadHistory()}
            >
              Retry
            </button>
          </p>
        )}
        {loaded && !loading && reports.length === 0 && (
          <p role="status" aria-live="polite">No historical report versions.</p>
        )}
        {loaded && !loading && reports.map((report) => (
          <ReportDownload key={`${report.report_id}-v${report.version}`} report={report} />
        ))}
      </div>
    </div>
  );
}
