import json
import subprocess
from datetime import date
from pathlib import Path

import yaml
from pydantic import ValidationError

from seba.models import (
    Emphasis,
    GoalMeta,
    GoalSettings,
    GoalState,
    GoalSummary,
    Grade,
    GradeReview,
    Item,
    SessionRecord,
    Syllabus,
    UpdateConcept,
)
from seba.scheduler.apply import replay
from seba.syllabus.graph import SyllabusError, extend, load_concepts, load_syllabus


class StoreError(Exception):
    pass


def parse_notes(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current is not None and line.strip():
            sections[current].append(line)
    return sections


class Store:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        (data_dir / "goals").mkdir(parents=True, exist_ok=True)
        (data_dir / "sources").mkdir(exist_ok=True)
        if not (data_dir / ".git").exists():
            self._git("init")
        # The data repo is Seba's own; give it a local identity so commits work
        # without relying on the machine's global git config (a fresh box or CI
        # runner has none), and disable signing so an ambient commit.gpgsign=true
        # can't block our automated commits. Set unconditionally (idempotent) so
        # a data repo created before this fix also gets it.
        self._git("config", "user.name", "seba")
        self._git("config", "user.email", "seba@localhost")
        self._git("config", "commit.gpgsign", "false")

    def _git(self, *args: str) -> None:
        subprocess.run(
            ["git", *args], cwd=self.data_dir, check=True, capture_output=True
        )

    def _goal_dir(self, name: str) -> Path:
        return self.data_dir / "goals" / name

    def create_goal(self, name: str, syllabus: Syllabus, subject: str) -> None:
        gdir = self._goal_dir(name)
        if gdir.exists():
            raise StoreError(f"goal '{name}' already exists")
        (gdir / "sessions").mkdir(parents=True)
        (gdir / "goal.yaml").write_text(
            yaml.safe_dump({"name": name, "subject": subject})
        )
        self._write_syllabus(gdir, syllabus)
        (gdir / "items.jsonl").write_text("")
        (gdir / "notes.md").write_text("")
        self._git("add", "-A")
        self._git("commit", "-m", f"{name}: created")

    def extend_syllabus(
        self, name: str, path: Path, pending: list[UpdateConcept] | None = None
    ) -> list[str]:
        """Append the concepts in `path`; returns their ids in file order.
        Everything is checked before anything is written. Leaves any pending
        session alone: the next command builds its handler from this file.
        `pending` is that session's concept changes: the new concepts are
        judged against the syllabus as they have changed it, since the
        session's drops must still be legal when `seba end` replays them."""
        syllabus = self.load_goal(name).syllabus
        try:
            new = load_concepts(path)
        except SyllabusError as e:
            raise StoreError(str(e)) from e
        try:
            merged = extend(syllabus, new, against=replay(syllabus, pending or []))
        except SyllabusError as e:
            raise StoreError(f"{path.name}: {e}") from e
        self._write_syllabus(self._goal_dir(name), merged)
        self._git("add", f"goals/{name}/syllabus.yaml")
        self._git("commit", "-m", f"{name}: extended (+{len(new)})")
        return [c.id for c in new]

    def _load_items(self, path: Path) -> list[Item]:
        items = []
        for n, line in enumerate(path.read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                items.append(Item.model_validate(json.loads(line)))
            except (json.JSONDecodeError, ValidationError) as e:
                raise StoreError(f"{path.name}:{n}: {e}") from e
        return items

    def _load_meta(self, path: Path) -> GoalMeta:
        try:
            return GoalMeta.model_validate(yaml.safe_load(path.read_text()))
        except (yaml.YAMLError, ValidationError) as e:
            raise StoreError(f"{path.name}: {e}") from e

    def _write_items(self, gdir: Path, items: list[Item]) -> None:
        tmp = gdir / "items.jsonl.tmp"
        tmp.write_text(
            "".join(json.dumps(i.model_dump(mode="json")) + "\n" for i in items)
        )
        tmp.rename(gdir / "items.jsonl")

    def _write_syllabus(self, gdir: Path, syllabus: Syllabus) -> None:
        # exclude_none: `dropped_from` appears only on a dropped concept.
        (gdir / "syllabus.yaml").write_text(
            yaml.safe_dump(
                syllabus.model_dump(mode="json", exclude_none=True), sort_keys=False
            )
        )

    def save_tuning(
        self,
        name: str,
        settings: GoalSettings,
        emphasis: dict[str, Emphasis],
        items: list[Item],
        *,
        direction: str | None = None,
    ) -> bool:
        """Write settings, emphasis, cards and, unless it is None, the direction.
        Commits only if something changed: `_git` runs with check=True and an
        empty commit fails."""
        gdir = self._goal_dir(name)
        path = gdir / "goal.yaml"
        update: dict[str, GoalSettings | dict[str, Emphasis] | str] = {
            "settings": settings,
            "emphasis": emphasis,
        }
        if direction is not None:
            update["direction"] = direction
        meta = self._load_meta(path).model_copy(update=update)
        path.write_text(
            yaml.safe_dump(
                meta.model_dump(mode="json", exclude_none=True), sort_keys=False
            )
        )
        self._write_items(gdir, items)
        paths = (f"goals/{name}/goal.yaml", f"goals/{name}/items.jsonl")
        self._git("add", *paths)
        staged = subprocess.run(
            ["git", "diff", "--cached", "--quiet", "--", *paths],
            cwd=self.data_dir,
            capture_output=True,
        )
        if staged.returncode == 0:
            return False
        if staged.returncode != 1:
            raise StoreError(f"git diff failed: {staged.stderr.decode().strip()}")
        self._git("commit", "-m", f"{name}: tuned")
        return True

    def _outcomes_files(self, name: str) -> list[Path]:
        return sorted(self._goal_dir(name).glob("sessions/*.outcomes.yaml"))

    def load_goal(self, name: str) -> GoalState:
        gdir = self._goal_dir(name)
        if not gdir.exists():
            raise StoreError(f"no such goal: '{name}'")
        meta = self._load_meta(gdir / "goal.yaml")
        try:
            syllabus = load_syllabus(gdir / "syllabus.yaml")
        except (yaml.YAMLError, SyllabusError) as e:
            raise StoreError(str(e)) from e
        items = self._load_items(gdir / "items.jsonl")
        outcomes = self._outcomes_files(name)
        concept_of = {i.id: i.concept for i in items}
        last_hint, recent_grades = None, []
        by_concept: dict[str, list[Grade]] = {}
        all_by_concept: dict[str, list[Grade]] = {}
        started_at: dict[str, int] = {}  # session a concept last went in-progress
        passed_at: dict[str, list[int]] = {}  # sessions with a good/easy card review
        last_errors: set[str] = set()
        again_runs: dict[str, int] = {}
        last_trouble: list[GradeReview] = []
        last_date: date | None = None
        # ponytail: re-reads every outcomes file per load; sessions are small and
        # few. Cache or a derived index only if a goal's history gets long.
        for n, path in enumerate(outcomes, 1):
            rec = SessionRecord.model_validate(yaml.safe_load(path.read_text()))
            recent = n > len(outcomes) - 3
            last = n == len(outcomes)
            if last:
                last_date, last_errors = rec.session_date, set()
                last_trouble = []
            for r in rec.reviews:
                if r.grade == Grade.AGAIN:
                    again_runs[r.id] = again_runs.get(r.id, 0) + 1
                elif r.grade != Grade.SKIPPED:
                    again_runs.pop(r.id, None)
                if last and r.grade in (Grade.AGAIN, Grade.HARD):
                    last_trouble.append(r)
                cid = concept_of.get(r.id)  # item may since have been deleted
                if cid is not None:
                    all_by_concept.setdefault(cid, []).append(r.grade)
                    if r.grade in (Grade.GOOD, Grade.EASY):
                        passed_at.setdefault(cid, []).append(n)
                    elif last and r.grade == Grade.AGAIN:
                        last_errors.add(cid)
                if recent:
                    recent_grades.append(r.grade)
                    if cid is not None:
                        by_concept.setdefault(cid, []).append(r.grade)
            for c in rec.concepts:
                if c.status_change == "started":
                    started_at.setdefault(c.id, n)
                elif c.status_change == "reopened":
                    started_at[c.id] = n
            if recent:
                last_hint = rec.next_session_hint or last_hint
        return GoalState(
            name=name,
            subject=meta.subject,
            direction=(meta.direction or "").strip() or syllabus.goal.strip(),
            syllabus=syllabus,
            items=items,
            notes=(gdir / "notes.md").read_text(),
            settings=meta.settings,
            emphasis={
                cid: e
                for cid, e in meta.emphasis.items()
                if cid in {c.id for c in syllabus.concepts}
            },
            last_hint=last_hint,
            session_number=len(outcomes) + 1,
            recent_grades=recent_grades,
            recent_by_concept=by_concept,
            grades_by_concept=all_by_concept,
            last_session_errors=last_errors,
            again_runs=again_runs,
            last_trouble=last_trouble,
            started_at=started_at,
            last_session_date=last_date,
            passes={
                cid: len({s for s in passed_at.get(cid, []) if s > start})
                for cid, start in started_at.items()
            },
        )

    def save_session(
        self, name: str, record: SessionRecord, transcript: str, updated: GoalState
    ) -> None:
        gdir = self._goal_dir(name)
        # The only durable record of when a session happened; mtime doesn't survive
        # a clone of the data repo, and the lapse check needs a real date.
        record = record.model_copy(
            update={"session_date": record.session_date or date.today()}
        )
        n = f"{len(self._outcomes_files(name)) + 1:03d}"
        sdir = gdir / "sessions"
        marker = "" if record.complete else "**INCOMPLETE**\n\n"
        (sdir / f"{n}.md").write_text(
            f"# Session {n}\n\n{marker}{record.summary or '(no summary)'}\n"
        )
        (sdir / f"{n}.outcomes.yaml").write_text(
            yaml.safe_dump(record.model_dump(mode="json"), sort_keys=False)
        )
        (sdir / f"{n}.transcript.md").write_text(transcript)

        self._write_items(gdir, updated.items)
        self._write_syllabus(gdir, updated.syllabus)

        noted = [c for c in record.concepts if c.note]
        if noted:
            sections = parse_notes((gdir / "notes.md").read_text())
            for c in noted:
                sections.setdefault(c.id, []).insert(0, f"- [s{n}] {c.note}")
            (gdir / "notes.md").write_text(
                "".join(
                    f"## {cid}\n" + "\n".join(lines) + "\n\n"
                    for cid, lines in sections.items()
                )
            )

        self._git("add", "-A")
        self._git("commit", "-m", f"{name}: session {n}")

    def list_goals(self) -> list[GoalSummary]:
        out = []
        today = date.today().isoformat()
        for gdir in sorted((self.data_dir / "goals").iterdir()):
            if not gdir.is_dir():
                continue
            gs = self.load_goal(gdir.name)
            dropped = {c.id for c in gs.syllabus.concepts if c.status == "dropped"}
            due = sum(
                1
                for i in gs.items
                if not i.suspended
                and i.concept not in dropped
                and str(i.fsrs.get("due", ""))[:10] <= today
            )
            out.append(
                GoalSummary(
                    name=gs.name,
                    subject=gs.subject,
                    session_count=gs.session_number - 1,
                    due_count=due,
                )
            )
        return out
