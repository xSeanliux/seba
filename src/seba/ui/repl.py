from rich.console import Console

from seba.models import SessionRecord

console = Console()


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
