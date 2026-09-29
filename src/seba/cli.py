from datetime import date, datetime, timezone
from pathlib import Path

import typer
import yaml
from pydantic import ValidationError

from seba import config
from seba.models import (
    Emphasis,
    GoalSettings,
    GoalState,
    PendingSession,
    SubjectProfile,
)
from seba.scheduler.agenda import build_agenda
from seba.scheduler.apply import apply_record
from seba.scheduler.items import due_now
from seba.session.loader import load_overlay, load_profile
from seba.session.pending import (
    PendingError,
    clear_pending,
    load_pending,
    pending_path,
    save_pending,
)
from seba.session.tools import ToolHandler
from seba.store.store import Store, StoreError
from seba.syllabus.graph import SyllabusError, load_syllabus
from seba.ui import repl
from seba.ui.view import build_view_data, render_view

app = typer.Typer(no_args_is_help=True)


def _store() -> Store:
    return Store(config.data_dir())


def _profile(subject: str) -> SubjectProfile:
    p = load_profile(subject)
    if p is None:
        typer.echo(
            f"no subject profile '{subject}' — create "
            f"{config.data_dir()}/subjects/{subject}/profile.yaml "
            f"(copy from subjects/_templates/)",
            err=True,
        )
        raise typer.Exit(1)
    return p


def _load_goal(store: Store, goal: str) -> GoalState:
    """load_goal, but turn a StoreError into a clean stderr + exit 1."""
    try:
        return store.load_goal(goal)
    except StoreError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("new-goal")
def new_goal(
    name: str,
    subject: str = typer.Option(...),
    from_file: Path = typer.Option(
        ...,
        "--from-file",
        exists=True,
        dir_okay=False,
        help="syllabus YAML drafted in conversation",
    ),
):
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
    try:
        goals = _store().list_goals()
    except StoreError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    if not goals:
        typer.echo("no goals yet")
        return
    for g in goals:
        done_msg = f"{g.session_count} sessions · {g.due_count} due today"
        repl.console.print(f"[bold]{g.name}[/] ({g.subject}) — {done_msg}")


NO_TRANSCRIPT = "(session conducted via Claude Code; no transcript captured)\n"


def _load_pending_or_exit(ppath: Path) -> PendingSession | None:
    """load_pending, but turn a malformed file into a clean stderr + exit 1."""
    try:
        return load_pending(ppath)
    except PendingError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


def _session(goal: str):
    """Load the in-progress session or exit with a hint."""
    store = _store()
    ppath = pending_path(store.data_dir, goal)
    pending = _load_pending_or_exit(ppath)
    if pending is None:
        typer.echo(
            f"no session in progress for '{goal}' — run: seba start {goal}", err=True
        )
        raise typer.Exit(1)
    state = _load_goal(store, goal)
    handler = ToolHandler(
        pending.agenda,
        state.syllabus,
        config.data_dir() / "sources",
        _profile(state.subject).max_reviews_per_session,
        state.passes,
        state.settings.completion_passes,
        {i.concept for i in state.items},
    )
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
    state = _load_goal(store, goal)
    updated = apply_record(state, pending.record, datetime.now(timezone.utc))
    # Save durably BEFORE clearing pending: a crash inside save_session (file
    # writes + git) must never leave the session lost with the pending gone.
    # ponytail: narrow double-apply window if a crash lands between save and
    # clear; a start-side idempotency guard is deferred to the T6 dogfood.
    store.save_session(goal, pending.record, NO_TRANSCRIPT, updated)
    clear_pending(ppath)
    repl.receipt(pending.record)


@app.command()
def start(
    goal: str,
    concept: str | None = typer.Option(
        None, "--concept", help="teach this concept today instead of the usual pick"
    ),
):
    store = _store()
    state = _load_goal(store, goal)
    ppath = pending_path(store.data_dir, goal)
    pending = _load_pending_or_exit(ppath)
    if pending is not None and concept is not None:
        raise _refuse(
            f"a session is already in progress for '{goal}' — end or abandon it "
            "before choosing a concept"
        )
    if pending is None:
        profile = _profile(state.subject)  # only needed to build a new agenda
        try:
            agenda = build_agenda(
                state,
                profile,
                date.today(),
                config.data_dir() / "sources",
                teach=concept,
            )
        except SyllabusError as e:
            raise _refuse(str(e))
        pending = PendingSession(goal=goal, agenda=agenda, started=date.today())
        save_pending(ppath, pending)
    else:
        typer.echo("(resuming session in progress)")
    graded = sorted({r.id for r in pending.record.reviews})
    typer.echo(
        yaml.safe_dump(
            {
                "agenda": pending.agenda.model_dump(mode="json"),
                "subject_style": load_overlay(state.subject),
                "already_graded": graded,
                "ungraded_reviews": [
                    r.id for r in pending.agenda.review_items if r.id not in set(graded)
                ],
                "minted_so_far": len(pending.record.new_items),
            },
            sort_keys=False,
            allow_unicode=True,
        )
    )


@app.command()
def grade(goal: str, item_id: str, grade: str, note: str | None = typer.Option(None)):
    _dispatch(goal, "grade_review", {"id": item_id, "grade": grade, "note": note})


@app.command()
def mint(
    goal: str,
    concept: str = typer.Option(...),
    type: str = typer.Option(...),
    front: str = typer.Option(...),
    back: str = typer.Option(...),
):
    _dispatch(
        goal,
        "mint_item",
        {"concept": concept, "type": type, "front": front, "back": back},
    )


