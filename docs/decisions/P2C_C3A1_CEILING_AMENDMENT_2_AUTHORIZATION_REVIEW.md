# Authorization Review — P2-C C3a1 Work Order Amendment 2

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a1`
- Reviewer role: `AUTHORIZATION_REVIEWER`
- Future implementation-worker independence: `YES`
- Date: `2026-07-31`
- Disposition: `REVIEW_PASS / APPROVED UNDER OPERATOR-DELEGATED AUTHORITY`

## Mechanical evidence

- current partial BUILD is unstaged;
- exact file inventory is 50 changed paths against the existing 50-path
  ceiling, with zero missing and zero outside paths;
- the worker's 49 count came from an aggregated untracked-directory view and
  is corrected here rather than propagated;
- the three affected Python test hosts are 323, 342 and 372 lines;
- the hard executable Python limit is 300 and no exception applies;
- the accepted F1/F2 review matrix needs distinct CVF/application,
  cross-backend parity and real-PostgreSQL homes;
- exactly three companion paths are therefore necessary and sufficient.

## Review disposition

`P2C-C3A1-BUILD-RE-REVIEW-BLOCK-F1` is closed without waiver by authorizing
only the three named test companions. The exact ceiling becomes 53. The
amendment preserves the review requirements while keeping every Python file
under the load-bearing guard; it does not authorize compression by deleting
tests, a debt entry or an exemption.

The operator's standing delegation approves this Work Order amendment. It
does not authorize Claude CLI/MCP control, worker stage/commit/push,
self-review/FREEZE, C3a2, frontend work, tenant/data_scope changes or broader
claims.

After this amendment checkpoint is pushed, a separate four-surface resume
checkpoint must become the exact review parent. The external manual worker
then resumes only the amended C3a1 repair and returns:

`READY_FOR_INDEPENDENT_P2C_C3A1_BUILD_RE_RE_REVIEW`.
