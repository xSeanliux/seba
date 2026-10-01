from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal

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
from seba.syllabus.graph import SyllabusError, edit, frontier, load_syllabus
from seba.ui import repl
from seba.ui.view import build_view_data, render_view

app = typer.Typer(
    no_args_is_help=True,
    help=(
        "A long-term personal tutor: spaced review and guided teaching for "
        "goals that span many sessions. Each command is one step, reading "
        "and writing state in $SEBA_DATA_DIR (default ~/seba-data), its own "
        "git repository. Driven by the seba-tutor and seba-syllabus Claude "
        "Code skills; seba status is the one command run by hand."
    ),
)


def _store() -> Store:
    return Store(config.data_dir())


def _profile(subject: str) -> SubjectProfile:
    p = load_profile(subject)
    if p is None:
        typer.echo(
            f"no subject profile '{subject}' — create "
            f"{config.data_dir()}/subjects/{subject}/profile.yaml "
            f"(copy from {config.REPO_ROOT / 'subjects' / '_templates'}/)",
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
    subject: str = typer.Option(..., help="an existing subject profile's name"),
    from_file: Path = typer.Option(
        ...,
        "--from-file",
        exists=True,
        dir_okay=False,
        help="syllabus YAML drafted in conversation: goal, subject and concepts",
    ),
):
    """Create a goal from a syllabus drafted in conversation.

    Used by the syllabus skill, once, to set up a goal; never run mid-session.
    Reads the subject profile and the syllabus file. Writes the goal's
    directory (goal.yaml, syllabus.yaml, items.jsonl, notes.md) and commits
    "<name>: created". Prints a line confirming the goal and how to start it.

    Refuses:
    - no subject profile '<subject>' — create <dir>/profile.yaml (copy from
      <repo>/subjects/_templates/)
    - <file>: <detail> — the syllabus file does not parse or validate
      (duplicate concept ids, a prereq/soft_prereq/confusable_with naming an
      id not in the file, or a prereq/soft_prereq cycle)
    """
    store = _store()
    _profile(subject)
    try:
        syllabus = load_syllabus(from_file)
    except SyllabusError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    store.create_goal(name, syllabus, subject)
    typer.echo(f"goal '{name}' created — start with: seba start {name}")


@app.command("extend")
def extend_cmd(
    goal: str,
    from_file: Path = typer.Option(
        ...,
        "--from-file",
        exists=True,
        dir_okay=False,
        help="concepts to add: a bare list, or a mapping with a 'concepts:' list",
    ),
):
    """Append learner-approved concepts to a goal's syllabus.

    Used by the syllabus skill, drafting concepts for a new source; or by the
    tutor mid-session, for a gap found while teaching. Reads the syllabus on
    disk and, if a session is pending, that session's recorded concept
    changes, so a new concept is judged against the syllabus as the session
    has changed it. Writes syllabus.yaml and commits "<goal>: extended
    (+<n>)". Prints the added ids. Acts at once; never touches the pending
    session.

    Refuses:
    - no such goal: '<goal>'
    - <file>: holds no concepts — expected a list of concepts, or a mapping
      with a 'concepts:' list
    - <file>: concept ids already in the syllabus: [<ids>]
    - <file>: concept ids repeated in the file: [<ids>]
    - <file>: new concept '<id>' has status <status>; a new concept is
      unseen, or done if the learner already has it
    - <file>: new concept '<id>' depends on <ids>, which is dropped —
      restore that first
    - <file>: <detail> — the file does not parse, or a concept fails
      validation
    """
    # Never touches the pending session: its agenda stands, and the next
    # command's handler is built from the extended syllabus on disk. Its
    # record is read so the new concepts are judged against what it changed.
    store = _store()
    pending = _load_pending_or_exit(pending_path(store.data_dir, goal))
    try:
        added = store.extend_syllabus(
            goal, from_file, pending.record.concepts if pending else None
        )
    except StoreError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    typer.echo(f"added {len(added)} concept(s): {', '.join(added)}")


_EDIT_FLAGS = "--name, --add-prereq, --remove-prereq, --add-source or --status"
_EDIT_STATUS: dict[str, Literal["dropped", "restored"]] = {
    "dropped": "dropped",
    "restored": "restored",
}


