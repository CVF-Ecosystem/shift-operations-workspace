# P4-A1 Governed Retrieval Amendment 5 Pre-Entry Restoration

Disposition: PRE_ENTRY_PROTECTED_RESTORATION_PASS

## Authority

- Amendment 5 SHA-256:
  `923742468475ebb57c3042021d6965db08b030ea745c054e07447628e9264897`
- Amendment 5 review SHA-256:
  `51ea1bbd3ba4b540dab76c8d0b0ff6488fcd12b68119ab95225ab0375cb819ac`
- HEAD before and after:
  `d878001b6a1a536218b2c66019243510ef3f7aec`
- Executor role: `PRE_ENTRY_SESSION_SYNC_STEWARD`
- Operation: exact-six CRLF/bare-CR to LF normalization only

## Exact-Six Result

| Path | Pre-image raw SHA-256 | Post-image raw SHA-256 | CRLF/bare CR after |
|---|---|---|---:|
| `CVF_SESSION/ACTIVE_SESSION_STATE.json` | `cf56f6da1a76d906260a78f76f5fdd5e6981c459050e86e96a6f88e526fe6aa0` | `dc7051824f62c06f6e95c6c0bd8352544ff4405f89c592363e92e3e8f28a67b9` | `0/0` |
| `SESSION/ACTIVE_SESSION_STATE.json` | `0408194104c14ad4ecfc55d34b2a041392cc4ae523aac9a0c3b315803581d499` | `c9c9e2e0bb46d6b2585ab091deb6a721e455babccc7f8d3eb407178056c59c69` | `0/0` |
| `SESSION/SESSION_MEMORY.md` | `14b6bd783e9f541835d7e6c75409f05074f860b5d8d2c8a82a83de7cfd0f865f` | `68c366677fb6a7a39229d371cc88acbf3ec27b247ff74f468070ffbded154e91` | `0/0` |
| `docs/implementation/EXECUTION_ROADMAP.md` | `f9e1c08d709a9627165a5fb44cbe9f16f9de5b54697c97ba72acfbf3d265be3e` | `e5fa3a5695f5817a7152e2ea983d456b38219ab1a79a5ba769a936016fd86f9e` | `0/0` |
| `knowledge/PROJECT_CONTEXT.md` | `9c0a81244582941daa5be71842e4f9e111489fdff09276eb35bde844b720773e` | `f2318222889f428f1b6951510c79e2889255e3e3594179076efbfdb54c363a34` | `0/0` |
| `knowledge/manifest.json` | `e2586fa4c3c89ecd5797743cfce0aa7f832e8ddc0f7913843759c810d5bb017a` | `e561a9bdb34cb9eb7949ec7fc6afc0ab9cc488d4984245d6c0d54f8974d963df` | `0/0` |

Every LF-normalized pre-image hash equaled its approved post-image before the
write. No content drift beyond line endings was present.

## Verification

- Protected 15-row aggregate:
  `bb180b1dfdd180d8d8350492d0803e5adb6eb08d4cc3385a4204f6a18b00eaa7`
- `python scripts/check_project_knowledge.py`: PASS
- `python scripts/check_session_state.py`: PASS
- Staged paths: `0`
- Commit/push operations: `0/0`
- Network/provider/product API/external database/Docker/PostgreSQL calls:
  `0/0/0/0/0/0`
- Test/runtime implementation edits: `0`
- Restoration writes outside exact six: `0`

## Release Boundary

Only the exact-eight Amendment 5 test-split worker may proceed next. The six
protected paths remain forbidden to that worker. Repair 4 semantic acceptance,
closure, commit, parking, provider work, P4-A, P4-A2, LPCI1-REF and deeper
project development remain unauthorized pending independent rereview.
