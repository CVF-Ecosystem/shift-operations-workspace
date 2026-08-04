# Amendment 18 — Frozen Execution Sheet

Status: `PENDING_INDEPENDENT_REVIEW`. This sheet is normative. Copy commands
verbatim, run once in order, and stop at the first non-zero result. PowerShell
control grammar is prohibited after preflight. Calls remain zero.

## Frozen atomic repair payload

Invoke `apply_patch` exactly once with this payload:

```diff
*** Begin Patch
*** Update File: packages/refinery-bridge/src/refinery_bridge/output_models.py
@@
     @model_validator(mode="after")
     def valid_result(self) -> "RefineryResultV1":
+        validate_safe_string(self.source_owner_id)
+        validate_safe_string(self.source_link)
         if tuple(receipt.stage for receipt in self.stage_receipts) != STAGE_ORDER:
*** Update File: packages/refinery-bridge/src/refinery_bridge/protection.py
@@
         and candidate.source_link == result.source_link
         and candidate.source_fingerprint == result.source_fingerprint
+        and candidate.normalization_rules_version == result.stage_receipts[1].control_version
+        and candidate.terminology_rules_version == result.stage_receipts[2].control_version
+        and candidate.classification_rules_version == result.stage_receipts[3].control_version
+        and candidate.redaction_rules_version == result.stage_receipts[5].control_version
         and candidate.quality_rules_version == result.quality_receipt.rules_version
@@
         receipt is not None
+        and receipt.route.sink_available is True
         and receipt.reason == expected
*** Update File: packages/refinery-bridge/src/refinery_bridge/pipeline.py
@@
     assert analysis is not None
+    public_match_ids = tuple(sorted(set(analysis.match_ids)))
     failures = {
@@
-                     ids=analysis.match_ids)
+                     ids=public_match_ids)
@@
-                 ids=analysis.match_ids)
+                 ids=public_match_ids)
*** Update File: packages/refinery-bridge/src/refinery_bridge/pipeline.py
@@
-                match_ids=analysis.match_ids,
-                match_count=len(analysis.match_ids),
+                match_ids=tuple(sorted(set(analysis.match_ids))),
+                match_count=len(set(analysis.match_ids)),
*** Update File: tests/unit/test_refinery_models.py
@@
 from pydantic import ValidationError
 
+from refinery_bridge.canonical import candidate_fingerprint
@@
 def test_no_candidate_disposition_binds_first_failure() -> None:
@@
     with pytest.raises(ValidationError):
         RefineryResultV1.model_validate(dumped)
+
+
+def test_public_results_reject_version_route_and_provenance_drift() -> None:
+    ready = refine(payload(), controls(), dedupe_context=empty_context(), quarantine_route=route())
+    assert isinstance(ready, RefineryResultV1)
+    dumped = ready.model_dump()
+    dumped["context_candidate"]["normalization_rules_version"] = "normalization-v2"
+    dumped["candidate_fingerprint"] = candidate_fingerprint(
+        dumped["context_candidate"]
+    ).model_dump()
+    with pytest.raises(ValidationError):
+        RefineryResultV1.model_validate(dumped)
+
+    quarantined = refine(payload("QC03 stopped hồi 11h40"), controls(), dedupe_context=empty_context(), quarantine_route=route())
+    assert isinstance(quarantined, RefineryResultV1)
+    dumped = quarantined.model_dump()
+    dumped["quarantine_receipt"]["route"]["sink_available"] = False
+    with pytest.raises(ValidationError):
+        RefineryResultV1.model_validate(dumped)
+
+    fallback = refine(payload(), controls(), dedupe_context=None, quarantine_route=route(available=False))
+    assert isinstance(fallback, RefineryResultV1)
+    for field, unsafe in (("source_owner_id", " owner "), ("source_link", "https://u:p@example/x")):
+        dumped = fallback.model_dump()
+        dumped[field] = unsafe
+        with pytest.raises(ValidationError):
+            RefineryResultV1.model_validate(dumped)
*** Update File: tests/unit/test_refinery_canonical.py
@@
+from datetime import datetime, timezone
 import hashlib
@@
-from refinery_bridge.canonical import (
+from pydantic import ValidationError
+
+from refinery_bridge.canonical import (
     candidate_fingerprint,
     canonical_json_bytes,
     collision_suspected,
+    dedupe_content_fingerprint,
@@
-from refinery_bridge.input_models import SourceFingerprintV1
+from refinery_bridge.input_models import DedupeRecordV1, SourceFingerprintV1
@@
 def test_collision_predicate_complete_vectors() -> None:
@@
     assert not collision_suspected(base, neither)
+
+
+def test_all_typed_fingerprints_have_independent_golden_bytes() -> None:
+    source_bytes = "Tiếng Việt".encode("utf-8")
+    source = source_fingerprint("Tiếng Việt")
+    assert (source.sha256, source.sha512, source.byte_length) == (
+        hashlib.sha256(source_bytes).hexdigest(), hashlib.sha512(source_bytes).hexdigest(), len(source_bytes)
+    )
+    preimage = {"schema_version": "1.0", "value": "x"}
+    golden = b'{"schema_version":"1.0","value":"x"}'
+    for typed in (dedupe_content_fingerprint(preimage), candidate_fingerprint(preimage)):
+        assert (typed.sha256, typed.sha512, typed.byte_length) == (
+            hashlib.sha256(golden).hexdigest(), hashlib.sha512(golden).hexdigest(), len(golden)
+        )
+    with pytest.raises(ValidationError):
+        DedupeRecordV1(
+            scope_id="scope", prior_source_id="prior",
+            observed_at=datetime(2026, 7, 21, tzinfo=timezone.utc),
+            source_fingerprint=candidate_fingerprint(preimage),
+        )
*** Update File: tests/unit/test_refinery_pipeline.py
@@
 from datetime import datetime, timezone
 
+import pytest
+from pydantic import ValidationError
@@
 def test_redaction_and_sensitivity_escalation_are_safe() -> None:
@@
     assert "<redacted:credential>" in result.context_candidate.redacted_normalized_text
+
+
+def test_dedupe_edges_selection_and_permutation_are_deterministic() -> None:
+    current = payload()
+    bounds = empty_context()
+    source = source_fingerprint(str(current["raw_text"]))
+    earlier = DedupeRecordV1(
+        scope_id="scope-1", prior_source_id="z-earlier",
+        observed_at=bounds.window_start, source_fingerprint=source,
+    )
+    later = DedupeRecordV1(
+        scope_id="scope-1", prior_source_id="a-later",
+        observed_at=bounds.window_end, source_fingerprint=source,
+    )
+    with pytest.raises(ValidationError):
+        DedupeContextV1(
+            scope_id="scope-1", window_start=bounds.window_start,
+            window_end=bounds.window_end,
+            records=(earlier.model_copy(update={"observed_at": bounds.window_start.replace(year=2025)}),),
+        )
+    with pytest.raises(ValidationError):
+        DedupeContextV1(
+            scope_id="scope-1", window_start=bounds.window_start,
+            window_end=bounds.window_end,
+            records=(later.model_copy(update={"observed_at": bounds.window_end.replace(year=2027)}),),
+        )
+    outputs = []
+    for records in ((later, earlier), (earlier, later)):
+        result = refine(
+            current, controls(),
+            dedupe_context=bounds.model_copy(update={"records": records}),
+            quarantine_route=route(),
+        )
+        assert isinstance(result, RefineryResultV1)
+        assert result.disposition == Disposition.NO_CANDIDATE_DUPLICATE
+        assert result.duplicate_receipt is not None
+        assert result.duplicate_receipt.selected_prior_source_id == "z-earlier"
+        assert result.duplicate_receipt.match_ids == ("a-later", "z-earlier")
+        outputs.append(result.model_dump_json())
+    assert outputs[0] == outputs[1]
*** Update File: tests/unit/test_refinery_adversarial.py
@@
 def test_stage_unavailable_is_typed_and_fail_stop(monkeypatch: pytest.MonkeyPatch) -> None:
@@
     assert result.disposition == Disposition.NO_CANDIDATE_FALLBACK
+
+
+def test_disclosure_matrix_excludes_values_from_union_receipt_log_and_snapshot(
+    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
+) -> None:
+    secret = "ac07-matched-secret"
+    invalid = {**payload(secret), "source_link": " unsafe "}
+    first = run(invalid)
+    second = run(invalid)
+    assert isinstance(first, PreAdmissionRejectionV1)
+    assert first.model_dump_json() == second.model_dump_json()
+    assert secret not in first.model_dump_json()
+
+    broken = controls().model_dump()
+    broken["terminology_map"] = {"a": "b", "b": "a"}
+    with pytest.raises(ValidationError):
+        ControlBundleV1.model_validate(broken)
+    caplog.set_level(logging.DEBUG)
+    monkeypatch.setattr(
+        pipeline_module, "conflict_reason",
+        lambda *_: (_ for _ in ()).throw(RuntimeError(secret)),
+    )
+    failed = run(payload(secret))
+    assert isinstance(failed, RefineryResultV1)
+    surfaces = (
+        failed.model_dump_json(), failed.stage_receipts[4].model_dump_json(),
+        json.dumps(failed.model_dump(mode="json"), sort_keys=True), caplog.text,
+    )
+    assert all(secret not in surface for surface in surfaces)
*** Update File: IMPLEMENTATION_STATUS.json
@@
-    "governance_disposition": "BUILD_CANDIDATE_PENDING_INDEPENDENT_REVIEW — one R2-authorized invocation bound to Work Order 3a2bf12e and exact 26 paths.",
-    "authority_commits": "SPEC/Work Order authorization 72a712d; fresh R2 acknowledgment checkpoint b93e403.",
+    "governance_disposition": "BUILD_REPAIR_IN_PROGRESS — final independent review CHANGES_REQUIRED; Amendment 18 authorizes exact9 repairs within final exact32 dirty BUILD/continuity paths.",
+    "authority_commits": "Original SPEC/Work Order authority 72a712d/b93e403; final review 4f5099c5; A18 reviewed authority/R2 lineage is recorded in canonical continuity.",
@@
-    "changed_set": "Exactly 26 Work Order paths: deterministic local package, two fixtures, six test/helper paths, root/package metadata, contract, registry/catalog and this status surface.",
-    "evidence_status": "Pending ordered focused/full/repository gates and independent BUILD review. Provider/network/remote-ingest call count is fixed at zero.",
+    "changed_set": "Exactly 32 dirty BUILD/continuity paths after authorized knowledge additions and continuity/source-size repair; A18 repair touches exactly nine already-dirty paths.",
+    "evidence_status": "Retained A14 evidence: focused 53, catalog, full non-live 1593/128, session/repository/static/final gates PASS. Final review is CHANGES_REQUIRED (F1-F4); A18 repair and all post-repair gates are pending. Calls remain zero.",
@@
-    "next_governed_move": "Complete the authorized local gates, then independent BUILD review. No later lane activates from BUILD candidate status."
+    "next_governed_move": "After fresh A18 R2, apply only exact9 repair and ordered local gates; then obtain fresh independent BUILD re-review. No later lane activates."
*** Update File: knowledge/manifest.json
@@
-          "sha256": "0403f6170dbcab9fc912ea63b003f1d8325a71f36fc408887c23445cfcaacf10"
+          "sha256": "9d9d7d2ff387365ce018cc51de07a24d1eb3a21c08cb723feb3d74e114ae5eb6"
*** End Patch
```

