# Practical Messaging — how this repo works

A two-day training course. **The decks are generated**, not edited: `outlines/*.md` and
`tools/*.py` are the source, `build/*.pptx` is output. An edit made in PowerPoint is lost on
the next build.

**⚑ `Practical Messaging - Day N - 2026.pptx` at the ROOT is a delivery snapshot, not source.**
It is a copy of `build/` taken for a specific delivery, committed so the pack can be picked up
without a build, and it goes **stale the moment an outline changes**. **Never edit either, and
never treat the root `.pptx` as the current deck**: `python3 tools/build_deck.py` is what is
current. Refresh the snapshot by re-copying from `build/` and asking Ian to re-export the PDF.
Previous years' pairs live in `archive/`.

**⚑ The 2026 PDFs are NOT a faithful copy, and the `.pptx` is the artefact that is.** PowerPoint
substitutes for Caveat **when it exports**, though it renders it correctly on screen, so every
callout in both PDFs is in Plex Sans and the near-width ones wrap to two lines. Verified rather
than assumed: **zero occurrences of the string `Caveat`** in either PDF, raw or through every
decompressed stream, against `typeface="Caveat"` **38** and **32** times in the decks. **The test
is one line** — `grep -c Caveat` a PDF, or render a callout page with `pdftoppm` and look at it;
on D1 p23 the figure's baked-in labels are handwriting and the callouts above them are not.
BACKLOG **G19** has the diagnosis and the built-but-uninstalled fix.

**Branch `deck-redevelopment`.** Day 1 is **132 slides**, Day 2 **138**, from 91 + 90 outline
entries, with **118 figures** across thirteen families plus **2 print cards**. **97 go on slides, 9 are
the two handouts'** (8 routing, 1 AsyncAPI), **9 are exercise materials** (4 Paper Flow, 5 RMQ Quick Start),
and **3 are placed nowhere** — `conversation-timeout`, `paper-the-desk` and
`bpmn-compensation-fragment`, all kept in the family. *`tools/` is the arithmetic, not this line.* **Both days' counts move with every
`REVIEW.md` row** — `python3 tools/deck_index.py <day>` is the truth. Day 2's 138 includes **four
`#group:` divider cards**, which are slides and carry a folio. `handouts/` is a third
destination beside the deck and the print cards, and a figure there is held at reading distance, not
read across a room: it is fitted to a **154mm** text block, so its **printed letter size is `154 / w`**
and the canvas width is the only lever on it.

---

## Read order

| read | for |
|---|---|
| **`BACKLOG.md`** | **what is outstanding**, sized. Read it before choosing work. An index — each line points at its detail |
| **`REVIEW.md`** | **closed 2026-09-10, all thirty rows** — Ian's first pass over the built decks. Read it for *why a slide is the way it is*, not for work. `BACKLOG.md` §H is its one-line index. **Ian numbers by SLIDE, not by outline entry** |
| **`REDEVELOPMENT-PLAN.md`** | the **source of truth**: scope, decisions, work queues, the Phase 2 image list (§8), the rationale log (§9), the timing pass (§11), why this visual style (§13). *Two sections are numbered §9; the rationale log is the first* |
| **`styles.md`** | the **authoritative visual spec** — canvas, type, sizes, palette, diagram rules, print. `tools/build_deck.py` implements it; **where the two disagree, `styles.md` wins** |
| `outlines/DayOne.md`, `DayTwo.md` | **the build input.** Content edits happen here, never in the deck |
| `tools/README.md` | how to build a figure: the `Diagram` API, the BPMN elements, per-family notes |
| **the outline grammar** | `tools/outline.py`'s docstring is the implementation. **`#divider:`** opts a `#group:` into a divider slide; **`#reveal: bullets`** gives one click per bullet. Both opt-in per entry, like `#layout:`. **`+ layers` rides on the image LINK, not the entry** — `[→ …/x.png + layers]` stacks `x-l1.png`, `x-l2.png` … over the base at one rect, a click each, because it is a property of the picture rather than of the slide |
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

