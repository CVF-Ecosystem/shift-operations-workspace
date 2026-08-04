# Work Order Amendment 25 — File-Split Debt Pin Reconciliation

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-25-2026-08-04`
- Consumed A24 SHA-256: `cc4d481d128b07566628871a01667ddbc1d1a45c2bd4b65c20241290b1bef51a`
- A24 review SHA-256: `00a93584a419b8fb274c3e205c1770122430f7c55979c0682b73b9d438153d69`
- A24 authority / R2 acknowledgment checkpoints: `478aef7311e759855c6e76670c60c71295f4aef7` / `86ee107b34e049d9b718f042bbfff35fdb0927b8`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REREVIEW`
- Calls: `0 provider / 0 network / 0 remote-ingest`

## Trigger and retained stop truth

A24 preflight and atomic exact-four repair/post-audit passed. Focused catalog
drift tests passed `5`; the project Knowledge validator passed; the focused
Knowledge Pack suite passed `86`; catalog check passed; the full non-live suite
passed `1597 / 128 skipped`; and session-state validation passed. Repository
validation then stopped at its first failure because the file-size guard found
the debt entry for `scripts/generate_catalog.py` still pinned to its pre-A24
SHA-256. JSON/YAML/contract/import-I/O/secret/diff and final audits were
`NOT_RUN`. There was no retry and no provider/network/remote-ingest call.

Read-only diagnosis confirms the debt registry contains the old generator SHA
exactly once and the new SHA zero times. A24 and its fresh R2 are consumed.

Initial authorization review `5a222a068ac54f035d303bd32030f41147c918f8dbdf449a573e1757621629f6`
returned blocking finding `A25-AUTH-F1`, no waiver: the original required
post-hash silently included whole-file LF normalization. This corrected Work
Order closes the finding by preserving all 29 CRLF sequences and binding the
literal-only post-hash. Fresh independent re-review is mandatory.

## Scope and immutable bindings

Current candidate is exact34 and staged0. A25 authorizes exactly one repair
path and final exact35:

1. `docs/reference/FILE_SPLIT_DEBT_BASELINE.json`.

The final exact35 is the retained A24 exact34 plus that debt registry. Excluding
the volatile canonical memory and active handoff and the one repair path, the
protected exact32 manifest is:

`9399529ae64ea63170ea94549ce1809618a8c79f60ab3149d86e9b4e4bb79cac`

The manifest algorithm is SHA-256 over ordinal-path-sorted records
`path UTF-8 + NUL + lowercase file SHA-256 ASCII + LF`.

| Path | Required pre SHA-256 | Required post SHA-256 |
|---|---|---|
| `docs/reference/FILE_SPLIT_DEBT_BASELINE.json` | `26e0929059d4d1c1e851dc75cfb775e306c86c10c5b7e1f6f1a7285e55f76b52` | `a647cb498ef800ef2b4ce8e6491741fec9ceb82d001e04f3e459d57ced6f9f4e` |

The only authorized byte change is one literal replacement:

```diff
-      "sha256": "fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b",
+      "sha256": "6a04502d0ef35e69225a5cb1fbd652c18db4d23814219c0e0cdb27792735b9b6",
```

The debt registry's existing 29 CRLF sequences must remain byte-identical; no
line-ending normalization is authorized. All 34 retained candidate paths,
including all four A24 outputs, are immutable. No debt fields, limits, path
entries, rationale, source, test, catalog, knowledge or continuity payload may
otherwise change during the repair.

## Retained A24 evidence

The following completed A24 evidence is retained without rerun or relabeling:

- exact-four repair/post-audit PASS;
- focused catalog drift `5 passed`;
- project Knowledge validator PASS;
- focused Knowledge Pack `86 passed`;
- catalog `--check` PASS;
- full non-live pytest `1597 passed / 128 skipped`;
- session-state validator PASS.

These retained results are valid because A25 changes only the repository-owned
file-size debt pin and protects every source, test, catalog, knowledge and
continuity candidate byte covered by those gates.

## One ordered invocation

After independent authorization review, pushed authority checkpoint, and a
fresh exact A25 R2 acknowledgment, `REPAIR_WORKER` runs once, stops at the
first failure, and never retries:

1. verify dynamic authority topology, ASCII R2 digest, artifact hashes,
   staged0, exact34, debt prehash, exactly one old/zero new SHA occurrence,
   and protected32 manifest;
2. use one `apply_patch` to perform the exact one-line replacement above while
   preserving exactly 29 CRLF sequences and every non-literal byte;
3. assert the debt posthash, exactly 29 CRLF sequences, zero old/exactly one new occurrence, final exact35,
   unchanged protected32 manifest, all retained A24 posthashes, and staged0;
4. run `python scripts/check_file_size.py` once;
5. run `python scripts/testing/validate_repository.py` once;
6. run the remaining JSON/YAML/contract/import-I/O/secret/diff gates once;
7. run the final exact35/exact1/protected32/posthash/continuity audit last.

No provider/network/remote-ingest/POST call, full-suite rerun, alternate fix,
BUILD commit, self-review, FREEZE, waiver, further debt, or later-lane expansion
is authorized. Any first failure consumes the invocation and requires a new
reviewed amendment and fresh R2.

## Exact authority boundary

Independent review must reproduce the retained evidence, exact-one change,
pre/post hashes, exact35/protected32 manifests, and no-rerun boundary. Only a
pushed governance authority checkpoint followed by the exact fresh R2 bound to
this file's SHA-256 may authorize the single invocation.
