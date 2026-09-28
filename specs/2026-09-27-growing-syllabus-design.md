# Changing a syllabus after it starts — design

Status: **design confirmed.** Settled over five rounds of design review. No code written yet. Terms are defined in `CONTEXT.md`.

## Where this started, and where it landed

The request came from a learner using Seba as a research companion: a curriculum
of papers, not known in advance, related by the direction of the research.

Review settled that a paper is a **source**, not a concept, and that sources and
concepts map many to many. The model already allows that: a concept carries a
list of sources. What the model does not allow is *change*. A syllabus is written
once and nothing can add to it, remove from it, or steer it.

That is a limit for every learner. Someone studying probability hits it when a
missing prerequisite turns up in session four, when they decide to skip a
chapter, or when they want chapter five today. So this change is scoped to what
any goal can use, and contains nothing specific to research.

## Design

### 1. Mapping: adding concepts

```
seba extend GOAL --from-file PATH
```

The file holds concepts in the existing schema. They are appended and the merged
syllabus goes through the existing validation: duplicate ids, unknown
references, cycles. New concepts may point at existing ones. An id that already
exists is refused. A failed validation writes nothing.

Works between sessions and during one. The agenda of a session in progress is
unchanged.

Adding a source to a concept that already exists:

```
seba concept GOAL ID --add-source LOCATOR
```

Mapping is a conversation. The tutor skims the source's abstract and headings,
drafts the concepts, names which existing concepts the source reuses, and
revises with the learner. Nothing is saved without an explicit yes. Drafting
defaults:

- One to three concepts per source, each named by what the learner could explain
  without the source in front of them.
- Background a source assumes becomes its own concept and a hard prerequisite.
  This is how a **gap** gets closed.
- Sized to a session or two. Never carved by section.

### 2. Dropping and restoring

```
seba concept GOAL ID --status dropped
seba concept GOAL ID --status restored
```

A dropped concept leaves the frontier and the teaching slot, and its cards stop
being reviewed. Its history, notes and cards are kept. Restoring returns it to
the status it had.

A concept that others depend on cannot be dropped while they are live; the
refusal names them. Drop the dependents first, or remove the edge by hand.

### 3. Steering

```
seba start GOAL --concept ID
```

Overrides the automatic pick for this session. The concept must be in progress
or on the frontier. Unmet hard prerequisites are a refusal that names them,
because those edges are the curriculum. Refused when a session is already
pending.

### 4. Direction

The briefing opens with the goal's direction, which today never reaches the
tutor. `seba tune GOAL --direction TEXT` changes it.

When the direction changes, the tutor walks the unseen concepts with the learner
and proposes drops one at a time.

When at most one concept is left unseen, the briefing says so and tells the
tutor to propose what comes next or confirm the goal is finished.

### 5. Wording

Progress reads `7 done, 2 open, 1 dropped` rather than `7/9`.

## Left out, and why

| Idea | Why |
|---|---|
| Sources tracked in their own right (title, read state) | Specific to reading goals. A source enters through the concepts mapped from it |
| Reading list in the view | Same. Derivable later from each concept's sources without new storage |
| Steering by source | Same. Steering by concept covers it |
| Recording open research questions | Out of scope: the tool is about what the learner knows |
| Ranking ready concepts | The learner picks |
| Editing prerequisite edges by command | Rare. The syllabus file can be edited by hand and is validated on load |

## Files touched

| File | Change |
|---|---|
| `models.py` | `Status.DROPPED`; status to restore to |
| `syllabus/graph.py` | `extend`; dropped excluded from frontier; drop and restore moves |
| `store/store.py` | write syllabus on extend; direction |
| `scheduler/agenda.py` | teach override; direction and exhaustion lines; dropped cards excluded; wording |
| `session/tools.py` | `dropped`, `restored`, `--add-source` |
| `cli.py` | `extend`; `start --concept`; `tune --direction` |
| `ui/view.py`, `view_template.html` | dropped shown; wording |
| `skills/seba-tutor/SKILL.md` | command table; "Changing a syllabus" |

## Testing

- Extending with a concept whose prerequisite already exists succeeds, and it
  reaches the frontier once that prerequisite is done.
- Extending with a duplicate id, an unknown reference, or a cycle through an
  existing concept is refused and leaves the syllabus file byte-identical.
- Extending during a pending session lets a card be minted on the new concept.
- A dropped concept is absent from the frontier and the agenda, and its due
  cards are not reviewed. Restoring brings back its status and its cards.
- Dropping a concept with a live dependent is refused and names the dependent.
- `start --concept` picks the named concept over an earlier frontier entry; it is
  refused on unmet prerequisites, on a dropped concept, and with a session pending.
- The briefing carries the direction, and the exhaustion line at one unseen
  concept but not at two.

## Depends on

The settings block and `seba tune` from the scheduling change. This one lands
second.
