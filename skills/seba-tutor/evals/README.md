# seba-tutor evals

Each eval plays **one tutor turn** against real learner state. Every run gets
its own sandbox, so nothing touches `~/seba-data`.

| File | Role |
|---|---|
| `evals.json` | the evals: scenario, conversation so far, the learner's latest message, assertions |
| `setup.sh SCENARIO DEST` | builds `DEST/data` (a `SEBA_DATA_DIR` in the scenario's state) and `DEST/bin/seba`, which runs this checkout's CLI on that dir and logs each call to `DEST/seba.log` |
| `prompt.py EVAL RUN_DIR SKILL_DIR` | prints the task for the agent playing the tutor |
| `check.py EVAL RUN_DIR` | grades the eval's `[check]` assertions from the run's log, its learner state and `outputs/reply.md`; prints JSON |

Assertions marked `[check]` are mechanical. The rest need a reader.

## One run

```bash
run=/tmp/seba-eval/wrong-review   # any scratch dir
skills/seba-tutor/evals/setup.sh review-pending "$run/sandbox"
mkdir -p "$run/outputs" /tmp/seba-eval/skill
cp skills/seba-tutor/SKILL.md /tmp/seba-eval/skill/   # a copy without evals/, so the agent can't read the assertions
python3 skills/seba-tutor/evals/prompt.py wrong-review-graded-again "$run" /tmp/seba-eval/skill > "$run/task.md"
# Have a fresh agent read and do task.md, e.g. a Claude Code subagent:
#   "Read $run/task.md and carry out exactly what it says."
uv run python skills/seba-tutor/evals/check.py wrong-review-graded-again "$run"
```

To compare two skill versions, run each eval once per version and compare the
results. The skill-creator plugin's `eval-viewer` can show the replies side by
side.