## Exact test matrix

Exactly four new collected functions are added, one per authorized test file:

1. models: reject recomputed-fingerprint control-version drift, unavailable
   quarantine route, whitespace owner and URI-userinfo fallback link;
2. canonical: independently hash exact source/canonical bytes for all three
   typed constructors and reject candidate-to-source constructor substitution;
3. pipeline: accept both inclusive window edges, reject out-of-window, preserve
   chronological selection, lexical public ids and permutation-identical JSON;
4. adversarial: stable invalid-union bytes plus no matched value in union,
   receipt, sanitized exception result, log or serialized snapshot, with a
   control-construction failure in the same matrix.

Baseline 53 plus exactly four new functions requires exactly 57 collected.

## Exact orchestration

Run this exact preflight block once before the atomic patch. The canonical
state's `p3a_amendment_18_authority.artifacts` map is the checkpoint-owned
lineage binding and includes every Work Order/sheet/review artifact.

```powershell
git merge-base --is-ancestor HEAD origin/main
git merge-base --is-ancestor origin/main HEAD
git diff --cached --quiet
$env:PYTHONPATH='packages/refinery-bridge/src;tests/unit'
@'
import hashlib, json, re, subprocess
from pathlib import Path
state=json.loads(Path('SESSION/ACTIVE_SESSION_STATE.json').read_text(encoding='utf-8'))
auth=state['p3a_amendment_18_authority']
assert auth['freshR2Accepted'] is True
for path,digest in auth['artifacts'].items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
exact32=tuple(sorted(('IMPLEMENTATION_STATUS.json','SESSION/SESSION_MEMORY.md','SESSION/archive/SESSION_MEMORY_2026-07-22_TO_2026-07-31.md','SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md','SESSION/handoffs/archive/AGENT_HANDOFF_2026-08-03_P3A_REFINERY_FOUNDATION.md','docs/catalog/MODULE_CATALOG.md','docs/catalog/MODULE_REGISTRY.json','fixtures/refinery/normalized_message.json','fixtures/refinery/qualified_time_message.json','knowledge/PROJECT_CONTEXT.md','knowledge/manifest.json','packages/refinery-bridge/README.md','packages/refinery-bridge/contracts/refinery_contract.yaml','packages/refinery-bridge/pyproject.toml','packages/refinery-bridge/src/refinery_bridge/__init__.py','packages/refinery-bridge/src/refinery_bridge/canonical.py','packages/refinery-bridge/src/refinery_bridge/controls.py','packages/refinery-bridge/src/refinery_bridge/dedupe.py','packages/refinery-bridge/src/refinery_bridge/enums.py','packages/refinery-bridge/src/refinery_bridge/input_models.py','packages/refinery-bridge/src/refinery_bridge/normalization.py','packages/refinery-bridge/src/refinery_bridge/output_models.py','packages/refinery-bridge/src/refinery_bridge/pipeline.py','packages/refinery-bridge/src/refinery_bridge/protection.py','packages/refinery-bridge/src/refinery_bridge/receipt_models.py','pyproject.toml','tests/unit/_refinery_fixtures.py','tests/unit/test_refinery_adversarial.py','tests/unit/test_refinery_canonical.py','tests/unit/test_refinery_contract.py','tests/unit/test_refinery_models.py','tests/unit/test_refinery_pipeline.py')))
dirty=tuple(sorted(line[3:] for line in subprocess.check_output(['git','status','--porcelain=v1','-uall'],text=True).splitlines()))
assert dirty==exact32
def manifest(paths):
    data=b''.join(p.encode()+b'\0'+hashlib.sha256(Path(p).read_bytes()).hexdigest().encode()+b'\n' for p in sorted(paths))
    return hashlib.sha256(data).hexdigest()
stable=tuple(p for p in exact32 if p not in ('SESSION/SESSION_MEMORY.md','SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md'))
repair=('IMPLEMENTATION_STATUS.json','knowledge/manifest.json','packages/refinery-bridge/src/refinery_bridge/output_models.py','packages/refinery-bridge/src/refinery_bridge/pipeline.py','packages/refinery-bridge/src/refinery_bridge/protection.py','tests/unit/test_refinery_adversarial.py','tests/unit/test_refinery_canonical.py','tests/unit/test_refinery_models.py','tests/unit/test_refinery_pipeline.py')
assert manifest(stable)=='a50cebb5f4f4b2e6b6ae79bc56ebc70ac17c1fdd28b7242267a17e96e9c6a436'
assert manifest(tuple(p for p in stable if p not in repair))=='68cbd2430a85e1cafc5a79b46a72d6479a9c2b0a09629cfb387f78c78d7a6070'
pre={'packages/refinery-bridge/src/refinery_bridge/output_models.py':'62333c0a2fb0734e50b6a3b564af6303c3488db8e14ec4ac97b86db624b0bd9a','packages/refinery-bridge/src/refinery_bridge/protection.py':'d909c740e1a2e93859ca47a596c3dac2afaf740648044523b5d5e9de3e58a3f5','packages/refinery-bridge/src/refinery_bridge/pipeline.py':'69a55e2e7ad3b115176ae853f2756d3115f69aa12d0d1f7a6088ab15bb8371bf','tests/unit/test_refinery_models.py':'d99c48ef9fa7b8a29d762c28965ed719039adcd5d2ec5d15ceb2158703732dc8','tests/unit/test_refinery_canonical.py':'1d6ac9bdcec387e3c5dcd0e8d259275d5fd08d1b1be2aec6dddba31b99f22e88','tests/unit/test_refinery_pipeline.py':'8a2503128927333d33e439a29d562724b5ab45460ea882a6ce02a2a83a7f7104','tests/unit/test_refinery_adversarial.py':'1fc79f95f928656988736c10e9456550c61f2836a36662f344935ae87acdb768','IMPLEMENTATION_STATUS.json':'0403f6170dbcab9fc912ea63b003f1d8325a71f36fc408887c23445cfcaacf10','knowledge/manifest.json':'b7c0d5ccc70284a07453f80b37e51f8f5feed04dedea393497d9f16ef9ff2cc9'}
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pre.items())
ma=Path('SESSION/archive/SESSION_MEMORY_2026-07-22_TO_2026-07-31.md'); ha=Path('SESSION/handoffs/archive/AGENT_HANDOFF_2026-08-03_P3A_REFINERY_FOUNDATION.md')
assert hashlib.sha256(ma.read_bytes()).hexdigest()=='e218cbc150d03bd9c42f623f972e43ee33ee00b530882195e2c8c145ab918f86' and len(ma.read_text(encoding='utf-8').splitlines())==335
assert hashlib.sha256(ha.read_bytes()).hexdigest()=='c50d4bfd7c7745fa1bb3e5758eddb57c905f5d10fac5da5fda8707f63aee0d44' and len(ha.read_text(encoding='utf-8').splitlines())==394
memory=Path('SESSION/SESSION_MEMORY.md').read_text(encoding='utf-8'); handoff=Path('SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md').read_text(encoding='utf-8')
assert hashlib.sha256(memory[memory.index('Historical continuity from 2026-07-22'):].encode()).hexdigest()=='6a055880ab97e542fa122ff6cbe3025d993aa521d3b4e9098abf82fa97237ac6'
assert hashlib.sha256(handoff[handoff.index('The original P3-A intake/design/spec foundation'):].encode()).hexdigest()=='46f46615b06dff42a2c44b55321e30c862881146a58a98549fe06f06aaceb357'
assert len(memory.splitlines())<=600 and len(handoff.splitlines())<=600
for doc in (Path('SESSION/SESSION_MEMORY.md'),Path('SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md')):
    target=re.search(r'\]\((archive/[^)]+)\)',doc.read_text(encoding='utf-8')).group(1)
    assert (doc.parent/target).resolve().is_file()
'@ | python -
```

