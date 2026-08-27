# channel-adapters

P4-D provides one digest-only `generic-webhook` adapter and deterministic
contract-only Zalo/WhatsApp mocks. The mocks make no vendor-format or live
delivery claim and cannot be selected at runtime. PWA, portal, email, SMS,
real vendor formats, credentials, retry and production deployment are outside
this bounded package tranche.
