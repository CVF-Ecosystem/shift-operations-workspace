# PROJECT KNOWLEDGE PACK SPEC

- Tranche: `PROJECT-KNOWLEDGE-PACK-2026-08-03`
- Parent design: `docs/decisions/ADR_2026-08-03_PROJECT_KNOWLEDGE_PACK.md`
- Risk: `R2`
- Status: `SPEC_COMPLETE_PENDING_INDEPENDENT_REVIEW`
- Active role: `SPEC_AUTHOR`

## 1. Bounded outcome

The BUILD governed by a later authorized Work Order may create a local-only,
repository-owned knowledge pack made of three curated Markdown files, one
machine manifest and deterministic validation/rehearsal evidence. The pack is
advisory context. It must cite canonical project sources and must not become a
second source of continuity, policy, implementation, catalog, roadmap or
operational truth.

This SPEC grants no BUILD, provider-call, remote-ingest, external-write,
Refinery, retrieval, RAG, installation, commit or FREEZE authority.

## 2. Exact candidate BUILD surface

A later Work Order may authorize exactly these eight final BUILD paths and no
others:

1. `knowledge/README.md`
2. `knowledge/PROJECT_CONTEXT.md`
3. `knowledge/OPERATIONS_GLOSSARY.md`
4. `knowledge/GOVERNANCE_BOUNDARIES.md`
5. `knowledge/manifest.json`
6. `scripts/check_project_knowledge.py`
7. `tests/unit/test_project_knowledge_pack.py`
8. `tests/integration/test_project_knowledge_ingest_rehearsal.py`

Governance records, continuity, implementation status, roadmap and catalog are
protected during BUILD. Any later closure synchronization must use a separate
C4 authorization and commit.

## 3. Curated document contract

### R1 — Exact eligible document set

The only locally index-eligible Markdown files are:

- `PROJECT_CONTEXT.md` — bounded product, architecture, implemented-status and
  business-roadmap orientation;
- `OPERATIONS_GLOSSARY.md` — stable domain terms and ownership boundaries;
- `GOVERNANCE_BOUNDARIES.md` — startup continuity, seven-step control chain,
  evidence, data-handling and claim limits.

`README.md` is operator guidance only and is never manifest-eligible. No other
Markdown file under `knowledge/` is permitted. Every curated document must be
UTF-8, non-empty, substantive, concise, and identify itself as advisory with
links to its canonical sources.

### R2 — Authority and conflict rules

Content must follow this topic-to-authority map:

| Topic | Canonical authority |
|---|---|
| Active continuity | `SESSION/ACTIVE_SESSION_STATE.json`, resolved active handoff and `SESSION/SESSION_MEMORY.md`; the compatibility mirror must agree |
| Implementation disposition | `IMPLEMENTATION_STATUS.json` |
| Module inventory/status | `docs/catalog/MODULE_REGISTRY.json` |
| Business sequence | `docs/implementation/EXECUTION_ROADMAP.md` |
| Governance contract/policy | `AGENTS.md`, `.cvf/manifest.json`, `.cvf/policy.json` |
| Domain terminology | The named `packages/operations-domain/` or `packages/workspace-contracts/` source cited by the entry |

List order does not create precedence. A curated claim that conflicts with its
topic authority makes that entry ineligible. Disagreement among overlapping
canonical continuity surfaces stops validation as
`BLOCKED_CONTINUITY_DRIFT`; any other canonical conflict stops validation as
`BLOCKED_KNOWLEDGE_SOURCE_CONFLICT`. The validator must never silently choose a
fallback source.

Curated documents must not copy mutable active next-move text, the active
handoff body, provider-local memory, raw operational records, production or
customer data, provider request/response bodies, credentials or secrets.

### R3 — Claim language

`knowledge/README.md` must replace the bootstrap overclaim with current
downstream truth: the pinned public-core helper can create a disposable local
index, while this project has no implemented remote ingest, retrieval, context
injection, RAG or learning runtime. The README and curated documents must not
state or imply that the pack automatically retrieves or injects context, that
the static validator is DLP/data minimization, or that provider/model behavior,
Refinery enforcement or production governance has been proved.

The validator must reject, case-insensitively, these unqualified claim phrases
in pack Markdown: `automatically retrieve`, `automatically inject`,
`enforcement will reject`, `retrieval is implemented`, `rag is implemented`,
and `production ready`. A test fixture may contain them only as isolated
negative-test input outside the final pack.

## 4. Manifest contract

### R4 — Exact top-level schema

`knowledge/manifest.json` must be UTF-8 JSON with no duplicate keys and exactly
these top-level fields:

