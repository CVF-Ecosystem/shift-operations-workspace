# Work Order Amendment 24 — Platform-Stable Catalog Writes and Test Isolation

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-24-2026-08-04`
- Consumed A23 SHA-256: `98825deb5c9b68f3c2112020255820991dbe86b136ce8dc69fa2353d2ad00d63`
- A23 review SHA-256: `af32aff2af5003df5dfcc9131b25204f3f63baff9655560949da1ac1052d2ce8`
- A23 authority / R2 acknowledgment checkpoints: `cd24315b9e10435abb9224cda75fa2d2c9a64052` / `9a62662f2f5578ce04f10e9146afe015dca2bd8e`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Calls: `0 provider / 0 network / 0 remote-ingest`

## Trigger and retained stop truth

A23 preflight, exact-two normalization/post-audit, project Knowledge validator,
focused Knowledge Pack `86`, and catalog check passed. Full non-live pytest then
failed `2 failed / 1587 passed / 128 skipped / 8 errors`; all failures reported
`KPK_ELIGIBILITY_MISMATCH` / `KPK_SOURCE_PIN_DRIFT` for `PROJECT_CONTEXT.md`.
Execution stopped there; later gates were `NOT_RUN`, with no retry or call.

Read-only diagnosis found both catalog files restored to their original CRLF
pre-hashes. `tests/integration/test_catalog_drift_detection.py` snapshots them
with `read_text()` and restores with `write_text()`, which changes LF to CRLF on
Windows. The canonical generator uses the same platform-dependent text writes.
The catalog tests run before Knowledge tests in the full suite, so their teardown
creates the observed source-pin drift. A23/R2 are consumed.

## Scope and bindings

Current candidate is exact32, stable30 manifest
`f9bcbbc6e0bed42283c7aad994f6b1563311bcb216954e80c81016ad8734e056`,
staged0. A24 authorizes exactly four repair paths and final exact34:

1. `scripts/generate_catalog.py`;
2. `tests/integration/test_catalog_drift_detection.py`;
3. `docs/catalog/MODULE_REGISTRY.json`;
4. `docs/catalog/MODULE_CATALOG.md`.

The protected 28 existing stable paths exclude the two catalog paths and remain
bound to `0b87e6d8eec3d551d1106d1a5475bc45d845ecd0c39f9807786c5632e5f4e09e`.
The final exact34 consists of the retained exact32 plus the two source/test paths.

| Path | Pre SHA-256 | Required post SHA-256 |
|---|---|---|
| `scripts/generate_catalog.py` | `fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b` | `6a04502d0ef35e69225a5cb1fbd652c18db4d23814219c0e0cdb27792735b9b6` |
| `tests/integration/test_catalog_drift_detection.py` | `72e57f9ed304e358a977c514e1baa2648af155bea48b93bda00d2799322d9fa8` | `820e4f3bd5b299f341e511e15ecb0de2de7a3e49b28a68f1aa83eabd5aee791d` |
| `docs/catalog/MODULE_REGISTRY.json` | `9447544840c4f526d1d39769b63b84c4223ce689e2061e36a9416f9a4a741013` | `1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727` |
| `docs/catalog/MODULE_CATALOG.md` | `49a082972cbd4955e5932ed39f90390cb3bf281ca34dbe5a988498d2f9aaf995` | `32fe4ecbb7f7b493ba1536975d81aa95a895ca1424309dd580f232b8ee1bb484` |

`knowledge/manifest.json` remains immutable at
`cbf115da32e5ad9418f1d91678d2ec2f875e174ee434f5762648325f63da4f80`.
All A18 output/archive/suffix/link/line bindings remain mandatory.

## Exact atomic repair

Use one `apply_patch` containing only these changes:

```diff
--- a/scripts/generate_catalog.py
+++ b/scripts/generate_catalog.py
@@
-            json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
+            json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
@@
-        CATALOG_MD_PATH.write_text(render_markdown(registry), encoding="utf-8")
+        CATALOG_MD_PATH.write_text(render_markdown(registry), encoding="utf-8", newline="\n")
--- a/tests/integration/test_catalog_drift_detection.py
+++ b/tests/integration/test_catalog_drift_detection.py
@@
-    registry_backup = REGISTRY_PATH.read_text(encoding="utf-8")
-    markdown_backup = CATALOG_MD_PATH.read_text(encoding="utf-8")
+    registry_backup = REGISTRY_PATH.read_bytes()
+    markdown_backup = CATALOG_MD_PATH.read_bytes()
@@
-        REGISTRY_PATH.write_text(registry_backup, encoding="utf-8")
-        CATALOG_MD_PATH.write_text(markdown_backup, encoding="utf-8")
+        REGISTRY_PATH.write_bytes(registry_backup)
+        CATALOG_MD_PATH.write_bytes(markdown_backup)
```

Then run the reviewed all-reads-before-any-write exact-two binary CRLF-to-LF
normalization. No manifest, status, context or other edit is permitted.

## One ordered invocation

Use actual outer timeout >=600 seconds and `PYTHONUNBUFFERED=1`; run once,
stop first failure, no retry:

1. verify dynamic A24 topology/ASCII R2 digest, artifact/prehash/exact32/
   stable30/protected28/immutable bindings and staged0;
2. apply the exact atomic two-source patch once;
3. normalize exact-two catalog bytes once;
4. assert all four posthashes, final exact34, protected28 and staged0;
5. run focused catalog-drift tests once;
6. project Knowledge validator once;
7. focused Knowledge Pack suite once;
8. catalog check once;
9. full non-live pytest once;
10. remaining session/repository/JSON/YAML/contract/import-I/O/secret/diff gates;
11. final exact34/exact4/protected28/posthash/continuity audit.

No provider/network/remote-ingest/POST call, alternate fix, BUILD commit,
self-review, FREEZE, waiver, debt or later-lane expansion is authorized.
Independent review, authority checkpoint and fresh exact A24 R2 are mandatory.
