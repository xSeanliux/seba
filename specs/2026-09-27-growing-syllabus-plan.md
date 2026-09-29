# Changing a Syllabus After It Starts — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Task 1 runs alone. Tasks 2 to 5 run in parallel, each in its own worktree on its own branch, and are merged afterwards. Task 6 runs after the merge.

**Goal:** Let a syllabus change while a goal is under way: add concepts, add a source to a concept, drop and restore concepts, steer a session to a chosen concept, and put the goal's direction in front of the tutor.

**Architecture:** A syllabus stays a validated graph of concepts in `syllabus.yaml`. Changes that belong to a tutoring conversation (drop, restore, add a source) are recorded in the session and applied at `seba end`, like every other concept move. Changes that stand alone (`seba extend`, `seba tune --direction`, `seba start --concept`) act at once. The tool handler judges every call against the goal's state *as this session has changed it so far*, by replaying the session's record over the loaded syllabus.

**Tech Stack:** Python 3.12, py-fsrs 6.3.1, pydantic v2, typer, PyYAML, pytest, ruff, ty, uv.

**Spec:** `specs/2026-09-27-growing-syllabus-design.md`, with `CONTEXT.md` and `docs/adr/0001-scheduler-owns-the-schedule.md` (branch `docs/scheduling-syllabus-specs`). Stacked on PR 1, branch `feat/scheduling-controls`.

## Global Constraints

