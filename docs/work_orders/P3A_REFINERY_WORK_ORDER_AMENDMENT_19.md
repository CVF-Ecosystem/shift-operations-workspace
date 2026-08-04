# Work Order Amendment 19 — Deterministic Catalog Repair and Remaining Gates

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-19-2026-08-04`
- Consumed A18 SHA-256: `2b11f8198a206a2c5df94e83b36ac6029c4829496d04717ef86058c483240d2a`
- A18 final authorization review SHA-256: `b9faf3544ac49615bf801c63503e658ac426b57ea9a0273bd85d4cfc3f4d4553`
- A18 authority / R2 acknowledgment checkpoints: `e9090f966f14f88a4de768e217c8ad4433dfcf29` / `8caaaa83a3cc46c1d81796f69968fb0a9327f713`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Calls: `0 provider / 0 network / 0 remote-ingest`

## Trigger and retained stop truth

A18 preflight passed. Its one atomic exact-nine patch completed, the direct
public-invariant/multi-match probe passed `4/4`, the explicit Refinery suite
passed `57`, project-knowledge validation passed, the focused Knowledge Pack
suite passed `86`, and the file-size guard passed. The next command,
`python scripts/generate_catalog.py --check`, returned non-zero because the
reviewed source/test repair added eight counted lines:

- total code LOC was stored as `20258` and recomputed as `20266`;
- `refinery-bridge` LOC was stored as `1561` and recomputed as `1569`;
- module count `22`, code-file count `225`, status totals and the other module
  metrics remained unchanged;
- the generated Markdown therefore no longer matched the registry.

Execution stopped at that first failure. Catalog write, full non-live pytest,
session/repository/JSON/YAML/contract/security/diff checks and the final audit
were `NOT_RUN`. No retry, provider, network or remote-ingest call occurred.
A18 and its fresh R2 are consumed. The retained dirty candidate remains exact
32 paths and has no BUILD commit, REVIEW_PASS, FREEZE or later-lane authority.

## Exact retained candidate binding

Using ordinal case-sensitive path sorting and UTF-8 records
`path + NUL + lowercase_file_sha256 + LF`:

- exact dirty paths: `32`;
- stable paths excluding the two volatile continuity front doors: `30`;
- stable-30 manifest SHA-256:
  `52a253f0b7e724f4d7b21d6324a02f801282d16b53fc5f072ba38598d21e02b3`;
- protected paths excluding the exact-three repair ceiling from stable30: `27`;
- protected-27 manifest SHA-256:
  `82aa69f30ba5ee7ab0ff7074293da47b252e0e5dd75417e705fa339f47d19475`;
- staged path count: `0`.

The exact-three pre-hashes are:

| Path | Pre-repair SHA-256 |
|---|---|
| `docs/catalog/MODULE_REGISTRY.json` | `1fb8b6e1638b69e6df3ababb823cc18e12238b3d0d2841e501074ff461c22d35` |
| `docs/catalog/MODULE_CATALOG.md` | `94e6c6e960d0b944edeecd34a971da7b6b3ebe70228eecd43b7cf4a761e13dd6` |
| `knowledge/manifest.json` | `49e7f64e58ceb530271db920551220908efefe1235f33d3a9984a6640507b0d1` |

Retain all nine A18 post-repair hashes byte-for-byte:

| Path | Retained SHA-256 |
|---|---|
| `IMPLEMENTATION_STATUS.json` | `9d9d7d2ff387365ce018cc51de07a24d1eb3a21c08cb723feb3d74e114ae5eb6` |
| `packages/refinery-bridge/src/refinery_bridge/output_models.py` | `7ea839ac3cad56ec7fa058a9e3ad7da05a6b0cd6b31b65a1ad5eb8e677260396` |
| `packages/refinery-bridge/src/refinery_bridge/pipeline.py` | `7b5bfc9374f59a636f9cf0dd963eb1d05ccee64a4bd96f50f98f5853d7891d58` |
| `packages/refinery-bridge/src/refinery_bridge/protection.py` | `9a37cdc0879ad087864aea6d027b1a5a623e2a77dab70f6cdef67e18421a9c53` |
| `tests/unit/test_refinery_adversarial.py` | `291c920f5b3d9c137522f6cb191bc348cdd832cb1b9a41cb3c89d885b4bee74d` |
| `tests/unit/test_refinery_canonical.py` | `9e3e552f0122b39aa568481303ebfe41b3b94eed9c3a975b300cd33698c3bed1` |
| `tests/unit/test_refinery_models.py` | `7af17012708ceead193bc35361e96665acf17cd3c886ca3fac9f72b9fffc3d89` |
| `tests/unit/test_refinery_pipeline.py` | `a25f0878eeb5ca6359885c25ba2798abee23b379dabd32c375dba5d210e4d518` |
| `knowledge/manifest.json` | repair-path pre-hash above; only the registry pin may change |

Retain the memory archive `335` lines / `e218cbc150d03bd9c42f623f972e43ee33ee00b530882195e2c8c145ab918f86`,
handoff archive `394` lines / `c50d4bfd7c7745fa1bb3e5758eddb57c905f5d10fac5da5fda8707f63aee0d44`,
memory suffix `6a055880ab97e542fa122ff6cbe3025d993aa521d3b4e9098abf82fa97237ac6`,
handoff suffix `46f46615b06dff42a2c44b55321e30c862881146a58a98549fe06f06aaceb357`,
resolving archive links and all four continuity/archive files at or below 600
lines. Authority/R2 updates may change only the volatile continuity preambles.

## Exact repair ceiling — three paths

Only these already-dirty paths may change:

1. `docs/catalog/MODULE_REGISTRY.json`;
2. `docs/catalog/MODULE_CATALOG.md`;
3. `knowledge/manifest.json`.

No source, test, status, project-context, roadmap, archive, contract, package,
fixture, dependency or other path may change. Final dirty scope remains exact
32. The generator source is immutable at SHA-256
`fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b`.

## Deterministic repair payload

Use the reviewed generator functions once with frozen
`generated_at = 2026-08-04T00:00:00+00:00`. This is the only catalog write:

```powershell
@'
import importlib.util, json
from pathlib import Path
p=Path('scripts/generate_catalog.py')
s=importlib.util.spec_from_file_location('catalog_gen',p)
g=importlib.util.module_from_spec(s); s.loader.exec_module(g)
r=g.load_registry(); assert not g.verify(r)
r=g.enrich_metrics(r,generated_at='2026-08-04T00:00:00+00:00')
g.REGISTRY_PATH.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
g.CATALOG_MD_PATH.write_text(g.render_markdown(r),encoding='utf-8')
'@ | python -
```

Then invoke `apply_patch` exactly once to replace only the project-context
registry pin in `knowledge/manifest.json`:

```diff
*** Begin Patch
*** Update File: knowledge/manifest.json
@@
-          "sha256": "1fb8b6e1638b69e6df3ababb823cc18e12238b3d0d2841e501074ff461c22d35"
+          "sha256": "1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727"
*** End Patch
```

Required post-hashes are:

| Path | Post-repair SHA-256 |
|---|---|
| `docs/catalog/MODULE_REGISTRY.json` | `1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727` |
| `docs/catalog/MODULE_CATALOG.md` | `32fe4ecbb7f7b493ba1536975d81aa95a895ca1424309dd580f232b8ee1bb484` |
| `knowledge/manifest.json` | `cbf115da32e5ad9418f1d91678d2ec2f875e174ee434f5762648325f63da4f80` |

The registry must report exactly `22` modules, `20266` code LOC, `225` code
files, status totals `contract-only=6, enforced=2, partial=8, stub=6`, and
`refinery-bridge` metrics `1569 / 11 / 11`. No other registry semantic field
may change except the frozen generated timestamp and those two LOC values.

## One ordered continuation

Run once, stop at the first non-zero command or contract failure, no retry:

1. verify pushed A19 authority/R2 lineage, bound A19/review hashes, empty staged
   set, exact32/stable30/protected27, exact-three pre-hashes, all A18
   retained hashes, generator hash and archive/suffix/link/line bindings;
2. run the deterministic catalog payload exactly once;
3. apply the fixed one-line knowledge-manifest patch exactly once;
4. assert exact-three post-hashes, exact registry semantics, exact32 path set,
   unchanged protected27/A18 repair outputs, and staged zero;
5. run `python scripts/check_project_knowledge.py` once;
6. run the two-file focused Knowledge Pack suite once;
7. run `python scripts/generate_catalog.py --check` once;
8. run `python -m pytest -q` once;
9. run session-state, repository validator, JSON/YAML, Refinery contract,
   forbidden import/I/O, secret and `git diff --check` gates once;
10. run a final exact32/exact3/protected27/post-hash/archive/suffix/link/line/
    staged audit once.

Retain without rerun: A18 probe `4/4`, Refinery `57`, pre-repair Knowledge Pack
validator/`86`, and file-size PASS. The failed A18 catalog check is not retried
or relabeled; A19 runs a new post-repair catalog check. No catalog CLI `--write`
is permitted in addition to the single frozen generator-function payload.

## Stop and claim boundary

No provider/network/remote-ingest/POST call, retry, alternate generator,
timestamp substitution, new helper, BUILD commit, self-review, FREEZE, waiver,
debt or later-lane expansion is authorized. PASS yields only a dirty exact32
local candidate pending fresh independent BUILD review.

Independent authorization review, a bounded partially staged authority
checkpoint, and fresh exact human R2 naming this Amendment SHA, exactly three
repair paths, final exact32 and zero provider/network/remote-ingest calls are
mandatory before continuation.