- `schemaVersion`: exact string `1.0`;
- `packId`: exact string `shift-operations-project-knowledge`;
- `classification`: exact string `INTERNAL`;
- `reviewedAt`: an ISO calendar date `YYYY-MM-DD` not later than the
  validator's current UTC date; the validation clock must be injectable in
  tests;
- `entries`: an array of exactly three entries.

Unknown fields fail validation. JSON booleans must be true booleans; integers
must not be accepted where booleans are required.

### R5 — Exact entry schema

Each entry must contain exactly:

- `id`: unique lower-kebab-case stable identifier;
- `path`: one of the three exact basenames in R1;
- `owner`: exactly one of `ORCHESTRATOR`, `SPEC_AUTHOR`,
  `SESSION_SYNC_STEWARD`;
- `classification`: exact string `INTERNAL`;
- `disposition`: exactly one of `ACTIVE`, `OWNER_WITHDRAWN`,
  `SECURITY_RECLASSIFIED`, `REVIEW_BLOCKED`;
- `dispositionReason`: JSON `null` when disposition is `ACTIVE`, otherwise a
  non-empty string that contains no sensitive value;
- `purpose`: non-empty bounded text;
- `allowedConsumers`: non-empty array containing only
  `LOCAL_GOVERNED_AGENT` and/or `HUMAN_OPERATOR`, without duplicates;
- `sourcePins`: a non-empty array of exact objects containing only `path` and
  `sha256`;
- `reviewedAt`: an ISO calendar date `YYYY-MM-DD`, not later than the manifest
  date or the validator's injectable current UTC date;
- `refreshTriggers`: a non-empty array containing all exact values
  `SOURCE_SHA256_CHANGE`, `OWNER_WITHDRAWAL`, `SECURITY_RECLASSIFICATION`,
  `CONTINUITY_OR_BOOTSTRAP_CHANGE`, `REVIEW_FINDING` and no unknown value;
- `retentionPolicy`: exact string
  `RETAIN_WHILE_SOURCES_ARE_CURRENT_AND_OWNER_MAINTAINS_ENTRY`;
- `correctionPolicy`: exact string
  `REVIEWED_COMMIT_OR_AUTHORIZED_R2_WITHDRAWAL`;
- `eligibleForLocalIndex`: a JSON boolean derived under R7.

Unknown or missing entry fields fail validation.

### R6 — Path and pin semantics

`entries[].path` is relative to the `knowledge/` root and is deliberately
restricted to a direct-child basename: forward-slash normalized, no `/`, `\\`,
drive, URI, absolute prefix, dot segment, traversal or symlink. This makes the
manifest value exactly comparable to the upstream helper's
`chunks[].sourceFile = file.Name` output without a lossy projection.

Each `sourcePins[].path` is a unique project-root-relative POSIX path to a
regular tracked source file. Absolute paths, URIs, backslashes, empty/dot
segments, traversal, symlinks and resolution outside the project root fail.
Each `sha256` is exactly 64 lowercase hexadecimal characters and must equal
SHA-256 over the source's current raw bytes. The manifest must not pin itself,
generated `_index.json`, provider-local files or files outside the project.

The three entries have these exact ids, owners, consumers and source-path sets;
no extra or missing source path is allowed:

| id / path | owner | allowedConsumers | exact source paths |
|---|---|---|---|
| `project-context` / `PROJECT_CONTEXT.md` | `ORCHESTRATOR` | both allowed values | `IMPLEMENTATION_STATUS.json`; `docs/catalog/MODULE_REGISTRY.json`; `docs/implementation/EXECUTION_ROADMAP.md` |
| `operations-glossary` / `OPERATIONS_GLOSSARY.md` | `SPEC_AUTHOR` | both allowed values | `packages/operations-domain/README.md`; `packages/operations-domain/src/operations_domain/models.py`; `packages/operations-domain/src/operations_domain/lifecycle.py`; `packages/operations-domain/src/operations_domain/assignment_models.py`; `packages/operations-domain/src/operations_domain/report_models.py`; `packages/workspace-contracts/README.md` |
| `governance-boundaries` / `GOVERNANCE_BOUNDARIES.md` | `SESSION_SYNC_STEWARD` | both allowed values | `AGENTS.md`; `.cvf/manifest.json`; `.cvf/policy.json`; `docs/cvf/CONTEXT_CONTROL.md`; `docs/cvf/EVIDENCE_AND_TRUTH.md`; `docs/cvf/PROVIDER_GOVERNANCE.md`; `docs/cvf/RISK_AND_APPROVAL.md` |

