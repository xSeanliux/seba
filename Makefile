.PHONY: check test typecheck lint fmt format

# Run every CI check locally.
check: lint fmt typecheck test

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
