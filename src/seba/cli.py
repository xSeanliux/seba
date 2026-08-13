from datetime import date, datetime, timezone
from pathlib import Path

import typer
import yaml

from seba import config
from seba.models import PendingSession, SubjectProfile
from seba.scheduler.agenda import build_agenda
from seba.scheduler.apply import apply_record
from seba.session.loader import load_overlay, load_profile
from seba.session.pending import (
    PendingError,
    clear_pending,
    load_pending,
    pending_path,
    save_pending,
)
from seba.session.tools import ToolHandler
from seba.store.store import Store
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
    goals = _store().list_goals()
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
    state = store.load_goal(goal)
    handler = ToolHandler(
        pending.agenda,
        state.syllabus,
        config.data_dir() / "sources",
        _profile(state.subject).max_reviews_per_session,
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
    state = store.load_goal(goal)
    updated = apply_record(state, pending.record, datetime.now(timezone.utc))
    # Save durably BEFORE clearing pending: a crash inside save_session (file
    # writes + git) must never leave the session lost with the pending gone.
    # ponytail: narrow double-apply window if a crash lands between save and
    # clear; a start-side idempotency guard is deferred to the T6 dogfood.
    store.save_session(goal, pending.record, NO_TRANSCRIPT, updated)
    clear_pending(ppath)
    repl.receipt(pending.record)


@app.command()
def start(goal: str):
    store = _store()
    state = store.load_goal(goal)
    ppath = pending_path(store.data_dir, goal)
    pending = _load_pending_or_exit(ppath)
    if pending is None:
        profile = _profile(state.subject)  # only needed to build a new agenda
        agenda = build_agenda(
            state, profile, date.today(), config.data_dir() / "sources"
        )
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
    status: str | None = typer.Option(None, help="started|completed"),
    note: str | None = typer.Option(None),
):
    _dispatch(
        goal,
        "update_concept",
        {"id": concept_id, "status_change": status, "note": note},
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
