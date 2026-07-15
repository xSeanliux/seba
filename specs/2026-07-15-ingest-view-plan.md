# Seba Ingest + View Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Two extensions to the tutor loop: (A) `seba ingest`/`seba sources` — turn a saved PDF (or a tutor-written web manifest) into an addressable **manifest of bounded locators** the syllabus can reference; (B) `seba view` — render a goal's concept graph, card counts, and FSRS status as a **self-contained HTML file** from a bundled template, openable in a browser.

**Architecture:** Both features follow seba's seam: the deterministic CLI does mechanical, stateful work (read a PDF outline, compute view data, inject JSON into a static template); Claude Code does judgment work (picking locators when drafting a syllabus, running `seba view` after a session). No network in the Python core — a web link is fetched by the tutor, never by seba. The view template ships inside the package with inline CSS/JS (no CDN); the CLI only injects a JSON data blob.

**Tech Stack:** Python ≥3.12, uv, pydantic v2, typer, pyyaml, **pypdf (new dep, T3)**, graphlib (stdlib), importlib.resources (stdlib). No JS build step — the template is a hand-written static file.

## Global Constraints

- Repo: `~/Desktop/Projects/seba`. Branch from `main` (at `6b2fb0b`, 72 tests green). Suggested branch: `feat/ingest-view`. PR base `main`. Commit locally; push/PR at the end.
- Deps after T3 EXACTLY: `fsrs`, `pydantic>=2`, `pyyaml`, `rich`, `typer`, `pypdf`; dev: `pytest`, `ruff`, `ty`. Nothing else.
- All schemas live in `src/seba/models.py`. No module defines its own dict shapes — the view data blob and the manifest are pydantic models.
- Imports strictly downward: `cli → session → scheduler → store`; `syllabus`, `ingest`, `ui` are siblings used by `cli`. No circular imports.
- Loud failures: malformed manifests raise `IngestError` naming the file; CLI failures print the reason to stderr and exit non-zero; never silently default. One exception, by design: a malformed *entry inside a PDF outline* is skipped (outlines are wild in practice) — but a whole-PDF read failure is loud.
- Zero network and no API key anywhere, including tests. `seba ingest` takes a **local path only** — URL acquisition is the tutor's job (documented in SKILL.md, T6).
- The view template is **self-contained**: inline CSS + JS, no external requests of any kind. The CLI's only templating operation is replacing the literal token `__SEBA_DATA__` with a JSON blob.
- Run every gate with `make check` (ruff + format + ty + pytest). Commit after each green cycle, conventional-commit subjects. If `make fmt` fails, run `make format` and include the result in the same commit.
- CLI contract added by this plan (T6 documents it; do not rename):
  - `seba ingest PATH [--name NAME]` — local PDF → `sources/<name>/book.pdf` + `manifest.yaml`; prints one locator line per section; exit 1 + reason on unreadable input.
  - `seba sources [NAME]` — list locator lines from all (or one) manifests; friendly message when none.
  - `seba view GOAL [--json] [--open]` — writes `goals/<goal>/view.html` and prints its path; `--json` prints the ViewData JSON instead; `--open` also opens it in the default browser.

## Orchestrator briefing (read this first if you are the PM agent)

**Repo state at plan time (2026-07-15):** `main` @ `6b2fb0b`, working tree clean, `make check` green (72 passed). No open PRs.

**Worker model:** Sonnet-class agents, one fresh implementer per task, task review after each (spec + quality), final whole-branch review before PR.

