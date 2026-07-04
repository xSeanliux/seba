import os
import re
import subprocess
from pathlib import Path
from typing import Callable

from seba.models import Syllabus
from seba.syllabus.graph import SyllabusError, load_syllabus

_PROMPT = Path(__file__).parent / "prompts" / "synthesis.md"


def draft_syllabus(goal: str, subject: str, toc: str,
                   complete: Callable[[str], str]) -> str:
    prompt = _PROMPT.read_text().format(goal=goal, subject=subject, toc=toc)
    out = complete(prompt)
    fenced = re.search(r"```(?:yaml)?\n(.*?)```", out, re.DOTALL)
    return fenced.group(1) if fenced else out


def default_editor(path: Path) -> None:
    subprocess.run([os.environ.get("EDITOR", "nano"), str(path)], check=True)


def edit_until_valid(yaml_text: str, path: Path,
                     editor: Callable[[Path], None]) -> Syllabus:
    path.write_text(yaml_text)
    last_error: SyllabusError | None = None
    for _ in range(3):
        editor(path)
        try:
            return load_syllabus(path)
        except SyllabusError as e:
            last_error = e
            body = "\n".join(l for l in path.read_text().splitlines()
                             if not l.startswith("# ERRORS") and not l.startswith("#   "))
            path.write_text(f"# ERRORS: fix and save again\n#   {e}\n{body}")
    raise last_error
