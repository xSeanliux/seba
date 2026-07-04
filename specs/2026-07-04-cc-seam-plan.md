# Seba Claude-Code Seam Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Seba's Anthropic-API dialogue harness with Claude Code itself: the tutor dialogue runs inside the user's Claude Code session (Max subscription, zero marginal cost, ToS-clean), and Seba's deterministic half — store, scheduler, syllabus, validation, gates — is exposed as `seba` CLI subcommands that Claude Code calls mid-conversation, directed by a personal skill.

**Architecture:** The seam moves from "Python process holding an in-memory ToolHandler around an API loop" to "stateless CLI invocations sharing a durable pending-session file." `seba start` builds the agenda (context firewall unchanged) and writes `session.pending.yaml`; `seba grade/mint/concept` validate through the existing `ToolHandler` and persist incrementally; `seba end` enforces the session-end gate, applies the record (FSRS + syllabus), saves, and git-commits. Claude Code is the LLM half: it conducts the dialogue, grades per the rubric, and calls the scripts — instructed by `skills/seba-tutor/SKILL.md`. Crash resilience improves: every accepted outcome is already on disk, so the recovery/extract machinery is deleted along with the whole API layer.

**Tech Stack:** Python ≥3.12, uv, pydantic v2, py-fsrs (`fsrs`), typer, rich, pyyaml, pytest. `anthropic` is REMOVED.

## Global Constraints

