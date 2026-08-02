// P2C-MUTATION-FULL-UI-C3C (SPEC R18/R31, WO C3C-BUILD-REREV-F3): operatorApi
// wraps the typed request primitive from api.ts for all C3c operator
// mutations. It never forks auth, error mapping, query encoding, or retry
// logic. Arguments are typed with the existing exact backend union types
// rather than `string`, so a caller can never pass an out-of-domain value
// past the type checker.
import { request } from './api';
import { enqueueTransition } from '../offline/queue';
import type { CustomerRequest, CustomerRequestStatus, Handover, Incident, IncidentStatus, OperationalEvent, RiskClass, Shift, Task, TaskCreationIntentResponse, TaskStatus } from '../types/operations';
import type { CapabilitiesResponse, Message, OperationalEventType, ReportResponse, ReportStatus } from '../types/backendContracts';

export type ReportEntry = ReportResponse;

export const transitionTaskOnline = (taskId: string, target_status: TaskStatus, expectedVersion: number) =>
  request<Task>(`/tasks/${encodeURIComponent(taskId)}/transition`, {
    method: 'POST', body: { target_status, expected_version: expectedVersion }
  });

export const transitionCustomerRequestOnline = (requestId: string, target_status: CustomerRequestStatus, expectedVersion: number) =>
  request<CustomerRequest>(`/customer-requests/${encodeURIComponent(requestId)}/transition`, {
    method: 'POST', body: { target_status, expected_version: expectedVersion }
  });

export const transitionIncidentOnline = (incidentId: string, target_status: IncidentStatus, expectedVersion: number) =>
  request<Incident>(`/incidents/${encodeURIComponent(incidentId)}/transition`, {
    method: 'POST', body: { target_status, expected_version: expectedVersion }
  });

export const operatorApi = {
  createShift: (name: string, starts_at: string, ends_at: string) =>
    request<Shift>('/shifts', { method: 'POST', query: { name, starts_at, ends_at } }),

  closeShift: (shiftId: string, expectedVersion: number) =>
    request<Shift>(`/shifts/${encodeURIComponent(shiftId)}/close`, {
      method: 'POST',
      body: { expected_version: expectedVersion }
    }),

  getCapabilities: (shiftId: string, signal?: AbortSignal) =>
    request<CapabilitiesResponse>(`/shifts/${encodeURIComponent(shiftId)}/capabilities`, { signal }),

  createMessage: (shiftId: string, text: string) =>
    request<Message>('/messages', { method: 'POST', body: { shift_id: shiftId, text } }),

  createEvent: (shiftId: string, event_type: OperationalEventType, title: string, risk_class: RiskClass) =>
    request<OperationalEvent>('/events', {
      method: 'POST',
      body: { shift_id: shiftId, event_type, title, risk_class }
    }),

  createTaskIntent: (shiftId: string, title: string, risk_class: RiskClass, description?: string) =>
    request<TaskCreationIntentResponse>('/tasks/creation-intents', {
      method: 'POST',
      body: { shift_id: shiftId, title, risk_class, description: description || undefined }
    }),

  createTask: (shiftId: string, title: string, risk_class: RiskClass, intentId?: string, description?: string) =>
    request<Task>('/tasks', {
      method: 'POST',
      body: { shift_id: shiftId, title, risk_class, intent_id: intentId ?? null, description: description || undefined }
    }),

  transitionTask: (taskId: string, target_status: TaskStatus, expectedVersion: number) => {
    if (!navigator.onLine) enqueueTransition('task.transition', taskId, target_status, expectedVersion);
    return transitionTaskOnline(taskId, target_status, expectedVersion);
  },

  createCustomerRequest: (shiftId: string, customerId: string, summary: string) =>
    request<CustomerRequest>('/customer-requests', {
      method: 'POST',
      body: { shift_id: shiftId, customer_id: customerId, summary }
    }),

  transitionCustomerRequest: (requestId: string, target_status: CustomerRequestStatus, expectedVersion: number) => {
    if (!navigator.onLine) enqueueTransition('customer_request.transition', requestId, target_status, expectedVersion);
    return transitionCustomerRequestOnline(requestId, target_status, expectedVersion);
  },

  reportIncident: (shiftId: string, summary: string, risk_class: RiskClass, description?: string) =>
    request<Incident>('/incidents', {
      method: 'POST',
      body: { shift_id: shiftId, summary, risk_class, description: description || undefined }
    }),

  transitionIncident: (incidentId: string, target_status: IncidentStatus, expectedVersion: number) => {
    if (!navigator.onLine) enqueueTransition('incident.transition', incidentId, target_status, expectedVersion);
    return transitionIncidentOnline(incidentId, target_status, expectedVersion);
  },

  createHandover: (from_shift_id: string, to_shift_id: string) =>
    request<Handover>('/handovers', {
      method: 'POST',
      body: { from_shift_id, to_shift_id }
    }),

  generateReport: (shiftId: string) =>
    request<ReportEntry>('/reports', { method: 'POST', body: { shift_id: shiftId } }),

  listReports: (shiftId: string, signal?: AbortSignal) =>
    request<ReportEntry[]>('/reports', { query: { shift_id: shiftId }, signal }),

  createReportVersion: (reportId: string, expectedVersion: number, expectedStatus: ReportStatus) =>
    request<ReportEntry>(`/reports/${encodeURIComponent(reportId)}/versions`, {
      method: 'POST',
      body: { expected_version: expectedVersion, expected_status: expectedStatus }
    }),

  submitReport: (reportId: string, expectedVersion: number, expectedStatus: ReportStatus) =>
    request<ReportEntry>(`/reports/${encodeURIComponent(reportId)}/submit-review`, {
      method: 'POST',
      body: { expected_version: expectedVersion, expected_status: expectedStatus }
    })
};