After the patch, run this exact direct probe once before focused pytest:

```powershell
$env:PYTHONPATH='packages/refinery-bridge/src;tests/unit'
@'
from datetime import datetime, timezone
from pydantic import ValidationError
from refinery_bridge.canonical import candidate_fingerprint, source_fingerprint
from refinery_bridge.input_models import DedupeRecordV1
from refinery_bridge.output_models import RefineryResultV1
from refinery_bridge.pipeline import refine
from _refinery_fixtures import controls, empty_context, payload, route
ready=refine(payload(),controls(),dedupe_context=empty_context(),quarantine_route=route())
d=ready.model_dump(); d['context_candidate']['normalization_rules_version']='normalization-v2'; d['candidate_fingerprint']=candidate_fingerprint(d['context_candidate']).model_dump()
try: RefineryResultV1.model_validate(d); raise AssertionError('CASE_1_FAIL')
except ValidationError: print('CASE_1_PASS')
q=refine(payload('QC03 stopped hồi 11h40'),controls(),dedupe_context=empty_context(),quarantine_route=route()); d=q.model_dump(); d['quarantine_receipt']['route']['sink_available']=False
try: RefineryResultV1.model_validate(d); raise AssertionError('CASE_2_FAIL')
except ValidationError: print('CASE_2_PASS')
f=refine(payload(),controls(),dedupe_context=None,quarantine_route=route(available=False))
for field,value in (('source_owner_id',' owner '),('source_link','https://u:p@example/x')):
 d=f.model_dump(); d[field]=value
 try: RefineryResultV1.model_validate(d); raise AssertionError('CASE_3_FAIL')
 except ValidationError: pass
print('CASE_3_PASS')
current=payload(); fp=source_fingerprint(str(current['raw_text'])); ctx=empty_context(); z=DedupeRecordV1(scope_id='scope-1',prior_source_id='z-earlier',observed_at=datetime(2026,7,21,10,tzinfo=timezone.utc),source_fingerprint=fp); a=DedupeRecordV1(scope_id='scope-1',prior_source_id='a-later',observed_at=datetime(2026,7,21,11,tzinfo=timezone.utc),source_fingerprint=fp); out=refine(current,controls(),dedupe_context=ctx.model_copy(update={'records':(a,z)}),quarantine_route=route()); assert out.duplicate_receipt.selected_prior_source_id=='z-earlier' and out.duplicate_receipt.match_ids==('a-later','z-earlier'); print('CASE_4_PASS')
'@ | python -
```