@app.command("edit")
def edit_cmd(
    goal: str,
    concept_id: str,
    name: str | None = typer.Option(None, "--name", help="the concept's new name"),
    add_prereq: list[str] | None = typer.Option(
        None, "--add-prereq", help="a hard prerequisite (concept id) to add; repeatable"
    ),
    remove_prereq: list[str] | None = typer.Option(
        None,
        "--remove-prereq",
        help="a hard prerequisite (concept id) to remove; repeatable",
    ),
    add_source: list[str] | None = typer.Option(
        None, "--add-source", help="a locator to add to its sources; repeatable"
    ),
    status: str | None = typer.Option(None, "--status", help="dropped or restored"),
):
    """Change one concept's name, hard prerequisites, sources, or dropped
    status, between sessions.

    Used by the learner through the syllabus skill. Reads the syllabus on
    disk. Writes syllabus.yaml and commits "<goal>: edited <concept_id>",
    unless nothing changed. Prints one line per change (name, prereq added or
    removed, source added, status), or "nothing changed". Flags combine; give
    at least one.

    Refuses:
    - a session is in progress for '<goal>' — end or abandon it before
      editing the syllabus
    - no such goal: '<goal>'
    - nothing to edit — give --name, --add-prereq, --remove-prereq,
      --add-source or --status
    - --name needs text
    - --status must be dropped or restored
    - unknown concept: '<concept_id>'
    - '<concept_id>' does not depend on <id> — --remove-prereq names an edge
      that is not there
    - '<concept_id>' cannot depend on itself — --add-prereq names itself
    - '<concept_id>' already depends on <id> — --add-prereq names an edge
      already there
    - concept '<concept_id>' has unknown prereqs: [<ids>] — --add-prereq
      names a concept id that does not exist
    - cannot drop '<concept_id>': <ids> depend on it — drop them first, or
      remove the edge with seba edit --remove-prereq
    - '<concept_id>' is already dropped
    - '<concept_id>' is <status>; only a dropped concept can be restored
    - cannot restore '<concept_id>': it depends on <ids>, which is dropped —
      restore that first
    - concept '<concept_id>' depends on <ids>, which is dropped — restore
      that first — a prerequisite added in this same call is dropped

    Acts at once.
    """
    store = _store()
    # A pending record and a direct edit must not disagree about the syllabus:
    # `seba end` replays the record onto whatever is on disk.
    if _load_pending_or_exit(pending_path(store.data_dir, goal)) is not None:
        raise _refuse(
            f"a session is in progress for '{goal}' — end or abandon it before "
            "editing the syllabus"
        )
    state = _load_goal(store, goal)
    given = (name, status, add_prereq, remove_prereq, add_source)
    if all(v is None for v in given):
        raise _refuse(f"nothing to edit — give {_EDIT_FLAGS}")
    if name is not None:
        name = " ".join(name.split())  # one line, as `seba concepts` prints it
        if not name:
            raise _refuse("--name needs text")
    if status is not None and status not in _EDIT_STATUS:
        raise _refuse("--status must be dropped or restored")
    try:
        edited = edit(
            state.syllabus,
            concept_id,
            name=name,
            add_prereqs=add_prereq,
            remove_prereqs=remove_prereq,
            add_sources=add_source,
            status=_EDIT_STATUS.get(status or ""),
        )
    except SyllabusError as e:
        raise _refuse(str(e))
    [was] = [c for c in state.syllabus.concepts if c.id == concept_id]
    [now] = [c for c in edited.concepts if c.id == concept_id]
    said = [f'name: "{was.name}" → "{now.name}"'] if was.name != now.name else []
    said += [f"prereq added: {p}" for p in now.prereqs if p not in was.prereqs]
    said += [f"prereq removed: {p}" for p in was.prereqs if p not in now.prereqs]
    said += [f"source added: {s}" for s in now.sources if s not in was.sources]
    if was.status != now.status:
        said.append(f"status: {was.status} → {now.status}")
    if not said:
        typer.echo("nothing changed")
        return
    store.commit_syllabus(goal, edited, f"{goal}: edited {concept_id}")
    typer.echo("\n".join(said))


