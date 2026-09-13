---
name: deck-build
description: Build the Practical Messaging .pptx decks from outlines/ — the house Markdown grammar, what build_deck.py does with each block, how figures and photographs are laid out, and how to answer an overflow. Use when editing outlines/DayOne.md or DayTwo.md, changing tools/build_deck.py or tools/outline.py, adding or moving a slide, wiring an #image: marker, or reading the overflow report.
---

# Building the decks

`outlines/*.md` → `tools/outline.py` (grammar) → `tools/build_deck.py` (`styles.md`) →
`build/*.pptx` and `build/preview/*.png`.

**`build/` is gitignored and never edited by hand.** An edit made in PowerPoint is lost on the
next build. If a slide is wrong, the fix is in the outline or in the builder.

**`styles.md` is the spec and `build_deck.py` is its implementation.** Where the two disagree,
`styles.md` wins; where the builder decides something `styles.md` does not, the reason is in a
comment and the decision belongs back in `styles.md` once Ian has seen it.

## The grammar

A house dialect of Markdown, **not CommonMark**. `tools/outline.py` owns it and nothing else
parses it — parsing it in three places is how the three drift apart.

```
# Title                                  the deck title, once
## Section                               a teaching section
#group: <title>                          a run of slides in a sub-topic — NOT an entry, not counted
### Slide: <name>                        an entry. `###` is reserved for slides and nothing else
*blurb*                                  italic line under a `##`, the section's own summary
- bullet                                 body; nested by two-space indent
1. numbered                              body, an ordered list
| a | b |                                a table
▎ text                                   a CALLOUT — the line the presenter says aloud
#image: <alt>  [→ resources/x.png]       a figure, resolved or still pending
#layout: side                            text left, drawing right — opt-in, per entry
#note: <text>                            a build note. NEVER reaches the deck
Presenter notes: <text>                  speaker notes, and they DO ship
```lang … ```                            a code listing
> quote                                  a block quotation
```

Count entries with `len(re.findall(r'\n### ', s))`, or split on `'\n## '` per section.

### Four things about the grammar that have each cost rework

1. **⚑ Soft wrapping means a line is not a block.** The outlines are written to a ~110-column
   measure, so a bullet, a paragraph, a callout and a presenter note all routinely continue on
   the next line **with no marker**. Every block accumulates continuations until a line that
   *starts* a new one. A parser that takes each line as its own block yields four-word bullets
   and loses half the prose.
2. **⚑ `#note:` runs to the blank line, not to the end of its own line.** Skipping only the
   marker line shipped build instructions onto three slides at 18pt. `grep '#note:'` finds the
   marker and reads as clean — **the leak is on the lines after it.**
3. **`#note:` is stripped and `Presenter notes:` is kept.** That asymmetry is the whole of rule
   2 in `CLAUDE.md`: presenter notes become the deck's speaker notes, so **never put provenance
   in an outline** — no review codes, no dates, no "merged from three slides". Reasoning goes in
   the commit message and the plan.
4. **Anchor a cut on `'\n## X\n'`.** Section headings recur inside prose in backticks
   (`` `## Versioning` ``), so `str.index('## Versioning')` matches the intro, not the section.
   An unanchored cut silently mangled `DayTwo.md` once and needed `git restore`.

## What the builder does

**Layout is computed once into draw-ops and two back ends consume it** — `_Pptx` and `_Svg`.
That is the same move `diagram.py` makes, for the same reason: **there is no PowerPoint here**,
so rendering is the only way to see a slide, and a preview that re-derived the layout would be a
preview of a different deck.

**Four arrangements. What decides between the first three is whether the picture carries type; the
fourth is an override you write in the outline.**

| the slide has | layout |
|---|---|
| a **drawing** (`.png`) | **the figure leads** — title, callout, then the figure at full content width |
| **photographs** (`.jpg`) | text left, photographs in a fixed manila panel right, 1.15 : 0.85 |
| no picture | full width, same left margin and kicker |
| `#layout: side` | **text left, the drawing right**, 0.47 : 0.53 — and the entry does **not** split |

**⚑ `#layout: side` costs the drawing most of what the figure-leads rule protects**, so it is opt-in and
the builder **reports what each one costs by name every run**. The six §4.4 slides Ian asked for land at
49–71% of their Phase 2 label size, against 85–101% as full-width figure slides. Reach for it when the
words and the picture are one thought — Ian: *"It's too weird to read the words, then show the diagram
here"* — not to save a slide. **Report the numbers back rather than absorbing them.**

