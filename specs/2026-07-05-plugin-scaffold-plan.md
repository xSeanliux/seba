# Seba — Claude Code plugin packaging plan

**Goal:** a user installs seba with one command —
`claude plugin marketplace add xSeanliux/seba && claude plugin install seba@seba`
— then opens `claude`, asks to study, and it works. No manual `uv tool
install`, no skill symlink, no PATH fiddling. Only machine prerequisite: `uv`
(which itself bootstraps Python + deps).

**Non-goals (v1 of the plugin):** PyPI publishing, Windows support, auto-installing
`uv` for the user (document it as a prerequisite instead).

## Why this is feasible (confirmed against the plugin docs)

- A plugin bundles arbitrary files under `${CLAUDE_PLUGIN_ROOT}` — so the whole
  `src/seba` package + `pyproject.toml` + `uv.lock` ship inside the plugin.
- `${CLAUDE_PLUGIN_ROOT}` (read-only bundle) and `${CLAUDE_PLUGIN_DATA}`
  (persistent, survives updates) are substituted in hook/MCP/skill-content
  contexts.
- There is **no** `/plugin install` hook; the idiomatic setup point is a
  **`SessionStart` hook** that runs once-per-version (diff-guarded) to prepare
  deps.
- Result: no global `seba` binary needed — the skill invokes the CLI via
  `uv run --project <data-dir> seba …`.

## The one real risk — validate FIRST (Phase 0 spike)

The open question: **when Claude follows a SKILL.md instruction and runs a Bash
command, are `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}` exported into that
shell?** Docs confirm substitution in hook/MCP *config* and in *skill content*
(the SKILL.md text itself is substituted), but the model's ad-hoc Bash tool env
is the unknown.

Spike (before building anything): a throwaway plugin with a skill whose SKILL.md
says "run `echo root=${CLAUDE_PLUGIN_ROOT} data=${CLAUDE_PLUGIN_DATA}`". Install
via `--plugin-dir`, trigger the skill, see whether the paths resolve.

- **If skill-content substitution works** (likely): bake `${CLAUDE_PLUGIN_ROOT}`
  into the SKILL.md command text directly — it's replaced at load time, before
  Claude ever runs it. The command becomes a literal absolute path.
- **If not:** the `SessionStart` hook (which *does* get the env vars) writes the
  resolved data-dir path to a fixed file (e.g. `~/.seba/plugin-data-path`), and
  the skill reads it. Fallback that never depends on the model's Bash env.

Everything below assumes the spike picks one of these; the rest is the same.

## Structure

Ship the plugin **from this same repo** (it's also a marketplace):

```
seba/
├── .claude-plugin/
│   ├── plugin.json           # NEW — plugin manifest
│   └── marketplace.json      # NEW — one-entry marketplace pointing at this repo
├── skills/seba-tutor/SKILL.md    # EDIT — CLI invocation (see Phase 3)
├── hooks/
│   └── seba-setup.sh         # NEW — diff-guarded `uv sync` into CLAUDE_PLUGIN_DATA
├── src/seba/ …               # bundled as-is (already here)
├── pyproject.toml, uv.lock   # bundled as-is
└── Makefile, README, docs/ … # unchanged
```

Bundling the package the repo already contains means zero duplication — the
plugin *is* the repo.

## Phases

### Phase 0 — Spike the invocation seam (above). Decide root-substitution vs hook-written-path. Blocks everything.

### Phase 1 — Manifest + marketplace
- `.claude-plugin/plugin.json`: `name: seba`, `version`, `description`,
  `skills` (points at `skills/seba-tutor`), `hooks`.
- `.claude-plugin/marketplace.json`: single plugin entry referencing this repo.
- Verify: `claude plugin marketplace add <local-path>` lists seba;
  `claude plugin install` succeeds and the skill shows up.

### Phase 2 — Dependency bootstrap (`hooks/seba-setup.sh`, wired as a `SessionStart` hook)
Diff-guarded so it only runs `uv sync` when the plugin version changes:
```sh
# pseudo — copy bundle to persistent data dir, sync once per version
diff -q "$CLAUDE_PLUGIN_ROOT/uv.lock" "$CLAUDE_PLUGIN_DATA/uv.lock" >/dev/null 2>&1 \
  || { cp -r "$CLAUDE_PLUGIN_ROOT"/{src,pyproject.toml,uv.lock} "$CLAUDE_PLUGIN_DATA"/ \
       && uv sync --frozen --project "$CLAUDE_PLUGIN_DATA"; }
```
- First session builds the venv (pydantic-core Rust wheel compiles once, caches).
- Assume `uv` is present (decision 1). A "uv not found → how to install" message
  is a later follow-up, not v1.
- Verify: fresh install → first session syncs; second session is a no-op.

### Phase 3 — Rework the skill's CLI invocation
- SKILL.md currently calls a global `seba …`. Change every call to
  `uv run --project "<DATA>" seba …` where `<DATA>` is whatever Phase 0 picked
  (baked `${CLAUDE_PLUGIN_DATA}` or the hook-written path).
- Keep the human-facing `seba` (via `make install`) working too — the skill's
  invocation is the only thing that changes, and both resolve to the same CLI.
- Verify: trigger the skill in a plugin-installed session; `seba status` / a full
  session run through the plugin path.

### Phase 4 — Learner-data separation (must not regress)
- `$SEBA_DATA_DIR` (default `~/seba-data`) is the **learner's** data — it must
  live outside the plugin, survive plugin update/uninstall. `CLAUDE_PLUGIN_DATA`
  holds only the venv/bundle. Confirm the setup hook never touches
  `$SEBA_DATA_DIR`, and uninstalling the plugin leaves `~/seba-data` intact.

### Phase 5 — End-to-end install test + docs
- On a clean checkout (or a machine without a global `seba`): install via
  marketplace, run a real session, confirm it works with no manual steps.
- README: add a "Install as a Claude Code plugin" section alongside the existing
  `make install` (which stays as the dev/local path).

## Decisions (resolved)
1. **Bundle deps via `uv sync`** (not PyPI/`uvx`). Assume `uv` is always present;
   the "uv not found" flag-and-explain message is a **later** follow-up, not v1.
   So Phase 2 does the plain `uv sync` without the missing-`uv` guard for now.
2. **Monorepo** — the plugin ships from this repo; no separate `seba-plugin` repo.
3. **`uv` is a hard prerequisite** — documented, not auto-installed. (Auto-install
   via `curl … | sh` is out of scope.)

## Success criteria
Fresh machine with `uv` present → `claude plugin install seba@seba` → open
`claude`, "let's study probability" → a real session runs end-to-end, learner
data lands in `~/seba-data`, with zero manual install steps.