@app.command()
def status():
    """List every goal with its session count and how many cards are due today.

    Used by anyone, any time; the one command run outside a skill. Reads
    every goal under $SEBA_DATA_DIR. Writes nothing. Prints "no goals yet",
    or one line per goal: name, subject, sessions so far, cards due today.
    """
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
        None,
        "--concept",
        help="teach this concept instead of the usual pick; must be in "
        "progress or on the frontier",
    ),
):
    """Begin today's session, or resume one already in progress.

    Used by the tutor, once per session, before doing anything else. Reads
    the goal's state and builds today's agenda (what's due, what to teach)
    if none is pending; resuming prints "(resuming session in progress)"
    instead. Writes session.pending.yaml. Prints the agenda as YAML:
    `agenda`, `subject_style`, `already_graded`, `ungraded_reviews`,
    `minted_so_far`, `concept_calls_so_far`.

    Refuses:
    - no such goal: '<goal>'
    - a session is already in progress for '<goal>' — end or abandon it
      before choosing a concept — only when --concept is given and a session
      is already pending
    - '<concept>' is dropped; restore it first
    - '<concept>' is done; reopen it if the learner wants it taught again
    - '<concept>' is not ready: <ids> must be done first — a hard
      prerequisite is not yet done
    - unknown concept: '<concept>'

    `--concept` is refused once a session is pending; start a new session to
    use it.
    """
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
                "concept_calls_so_far": len(pending.record.concepts),
            },
            sort_keys=False,
            allow_unicode=True,
        )
    )


@app.command()
def grade(
    goal: str,
    item_id: str,
    grade: str,
    note: str | None = typer.Option(
        None,
        help="required for again or hard: what went wrong or what the help was for",
    ),
):
    """Record a review grade for one card, as its exchange resolves.

    Used by the tutor, immediately after each review item in `seba start`'s
    `agenda.review_items`. Grade is again, hard, good, easy or skipped: skip
    only an item the session never reached, or whose concept was dropped this
    session. Reads this session's pending record. Writes
    session.pending.yaml. Prints "recorded".

    Refuses:
    - no session in progress for '<goal>' — run: seba start <goal>
    - '<item_id>' is not in this session's review items
    - '<item_id>' already graded
    - '<item_id>' belongs to '<concept>', which is dropped — grade it skipped
    - grading '<grade>' requires --note saying what went wrong (again) or
      what the help was for (hard)
    """
    _dispatch(goal, "grade_review", {"id": item_id, "grade": grade, "note": note})


@app.command()
def mint(
    goal: str,
    concept: str = typer.Option(..., help="the concept this card belongs to"),
    type: str = typer.Option(..., help="the card's item type, e.g. recall or apply"),
    front: str = typer.Option(..., help="the question side"),
    back: str = typer.Option(..., help="the answer side"),
):
    """Create one spaced-repetition card for a concept.

    Used by the tutor, mid-session, for material worth retaining a month —
    the transfer version of a problem, not the one just worked. Reads this
    session's pending record to check the per-session mint budget. Writes
    session.pending.yaml. Prints "minted".

    Refuses:
    - no session in progress for '<goal>' — run: seba start <goal>
    - mint budget reached (<n> this session); review capacity is <m>/session
    - unknown concept: '<concept>'
    - '<concept>' is dropped; restore it before minting a card for it
    """
    _dispatch(
        goal,
        "mint_item",
        {"concept": concept, "type": type, "front": front, "back": back},
    )


@app.command("concept")
def concept_cmd(
    goal: str,
    concept_id: str,
    status: str | None = typer.Option(
        None, help="started, completed, reopened, dropped or restored"
    ),
    note: str | None = typer.Option(
        None, help="a durable note: a misconception (prefix MISCONCEPTION:) or strength"
    ),
    evidence: str | None = typer.Option(
        None, help="required with --status completed: the exchange that showed it"
    ),
    add_source: str | None = typer.Option(
        None, help="a locator to add to the concept's sources"
    ),
):
    """Record a concept's progress, a note, or a source, during a session.

    Used by the tutor, as teaching happens: --status started when teaching
    begins, --status completed once the delayed check passes, a note for a
    misconception or strength. `dropped`, `restored` and `--add-source` are
    recorded now but only take effect in the syllabus at `seba end`; `started`
    and `completed` take effect at once, since later calls in the same
    session (passes, a repeat teach) depend on them. Reads this session's
    pending record and the syllabus as it stands with that record replayed.
    Writes session.pending.yaml. Prints "recorded", "recorded (no cards for
    this concept, so the delayed check was skipped)" for a completion with no
    cards, or the matching refusal.

    Refuses:
    - no session in progress for '<goal>' — run: seba start <goal>
    - unknown concept: '<concept_id>'
    - --add-source needs a locator
    - '<locator>' is already a source of '<concept_id>'
    - '<concept_id>' is dropped; restore it first — started, completed or
      reopened on a dropped concept
    - '<concept_id>' is <status>; only a done concept can be reopened
    - '<concept_id>' is done; reopening it is the learner's decision — if
      they agree, use --status reopened
    - '<concept_id>' is not ready: <ids> must be done first — started on an
      unseen concept with an undone hard prerequisite
    - completing a concept requires --evidence: name the specific exchange in
      this session that demonstrated the learner has it
    - '<concept_id>' has <n> of <m> unaided pass(es) in a later session; each
      is a good/easy review of one of its cards, in a session after the one
      where teaching started or the concept was reopened

    `dropped`, `restored` and a source added here apply at `seba end`;
    `started`, `completed` and `reopened` apply at once.
    """
    _dispatch(
        goal,
        "update_concept",
        {
            "id": concept_id,
            "status_change": status,
            "note": note,
            "evidence": evidence,
            "add_source": add_source,
        },
    )