Every second-level section in a curated document must end with one citation
line using exact grammar `Sources: ` followed by one or more backtick-wrapped,
semicolon-separated project-relative paths. The validator extracts only these
lines, rejects malformed/unknown paths, and requires the set of cited paths in
each document to equal that entry's `sourcePins[].path` set. This proves exact
referential coverage, not semantic support. Whether the prose is truthfully
supported and non-conflicting is an explicit independent-review obligation.

### R7 — Eligibility, freshness and disposition

`eligibleForLocalIndex` is asserted in the manifest but derived fail-closed by
the validator. It is true only when disposition is `ACTIVE` and all schema,
type, path, containment, source-pin, citation-coverage, classification,
ownership, continuity-field, content and security checks pass. The final
repository manifest requires all three entries to be `ACTIVE`, with null
reason and asserted/derived eligibility `true`. A stale, non-active or invalid
entry is omitted from the validator's eligible set and makes the CLI exit
nonzero; it must never be copied to rehearsal input.

Freshness events map deterministically as follows:

| Event | Representation | Diagnostic |
|---|---|---|
| source bytes changed | current SHA-256 differs from pin | `KPK_SOURCE_PIN_DRIFT` |
| owner withdrawal | `OWNER_WITHDRAWN` + reason | `KPK_OWNER_WITHDRAWN` |
| security reclassification | `SECURITY_RECLASSIFIED` + reason | `KPK_SECURITY_RECLASSIFIED` |
| continuity/bootstrap change | changed pin in the `governance-boundaries` entry, or failed exact continuity comparison below | `KPK_CONTINUITY_CHANGED` |
| review finding | `REVIEW_BLOCKED` + reason | `KPK_REVIEW_BLOCKED` |

For deterministic continuity conflict detection, the validator invokes the
repository's read-only session checker and additionally compares these exact
canonical/mirror pairs for equality: `currentMode`, `activePhase`,
`controlChainModel`, `activeHandoff`, `parkedOperatorCheckpoint`,
`nextAllowedMove`, and `updatedAt`, using the mapping already enforced by
`scripts/check_session_state.py`. It also requires `.cvf/manifest.json` and
`.cvf/policy.json` to agree exactly on `liveGovernanceEvidenceRequired` and
`mockAllowedOnlyForUi`, and the manifest `phaseModel` to equal the seven-step
chain in this SPEC. These are the only mechanically inferred canonical
conflicts. Semantic source support/conflict remains an independent human review
gate and must not be claimed as validator inference.

There is no age-based truth TTL. Source-byte changes, owner withdrawal,
security reclassification, continuity/bootstrap changes or review findings
make the affected entry stale until refreshed and reviewed. Ordinary
correction is a new reviewed commit. Reclassification, withdrawal or deletion
requires ORCHESTRATOR authorization plus explicit human R2 acknowledgment,
and SESSION_SYNC_STEWARD records the disposition. Git history is durable
history, not an erasure guarantee; secret/sensitive-data remediation requires
a separately authorized incident and may require host-level history repair.

## 5. Validator contract

### R8 — Deterministic, read-only validation

`scripts/check_project_knowledge.py` must run from the project root on the
repository pack by default, make no network/provider call, write no file and
return `0` only when the whole pack passes. It must emit stable diagnostic
codes and nonzero status for every failure class below:

- manifest JSON/schema/type/unknown-field failure;
- missing, duplicate, unmanifested or unexpected Markdown;
- invalid owner/classification/consumer/metadata/date;
- path escape, non-regular target, symlink or source-pin mismatch;
- citation-coverage or the exact canonical-field conflict in R7;
- empty, undersized or oversized curated Markdown;
- forbidden claim phrase;
- secret-like sentinel;
- committed or runtime `_index.json` residue.

Validation ordering must be deterministic. Diagnostics must identify the
entry/path and stable code but must not print matched secret values.

### R9 — Bounded static secret-like scan

The scan runs over raw UTF-8 text of the three curated Markdown files and
README, plus the decoded value of every manifest `purpose` and every non-null
`dispositionReason`. It uses Python regular-expression semantics and these
exact patterns/algorithms:

- PEM header, case-sensitive:
  `-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----`;
- assignment prefix, case-insensitive and multiline:
  `^[ \\t]*([A-Z][A-Z0-9_]*)[ \\t]*[:=]`;
- credential URL, case-insensitive:
  `\\b(?:https?|postgres(?:ql)?)://([^/\\s:@]+):([^@\\s/]+)@`;