**A photograph tolerates being small; a labelled drawing does not** — and the file extension
carries the distinction. Every photograph in `resources/` is a `.jpg`, every drawing a `.png`.

**An entry may become two slides**: the argument, then the picture. **The callout goes with the
picture** — it is the line the presenter says aloud about what is on screen — and both slides
keep the same title, so the pair reads as one thought with the picture revealed. **79 entries
split this way, which is why 181 entries build 291 slides.**

**⚑ A callout above a figure costs about 13 points of that figure.** It is laid out above the
picture and the picture gets what is left, so promoting a line to a callout on a figure slide is
paid for out of the drawing: `eip-invalid-message-channel` went 101% → 88% for one. Worth it when
the line is the thing the presenter says; check the report afterwards either way.

**A split needs its presenter note split too**, along the same seam, or the second half's
guidance lands on the first half's slide. And **re-check every "next slide" the entry contains**:
one split put a slide between a bullet and the worked example it pointed at.

**One labelled figure per slide.** Two sharing a stage each take about half its linear size,
which is the tax the diagram panel used to charge. Where a reader genuinely has to compare, the
answer is a **composed figure** — see the `figure-drawing` skill, which has the two-part test and
the one composition Ian reversed.

## Three things the `.pptx` does that the preview cannot show you

1. **A paragraph is one text box, and it wraps.** Not one box per wrapped line — that is what four
   callouts were running off the slide through, invisibly, because `word_wrap` was off and the box was
   the width of the whole slide. The preview drew them correctly the whole time. **A wrapping defect in
   the built deck will not appear in a preview**; check the XML (`x + cx` against 13.33in) or open it.
2. **Every slide builds by idea.** The grouping is inferred — a lead-in plus its bullets, then each
   table / code block / quotation / callout, then the picture. `--no-animation` turns it off.
   **⚑ There is no PowerPoint here and a malformed `p:timing` refuses to open rather than degrading**,
   so `emit_pptx` asserts every `spid` against a shape it actually wrote. If you touch `_timing`,
   re-run the four checks: dangling spids, duplicate `cTn` ids, `p:timing` last in `p:sld`, and a
   python-pptx reopen.
3. **`_first_baseline()` is a model of PowerPoint, not a measurement of one.** With a paragraph in a box
   PowerPoint places the first baseline, not us. If a built deck opens with every paragraph a few points
   low or high, that function is the one place to correct it and the error is the same fraction of an em
   everywhere.

## Finding a slide by its number

**Ian reviews by slide number and pushes back by slide number**, and the slide number is not the outline
entry number — 88 Day 1 entries build 136 slides, and the offset differs at every point in the deck.

```bash
python3 tools/deck_index.py 1              # the whole day
python3 tools/deck_index.py 1 --slide 63   # one slide, with its blocks and notes
python3 tools/deck_index.py 2 --slide 56-59
```

It runs the real layout, so it cannot drift from the deck. Counting `###` gives an answer that is wrong
by about a third.

## The overflow report is a deliverable, not a diagnostic

`styles.md`: *"Expect the floor to force content off crowded slides. That is intended — it will
find the slides doing too much, and it is a content decision as much as a design one."*

So the builder **never shrinks type to make content fit.** It lays the slide out at the floor,
measures what did not fit, and prints it. **The list that comes out is a content queue for Ian.**

**It is empty today.** A new overflow means an outline edit pushed a slide over.

Five ways the seven known overflows were answered, in the order to reach for them:

1. **Look for a seam before looking for something to lose.** Five of the seven were splits, and
   Ian took the option that moved no content every time. On one slide the seam was a sentence
   already written into it: *"You have met two of these already, under other names."*
2. **A block's measured height is not the cost of the sentence inside it.** One ruling costed a
   cut at 1.05in — the height of the whole opening *paragraph*, where the thing being cut was its
   first *sentence*. Moving the names alone recovered 0.62 of 1.02 and the slide stayed over.
   **When a ruling prices a cut, check whether the thing being cut is the whole block** — and
   when the arithmetic misses, that is a second decision to put to Ian, not a licence to find the
   difference yourself.
3. **⚑ A table row's height is its TALLEST cell.** Shortening the other one buys nothing at all — four
   attempts at one 0.07in overflow did exactly zero before that was measured. Find which cell sets the
   row before rewriting anything.
