# Growing syllabus — design

Status: **draft, awaiting review.** No code written yet.

## What the learner asked for

One learner uses Seba for academic research and builds a curriculum of papers.
The list is not known beforehand. The papers are related by an implicit
curriculum that the research subject determines.

Success looks like: a goal can start with three papers and have thirty a few
months later; each new paper lands in the right place in the graph; background
the papers assume gets taught before the paper that needs it; and the learner
can say "this one today" without fighting the scheduler.

## What blocks this today

- The syllabus is written once, by `seba new-goal`. Nothing adds a concept
  afterwards.
- The concept to teach is the first `in-progress` one, else the first on the
  frontier *in file order*. A paper appended last is taught last.
- `Syllabus.goal`, the one-line statement of what the learner is after, never
  reaches the tutor. The briefing carries the goal's short name only.
- "Concepts done: 7/9" reads as progress toward an end that a growing syllabus
  does not have.

Everything else already fits. A paper is a concept with a URL in `sources`,
prerequisite edges express "read this first", and the tutor already fetches a
bounded slice of a source at teach time.

## Design

### A. `seba extend`

```
seba extend GOAL --from-file PATH
```

The file holds a list of concepts in the existing schema. They are appended and
the **merged** syllabus goes through the existing `validate()`: duplicate ids,
unknown references, cycles. New concepts may name existing ones in `prereqs`,
`soft_prereqs` and `confusable_with`. An id that already exists is refused; this
command adds, it does not edit. A failed validation writes nothing.

Works between sessions and during one. `ToolHandler` reloads the syllabus on
every call, so a card can be minted against a concept added minutes earlier. The
agenda of the session in progress is unchanged.

### B. Choose what to teach

```
seba start GOAL --concept ID
```

Overrides the automatic pick for this session. The concept must be `in-progress`
or on the frontier. If it has unmet hard prerequisites the command refuses and
names them, because the edges are the curriculum. With a session already pending
the flag is refused rather than silently ignored.

Without the flag the pick is unchanged.

### C. Give the tutor the direction

The briefing opens with `Goal: <Syllabus.goal>`. For a research goal this line
is the research question, and it is what the tutor steers by when proposing what
to read next.

When at most one concept is left unseen, the briefing adds:

```
syllabus nearly exhausted (1 unseen) — before closing, propose what comes next
and add it with `seba extend`, or confirm the goal is finished.
```

No `open_ended` flag. A fixed goal that runs out is finished, a growing one gets
extended, and the learner knows which they have.

### D. Tutor protocol

A new `SKILL.md` section, "Growing a syllabus":

- **When.** At the close, after the negotiation turn. Also whenever the learner
  brings a paper, or the briefing says the syllabus is nearly exhausted.
- **Where candidates come from.** The references of the paper just read; gaps
  the session exposed; the goal line. The learner's own finds come first.
- **How many.** One to three. The list grows at the pace it is read.
- **Shape.** One paper is one concept, sized 1–3 sessions. A paper that needs
  more is split along its contributions (method, main result), not its sections.
  `sources` is the paper's URL plus the section, never the whole PDF.
- **Edges are the implicit curriculum.** `prereqs` for a paper that cannot be
  read without another; `soft_prereqs` for "helps". If a paper assumes background
  the learner lacks, add that background as its own concept and make it a hard
  prerequisite.
- **Gate.** Show the proposed concepts and edges and get an explicit yes before
  `seba extend`, as with a new goal.

### E. Progress wording

The briefing and the view say `7 done, 2 open` rather than `7/9`.

## Deliberately left out

- **Dropping a concept.** Research plans go stale, and a paper that stopped
  mattering will sit on the frontier. `--concept` makes that survivable. A
  `dropped` status touches the frontier, the view and the status state machine,
  so it waits until the stale entries are a real nuisance. See open question 2.
- **Editing edges after the fact.** Same reason.
- **Automatic paper discovery or ranking.** The tutor proposes in conversation
  with the tools it has. Seba stores what was agreed.
- **Citation-graph import.** The edges that matter are the ones this learner
  needs, which a citation graph does not know.

## Files touched

| File | Change |
|---|---|
| `syllabus/graph.py` | `extend(syllabus, concepts)` — append, then `validate` |
| `store/store.py` | `extend_goal` — write `syllabus.yaml`, commit |
| `scheduler/agenda.py` | `teach` override; goal line; exhaustion line; wording |
| `cli.py` | `extend`; `start --concept` |
| `ui/view.py`, `view_template.html` | progress wording |
| `skills/seba-tutor/SKILL.md` | command table; "Growing a syllabus" |

## Testing

- Extending with a concept whose prerequisite already exists succeeds, and the
  concept appears on the frontier once that prerequisite is done.
- Extending with a duplicate id, an unknown reference, or a cycle through an
  existing concept is refused and leaves `syllabus.yaml` byte-identical.
- `start --concept` picks the named concept over an earlier frontier entry.
- `start --concept` on a concept with unmet hard prerequisites is refused and
  names them.
- `start --concept` with a session pending is refused.
- The briefing carries the goal line, and the exhaustion line at one unseen
  concept but not at two.
- Extending during a pending session lets `mint` accept the new concept.

## Open questions

1. **Who finds the papers?** The design assumes both: the learner brings some,
   the tutor proposes others, the learner approves all. If this learner only
   ever brings their own, section D shrinks to "place it in the graph".
2. **Dropping.** Is a stale frontier already a problem for them?
3. **Paper as the unit.** One paper per concept is the default here. The
   alternative makes ideas the concepts and papers their sources, which suits a
   survey-style goal better but needs the ideas known up front, and that is the
   thing this learner does not have.
