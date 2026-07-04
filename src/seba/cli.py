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
