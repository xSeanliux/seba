"""Print the prompt that sends one agent to play one eval's tutor turn.

    python3 skills/seba-tutor/evals/prompt.py EVAL_NAME RUN_DIR SKILL_DIR

RUN_DIR/sandbox comes from setup.sh. SKILL_DIR is the skill version under test;
point it at a copy without this evals/ directory, so the agent cannot read the
assertions.
"""

import json
import sys
from pathlib import Path

name, run, skill = sys.argv[1], Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
spec = next(
    e
    for e in json.loads(Path(__file__).with_name("evals.json").read_text())["evals"]
    if e["name"] == name
)
transcript = "\n".join(
    f"{who.upper()}: {text}"
    for turn in spec["transcript"]
    for who, text in turn.items()
)
print(f"""You are being evaluated as the tutor in a Seba tutoring session. Play exactly ONE tutor turn.

1. Read the skill at {skill}/SKILL.md and follow it (read other files beside it only if it tells you to).
2. Sandbox: in this run `seba` is {run}/sandbox/bin/seba. Run every seba command by that full path. It already points at this learner's data; never set SEBA_DATA_DIR, never touch ~/seba-data, never edit files under {run}/sandbox yourself.
3. The conversation so far is below. The skill was loaded at the start of this conversation, but you have no memory of the commands you ran earlier: if you need session state, `seba start prob` resumes the session in progress and prints it.
4. Respond to the learner's latest message as the skill directs: run whatever seba commands you would run at this point (they really execute), then write the exact message you would send to the learner, nothing else, to {run}/outputs/reply.md.
5. Then stop. Do not invent the learner's next reply or play further turns.
6. Finally, in your last message, list the seba commands you ran and one or two sentences on why.

Conversation so far:
{transcript or "(none — this is the learner's first message)"}

LEARNER (latest): {spec["prompt"]}""")