@app.command("concept")
def concept_cmd(
    goal: str,
    concept_id: str,
    status: str | None = typer.Option(None, help="started|completed|reopened"),
    note: str | None = typer.Option(None),
    evidence: str | None = typer.Option(
        None, help="required with --status completed: the exchange that showed it"
    ),
):
    _dispatch(
        goal,
        "update_concept",
        {
            "id": concept_id,
            "status_change": status,
            "note": note,
            "evidence": evidence,
        },
    )


@app.command()
def end(
    goal: str, summary: str = typer.Option(...), hint: str = typer.Option(..., "--hint")
):
    store, pending, handler, ppath = _session(goal)
    result, is_error = handler.handle(
        "end_session", {"summary": summary, "next_session_hint": hint}
    )
    if is_error:
        typer.echo(result, err=True)
        raise typer.Exit(1)
    _finish(store, goal, pending, ppath)


@app.command()
def abandon(
    goal: str,
    discard: bool = typer.Option(
        False, "--discard", help="drop recorded outcomes instead of saving INCOMPLETE"
    ),
):
    store, pending, handler, ppath = _session(goal)
    if discard:
        clear_pending(ppath)
        typer.echo("pending session discarded")
        return
    _finish(store, goal, pending, ppath)  # complete=False → INCOMPLETE marker


@app.command()
def view(
    goal: str,
    json_out: bool = typer.Option(
        False, "--json", help="print the data blob instead of writing HTML"
    ),
    open_browser: bool = typer.Option(False, "--open", help="open the rendered view"),
):
    store = _store()
    state = _load_goal(store, goal)
    data = build_view_data(state, date.today())
    if json_out:
        typer.echo(data.model_dump_json())
        return
    out = store.data_dir / "goals" / goal / "view.html"
    out.write_text(render_view(data))
    typer.echo(str(out))
    if open_browser:
        typer.launch(str(out))


_FLAG = {
    "desired_retention": "--retention",
    "max_interval_days": "--max-interval",
    "concepts_per_session": "--concepts-per-session",
    "completion_passes": "--completion-passes",
}
_LEVELS = ("less", "normal", "more")


def _range(field: str) -> str:
    """The valid range of a setting, read off the model so it is stated once."""
    spec = GoalSettings.model_json_schema()["properties"][field]
    low, high = spec.get("minimum"), spec.get("maximum")
    return f"between {low} and {high}" if high is not None else f"at least {low}"


def _refuse(message: str) -> typer.Exit:
    typer.echo(message, err=True)
    return typer.Exit(1)


@app.command()
def tune(
    goal: str,
    retention: float | None = typer.Option(None, "--retention"),
    max_interval: int | None = typer.Option(None, "--max-interval"),
    concepts_per_session: int | None = typer.Option(None, "--concepts-per-session"),
    completion_passes: int | None = typer.Option(None, "--completion-passes"),
    concept: str | None = typer.Option(None, "--concept"),
    emphasis: str | None = typer.Option(None, "--emphasis", help="less|normal|more"),
):
    store = _store()
    state = _load_goal(store, goal)
    asked = {
        "desired_retention": retention,
        "max_interval_days": max_interval,
        "concepts_per_session": concepts_per_session,
        "completion_passes": completion_passes,
    }
    changes = {k: v for k, v in asked.items() if v is not None}
    if not changes and concept is None and emphasis is None:
        typer.echo(
            yaml.safe_dump(
                {
                    "settings": state.settings.model_dump(mode="json"),
                    "emphasis": {c: str(e) for c, e in state.emphasis.items()},
                },
                sort_keys=False,
            )
        )
        return

    try:
        settings = GoalSettings.model_validate(
            {**state.settings.model_dump(), **changes}
        )
    except ValidationError as e:
        fields = [str(err["loc"][0]) for err in e.errors()]
        raise _refuse("\n".join(f"{_FLAG[f]} must be {_range(f)}" for f in fields))

    said = [
        f"{k}: {getattr(state.settings, k)} → {v}"
        for k, v in changes.items()
        if getattr(state.settings, k) != v
    ]
    levels = dict(state.emphasis)
    items = state.items
    if (concept is None) != (emphasis is None):
        raise _refuse("--concept and --emphasis go together")
    if concept is not None and emphasis is not None:
        if concept not in {c.id for c in state.syllabus.concepts}:
            raise _refuse(f"unknown concept: '{concept}'")
        if emphasis not in _LEVELS:
            raise _refuse(f"--emphasis must be one of: {', '.join(_LEVELS)}")
        was = str(levels.get(concept, "normal"))
        if emphasis == "normal":
            levels.pop(concept, None)
        else:
            levels[concept] = Emphasis(emphasis)
        line = f"emphasis [{concept}]: {was} → {emphasis}"
        if emphasis == "more":
            # The one direct override of the schedule, and only because the
            # learner asked: "I keep losing functors" on Monday, functors Tuesday.
            mine = [i for i in items if i.concept == concept]
            items = [
                due_now(i, date.today()) if i.concept == concept else i for i in items
            ]
            line += f" ({len(mine)} card{'' if len(mine) == 1 else 's'} due now)"
        if was != emphasis or emphasis == "more":
            said.append(line)

    # Nothing to say means nothing to write; and save_tuning itself declines to
    # commit when the files come out identical (emphasis `more` set twice).
    if not said or not store.save_tuning(goal, settings, levels, items):
        typer.echo("nothing changed")
        return
    typer.echo("\n".join(said))
