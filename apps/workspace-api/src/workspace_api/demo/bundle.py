"""Pinned deployable synthetic records; no test-fixture runtime import."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

P5A2_DEMO_BUNDLE_SHA256 = "5a7f1dbc61fbdc40b4c201763c18c463902ea8d928ad105eddeff7b16a617cae"


def load_bundle() -> dict:
    path = Path(__file__).with_name("source_bundle_v1.json")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != P5A2_DEMO_BUNDLE_SHA256:
        raise ValueError("synthetic bundle integrity failure")
    bundle = json.loads(raw)
    if (bundle.get("bundle_version") != "P5A2-SOURCE-DEMO-DATA-1"
            or bundle.get("fixture_id") != "P5A2-SOURCE-DEMO-1"
            or bundle.get("instance_id") != "P5A2-SOURCE-DEMO-LOCAL-1"
            or bundle.get("actor_id") != "PUBLIC_ACTOR"
            or bundle.get("coverage_mode") != "SYNTHETIC_FIXTURE"
            or len(bundle.get("shifts", [])) != 36
            or len(bundle.get("assignments", [])) != 36
            or len(bundle.get("reports", [])) != 37):
        raise ValueError("synthetic bundle shape failure")
    return bundle
