You are designing a long-term study syllabus. Goal: "{goal}". Subject
preset: {subject}.

Below is the table of contents of the primary source. Produce a concept
graph as YAML: top-level keys `goal`, `subject`, `concepts`; each concept
has `id` (kebab-case), `name`, `prereqs` (list of ids), `sources` (list of
"<source-dir>/<file>#<section>" refs into the ToC where applicable),
`status: unseen`, `est_sessions` (1-3).

Rules: concepts sized to 1-3 sessions each; prereq edges may REORDER or
cut across the book's chapter order; INSERT prerequisite concepts the book
assumes but does not teach; the book guides, it does not dictate. Output
ONLY the YAML.

# Table of contents
{toc}
