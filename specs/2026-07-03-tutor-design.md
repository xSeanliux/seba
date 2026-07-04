# Seba — Design Spec

**Date:** 2026-07-03
**Status:** Approved design, pre-implementation
**Audience:** Implementing agents. Each module section is written to be buildable in isolation against the interfaces defined here.

> **Name:** *seba*, from Egyptian *sbꜣ* — "to teach". The same root gives *sbꜣyt* (the instruction-literature genre: Ptahhotep, Amenemope) and, written 𓇼, also means "star" and "door". A teaching that is a door that is a star. Package, CLI command, and repo are all `seba`.

---

## 1. What this is

Seba is a long-term personal tutor that runs in the terminal. The user converses with it daily; it teaches through guided dialogue and practice questions. Unlike chat-based "learning modes", it owns a **curriculum** (a concept graph synthesized from a textbook's table of contents plus web research) and a **longitudinal learner state** (what the user knows, what's shaky, what's due for review), both stored as plain text in git. Session 40 provably knows what happened in session 1.

First two subjects, built simultaneously to force honest abstraction:

- **Probability** (technical: concept-graph-heavy, teach-heavy sessions)
- **Italian** (language: item-scheduling-heavy, review-heavy sessions)

Explicitly **out of scope**: the learning feed / doomscroll replacer, e-ink rendering, Telegram integration, web UI, full PDF ingestion pipelines. These are future satellites; nothing here may depend on them, but the plain-text state format is the seam they will later attach to.

## 2. Core design principle: the seam

The system is split by what must be deterministic versus what benefits from model judgment:

- **Code owns:** state storage, schema validation, review scheduling (FSRS), syllabus graph operations, session agenda construction, applying state updates.
- **The LLM owns:** syllabus drafting, conducting the teaching dialogue, grading free-form answers, distilling a session into structured outcomes.

The boundary is typed in both directions:

1. **Agenda** (code → LLM): what this session should cover, computed by the scheduler.
2. **Outcome tools** (LLM → code): during the session the tutor records what happens through validated tool calls — `grade_review`, `mint_item`, `update_concept`, `end_session`. Each call is schema-checked at the moment it's made (bad args → immediate retry with the validation error), and applied to in-memory state by code. Grades land while the exchange is fresh; a crash mid-session loses nothing already recorded.

A transcript-level **extraction pass exists only as crash recovery** (`seba extract`): if a session dies before `end_session`, it replays the transcript through the same tool schemas to backfill.

The LLM never edits state files — tools are code functions applying validated updates. Code never generates prose. Every module below is testable without an LLM by injecting synthetic artifacts at this seam.

## 3. Repository layout

```
seba/
├── pyproject.toml            # uv-managed; deps: anthropic, py-fsrs, pydantic, rich, pyyaml, typer
├── README.md
├── src/seba/
│   ├── __init__.py
│   ├── cli.py                # entry points: seba, seba new-goal, seba status
│   ├── config.py             # paths, model ids, API config
│   ├── models.py             # ALL pydantic schemas (single source of truth)
│   ├── store/                # M1 — state persistence
│   │   ├── __init__.py
│   │   └── store.py
│   ├── scheduler/            # M2 — FSRS + agenda building
│   │   ├── __init__.py
│   │   ├── items.py          # FSRS wrapper
│   │   ├── concepts.py       # concept progression (v0: checkbox; v1: ladder)
│   │   └── agenda.py         # agenda builder
│   ├── syllabus/             # M3 — concept graph operations
│   │   ├── __init__.py
│   │   └── graph.py
│   ├── session/              # M4 — LLM harness
│   │   ├── __init__.py
│   │   ├── dialogue.py       # streaming chat loop + tool dispatch
│   │   ├── tools.py          # outcome-tool definitions + handlers
│   │   ├── recovery.py       # seba extract: transcript → backfilled tool calls
│   │   └── prompts/
│   │       ├── system_base.md
│   │       └── recovery.md
│   ├── synthesis/            # M5 — goal + ToC → syllabus.yaml (+ subject profile if missing)
│   │   ├── __init__.py
│   │   ├── synthesize.py
│   │   └── prompts/synthesis.md
│   └── ui/                   # M6 — terminal REPL
│       ├── __init__.py
│       └── repl.py
├── subjects/                 # bundled subject profiles — DATA, not code
│   ├── probability/
│   │   ├── profile.yaml      # scheduling knobs (see §4.5)
│   │   └── overlay.md        # teaching-style prompt overlay
│   ├── italian/
│   │   ├── profile.yaml
│   │   └── overlay.md
│   └── _templates/           # generic technical / language starters for new subjects
│       ├── technical/ · language/
├── tests/                    # mirrors src/seba/; seam tests need no LLM
│   ├── test_store.py
│   ├── test_scheduler.py
│   ├── test_syllabus.py
│   ├── test_extraction_schema.py
│   └── fixtures/             # synthetic agendas, outcomes, transcripts
└── data/                     # user data — gitignored by the code repo,
    │                         # ITSELF a separate git repo (learning history)
    ├── goals/
    │   ├── probability/
    │   │   ├── goal.yaml         # goal metadata + subject preset name
    │   │   ├── syllabus.yaml     # concept graph
    │   │   ├── items.jsonl       # FSRS cards, one JSON object per line
    │   │   ├── notes.md          # tutor's freeform learner notes (v0 mastery carrier)
    │   │   └── sessions/
    │   │       ├── 001.md        # human-readable distillation
    │   │       └── 001.outcomes.yaml  # machine-readable outcomes (audit trail)
    │   └── italian/ …
    └── sources/
        └── blitzstein/
            ├── toc.md            # table of contents (user-provided)
            └── ch09.md           # optional chapter texts, referenced by syllabus
```

Conventions:

- All schemas live in `models.py` as pydantic models. No module defines its own dict shapes.
- Modules import strictly downward: `ui → session → scheduler → store`; `synthesis` and `syllabus` are siblings used by `cli`. No circular imports.
- Prompts are markdown files with `{placeholder}` substitution, not Python string literals — editable without touching code.
- `data/` location configurable via `SEBA_DATA_DIR`, default `~/seba-data`. The store commits to the data repo after every session (`git add -A && git commit`).

## 4. Data model (pydantic, in `models.py`)

### 4.1 Syllabus — `syllabus.yaml`

```yaml
goal: "measure-theoretic probability"
subject: probability          # selects prompt preset
concepts:
  - id: conditional-expectation-as-rv
    name: "Conditional expectation as a random variable"
    prereqs: [conditional-probability, random-variables]
    sources: ["blitzstein/ch09.md#9.2", "https://…"]   # optional
    status: unseen            # unseen | in-progress | done   (v0)
    est_sessions: 2
```

Rules (enforced by `syllabus/graph.py`): ids kebab-case unique; prereq edges must form a DAG (validated on load, cycle → hard error naming the cycle); `frontier()` = concepts whose prereqs are all `done`, ordered by declaration order.

### 4.2 Items — `items.jsonl`

One JSON object per line (append-friendly, diff-friendly):

```json
{"id": "it-041", "concept": "law-of-total-probability", "type": "recall",
 "front": "State the law of total probability", "back": "P(A) = Σ P(A|Bᵢ)P(Bᵢ) …",
 "fsrs": {"stability": 4.2, "difficulty": 6.1, "due": "2026-07-05", "state": "review", "reps": 3, "lapses": 0},
 "created": "2026-06-28", "suspended": false}
```

`type` ∈ `recall | apply | cloze | produce | recognize`. The `fsrs` block is owned entirely by `py-fsrs`; no other module reads its internals — only `due` for filtering.

### 4.3 Agenda (code → LLM; never persisted except in logs)

```python
class Agenda(BaseModel):
    goal: str
    subject: str
    session_number: int
    briefing: str                 # human-readable summary assembled by scheduler
    review_items: list[ReviewItem]    # id, type, front, back
    teach_concept: TeachConcept | None  # id, name, source_excerpts: list[str], guidance: str
    practice_quota: int           # target new practice questions
    pace_hint: Literal["push-harder", "steady", "step-back"]
```

`briefing` composition: session number; concepts done/in-progress; verbatim recent `notes.md` excerpts; last session's `next_session_hint`.
`pace_hint` from recent practice success rate in outcomes history: >90 % → push-harder, <70 % → step-back, else steady.

### 4.4 Outcome tools (LLM → code, validated per call)

The tutor records outcomes via tool calls during the session. Tool arg schemas (pydantic models in `models.py`; tool definitions generated from them in `session/tools.py`):

```python
class GradeReview(BaseModel):      # call immediately after a review exchange resolves
    id: str                        # must be in agenda.review_items, else rejected
    grade: Literal["again", "hard", "good", "easy"]
    note: str | None = None

class MintItem(BaseModel):         # a fact/skill worth retaining a month from now
    concept: str                   # must exist in syllabus
    type: ItemType
    front: str
    back: str

class UpdateConcept(BaseModel):
    id: str                        # must exist in syllabus
    status_change: Literal["started", "completed"] | None = None
    note: str | None = None        # misconceptions, strengths — freeform

class EndSession(BaseModel):       # exactly once, at session close
    summary: str                   # 3–6 sentences → sessions/NNN.md body
    next_session_hint: str
```

Handler rules: invalid args or unknown ids → tool returns the validation error, model retries in-flow; `mint_item` capped at 10/session (excess rejected with explanation); all accepted calls accumulate in an in-memory `SessionRecord`, applied to state and persisted by the store only at save time (or on crash, whatever was accepted so far). `SessionRecord` also serializes to `sessions/NNN.outcomes.yaml` as the audit trail — same artifact as before, now built incrementally.

### 4.5 Subject profiles — data, not code

A subject = directory under `subjects/` (bundled) or `data/subjects/` (user-created):

```yaml
# subjects/italian/profile.yaml
name: italian
kind: language                    # template family it was derived from
max_reviews_per_session: 20
item_types: [recognize, produce, cloze]
session_shape: review-heavy      # briefing/agenda emphasis
```

plus `overlay.md`, the teaching-style prompt fragment appended to `system_base.md`. Bundled: `probability` (kind: technical, teach-heavy, item types recall/apply), `italian`. **New subjects require zero code:** `seba new-goal astronomy` with no matching profile → synthesis drafts `profile.yaml` + `overlay.md` from the closest `_templates/` family, opens both in `$EDITOR` alongside the syllabus. *(v0 interim: auto-drafting ships with agentic synthesis in v1; until then a missing profile is a friendly error pointing at the template to copy.)*

## 5. Modules

Each module lists: purpose, public interface, dependencies, acceptance criteria. Implementing agents should treat interfaces as contracts — internals are free.

### M1 `store` — state persistence

**Purpose:** the only module that touches disk under `data/`.

```python
class Store:
    def __init__(self, data_dir: Path): ...
    def list_goals(self) -> list[GoalSummary]           # name, subject, session_count, due_count
    def load_goal(self, name: str) -> GoalState          # syllabus + items + notes + last hint
    def save_session(self, name: str, record: SessionRecord,
                     transcript: str, updated: GoalState) -> None
    # writes sessions/NNN.md + NNN.outcomes.yaml, rewrites items.jsonl,
    # appends concept notes to notes.md, updates syllabus statuses, git-commits
    def create_goal(self, name: str, syllabus: Syllabus, subject: str) -> None
```

**Depends on:** models only.
**Acceptance:** round-trip property — `load(save(x)) == x`; save is atomic (write temp, rename); malformed YAML/JSONL on load → error naming file and line, never silent default; every `save_session` produces exactly one git commit in the data repo with message `probability: session 12`.

### M2 `scheduler` — FSRS + agenda

**Purpose:** everything time- and evidence-based.

```python
def due_items(items: list[Item], today: date, limit: int) -> list[Item]
    # overdue first (most overdue first), then due-today; never exceeds limit
def apply_review(item: Item, grade: Grade, today: date) -> Item      # py-fsrs wrapper
def mint_item(new: NewItem, today: date) -> Item                     # new card, FSRS init state
def build_agenda(goal: GoalState, preset: SubjectPreset, today: date) -> Agenda
```

`build_agenda` logic: pick due items up to `preset.max_reviews_per_session`; pick teach concept = first `in-progress` concept, else first frontier concept, else `None` (all done → review-only session); pull `source_excerpts` by reading files referenced in the concept's `sources` (silently skip missing files, note in briefing); compute `pace_hint` from the last 3 sessions' review-grade history.

**Depends on:** models, py-fsrs, store (read-only, via passed-in `GoalState`).
**Acceptance:** deterministic — same state + same date → identical agenda; simulation test: 30 synthetic days of `good` grades → item intervals grow monotonically; `again` grade → item due within 1 day; concept selection respects DAG (never teaches concept with unmet prereqs).

### M3 `syllabus` — graph operations

```python
def load_syllabus(path: Path) -> Syllabus        # validates DAG, unique ids
def frontier(s: Syllabus) -> list[Concept]
def apply_status(s: Syllabus, concept_id: str, status: Status) -> Syllabus
```

**Acceptance:** cycle detection with cycle named in error; frontier correct on fixture graphs (diamond, chain, disconnected components).

### M4 `session` — LLM harness

**Purpose:** conduct the dialogue; dispatch outcome tools; recover crashed sessions.

```python
def run_session(agenda: Agenda, profile: SubjectProfile, io: SessionIO) -> tuple[SessionRecord, str]
    # returns (accumulated outcomes, full transcript);
    # io abstracts input/output so tests can script a session
def recover_session(transcript: str, agenda: Agenda) -> SessionRecord
    # `seba extract` path: replays a dead session's transcript through the same
    # tool schemas with a cheaper model to backfill a SessionRecord
```

Dialogue loop: streaming responses; system prompt = `system_base.md` + subject `overlay.md` + serialized agenda; tools = the four outcome tools (§4.4) plus `fetch_source(ref)`; tool results feed back in-flow (validation errors included, so the model self-corrects). Session ends on `Ctrl-D`, `/done`, or the model calling `end_session`; `/skip` moves past a stuck exchange. The grading rubric lives in the `grade_review` tool description: wrong or no recall → `again`; correct with significant hesitation/hints → `hard`; correct → `good`; instant and confident → `easy`. Grades include `skipped` for items the session never reached — FSRS state untouched, item stays due.

**Deterministic gates** (code checkpoints in the loop — the dialogue is free in the middle, gated at the boundaries):

- *Session-end gate:* an `end_session` call (or user `/done`) is rejected while agenda review items remain ungraded; the handler returns the list of missing ids and the model must `grade_review` each (or mark `skipped`) before the close is accepted. On `Ctrl-D`/hard exit the gate can't run — the incomplete path (§6) covers it.
- *Save-time invariants:* exactly one accepted `end_session`; every accepted grade maps to an agenda item; concept statuses only move along legal edges (`unseen→in-progress→done`). Violation → session saved `INCOMPLETE`, state never corrupted.

Transcript saved verbatim to `sessions/NNN.transcript.md` for audit, **never fed into future sessions** (distillation is the memory). If a session dies before `end_session`, accepted tool calls are still persisted; `seba extract` backfills the remainder via `recover_session` (model: `claude-haiku-4-5`).

**Depends on:** models, anthropic SDK, prompts.
**Acceptance:** tool handlers unit-tested (valid, invalid-id, over-cap, double `end_session`); `run_session` drivable end-to-end by a scripted `SessionIO` with a mocked model emitting tool calls; `recover_session` tested against 3+ fixture transcripts with known correct records.

### M5 `synthesis` — ToC → syllabus

**Purpose:** `seba new-goal <name> --subject <profile> --toc <path>` → draft `syllabus.yaml` → open in `$EDITOR` → validate on save (DAG check; on failure, reopen with errors as YAML comments) → `store.create_goal`. If no matching subject profile exists, additionally draft `profile.yaml` + `overlay.md` from the closest `_templates/` family and open those for editing too (§4.5).

v0: single LLM call with the ToC and the synthesis prompt (asks for: concept granularity of 1–3 sessions each, prereq edges that may reorder or cut across chapters, inserted prerequisite concepts the book assumes, source mappings to ToC sections). **v1 upgrade (same interface):** agentic loop with web search — fetch other syllabi/ToCs for the same subject, propose supplementary sources per concept.

**Acceptance:** generated YAML always passes `load_syllabus` or the editor-retry loop engages; works from a plain markdown ToC with no other input.

### M6 `ui` — REPL

**Purpose:** thin. `tutor` → goal picker with due counts → briefing card → chat (rich-rendered markdown, streaming) → on exit, "session saved: 2 items minted, 4 reviewed, conditional-expectation → in-progress" one-liner. `seba status` → per-goal table: concepts done/total, items due today/this week, last session date.

**Depends on:** session, scheduler, store.
**Acceptance:** manual; must handle terminal resize and long streamed lines without corruption (rich handles this — don't hand-roll).

## 6. Session lifecycle (end-to-end, turn level)

```
seba
 └─ store.list_goals() → picker → store.load_goal("probability")
 └─ scheduler.build_agenda(state, profile, today)
 └─ ui: briefing card ("session 12 · 4 due · today: conditional expectation")
 └─ session.run_session(...):
      1. tutor opens with continuity ("last time…"), poses first due review
      2. per review exchange:
           learner answers → corrective feedback, misconception named
           → grade_review(id, grade, note?) recorded silently → next review
      3. reviews done → teach segment on agenda.teach_concept:
           worked example → faded practice → independent practice
           attempts drive update_concept(...) / mint_item(...) as warranted
      4. tangents allowed anytime; tutor may fetch_source(ref)
      5. learner types /done (or time budget) → tutor gives verbal recap
           → calls end_session(summary, next_session_hint)
 └─ scheduler.apply_review / mint_item finalize FSRS state from SessionRecord
 └─ syllabus.apply_status per concept outcome
 └─ store.save_session(...)                     ← one git commit
 └─ ui receipt: "4 reviewed · 2 minted · conditional-expectation → in-progress"
```

Failure handling: outcome tools are validated and accepted **during** the session, so a crash (API death, Ctrl-C) loses nothing already recorded — the partial transcript and partial `SessionRecord` are saved with an `INCOMPLETE` marker, and `seba extract <goal> <n>` backfills anything after the last accepted call via `recover_session`. A session's learning is never lost to a parse error.

## 7. Prompts (contracts, not final text)

**`system_base.md`** (subject-agnostic — all subject character lives in overlays) must establish: (a) you are a long-term tutor mid-relationship, the agenda's briefing is your memory — reference it naturally; (b) pedagogy policy: for new concepts use worked example → faded scaffolding → independent practice, target roughly 85 % success, honor `pace_hint`; ask "why" / "convince me" follow-ups; name misconceptions explicitly when correcting; (c) weave review items in conversationally near the start, get an actual answer attempt before revealing, and call `grade_review` the moment each resolves; (d) tangents are allowed and good — follow them, record anything durable via `update_concept`/`mint_item`; (e) never dump an answer the learner could produce with one more hint; (f) close by recapping aloud, then call `end_session`.

**`subjects/probability/overlay.md`**: notation in Unicode math (σ-algebra, 𝔼[X|Y]) with LaTeX in fences only for complex derivations; practice = compute / prove-sketch / find-counterexample; push for statements *and* intuitions.

**`subjects/italian/overlay.md`**: conduct increasing fractions of the session in Italian as the learner advances (briefing indicates level); practice = production over recognition; correct errors by recasting, then drill the pattern.

**Tool descriptions** carry their own contracts: `grade_review` embeds the grading rubric (§M4); `mint_item` embeds "only facts/skills worth retaining a month from now, not session-local scaffolding".

**`recovery.md`**: input = transcript + agenda; drives `recover_session` to emit the same tool calls the live session should have made.

## 8. Mastery model — versioned

- **v0 (build this):** concepts are checkboxes (`unseen/in-progress/done`) driven by `ConceptOutcome.status_change`; nuance lives in `notes.md` free text, surfaced verbatim in briefings; items carry all quantitative memory via FSRS.
- **v1:** replace checkbox with the evidence ladder (`introduced → practicing → solid → mastered`; promotion on counted correct attempts across sessions, demotion on 2 consecutive failures, `mastered` requires a probe ≥7 days after `solid`). Only `scheduler/concepts.py` and the `UpdateConcept` schema change.
- **post-v1 (optional):** BKT posterior per concept at the same seam.

## 8a. Context budget

The scheduler is the context firewall: the model sees a *selection*, never the state. Rules, enforced in `build_agenda`:

- **Items:** only FSRS-due items, capped by `max_reviews_per_session`. `items.jsonl` (potentially thousands of cards) never enters context.
- **Syllabus:** the briefing names counts + the current frontier (≤10 concept names), never the full graph.
- **Notes:** `notes.md` is structured per-concept (`## concept-id` sections, newest first). The briefing includes only notes for concepts in this session's scope — the review items' concepts, the teach concept and its direct prereqs — and at most the 3 newest notes per concept. Total briefing budget: ~1,000 tokens; scheduler truncates oldest-first beyond it and appends "(older notes omitted)".
- **Sources:** excerpts resolved at section granularity (`ch09.md#9.2`), total excerpt budget ~4,000 tokens; over budget → keep the teach concept's primary source, drop the rest, note it in the agenda.
- **History:** last session's `next_session_hint` only. Transcripts are never fed forward (§M4).
- **Consolidation (v1):** when a concept's notes exceed 5 entries, a maintenance pass (`seba gc`, cheap model) rewrites them into one distilled note — same move as session distillation, applied to the notes themselves.

Net effect: session context ≈ system prompt (~2k) + agenda (~1–5k) + live dialogue. Independent of how many months of history or thousands of items exist.

## 9. Build order

**Milestone v0 — the loop (target: usable for real study).**

1. `models.py` + M1 store + M3 syllabus, with tests. *(No LLM needed.)*
2. M2 scheduler, with the 30-day simulation test. *(No LLM needed.)*
3. M4 session: dialogue loop + outcome tools + recovery, fixture-tested.
4. M5 synthesis (single-call version, incl. profile drafting) + M6 REPL + `cli.py`.
5. Dogfood gate: create both real goals (probability + Italian), run 3 real sessions each across ≥3 distinct days. Success = session N+1's briefing correctly reflects session N (shaky concepts resurface, mastered items sleep, frontier advances).

Steps 1–2 and 3 are parallelizable across agents once `models.py` is merged; `models.py` itself must be a single owned artifact, first.

**Milestone v1 — depth (order by observed pain, not this list):** concept ladder · `seba drill <goal>` review-only rapid-fire session mode (same agenda machinery with `teach_concept: None`, terse drill overlay — needed once Italian's due queue outgrows conversational weaving) · agentic synthesis with web search · pace model from logged history · `seba extract` polish · TUI upgrade (textual).

## 10. Testing strategy

- Seam tests (majority): synthetic `GoalState` → agenda assertions; synthetic `SessionRecord` → state assertions; tool-handler validation paths. Zero API cost, fully deterministic.
- Fixture transcripts for recovery — plus a scripted-session tier where a mocked model emits tool calls; the one place live LLM behavior is load-bearing runs in a separate `pytest -m llm` tier (not CI-default).
- The 30-day FSRS simulation (M2) doubles as the BKT-sim spike from the project docs.
- Dogfooding is the real test (§9 step 5); instrument nothing, read the git log of `data/`.

## 11. Risks

| Risk | Mitigation |
|------|-----------|
| Tutor misgrades or forgets to call tools → memory corrupts/gaps silently | Rubric in tool descriptions; session-end gate blocks close until every agenda item is graded or `skipped`; save-time invariants; `*.outcomes.yaml` audit trail; everything human-editable |
| Tutor lectures instead of dialogues | System-prompt policy + dogfood gate; cheap to iterate, prompts are files |
| Item minting floods (too many cards) | Cap 10/session; `suspended` flag; "worth retaining in a month" rubric |
| Syllabus draft quality poor | Human edits in `$EDITOR` before first session is a hard gate, not optional |
| Two subjects double the prompt-tuning surface | Shared base prompt; overlays kept short; dogfood both from day one (that's the point) |

## 12. Configuration defaults

- Dialogue model: `claude-sonnet-5` (config: `SEBA_MODEL`); recovery: `claude-haiku-4-5` (config: `SEBA_RECOVERY_MODEL`).
- Python ≥3.12, `uv` for env/deps. Deps: `anthropic`, `fsrs` (py-fsrs), `pydantic` v2, `rich`, `pyyaml`, `typer`. No others without cause.
- FSRS parameters: library defaults; desired retention 0.9. Revisit only with real log data.
