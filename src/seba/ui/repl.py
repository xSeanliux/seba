from rich.console import Console
from rich.panel import Panel

from seba.models import Agenda, SessionRecord

console = Console()


def briefing_card(agenda: Agenda) -> None:
    teach = agenda.teach_concept.name if agenda.teach_concept else "review only"
    console.print(
        Panel(
            f"{agenda.goal} · session {agenda.session_number} · "
            f"{len(agenda.review_items)} due · today: {teach}\n\n{agenda.briefing}",
            title="tutor",
        )
    )


def receipt(record: SessionRecord) -> None:
    graded = sum(1 for r in record.reviews if r.grade != "skipped")
    skipped = len(record.reviews) - graded
    parts = [f"{graded} reviewed"]
    if skipped:
        parts.append(f"{skipped} skipped")
    parts.append(f"{len(record.new_items)} minted")
    parts += [f"{c.id} → {c.status_change}" for c in record.concepts if c.status_change]
    status = "" if record.complete else "  [red]INCOMPLETE[/]"
    console.print("[dim]" + " · ".join(parts) + "[/]" + status)
