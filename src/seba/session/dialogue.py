import json
from pathlib import Path
from typing import Callable, Protocol

from seba.models import Agenda, SessionRecord, Syllabus
from seba.session.loader import system_prompt
from seba.session.tools import ToolHandler, anthropic_tools


class SessionIO(Protocol):
    def get_input(self) -> str | None: ...
    def show_chunk(self, text: str) -> None: ...
    def show(self, text: str) -> None: ...


Send = Callable[[str, list[dict]], object]


def make_send(client, model: str) -> Send:
    tools = anthropic_tools()

    def send(system: str, messages: list[dict]):
        return client.messages.create(model=model, max_tokens=2000,
                                      system=system, messages=messages,
                                      tools=tools)
    return send


def _assistant_blocks(message) -> list[dict]:
    out = []
    for b in message.content:
        if b.type == "text":
            out.append({"type": "text", "text": b.text})
        elif b.type == "tool_use":
            out.append({"type": "tool_use", "id": b.id, "name": b.name,
                        "input": b.input})
    return out


def run_session(agenda: Agenda, syllabus: Syllabus, overlay: str,
                sources_dir: Path, io: SessionIO, send: Send
                ) -> tuple[SessionRecord, str]:
    handler = ToolHandler(agenda, syllabus, sources_dir)
    system = system_prompt(agenda, overlay)
    messages: list[dict] = [
        {"role": "user", "content": "(session start — greet and begin)"}]
    transcript: list[str] = []

    while True:
        message = send(system, messages)
        messages.append({"role": "assistant",
                         "content": _assistant_blocks(message)})
        results = []
        for block in message.content:
            if block.type == "text":
                io.show_chunk(block.text)
                transcript.append(f"TUTOR: {block.text}")
            elif block.type == "tool_use":
                result, is_error = handler.handle(block.name, dict(block.input))
                transcript.append(
                    f"[tool] {block.name}({json.dumps(dict(block.input))})"
                    f" -> {result}")
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": result, "is_error": is_error})
        if results:
            messages.append({"role": "user", "content": results})
        if message.stop_reason == "tool_use":
            continue
        if handler.record.complete:
            return handler.record, "\n".join(transcript)

        user = io.get_input()
        if user is None:
            return handler.record, "\n".join(transcript)
        if user.strip() == "/done":
            missing = handler.missing_grades()
            if not missing and handler.record.complete:
                return handler.record, "\n".join(transcript)
            user = ("(user is done; ungraded reviews: "
                    + (", ".join(missing) or "none")
                    + "; grade or skip each, then call end_session)")
        transcript.append(f"LEARNER: {user}")
        messages.append({"role": "user", "content": user})