@app.command()
def end(
    goal: str,
    summary: str = typer.Option(..., help="3-6 sentences on what happened"),
    hint: str = typer.Option(
        ..., "--hint", help="a concrete procedure and stopping rule for next session"
    ),
):
    """Close the session and save it.

    Applies the session's drops, restores and added sources to the syllabus
    and folds its grades into the schedule. Used by the tutor, once, after
    every review is graded. Reads this
    session's pending record and the goal's state. Writes the session's files
    (summary, outcomes, transcript) and the updated syllabus.yaml and
    items.jsonl, commits "<goal>: session <n>", and deletes
    session.pending.yaml. Prints a receipt of what the session recorded.

    Refuses:
    - no session in progress for '<goal>' — run: seba start <goal>
    - session already ended
    - cannot end: ungraded review items: <ids>. Grade each (or grade as
      'skipped') first.
    """
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
    """End a session the learner quit early, without a summary or hint.

    Used by the tutor when the learner stops abruptly; never leave a session
    pending. By default, saves what was recorded as an INCOMPLETE session, the
    same as `seba end` otherwise. With --discard, throws away everything
    recorded this session instead: no grades, cards or concept changes reach
    disk. Reads this session's pending record. Writes the session's files
    (with --discard, nothing) and deletes session.pending.yaml. Prints a
    receipt of what was discarded, or (without --discard) the same receipt
    `seba end` prints.

    Refuses:
    - no session in progress for '<goal>' — run: seba start <goal>
    """
    store, pending, handler, ppath = _session(goal)
    if discard:
        clear_pending(ppath)
        r = pending.record
        typer.echo(
            f"pending session discarded ({len(r.reviews)} grades, "
            f"{len(r.new_items)} minted, {len(r.concepts)} concept calls)"
        )
        return
    _finish(store, goal, pending, ppath)  # complete=False → INCOMPLETE marker


@app.command()
def view(
    goal: str,
    json_out: bool = typer.Option(
        False, "--json", help="print the view's data as JSON instead of writing HTML"
    ),
    open_browser: bool = typer.Option(
        False, "--open", help="open the written HTML file in the browser"
    ),
):
    """Render the goal's dependency graph and card status.

    Used by anyone, any time, usually after `seba end`. Reads the goal's
    state. Writes nothing but the rendered file itself:
    goals/<goal>/view.html, overwritten each run, never committed. With
    --json, prints the view's data instead of writing that file. Prints the
    path to the written file, unless --json.

    Refuses:
    - no such goal: '<goal>'
    """
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


