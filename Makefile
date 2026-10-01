.PHONY: check test typecheck lint fmt format docs-gen docs-check

# Run every CI check locally.
check: lint fmt typecheck docs-check test

test:
	uv run pytest -q

typecheck:
	uv run ty check src

lint:
	uv run ruff check .

# CI gate: fails if anything is unformatted.
fmt:
	uv run ruff format --check .

# Dev convenience: apply formatting in place.
format:
	uv run ruff format .

# Regenerate the CLI reference from the code.
docs-gen:
	./scripts/check-doc-gen.sh gen

# CI gate: fails if docs/cli.md drifts from src/seba/cli.py.
docs-check:
	./scripts/check-doc-gen.sh check
