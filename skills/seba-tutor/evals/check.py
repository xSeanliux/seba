"""Grade an eval run's [check] assertions from its sandbox state.

    uv run python skills/seba-tutor/evals/check.py EVAL_NAME RUN_DIR

RUN_DIR holds sandbox/ (from setup.sh) and outputs/reply.md (the tutor's
message). Prints the results as JSON, one {text, passed, evidence} per [check]
assertion of that eval in evals.json, in the field names the skill-creator
viewer reads. Judged assertions are left to a reader.
"""

import json
import re
import sys
from collections.abc import Callable
from pathlib import Path

import yaml

from seba.models import GradeReview, Item, ItemType, PendingSession, SessionRecord

EVALS = Path(__file__).with_name("evals.json")


class Run:
    def __init__(self, root: Path) -> None:
        goal = root / "sandbox" / "data" / "goals" / "prob"
        log = (root / "sandbox" / "seba.log").read_text()
        self.calls: list[list[str]] = [json.loads(line) for line in log.splitlines()]
        self.reply = (root / "outputs" / "reply.md").read_text()
        pending = goal / "session.pending.yaml"
        self.pending = (
            PendingSession.model_validate(yaml.safe_load(pending.read_text()))
            if pending.exists()
            else None
        )
        self.sessions = sorted(p.name for p in (goal / "sessions").glob("*.md"))
        # The session this run touched: still pending, or the last one saved.
        saved = sorted((goal / "sessions").glob("*.outcomes.yaml"))
        self.record = (
            self.pending.record
            if self.pending
            else SessionRecord.model_validate(yaml.safe_load(saved[-1].read_text()))
        )
        items = [
            Item.model_validate_json(line)
            for line in (goal / "items.jsonl").read_text().splitlines()
        ]
        self.die = next((i.id for i in items if "fair die" in i.front), None)
        self.coin = next((i.id for i in items if "coins" in i.front), None)

    def ran(self, *words: str) -> list[str]:
        """Logged calls containing every word, as strings for evidence."""
        return [" ".join(c) for c in self.calls if all(w in c for w in words)]

    def review(self, item: str | None) -> GradeReview | None:
        return next((r for r in self.record.reviews if r.id == item), None)

    def grade(self, item: str | None) -> str | None:
        rv = self.review(item)
        return rv.grade if rv else None

    def started(self, concept: str) -> int:
        return sum(
            c.id == concept and c.status_change == "started"
            for c in self.record.concepts
        )

    def moved(self, status: str) -> bool:
        return any(c.status_change == status for c in self.record.concepts)


Check = Callable[[Run], tuple[bool, str]]


def questions(r: Run) -> int:
    """Question marks in prose; a `?` inside a code block is a blank in a drawing."""
    return re.sub(r"```.*?```", "", r.reply, flags=re.S).count("?")


def no_latex(r: Run) -> tuple[bool, str]:
    hits = re.findall(
        r"\$[^$\n]+\$|\\(?:frac|cap|cup|mid|cdot|le|ge|in|\(|\[)", r.reply
    )
    return not hits, f"LaTeX found: {hits}" if hits else "no LaTeX markers"


def die_graded(grade: str) -> Check:
    return lambda r: (r.grade(r.die) == grade, f"recorded: {r.review(r.die)}")


def one_sentence_note(r: Run) -> tuple[bool, str]:
    rv = r.review(r.die)
    note = (rv.note if rv else None) or ""
    ok = bool(note) and "\n" not in note and not re.search(r"[.!?]\s+[A-Z]", note)
    return ok, f"note: {note!r}"


def sentences(text: str | None) -> int:
    return len([p for p in re.split(r"(?<=[.!?])\s+", text or "") if p.strip()])


QUANTITY = re.compile(
    r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|fifteen|twenty|thirty)"
    r"\s*(-\s*)?(min|mins|minutes?|hours?|problems?|cards?|questions?|exercises?|examples?)\b",
    re.I,
)


TYPES = set(ItemType)


