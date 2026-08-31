# Independent SPEC Review — CVF Core Refresh Attempt 4 Carrier

- Tranche: `CVF-CORE-REFRESH-ATTEMPT-4-CARRIER-2026-08-31`
- Phase: `SPEC`
- Role: `INDEPENDENT_SPEC_REVIEWER`
- Risk: `R2`
- Disposition: `SPEC_REVIEW_CHANGES_REQUIRED`
- Findings: `CSR4-F1..CSR4-F5`
- Waivers: `NONE`
- BUILD authority: `NOT_GRANTED`
- External-effect authority: `NOT_GRANTED`

## Exact reviewed set

| Artifact | Raw SHA-256 |
|---|---|
| `docs/specs/CVF_CORE_REFRESH_ATTEMPT_4_CARRIER_2026-08-31_SPEC.md` | `c9f2246c575dc5565a2592ecbdc7cd538d4d9dfe28c05faa35b13f7b83bd7871` |
| `docs/cvf/invariants/cvf-core-refresh-attempt-4-carrier-modes-2026-08-31.json` | `a6c45d11d99ca2dc04e073ae36c1f97cc86e740e6027636795b1a4532e0bc454` |
| `docs/specs/cvf_core_refresh_attempt_4_carrier_2026_08_31_invariant_pin.py` | `c4bc49720697f790d131dd9bcd4f931a4351bb69667690ab21217e2793a80ca1` |
| `docs/cvf/invariants/registry.json` | `860bd0376e5915dfaf25ace042a27e4be3a8adeb8450ed7e37f0d2f92ea1e40d` |

The matrix raw/canonical file digest recomputed to
`a6c45d11d99ca2dc04e073ae36c1f97cc86e740e6027636795b1a4532e0bc454`.
The static pin resolves to that same digest. The collision-free registry entry
occurs exactly once and points to the reviewed matrix path.

Accepted lineage also recomputed byte-for-byte:

| Artifact | Raw SHA-256 |
|---|---|
| carrier INTAKE | `910ca62b6e7e13ea28cc5e28a1b867d80dd49f023a67cc18b3af425e962062e7` |
| carrier INTAKE review | `f431793766683b249a9eb17d75fc2784896c8e215cb9261d04003e1903815307` |
| accepted carrier DESIGN | `8f5ab09aac72a99ea706444e2f57d47a20a5bd928544cbccf799129333be3a95` |
| final carrier DESIGN review | `91d43cfa5e596312e3473bfbe8cbb1b170f13a81137dbeb352d52850c2ca07e7` |

## Checks that passed

- JSON duplicate-key parsing passed for the matrix and registry.
- `python scripts/check_invariant_families.py` returned
  `INVARIANT FAMILY CHECK: PASS`.
- Direct pin recomputation returned `PIN_PASS`.
- `python scripts/check_session_state.py` returned `SESSION STATE: PASS`.
- `git diff --check` passed for the exact SPEC-owned paths.
- The corpus contains exactly 77 unique ids. Sorting the ids, encoding them as
  compact JSON plus LF, and hashing those bytes reproduced
  `2d7c62eedb020f0406336817a788eae8bf2739515f31eca1459880159ab85f20`.
- The raw carrier tuples preserve the accepted order, place
  `--PublicRemote` directly before `--CarrierSha256`, and contain no
  `ProjectRemote` option or deferred value. The Project remote remains a
  separate parent-Work-Order config fact.
- The SPEC preserves the staged Work Order/review/external-authority hash
  graph, caller-side host contract, pinned tool resolution, closed Git argv
  forms, G1 semantic-refusal classification, finite observation boundary,
  negative-only carrier-tranche Execute boundary and two-path future BUILD
  ceiling.

The repository-wide `python scripts/check_file_size.py` was also run. It
reported only the already accepted upstream carrier DESIGN and DESIGN review
above 600 lines; none of the four exact SPEC-owned reviewed paths was named by
that failure. No exception or repair is granted by this review.

## Findings

### CSR4-F1 — corpus ids cannot derive the required mode and refusal code

SPEC R9 requires every id to be
`<MODE>__<EXPECTED_CODE>__<CASE>` and requires the harness to derive the
expected carrier mode and refusal code from the first two segments. All 77
matrix ids violate the exact mode domain: their first segments are uppercase
or category labels such as `AST`, `CONFIG`, `DRYRUN` and `EXECUTE`, while the
carrier modes are ordinal `ParseOnly`, `DryRun` and `Execute`. Independently
comparing the second segments with the matrix-owned refusal-code domains also
found 65 of 77 outside those domains. The pinned count and digest are
self-consistent, but they freeze a corpus that cannot implement its own
derivation contract.

Required repair: choose one collision-free id grammar that carries the exact
mode and expected matrix refusal code, update every affected id, recompute the
count/digest and pin, and make the SPEC unambiguous about any separate
category label. The repaired set must still cover all required static,
parser, Git/config, manifest, authority and negative-Execute operators.

### CSR4-F2 — required `execution_id` has no matrix-owned domain

