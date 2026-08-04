# Work Order Amendment 28 — Manifest Pin Indentation Repair

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-28-2026-08-04`
- Consumed A27 SHA-256: `03dc3ed14e163f645ba4f6697bff5982d7f1748fa10b7230ea59b16ec2be1a90`
- A27 authority / R2 checkpoints: `b2a593df9e999476f97125cf9eecf7aa8bfc5711` / `bbf02b674ec097c96351f7c6c13907e7dd87535a`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Calls: `0 provider / 0 network / 0 remote-ingest`

## Trigger and retained stop truth

A27 preflight passed. Its atomic exact-two patch produced the required
`IMPLEMENTATION_STATUS.json` SHA-256
`18b21d8d263ff0518389ab413550b006661d9fabee83cb373320235a6d9ab404`.
The immediate post-patch assertion then failed before every later gate because
the manifest pin line was emitted with eight leading spaces instead of the
existing ten. The pin value is correct and unique, JSON remains valid, exact35,
protected31 and staged0 remain intact. There was no retry and no provider,
network or remote-ingest call. A27 and its fresh R2 are consumed.

## Exact one-path scope

A28 authorizes exactly one already-dirty repair path while final candidate
scope remains exact35:

1. `knowledge/manifest.json`.

All other exact35 paths are byte-protected. Excluding canonical memory, active
handoff and the one repair path leaves exact32 protected paths with ordinal
manifest SHA-256:

`a23aa562f08c2154c96d3b7664589c1c05c1861e77eaab23b2074b3020673cca`

| Binding | SHA-256 |
|---|---|
| Manifest pre | `1988ab40737f9f6e2e695c145c2c7a197962b902211f963ef76a8eec2acfbd46` |
| Manifest required post | `251ca93f47a6527a0d941b7cbd371130a041fb21154ab269a05153b7751844a4` |
| Stable33 pre | `a480733e3565d3ed6b51773a0fef1e725025618afeb176e266ebfae0ad76d7a2` |
| Stable33 required post | `f6ed2c05f7db2737d5d668568eaaf0ea93e22dd66ba19120b10330aab27ee5ff` |

## Exact repair

Use one atomic `apply_patch` changing only two leading ASCII spaces:

```diff
-        "sha256": "18b21d8d263ff0518389ab413550b006661d9fabee83cb373320235a6d9ab404"
+          "sha256": "18b21d8d263ff0518389ab413550b006661d9fabee83cb373320235a6d9ab404"
```

The line must have exactly ten leading ASCII spaces after repair. No value,
field, entry, ordering, line ending or other byte may change.

## One ordered invocation

After independent authorization review, pushed authority checkpoint and fresh
exact A28 R2, `REPAIR_WORKER` runs once, stops first failure and never retries:

1. verify dynamic authority/R2 topology, artifacts, staged0, exact35, manifest
   pre-hash, stable33 pre-hash, protected32 and exact eight-space/ten-space
   occurrence counts;
2. apply the exact one-path/two-space patch once;
3. assert manifest post-hash, exact ten-space/zero eight-space occurrence,
   exact35, protected32, post-stable33 and staged0;
4. resume A27 never-run gates exactly once: both JSON parses, project Knowledge
   validator, focused Knowledge Pack suite, session, file-size, repository,
   secret, diff and final audits.

No provider/network/remote-ingest/POST call, status/source/test/catalog/fixture
edit, full-suite or Refinery-suite rerun, alternate fix, BUILD commit,
self-review, FREEZE, waiver or later-lane action is authorized. Any first
failure consumes the invocation and requires a fresh reviewed amendment/R2.

