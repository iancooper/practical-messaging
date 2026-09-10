# Practical Messaging — how this repo works

A two-day training course. **The decks are generated**, not edited: `outlines/*.md` and
`tools/*.py` are the source, `build/*.pptx` is output. An edit made in PowerPoint is lost on
the next build.

**Branch `deck-redevelopment`.** Day 1 is **134 slides**, Day 2 **153**, from 88 + 90 outline
entries, with **101 figures** across twelve families plus **2 print cards**. **92 of the 101 go on
slides; the other 9 are the two handouts'** — 8 routing, 1 AsyncAPI. **Day 1's counts move with every
`REVIEW.md` row** — `python3 tools/deck_index.py 1` is the truth. `handouts/` is a third
destination beside the deck and the print cards, and a figure there is held at reading distance, not
read across a room: it is fitted to a **154mm** text block, so its **printed letter size is `154 / w`**
and the canvas width is the only lever on it.

---

## Read order

| read | for |
|---|---|
| **`BACKLOG.md`** | **what is outstanding**, sized. Read it before choosing work. An index — each line points at its detail |
| **`REVIEW.md`** | **the live queue** — Ian's first pass over the built decks, worked top to bottom. `BACKLOG.md` §H is its one-line index. **Ian numbers by SLIDE, not by outline entry** |
| **`REDEVELOPMENT-PLAN.md`** | the **source of truth**: scope, decisions, work queues, the Phase 2 image list (§8), the rationale log (§9), the timing pass (§11), why this visual style (§13). *Two sections are numbered §9; the rationale log is the first* |
| **`styles.md`** | the **authoritative visual spec** — canvas, type, sizes, palette, diagram rules, print. `tools/build_deck.py` implements it; **where the two disagree, `styles.md` wins** |
| `outlines/DayOne.md`, `DayTwo.md` | **the build input.** Content edits happen here, never in the deck |
| `tools/README.md` | how to build a figure: the `Diagram` API, the BPMN elements, per-family notes |
| `handouts/*.md` | the **takeaway pack** — *Routing Patterns* and *Managing Asynchronous APIs*, both signposted from the deck. Tracked Markdown; **`handouts/build.sh` prints them to A4**, through `print.css` (the house sheet, styles.md at document sizes) and `print.html`. The **PDFs are generated and gitignored**, like `build/` |
| `code-rewrites.md` | the **separate** Day 1 coding-exercise workstream. Read only if that is the job |
| `PROMPT.md` (untracked, if present) | session hand-off — what happened lately, and Ian's open desk |

If any two disagree, **the plan wins**.

---

## The pipeline

```
outlines/DayOne.md ─┐
outlines/DayTwo.md ─┤
                    ├─► tools/outline.py ──► tools/build_deck.py ──► build/*.pptx
resources/*.png ────┤        (grammar)          (styles.md)     └──► build/preview/*.png
resources/*.jpg ────┘                                                 (the only way to LOOK)
      ▲
      └── tools/<family>.py ──► tools/diagram.py ──► .drawio (editable) + .png (what ships)
                                        ▲
                       tools/lint_figures.py · tools/reads_at.py
```

`diagram.py` emits the `.drawio` and the `.png` from **one** definition so they cannot drift.
`build_deck.py` computes layout once into draw-ops and renders it two ways — `.pptx` and PNG
preview — for the same reason: **there is no PowerPoint and no drawio CLI on this machine**, so
a preview that re-derived the layout would be a preview of a different deck.

## Commands

`/verify` · `/build` · `/preview` · `/figure` · `/sheet` — see `.claude/commands/`. The
procedures they load are in `.claude/skills/`: `deck-build`, `figure-drawing`, `review-sheet`.

## The tools

