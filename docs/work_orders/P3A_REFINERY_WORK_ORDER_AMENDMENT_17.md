# Work Order Amendment 17 — P3-A Canonical Preflight Syntax

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-17-2026-08-04`
- Parent Amendment 16 SHA-256: `076032a3f1c5ed3943c574a894dff90cb887ec8b36d78af37e7d3f96427f3162`
- Amendment 16 review SHA-256: `e6ffe5e0c45abdd9eeaa2fb4e1ba031260243c8a34df748d55cc8feb49c44879`
- Failed A16 acknowledgment checkpoint: `2141f306ebe1509ea606a7db9965b1e64dfa91b5`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Calls: `0 provider / 0 network / 0 remote-ingest`

## Consumed A16 truth

The A16 acknowledgment was pushed. Its first command failed PowerShell parsing
at compressed token sequence `foreach($p in$a)` before any assertion or file
operation executed. Stop-first/no-retry was honored. No repair, probe, test or
later gate ran; zero calls. All exact32 bytes and nine repair pre-hashes remain
unchanged. A16/R2 are consumed and cannot be retried.

## Sole correction

Use canonical multiline PowerShell with whitespace-separated grammar for every
loop and conditional, including `foreach ($p in $a)`. The preflight must be
stored/read as a script block or file-safe multiline command, parsed before
execution, and invoked once only. No compressed `foreach`, `if`, `function` or
operator token adjacency is permitted.

Amendment 17 otherwise incorporates Amendment 16 and Amendment 15 unchanged:
exact nine repair paths/final exact32; stable30
`a50cebb5f4f4b2e6b6ae79bc56ebc70ac17c1fdd28b7242267a17e96e9c6a436`;
protected21
`68cbd2430a85e1cafc5a79b46a72d6479a9c2b0a09629cfb387f78c78d7a6070`;
all nine pre-hashes; canonical archive paths/hashes; four Markdown ceilings;
suffixes; exact repair/probe/acceptance/status work; ordered gates and claim
boundary.

## Ordered continuation

Run once, no retry, stop at first failure:

1. parse and run the canonical multiline preflight once, using the two A16
   archive paths and pushed A17 authority/R2 lineage;
2. edit exactly A15's nine repair paths;
3. run the four-case direct probe once;
4. run the explicit five-file focused suite once, all pass and at least 57;
5. run knowledge validation and focused Knowledge Pack once;
6. run file-size and catalog `--check` once without catalog mutation;
7. run full non-live pytest once;
8. run session/repository/static/security/diff checks once;
9. run final exact32/exact-nine/protected21/archive/suffix/line/staged audit.

No provider/network/remote-ingest, BUILD commit, self-review, FREEZE, waiver,
debt, expansion or later-lane action. PASS yields only a dirty exact32 candidate
pending independent BUILD re-review.

Independent authorization review, governance-only checkpoint and fresh exact
R2 naming this SHA, exact9/final32 and zero calls are mandatory.
