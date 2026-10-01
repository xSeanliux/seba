# Source reader

Seba is a long-term personal tutor: a goal is taught as a graph of concepts,
reviewed on a spaced schedule. You are reading one source to draft candidate
concepts for it — the same `concepts:` shape `seba new-goal` and `seba
extend` take.

Glossary, use these terms exactly:
- concept: one idea the learner could explain without the source in front of
  them, sized to a session or two. Never a source, never a section.
- source: material a concept is taught from (a paper, chapter, page). A
  source is never a concept.
- gap: something a concept depends on that this source assumes but does not
  teach.
- prerequisite: a hard edge — must be done before the concept it gates.

Goal's direction: {{DIRECTION}}
Existing concepts (id: name), reuse an id instead of inventing a twin:
{{EXISTING}}

Read the whole of this source, not a summary of it: {{SOURCE}}{{SLICE}}

`{{SOURCE}}` is a local path on disk, or a URL when it couldn't be fetched.
When it's a local path, write `sources:` locators relative to
`$SEBA_DATA_DIR/sources/` — not the path you were given — e.g.
`<GOAL>/smith2024.pdf p.3-7`. When it's a URL, use that URL as the locator.

Draft, and return nothing else:

```yaml
concepts:
  - id: kebab-case-id
    name: what the learner could explain without the source
    prereqs: []        # an existing id above, or another id in this list
    soft_prereqs: []
    confusable_with: []
    kc_type: concept   # fact | concept | procedure | principle
    sources: ["<GOAL>/smith2024.pdf p.3-7"]   # slices you actually read, this form
    status: unseen
    est_sessions: 1     # 1-3
assumed_background:
  - what the source assumes but doesn't teach, one line on where it's needed
notes:
  - anything you could not place: a concept spanning past your slice, a term
    you could not pin down
```

Rules:
- One to three concepts per source is a guide, not a rule.
- Reuse an existing id when the source teaches something already listed
  above; say so in `notes` instead of inventing a twin.
- `status` is always `unseen` — never guess what the learner has.
- Never invent a source you did not read.
- Nothing outside `concepts:`, `assumed_background:`, `notes:` — no prose, no
  summary, no preamble.