**⚑ Shared layout is necessary and it is not sufficient.** Until 2026-09-13 the preview drew
**every italic roman and every bold Caveat light** — 1,752 and 100 characters — because
`emit_pptx` set the attribute and `emit_svg` unpacked it and threw it away. The geometry
agreed perfectly the whole time. **An attribute only one back end reads is the shape of this
bug**, and a roman run looks like a run, so nothing downstream can catch it: the whole §G
visual sweep was run blind to italics. When a preview and a deck might disagree, the question
is never *do they share a layout* — it is **which attributes does each one read**.

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
python3 tools/lint_figures.py         # labels off/onto shapes, all THIRTEEN families -- 5+ MINUTES
python3 tools/lint_figures.py reference_cards         # the cards are NOT in the default twelve
python3 tools/reads_at.py             # `at full` AND `room` -- ~2.5 min; --all, --floor N, --no-deck
python3 tools/side_cost.py 2          # what `#layout: side` WOULD cost a slide; --slide N, --all
```

**The thirteen figure families**, each `python3 tools/<name>.py [figure-name | --list]`:
`eip_figures` (26, **8 of them handout-only**) · `coupling_grids` (5) · `if_later` (2) ·
`queues_streams` (11) · `integration_styles` (4) · `app_shapes` (3) · `conversations` (3) — Day 1;
`bpmn_hotel` (13) · `bpmn_shopping` (6) · `paper_flow` (**16** — the montage is now **ten** of them:
a base, eight transparent one-click overlays and an all-arrows static) · `flow_reactive` (23) — Day 2;
`asyncapi_figures` (1, **handout-only**) — the AsyncAPI handout; `rmq_figures` (**5, exercise-only**) —
the RabbitMQ Quick Start, and **the only family on no slide of either deck**.
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
5. **Rebuilds must be byte-identical.** After ANY `diagram.py` edit, rebuild all thirteen families
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
   **⚑ `#layout: side` is the agreed exception** — a half-stage is 6.1in against the 12.4 every
   figure was measured at, and Ian has ruled that fine (`styles.md`).
   **⚑ And `side` is only the LOUDEST way a figure gets less than the full stage.** `#layout:
   figure`, a photograph sharing the panel and a multi-figure entry all narrow it too, and the
   deck's median figure lands at **87%** of the width the floor was set from. So the drawing's
   own number and the room's number are two different things, and **`reads_at.py` now prints
   both** — `at full` is a property of the figure, `room` is what the narrowest slide it is
   actually on gives it. **61 of 89 placed figures are under the floor in the room; 31 of 105
   were under it at full width**, and the second number is the one this file used to quote.
   `--no-deck` still prints it, labelled as the fiction it is.
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
13. **Check whether a convention is *taught* before changing it.** `grep -rn` across `exercises/`
    and `outlines/` first — Paper Flow's notation is line 35 of a printed delegate brief.
    **⚑ And check the evidence too**: this rule used to cite that line as teaching *red dashed = paper
    moving*. It does not. It says **dashed / solid**, with no colour, and `paper-notation-key.png` draws
    the dashed arrow in **carbon** — so the outline's *"Red dashed arrows"* contradicted its own next
    slide until R4-8. A cited convention can be misremembered by the very note warning you to check it.
    **⚑ And `styles.md` was carrying the same wrong example** — its palette table gave *"the red dashed
    arrows: paper moving between trays"* as `annotation`'s home until R4-15. The spec is not immune.
14. **A recorded blocker is a claim, and claims are checked like any other.** Two in one pass.
    *"Recolour = redraw, no `.drawio` renderer here"* (R4-15): wrong — `repaint_paper_reds.py` remaps
    the `.png` and the `.drawio` together and needs no renderer, so a ~5.5-day G1 item was ~20 minutes.
    *"The builder cannot animate inside a figure"* (R4-13): **true, and irrelevant** — a layer is its
    own transparent diagram and the builder stacks layers, which it could always do. **A blocker written
    by the last person to look is evidence, not a verdict** — and rule 4 applies to it too.
15. **Two settled decisions can contradict each other, and neither will say so.** The diagram
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
- **A font installed is not a font PowerPoint can see.** Office reads its font list **at launch**.
  `tools/fonts/*.ttf` went into `~/Library/Fonts/` on 10 Sep and five callouts still wrapped two days
  later, because PowerPoint had been up since 8 Sep. `ps -eo pid,lstart,comm | grep -i powerpoint`
  against the font's mtime settles it in one command — **run it before believing any install**.
  ⚑ And the substitute is a different **face**, not Caveat scaled, so `SUBST_W`'s single factor
  cannot rank which callouts wrap; it matched four of five by luck and made the fifth look like a
  separate bug. **Only a screenshot can see this class of defect** — the preview renderer reads the
  vendored files directly and never substitutes.
- **A `.pptx` is never byte-identical between builds** — it is a zip, and the entry mtimes move
  every time. Rule 5's test is for figures; to prove a builder change touched nothing, `unzip -q`
  both builds and `diff -r` the trees. That is what proved the callout-warning rewrite was
  stderr-only.
- **Ask before publishing anything** — a review sheet is a web page and needs Ian's say-so.
- **One commit per item**, with the reasoning in the message. Update the plan *and* `BACKLOG.md`
  in the same pass as the outline.
- Ian **reads line by line and pushes back by line number**. Count your own options before
  offering them, and prefer being plainly wrong over defensively right.
