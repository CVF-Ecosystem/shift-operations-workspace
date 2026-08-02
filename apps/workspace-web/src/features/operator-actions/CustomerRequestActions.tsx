// P2C-MUTATION-FULL-UI-C3C (SPEC R18/R20, WO C3C-BUILD-REV-F4): Customer
// Request creation and transition actions. Target states are derived from
// the canonical backend lifecycle table - WAITING cannot skip to CLOSED.
import { useCallback, useState } from 'react';
import { operatorApi } from '../../services/operatorApi';
import { useMutationControl } from './useMutationControl';
import { MutationFeedback } from './MutationFeedback';
import { CUSTOMER_REQUEST_LIFECYCLE } from './types';
import type { CustomerRequest, CustomerRequestStatus } from '../../types/operations';

interface CustomerRequestActionsProps {
  shiftId: string;
  customerRequests: CustomerRequest[];
  onRefresh: () => Promise<void>;
}

export function CustomerRequestActions({ shiftId, customerRequests, onRefresh }: CustomerRequestActionsProps) {
  const [customerId, setCustomerId] = useState('');
  const [summary, setSummary] = useState('');

  const doCreate = useCallback(async () => {
    await operatorApi.createCustomerRequest(shiftId, customerId.trim(), summary.trim());
    setCustomerId('');
    setSummary('');
  }, [shiftId, customerId, summary]);

  const createControl = useMutationControl(doCreate, onRefresh);
  const createDisabled = createControl.isSubmitting || createControl.isLockedOut;

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerId.trim() || !summary.trim()) return;
    await createControl.submit();
  };

  return (
    <div className="action-group">
      <form aria-label="Create customer request" className="action-form" onSubmit={handleCreateSubmit}>
        <h3 className="form-legend">Create Customer Request</h3>
        <label htmlFor="cr-customer-id" className="form-label">Customer ID</label>
        <input
          id="cr-customer-id"
          type="text"
          value={customerId}
          onChange={(e) => { setCustomerId(e.target.value); createControl.reset(); }}
          required
          disabled={createDisabled}
          maxLength={120}
          aria-describedby={createControl.feedbackId}
          className="form-input"
        />
        <label htmlFor="cr-summary" className="form-label">Summary</label>
        <input
          id="cr-summary"
          type="text"
          value={summary}
          onChange={(e) => { setSummary(e.target.value); createControl.reset(); }}
          required
          disabled={createDisabled}
          maxLength={500}
          className="form-input"
        />
        <button
          type="submit"
          disabled={createDisabled || !customerId.trim() || !summary.trim()}
          aria-busy={createControl.isSubmitting}
          className="form-btn form-btn--primary"
        >
          {createControl.isSubmitting ? 'Creating…' : 'Create request'}
        </button>
        <MutationFeedback
          id={createControl.feedbackId}
          state={createControl.state}
          onRefreshAndUnlock={() => void createControl.refreshAndUnlock()}
        />
      </form>

      {customerRequests.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <h3 className="form-legend">Customer Request Transitions</h3>
          <ul className="cr-list" aria-label="Customer request list">
            {customerRequests.map((cr) => (
              <CustomerRequestItem key={cr.request_id} request={cr} onRefresh={onRefresh} />
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function CustomerRequestItem({ request, onRefresh }: { request: CustomerRequest; onRefresh: () => Promise<void> }) {
  const legalTargets = CUSTOMER_REQUEST_LIFECYCLE[request.status];
  const [targetStatus, setTargetStatus] = useState<CustomerRequestStatus | ''>(legalTargets[0] ?? '');

  const doTransition = useCallback(async () => {
    if (!targetStatus) return;
    await operatorApi.transitionCustomerRequest(request.request_id, targetStatus, request.version);
  }, [request.request_id, request.version, targetStatus]);

  const control = useMutationControl(doTransition, onRefresh);
  const disabled = control.isSubmitting || control.isLockedOut;

  if (legalTargets.length === 0) {
    return (
      <li className="cr-list__item">
        <span className="cr-list__summary">{request.summary}</span>
        <span className="cr-list__status status-badge">{request.status}</span>
      </li>
    );
  }

  return (
    <li className="cr-list__item">
      <span className="cr-list__summary">{request.summary}</span>
      <span className="cr-list__status status-badge">{request.status}</span>
      <form
        aria-label={`Transition request ${request.summary}`}
        className="action-form action-form--inline"
        onSubmit={async (e) => { e.preventDefault(); await control.submit(); }}
      >
        <select
          aria-label={`Target status for ${request.summary}`}
          value={targetStatus}
          onChange={(e) => { setTargetStatus(e.target.value as CustomerRequestStatus); control.reset(); }}
          disabled={disabled}
          aria-describedby={control.feedbackId}
          className="form-input form-input--inline"
        >
          {legalTargets.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <button
          type="submit"
          disabled={disabled}
          aria-busy={control.isSubmitting}
          className="form-btn form-btn--small"
        >
          {control.isSubmitting ? 'Saving…' : 'Update'}
        </button>
        <MutationFeedback
          id={control.feedbackId}
          state={control.state}
          onRefreshAndUnlock={() => void control.refreshAndUnlock()}
        />
      </form>
    </li>
  );
}