- compact JWT, case-sensitive:
  `(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{8,}\\.[A-Za-z0-9_-]{8,}\\.[A-Za-z0-9_-]{8,}(?![A-Za-z0-9_-])`;
- AWS access-key id, case-sensitive: `\\bAKIA[0-9A-Z]{16}\\b`.

For each assignment prefix, uppercase capture group 1 and treat it as a
secret assignment only when it ends with one of the exact suffixes `API_KEY`,
`ACCESS_KEY`, `SECRET`, `TOKEN`, or `PASSWORD`; this deliberately catches both
bare names such as `TOKEN` and prefixed names such as `AUTH_TOKEN`.

For a sensitive assignment, parse the entire same-line remainder after `=` or
`:` with exact full-line grammar
`^[ \\t]*(?:\"([^\"\\r\\n]*)\"|'([^'\\r\\n]*)'|([^\\s\"'#]+))[ \\t]*(?:#.*)?$`.
Exactly one of the double-quoted, single-quoted or unquoted capture groups must
be populated and becomes the complete value. A missing/empty value, unmatched
quote, quoted newline, text after a closing quote other than whitespace or a
comment, or any remainder that does not fully match is a failure. For that
complete assignment value and each decoded URL-userinfo component, placeholder
acceptance is exact full-value matching after case-folding: `<redacted>`,
`<placeholder>`, `example`, or `dummy`; `${ENV_VAR}` is accepted only when it fully matches
`\\$\\{[A-Z][A-Z0-9_]*\\}` before case-folding. Placeholder substrings such as
`dummyRealSecret` fail. PEM, JWT and AWS matches have no placeholder bypass.
Tests must reject every bare and prefixed assignment suffix form in both
Markdown and a manifest human-controlled string. Safe controls must include:
prose without PEM dashes; an unassigned variable name; an assignment whose
name does not end in a sensitive suffix; a URL with no password userinfo (or
exact placeholder userinfo); a two-segment token; and an `AKIA` value with the
wrong length/alphabet. In both Markdown and a manifest-controlled string,
tests must also prove: quoted exact placeholder passes; a quoted
non-placeholder containing whitespace fails; and an unmatched quote fails.
This is bounded static screening only, not DLP, data minimization or
external-transfer authorization.

## 6. Disposable helper rehearsal contract

### R10 — Exact input and pinned helper

The integration rehearsal must resolve the core and its pin from
`.cvf/manifest.json`, require core `HEAD` to equal `cvfCoreCommit`, and invoke
only `<resolved-core>/scripts/ingest_cvf_downstream_knowledge.ps1`. It must
require that helper's raw-byte SHA-256 to equal
`856b99d9273b0384c40c05bc2132eae66e9dce20b9a9c8b75c3d91ae7016d2c6`.
Source inspection must reject the pinned helper if it contains PowerShell
network/remote-execution primitives from this exact case-insensitive token set:
`Invoke-WebRequest`, `Invoke-RestMethod`, `Start-BitsTransfer`, `curl`, `wget`,
`System.Net`, `HttpClient`, `WebClient`, `TcpClient`, `UdpClient`, or
`Start-Process`. This is reviewed-source evidence that the exact helper is
file-only; it is not an OS-level proof that a subprocess made zero packets.

After validator PASS, it creates a disposable directory outside the repository
and copies exactly the three eligible basenames from R1 into its direct root.
It must not copy `README.md`, `manifest.json`, any unmanifested file, directory
or symlink. It passes explicit `KnowledgePath`, `OutputIndex`, `CollectionId`
and `CollectionName` arguments. The exact collection values are:

- `CollectionId`: `shift-operations-project-knowledge`;
- `CollectionName`: `Shift Operations Project Knowledge`.

No POST, remote collection, provider call or repository write is permitted.
Any network primitive or helper-hash mismatch stops before subprocess launch.

### R11 — Index assertions and cleanup

The rehearsal output must satisfy all of the following before success:

- output exists only inside the disposable root;
- `collectionId` and `collectionName` equal R10;
- `chunkCount` is a positive integer and equals `chunks.length`;
- every chunk has a unique non-empty id, substantive content and non-empty
  keywords;
- the set of `chunks[].sourceFile` values equals exactly the three manifest
  `entries[].path` basenames whose derived eligibility is true;
- every eligible basename contributes at least one chunk;
- no sourceFile is `README.md`, an absolute path or an unmanifested name;
- no secret-like sentinel appears in serialized chunk content;
- no `_index.json` exists anywhere in the repository before or after the run.

The test must remove the entire disposable root in `finally` on success or
failure and assert both filesystem removal and absence of repository residue.
Host-specific `generatedAt` and `sourceFolder` are checked only for type and
containment within the disposable root; they are not reproducibility evidence.

