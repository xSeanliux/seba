.PHONY: check test typecheck lint fmt format install uninstall

# Install the `seba` CLI globally and link the seba-tutor skill into Claude Code.
install:
	uv tool install --force .
	mkdir -p $(HOME)/.claude/skills
	ln -sfn $(CURDIR)/skills/seba-tutor $(HOME)/.claude/skills/seba-tutor
	@echo "installed — run 'claude' and ask to study, or /seba-tutor"

# Remove both.
uninstall:
	-uv tool uninstall seba
	-rm -f $(HOME)/.claude/skills/seba-tutor

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
