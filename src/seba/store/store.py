import json
import subprocess
from datetime import date
from pathlib import Path

import yaml
from pydantic import ValidationError

from seba.models import GoalState, GoalSummary, Item, SessionRecord, Syllabus
from seba.syllabus.graph import SyllabusError, load_syllabus


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
            # The data repo is Seba's own; give it a local identity so commits
            # work without relying on the machine's global git config (a fresh
            # box or CI runner has none), and disable signing so an ambient
            # commit.gpgsign=true can't block our automated commits.
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
        (gdir / "syllabus.yaml").write_text(
            yaml.safe_dump(syllabus.model_dump(mode="json"), sort_keys=False)
        )
        (gdir / "items.jsonl").write_text("")
        (gdir / "notes.md").write_text("")
        self._git("add", "-A")
        self._git("commit", "-m", f"{name}: created")

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

    def _outcomes_files(self, name: str) -> list[Path]:
        return sorted(self._goal_dir(name).glob("sessions/*.outcomes.yaml"))

    def load_goal(self, name: str) -> GoalState:
        gdir = self._goal_dir(name)
        if not gdir.exists():
            raise StoreError(f"no such goal: '{name}'")
        try:
            meta = yaml.safe_load((gdir / "goal.yaml").read_text())
            syllabus = load_syllabus(gdir / "syllabus.yaml")
        except (yaml.YAMLError, SyllabusError) as e:
            raise StoreError(str(e)) from e
        items = self._load_items(gdir / "items.jsonl")
        outcomes = self._outcomes_files(name)
        last_hint, recent_grades = None, []
        for path in outcomes[-3:]:
            rec = SessionRecord.model_validate(yaml.safe_load(path.read_text()))
            recent_grades.extend(r.grade for r in rec.reviews)
            last_hint = rec.next_session_hint or last_hint
        return GoalState(
            name=name,
            subject=meta["subject"],
            syllabus=syllabus,
            items=items,
            notes=(gdir / "notes.md").read_text(),
            last_hint=last_hint,
            session_number=len(outcomes) + 1,
            recent_grades=recent_grades,
        )

    def save_session(
        self, name: str, record: SessionRecord, transcript: str, updated: GoalState
    ) -> None:
        gdir = self._goal_dir(name)
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

        tmp = gdir / "items.jsonl.tmp"
        tmp.write_text(
            "".join(json.dumps(i.model_dump(mode="json")) + "\n" for i in updated.items)
        )
        tmp.rename(gdir / "items.jsonl")
        (gdir / "syllabus.yaml").write_text(
            yaml.safe_dump(updated.syllabus.model_dump(mode="json"), sort_keys=False)
        )

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
            due = sum(
                1
                for i in gs.items
                if not i.suspended and str(i.fsrs.get("due", ""))[:10] <= today
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
