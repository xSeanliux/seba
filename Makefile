.PHONY: check test typecheck lint fmt format install uninstall

# Install the `seba` CLI globally and link the seba-tutor skill into Claude Code.
install:
	./scripts/install.sh

# Remove both.
uninstall:
	./scripts/uninstall.sh

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
