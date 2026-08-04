# Work Order Amendment 14 — P3-A Remaining-Gates Resume

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-14-2026-08-04`
- Consumed Amendment 13 SHA-256: `332895d89799ec724031057cf265b1c84e6a62a8510b6f86363a4fe309f9da50`
- Amendment 13 review SHA-256: `c9719ab585e33f6b74f9ea0e3e182e681ffa1a5f9fa952e73892294e502d36a7`
- Amendment 13 authority / acknowledgment: `af691d049ca37288d99a09ac0df790018e3fc31c` / `20f3f73c5fdd9d3704823c8191f067f57422be76`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Provider/network/remote-ingest calls: `0/0/0`

## Trigger and retained stop truth

Amendment 13 preflight passed. Its single atomic six-path patch completed, and
`python scripts/check_file_size.py` passed. Before the focused suite, an
unauthorized read-only command attempted `rg` against Windows-invalid wildcard
literal paths and returned non-zero. Execution stopped immediately; the
command was not retried. Focused tests, catalog check, full suite and later
gates are `NOT_RUN`. Provider/network/remote-ingest calls were zero. Amendment
13 and its R2 are consumed.

## Completed repair truth

All six repair paths changed exactly as reviewed:

- `pipeline.py`: 285 lines, SHA `69a55e2e7ad3b115176ae853f2756d3115f69aa12d0d1f7a6088ab15bb8371bf`;
- `protection.py`: 260 lines, SHA `d909c740e1a2e93859ca47a596c3dac2afaf740648044523b5d5e9de3e58a3f5`;
- memory archive: 335 lines, SHA `e218cbc150d03bd9c42f623f972e43ee33ee00b530882195e2c8c145ab918f86`;
- handoff archive: 394 lines, SHA `c50d4bfd7c7745fa1bb3e5758eddb57c905f5d10fac5da5fda8707f63aee0d44`;
- canonical memory and active handoff are 301 and 492 lines before this
  authority preamble update, each with resolving archive pointers.

The dirty candidate is exact 32 paths. Excluding only the two volatile
continuity front-door preambles gives stable 30 paths with ordinal UTF-8
manifest SHA `a50cebb5f4f4b2e6b6ae79bc56ebc70ac17c1fdd28b7242267a17e96e9c6a436`.
The stable memory suffix from `Historical continuity from 2026-07-22` through
EOF is 243 lines / `6a055880ab97e542fa122ff6cbe3025d993aa521d3b4e9098abf82fa97237ac6`.
The handoff suffix from `The original P3-A intake/design/spec foundation`
through EOF is 2 lines / `46f46615b06dff42a2c44b55321e30c862881146a58a98549fe06f06aaceb357`.

Authority and R2 updates may change only the preambles before those suffixes.
The authority checkpoint must use partial staging so only new governance
preamble hunks—not any rotation/archive/source repair hunk—are committed.
After checkpoint/R2, exact 32 dirty paths and stable-30/suffix bindings must
still reproduce. Staged paths must be zero before continuation.

## Exact repair ceiling and continuation

Repair-touch ceiling is `0`; no path may change during the continuation. Final
dirty scope remains exact 32. Run once, stopping first failure:

1. verify pushed authority/R2 lineage, A14/review hashes, empty staged set,
   exact-32 path set, stable-30 manifest, source/archive hashes, suffix hashes,
   line limits and resolving links;
2. run the focused Refinery suite by explicitly listing the five tracked test
   files (`models`, `canonical`, `pipeline`, `adversarial`, `contract`) once;
   expect `53` passed;
3. run `python scripts/generate_catalog.py --check` once and require no catalog
   mutation;
4. run the full non-live pytest suite once;
5. run session-state, repository validator, JSON/YAML, forbidden import/I/O,
   secret and diff checks once;
6. final exact-32/zero-touch/stable-30/source/archive/suffix/link/line/staged
   audit once.

The failed wildcard `rg` command is not rerun or relabeled. Retain the passed
atomic repair and file-size evidence. No provider/network/remote-ingest call,
retry, edit, BUILD commit, self-review, FREEZE or later lane is authorized.
PASS yields only a dirty exact-32 candidate pending independent BUILD review.

Independent authorization review, a bounded partially staged authority
checkpoint, and fresh exact human R2 for Amendment 14 (`0` repair paths,
final exact 32, zero provider/network/remote-ingest) are required.
