---
description: Rebuild one figure, lint it, measure what it reads at — and show the picture
argument-hint: <figure-name>
allowed-tools: Bash, Read, Edit, Write
---

Rebuild the figure named in `$ARGUMENTS`, check it, **and look at it**.

Load the **`figure-drawing`** skill first — it carries the `Diagram` API, the legibility
arithmetic, and what `compact` / `reads_at` / `lint_figures` each measure and each miss.

### 1 · Find its family

```bash
cd /Users/ian.cooper/Documents/practical-messaging
grep -ln "$ARGUMENTS" tools/*.py        # find the @figure("<name>") registration
```

The eleven families are `eip_figures` · `coupling_grids` · `if_later` · `queues_streams` ·
`integration_styles` · `app_shapes` · `conversations` · `bpmn_hotel` · `bpmn_shopping` ·
`paper_flow` · `flow_reactive`, plus `reference_cards` (**print**, and outside the default
eleven everywhere). Each takes `--list`.

### 2 · Rebuild, lint, measure

```bash
python3 tools/<family>.py <figure-name>
python3 tools/lint_figures.py <family>          # one family is fast; ALL ELEVEN is 5+ minutes
python3 tools/reads_at.py <family>              # or --all for every figure's asp / fit / reads
```

`reads_at` is the legibility check and `lint_figures` is not: lint measures a label against the
**shape** it sits in, `reads_at` measures it against the **room**.

### 3 · ⚑ Look at the PNG — this is the point of the command

```
Read resources/<figure-name>.png
```

**Do not stop at "lint clean".** That is this repo's standing failure mode. Every batch has
shipped first-draft defects invisible in the source *and* invisible to the linter, because lint
is blind to three whole classes: a label across a **rule** (gridline, axis, boundary), a note
across a **group's border**, and a label across a **cylinder's rim**. Each of the three has
produced a defect nobody caught by machine.

Say what you see: does the red mark **one** idea? Does every label clear every stroke? Is the
reading direction left to right? Does the foot comment clear the lowest shape *after*
compaction?

### 4 · If you changed `diagram.py` rather than the figure

**Rebuild all eleven families and show `git status`.** Every other figure must come back
**byte-identical**; if one moves, the change was not additive. Ten seconds, and it has caught
real regressions.

```bash
for f in eip_figures coupling_grids if_later queues_streams integration_styles \
         app_shapes conversations bpmn_hotel bpmn_shopping paper_flow flow_reactive; do
  python3 tools/$f.py > /dev/null; done
git status --short resources/
```

### 5 · If the figure appears in a deck

`python3 tools/build_deck.py` and, where the slide's layout is in question, `/preview` it.
