# Implementation Phases

## Phase 1 — Foundation and Contracts

Khóa domain lifecycle, Operations Ledger, JSON Schemas, database foundation, CVF risk/approval/evidence models và contract test framework. Gate: tạo được một shift record hoàn chỉnh không cần LLM; schemas valid; lifecycle/freeze rõ ràng.

## Phase 2 — Core Operations Workspace

Xây authentication, shifts, internal chat, attachments, Quick Actions, timeline, events, tasks, customer requests, incidents, handover, template reports, audit, PWA offline và realtime. Gate: hoàn thành một ca 12 giờ từ start đến freeze khi AI và external channels đều tắt.

## Phase 3 — CVF Governance and Refinery

Tích hợp CVF Application Profile, domain lock, risk/approval/evidence/data/provider/cost/refusal/termination/freeze policies; Refinery normalization, terminology, dedupe, redaction, conflict và context candidates. Gate: protected actions đi qua policy, R3/R4 không bypass, Refinery lỗi có fallback.

## Phase 4 — AI and Channel Capabilities

Xây AI Gateway, providers, model routing, context builder, structured output, budget, fallback, kill switch; Integration Edge, generic webhook, customer portal, identity mapping, routing, outbound và mock Zalo/WhatsApp. Gate: thay provider/channel không sửa core; invalid schema bị reject; external prompt injection không vượt trust boundary.

## Phase 5 — Reporting, Hardening and Freeze

Hoàn thiện báo cáo, dashboard, search, observability, backup/restore, resilience, security, performance, deployment profiles, runbook, Shadow Mode pilot và release freeze. Gate: evidence traceability, outage drills, backup restore và owner review đều đạt.