- Scope is what any goal can use. Nothing here is specific to research or reading goals.
- Left out on purpose; do not build any of it: sources tracked in their own right (title, read state); a reading list in the view; steering by source; recording open research questions; ranking ready concepts; editing prerequisite edges by command.
- A paper is a **source**, never a concept. Use the terms in `CONTEXT.md` exactly: goal, direction, concept, source, card, hard, mapping, emphasis, gap, dropped. A dropped concept is never called deleted or archived.
- A dropped concept leaves the frontier and the teaching slot, and its cards stop being reviewed. Its history, notes and cards are kept. Restoring returns it to the status it had.
- Hard prerequisite edges are the curriculum. A refusal that rests on them names the concepts involved.
- A refusal writes nothing: no change to any file, no commit.
- py-fsrs decides when a card comes back and Seba never changes that by itself (PR 1's rule). Nothing in this plan writes a due date.
- No data migration. A goal, a session outcome file, and a pending session written before this change must still load.
- Each `seba` command is a separate process. The tool handler is rebuilt for every command from the goal as stored on disk; the only thing carried between commands in a session is the pending session's record. Any rule that depends on what happened earlier in the same session must read that record.
- Python typing: never annotate as `Any` or `object`, and never add `# type: ignore` to a line that can be typed properly.
- The gate is `make check` (ruff, `ruff format --check`, `ty check src`, pytest). It must pass at the end of every task. Baseline at the start of this plan: 215 passed.
- Match the surrounding code: its comment density, naming and test style. No new dependencies.
- Commits use Conventional Commits and end with the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Rules for the parallel tasks (2 to 5)

These keep four branches mergeable. They bind Tasks 2, 3, 4 and 5.

- **Tests go in a new file**, named in the task. Change an existing test file only where this task changes behaviour an existing test asserts on, and say which in the report.
- **`src/seba/models.py` is closed**, except that Task 5 may change the `View*` models at the end of the file. Every other shape these tasks need is added by Task 1.
- **`src/seba/syllabus/__init__.py` is closed.** Import from `seba.syllabus.graph` directly, as the existing code does.
- **Each task owns the regions named in its Files list** and leaves the rest of those files alone, imports excepted. New functions go exactly where the task says, never at the end of a file unless the task says so.
- Compare statuses the way the surrounding code does (`c.status == "dropped"`), so that a task needs no new import for it.

## Review Focus

Inputs the design is silent on. Each has a test in the task that owns the code.

1. Two changes to the same concept in one session (drop then restore; drop then complete; restore then drop; add the same source twice) → each call is judged against the state the earlier calls left (Tasks 1 and 3).
2. Restoring a concept whose hard prerequisite is dropped → refused, naming the prerequisite; otherwise it is live and can never reach the frontier (Task 3).
3. An extension file that is empty, is not YAML, names a concept with status `in-progress` or `dropped`, or repeats an id within itself → a clean refusal naming the file, and `syllabus.yaml` byte-identical (Task 2).
4. `seba start --concept` on a day that would otherwise be a synthesis or return-after-lapse session → the learner's request wins and the concept is taught (Task 4).
5. A direction that is only whitespace → refused. A goal with no `direction` in `goal.yaml` → the briefing shows the syllabus's `goal` line, which is where the direction has lived until now (Tasks 1 and 5).

---

### Task 1: Foundation — shared shapes, and the handler judges against this session's state

Runs alone, first. Everything Tasks 2 to 5 share is defined here so that they do not collide.

**Files:**
- Modify: `src/seba/models.py`, `src/seba/syllabus/graph.py`, `src/seba/scheduler/apply.py`, `src/seba/session/tools.py`, `src/seba/store/store.py`
- Test: `tests/test_models.py`, `tests/test_syllabus.py`, `tests/test_apply.py`, `tests/test_tools.py`, `tests/test_store.py`, `tests/test_session_cli.py`

**Interfaces:**
- Consumes: PR 1 as merged on `feat/scheduling-controls`.
- Produces:
  - `Status.DROPPED = "dropped"`
  - `Concept.dropped_from: Status | None = None` — the status a dropped concept returns to. `None` on every concept that is not dropped.
  - `UpdateConcept.status_change: Literal["started", "completed", "reopened", "dropped", "restored"] | None`
  - `UpdateConcept.add_source: str | None = None`
  - `GoalMeta.direction: str | None = None`; `GoalState.direction: str = ""`
  - `seba.scheduler.apply.apply_change(syllabus: Syllabus, change: UpdateConcept) -> Syllabus` — applies one concept change; raises `SyllabusError` if the move is illegal.
  - `seba.scheduler.apply.replay(syllabus: Syllabus, changes: list[UpdateConcept]) -> Syllabus` — applies each in order, skipping any that raise. `apply_record` uses it.
  - `ToolHandler.effective() -> Syllabus` — the loaded syllabus with this session's record replayed over it.
  - `Store._write_syllabus(gdir: Path, syllabus: Syllabus) -> None` — the one place `syllabus.yaml` is written.

**Requirements:**

1. **Models.** Add the fields above. `dropped` and `restored` are accepted by the model in this task; what they *do* is Task 3. Until then `apply_change` raises `SyllabusError` for them (`"'dropped' is not supported yet"` is fine; Task 3 replaces it), so `replay` skips them and nothing moves.
2. **`frontier`** excludes dropped concepts. **`apply_status`** raises `SyllabusError` for any move on a dropped concept; today `_ORDER.index` would raise `ValueError` for a status not in `_ORDER`.
3. **`apply_change` and `replay`.** Move the loop in `apply_record` that walks `record.concepts` into these two functions, behaviour unchanged for `started`, `completed` and `reopened`. A change with no `status_change` and no `add_source` returns the syllabus as it is.
4. **The handler judges against effective state.** In `ToolHandler`, every rule that reads a concept's status reads it from `effective()`, not from `self.syllabus`. After the existing checks in `_update_concept` (unknown concept, the two guards around reopening, evidence, the pass count), a call with a `status_change` is tried with `apply_change` against the effective syllabus:
   - if it raises, and the call is `started` or `completed` on a concept that is already in that status, it is accepted as before (a repeated `started` is normal and must stay harmless);
   - if it raises otherwise, the call is refused with the error's message and is not recorded.

   This closes a fault that predates this plan: the handler replied "recorded" to a `completed` on a concept that was never started, and the move was dropped silently at `seba end`.
5. **Consequences to carry through.** With rule 4, within one session: a second `reopened` on the same concept is refused (it is in progress by then); `started` after `reopened` is accepted as a repeat. Some existing tests complete a concept that the fixture left `unseen`; they passed only because of the fault. Put the concept in progress in those tests rather than weakening the rule, and list each test you changed in your report.
6. **Syllabus writes.** `Store._write_syllabus` writes `syllabus.model_dump(mode="json", exclude_none=True)`, so `dropped_from` appears only on a dropped concept. `create_goal` and `save_session` use it.
7. **Direction is loaded.** `GoalState.direction` is `goal.yaml`'s `direction` if it is set and not blank, otherwise the syllabus's `goal` line, stripped. Nothing shows it yet; that is Task 5.

**Tests, each seen failing first:**

- models: `Concept` round-trips `status: dropped` with `dropped_from: in-progress`; a syllabus file written before this change (no `dropped_from`) loads.
- syllabus: a dropped concept is not on the frontier; its dependents are not on the frontier either while it is not done; `apply_status` on a dropped concept raises `SyllabusError`, never `ValueError`.
- apply: `replay` gives the same result as `apply_record` did for `started`/`completed`/`reopened`, including an illegal move in the middle of the list being skipped while later ones apply.
- tools: `completed` on an unseen concept is refused and not recorded; `started` twice is accepted; `reopened` twice in one session is refused the second time; `started` after `reopened` in one session is accepted; `completed` after `completed` is accepted as a repeat.
- store: `syllabus.yaml` has no `dropped_from` key for a goal with no dropped concept; direction falls back to the syllabus's `goal` line and prefers `goal.yaml`.
- session CLI: one end-to-end case through separate commands, `start`, `concept --status completed --evidence x` on an unseen concept exits 1.

**Commit:** `refactor(session): judge concept calls against this session's state; shared shapes for syllabus changes`

---

### Task 2: `seba extend` — adding concepts

Parallel. Branch `pr2/extend`.

**Files:**
- Modify: `src/seba/syllabus/graph.py` (new functions placed directly after `load_syllabus`), `src/seba/store/store.py` (new method placed directly after `create_goal`), `src/seba/cli.py` (new command placed directly after `new_goal`)
- Test: create `tests/test_extend.py`

**Interfaces:**
- Consumes: `Store._write_syllabus`, `Status.DROPPED`, `Concept.dropped_from` (Task 1).
- Produces:
  - `seba.syllabus.graph.load_concepts(path: Path) -> list[Concept]`
  - `seba.syllabus.graph.extend(s: Syllabus, new: list[Concept]) -> Syllabus`
  - `Store.extend_syllabus(name: str, path: Path) -> list[str]` — the ids added, in file order
  - `seba extend GOAL --from-file PATH`

**Requirements:**

1. The file holds concepts in the existing concept schema: either a mapping with a `concepts:` list (a whole syllabus file works; its `goal` and `subject` are ignored) or a bare list of concepts.
2. The new concepts are appended in file order and the merged syllabus goes through the existing `validate`: duplicate ids, unknown references, cycles. New concepts may point at existing ones, in `prereqs`, `soft_prereqs` and `confusable_with`.
3. Refusals, each a `SyllabusError` whose message begins with the file's name:
   - the file cannot be read, is not YAML, or holds no concepts;
   - an id that already exists in the syllabus, or is repeated in the file: the message lists the ids;
   - a new concept whose status is not `unseen` or `done`, or that carries `dropped_from`: `new concept '<id>' has status <status>; a new concept is unseen, or done if the learner already has it`;
   - anything `validate` raises.
4. `Store.extend_syllabus` raises `StoreError` with that message. A refusal leaves `syllabus.yaml` byte-identical and makes no commit. On success it writes through `_write_syllabus`, stages only `goals/<name>/syllabus.yaml`, and commits `<name>: extended (+N)`.
5. `seba extend` prints `added N concept(s): a, b`. It exits 1 with the message on a refusal and on an unknown goal. `--from-file` must exist (typer's `exists=True`, as `new-goal` has it).
6. It works between sessions and during one. It never touches the pending session; the agenda of a session in progress is unchanged. A card can be minted on a new concept in that same session.

**Tests, each seen failing first:**

- a concept whose prerequisite already exists is added, and reaches the frontier once that prerequisite is done;
- a duplicate id, an id repeated in the file, an unknown reference, and a cycle are each refused, with `syllabus.yaml` byte-identical and the commit count unchanged. (A new concept cannot make an existing one depend on it, so build the cycle among new concepts, at least one of which also depends on an existing concept.)
- status `in-progress` and status `dropped` on a new concept are refused; status `done` is accepted;
- an empty file, a file that is not YAML, and a mapping with no `concepts` are refused, naming the file;
- both file shapes are accepted;
- during a pending session: `start`, `extend`, then `mint` on the new concept succeeds, the pending file's agenda is unchanged, and after `end` the new concept and the card are both stored;
- a goal extended with a concept written before this change (no `dropped_from`) round-trips.

**Commit:** `feat(syllabus): seba extend adds concepts to a syllabus under way`

---

### Task 3: Dropping, restoring, and adding a source

Parallel. Branch `pr2/drop-restore`.

**Files:**
- Modify: `src/seba/syllabus/graph.py` (new functions placed at the end of the file, after `apply_status`), `src/seba/scheduler/apply.py` (`apply_change`), `src/seba/session/tools.py` (`_update_concept`, `_mint_item`), `src/seba/scheduler/agenda.py` (`_reviews` and `_trouble_lines` only), `src/seba/store/store.py` (`list_goals` only), `src/seba/cli.py` (`concept_cmd` only)
- Test: create `tests/test_drop_restore.py`

**Interfaces:**
- Consumes: everything Task 1 produces.
- Produces:
  - `seba.syllabus.graph.drop(s: Syllabus, concept_id: str) -> Syllabus`
  - `seba.syllabus.graph.restore(s: Syllabus, concept_id: str) -> Syllabus`
  - `seba concept GOAL ID --status dropped|restored`
  - `seba concept GOAL ID --add-source LOCATOR`

**Requirements:**

1. **Drop.** `drop` sets the concept's status to `dropped` and `dropped_from` to the status it had. Refused with `SyllabusError`:
   - unknown concept;
   - already dropped: `'<id>' is already dropped`;
   - a live concept depends on it. A dependent is any concept that lists it in `prereqs` and is not itself dropped, whatever its status: `cannot drop '<id>': <a>, <b> depend on it — drop them first, or remove the edge in syllabus.yaml`. `soft_prereqs` and `confusable_with` never block a drop.
2. **Restore.** `restore` sets the status back to `dropped_from` (`unseen` if it is missing) and clears `dropped_from`. Refused with `SyllabusError`:
   - not dropped: `'<id>' is <status>; only a dropped concept can be restored`;
   - one of its hard prerequisites is dropped: `cannot restore '<id>': it depends on <a>, which is dropped — restore that first`.
3. **`apply_change`** dispatches `dropped` to `drop` and `restored` to `restore`, replacing Task 1's placeholder. With `add_source` set, it appends the locator to the concept's `sources` unless it is already there. A change may carry a status change and a source together.
4. **Handler.** Drop and restore are judged by Task 1's rule: tried against the effective syllabus, refused with the error's message. In addition:
   - `--add-source` with a blank locator is refused: `--add-source needs a locator`;
   - a locator already among the concept's sources, in the effective syllabus, is refused: `'<locator>' is already a source of '<id>'`;
   - `mint` on a concept that is dropped, in the effective syllabus, is refused: `'<id>' is dropped; restore it before minting a card for it`.
5. **Nothing of a dropped concept is reviewed.** In `_reviews`, the cards of dropped concepts are excluded from the due cards and from the warm-up cards. In `_trouble_lines`, a card of a dropped concept produces no line. In `Store.list_goals`, `due_count` excludes them. The cards stay in `items.jsonl` untouched, with their due dates as they were.
6. **Restoring brings the cards back** as they are. No due date is rewritten; a card that fell due while its concept was dropped is simply due.
7. `seba concept`'s `--status` help lists all five values. `--add-source` may be given with or without `--status`.

**Tests, each seen failing first:**

- graph: drop records `dropped_from`; restore returns an `in-progress` concept to `in-progress` and a `done` one to `done`; each refusal above, with its message naming the concepts;
- a concept with a live dependent cannot be dropped; once the dependent is dropped, it can; a dependent that is `done` still blocks;
- restoring a dependent while its prerequisite is dropped is refused;
- handler, one session: drop then restore is accepted and ends where it began; drop then `completed` is refused; restore then drop is accepted; drop twice is refused the second time; the same source added twice is refused the second time; mint on a concept dropped earlier in the session is refused;
- agenda: a dropped concept's due card is not in `review_items`; it is not the teach concept even if it was in progress; its slip produces no `slipped:` line; after restore, its card is back;
- store: `due_count` excludes a dropped concept's due card;
- CLI, end to end through separate commands: `start`, `concept --status dropped`, `end`; the next `start` has neither the concept nor its card; `concept --status restored`, `end`; the next `start` has both. `--add-source` then `end` leaves the locator in `syllabus.yaml`, and the next agenda's teach concept lists it in `sources`.

**Commit:** `feat(concepts): drop and restore a concept; add a source to a concept`

---

### Task 4: Steering — `seba start --concept`

Parallel. Branch `pr2/steering`.

**Files:**
- Modify: `src/seba/syllabus/graph.py` (new function placed directly after `frontier`), `src/seba/scheduler/agenda.py` (`build_agenda`'s signature, its session type, and the block that builds `ready`; one briefing line placed directly after the `Session type:` lines), `src/seba/cli.py` (`start` only)
- Test: create `tests/test_steering.py`

**Interfaces:**
- Consumes: `frontier` excluding dropped concepts, `Status.DROPPED` (Task 1).
- Produces:
  - `seba.syllabus.graph.check_teachable(s: Syllabus, concept_id: str) -> Concept`
  - `build_agenda(state, profile, today, sources_dir, *, teach: str | None = None) -> Agenda`
  - `seba start GOAL --concept ID`

**Requirements:**

1. `check_teachable` returns the concept if it is in progress or on the frontier. Otherwise it raises `SyllabusError`:
   - unknown concept: `unknown concept: '<id>'`;
   - dropped: `'<id>' is dropped; restore it first`;
   - done: `'<id>' is done; reopen it if the learner wants it taught again`;
   - hard prerequisites not done: `'<id>' is not ready: <a>, <b> must be done first`, naming every unmet one.
2. With `teach` given, `build_agenda` calls `check_teachable` and lets its error through. The session is ordinary, whatever the day would otherwise have been: the learner asked for a concept, and that outranks a synthesis or return-after-lapse session. The named concept is `teach_concept`. The follow-ons are the usual ready list, in its usual order, without the named concept, cut so that the whole list respects `concepts_per_session`.
3. The briefing says so, in one line: `steered: the learner asked for [<id>] today.`
4. With `teach` not given, `build_agenda` behaves exactly as before. Every existing agenda test passes unchanged.
5. `seba start GOAL --concept ID`:
   - refused when a session is already pending, before anything else is looked at: `a session is already in progress for '<goal>' — end or abandon it before choosing a concept`. Exit 1, the pending file untouched;
   - a `SyllabusError` from `check_teachable` is printed and exits 1. No pending file is written.
   - `seba start GOAL` with no `--concept` is unchanged, including resuming.

**Tests, each seen failing first:**

- `check_teachable`: each refusal with its message; an in-progress concept and a frontier concept are returned; two unmet prerequisites are both named;
- agenda: the named concept is taught over an earlier frontier entry and over a concept in progress; with `concepts_per_session: 2` the follow-on is the usual first pick and the named concept is not repeated; on a synthesis day and on a return-after-lapse day the session is ordinary and teaches the named concept; the `steered:` line is present, and absent without `teach`;
- CLI: `start --concept` picks the named concept; it is refused on unmet prerequisites, on a dropped concept, on a done concept, on an unknown concept, and with a session pending; after each refusal no pending file exists (or, for the pending case, the existing one is byte-identical).

To test the dropped case without Task 3, write the concept's status directly into the syllabus the test builds.

**Commit:** `feat(agenda): seba start --concept steers a session to a chosen concept`

---

### Task 5: Direction, running out of syllabus, and the wording of progress

Parallel. Branch `pr2/direction`.

**Files:**
- Modify: `src/seba/scheduler/agenda.py` (in `build_agenda`, only the statement that first builds `lines`, and one new line placed directly before `lines += _stuck_lines(state)`), `src/seba/store/store.py` (`save_tuning` only), `src/seba/cli.py` (`tune` only), `src/seba/models.py` (`View*` models only), `src/seba/ui/view.py`, `src/seba/ui/view_template.html`
- Test: create `tests/test_direction.py`; change `tests/test_agenda.py` and `tests/test_view.py` only where they assert on the old wording

**Interfaces:**
- Consumes: `GoalState.direction`, `GoalMeta.direction`, `Status.DROPPED` (Task 1).
- Produces:
  - `Store.save_tuning(name, settings, emphasis, items, *, direction: str | None = None) -> bool` — `None` leaves the direction as it is
  - `seba tune GOAL --direction TEXT`
  - `ViewStats.concepts_open: int`, `ViewStats.concepts_dropped: int`

**Requirements:**

1. **The briefing opens with the direction.** Its first line is `Direction: <direction>`, left out only if the direction is empty.
2. **Progress wording.** The next line reads `Session <n>. Concepts: 7 done, 2 open, 1 dropped.` Open is every concept that is unseen or in progress. The `, N dropped` part is left out when nothing is dropped. This replaces `Concepts done: 7/9`. Compute these counts where the line is built, so that the top of `build_agenda` is left as it is.
3. **Running out.** When at most one concept is left unseen, dropped concepts not counted, the briefing says so:
   - one left: `nearly out of syllabus: 1 concept left unseen (<id>) — propose what comes next, or confirm with the learner that the goal is finished.`
   - none left: `out of syllabus: no concept left unseen — propose what comes next, or confirm with the learner that the goal is finished.`
   - two or more: no line.
4. **`seba tune GOAL --direction TEXT`** sets the direction in `goal.yaml`. Blank text is refused: `--direction needs text`. It can be combined with the other flags, and every refusal still writes nothing. The output says what changed: `direction: "<old>" → "<new>"`. Setting it to what it already is changes nothing and says `nothing changed`. With no flags, `tune` prints `direction` along with settings and emphasis.
5. **The view.** `ViewStats` gains `concepts_open` and `concepts_dropped`; `concepts_done` and `concepts_total` keep their meaning. `cards_due`, and each dropped concept's own `due`, do not count a dropped concept's cards as due. The page reads `7 done, 2 open, 1 dropped` where it read `7/9`, and shows a dropped concept as dropped, visibly set apart from unseen, in progress and done. Read `view_template.html` in full first and follow how it already styles a status.

**Tests, each seen failing first:**

- agenda: the first line is the direction; it falls back as Task 1 defined and is left out when empty; the progress line in each of its two forms; the running-out line at one unseen and at none, and its absence at two; a dropped concept is not counted as unseen;
- store: `save_tuning` with a direction writes it and commits; with `None` it leaves an existing direction alone;
- CLI: `tune --direction` round-trips through `goal.yaml` and reaches the next `start`'s briefing; blank text is refused and nothing is written; a valid direction with an out-of-range setting writes nothing; the same direction twice says `nothing changed` and makes no commit; `tune` with no flags prints the direction;
- view: the new counts; a dropped concept's due card is not counted; the rendered page contains the new wording and marks the dropped concept.

To test dropped concepts without Task 3, write the concept's status directly into the syllabus the test builds.

**Commit:** `feat(briefing): the goal's direction, running out of syllabus, and progress as done/open/dropped`

---

### Task 6: Tell the tutor — `SKILL.md` and the command table

Runs alone, after Tasks 2 to 5 are merged. Documentation only.

**Files:**
- Modify: `skills/seba-tutor/SKILL.md`, `docs/development.md`

**Interfaces:**
- Consumes: every command, refusal and briefing line from Tasks 1 to 5, as merged.
- Produces: nothing in code.

**Requirements:**

The reader is a model acting as tutor, mid-session, with the learner waiting. Say what is true now and what to do. Keep the file's voice. The code is the authority: quote command flags, refusals and briefing lines as the code produces them.

1. **Command tables**, in both files: `seba extend GOAL --from-file PATH`; `seba concept`'s `--status` with all five values and `--add-source LOCATOR`; `seba start GOAL [--concept ID]`; `seba tune`'s `--direction TEXT`.
2. **Briefing lines:** `Direction:`, the progress line, `steered:`, and the two running-out lines, each with what the tutor does on reading it.
3. **A section "Changing a syllabus"** covering:
   - **Mapping a new source.** It is a conversation. Skim the source's abstract and headings; never load the whole of it. Draft the concepts, name which existing concepts the source reuses, and revise with the learner. Nothing is saved without an explicit yes. Drafting defaults: one to three concepts per source, each named by what the learner could explain without the source in front of them; background the source assumes becomes its own concept and a hard prerequisite, which is how a gap gets closed; sized to a session or two; never carved by section. A source is never a concept.
   - **Saving a mapping:** new concepts through `seba extend`; a source that an existing concept can also be taught from, through `--add-source`.
   - **Dropping and restoring:** what each does, that a concept with live dependents cannot be dropped and the refusal names them, and that nothing is dropped without the learner saying so.
   - **Steering:** when the learner asks for a particular concept, `seba start GOAL --concept ID`, before the session starts; what the refusals mean.
   - **When the direction changes:** record it with `seba tune --direction`, then walk the unseen concepts with the learner and propose drops one at a time.
   - **Running out:** what to do on the running-out lines.
4. **Correct what Task 1 changed.** The skill says that after `--status reopened`, `--status started` for the same concept in the same session is refused. It is now accepted as a repeat. A `completed` on a concept that was never started is now refused at the call. Find every statement the new behaviour makes false and fix it.

Check each sentence you write against the code. Run `make check`, which must still pass.

**Commit:** `docs(skill): changing a syllabus — mapping, dropping, steering, direction`