```
python3 tools/diagram.py --check      # renderer + fonts; expect "all good"
python3 tools/outline.py              # parse both outlines; --slide "X" dumps one entry
python3 tools/deck_index.py 1         # SLIDE NUMBER -> section, title, figure; --slide 63 dumps one
python3 tools/build_deck.py           # both decks + the overflow report -> build/
python3 tools/build_deck.py --report  #   measure only, write nothing
python3 tools/build_deck.py --day 1 --preview 14,15   # -> build/preview/ ; also `all`, `over`
python3 tools/lint_figures.py         # labels off/onto shapes, all TWELVE families -- 5+ MINUTES
python3 tools/lint_figures.py reference_cards         # the cards are NOT in the default twelve
python3 tools/reads_at.py             # what a label reads at IN THE ROOM -- ~2 min; --all, --floor N
```

**The twelve figure families**, each `python3 tools/<name>.py [figure-name | --list]`:
`eip_figures` (23, **8 of them handout-only**) · `coupling_grids` (5) · `if_later` (2) ·
`queues_streams` (11) · `integration_styles` (4) · `app_shapes` (3) · `conversations` (3) — Day 1;
`bpmn_hotel` (13) · `bpmn_shopping` (6) · `paper_flow` (7) · `flow_reactive` (23) — Day 2;
`asyncapi_figures` (1, **handout-only**) — the AsyncAPI handout.
Plus `reference_cards` (2, **print**), and two repair tools: `repatch_steps.py`,
`repaint_paper_reds.py`.

## Style in one screen

**Two registers.** Everything is hand-drawn — `sketch=1`, Caveat labels — **except BPMN**,
which is straight-stroked with Plex Sans labels, because the section puts the delegates' own
paper flow beside the same flow in a notation the industry reads, and a wobbly BPMN collapses
that contrast. Both keep the Field Guide palette. There is no third register.

**Palette** (`styles.md`): `ink #181B1F` · `paper #FDFCFA` · `carbon #1D4E6B` ·
`annotation #C0453B` · `manila #F3EFE6` · `rule #E0D9C8` · `muted #8A8578` · `comment #2F5D3A`.

**Four text colours, four questions.** *What is this?* → ink. *Where does it go?* → carbon.
*What is the one thing here?* → annotation. *What do we say about it?* → comment.
**`muted` is for lines, not letters** — 3.6:1 on the paper, the only colour under 4.5:1.

**One idea in red per figure**, stated as a red note at the top — the sentence the presenter
says aloud. Two reds means the figure is doing two jobs. Paired figures contrast *through* red.

**Type.** Titles Plex Serif SemiBold 29pt · body Plex Sans **18pt floor**, sub-items 16 ·
kickers Plex Mono 12 · callouts **Caveat 24pt** · tables 15 · code Plex Mono 15.

---

## Rules that must hold

Each cost real rework at least once. The long-form versions are in the skills.

1. **Look at the PNG.** Every batch has shipped first-draft defects **invisible in the source**
   and invisible to the linter — labels on strokes, an arrow through a box, a route hidden
   behind a cylinder's fill, a border that ran under the shape *outside* it. `lint_figures.py`
   measures overlap; it does not have taste, and it is blind to rules, group borders and
   cylinder rims. A command that reports "lint clean" and stops is this repo's failure mode.
2. **Never put provenance in an outline.** No review codes, no dates, no "merged from".
   **Presenter notes ship as the deck's speaker notes.** Reasoning goes in the commit message
   and the plan.
3. **Never edit `build/`.** It is gitignored and regenerated. Fix the outline or the builder.
4. **Test the assumption before reporting a blocker.** Four wrong reports to Ian, every one the
   same shape: something assumed absent, never checked. A file may exist and still not contain
   what a note says it contains; a marker with a link on it is not proof there is a picture —
   check the extension and open it. **Spend the two minutes proving it.**
5. **Rebuilds must be byte-identical.** After ANY `diagram.py` edit, rebuild all twelve families
   and check `git status`. Every existing figure must come back unchanged; if one moves, the
   change was not additive. Ten seconds, and it has caught real regressions.
