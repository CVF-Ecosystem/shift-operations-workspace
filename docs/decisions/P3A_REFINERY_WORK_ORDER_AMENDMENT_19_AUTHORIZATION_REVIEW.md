# P3-A Refinery Work Order Amendment 19 — Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Amendment reviewed:
  `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_19.md`
- Reviewed SHA-256:
  `3b78afc6492c19de192cae4f86ac0cda2234055f2e984b523a100e2b5ace11f7`
- Provider/network/remote-ingest calls during review: `0/0/0`
- Findings: `NONE`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 19 is necessary, sufficient and non-expansive for the retained A18
catalog-check stop. It authorizes exactly three already-dirty catalog/pin
paths, retains the exact32 candidate and every protected A18 output, and orders
one deterministic repair followed by only the gates that remain validly due.
PASS is authorization-review evidence only. It is not repair authority, BUILD
evidence, a BUILD commit, independent BUILD review, FREEZE or later-lane
authority.

## Governance and consumed-A18 truth

Workspace doctor returned `PASS WITH NOTE` with `24` passed checks and only the
pre-existing bounded legacy catalog-kit warning. Canonical memory, state,
mirror and active handoff agree that A18 was consumed at the first catalog
check failure after these retained passes:

- preflight;
- one atomic exact-nine repair;
- direct probe `4/4`;
- Refinery focused suite `57`;
- project-knowledge validator and focused Knowledge Pack suite `86`;
- file-size guard.

The failed catalog check, full suite and later gates are not relabeled or
silently inherited as PASS. A19 correctly treats them as failed/not-run and
defines a new bounded continuation. A18 authority commit
`e9090f966f14f88a4de768e217c8ad4433dfcf29` and acknowledgment commit
`8caaaa83a3cc46c1d81796f69968fb0a9327f713` are ancestors of pushed
`origin/main`; `HEAD == origin/main == 8caaaa83a3cc46c1d81796f69968fb0a9327f713`.
The consumed A18 Work Order, frozen sheet and final authorization review
reproduce at their bound hashes:

- A18: `2b11f8198a206a2c5df94e83b36ac6029c4829496d04717ef86058c483240d2a`;
- sheet: `deff7d1ae7289a4af3a07d8696fb02a47a3411d4a5ba7fa936b5afcab523e2f3`;
- review: `b9faf3544ac49615bf801c63503e658ac426b57ea9a0273bd85d4cfc3f4d4553`.

## Exact candidate and repair ceiling

Before this review artifact was created, the worktree was exact35: every one
of the exact32 candidate paths plus exactly A19, canonical state and mirror;
staged paths were zero. Independent ordinal/case-sensitive reproduction gives:

| Binding | Reproduced result |
|---|---|
| Exact candidate paths | `32` |
| Stable paths excluding memory/handoff | `30` |
| Stable30 manifest | `52a253f0b7e724f4d7b21d6324a02f801282d16b53fc5f072ba38598d21e02b3` |
| Exact repair paths | `3` |
| Protected stable paths | `27` |
| Protected27 manifest | `82aa69f30ba5ee7ab0ff7074293da47b252e0e5dd75417e705fa339f47d19475` |
| Staged paths | `0` |

The exact-three pre-hashes reproduce:

1. `docs/catalog/MODULE_REGISTRY.json` —
   `1fb8b6e1638b69e6df3ababb823cc18e12238b3d0d2841e501074ff461c22d35`;
2. `docs/catalog/MODULE_CATALOG.md` —
   `94e6c6e960d0b944edeecd34a971da7b6b3ebe70228eecd43b7cf4a761e13dd6`;
3. `knowledge/manifest.json` —
   `49e7f64e58ceb530271db920551220908efefe1235f33d3a9984a6640507b0d1`.

All eight non-manifest A18 post-repair hashes reproduce exactly. The ninth A18
path, `knowledge/manifest.json`, reproduces the exact A19 pre-hash above; A19
permits only its registry source-pin substitution. No source, test, status,
project-context, contract, fixture, package, dependency, archive, roadmap or
other path is needed or allowed. Registry and generated Markdown are necessary
to close the measured catalog drift; the manifest pin is necessary to keep the
closed Knowledge Pack source binding truthful. Those three are sufficient.