**Execution model (lesson from PR #3): sequential implementers on ONE branch, in task-number order.** Do NOT use worktree isolation — worktree subagents branch from `main` and lose prior tasks' files (this bit every agent in PRs #1–2). T2∥T3 and nothing else are file-disjoint; parallelism is allowed ONLY there and ONLY if both workers operate in the same checkout on the same branch without committing concurrently — when in doubt, run them sequentially. Everything else is strictly sequential.

**Task DAG:**

```
main (6b2fb0b)
 └─ T1 models (both features' schemas)
     ├─ T2 view data builder (ui/view.py)      ── file-disjoint ──┐
     ├─ T3 ingest module (ingest.py) + pypdf   ── file-disjoint ──┤
     │                                                            ├─ T4 view template + `seba view` CLI
     │                                                            └─ T5 `seba ingest`/`seba sources` CLI (AFTER T4 — both edit cli.py)
     └───────────────────────────────────────────────────────────── T6 SKILL.md + docs
T7 dogfood — HUMAN-GATED: stop and hand back to the user.
```

**Worker prompt recipe:** give each worker its full task section + the Global Constraints block + nothing else. Interfaces blocks define what neighbors expect — workers must not rename anything listed there. A worker whose "expect PASS" step fails after 2 fix attempts stops and reports the failing output verbatim; PM decides.

**Design decisions already made (do not relitigate):**
1. `seba ingest` reads **local PDFs only** and never touches the network. A URL is resolved by the tutor: URL→PDF gets downloaded (e.g. `curl -L -o /tmp/x.pdf …`) then ingested; URL→website gets a hand-written `manifest.yaml` (kind `web`, one section per page URL) written by the tutor — the CLI validates and lists it via `seba sources`.
2. PDFs are **kept as PDFs** and referenced by page range (`<name>/book.pdf p.12-40`). No text extraction, no markdown conversion — Claude Code reads PDF page ranges natively at teach time.
3. A PDF with no outline yields `sections: []` plus a printed hint; the tutor then maps page ranges from the book's ToC by hand. Ingest must not guess.
4. The view graph is a **hand-rolled layered SVG** in the template's inline JS (layer = longest prereq path, computed in Python). No mermaid, no CDN, no JS deps.
5. `view.html` is written into the goal directory in the data repo and may ride into a later session commit — accepted, same policy as `session.pending.yaml`.
6. `seba view --open` uses `typer.launch` (cross-platform) — not `open`/`xdg-open` subprocess calls.

---

### Task 1: Models for both features

**Files:**
- Modify: `src/seba/models.py` (append five models after `PendingSession`)
- Test: `tests/test_models.py` (append)

**Interfaces:**
- Consumes: existing `Status`, `Grade` StrEnums, `BaseModel`, `Field`, `date`, `Literal` (all already imported in models.py).
- Produces (T2–T5 depend on these EXACT names and fields):
  - `SourceSection(title: str, page_start: int | None = None, page_end: int | None = None, url: str | None = None)`
  - `SourceManifest(name: str, kind: Literal["pdf", "web"], file: str | None = None, pages: int | None = None, sections: list[SourceSection] = [])`
  - `ViewConcept(id: str, name: str, status: Status, layer: int, prereqs: list[str], cards: int, due: int, est_sessions: int)`
  - `ViewStats(concepts_done: int, concepts_total: int, cards_total: int, cards_due: int, frontier: list[str])`
  - `ViewData(goal: str, subject: str, session_number: int, generated: date, stats: ViewStats, concepts: list[ViewConcept], recent_grades: list[Grade])`

- [ ] **Step 1: Write the failing test** — append to `tests/test_models.py`:

```python
def test_source_manifest_roundtrip():
    from seba.models import SourceManifest, SourceSection

    m = SourceManifest(
        name="alg",
        kind="pdf",
        file="alg/book.pdf",
        pages=320,
        sections=[SourceSection(title="1. Groups", page_start=12, page_end=40)],
    )
    again = SourceManifest.model_validate(m.model_dump(mode="json"))
    assert again == m
    web = SourceManifest(
        name="ct",
        kind="web",
        sections=[SourceSection(title="Ch 3", url="https://example.org/ch3")],
    )
    assert web.file is None and web.sections[0].url == "https://example.org/ch3"


def test_view_data_shape():
    from datetime import date

    from seba.models import ViewConcept, ViewData, ViewStats

    v = ViewData(
        goal="prob",
        subject="probability",
        session_number=3,
        generated=date(2026, 7, 15),
        stats=ViewStats(
            concepts_done=1,
            concepts_total=2,
            cards_total=5,
            cards_due=2,
            frontier=["bayes"],
        ),
        concepts=[
            ViewConcept(
                id="bayes",
                name="Bayes",
                status="unseen",
                layer=1,
                prereqs=["sample-spaces"],
                cards=3,
                due=2,
                est_sessions=2,
            )
        ],
        recent_grades=["good"],
    )
    blob = v.model_dump(mode="json")
    assert blob["generated"] == "2026-07-15"          # JSON-safe for the template
    assert blob["concepts"][0]["status"] == "unseen"  # enum -> plain string
```

- [ ] **Step 2: Run to verify it fails** — `uv run pytest tests/test_models.py -v` — Expected: FAIL (ImportError: `SourceManifest`).

- [ ] **Step 3: Implement** — append to `src/seba/models.py` (after `PendingSession`; `Literal`, `date`, `Field`, `Status`, `Grade` are already in scope):

```python
class SourceSection(BaseModel):
    title: str
    page_start: int | None = None  # 1-based, pdf manifests
    page_end: int | None = None
    url: str | None = None  # web manifests


class SourceManifest(BaseModel):
    name: str
    kind: Literal["pdf", "web"]
    file: str | None = None  # e.g. "alg/book.pdf", relative to sources/
    pages: int | None = None
    sections: list[SourceSection] = Field(default_factory=list)


class ViewConcept(BaseModel):
    id: str
    name: str
    status: Status
    layer: int  # longest prereq path from a root; drives graph column
    prereqs: list[str]
    cards: int
    due: int
    est_sessions: int


class ViewStats(BaseModel):
    concepts_done: int
    concepts_total: int
    cards_total: int
    cards_due: int
    frontier: list[str]


class ViewData(BaseModel):
    goal: str
    subject: str
    session_number: int
    generated: date
    stats: ViewStats
    concepts: list[ViewConcept]
    recent_grades: list[Grade]
```

- [ ] **Step 4: Gate and commit**

```bash
make check
git add -A && git commit -m "feat: models for source manifests and goal view data"
```

---

### Task 2: View data builder (`src/seba/ui/view.py`)

**Files:**
- Create: `src/seba/ui/view.py`
- Test: `tests/test_view.py` (created here; T4 appends to it)

**Interfaces:**
- Consumes: T1's `ViewConcept`, `ViewStats`, `ViewData`; existing `GoalState`, `Status`, `syllabus.graph.frontier`.
- Produces (T4 depends on these EXACT names):
  - `build_view_data(state: GoalState, today: date) -> ViewData`
  - Layer rule: `layer = 0` for a concept with no prereqs, else `1 + max(prereq layers)`.
  - Due rule (mirror of `store.list_goals`): item counts as due iff `not suspended and str(fsrs["due"])[:10] <= today.isoformat()`.

- [ ] **Step 1: Write the failing test** — create `tests/test_view.py`:

```python
from datetime import date

from seba.models import Concept, GoalState, Item, Syllabus
from seba.ui.view import build_view_data

TODAY = date(2026, 7, 15)


def state(concepts, items=()):
    return GoalState(
        name="prob",
        subject="probability",
        syllabus=Syllabus(goal="prob", subject="probability", concepts=list(concepts)),
        items=list(items),
        session_number=3,
        recent_grades=["good", "again"],
    )


def item(id, concept, due="2020-01-01T00:00:00+00:00", suspended=False):
    return Item(
        id=id,
        concept=concept,
        type="recall",
        front="f",
        back="b",
        fsrs={"due": due},
        created=TODAY,
        suspended=suspended,
    )


def test_layers_and_frontier():
    s = state(
        [
            Concept(id="a", name="A", status="done"),
            Concept(id="b", name="B", prereqs=["a"]),
            Concept(id="c", name="C", prereqs=["a", "b"]),
        ]
    )
    v = build_view_data(s, TODAY)
    by = {c.id: c for c in v.concepts}
    assert (by["a"].layer, by["b"].layer, by["c"].layer) == (0, 1, 2)
    assert v.stats.frontier == ["b"]  # a done, b unlocked, c blocked by b
    assert v.stats.concepts_done == 1 and v.stats.concepts_total == 3


def test_card_counts_and_due():
    s = state(
        [Concept(id="a", name="A")],
        [
            item("it-1", "a"),                                  # overdue
            item("it-2", "a", due="2099-01-01T00:00:00+00:00"), # future
            item("it-3", "a", suspended=True),                  # suspended: never due
        ],
    )
    v = build_view_data(s, TODAY)
    [c] = v.concepts
    assert (c.cards, c.due) == (3, 1)
    assert (v.stats.cards_total, v.stats.cards_due) == (3, 1)
    assert v.generated == TODAY and v.recent_grades == ["good", "again"]
```

- [ ] **Step 2: Run to verify it fails** — `uv run pytest tests/test_view.py -v` — Expected: FAIL (no module `seba.ui.view`).

- [ ] **Step 3: Implement** — create `src/seba/ui/view.py`:

```python
from datetime import date
from graphlib import TopologicalSorter

from seba.models import GoalState, Status, ViewConcept, ViewData, ViewStats
from seba.syllabus.graph import frontier


def build_view_data(state: GoalState, today: date) -> ViewData:
    concepts = state.syllabus.concepts
    by_id = {c.id: c for c in concepts}
    order = TopologicalSorter({c.id: set(c.prereqs) for c in concepts}).static_order()
    layer: dict[str, int] = {}
    for cid in order:
        layer[cid] = 1 + max((layer[p] for p in by_id[cid].prereqs), default=-1)

    cutoff = today.isoformat()

    def is_due(i) -> bool:
        return not i.suspended and str(i.fsrs.get("due", ""))[:10] <= cutoff

    view_concepts = []
    for c in concepts:
        cards = [i for i in state.items if i.concept == c.id]
        view_concepts.append(
            ViewConcept(
                id=c.id,
                name=c.name,
                status=c.status,
                layer=layer[c.id],
                prereqs=c.prereqs,
                cards=len(cards),
                due=sum(1 for i in cards if is_due(i)),
                est_sessions=c.est_sessions,
            )
        )

    stats = ViewStats(
        concepts_done=sum(c.status == Status.DONE for c in concepts),
        concepts_total=len(concepts),
        cards_total=len(state.items),
        cards_due=sum(1 for i in state.items if is_due(i)),
        frontier=[c.id for c in frontier(state.syllabus)],
    )
    return ViewData(
        goal=state.name,
        subject=state.subject,
        session_number=state.session_number,
        generated=today,
        stats=stats,
        concepts=view_concepts,
        recent_grades=state.recent_grades,
    )
```

- [ ] **Step 4: Gate and commit**

```bash
make check
git add -A && git commit -m "feat: goal view data builder (layers, frontier, card/due counts)"
```

---

### Task 3: Ingest module (`src/seba/ingest.py`) + pypdf

**Files:**
- Modify: `pyproject.toml` via `uv add pypdf`
- Create: `src/seba/ingest.py`
- Test: `tests/test_ingest.py`

**Interfaces:**
- Consumes: T1's `SourceManifest`, `SourceSection`.
- Produces (T5 depends on these EXACT names):
  - `class IngestError(Exception)`
  - `ingest_pdf(pdf: Path, sources_dir: Path, name: str) -> SourceManifest` — copies the PDF to `sources_dir/<name>/book.pdf`, writes `sources_dir/<name>/manifest.yaml`, returns the manifest. Raises `IngestError` (naming the input file) if the PDF is unreadable.
  - `load_manifest(path: Path) -> SourceManifest` — raises `IngestError` naming the file on malformed content.
  - `iter_manifests(sources_dir: Path) -> list[SourceManifest]` — every `*/manifest.yaml`, sorted; `[]` if the dir doesn't exist.
  - `locator(m: SourceManifest, s: SourceSection) -> str` — `"<file> p.<start>-<end>"` for pdf, the section's `url` for web.
  - Section pages are **1-based inclusive**; section end = (next outline entry's start − 1), last section ends at the last page; a malformed single outline entry is skipped, never fatal.

- [ ] **Step 1: Add the dependency**

```bash
uv add pypdf
```

- [ ] **Step 2: Write the failing test** — create `tests/test_ingest.py`:

```python
from pathlib import Path

import pytest
import yaml
from pypdf import PdfWriter

from seba.ingest import IngestError, ingest_pdf, iter_manifests, load_manifest, locator
from seba.models import SourceManifest, SourceSection


def make_pdf(path: Path, pages: int = 6, outline: bool = True) -> None:
    w = PdfWriter()
    for _ in range(pages):
        w.add_blank_page(width=200, height=200)
    if outline:
        w.add_outline_item("1. Groups", 0)      # pdf pages are 0-based here
        w.add_outline_item("2. Rings", 3)
    with path.open("wb") as f:
        w.write(f)


def test_ingest_pdf_with_outline(tmp_path):
    pdf = tmp_path / "Algebra Book.pdf"
    make_pdf(pdf)
    m = ingest_pdf(pdf, tmp_path / "sources", "alg")
    assert m.kind == "pdf" and m.pages == 6 and m.file == "alg/book.pdf"
    assert [(s.title, s.page_start, s.page_end) for s in m.sections] == [
        ("1. Groups", 1, 3),   # 1-based, ends where the next section starts
        ("2. Rings", 4, 6),    # last section runs to the final page
    ]
    assert (tmp_path / "sources" / "alg" / "book.pdf").exists()
    on_disk = load_manifest(tmp_path / "sources" / "alg" / "manifest.yaml")
    assert on_disk == m
    assert locator(m, m.sections[0]) == "alg/book.pdf p.1-3"


def test_ingest_pdf_without_outline(tmp_path):
    pdf = tmp_path / "scan.pdf"
    make_pdf(pdf, pages=3, outline=False)
    m = ingest_pdf(pdf, tmp_path / "sources", "scan")
    assert m.sections == [] and m.pages == 3


def test_ingest_rejects_non_pdf(tmp_path):
    bad = tmp_path / "notes.pdf"
    bad.write_text("just text, not a pdf")
    with pytest.raises(IngestError, match="notes.pdf"):
        ingest_pdf(bad, tmp_path / "sources", "notes")


def test_load_manifest_malformed_names_file(tmp_path):
    p = tmp_path / "manifest.yaml"
    p.write_text("kind: nonsense\n")
    with pytest.raises(IngestError, match="manifest.yaml"):
        load_manifest(p)


def test_iter_manifests_and_web_locator(tmp_path):
    assert iter_manifests(tmp_path / "nope") == []
    src = tmp_path / "sources" / "ct"
    src.mkdir(parents=True)
    web = SourceManifest(
        name="ct",
        kind="web",
        sections=[SourceSection(title="Ch 3", url="https://example.org/ch3")],
    )
    (src / "manifest.yaml").write_text(yaml.safe_dump(web.model_dump(mode="json")))
    [m] = iter_manifests(tmp_path / "sources")
    assert m == web
    assert locator(m, m.sections[0]) == "https://example.org/ch3"
```

- [ ] **Step 3: Run to verify it fails** — `uv run pytest tests/test_ingest.py -v` — Expected: FAIL (no module `seba.ingest`).

- [ ] **Step 4: Implement** — create `src/seba/ingest.py`:

```python
import shutil
from pathlib import Path

import yaml
from pydantic import ValidationError
from pypdf import PdfReader

from seba.models import SourceManifest, SourceSection


class IngestError(Exception):
    pass


def _flatten_outline(reader: PdfReader) -> list[tuple[str, int]]:
    """(title, 0-based start page) per outline entry, sorted by page.

    Real-world outlines are messy; a single unresolvable entry is skipped
    rather than failing the whole ingest (deliberate exception to fail-loud).
    """
    out: list[tuple[str, int]] = []

    def walk(entries) -> None:
        for e in entries:
            if isinstance(e, list):
                walk(e)
                continue
            try:
                out.append((str(e.title), reader.get_destination_page_number(e)))
            except Exception:  # noqa: BLE001 — skip one bad entry, keep the rest
                continue

    walk(reader.outline)
    out.sort(key=lambda t: t[1])
    return out


def ingest_pdf(pdf: Path, sources_dir: Path, name: str) -> SourceManifest:
    try:
        reader = PdfReader(pdf)
        pages = len(reader.pages)
        flat = _flatten_outline(reader)
    except Exception as e:
        raise IngestError(f"{pdf.name}: not a readable PDF ({e})") from e

    sections = []
    for i, (title, start0) in enumerate(flat):
        end0 = flat[i + 1][1] - 1 if i + 1 < len(flat) else pages - 1
        sections.append(
            SourceSection(
                title=title, page_start=start0 + 1, page_end=max(end0, start0) + 1
            )
        )

    dest = sources_dir / name
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pdf, dest / "book.pdf")
    manifest = SourceManifest(
        name=name, kind="pdf", file=f"{name}/book.pdf", pages=pages, sections=sections
    )
    (dest / "manifest.yaml").write_text(
        yaml.safe_dump(manifest.model_dump(mode="json"), sort_keys=False, allow_unicode=True)
    )
    return manifest


def load_manifest(path: Path) -> SourceManifest:
    try:
        return SourceManifest.model_validate(yaml.safe_load(path.read_text()))
    except (yaml.YAMLError, ValidationError, OSError) as e:
        raise IngestError(f"{path.name}: {e}") from e


def iter_manifests(sources_dir: Path) -> list[SourceManifest]:
    if not sources_dir.exists():
        return []
    return [load_manifest(p) for p in sorted(sources_dir.glob("*/manifest.yaml"))]


def locator(m: SourceManifest, s: SourceSection) -> str:
    if m.kind == "pdf":
        return f"{m.file} p.{s.page_start}-{s.page_end}"
    return s.url or ""
```

- [ ] **Step 5: Gate and commit**

```bash
make check
git add -A && git commit -m "feat: PDF ingest to source manifests (pypdf outline -> page-range locators)"
```

---

### Task 4: View template + `seba view` CLI

**Files:**
- Create: `src/seba/ui/view_template.html`
- Modify: `src/seba/cli.py` (append one command + two imports)
- Test: `tests/test_view.py` (append)

**Interfaces:**
- Consumes: T2's `build_view_data`; existing `_store()`, `app`, `config`.
- Produces:
  - `render_view(data: ViewData) -> str` in `src/seba/ui/view.py` — reads the packaged template, replaces the single token `__SEBA_DATA__` with `json.dumps(data.model_dump(mode="json"))`.
  - CLI: `seba view GOAL [--json] [--open]` per the Global Constraints contract.
- Packaging gate: the template must land in the wheel. If Step 6's wheel check fails, STOP and report BLOCKED (PM decides the pyproject fix) — do not guess at build-backend config keys.

- [ ] **Step 1: Write the failing tests** — append to `tests/test_view.py`:

```python
import json

from typer.testing import CliRunner

from seba.cli import app
from seba.ui.view import render_view

runner = CliRunner()


def test_render_view_injects_data():
    v = build_view_data(state([Concept(id="a", name="A")]), TODAY)
    html = render_view(v)
    assert "__SEBA_DATA__" not in html
    assert '"goal": "prob"' in html
    assert "<script" in html and "http" not in html.split("<script")[0].lower().replace(
        "http-equiv", ""
    )  # no external URLs before the data script (self-contained head)


def test_view_cli(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    from seba.models import Syllabus as _S  # local alias to build a real goal
    from seba.store.store import Store

    Store(tmp_path / "data").create_goal(
        "prob",
        _S(goal="prob", subject="probability", concepts=[Concept(id="a", name="A")]),
        "probability",
    )
    result = runner.invoke(app, ["view", "prob", "--json"])
    assert result.exit_code == 0
    blob = json.loads(result.output)
    assert blob["stats"]["concepts_total"] == 1

    result2 = runner.invoke(app, ["view", "prob"])
    assert result2.exit_code == 0
    out = tmp_path / "data" / "goals" / "prob" / "view.html"
    assert out.exists() and str(out) in result2.output
    assert '"concepts_total": 1' in out.read_text()
```

- [ ] **Step 2: Run to verify it fails** — `uv run pytest tests/test_view.py -v` — Expected: FAIL (`render_view` not defined).

- [ ] **Step 3: Add `render_view`** — append to `src/seba/ui/view.py` (add `import json` and `from importlib.resources import files` to its imports; add `ViewData` already imported):

```python
def render_view(data: ViewData) -> str:
    template = files("seba.ui").joinpath("view_template.html").read_text()
    return template.replace("__SEBA_DATA__", json.dumps(data.model_dump(mode="json")))
```

- [ ] **Step 4: Create `src/seba/ui/view_template.html`** — the complete file (self-contained; the ONLY dynamic part is the `__SEBA_DATA__` token):

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>seba — goal view</title>
<style>
  body { font: 14px/1.5 -apple-system, system-ui, sans-serif; color: #0f172a;
         background: #fff; max-width: 1040px; margin: 2rem auto; padding: 0 1rem; }
  h1 { margin: 0 0 .25rem; font-size: 1.4rem; }
  #stats { color: #475569; margin: 0 0 .5rem; }
  .legend { color: #475569; font-size: 12px; margin-bottom: 1.25rem; }
  .legend i { display: inline-block; width: 11px; height: 11px; border-radius: 3px;
              margin: 0 4px 0 12px; vertical-align: -1px; border: 1px solid #64748b; }
  #graphwrap { overflow-x: auto; margin-bottom: 2rem; }
  table { border-collapse: collapse; width: 100%; }
  th, td { text-align: left; padding: 6px 10px; border-bottom: 1px solid #e2e8f0; }
  th { color: #475569; font-weight: 600; }
  #generated { color: #94a3b8; font-size: 12px; margin-top: 1.5rem; }
</style>
</head>
<body>
<h1 id="title"></h1>
<p id="stats"></p>
<p class="legend">status:
  <i style="background:#e2e8f0"></i>unseen
  <i style="background:#fde68a"></i>in-progress
  <i style="background:#86efac"></i>done
  <i style="background:#fff;border-color:#2563eb;border-width:2px"></i>frontier
</p>
<div id="graphwrap"><svg id="graph" xmlns="http://www.w3.org/2000/svg"></svg></div>
<table id="cards">
  <thead><tr><th>concept</th><th>status</th><th>est. sessions</th><th>cards</th><th>due</th></tr></thead>
  <tbody></tbody>
</table>
<p id="generated"></p>
<script>
const DATA = __SEBA_DATA__;
const COLORS = { "unseen": "#e2e8f0", "in-progress": "#fde68a", "done": "#86efac" };

document.title = `seba — ${DATA.goal}`;
document.getElementById("title").textContent = `${DATA.goal} (${DATA.subject})`;
const S = DATA.stats;
document.getElementById("stats").textContent =
  `session ${DATA.session_number} · concepts ${S.concepts_done}/${S.concepts_total} done · ` +
  `cards ${S.cards_total} (${S.cards_due} due today) · frontier: ${S.frontier.join(", ") || "none"}`;

// ---- layered dependency graph ----
const svg = document.getElementById("graph");
const NS = "http://www.w3.org/2000/svg";
const W = 200, H = 46, XGAP = 80, YGAP = 24, PAD = 24;
const layers = new Map();
for (const c of DATA.concepts) {
  if (!layers.has(c.layer)) layers.set(c.layer, []);
  c._row = layers.get(c.layer).length;
  layers.get(c.layer).push(c);
}
const pos = new Map();
for (const c of DATA.concepts)
  pos.set(c.id, { x: PAD + c.layer * (W + XGAP), y: PAD + c._row * (H + YGAP) });
const maxLayer = Math.max(0, ...DATA.concepts.map(c => c.layer));
const maxRows = Math.max(1, ...[...layers.values()].map(l => l.length));
svg.setAttribute("width", PAD * 2 + (maxLayer + 1) * W + maxLayer * XGAP);
svg.setAttribute("height", PAD * 2 + maxRows * (H + YGAP));

function el(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  (parent || svg).appendChild(e);
  return e;
}
for (const c of DATA.concepts)                    // edges first, under the nodes
  for (const p of c.prereqs) {
    const a = pos.get(p), b = pos.get(c.id);
    if (!a || !b) continue;
    const x1 = a.x + W, y1 = a.y + H / 2, x2 = b.x, y2 = b.y + H / 2;
    el("path", { d: `M${x1},${y1} C${x1 + XGAP / 2},${y1} ${x2 - XGAP / 2},${y2} ${x2},${y2}`,
                 fill: "none", stroke: "#94a3b8", "stroke-width": 1.5 });
  }
for (const c of DATA.concepts) {
  const { x, y } = pos.get(c.id);
  const onFrontier = S.frontier.includes(c.id);
  const g = el("g", {});
  el("rect", { x, y, width: W, height: H, rx: 8, fill: COLORS[c.status] || "#e2e8f0",
               stroke: onFrontier ? "#2563eb" : "#64748b",
               "stroke-width": onFrontier ? 2.5 : 1 }, g);
  const t1 = el("text", { x: x + 10, y: y + 19, "font-size": 12, "font-weight": 600 }, g);
  t1.textContent = c.name.length > 26 ? c.name.slice(0, 25) + "…" : c.name;
  const t2 = el("text", { x: x + 10, y: y + 36, "font-size": 11, fill: "#475569" }, g);
  t2.textContent = `${c.id} · ${c.cards} cards` + (c.due ? ` · ${c.due} due` : "");
}

// ---- per-concept table ----
const tbody = document.querySelector("#cards tbody");
for (const c of DATA.concepts) {
  const tr = document.createElement("tr");
  for (const v of [c.name, c.status, c.est_sessions, c.cards, c.due]) {
    const td = document.createElement("td");
    td.textContent = v;
    tr.appendChild(td);
  }
  tbody.appendChild(tr);
}
document.getElementById("generated").textContent =
  `generated ${DATA.generated} · recent grades: ${DATA.recent_grades.join(" ") || "—"}`;
</script>
</body>
</html>
```

- [ ] **Step 5: Add the CLI command** — in `src/seba/cli.py`, add to the imports block:

```python
from seba.ui.view import build_view_data, render_view
```

and append the command (after `abandon`):

```python
@app.command()
def view(
    goal: str,
    json_out: bool = typer.Option(False, "--json", help="print the data blob instead of writing HTML"),
    open_browser: bool = typer.Option(False, "--open", help="open the rendered view"),
):
    store = _store()
    state = store.load_goal(goal)
    data = build_view_data(state, date.today())
    if json_out:
        typer.echo(data.model_dump_json())
        return
    out = store.data_dir / "goals" / goal / "view.html"
    out.write_text(render_view(data))
    typer.echo(str(out))
    if open_browser:
        typer.launch(str(out))
```

- [ ] **Step 6: Gate, wheel check, commit**

```bash
make check
uv build && unzip -l dist/*.whl | grep view_template.html && rm -rf dist
```

Expected: tests pass AND the grep prints the template path inside the wheel. If the grep finds nothing: STOP, report BLOCKED with the `unzip -l` output — do not invent pyproject keys.

```bash
git add -A && git commit -m "feat: seba view — render goal graph + card status to self-contained HTML"
```

---

### Task 5: `seba ingest` + `seba sources` CLI commands

**Files:**
- Modify: `src/seba/cli.py` (append two commands + one import)
- Test: `tests/test_ingest.py` (append)

**Interfaces:**
- Consumes: T3's `IngestError`, `ingest_pdf`, `iter_manifests`, `locator`; existing `config.data_dir()`.
- Produces: the `seba ingest` / `seba sources` contract from Global Constraints (T6 documents it verbatim).

- [ ] **Step 1: Write the failing tests** — append to `tests/test_ingest.py`:

```python
from typer.testing import CliRunner

from seba.cli import app

runner = CliRunner()


def test_ingest_cli(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    pdf = tmp_path / "Algebra Book.pdf"
    make_pdf(pdf)
    result = runner.invoke(app, ["ingest", str(pdf)])
    assert result.exit_code == 0
    assert "algebra-book" in result.output          # default name = slugified stem
    assert "algebra-book/book.pdf p.1-3" in result.output
    assert (tmp_path / "data" / "sources" / "algebra-book" / "manifest.yaml").exists()

    named = runner.invoke(app, ["ingest", str(pdf), "--name", "alg"])
    assert named.exit_code == 0 and "alg/book.pdf p.1-3" in named.output


def test_ingest_cli_rejects_bad_pdf(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    bad = tmp_path / "bad.pdf"
    bad.write_text("nope")
    result = runner.invoke(app, ["ingest", str(bad)])
    assert result.exit_code == 1


def test_sources_cli(monkeypatch, tmp_path):
    monkeypatch.setenv("SEBA_DATA_DIR", str(tmp_path / "data"))
    empty = runner.invoke(app, ["sources"])
    assert empty.exit_code == 0 and "no sources" in empty.output.lower()

    pdf = tmp_path / "alg.pdf"
    make_pdf(pdf)
    runner.invoke(app, ["ingest", str(pdf), "--name", "alg"])
    listed = runner.invoke(app, ["sources"])
    assert "alg/book.pdf p.1-3" in listed.output and "1. Groups" in listed.output
    one = runner.invoke(app, ["sources", "alg"])
    assert "2. Rings" in one.output
    missing = runner.invoke(app, ["sources", "ghost"])
    assert missing.exit_code == 1
```

- [ ] **Step 2: Run to verify it fails** — `uv run pytest tests/test_ingest.py -v` — Expected: new tests FAIL (no `ingest` command).

- [ ] **Step 3: Implement** — in `src/seba/cli.py`, add to the imports block:

```python
from seba.ingest import IngestError, ingest_pdf, iter_manifests, locator
```

and append the commands (after `view`):

```python
@app.command()
def ingest(
    path: Path = typer.Argument(..., exists=True, dir_okay=False, help="a local PDF"),
    name: str | None = typer.Option(None, help="source name (default: slugified file stem)"),
):
    slug = name or path.stem.lower().replace(" ", "-")
    try:
        m = ingest_pdf(path, config.data_dir() / "sources", slug)
    except IngestError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    typer.echo(f"ingested '{slug}': {m.pages} pages, {len(m.sections)} sections")
    if not m.sections:
        typer.echo(
            "(no outline in this PDF — write page ranges into concept sources "
            "by hand from its table of contents)"
        )
    for s in m.sections:
        typer.echo(f"  {locator(m, s)}  — {s.title}")


@app.command()
def sources(name: str | None = typer.Argument(None)):
    manifests = iter_manifests(config.data_dir() / "sources")
    if name is not None:
        manifests = [m for m in manifests if m.name == name]
        if not manifests:
            typer.echo(f"no source '{name}' — run: seba sources", err=True)
            raise typer.Exit(1)
    if not manifests:
        typer.echo("no sources ingested — run: seba ingest PATH")
        return
    for m in manifests:
        typer.echo(f"{m.name} ({m.kind}{f', {m.pages} pages' if m.pages else ''})")
        for s in m.sections:
            typer.echo(f"  {locator(m, s)}  — {s.title}")
```

- [ ] **Step 4: Gate and commit**

```bash
make check
git add -A && git commit -m "feat: seba ingest / seba sources CLI over source manifests"
```

---

### Task 6: SKILL.md + docs

**Files:**
- Modify: `skills/seba-tutor/SKILL.md`
- Modify: `docs/development.md`

Accuracy over embellishment: before writing, verify every command/flag against the actual `src/seba/cli.py` on this branch (`uv run seba --help`, `uv run seba ingest --help`, `uv run seba view --help`).

- [ ] **Step 1: SKILL.md — command table.** Add three rows to the existing commands table:

```markdown
| `seba ingest PATH [--name NAME]` | register a local PDF as a source: copies it into sources/, prints one locator per outline section |
| `seba sources [NAME]` | list every registered source locator (paste-ready for syllabus `sources:` lists) |
| `seba view GOAL [--open]` | render the goal's dependency graph + card status to HTML; `--open` shows it in the browser |
```

- [ ] **Step 2: SKILL.md — rewrite "Creating a new goal" step 1** (replace the current step-1 paragraph about sources; keep steps 2–4 as they are):

```markdown
1. Interview the learner: goal, prior knowledge, and the **primary source and
   where it lives**. Register it BEFORE drafting the syllabus:
   - **Local PDF** → `seba ingest /path/to/book.pdf --name NAME`. It prints one
     paste-ready locator per chapter (e.g. `NAME/book.pdf p.12-40`).
   - **Web link to a PDF** → download it first (`curl -L -o /tmp/book.pdf URL`),
     then ingest the downloaded file as above. Never read the PDF into context.
   - **Web link to a website** → write `$SEBA_DATA_DIR/sources/NAME/manifest.yaml`
     yourself, one section per page:

     ```yaml
     name: ct
     kind: web
     sections:
       - title: "Ch 3: Functors"
         url: https://example.org/ch3
     ```
   - `seba sources` lists every registered locator — pick concept `sources` from
     that list, never invent refs. If a PDF has no outline, map page ranges from
     its table of contents by hand.
   - No source at all is fine too — the goal just won't be source-grounded.
```

- [ ] **Step 3: SKILL.md — session close.** In the session-protocol step where the session ends (`seba end`), append one sentence:

```markdown
   After a successful `seba end`, offer the learner a progress picture:
   `seba view GOAL --open` (regenerate it any time — it renders from saved state).
```

- [ ] **Step 4: docs/development.md.** Add the three commands to the command-reference table (same three rows as Step 1), and one line to the architecture section:

```markdown
- `ingest`/`view` — deterministic tooling around the loop: `seba ingest` turns a
  local PDF's outline into a manifest of page-range locators (`sources/<name>/`);
  `seba view` renders `GoalState` through a bundled self-contained HTML template
  (`src/seba/ui/view_template.html`) — the CLI only injects a JSON blob.
```

- [ ] **Step 5: Verify docs against code, gate, commit**

```bash
uv run seba --help    # confirm ingest, sources, view all listed as documented
make check
git add -A && git commit -m "docs: ingest/sources/view in skill and dev docs"
```

---

### Task 7: Dogfood gate (manual — HUMAN ONLY)

No files. Hand off to the user:

- [ ] **Step 1:** `seba ingest` a real PDF (your category-theory or probability book). Check `seba sources` prints sensible chapter locators; spot-check one page range against the actual book.
- [ ] **Step 2:** For the website source: have the tutor write a `kind: web` manifest for the category-theory site and confirm `seba sources` lists its pages.
- [ ] **Step 3:** `seba view GOAL --open` on your real goal. Check: graph topology matches the syllabus prereqs, statuses/colors are right, due counts match `seba status`, and it renders offline (Wi-Fi off).
- [ ] **Step 4:** Run one real session where the syllabus references an ingested locator; confirm the tutor reads only that page range at teach time.

---

## Self-review (done at plan time)

- **Spec coverage:** PDF → manifest + page-range locators ✅(T3/T5) · web link handled tutor-side, PDF-by-URL via download + ingest, website via hand-written manifest, both listed by `seba sources` ✅(T3 web-manifest test, T5, T6) · view = CLI + bundled template, CLI renders, `--open` opens, Claude triggers by running the command ✅(T2/T4/T6) · no whole-book context loads anywhere ✅(design decisions 1–3).
- **Type consistency:** `SourceManifest`/`SourceSection` defined T1, consumed T3/T5; `ViewData` chain T1→T2→T4; `locator()` signature identical in T3 and T5; `build_view_data(state, today)` identical in T2 and T4.
- **Placeholder scan:** clean — every step carries full code, the template is complete, no "similar to Task N".
- **Known risks carried deliberately:** (a) pypdf outline quality varies — mitigated by skip-bad-entry + the no-outline fallback path (decision 3); (b) wheel inclusion of the template is verified by an explicit gate with a BLOCKED escape (T4 step 6), not assumed; (c) `view.html` riding into a data-repo commit — accepted (decision 5).
