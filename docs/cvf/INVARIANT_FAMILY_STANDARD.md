# CVF Invariant Family Standard

Provider-neutral, repository-native contract for invariant-family reasoning
(tranche `CROSS-AGENT-INVARIANT-LEARNING-2026-08-22`). This guide is
human-readable semantics and procedure only; it is not the semantic owner of
any family. See `docs/decisions/DESIGN_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md`
and `docs/specs/CROSS_AGENT_INVARIANT_LEARNING_SPEC.md` for the full design
record.

## Why this exists

Repeated P4-B repair rounds closed each reviewer-named probe while an
adjacent member of the same invariant family stayed open, because prose
requirements were translated into individual test conditions rather than a
complete outcome/fact/counter family. This standard converts that lesson into
a machine-checkable contract so every human and agent follows the same
method, independent of chat history or model identity.

## The four normative layers

1. **This guide** — semantics, applicability and role procedure (no
   per-outcome rules).
2. **`docs/cvf/invariants/invariant-family.schema.json`** — closed JSON
   Schema (Draft 2020-12) for the matrix format.
3. **`docs/cvf/invariants/registry.json`** — the exact list of registered
   family ids, matrix paths, owners, applicability and lifecycle.
4. **One JSON matrix per registered family** — the sole semantic source for
   that family's outcomes, fields, relations, mutations and ownership
   bindings.

Point to a matrix by family id and canonical digest; never copy its content
into another document.

## Applicability

A new or materially changed R2/R3 tranche must register a family when at
least one trigger applies (see SPEC R1 for the exact list): shared receipt/
model contracts across outcomes, outcome-controlled field presence, exact
counter relations, multiple validator surfaces for one contract, coupled
prompt/schema or contract/fixture artifacts, or a prior finding exposing an
adjacent family member. Otherwise the SPEC records `NOT_APPLICABLE` with a
reason. Legacy tranches are not retrofitted merely by installing this
mechanism; registration becomes mandatory only when their triggered surface
is materially changed.

## Role procedure

- `SPEC_AUTHOR` declares the family id (or `NOT_APPLICABLE`) and states the
  matrix's independent contract source before any adapter code exists.
- `WORK_ORDER_AUTHOR` and `REVIEWER` complete the shared
  `docs/templates/INVARIANT_FAMILY_PROOF.md` section, referencing matrix id
  and digest rather than restating rules.
- `IMPLEMENTATION_WORKER` materializes adapters against the pinned matrix
  digest; a matrix change invalidates the pin and requires review.
- `REVIEWER` independently recomputes the matrix digest, reruns the full
  corpus, samples at least one raw emitted positive per outcome, and verifies
  no matrix expectation was derived during BUILD.

## What the guard proves — and does not

`scripts/check_invariant_families.py` is a read-only CLI over
`scripts/invariant_family_contract.py`. It depends only on the Python
standard library plus `jsonschema` (already present in this repository's
stable runtime); it makes no provider, network, install, database, or
dynamic-import action, and it never infers BUILD authority from Git tracking
state. It validates closed registry and matrix structure (both schema-level
via `jsonschema.Draft202012Validator` and Python-level semantic uniqueness),
duplicate JSON keys, path safety, registry/matrix identity and exact
file-set agreement, outcome/shape/field/relation/mutation completeness, and
real ownership-binding enforcement (owner/consumer path safety plus
per-strategy proof, including `CANONICAL_DIGEST` recomputation).

The guard and its conformance tests do not claim to discover an undeclared
semantic duplicate anywhere in arbitrary source code, and they do not prove
that any AI agent read or followed this guidance — only a separately
authorized bounded live checkpoint can support that narrower claim (see
`docs/decisions/DESIGN_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md` §11).

## Where to look

- Registry: `docs/cvf/invariants/registry.json`
- Matrix schema: `docs/cvf/invariants/invariant-family.schema.json`
- Bootstrap synthetic matrix: `docs/cvf/invariants/synthetic-terminal-outcome.json`
- Shared proof template: `docs/templates/INVARIANT_FAMILY_PROOF.md`
- Guard CLI: `scripts/check_invariant_families.py`
- Contract module: `scripts/invariant_family_contract.py`