## 7. Required tests

### R12 — Unit matrix

`tests/unit/test_project_knowledge_pack.py` must include positive validation of
the repository pack and isolated negative cases for:

1. duplicate JSON key and unknown/missing field;
2. bool/int confusion and unknown owner/classification/consumer;
3. duplicate id/path/source pin;
4. absolute, traversal, backslash, nested and symlink paths;
5. source absence, source-pin drift and unsupported source coverage;
6. unmanifested Markdown and forbidden README eligibility;
7. every freshness trigger and stale-entry exclusion from the eligible set;
8. invalid dates, future manifest review date and future entry review date,
   using an injected validation date;
9. every forbidden claim phrase;
10. every R9 secret sentinel plus corresponding safe controls;
11. repository/runtime `_index.json` residue;
12. stable non-secret diagnostics and deterministic validation order.

### R13 — Integration matrix

`tests/integration/test_project_knowledge_ingest_rehearsal.py` must prove:

1. exact core/helper pin resolution and file-only source-token inspection;
2. exact three-file disposable input with README excluded;
3. exact manifest-basename/index-sourceFile set equality;
4. positive chunk coverage and metadata checks;
5. failure on unexpected, missing, absolute or stale sourceFile;
6. failure on secret-like chunk content;
7. cleanup after both PASS and deliberately induced helper/assertion failure;
8. zero repository `_index.json` residue.

Tests may use temporary copies and synthetic fixtures but must not mock a claim
about AI governance or provider behavior. This tranche makes no such claim and
requires no real provider call.

## 8. Acceptance criteria

- `AC-01` Exact eight-path BUILD diff; no protected or ninth path changes.
- `AC-02` Manifest and all three entries satisfy R4-R7 with exact schema/types,
  exact direct-child basename semantics and current raw-byte source pins.
- `AC-03` Exact curated file set exists; README is not eligible and no
  unmanifested Markdown or `_index.json` exists.
- `AC-04` Authority mapping, advisory status, conflict stops, freshness and
  R2 withdrawal/correction boundaries are explicit and validated.
- `AC-05` All unit cases in R12 PASS, including stale exclusion, path/symlink
  attacks, secret sentinels and safe controls.
- `AC-06` The real pinned public-core helper runs locally against only the
  disposable three-file input; no helper copy or core edit occurs.
- `AC-07` Integration assertions in R13 PASS and index sourceFile set equals
  manifest eligible basenames exactly.
- `AC-08` Disposable input/output is removed on success and failure; repository
  and Git status contain no `_index.json` or runtime residue.
- `AC-09` Static validator/rehearsal make zero provider calls and zero external
  writes; the exact helper bytes pass the R10 file-only source inspection. No
  OS-level zero-packet claim is made.
- `AC-10` Repository JSON, session-mirror, catalog, file-size, repository and
  workspace-doctor gates PASS; only the already-bounded doctor warning may
  remain.
- `AC-11` Independent BUILD review later verifies source, tests, diff, cleanup
  and bounded claims without relying on self-approval.
- `AC-12` Closure claims only a validated local pack and disposable chunking by
  the pinned helper; it does not claim remote ingest, retrieval, injection,
  provider/model behavior, Refinery, RAG, learning or production governance.

## 9. Stop conditions

Stop immediately on any path overflow, source-pin drift, continuity or
canonical-source conflict, unknown classification/owner, sensitive or
RESTRICTED content, secret-like match, helper/core-pin mismatch, network or
provider-call possibility, POST/remote-write path, repository `_index.json`,
cleanup failure, test/gate failure, broadened claim, or missing independent
review. Do not retry a provider call because none is authorized.

## 10. Verification commands proposed for a later Work Order

The Work Order must authorize exact commands or semantically equivalent
repository-native invocations for:

```powershell
python scripts/check_project_knowledge.py
python -m pytest tests/unit/test_project_knowledge_pack.py -q
python -m pytest tests/integration/test_project_knowledge_ingest_rehearsal.py -q
python scripts/check_session_state.py
python scripts/generate_catalog.py --check
python scripts/check_file_size.py
python scripts/testing/validate_repository.py
```

It must additionally run the workspace doctor resolved from the pinned core,
verify the exact changed set, scan for `_index.json` residue and prove the
worktree contains no unauthorized runtime artifact.

## 11. Next governed move

Independent SPEC review only. A PASS may permit Work Order authoring. No BUILD,
provider call, helper execution, remote ingest, external write, staging, commit
or continuity/catalog synchronization is authorized by this draft.
