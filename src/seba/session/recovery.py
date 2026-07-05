import yaml

from pathlib import Path

from seba.models import Agenda, SessionRecord, Syllabus
from seba.session.dialogue import Send, _assistant_blocks
from seba.session.loader import recovery_prompt
from seba.session.tools import ToolHandler

MAX_ROUNDS = 20


class RecoveryError(Exception):
    pass


def recover_session(transcript: str, agenda: Agenda, syllabus: Syllabus,
                    sources_dir: Path, send: Send) -> SessionRecord:
    handler = ToolHandler(agenda, syllabus, sources_dir)
    system = recovery_prompt(
        transcript, yaml.safe_dump(agenda.model_dump(), sort_keys=False))
    messages: list[dict] = [
        {"role": "user", "content": "(reconstruct the session via tool calls)"}]
    for _ in range(MAX_ROUNDS):
        message = send(system, messages)
        messages.append({"role": "assistant",
                         "content": _assistant_blocks(message)})
        results = []
        for block in message.content:
            if block.type == "tool_use":
                result, is_error = handler.handle(block.name, dict(block.input))
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": result, "is_error": is_error})
        if results:
            messages.append({"role": "user", "content": results})
        if message.stop_reason != "tool_use" or handler.record.complete:
            return handler.record
    raise RecoveryError(f"recovery did not converge in {MAX_ROUNDS} rounds")