## Deterministic generator reproduction

The immutable generator hashes to
`fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b`.
Its frozen PowerShell block parses without error and its embedded Python body
compiles. Independent in-memory invocation of `load_registry`,
`enrich_metrics(..., generated_at='2026-08-04T00:00:00+00:00')` and
`render_markdown` reproduced exactly:

| Output | SHA-256 |
|---|---|
| `docs/catalog/MODULE_REGISTRY.json` | `1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727` |
| `docs/catalog/MODULE_CATALOG.md` | `32fe4ecbb7f7b493ba1536975d81aa95a895ca1424309dd580f232b8ee1bb484` |
| `knowledge/manifest.json` after its sole pin replacement | `cbf115da32e5ad9418f1d91678d2ec2f875e174ee434f5762648325f63da4f80` |

The generated registry reports exactly `22` modules, `20266` code LOC, `225`
code files, status totals `6/2/8/6` for
`contract-only/enforced/partial/stub`, and `refinery-bridge` metrics
`1569/11/11`. A recursive semantic comparison found only three registry
changes: frozen `generated_at`, total `code_loc` and Refinery `loc`. The
one-line manifest anchor occurs exactly once. The payload writes only registry
and catalog; the one atomic patch changes only the matching registry pin.

## Retained boundaries and ordered continuation

Archive hashes/lines reproduce at `335/e218cbc1…f86` and
`394/c50d4bfd…d44`. Normalized suffixes reproduce at `6a055880…ac6` and
`46f46615…b357`; both Markdown archive links resolve; memory is `324` lines
and handoff `594`, with both archives also at or below 600.

The continuation order is sound and fail-closed: authority and immutable
preflight precede the single generator write; its one-line pin patch follows;
post-hash/scope/protected checks precede knowledge and catalog gates; the full
suite precedes remaining repository/static/security gates; the final audit is
last. Every step runs at most once, stops at its first non-zero/contract
failure and forbids retry, alternate generator, timestamp substitution,
catalog CLI `--write`, helper, provider/network/remote-ingest/POST call and
BUILD commit. Retaining the already-passed A18 evidence avoids retrying or
mislabeling it. A successful continuation yields only a dirty exact32 candidate
pending fresh independent BUILD review.

## Exact next authority boundary

COMMIT_STEWARD may next partial-stage, commit and push exactly these six
governance paths/hunks:

1. `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_19.md`;
2. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_19_AUTHORIZATION_REVIEW.md`;
3. `SESSION/ACTIVE_SESSION_STATE.json`;
4. `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
5. only the new A19/review governance preamble hunks in
   `SESSION/SESSION_MEMORY.md`;
6. only the new A19/review governance preamble/compaction hunks in
   `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`.

The front-door governance hunks are separated from their retained candidate
rotation hunks, so partial staging is feasible. The checkpoint must preserve
all exact32 candidate hunks unstaged, retain protected27 and all bound hashes,
leave the handoff at or below 600 lines, and finish with staged zero. No repair
may run from this PASS alone.

After that exact-six checkpoint is pushed, the required fresh human R2 wording
is:

> Tôi phê duyệt R2 cho
> P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-19-2026-08-04, Work Order Amendment
> SHA-256 3b78afc6492c19de192cae4f86ac0cda2234055f2e984b523a100e2b5ace11f7,
> đúng 3 repair paths và final exact 32 BUILD/continuity paths, zero
> provider/network/remote-ingest calls.

Only after that exact acknowledgment is recorded and pushed may one
`REPAIR_WORKER` run the Amendment 19 continuation once. Any mismatch or failed
gate consumes the invocation and requires a fresh governed disposition; no
retry, self-review, BUILD commit, FREEZE, P3-B/P3-C, retrieval, RAG or learning
authority is granted.