CHECKS: dict[str, Check] = {
    "runs `seba start prob`": lambda r: (
        bool(r.ran("start", "prob")),
        f"{r.ran('start')}",
    ),
    "records no grade (the learner has not answered anything yet)": lambda r: (
        not r.ran("grade"),
        f"grade calls: {r.ran('grade')}",
    ),
    "reply reveals no review card answer (no 1/3, {2,4,6} or HH/HT/TH)": lambda r: (
        not re.search(r"1/3|⅓|\{2, ?4, ?6\}|HT", r.reply),
        "searched reply for card backs",
    ),
    "reply has exactly one question mark": lambda r: (
        questions(r) == 1,
        f"{questions(r)} '?'",
    ),
    "reply has at most one question mark": lambda r: (
        questions(r) <= 1,
        f"{questions(r)} '?'",
    ),
    "reply has no question mark (the learner is leaving)": lambda r: (
        questions(r) == 0,
        f"{questions(r)} '?'",
    ),
    "reply uses no LaTeX": no_latex,
    "reply has no routine praise (great, excellent, nice try, good job, well done)": lambda r: (
        not re.search(
            r"\b(great|excellent|nice try|good job|well done)\b", r.reply, re.I
        ),
        "searched reply for praise words",
    ),
    "grades the die card `again`": die_graded("again"),
    "grades the die card `hard`": die_graded("hard"),
    "the grade carries a --note of one sentence with no line breaks": one_sentence_note,
    "does not grade the coin card (the learner has not answered it)": lambda r: (
        r.review(r.coin) is None,
        f"coin review: {r.review(r.coin)}",
    ),
    "never runs `seba abandon`": lambda r: (
        not r.ran("abandon"),
        f"{r.ran('abandon')}",
    ),
    "never runs `seba abandon --discard`": lambda r: (
        not r.ran("abandon", "--discard"),
        f"{r.ran('abandon')}",
    ),
    "the session is still pending and still holds the recorded grade": lambda r: (
        r.review(r.die) is not None,
        f"pending: {r.pending is not None}; die review: {r.review(r.die)}",
    ),
    "does not start independence as a concept this session (no `--status started` on independence)": lambda r: (
        not any(c.id == "independence" for c in r.record.concepts),
        f"concept calls: {r.record.concepts}",
    ),
    "no session is left pending": lambda r: (
        r.pending is None,
        f"pending: {r.pending is not None}",
    ),
    "session 2 is saved to the learner's history": lambda r: (
        "002.md" in r.sessions,
        f"sessions: {r.sessions}",
    ),
    "mints at least one card for conditional-probability": lambda r: (
        any(i.concept == "conditional-probability" for i in r.record.new_items),
        f"minted: {[i.front for i in r.record.new_items]}",
    ),
    "conditional-probability is not recorded completed in the pending session": lambda r: (
        not r.moved("completed"),
        f"concept calls: {r.record.concepts}",
    ),
    "does not end the session yet (the learner's recap has not happened)": lambda r: (
        r.pending is not None and not r.ran("end"),
        f"end calls: {r.ran('end')}; pending: {r.pending is not None}",
    ),
    "the die card's grade stays `again` (no regrade)": lambda r: (
        r.grade(r.die) == "again" and not r.ran("grade"),
        f"die review: {r.review(r.die)}; grade calls: {r.ran('grade')}",
    ),
    "the session is saved complete (not INCOMPLETE) and none is left pending": lambda r: (
        r.pending is None and r.record.complete,
        f"pending: {r.pending is not None}; complete: {r.record.complete}",
    ),
    "the coin card (never reached) is graded `skipped`": lambda r: (
        r.grade(r.coin) == "skipped",
        f"coin review: {r.review(r.coin)}",
    ),
    "the --summary has 3 to 6 sentences": lambda r: (
        3 <= sentences(r.record.summary) <= 6,
        f"{sentences(r.record.summary)} sentences: {r.record.summary!r}",
    ),
    "the --hint names no time or count quantity (minutes, problems, cards...)": lambda r: (
        bool(r.record.next_session_hint)
        and not QUANTITY.search(r.record.next_session_hint or ""),
        f"hint: {r.record.next_session_hint!r}",
    ),
    "records bayes-rule `--status started`": lambda r: (
        r.started("bayes-rule") > 0,
        f"concept calls: {r.record.concepts}",
    ),
    "does not reopen conditional-probability (the learner has not agreed)": lambda r: (
        not r.moved("reopened"),
        f"concept calls: {r.record.concepts}",
    ),
    "reply draws an ASCII diagram (a code block of 3+ lines)": lambda r: (
        any(
            len(b.strip().splitlines()) >= 3
            for b in re.findall(r"```[^\n]*\n(.*?)```", r.reply, re.S)
        ),
        "looked for fenced code blocks",
    ),
    "reply does not state the answer (1/3)": lambda r: (
        not re.search(r"1/3|⅓|one in three|one out of three", r.reply, re.I),
        "searched reply for 1/3",
    ),
    "every `seba mint` call uses a valid card type": lambda r: (
        all(
            c[c.index("--type") + 1] in TYPES
            for c in r.calls
            if c[1:2] == ["mint"] and "--type" in c
        ),
        f"types: {[c[c.index('--type') + 1] for c in r.calls if '--type' in c]}",
    ),
    "records `started` on conditional-probability only once (it was already recorded)": lambda r: (
        r.started("conditional-probability") == 1,
        f"concept calls: {r.record.concepts}",
    ),
    "reply does not list the even faces (finding them is the learner's next step)": lambda r: (
        not re.search(r"2\D{1,12}4\D{1,12}6", r.reply),
        "searched reply for 2 … 4 … 6",
    ),
}


def main() -> None:
    name, root = sys.argv[1], Path(sys.argv[2])
    spec = next(e for e in json.loads(EVALS.read_text())["evals"] if e["name"] == name)
    run = Run(root)
    results = []
    for text in spec["assertions"]:
        if text.startswith("[check] "):
            passed, evidence = CHECKS[text.removeprefix("[check] ")](run)
            results.append({"text": text, "passed": passed, "evidence": evidence})
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