6. **Never compare the two registers by point number.** Plex Sans's x-height is 0.516em against
   Caveat's 0.400, so 14pt of Plex reads as 18pt of Caveat — and 18pt of Plex as 23pt of Caveat.
   Use `Diagram._pt()`. Ranking families by `size=` names BPMN worst when it is the one family
   already at the floor.
7. **The 18pt floor is in canvas units, so `w` decides what it means.** A label reads at roughly
   `18 × 890 / w` real points; `w ≈ 890` is where the two floors meet. And **aspect is the other
   half** — a 16:9 slide leaves ~2.2 : 1, so anything squarer is fitted by *height* and the width
   stops mattering. `reads_at.py` is the legibility check; `lint_figures.py` is not.
8. **"Cut" means gone.** Check the content has not reappeared as a note somewhere else.
9. **Anchor outline cuts on `'\n## X\n'`.** Headings recur inside prose in backticks; an
   unanchored cut mangled `DayTwo.md` once.
10. **The outlines are soft-wrapped, so a line is not a block** — bullets, prose, callouts and
    presenter notes all continue on the next line with no marker. And **`#note:` runs to the
    blank line**: `grep '#note:'` reads as clean while the leak is on the lines *after* it.
11. **A clipped label looks like a short label.** Nothing downstream can tell. Any proportional
    width needs a min-content floor, and a layout that squeezes must say so on stderr.
12. **Not every artefact belongs in an outline.** **Handouts live in `handouts/`**, exercise
    materials and facilitator answers in `exercises/`, figures and photographs in `resources/` —
    and all of them are referenced from the **plan**. Wiring a worked answer in as an `#image:`
    puts it in front of the room before the task. A handout gets **one line and a presenter note**
    on the slide that hands it out, and nothing more.
13. **Check whether a convention is *taught* before changing it.** Paper Flow's *red dashed =
    paper moving* is line 35 of a printed delegate brief. `grep -rn` across `exercises/` and
    `outlines/` first.
14. **Two settled decisions can contradict each other, and neither will say so.** The diagram
    panel and the 18pt floor were both agreed with Ian, months apart, and together put every
    figure at 37–53% of the size it was measured at. **When two specs meet, measure the join.**

## Working here

- **Absolute paths.** The Bash tool's working directory persists between calls.
- **`timeout` does not exist on macOS** — wrapping a search in it fails silently and looks
  exactly like "nothing found".
- **No renderer beyond `rsvg-convert`** — no drawio CLI, no `soffice`, no ImageMagick. The
  repo PDFs are stale; the `.pptx` embedded images are the source of truth.
- **`--preview N` is ZERO-based**, and `build/preview/` is not cleared between runs. To preview
  the *n*th slide pass `n - 1`, and `rm -f build/preview/*.png` first.
- **`ls resources/ | grep -i <stem>`, never a guess at the filename.** `resources/` uses two
  naming conventions (`X.drawio.png` and a bare `X.png`), and `session-work/imgs/` is named
  `dayN-sNNN-M`, so **no filename search will ever find a photograph — you have to open them.**
- **A handout is proved by BUILDING it, not by reading it — and then by LOOKING at the PDF.**
  `handouts/build.sh` (no arguments builds both). **Four** defects are invisible in Markdown and
  every one has shipped here: pandoc **drops the leading `N. `** when it makes a heading id, so
  `](#1-discovery)` is a dead link no Markdown reader will show you; a preformatted block wraps past
  **~62 monospace columns**; an arrow glyph inside one **falls out of the monospace face** and
  destroys the alignment, so the diagrams are pure ASCII; and **WeasyPrint does not synthesise an
  oblique**, so before the italic faces were vendored every `*emphasis*` in both handouts rendered
  upright, silently. Reading the Markdown shows you none of the four.
- **Ask before publishing anything** — a review sheet is a web page and needs Ian's say-so.
- **One commit per item**, with the reasoning in the message. Update the plan *and* `BACKLOG.md`
  in the same pass as the outline.
- Ian **reads line by line and pushes back by line number**. Count your own options before
  offering them, and prefer being plainly wrong over defensively right.
