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
- **No hooks.** Dep setup is **lazy, on-demand, inside the skill** — it runs only
  when the learner engages seba, never on unrelated `claude` sessions. `uv run`
  auto-syncs the venv from the bundled `uv.lock` before executing, so the first
  seba call of the first session builds deps and every later call is a fast
  up-to-date check. No `SessionStart` hook, no per-session overhead.
- Result: no global `seba` binary needed — the skill invokes the CLI via
  `uv run` (see the invocation seam below).

## The invocation seam — RESOLVED by the docs (no spike needed)

The earlier open question was whether the plugin path vars reach the CLI call.
The [plugins reference — Environment variables](https://code.claude.com/docs/en/plugins-reference.md#environment-variables)
settles it:

> All are substituted inline anywhere they appear in **skill content**, agent
> content, hook commands, monitor commands, and MCP or LSP server configs. All
> are also exported as environment variables to hook processes and MCP or LSP
> server subprocesses.

Three path vars: `${CLAUDE_PLUGIN_ROOT}` (read-only bundle), `${CLAUDE_PLUGIN_DATA}`
(persistent, for the venv — resolves to `~/.claude/plugins/data/<id>/`, created on
first reference), `${CLAUDE_PROJECT_DIR}` (project root). Plugin `user_config`
values also surface as `${user_config.KEY}` / `CLAUDE_PLUGIN_OPTION_<KEY>`.

**So: bake both path vars straight into the SKILL.md command text.** They
substitute to literal absolute paths at load time, before Claude runs anything —
no reliance on whether the var is exported into the model's ad-hoc Bash (it is
only guaranteed for hook/MCP subprocesses, not the model's Bash). The seba call
in the skill reads:

```
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --project "${CLAUDE_PLUGIN_ROOT}" seba …
```

- `--project "${CLAUDE_PLUGIN_ROOT}"` — run the bundled package (read-only, wiped
  on update; fine, nothing is written there).
- `UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv"` — put the venv in the
  **persistent** data dir so it survives plugin updates and isn't rebuilt every time.
- `uv run` auto-syncs that venv from the bundled `uv.lock` before running — the
  lazy, on-demand bootstrap. No hook.

A one-line wrapper (`bin/seba` in the bundle) can hide this so the skill just
calls `"${CLAUDE_PLUGIN_ROOT}/bin/seba" …` with `CLAUDE_PLUGIN_DATA` passed in;
decide during Phase 1.

Optional 5-minute confirmation spike (not a blocker): a throwaway plugin loaded
via `claude --plugin-dir ./env-test`, whose skill echoes the two vars, to eyeball
that substitution behaves as documented.

**Caveat — data separation:** uninstalling the plugin deletes `${CLAUDE_PLUGIN_DATA}`
(unless `--keep-data`). That's fine — it only holds the venv, which `uv run`
rebuilds on next use. The learner's `$SEBA_DATA_DIR` (`~/seba-data`) is a separate
user-level dir and is never touched.

## Structure

Ship the plugin **from this same repo** (it's also a marketplace):

```
seba/
├── .claude-plugin/
│   ├── plugin.json           # NEW — plugin manifest
│   └── marketplace.json      # NEW — one-entry marketplace pointing at this repo
├── skills/seba-tutor/SKILL.md    # EDIT — CLI invocation (see Phase 3)
├── bin/seba                  # NEW (optional) — wrapper: uv run w/ venv in PLUGIN_DATA
├── src/seba/ …               # bundled as-is (already here)
├── pyproject.toml, uv.lock   # bundled as-is
└── Makefile, README, docs/ … # unchanged
```

Bundling the package the repo already contains means zero duplication — the
plugin *is* the repo.

## Phases

### Phase 0 — Optional confirmation spike (not blocking; docs already answer it)
Load a throwaway `env-test` plugin via `claude --plugin-dir` whose skill echoes
`${CLAUDE_PLUGIN_ROOT/DATA}` and eyeball substitution. Skip if confident.

### Phase 1 — Manifest + marketplace (this repo *is* the plugin, monorepo)
- `.claude-plugin/plugin.json`: minimal — `name: seba` is the only required field;
  add `version`, `description`. `skills/` and inline/`hooks/hooks.json` hooks are
  auto-discovered. **Components live at the plugin root, not inside
  `.claude-plugin/`** — only `plugin.json`/`marketplace.json` go there.
- `.claude-plugin/marketplace.json` (this repo doubles as its own marketplace),
  modeled on caveman's:
  ```json
  {
    "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
    "name": "seba",
    "description": "…",
    "owner": { "name": "Sean Liu", "url": "https://github.com/xSeanliux" },
    "plugins": [{ "name": "seba", "source": "./", "category": "productivity" }]
  }
  ```
  `source: "./"` → the plugin is the repo root.
- Validate before loading: `claude plugin validate .`
- Install path for users: `claude plugin marketplace add xSeanliux/seba && claude plugin install seba@seba`.
- Verify: `claude plugin marketplace add <local-path>` lists seba; install succeeds; the skill shows up.

### Phase 2 — Lazy, on-demand dependency bootstrap (NO hook)
Bootstrap happens the first time the skill runs seba, not on session start.
`uv run` auto-syncs the venv from the bundled `uv.lock` before executing:
```sh
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" \
  uv run --project "${CLAUDE_PLUGIN_ROOT}" seba "$@"
```
- Code runs from the read-only bundle; the venv lives in persistent
  `${CLAUDE_PLUGIN_DATA}/venv` (survives plugin updates, not rebuilt each call).
- First seba call of the first session compiles deps (pydantic-core Rust wheel,
  once, cached); later calls are a fast uv up-to-date check.
- **Runs only when the learner engages seba** — zero cost on unrelated `claude`
  sessions. This is the whole reason to avoid a `SessionStart` hook.
- Optional: wrap the above in `bin/seba` (in the bundle) so the skill line stays
  short. Assume `uv` is present (decision 1); "uv not found" message is a later
  follow-up.

### Phase 3 — Rework the skill's CLI invocation
- SKILL.md currently calls a global `seba …`. Change every call to the Phase-2
  form (either the full `UV_PROJECT_ENVIRONMENT=… uv run --project "${CLAUDE_PLUGIN_ROOT}" seba …`
  or `"${CLAUDE_PLUGIN_ROOT}/bin/seba" …` with `CLAUDE_PLUGIN_DATA` passed in).
  Both `${…}` substitute at load into literal paths.
- Keep the human-facing global `seba` (via `make install`) working too — the
  skill's invocation is the only thing that changes; both resolve to the same CLI.
- Verify: trigger the skill in a plugin-installed session; `seba status` / a full
  session run through the plugin path.

### Phase 4 — Learner-data separation (must not regress)
- `$SEBA_DATA_DIR` (default `~/seba-data`) is the **learner's** data — it must
  live outside the plugin, survive plugin update/uninstall. `CLAUDE_PLUGIN_DATA`
  holds only the venv. Confirm nothing in the plugin touches `$SEBA_DATA_DIR`,
  and uninstalling the plugin leaves `~/seba-data` intact.

### Phase 5 — End-to-end install test + docs
- On a clean checkout (or a machine without a global `seba`): install via
  marketplace, run a real session, confirm it works with no manual steps.
- README: add a "Install as a Claude Code plugin" section alongside the existing
  `make install` (which stays as the dev/local path).

## Decisions (resolved)
1. **Bundle deps, resolved lazily by `uv run`** (not PyPI/`uvx`, not a
   `SessionStart` hook). Bootstrap runs only when the skill invokes seba. Assume
   `uv` is always present; the "uv not found" flag-and-explain message is a
   **later** follow-up, not v1.
2. **Monorepo** — the plugin ships from this repo; no separate `seba-plugin` repo.
3. **`uv` is a hard prerequisite** — documented, not auto-installed. (Auto-install
   via `curl … | sh` is out of scope.)

## Success criteria
Fresh machine with `uv` present → `claude plugin install seba@seba` → open
`claude`, "let's study probability" → a real session runs end-to-end, learner
data lands in `~/seba-data`, with zero manual install steps.
