# integration-edge

**ROLE: BACKEND (edge/DMZ gateway)** · Deploy riêng ở biên public · Nhận kênh
ngoài (webhook), không sở hữu business truth.
Ranh giới: [`docs/architecture/FRONTEND_BACKEND_BOUNDARY.md`](../../docs/architecture/FRONTEND_BACKEND_BOUNDARY.md).

Public/DMZ boundary cho webhooks và outbound delivery.

## Non-ownership

Edge không sở hữu business truth, không confirm event và không truy cập toàn bộ Operations Ledger.

## Required controls

Signature verification, raw payload preservation, dedupe, rate limit, attachment validation, quarantine và canonicalization.
