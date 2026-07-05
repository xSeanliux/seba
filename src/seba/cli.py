from datetime import date, datetime, timezone
from pathlib import Path

import anthropic
import typer

from seba import config
from seba.models import SubjectProfile
from seba.scheduler.agenda import build_agenda
from seba.scheduler.apply import apply_record
from seba.session.dialogue import make_send, run_session
from seba.session.loader import load_overlay, load_profile
from seba.session.recovery import recover_session
from seba.store.store import Store
from seba.synthesis.synthesize import default_editor, draft_syllabus, edit_until_valid
from seba.ui import repl

app = typer.Typer(no_args_is_help=False, invoke_without_command=True)


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


@app.callback()
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        learn(goal=None)


@app.command()
def learn(goal: str | None = typer.Argument(None)):
    store = _store()
    goals = store.list_goals()
    if not goals:
        typer.echo("no goals yet — run: seba new-goal NAME --subject S --toc PATH")
        raise typer.Exit(1)
    if goal is None:
        for i, g in enumerate(goals, 1):
            repl.console.print(
                f"[bold]{i}[/] {g.name} ({g.subject}) · "
                f"session {g.session_count + 1} · {g.due_count} due")
        goal = goals[int(repl.console.input("pick> ")) - 1].name

    state = store.load_goal(goal)
    profile = _profile(state.subject)
    agenda = build_agenda(state, profile, date.today(),
                          config.data_dir() / "sources")
    repl.briefing_card(agenda)

    client = anthropic.Anthropic()
    record, transcript = run_session(
        agenda, state.syllabus, load_overlay(state.subject),
        config.data_dir() / "sources", repl.TerminalIO(),
        make_send(client, config.model()))
    updated = apply_record(state, record, datetime.now(timezone.utc))
    store.save_session(goal, record, transcript, updated)
    repl.receipt(record)
    if not record.complete:
        typer.echo(f"run: seba extract {goal} {state.session_number}")


@app.command("new-goal")
def new_goal(name: str, subject: str = typer.Option(...),
             toc: Path = typer.Option(...)):
    store = _store()
    _profile(subject)  # must exist (v0: bundled or hand-copied from template)
    client = anthropic.Anthropic()

    def complete(prompt: str) -> str:
        msg = client.messages.create(model=config.recovery_model(),
                                     max_tokens=4000,
                                     messages=[{"role": "user", "content": prompt}])
        return "".join(b.text for b in msg.content if b.type == "text")

    draft = draft_syllabus(name, subject, toc.read_text(), complete)
    syllabus = edit_until_valid(draft, config.data_dir() / f"{name}-syllabus.yaml",
                                default_editor)
    store.create_goal(name, syllabus, subject)
    typer.echo(f"goal '{name}' created — start with: seba learn {name}")


@app.command()
def status():
    goals = _store().list_goals()
    if not goals:
        typer.echo("no goals yet")
        return
    for g in goals:
        done_msg = f"{g.session_count} sessions · {g.due_count} due today"
        repl.console.print(f"[bold]{g.name}[/] ({g.subject}) — {done_msg}")


@app.command()
def extract(goal: str, n: int):
    store = _store()
    state = store.load_goal(goal)
    tdir = store.data_dir / "goals" / goal / "sessions"
    transcript = (tdir / f"{n:03d}.transcript.md").read_text()
    profile = _profile(state.subject)
    agenda = build_agenda(state, profile, date.today(),
                          config.data_dir() / "sources")
    client = anthropic.Anthropic()
    record = recover_session(transcript, agenda, state.syllabus,
                             config.data_dir() / "sources",
                             make_send(client, config.recovery_model()))
    updated = apply_record(state, record, datetime.now(timezone.utc))
    store.save_session(goal, record, transcript, updated)
    repl.receipt(record)