4. **⚑ An overflowing slide is not merely over-long — it is *unreviewed*.** Fixing the overflow
   is what puts it in front of a reader for the first time. The first preview of a newly-fitting
   table showed `Out-Only` rendering as **"Out-"** and both `In-Only` and `In-Out` as **"In-O"**,
   on the one slide whose entire argument is per-pattern. Sweeping the other thirteen tables
   found four more clipped row labels. **Preview anything you have just fitted.**
5. **A clipped label looks like a short label**, and nothing downstream can tell. Every column
   now has a min-content floor (its longest unbreakable word) and only the slack above the floors
   is shared out; the remaining failure mode writes to stderr rather than clipping quietly.
   `_kicker` got the same fix — a `#group:` title is drawn full-bleed with no wrap, so a long one
   ran **under the figure panel**, invisible until the first slide to put a picture beside it.
6. **Cutting is last, and "cut" means gone.** The Fallacies were cut from §1 and then parked as a
   `#note:` elsewhere; Ian caught it. Check the content has not reappeared anywhere in the deck.

## Standing advisories that are not failures

The builder prints three things every run. Report them only if a count moved.

- **Photo-panel slides** (2 on Day 2) — working as designed.
- **The 15 multi-figure entries** — Ian ruled on these, plan §8 item 23e. Thirteen he ruled on
  plus two that carry three figures each.
- **Figures under 85% of their Phase 2 label size** — 2 on Day 1, 3 on Day 2, `BACKLOG.md` B2.
  **`boundary-what-crosses` was the one worth doing and is done** (82% → 96%, 2026-09-09). The
  rest have **no action available** while both the canvas and the stage are height-fitted, because
  the aspect cancels out — two of them are 2021 `.drawio` exports rather than figures of ours.

## Editing an outline

- **Read the affected section *and* what it cross-references** before proposing anything.
- **Update all four plan surfaces in the same pass**: the §4 / §5 work-queue tables, the §3
  counts, and the §8 image budget. Plus `BACKLOG.md` if an item closes.
- **Re-run the cross-reference sweep after any structural change**, not once at the end. **It finds
  references that were wrong before you arrived** — three of the four on the last run were, including one
  that G4 had broken a month earlier and one that a *new figure* invalidated (*"the drawn form of the
  slide before it"* stopped being true when the slide before it got a drawing).
  "Discussed next" / "the next slide" notes break on any reorder — and **a note can survive a
  reorder and still mislead**: check what got *inserted* between a note and its payoff, not only
  what got renamed.
- **Not every artefact belongs in an outline.** Handouts, exercise materials and facilitator
  reference answers are built into `resources/` and referenced from the **plan**. Wiring a worked
  answer in as an `#image:` would put it in front of the room before the task.
- **A marker with a link on it is not proof there is a picture.** One pointed at its
  `.excalidraw` **source** for months and every count in the repo read it as linked. Check the
  extension and check the file opens. Five markers name **two** paths — the render *and* its
  editable source — and the parser takes the first.
- **`ls resources/ | grep -i <stem>`, never a guess at the filename.** `resources/` uses both
  `X.drawio.png` and a bare `X.png`.
- **Nothing in `exercises/` or `videos/` is this workstream's to change.** But `outlines/DayOne.md`
  names those decks and videos by title, so a rename over there comes back here as a request.

## The three sweeps — run 2026-09-09, and what they taught

`BACKLOG.md` B4, B5 and B6 are closed; plan §8 item 24 has the detail. **B6 is not a one-off** —
re-run it after every structural change.

- **The load-bearing line hiding in the presenter notes.** Caught six times, twice by Ian, before
  Day 1 §4 was swept; four more came out of that sweep. **But two candidates were false positives
  the figures were already answering** — *Messaging Gateway* draws the endpoint/gateway split and
  reds it, and *Datatype Channel*'s carrying sentence is its own foot comment. **A line is not
  buried if the picture is saying it**, and neither `grep` nor the outline can see that: both were
  written, previewed and reverted. **Render the slide before promoting anything onto it.**
- **Image-dump slides.** Day 2's 17-image entry was found and split. Day 1 was checked and is a
  clean negative: **49 images across 91 entries and no entry with more than one.**
- **Stale cross-references — re-run after every structural change, not once at the end.** Four
  were wrong on the last pass, two of them left over from a change three sessions earlier. All of
  them now **name the slide** instead of counting from it, which is the only form that survives a
  reorder. **A positional reference is a bug with a delay on it.**