After the probe, run these exact direct commands once in this order:

```powershell
python -m pytest tests/unit/test_refinery_models.py tests/unit/test_refinery_canonical.py tests/unit/test_refinery_pipeline.py tests/unit/test_refinery_adversarial.py tests/unit/test_refinery_contract.py -q
python scripts/check_project_knowledge.py
python -m pytest tests/unit/test_project_knowledge_pack.py tests/integration/test_project_knowledge_ingest_rehearsal.py -q
python scripts/check_file_size.py
python scripts/generate_catalog.py --check
python -m pytest -q
python scripts/check_session_state.py
python scripts/testing/validate_repository.py
python -m json.tool IMPLEMENTATION_STATUS.json
python -m json.tool knowledge/manifest.json
python -c "import pathlib,yaml; files=('packages/refinery-bridge/contracts/refinery_contract.yaml','.cvf/policy.json'); [yaml.safe_load(pathlib.Path(p).read_text(encoding='utf-8')) for p in files]"
python -m pytest tests/unit/test_refinery_contract.py -q
@'
import re, subprocess
d=subprocess.check_output(['git','diff','--no-ext-diff'],text=True,encoding='utf-8')
assert not re.search(r'(?i)(sk-[a-z0-9]{20,}|bearer\s+eyj[a-z0-9._-]+|(?:api[_-]?key|token)\s*[:=]\s*["\x27][^"\x27]{16,})',d)
'@ | python -
git diff --check
```

