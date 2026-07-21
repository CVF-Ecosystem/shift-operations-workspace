.PHONY: bootstrap dev test validate catalog catalog-check size-check tree clean

bootstrap:
	python -m venv .venv
	. .venv/bin/activate && pip install -e '.[dev]'
	pnpm install

dev:
	docker compose up --build

test:
	python -m pytest

# Full repository validation, including the module-catalog consistency gate.
validate:
	python scripts/testing/validate_repository.py

# Regenerate the module catalog (metrics + MODULE_CATALOG.md) from the registry.
catalog:
	python scripts/generate_catalog.py --write

# Verify the module catalog without writing (CI / pre-commit gate).
catalog-check:
	python scripts/generate_catalog.py --check

# File size guard: flag files growing into technical debt.
size-check:
	python scripts/check_file_size.py --warn

tree:
	python scripts/maintenance/generate_tree.py

clean:
	rm -rf .venv node_modules apps/workspace-web/node_modules apps/workspace-web/dist