- Repo: `~/Desktop/Projects/seba`. Branch from `init/v0-loop` (PR #2 head); this plan is PR #3, stacked on PR #2. Commit locally; do not push unless the user asks.
- Python ≥3.12; deps after Task 2 EXACTLY: `fsrs`, `pydantic>=2`, `rich`, `pyyaml`, `typer`; dev: `pytest`. `anthropic` must be gone from `pyproject.toml` and `uv.lock`.
- All schemas live in `src/seba/models.py`. No module defines its own dict shapes.
- Imports strictly downward: `cli → session → scheduler → store`; `syllabus` is a sibling used by `cli`/`store`. No circular imports.
- Grades: `again | hard | good | easy | skipped`. Concept statuses `unseen | in-progress | done`, forward one step only. `mint_item` cap 10/session. All unchanged from v0.
- Loud failures: malformed state files raise errors naming the file; CLI validation failures print the reason to stderr and exit non-zero; never silently default.
- Every test runs with zero network and no `ANTHROPIC_API_KEY`.
- Run tests with `uv run pytest`. Commit after every green test cycle, conventional-commit subjects.
- The pending-session file lives at `<data>/goals/<goal>/session.pending.yaml` inside the data repo. It may get swept into a `save_session` git commit for a *different* goal — accepted (plain-text state; harmless, even useful cross-machine).
- CLI session-command contract (the skill depends on these exact shapes — do not rename):
  - `seba start GOAL` → prints YAML with keys `agenda`, `subject_style`, `already_graded`, `ungraded_reviews`, `minted_so_far`; exit 0.
  - `seba grade GOAL ITEM_ID GRADE [--note TEXT]`
  - `seba mint GOAL --concept ID --type TYPE --front TEXT --back TEXT`
  - `seba concept GOAL CONCEPT_ID [--status started|completed] [--note TEXT]`
  - `seba end GOAL --summary TEXT --hint TEXT` (exit 1 + ungraded ids while gate unsatisfied)
  - `seba abandon GOAL [--discard]`
  - `seba new-goal NAME --subject SUBJECT --from-file PATH`
  - `seba status`

## Orchestrator briefing (read this first if you are the PM agent)

**Repo state at plan time (2026-07-04):** this plan is already committed on `init/v0-loop` (at `05cb94b`); the working tree is clean. PR #1 (`init/v0-foundation`→`main`) and PR #2 (`init/v0-loop`→`init/v0-foundation`) are open and unmerged on `github.com/xSeanliux/seba`. Create a new branch off `init/v0-loop` (suggested: `init/v0-cc-seam`), execute there, and open PR #3 with base `init/v0-loop` when done. Full test suite at plan time: 69 passed, `uv run pytest -q`.

**Worktree gotcha (bit every agent in PRs #1–2):** `isolation: worktree` subagents branch from the repo's default branch (`main`), NOT your working branch — their premises (existing files) won't exist. Every dispatch must open with: "run `git reset --hard <your-branch>` first, confirm `<key file>` exists." Include your branch name and current HEAD sha in each dispatch. Also: `.claude/` and `.superpowers/` are gitignored — if `git status` ever shows `.claude/worktrees/` as untracked, do NOT `git add` it.

**Merging worker output:** worker branches are named `worktree-agent-<id>`. Merge with `git merge --no-ff <branch> -m "merge: T<n> <title>"` in task-number order, run `uv run pytest -q` after each, then `git worktree remove --force .claude/worktrees/agent-<id>` and `git branch -D <branch>`.

**Task dependency DAG** (arrows = "needs merged first"):

```
init/v0-loop (8c147ed lineage, PR #2 head)
 ├─ T1 pending-session persistence     ── disjoint files ──┐
 ├─ T2 demolition + new-goal rewrite   ── disjoint files ──┼─ T3 session CLI commands
 │                                                          │    ├─ T4 integration test rewrite
 │                                                          │    └─ T5 SKILL.md + install + README
 └──────────────────────────────────────────────────────────┘
T6 dogfood — HUMAN-GATED, do not attempt; hand off to the user.
```

Safe parallel waves: **wave 1** = T1, T2 (file-disjoint by design — T1 creates `session/pending.py` + edits `models.py`/new test file; T2 only deletes/edits other files) · **wave 2** = T3 · **wave 3** = T4, T5 (T5 writes docs against the Global Constraints command contract; T4 tests through T3's commands).

**Design decisions already made (do not relitigate):**
1. API mode is DELETED, not kept as fallback (user's explicit call). `learn`, `extract`, `dialogue.py`, `recovery.py`, `make_send`, both session prompt files, the whole `synthesis/` module, `TerminalIO`, `config.model()/recovery_model()`, and the `anthropic` dep all go.
2. The `synthesis` module goes entirely: Claude Code drafts the syllabus YAML itself in-conversation (the drafting rules move into SKILL.md), and `new-goal --from-file` just validates + creates. The spec's human-edit hard gate becomes a SKILL.md instruction: show the drafted syllabus and get explicit learner approval before `new-goal`.
3. `ToolHandler` is reused UNCHANGED for validation (including its `fetch_source` branch — harmless, already tested). Resumed records are injected by attribute assignment (`handler.record = pending.record`), not a constructor change.
4. No transcript in CC mode. `save_session` gets the fixed placeholder string (see T3 `NO_TRANSCRIPT`). Claude Code's own session log is the transcript of record.
5. Skill is a personal skill: file lives in repo at `skills/seba-tutor/SKILL.md`; install = symlink into `~/.claude/skills/` + `uv tool install` for a global `seba` command. Install commands go in README; T6 (human) actually runs them.

**Working model:** one repo, sequential merges in task-number order, full `uv run pytest` after each merge; a red suite blocks the next wave. If a worktree agent starts from a stale base, it must `git reset --hard <this-plan's-branch>` first — tell it the branch name and HEAD sha in the dispatch.

**Worker prompt recipe:** give each worker its full task section + the Global Constraints block + nothing else. Interfaces blocks define what neighbors expect — workers must not rename anything listed there.

**Allowed deviation:** none silently. A worker whose "expect PASS" step fails after 2 fix attempts stops and reports the failing output verbatim; PM decides. Known live risk: T4's integration test runs against the real wall clock (see T4 notes) — the test is designed date-independent; if it flakes on a date boundary, that is a PM-level bug report, not a worker fix.

---

### Task 1: Pending-session persistence

**Files:**
- Modify: `src/seba/models.py` (append one model)
- Create: `src/seba/session/pending.py`
- Test: `tests/test_pending.py`

**Interfaces:**
- Consumes: `models.Agenda`, `models.SessionRecord`.
- Produces (T3 depends on these exact names):
  - `PendingSession(goal: str, agenda: Agenda, record: SessionRecord = SessionRecord(), started: date)` — in `models.py`.
  - `pending_path(data_dir: Path, goal: str) -> Path` — `<data>/goals/<goal>/session.pending.yaml`.
  - `load_pending(path: Path) -> PendingSession | None` — `None` if absent; `PendingError` naming the file on malformed content.
  - `save_pending(path: Path, pending: PendingSession) -> None` — atomic (write `.tmp`, rename).
  - `clear_pending(path: Path) -> None` — idempotent.
  - `class PendingError(Exception)`.

- [ ] **Step 1: Write the failing test**

`tests/test_pending.py`:
```python
from datetime import date
from pathlib import Path

import pytest
from seba.models import Agenda, GradeReview, PendingSession, ReviewItem, SessionRecord
from seba.session.pending import (PendingError, clear_pending, load_pending,
                                  pending_path, save_pending)


def agenda():
    return Agenda(goal="prob", subject="probability", session_number=1,
                  briefing="b",
                  review_items=[ReviewItem(id="it-1", type="recall", front="f", back="b")],
                  teach_concept=None, practice_quota=3, pace_hint="steady")


def test_pending_path(tmp_path: Path):
    assert pending_path(tmp_path, "prob") == tmp_path / "goals" / "prob" / "session.pending.yaml"


def test_roundtrip(tmp_path: Path):
    p = tmp_path / "session.pending.yaml"
    ps = PendingSession(goal="prob", agenda=agenda(), started=date(2026, 7, 4))
    ps.record.reviews.append(GradeReview(id="it-1", grade="good"))
    save_pending(p, ps)
    loaded = load_pending(p)
    assert loaded == ps
    assert loaded.record.reviews[0].grade == "good"
    assert not p.with_suffix(".tmp").exists()  # atomic write cleaned up


def test_missing_returns_none(tmp_path: Path):
    assert load_pending(tmp_path / "nope.yaml") is None


def test_malformed_names_file(tmp_path: Path):
    p = tmp_path / "session.pending.yaml"
    p.write_text("not: [valid: pending")
    with pytest.raises(PendingError, match="session.pending.yaml"):
        load_pending(p)


def test_clear_is_idempotent(tmp_path: Path):
    p = tmp_path / "session.pending.yaml"
    save_pending(p, PendingSession(goal="g", agenda=agenda(), started=date(2026, 7, 4)))
    clear_pending(p)
    assert not p.exists()
    clear_pending(p)  # no error on second call
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_pending.py -v` — Expected: FAIL (no `PendingSession`, no `seba.session.pending`).

- [ ] **Step 3: Implement**

Append to `src/seba/models.py` (after `GoalSummary`):
```python
class PendingSession(BaseModel):
    goal: str
    agenda: Agenda
    record: SessionRecord = Field(default_factory=SessionRecord)
    started: date
```

Create `src/seba/session/pending.py`:
```python
from pathlib import Path

import yaml
from pydantic import ValidationError

from seba.models import PendingSession


class PendingError(Exception):
    pass


def pending_path(data_dir: Path, goal: str) -> Path:
    return data_dir / "goals" / goal / "session.pending.yaml"


def load_pending(path: Path) -> PendingSession | None:
    if not path.exists():
        return None
    try:
        return PendingSession.model_validate(yaml.safe_load(path.read_text()))
    except (yaml.YAMLError, ValidationError) as e:
        raise PendingError(f"{path.name}: {e}") from e


def save_pending(path: Path, pending: PendingSession) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(yaml.safe_dump(pending.model_dump(mode="json"), sort_keys=False,
                                  allow_unicode=True))
    tmp.rename(path)


def clear_pending(path: Path) -> None:
    path.unlink(missing_ok=True)
```

- [ ] **Step 4: Run tests, expect PASS, commit**

```bash
uv run pytest tests/test_pending.py -v && uv run pytest -q
git add -A && git commit -m "feat: durable pending-session state for CLI-driven sessions"
```

---

### Task 2: Demolition — remove the API harness; rewrite new-goal

**Files:**
- Delete: `src/seba/session/dialogue.py`, `src/seba/session/recovery.py`, `src/seba/session/prompts/` (whole dir), `src/seba/synthesis/` (whole module), `tests/test_dialogue.py`, `tests/test_recovery.py`, `tests/test_synthesis.py`
- Modify: `src/seba/cli.py`, `src/seba/session/loader.py`, `src/seba/session/tools.py`, `src/seba/ui/repl.py`, `src/seba/config.py`, `pyproject.toml`, `tests/test_cli.py`, `tests/test_loader.py`, `tests/test_tools.py`, `tests/test_config.py`
- Delete after modify: `tests/test_integration.py` (T4 rewrites it from scratch; deleting here keeps the suite green between waves)

**Interfaces:**
- Consumes: `syllabus.load_syllabus`, `syllabus.SyllabusError`, `store.Store`.
- Produces (T3/T5 depend on):
  - `cli.py` retains: `app`, `_store()`, `_profile(subject)`, `status` command.
  - `new-goal` command with EXACT signature: `seba new-goal NAME --subject SUBJECT --from-file PATH` — validates the YAML at PATH via `load_syllabus` (exit 1, error text on stderr, on failure; no goal dir created), then `store.create_goal`.
  - `loader.load_profile` / `loader.load_overlay` survive unchanged.
  - `tools.ToolHandler` survives unchanged EXCEPT `anthropic_tools()` is deleted.
  - `repl.console`, `repl.briefing_card`, `repl.receipt` survive; `TerminalIO` deleted.
  - `config.data_dir()` / `config.subjects_dirs()` survive; `config.model()` / `config.recovery_model()` deleted.

- [ ] **Step 1: Delete files and the dependency**

```bash
git rm -r src/seba/session/prompts src/seba/synthesis
git rm src/seba/session/dialogue.py src/seba/session/recovery.py
git rm tests/test_dialogue.py tests/test_recovery.py tests/test_synthesis.py tests/test_integration.py
uv remove anthropic
```

- [ ] **Step 2: Rewrite `src/seba/cli.py`**

Replace the whole file with:
```python
from pathlib import Path

import typer

from seba import config
from seba.models import SubjectProfile
from seba.session.loader import load_profile
from seba.store.store import Store
from seba.syllabus.graph import SyllabusError, load_syllabus
from seba.ui import repl

app = typer.Typer(no_args_is_help=True)


def _store() -> Store:
    return Store(config.data_dir())


def _profile(subject: str) -> SubjectProfile:
    p = load_profile(subject)
    if p is None:
        typer.echo(f"no subject profile '{subject}' — create "
                   f"{config.data_dir()}/subjects/{subject}/profile.yaml "
                   f"(copy from subjects/_templates/)", err=True)
        raise typer.Exit(1)
    return p


@app.command("new-goal")
def new_goal(name: str, subject: str = typer.Option(...),
             from_file: Path = typer.Option(..., "--from-file",
                                            help="syllabus YAML drafted in conversation")):
    store = _store()
    _profile(subject)
    try:
        syllabus = load_syllabus(from_file)
    except SyllabusError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    store.create_goal(name, syllabus, subject)
    typer.echo(f"goal '{name}' created — start with: seba start {name}")


@app.command()
def status():
    goals = _store().list_goals()
    if not goals:
        typer.echo("no goals yet")
        return
    for g in goals:
        done_msg = f"{g.session_count} sessions · {g.due_count} due today"
        repl.console.print(f"[bold]{g.name}[/] ({g.subject}) — {done_msg}")
```

(`learn`, `extract`, the picker callback, and every `anthropic` import are gone. T3 adds the session commands to this file.)

- [ ] **Step 3: Trim the surviving modules**

`src/seba/session/loader.py` — delete `system_prompt`, `recovery_prompt`, and the `_PROMPTS` constant; keep `load_profile`, `load_overlay`, and their imports (`yaml`, `config`, `SubjectProfile`; drop `Agenda` and `Path` if now unused).

`src/seba/session/tools.py` — delete the `anthropic_tools()` function only. Keep `TOOL_MODELS`, `MINT_CAP`, and `ToolHandler` exactly as they are (including the `fetch_source` branch in `handle`).

`src/seba/ui/repl.py` — delete the `TerminalIO` class; keep `console`, `briefing_card`, `receipt`.

`src/seba/config.py` — delete `model()` and `recovery_model()`; keep `REPO_ROOT`, `data_dir()`, `subjects_dirs()`.

- [ ] **Step 4: Trim the tests to match**

`tests/test_config.py` — delete `test_models_defaults`.

`tests/test_loader.py` — delete `test_recovery_prompt`; delete the `agenda()` helper and its import; replace `test_overlay_and_system_prompt` with:
```python
def test_overlay():
    overlay = load_overlay("probability")
    assert "σ-algebra" in overlay
    assert load_overlay("nonexistent") == ""
```
and trim the import line to `from seba.session.loader import load_overlay, load_profile`.

`tests/test_tools.py` — delete `test_anthropic_tools_shape` and remove `anthropic_tools` from the import.

`tests/test_cli.py` — replace the whole file with:
```python
from typer.testing import CliRunner

from seba.cli import app

runner = CliRunner()

GOOD = "goal: g\nsubject: probability\nconcepts:\n  - id: a\n    name: A\n"
BAD = "goal: g\nsubject: probability\nconcepts:\n  - id: a\n    name: A\n    prereqs: [ghost]\n"


def test_status_empty(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path))
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "no goals" in result.output.lower()


def test_new_goal_from_file(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    f = tmp_path / "syllabus.yaml"
    f.write_text(GOOD)
    result = runner.invoke(app, ["new-goal", "prob", "--subject", "probability",
                                 "--from-file", str(f)])
    assert result.exit_code == 0
    assert (tmp_path / "data" / "goals" / "prob" / "syllabus.yaml").exists()


def test_new_goal_invalid_syllabus_rejected(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    f = tmp_path / "syllabus.yaml"
    f.write_text(BAD)
    result = runner.invoke(app, ["new-goal", "prob", "--subject", "probability",
                                 "--from-file", str(f)])
    assert result.exit_code == 1
    assert "ghost" in (result.output + str(result.exception or ""))
    assert not (tmp_path / "data" / "goals" / "prob").exists()


def test_new_goal_unknown_subject(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    f = tmp_path / "syllabus.yaml"
    f.write_text(GOOD)
    result = runner.invoke(app, ["new-goal", "x", "--subject", "nonexistent",
                                 "--from-file", str(f)])
    assert result.exit_code == 1
```

- [ ] **Step 5: Verify the purge, run everything, commit**

```bash
grep -rn "anthropic" src/ pyproject.toml && echo "PURGE INCOMPLETE" || echo "clean"
uv run python -c "import seba.cli, seba.session.tools, seba.session.loader"
uv run pytest -q
git add -A && git commit -m "refactor!: remove API dialogue harness; new-goal validates a drafted file

Claude Code (Max subscription) is now the dialogue harness; the anthropic
dependency, dialogue/recovery loop, prompts, and synthesis drafting are
deleted. Syllabus drafting moves into the seba-tutor skill; new-goal
validates and creates from a file."
```

Expected: grep prints `clean`; suite green (dialogue/recovery/synthesis/integration tests removed, the rest untouched or trimmed).

---

### Task 3: Session CLI commands — start / grade / mint / concept / end / abandon

**Files:**
- Modify: `src/seba/cli.py`
- Test: `tests/test_session_cli.py`

**Interfaces:**
- Consumes: T1's `pending` module and `PendingSession`; T2's `cli.py` skeleton; existing `ToolHandler`, `build_agenda`, `apply_record`, `Store`, `load_overlay`, `repl.receipt`.
- Produces: the CLI session-command contract in Global Constraints (T4 and T5 build on it verbatim).

- [ ] **Step 1: Write the failing test**

`tests/test_session_cli.py`:
```python
from datetime import date

import yaml
from fsrs import Card
from typer.testing import CliRunner

from seba.cli import app
from seba.models import Concept, Item, SessionRecord, Syllabus
from seba.store.store import Store

runner = CliRunner()


def _fsrs(due="2020-01-01T00:00:00+00:00"):
    d = Card().to_dict()
    d["due"] = due
    return d


def seed(data_dir, with_item=True):
    """Create goal 'prob'; optionally seed one long-overdue item."""
    store = Store(data_dir)
    store.create_goal("prob", Syllabus(goal="prob", subject="probability",
                                       concepts=[Concept(id="bayes", name="Bayes")]),
                      "probability")
    if with_item:
        gs = store.load_goal("prob")
        item = Item(id="it-1", concept="bayes", type="recall",
                    front="State Bayes", back="P(A|B)=...",
                    fsrs=_fsrs(), created=date(2026, 1, 1))
        store.save_session("prob", SessionRecord(complete=True, summary="seed",
                                                 next_session_hint="seed"),
                           "t", gs.model_copy(update={"items": [item]}))
    return store


def env(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    return tmp_path / "data"


def test_start_creates_pending_and_prints_agenda(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    result = runner.invoke(app, ["start", "prob"])
    assert result.exit_code == 0
    out = yaml.safe_load(result.output)
    assert out["ungraded_reviews"] == ["it-1"]
    assert out["agenda"]["review_items"][0]["front"] == "State Bayes"
    assert "σ-algebra" in out["subject_style"]
    assert (data / "goals" / "prob" / "session.pending.yaml").exists()


def test_start_resumes_existing_pending(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    runner.invoke(app, ["start", "prob"])
    runner.invoke(app, ["grade", "prob", "it-1", "good"])
    result = runner.invoke(app, ["start", "prob"])
    assert result.exit_code == 0 and "resuming" in result.output
    out = yaml.safe_load(result.output.split("\n", 1)[1])  # skip the resuming line
    assert out["already_graded"] == ["it-1"] and out["ungraded_reviews"] == []


def test_grade_records_and_rejects_duplicates_and_unknowns(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    runner.invoke(app, ["start", "prob"])
    assert runner.invoke(app, ["grade", "prob", "it-1", "good"]).exit_code == 0
    assert runner.invoke(app, ["grade", "prob", "it-1", "easy"]).exit_code == 1
    assert runner.invoke(app, ["grade", "prob", "it-99", "good"]).exit_code == 1
    assert runner.invoke(app, ["grade", "prob", "it-1", "great"]).exit_code == 2  # bad enum -> typer usage error is also acceptable as 1; accept either
```

Note to implementer on the last assertion: grade validity is checked by `ToolHandler` (pydantic), so an invalid grade string exits 1 with the validation text. Change the assertion to `== 1` and make `grade` a plain `str` argument passed through to the handler — do NOT make it a typer enum (the handler owns validation; one validator, one error format). The test as committed must read:
```python
    assert runner.invoke(app, ["grade", "prob", "it-1", "great"]).exit_code == 1
```

```python
def test_commands_without_pending_fail_with_hint(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    for args in (["grade", "prob", "it-1", "good"],
                 ["mint", "prob", "--concept", "bayes", "--type", "recall",
                  "--front", "f", "--back", "b"],
                 ["concept", "prob", "bayes", "--note", "n"],
                 ["end", "prob", "--summary", "s", "--hint", "h"]):
        result = runner.invoke(app, args)
        assert result.exit_code == 1
        assert "seba start" in (result.output + str(result.exception or ""))


def test_end_gate_then_success(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    store = seed(data)
    runner.invoke(app, ["start", "prob"])
    blocked = runner.invoke(app, ["end", "prob", "--summary", "s", "--hint", "h"])
    assert blocked.exit_code == 1 and "it-1" in (blocked.output + str(blocked.exception or ""))

    runner.invoke(app, ["grade", "prob", "it-1", "good"])
    runner.invoke(app, ["mint", "prob", "--concept", "bayes", "--type", "recall",
                        "--front", "nf", "--back", "nb"])
    runner.invoke(app, ["concept", "prob", "bayes", "--status", "started",
                        "--note", "shaky on priors"])
    done = runner.invoke(app, ["end", "prob", "--summary", "Reviewed Bayes.",
                               "--hint", "drill priors"])
    assert done.exit_code == 0

    assert not (data / "goals" / "prob" / "session.pending.yaml").exists()
    gs = store.load_goal("prob")
    assert gs.last_hint == "drill priors"
    assert "shaky on priors" in gs.notes
    assert len(gs.items) == 2  # original + minted
    assert gs.syllabus.concepts[0].status == "in-progress"
    sessions = data / "goals" / "prob" / "sessions"
    assert (sessions / "002.md").exists()
    assert "INCOMPLETE" not in (sessions / "002.md").read_text()
    assert "Claude Code" in (sessions / "002.transcript.md").read_text()


def test_abandon_discard(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    runner.invoke(app, ["start", "prob"])
    runner.invoke(app, ["grade", "prob", "it-1", "good"])
    result = runner.invoke(app, ["abandon", "prob", "--discard"])
    assert result.exit_code == 0
    assert not (data / "goals" / "prob" / "session.pending.yaml").exists()
    assert not (data / "goals" / "prob" / "sessions" / "002.md").exists()


def test_abandon_saves_incomplete(monkeypatch, tmp_path):
    data = env(monkeypatch, tmp_path)
    seed(data)
    runner.invoke(app, ["start", "prob"])
    runner.invoke(app, ["grade", "prob", "it-1", "good"])
    result = runner.invoke(app, ["abandon", "prob"])
    assert result.exit_code == 0
    assert not (data / "goals" / "prob" / "session.pending.yaml").exists()
    body = (data / "goals" / "prob" / "sessions" / "002.md").read_text()
    assert "INCOMPLETE" in body
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_session_cli.py -v` — Expected: FAIL (no `start` command).

- [ ] **Step 3: Implement — append to `src/seba/cli.py`**

Add these imports at the top (merging with T2's):
```python
from datetime import date, datetime, timezone

import yaml

from seba.models import PendingSession
from seba.scheduler.agenda import build_agenda
from seba.scheduler.apply import apply_record
from seba.session.loader import load_overlay, load_profile
from seba.session.pending import (clear_pending, load_pending, pending_path,
                                  save_pending)
from seba.session.tools import ToolHandler
```

Append the commands:
```python
NO_TRANSCRIPT = "(session conducted via Claude Code; no transcript captured)\n"


def _session(goal: str):
    """Load the in-progress session or exit with a hint."""
    store = _store()
    ppath = pending_path(store.data_dir, goal)
    pending = load_pending(ppath)
    if pending is None:
        typer.echo(f"no session in progress for '{goal}' — run: seba start {goal}",
                   err=True)
        raise typer.Exit(1)
    state = store.load_goal(goal)
    handler = ToolHandler(pending.agenda, state.syllabus,
                          config.data_dir() / "sources")
    handler.record = pending.record
    return store, pending, handler, ppath


def _dispatch(goal: str, tool: str, args: dict) -> None:
    store, pending, handler, ppath = _session(goal)
    result, is_error = handler.handle(tool, args)
    if is_error:
        typer.echo(result, err=True)
        raise typer.Exit(1)
    save_pending(ppath, pending)
    typer.echo(result)


def _finish(store: Store, goal: str, pending: PendingSession, ppath) -> None:
    state = store.load_goal(goal)
    updated = apply_record(state, pending.record, datetime.now(timezone.utc))
    clear_pending(ppath)
    store.save_session(goal, pending.record, NO_TRANSCRIPT, updated)
    repl.receipt(pending.record)


@app.command()
def start(goal: str):
    store = _store()
    state = store.load_goal(goal)
    profile = _profile(state.subject)
    ppath = pending_path(store.data_dir, goal)
    pending = load_pending(ppath)
    if pending is None:
        agenda = build_agenda(state, profile, date.today(),
                              config.data_dir() / "sources")
        pending = PendingSession(goal=goal, agenda=agenda, started=date.today())
        save_pending(ppath, pending)
    else:
        typer.echo("(resuming session in progress)")
    graded = sorted({r.id for r in pending.record.reviews})
    typer.echo(yaml.safe_dump({
        "agenda": pending.agenda.model_dump(),
        "subject_style": load_overlay(state.subject),
        "already_graded": graded,
        "ungraded_reviews": [r.id for r in pending.agenda.review_items
                             if r.id not in set(graded)],
        "minted_so_far": len(pending.record.new_items),
    }, sort_keys=False, allow_unicode=True))


@app.command()
def grade(goal: str, item_id: str, grade: str,
          note: str | None = typer.Option(None)):
    _dispatch(goal, "grade_review", {"id": item_id, "grade": grade, "note": note})


@app.command()
def mint(goal: str, concept: str = typer.Option(...),
         type: str = typer.Option(...), front: str = typer.Option(...),
         back: str = typer.Option(...)):
    _dispatch(goal, "mint_item", {"concept": concept, "type": type,
                                  "front": front, "back": back})


@app.command("concept")
def concept_cmd(goal: str, concept_id: str,
                status: str | None = typer.Option(None, help="started|completed"),
                note: str | None = typer.Option(None)):
    _dispatch(goal, "update_concept",
              {"id": concept_id, "status_change": status, "note": note})


@app.command()
def end(goal: str, summary: str = typer.Option(...),
        hint: str = typer.Option(..., "--hint")):
    store, pending, handler, ppath = _session(goal)
    result, is_error = handler.handle(
        "end_session", {"summary": summary, "next_session_hint": hint})
    if is_error:
        typer.echo(result, err=True)
        raise typer.Exit(1)
    _finish(store, goal, pending, ppath)


@app.command()
def abandon(goal: str, discard: bool = typer.Option(
        False, "--discard", help="drop recorded outcomes instead of saving INCOMPLETE")):
    store, pending, handler, ppath = _session(goal)
    if discard:
        clear_pending(ppath)
        typer.echo("pending session discarded")
        return
    _finish(store, goal, pending, ppath)  # complete=False → INCOMPLETE marker
```

Implementation notes (read before coding):
- `handler.record = pending.record` makes the handler mutate the pending record in place, so `save_pending(ppath, pending)` after a successful `handle` persists the accepted call. No copying.
- An invalid `--status` value (anything but `started`/`completed`) is rejected by `UpdateConcept` validation inside the handler → stderr + exit 1. Same principle as grades: the handler owns validation.
- `grade` passes `note: None` through; `GradeReview` defaults it. Same for `concept_cmd`.
- `end` validates through the handler's session-end gate; the error text already lists the ungraded ids.
- `abandon` without `--discard` reuses `_finish`: `record.complete` is `False`, so `save_session` writes the `INCOMPLETE` marker — identical semantics to a crashed API session.

- [ ] **Step 4: Run tests, expect PASS, commit**

```bash
uv run pytest tests/test_session_cli.py -v && uv run pytest -q
git add -A && git commit -m "feat: session CLI commands driven by pending-session state"
```

---

### Task 4: Integration test — the continuity property through the real CLI

**Files:**
- Create: `tests/test_integration.py` (T2 deleted the old one)

**Interfaces:**
- Consumes: T3's commands, `Store` (read-side assertions only). Produces nothing new — proves the loop end-to-end through the shipped surface.

Date note (why this test is wall-clock-safe): `start` uses the real `date.today()`. The test never pins a date. Session 1 has no items, so no reviews regardless of date. The card minted in session 1 gets `due = today` (the `mint_item` determinism fix from PR #2), so on the very next `start` — same real day — it is due. All content assertions (note, hint, front) are date-free. The only conceivable flake is a process that straddles midnight UTC between `end` and the next `start`; if that ever fires, report it, don't patch it.

- [ ] **Step 1: Write the test**

`tests/test_integration.py`:
```python
import yaml
from typer.testing import CliRunner

from seba.cli import app
from seba.store.store import Store

runner = CliRunner()

SYLLABUS = "goal: prob\nsubject: probability\nconcepts:\n  - id: bayes\n    name: Bayes\n"


def invoke_ok(args):
    result = runner.invoke(app, args)
    assert result.exit_code == 0, f"{args} failed: {result.output} {result.exception}"
    return result


def test_session_two_reflects_session_one(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    f = tmp_path / "syllabus.yaml"
    f.write_text(SYLLABUS)
    invoke_ok(["new-goal", "prob", "--subject", "probability", "--from-file", str(f)])

    # --- Session 1: teach, note a misconception, mint a card, end.
    out1 = yaml.safe_load(invoke_ok(["start", "prob"]).output)
    assert out1["ungraded_reviews"] == []          # nothing due on day one
    assert out1["agenda"]["teach_concept"]["id"] == "bayes"
    invoke_ok(["concept", "prob", "bayes", "--status", "started",
               "--note", "confuses prior with likelihood"])
    invoke_ok(["mint", "prob", "--concept", "bayes", "--type", "recall",
               "--front", "State Bayes' theorem", "--back", "P(A|B)=..."])
    invoke_ok(["end", "prob", "--summary", "Introduced Bayes.",
               "--hint", "drill the prior/likelihood split"])

    # --- Session 2: the minted card is due; briefing carries note + hint.
    out2 = yaml.safe_load(invoke_ok(["start", "prob"]).output)
    [review] = out2["agenda"]["review_items"]
    assert review["front"] == "State Bayes' theorem"
    assert "confuses prior with likelihood" in out2["agenda"]["briefing"]
    assert "drill the prior/likelihood split" in out2["agenda"]["briefing"]

    # end is gated until the review is graded
    blocked = runner.invoke(app, ["end", "prob", "--summary", "s", "--hint", "h"])
    assert blocked.exit_code == 1

    invoke_ok(["grade", "prob", review["id"], "good"])
    invoke_ok(["end", "prob", "--summary", "Drilled.", "--hint", "advance"])

    # --- Continuity assertions straight off disk.
    store = Store(tmp_path / "data")
    gs = store.load_goal("prob")
    assert gs.session_number == 3
    assert gs.recent_grades == ["good"]
    assert gs.items[0].fsrs["last_review"] is not None  # FSRS state advanced+persisted
    assert gs.syllabus.concepts[0].status == "in-progress"
```

- [ ] **Step 2: Run it, expect PASS on first try**

Run: `uv run pytest tests/test_integration.py -v` — Expected: PASS. A failure here means a wiring bug in T1–T3; fix in the task that owns the broken piece, never with shims here.

- [ ] **Step 3: Run everything, commit**

```bash
uv run pytest -q
git add -A && git commit -m "test: CLI-driven end-to-end continuity test"
```

---

### Task 5: The seba-tutor skill, install instructions, README rewrite

**Files:**
- Create: `skills/seba-tutor/SKILL.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: the CLI command contract from Global Constraints (verify each command name/flag against `src/seba/cli.py` before writing — accuracy over embellishment).
- Produces: docs only.

- [ ] **Step 1: Write `skills/seba-tutor/SKILL.md`**

```markdown
---
name: seba-tutor
description: Conduct a Seba tutoring session — spaced review plus guided teaching for the user's long-term learning goals (probability, Italian, ...). Use when the user asks to study, learn, review, be tutored, drill a subject, or says "seba".
---

# Seba tutor

You are a long-term personal tutor, mid-relationship with this learner. Seba's
scheduler owns what to cover; you own the dialogue and the grading. All state
lives outside this conversation — you read it via `seba start` and record
outcomes via the commands below, the moment they happen. Anything you do not
record does not exist next session.

## Commands (the `seba` CLI is on PATH)

| Command | Purpose |
|---|---|
| `seba status` | list goals with due counts |
| `seba start GOAL` | begin/resume a session; prints YAML: `agenda`, `subject_style`, `already_graded`, `ungraded_reviews`, `minted_so_far` |
| `seba grade GOAL ITEM_ID GRADE [--note TEXT]` | record a review grade the moment its exchange resolves |
| `seba mint GOAL --concept ID --type TYPE --front TEXT --back TEXT` | create a spaced-repetition card (cap 10/session) |
| `seba concept GOAL ID [--status started\|completed] [--note TEXT]` | record concept progress or a misconception/strength note |
| `seba end GOAL --summary TEXT --hint TEXT` | close the session (refuses while reviews are ungraded) |
| `seba abandon GOAL [--discard]` | learner quits early: save what was recorded as INCOMPLETE (or discard) |
| `seba new-goal NAME --subject SUBJECT --from-file PATH` | create a goal from a syllabus YAML you drafted |

Any command that fails prints the reason and exits non-zero — read the message,
fix the call (e.g. grade the listed items), and retry. Never work around a
refusal.

## Session protocol

1. `seba status`; if the user named a goal, `seba start GOAL` directly.
2. Parse the YAML. `agenda.briefing` is your memory of this learner — open with
   one natural sentence of continuity from it. `subject_style` governs notation
   and drill style for the whole session. Honor `agenda.pace_hint`.
3. **Reviews first**, woven in conversationally — not as a quiz sheet. For each
   item in `agenda.review_items`: pose the front, get a REAL answer attempt
   before revealing anything, give corrective feedback naming any misconception,
   then IMMEDIATELY run `seba grade`. Rubric:
   - `again` — wrong, or no recall
   - `hard` — correct but with significant hesitation or hints
   - `good` — correct
   - `easy` — instant and confident
   - `skipped` — only for items the session never reached
4. **Teach** `agenda.teach_concept` (if null: review-only session). Use its
   `source_excerpts`; for more context read files under `$SEBA_DATA_DIR/sources/`
   (default `~/seba-data/sources/`). Method: worked example → faded scaffolding
   → independent practice, about `agenda.practice_quota` practice questions,
   targeting ~85% learner success. Ask "why?" and "convince me" follow-ups.
   Never dump an answer the learner could produce with one more hint.
5. Record as you go: `seba concept` for status moves (`--status started` when
   teaching begins, `completed` only when the learner demonstrates it) and for
   durable notes (misconceptions, strengths — these surface in future
   briefings). `seba mint` only for facts/skills worth retaining a month from
   now — never session-local scaffolding.
6. Tangents are welcome — follow them, and record anything durable.
7. When the learner is done: recap aloud in 2–3 sentences, then
   `seba end GOAL --summary "3–6 sentences" --hint "concrete next-session hint"`.
   If it exits non-zero listing ungraded items, grade each (or `skipped`), then
   retry. If the learner quits abruptly, `seba abandon GOAL` — never leave a
   session pending silently.

## Creating a new goal

1. Interview the learner: goal, prior knowledge, primary source (ask for a
   table of contents — a file or pasted text).
2. Draft the syllabus YAML yourself: top-level `goal`, `subject`, `concepts`;
   each concept `id` (kebab-case), `name`, `prereqs` (list of ids), `sources`
   (refs like `dirname/file.md#section` into `$SEBA_DATA_DIR/sources/`),
   `status: unseen`, `est_sessions` (1–3). Size concepts to 1–3 sessions;
   prereq edges may reorder or cut across the book's chapter order; INSERT
   prerequisite concepts the book assumes but does not teach.
3. Show the draft to the learner and get explicit approval — this is a hard
   gate, not a formality.
4. Write it to a temp file and run `seba new-goal NAME --subject S --from-file
   PATH`. On validation errors (cycles, unknown prereqs, duplicate ids), fix
   the YAML and retry. Subjects: `probability`, `italian` are bundled; for a
   new subject, copy a template from the repo's `subjects/_templates/` into
   `$SEBA_DATA_DIR/subjects/<name>/` first.
```

- [ ] **Step 2: Rewrite README.md**

Keep the existing etymology opening and data-layout section. Replace everything about `learn`/`extract`/`ANTHROPIC_API_KEY`/`SEBA_MODEL` with the Claude-Code mode. Required content:

- **How it works now:** sessions run inside Claude Code (your subscription — no API key, no per-token cost). The `seba` CLI owns state, scheduling, and validation; the `seba-tutor` skill instructs Claude Code to conduct the dialogue and record outcomes through it.
- **Install:**
  ```bash
  uv tool install --force ~/Desktop/Projects/seba   # global `seba` command
  mkdir -p ~/.claude/skills
  ln -sfn ~/Desktop/Projects/seba/skills/seba-tutor ~/.claude/skills/seba-tutor
  ```
  Then from any directory: `claude` → ask to study, or `/seba-tutor`.
- **Env:** `SEBA_DATA_DIR` (default `~/seba-data`; its own git repo, one commit per session). `SEBA_MODEL`/`SEBA_RECOVERY_MODEL`/`ANTHROPIC_API_KEY` no longer exist — remove them.
- **Command reference:** the eight commands from the SKILL.md table, one line each.
- **Crash story:** every accepted outcome is on disk in `session.pending.yaml` the moment it's recorded; `seba start` resumes, `seba abandon` closes out. (The old `extract` command is gone — nothing to reconstruct.)

- [ ] **Step 3: Verify docs against code, commit**

```bash
uv run seba --help          # confirm the eight commands exist as documented
grep -n "extract\|learn\|ANTHROPIC" README.md && echo "STALE DOCS" || echo "clean"
git add -A && git commit -m "docs: seba-tutor skill and Claude-Code-mode README"
```

---

### Task 6: Dogfood gate (manual — HUMAN ONLY)

No files. Hand off to the user:

- [ ] **Step 1:** Run the install block from README (`uv tool install`, skill symlink).
- [ ] **Step 2:** In a fresh Claude Code session, create one real goal via the skill's new-goal protocol (real ToC in `$SEBA_DATA_DIR/sources/`). Approve the syllabus for real.
- [ ] **Step 3:** Run 3 real sessions across ≥3 distinct days. After each: check `data/` git log has one commit per session; `NNN.outcomes.yaml` grades match what actually happened; the next session's briefing surfaces shaky concepts and due items.
- [ ] **Step 4:** Success criteria (spec §9.5): session N+1's briefing correctly reflects session N — shaky concepts resurface, mastered items sleep, frontier advances. Also watch the CC-specific risk: does the tutor actually call `seba grade` the moment each review resolves, or does it drift into chatting without recording? Skill-text fixes are file edits, no code.

---

## Self-review (done at plan time)

- **Spec coverage:** pending persistence ✅(T1) · API removal + LLM-free new-goal ✅(T2) · session commands with identical validation + gates ✅(T3, reusing `ToolHandler` verbatim) · continuity property re-proven through the new surface ✅(T4) · skill + install + docs ✅(T5) · dogfood ✅(T6). Context firewall (§8a) untouched — `build_agenda` unchanged. Crash path improves: incremental disk persistence replaces `extract`.
- **Type consistency:** `PendingSession` defined T1, consumed T3; command contract stated once in Global Constraints, tested in T3/T4, documented in T5. `_session` returns `(store, pending, handler, ppath)` consistently in `end`/`abandon`/`_dispatch`.
- **Placeholder scan:** clean — every step carries the full code or exact content requirements.
- **Known risks carried deliberately:** (a) softer guarantee than the API loop — Claude Code *chooses* to call the scripts; mitigated by SKILL.md discipline, the `end` gate, and T6's explicit dogfood check. (b) `start` uses real `date.today()` — T4 is designed date-independent; midnight-UTC straddle is report-don't-patch. (c) pending file may ride along in another goal's data-repo commit — accepted.