The five carrier-receipt shapes require `execution_id`, but none declares a
field domain or conditional rule for it. The repository validator validates
only fields present in `fieldDomains`; an independent semantic probe therefore
accepted `{"INVALID":"OBJECT"}` as the `execution_id` of an otherwise valid
`PARSE_ONLY_ACCEPTED_VALID` object. This conflicts with the exact input
grammar and with DESIGN's `execution id or null` receipt boundary, and leaves
the sole semantic owner unable to reject wrong-type mutations.

Required repair: make the per-mode receipt value/domain explicit and
machine-enforced. If ParseOnly truly emits JSON null while Execute/DryRun use
the token grammar, extend the invariant contract/schema through an authorized
path or use closed shapes that can represent that distinction; do not leave a
required field outside `fieldDomains`.

### CSR4-F3 — future Execute shapes are partial fragments, not closed receipts

Every `LATER_PARENT_EXECUTE_PREFIX` shape requires only a small counter/status
subset. They omit the carrier envelope fields required by DESIGN section 7
and by the carrier shapes, including schema/family identity, execution id,
hash/check/observation/child-ledger digests and, in most E branches,
`filesystem_write_attempt_count`. Because SPEC R8 says an implementation
selects exactly one matrix shape with no prose fallback, the repository
validator accepted a seven-field `LATER_PARENT_EXECUTE_SUCCESS_VALID` object
as a complete exact shape. The matrix consequently cannot be the sole owner
of a canonical later-parent receipt.

Required repair: either define every later-parent outcome as a complete
closed receipt shape with all applicable domains/relations, or remove those
future shapes from this carrier family and defer them to the separately
governed parent invariant family. Do not rely on prose inheritance that the
matrix schema and SPEC expressly reject.

### CSR4-F4 — denied-candidate counters are not coupled

DESIGN requires a denied candidate to append exactly one non-launched entry,
increment `network_attempt_count` over the launched network-capable prefix,
leave `network_child_count` at the launched count, and make
`child_ledger_count` equal launched entries plus the refusal. The
`DENIED_NETWORK_CANDIDATE_VALID` shape declares independent enum ranges and
only one relation (`nonlaunched_refusal_count = 1`). A semantic probe was
accepted with DryRun, `child_ledger_count = 13`,
`network_attempt_count = 1`, `network_child_count = 3`, and
`local_child_count = 0`, an impossible prefix. This defeats the exact-counter
family trigger and one-sided relation mutation requirement.

Required repair: split denied candidates into finite reachable prefix shapes
or add machine-enforced relations that bind mode, local/network launched
counts, attempt count and ledger count for every permitted prefix. A cartesian
product of independent ranges is not an exact sequence contract.

### CSR4-F5 — matrix ownership does not bind the future carrier and validator

The matrix declares PowerShell receipt and independent Python validator
surfaces, and SPEC R8/R10 requires both future BUILD files to load/verify the
pinned matrix. Its only ownership consumer, however, is the static pin; its
`evidenceTestPaths` name only the generic invariant-framework tests. The exact
future carrier and carrier test are absent from ownership bindings. Because
the matrix becomes immutable after SPEC review and BUILD may change only
those two future paths, this omission cannot be repaired later without
violating phase ownership. The repository guard can therefore pass even if
the eventual carrier/test never consume this family.

Required repair: define enforceable pre-BUILD ownership bindings for the exact
future carrier/test consumers, using a strategy compatible with their future
absence at SPEC and enforceable after BUILD, or amend the invariant-family
contract in an independently reviewed prerequisite. The Work Order must be
able to prove that the frozen matrix owns both implementation validator
surfaces, not merely its digest pin.

## Invariant-family proof status

- Applicability: `TRIGGERED` / registered family
  `CVF-CORE-REFRESH-ATTEMPT-4-CARRIER-MODES-2026-08-31`.
- Matrix digest: independently recomputed as
  `a6c45d11d99ca2dc04e073ae36c1f97cc86e740e6027636795b1a4532e0bc454`.
- Mutation exclusions: `NONE`.
- Guard and pin evidence: PASS as recorded above.
- Raw emitted positive sampling and full implementation corpus: `NOT_RUN` and
  not claimable in SPEC because both BUILD paths remain absent and BUILD is
  unauthorized.
- Semantic completeness: FAIL under `CSR4-F1..CSR4-F5`; a structural guard
  PASS does not close these contract gaps.

## Final disposition and next move

Findings are `CSR4-F1..CSR4-F5`; waivers are `NONE`. The reviewed SPEC set
must not advance to WORK_ORDER.

The next eligible move is an orchestrator-authorized, consolidated same-phase
SPEC repair limited to:

1. `docs/specs/CVF_CORE_REFRESH_ATTEMPT_4_CARRIER_2026-08-31_SPEC.md`;
2. `docs/cvf/invariants/cvf-core-refresh-attempt-4-carrier-modes-2026-08-31.json`;
3. `docs/specs/cvf_core_refresh_attempt_4_carrier_2026_08_31_invariant_pin.py`;
4. `docs/cvf/invariants/registry.json` only if its entry must change.

A distinct independent reviewer must then recompute the exact replacement
hashes/digest and close every finding without waiver before any phase
transition. Work Order, BUILD, carrier source/test creation, carrier
execution, parent rebase movement, doctor/fetch/reconcile/network, provider
use, protected-assessment contact, fixture/P4-E/XR1 work, commit and push
remain unauthorized.