@app.command()
def concepts(
    goal: str,
    grep: str | None = typer.Option(
        None,
        "--grep",
        help="only concepts whose id or name contains TEXT (case-insensitive)",
    ),
):
    """List the goal's curriculum: direction, every concept, and the frontier.

    Used by anyone, any time, to look up a concept id or check what is ready.
    Read-only: reads the goal's syllabus and writes nothing. Prints a
    "direction:" line; "session: in progress" if a session is pending (`seba
    edit` refuses until it ends); one line per concept — id, status, name,
    "prereqs: ..." if it has hard prerequisites, "dropped from: <status>" if
    dropped; then a "frontier:" line listing the concepts ready to teach.
    --grep limits the concept lines to those whose id or name contains TEXT.

    Refuses:
    - no such goal: '<goal>'
    """
    store = _store()
    state = _load_goal(store, goal)
    shown = [
        c
        for c in state.syllabus.concepts
        if grep is None or grep.casefold() in f"{c.id}\n{c.name}".casefold()
    ]
    id_w = max((len(c.id) for c in shown), default=0)
    status_w = max((len(c.status) for c in shown), default=0)
    typer.echo(f"direction: {state.direction}")
    if pending_path(store.data_dir, goal).exists():
        typer.echo("session: in progress")  # `seba edit` refuses until it ends
    for c in shown:
        line = f"{c.id:<{id_w}}  {c.status:<{status_w}}  {c.name}"
        if c.prereqs:
            line += f"  prereqs: {', '.join(c.prereqs)}"
        if c.dropped_from is not None:
            line += f"  dropped from: {c.dropped_from}"
        typer.echo(line)
    ready = [c.id for c in frontier(state.syllabus)]
    typer.echo(f"frontier: {', '.join(ready) or 'none'}")


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
    retention: float | None = typer.Option(
        None,
        "--retention",
        help="desired retention, 0.70 to 0.97 (default 0.9); lower means longer "
        "intervals",
    ),
    max_interval: int | None = typer.Option(
        None,
        "--max-interval",
        help="longest gap between reviews, in days (default 180)",
    ),
    concepts_per_session: int | None = typer.Option(
        None,
        "--concepts-per-session",
        help="how many concepts a session may teach, 1 to 5 (default 1)",
    ),
    completion_passes: int | None = typer.Option(
        None,
        "--completion-passes",
        help="later sessions a concept's cards must pass before it can "
        "complete, at least 1 (default 1)",
    ),
    concept: str | None = typer.Option(
        None, "--concept", help="the concept whose emphasis to change; needs --emphasis"
    ),
    emphasis: str | None = typer.Option(
        None, "--emphasis", help="less, normal or more"
    ),
    direction: str | None = typer.Option(
        None, "--direction", help="what the goal is for, as the learner now puts it"
    ),
):
    """Show or change a goal's settings, one concept's emphasis, or its
    direction.

    Used by the learner, through either skill, usually between sessions, but
    also mid-session for a direct ask ("review bayes more"). With no flags,
    reads and prints the goal's direction, settings and non-default emphasis;
    with any flag, changes what it names. Reads the goal's state. Writes
    goal.yaml and items.jsonl (only emphasis `more` touches cards, moving
    them to due now) and commits "<goal>: tuned", unless nothing changed.
    Prints what changed, one line per setting, or "nothing changed".

    Refuses:
    - no such goal: '<goal>'
    - --retention must be between 0.7 and 0.97
    - --max-interval must be at least 1
    - --concepts-per-session must be between 1 and 5
    - --completion-passes must be at least 1
    - --direction needs text
    - --concept and --emphasis go together — one given without the other
    - unknown concept: '<concept>'
    - --emphasis must be one of: less, normal, more

    `--retention`, the interval ceiling and emphasis apply at each card's next
    review, including later in a session already under way; emphasis `more`
    also makes that concept's cards due now. `--concepts-per-session` and a
    changed emphasis otherwise show from the next session: the current
    session's review list and follow-on concepts were fixed at `seba start`.
    `--direction` is written at once.
    """
    store = _store()
    state = _load_goal(store, goal)
    asked = {
        "desired_retention": retention,
        "max_interval_days": max_interval,
        "concepts_per_session": concepts_per_session,
        "completion_passes": completion_passes,
    }
    changes = {k: v for k, v in asked.items() if v is not None}
    if not changes and concept is None and emphasis is None and direction is None:
        typer.echo(
            yaml.safe_dump(
                {
                    "direction": state.direction,
                    "settings": state.settings.model_dump(mode="json"),
                    "emphasis": {
                        c: str(e)
                        for c, e in state.emphasis.items()
                        if e != Emphasis.NORMAL
                    },
                },
                sort_keys=False,
                allow_unicode=True,
            )
        )
        return
    if direction is not None:
        # One line: a newline would put a line of its own into the briefing.
        direction = " ".join(direction.split())
        if not direction:
            raise _refuse("--direction needs text")

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
        was = str(levels.get(concept, Emphasis.NORMAL))
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
    # Against what goal.yaml holds, not the loaded direction: that falls back
    # to the syllabus's goal line, and a stated direction is still recorded.
    if direction == store.stored_direction(goal):
        direction = None  # already what the goal is for; leave goal.yaml alone
    if direction is not None:
        said.append(f'direction: "{state.direction}" → "{direction}"')

    # Nothing to say means nothing to write; and save_tuning itself declines to
    # commit when the files come out identical (emphasis `more` set twice).
    if not said or not store.save_tuning(
        goal, settings, levels, items, direction=direction
    ):
        typer.echo("nothing changed")
        return
    typer.echo("\n".join(said))
