#!/usr/bin/env python3
"""Select an eligible Alibaba free-quota model from the operator snapshot."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

DEFAULT_CATALOG = Path(__file__).with_name("model-quota-catalog.json")
REQUIRED_MODEL_FIELDS = {
    "model",
    "remaining",
    "total",
    "expires_on",
    "enabled",
    "priority",
}


class CatalogError(ValueError):
    """Raised when the quota catalog is malformed or has no eligible model."""


def load_catalog(path: Path = DEFAULT_CATALOG) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("provider") != "alibaba_dashscope":
        raise CatalogError("catalog provider must be 'alibaba_dashscope'")
    models = payload.get("models")
    if not isinstance(models, list) or not models:
        raise CatalogError("catalog models must be a non-empty list")
    for index, model in enumerate(models):
        if not isinstance(model, dict):
            raise CatalogError(f"models[{index}] must be an object")
        missing = REQUIRED_MODEL_FIELDS - model.keys()
        if missing:
            raise CatalogError(f"models[{index}] missing fields: {sorted(missing)}")
        try:
            expires_on = date.fromisoformat(str(model["expires_on"]))
        except ValueError as exc:
            raise CatalogError(f"models[{index}] has invalid expires_on") from exc
        if not str(model["model"]).strip():
            raise CatalogError(f"models[{index}] has an empty model code")
        if not isinstance(model["enabled"], bool):
            raise CatalogError(f"models[{index}] enabled must be boolean")
        for field in ("remaining", "total", "priority"):
            if not isinstance(model[field], int) or model[field] < 0:
                raise CatalogError(f"models[{index}] {field} must be a non-negative integer")
        if model["remaining"] > model["total"]:
            raise CatalogError(f"models[{index}] remaining exceeds total")
        model["_expires_on"] = expires_on
    return payload


def eligible_models(catalog: dict[str, Any], *, on_date: date) -> list[dict[str, Any]]:
    eligible = [
        model
        for model in catalog["models"]
        if model["enabled"]
        and model["remaining"] > 0
        and model["_expires_on"] > on_date
    ]
    return sorted(
        eligible,
        key=lambda model: (
            model["priority"],
            model["_expires_on"],
            -model["remaining"],
            model["model"],
        ),
    )


def select_model(path: Path = DEFAULT_CATALOG, *, on_date: date | None = None) -> str:
    run_date = on_date or date.today()
    candidates = eligible_models(load_catalog(path), on_date=run_date)
    if not candidates:
        raise CatalogError(f"no eligible Alibaba model on {run_date.isoformat()}")
    return str(candidates[0]["model"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--on-date", type=date.fromisoformat, default=date.today())
    parser.add_argument("--all", action="store_true", help="Print all eligible model codes")
    args = parser.parse_args()
    candidates = eligible_models(load_catalog(args.catalog), on_date=args.on_date)
    if not candidates:
        parser.error(f"no eligible Alibaba model on {args.on_date.isoformat()}")
    if args.all:
        for candidate in candidates:
            print(candidate["model"])
    else:
        print(candidates[0]["model"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