After every listed gate, run this exact final audit once:

```powershell
git diff --cached --quiet
python -c "from pathlib import Path; import hashlib,json; pre={'packages/refinery-bridge/src/refinery_bridge/output_models.py':'62333c0a2fb0734e50b6a3b564af6303c3488db8e14ec4ac97b86db624b0bd9a','packages/refinery-bridge/src/refinery_bridge/protection.py':'d909c740e1a2e93859ca47a596c3dac2afaf740648044523b5d5e9de3e58a3f5','packages/refinery-bridge/src/refinery_bridge/pipeline.py':'69a55e2e7ad3b115176ae853f2756d3115f69aa12d0d1f7a6088ab15bb8371bf','tests/unit/test_refinery_models.py':'d99c48ef9fa7b8a29d762c28965ed719039adcd5d2ec5d15ceb2158703732dc8','tests/unit/test_refinery_canonical.py':'1d6ac9bdcec387e3c5dcd0e8d259275d5fd08d1b1be2aec6dddba31b99f22e88','tests/unit/test_refinery_pipeline.py':'8a2503128927333d33e439a29d562724b5ab45460ea882a6ce02a2a83a7f7104','tests/unit/test_refinery_adversarial.py':'1fc79f95f928656988736c10e9456550c61f2836a36662f344935ae87acdb768','IMPLEMENTATION_STATUS.json':'0403f6170dbcab9fc912ea63b003f1d8325a71f36fc408887c23445cfcaacf10','knowledge/manifest.json':'b7c0d5ccc70284a07453f80b37e51f8f5feed04dedea393497d9f16ef9ff2cc9'}; assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h for p,h in pre.items()); assert hashlib.sha256(Path('IMPLEMENTATION_STATUS.json').read_bytes()).hexdigest()=='9d9d7d2ff387365ce018cc51de07a24d1eb3a21c08cb723feb3d74e114ae5eb6'; m=json.loads(Path('knowledge/manifest.json').read_text(encoding='utf-8')); assert m['entries'][0]['sourcePins'][0]['sha256']=='9d9d7d2ff387365ce018cc51de07a24d1eb3a21c08cb723feb3d74e114ae5eb6'; assert all(len(Path(p).read_text(encoding='utf-8').splitlines())<=300 for p in pre if p.endswith('.py'))"
python -c "from pathlib import Path; import hashlib; a=Path('SESSION/archive/SESSION_MEMORY_2026-07-22_TO_2026-07-31.md'); b=Path('SESSION/handoffs/archive/AGENT_HANDOFF_2026-08-03_P3A_REFINERY_FOUNDATION.md'); assert hashlib.sha256(a.read_bytes()).hexdigest()=='e218cbc150d03bd9c42f623f972e43ee33ee00b530882195e2c8c145ab918f86'; assert hashlib.sha256(b.read_bytes()).hexdigest()=='c50d4bfd7c7745fa1bb3e5758eddb57c905f5d10fac5da5fda8707f63aee0d44'; assert len(a.read_text(encoding='utf-8').splitlines())==335 and len(b.read_text(encoding='utf-8').splitlines())==394; assert len(Path('SESSION/SESSION_MEMORY.md').read_text(encoding='utf-8').splitlines())<=600 and len(Path('SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md').read_text(encoding='utf-8').splitlines())<=600"
@'
import hashlib, json, re, subprocess
from pathlib import Path
state=json.loads(Path('SESSION/ACTIVE_SESSION_STATE.json').read_text(encoding='utf-8'))
auth=state['p3a_amendment_18_authority']
exact32=tuple(sorted(auth['exact32Paths']))
repair=tuple(auth['repairPaths'])
dirty=tuple(sorted(line[3:] for line in subprocess.check_output(['git','status','--porcelain=v1','-uall'],text=True).splitlines()))
assert dirty==exact32
stable=tuple(p for p in exact32 if p not in ('SESSION/SESSION_MEMORY.md','SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md'))
protected=tuple(p for p in stable if p not in repair)
data=b''.join(p.encode()+b'\0'+hashlib.sha256(Path(p).read_bytes()).hexdigest().encode()+b'\n' for p in sorted(protected))
assert len(repair)==9 and len(protected)==21
assert hashlib.sha256(data).hexdigest()=='68cbd2430a85e1cafc5a79b46a72d6479a9c2b0a09629cfb387f78c78d7a6070'
memory=Path('SESSION/SESSION_MEMORY.md').read_text(encoding='utf-8')
handoff=Path('SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md').read_text(encoding='utf-8')
assert hashlib.sha256(memory[memory.index('Historical continuity from 2026-07-22'):].encode()).hexdigest()=='6a055880ab97e542fa122ff6cbe3025d993aa521d3b4e9098abf82fa97237ac6'
assert hashlib.sha256(handoff[handoff.index('The original P3-A intake/design/spec foundation'):].encode()).hexdigest()=='46f46615b06dff42a2c44b55321e30c862881146a58a98549fe06f06aaceb357'
for doc in (Path('SESSION/SESSION_MEMORY.md'),Path('SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md')):
    target=re.search(r'\]\((archive/[^)]+)\)',doc.read_text(encoding='utf-8')).group(1)
    assert (doc.parent/target).resolve().is_file()
'@ | python -
```

No command may be replaced, retried or followed after a failure. No catalog
write, provider/network/remote-ingest/POST/helper call or BUILD commit.
