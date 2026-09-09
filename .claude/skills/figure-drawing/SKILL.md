---
name: figure-drawing
description: Draw or edit a Practical Messaging figure with tools/diagram.py — the element vocabulary, the legibility arithmetic (compact, reads_at, the 18pt floor, aspect), what lint_figures.py cannot see, the composition test, and the defects that have shipped invisible in the source. Use when adding or changing any figure in the eleven families or the reference cards, editing tools/diagram.py, or acting on a reads_at / lint finding.
---

# Drawing a figure

`tools/diagram.py` emits **both** the editable `.drawio` and the `.png` from one definition, so
they cannot drift. `tools/README.md` has the full API and a per-family note; this is the
judgement that goes with it.

**Read `tools/README.md` for the API before writing code.** Read this for what the API will not
tell you.

## ⚑ Rule zero: look at the PNG

**Every batch has shipped first-draft defects invisible in the source and invisible to the
linter.** Not most batches — every one. A partial list, all of them found by eye:

a missing arrow (a publisher never joined to its own channel) · a label clipped off-canvas ·
every BPMN lane label stacked on its neighbour · a gateway with one outgoing path, which is not a
gateway · `→` rendered as a hollow `.notdef` box because **Caveat has no arrows and no maths** ·
arrows drawn straight through boxes · two consumer boxes overlapping · a leader line that crossed
the shape it pointed at, and struck the port's own label when re-aimed · a full-size cross
striking through its component's name, twice · a whole figure laid out right-to-left, so its feed
arrow ran backwards through a label · a pipe's mouth ellipse on a group boundary, swallowing the
port label beside it · a structural rule down the middle of a canvas striking every label centred
on it · a mirrored pair of arrows whose labels landed on different legs, because `_mid()` takes
the middle *segment* · three foot comments grown off their canvases when the floor was raised ·
a name drawn on top of its own arrow's label · a failed component's name lying on a fault
region's dashed border, then on the border's *other* side when moved · a refused-read routed
**behind** a cylinder and hidden by the cylinder's own fill · a dashed red arrow parallel to a
dashed red border two units away, so two refusals read as one shape · and a group border that
cleared the shape inside it but ran 2 units under the one **outside** it, in the same colour, so
the drawing said the opposite of what it meant.

**`diagram.py` warns at build time on a missing glyph.** That one is caught for you. Nothing else
is. On the reference cards, a measuring probe caught two defects and *looking* caught six.

**Render a new glyph magnified before trusting it in place** — `save(scale=10)` on a scratch
sheet. Marker geometry is in absolute units, so render scale is the only way to magnify it. The
manual-task marker failed instantly at 10× where at card size it was a smudge you would argue
yourself out of.

## What the checkers each measure — and each miss

| | measures | blind to |
|---|---|---|
| `lint_figures.py` | a label against the **shape** it sits in — 7 checks | `kind == "rule"` **entirely** (a label across a gridline, axis or boundary); a **group's border** for notes; a **cylinder's rim**, because it measures the rect |
| `reads_at.py` | a label against **the room** — `caveat-equivalent × 890 / max(w, 2.2h)` | anything that is not size: overlap, direction, whether the red means one thing |

**Each of lint's three blind spots has produced a defect nobody caught by machine.** Run both,
then still look.

`lint_figures.py` takes **over five minutes** across the eleven families — background it or ask
for a longer timeout, or it will look like it hangs. One family is fast. `reads_at.py` is ~2 min.
**`reference_cards` is in neither default** — lint it by name, and it is deliberately not in
`reads_at` at all.

## The legibility arithmetic

1. **A floor in canvas units is not a legibility guarantee.** A figure is scaled to fit its
   slide, so 18pt on a 460-unit canvas reads across a room at ~32 real points and the same 18 on
   a 1200-unit canvas reads at ~13. **`w ≈ 890` is where the diagram floor meets the 18pt body
   floor.** Choosing `w` is a legibility decision, not a layout one.
2. **Aspect is the other half.** A 16:9 slide leaves about **2.2 : 1** of usable area. Wider than
   that is fitted by width; **anything squarer is fitted by height**, and the width it was drawn
   at stops mattering. So **adding a row to a wide figure costs legibility twice**.
3. **⚑ On a height-fitted figure, width is FREE.** Widening costs *no legibility at all*, so
   **only shorten a label when width will not do it** — check `asp` and `fit` in
   `tools/reads_at.py --all` before deciding a figure is out of room. Three of one session's five
   geometry fixes were exactly this.
4. **⚑ But width is free and *size* is not: they are different questions.** A figure-slide stage
   is **2.57 : 1**, and a drawing squarer than that is fitted by the stage's *height*, so its
   aspect cancels out of how big it renders. Widening the canvas alone therefore buys nothing:
   `compact()` targets an effective width of 890 and `K_FLOOR` stops it at 0.55, so a
   wide-but-still-tall drawing lands over target and **loses** labels instead of gaining them.
   **The height has to come out.** And because margins are fixed while geometry scales, a final
   890 × 340 needs raw *content* nearer 3.1 : 1 than 2.6 : 1.
5. **`compact(target)` means `max(w, 2.2 × h)`** and shrinks the **geometry**, leaving the type
   alone — because what makes a figure wide is *distance*, and distance carries no information.
   Its diagnostic tells the two failure modes apart: width-bound names the longest label and says
   wrap it; **height-bound says *cut rows, not units***, because naming a label there sends the
   next reader to fix the wrong thing.
6. **Call `compact()` from the family's `figure` decorator, not from `main()`** — otherwise the
   linter measures the geometry as written rather than as rendered, and a note lying across a
   hexagon stays invisible for as long as the two disagree.
7. **⚑ `K_FLOOR = 0.55` fails silently.** A figure drawn one row taller than it needs can want a
   `k` below the floor; `compact` stops there, takes the label-fit branch and **says nothing**.
   Only `reads_at` will tell you. **The lever is dead vertical space, not content** — one figure
   was 17.6pt and the whole difference was 104 units of nothing above its foot comment.
8. **The label-fit clamp is `(advance + 12) / w`, so `w` is the lever, not the word.** Widen the
   shape rather than shortening the name it carries. A shape may not shrink below its own label,
   which is the honest floor for the 12 clamp-bound figures still under 18pt.
9. **⚑ The floor is per-face.** Plex Sans's x-height is `0.516`em against Caveat's `0.400`, so
   **14pt of Plex reads as 18pt of Caveat**. Never compare the two registers by point number —
   use `Diagram._pt()`. A survey that ranks families by `size=` names BPMN as the worst offender
   when it is the only family already at the floor, and "sweep everything to 17" would break it.
10. **`lx` / `ly` are text-space and do not scale**, so they are the only nudge that means the
   same thing before and after `compact()`. **Re-measure them every time the target moves**, in
   **post-compaction** units. A scratch probe printing each label's `x0..x1` against the shapes
   and group borders is worth writing before touching anything.
   **⚑ And an arrow label is inside `_extent`**, so an over-large `ly` does not just sit low — it
   makes the whole figure **taller**, and quietly gives back the aspect you were redrawing for. A
   `ly` of 33 against 30 cost 9 units of final height and 0.07 of aspect on one figure. If a
   drawing will not reach the aspect the arithmetic says it should, check the label offsets before
   touching the geometry.
11. **⚑ Two pieces of text cannot be spaced in raw units.** Their *positions* scale and their
    *heights* do not, so a comfortable 50-unit gap between two notes arrives as 29 against type
    24 tall. **Three separate figures have shipped this exact defect.** Size a text-to-text gap
    in **final** units — raw gap × k — and check the foot comment against the lowest shape after
    compaction, every time.
12. **A harder `compact` target is a licence to spend width, not to shorten labels.**
13. **Expect lint to go noisy after a harder compaction, and budget for it.** That is the tax and
    it is the work, not a sign the target is wrong.
14. **Raising a floor breaks layouts sized for the old one, invisibly.** Rebuild all eleven
    families and lint after any change to `CONTENT_PT` / `ASIDE_PT`.

## Colour, and what a label *is*

`Diagram._legible()` runs at the top of both serialisers and raises every label to **18pt**.
`CONTENT_PT` and `ASIDE_PT` are both 18, so **size no longer separates a remark from a name —
colour does.** Say what a note *is*; spend a `size=` only to go *above* the floor. `_legible()`
sweeps the **hand register only**, so a Plex Sans figure keeps every size as written — which is
what makes a dense print card possible at all.

**Four text colours, four questions.** *What is this?* → `INK`. *Where does it go?* → `CARBON`.
*What is the one thing here?* → `ANNOTATION`. *What do we say about it?* → `COMMENT`.

**`muted` is for lines, not letters.** `#8A8578` is 3.59:1 on the paper — the only colour under
4.5:1. It keeps hairlines, gridlines and dashed ties; text is `COMMENT` `#2F5D3A` (7.45:1). A
muted *edge* still strokes grey, but its **label** is COMMENT.

**A name is ink; a remark is comment green.** If removing the note would leave something in the
picture unnamed, it is content. The old rule said a *muted* note names the pattern element —
that was the defect, not the convention, and it cost two review rounds.

**One idea in red per figure**, stated as a red note at the top — the sentence the presenter says
aloud. *One idea*, not one arrow: `paper-guest-cycle` reds four hand-offs because "every stage
hands the next one a piece of paper" **is** its single idea. `Departure` had seven reds and no
idea, which is the failure this rule exists to prevent. **Paired figures contrast through red**:
*Polling Consumer* reds `receive()`, *Event-Driven Consumer* reds the push; *Invalid Message*
diverts from the **receiver**, *Dead Letter* from the **channel**.

## Composition — the two-part test

**⚑ Sharing apparatus is necessary but NOT sufficient. A reader separates *paths*, not boxes.**

`compact()` shrinks geometry and leaves type alone, so two stages glued side by side hit the
label-fit clamp and both lose about a quarter of their label size. **The saving is that the
apparatus is drawn once and only the outcomes are drawn twice.** Where a pair duplicates its own
stage, merging *recovers* room — one figure went 15.9pt → 18.0.

But that test was **half a rule**. `flow-lookup-two-answers` passed it on every count and Ian
still split it back: *"I think this is confusing combined."* Both answers ran **between the same
two nodes**, so every arc belonged to one mechanism or the other and nothing said which. **The
apparatus was halved and the paths were not.**

> **Compose only where the apparatus is drawn once *and* the outcomes do not have to be picked
> out of each other by eye.**

Three corollaries:

- **A figure under the floor is a SHAPE problem before it is a composition problem.** The
  15.9pt → 18.0 result was a **misattribution**: that figure was short because it was drawn
  1240 × 700, squarer than 2.2 : 1, so it was fitted by height. Redrawn wide and **separate**,
  both halves sit at 18.0 too. **Merging costs a picture; reshaping costs nothing.**
  `boundary-what-crosses` is the worked example: composed but still *stacked* — an application
  over its store, twice — it was 1.57 : 1 and rendered at **82%** of its measured label size.
  Laid out as a **row**, application beside store, it is 2.60 : 1 and lands at **96%**, with
  nothing cut. **Reshaping is the cheap fix and it is usually available.**
- **A premise cannot be composed with its own answers.** A figure that is a *state* the others
  change is not a comparand.
- **⚑ The arithmetic was right and the drawing was still wrong.** Every number behind that
  composition held up. It took a reader looking at it. **A figure argued from measurements has
  not been checked.**

**A family that argues one thing several times wants a shared `_frame()`** — `coupling_grids`
(one grid, three plots) and `integration_styles` (one stage, four styles). The test is whether
the *reader* has to compare across the figures.

## Construction habits

- **Settle the reading direction before the geometry.** One run's first pass locked the left-hand
  envelope while the consumers were on the right, so every arrow crossed the whole queue. One
  decision fixed four figures.
- **Put the consistency in a helper, not in your eye.** `queue()`, `node()`, `packet()` live in
  `diagram.py`; anything a family must do the same way every time belongs in its helper, never
  repeated per figure where the third one will quietly differ.
- **`_mid()` takes the middle *segment* of a polyline, not the midpoint of the path.** A
  redundant waypoint added purely to move a label is a legitimate fix — comment that it is one.
- **An orthogonal route needs a waypoint per corner, not per turn.** Two vias gave a trapezoid,
  which reads as an arc taking a short cut rather than a signal going the long way round. Name
  the ports' own y values.
- **A structural line down the middle fights every centred label**, and neither `_legible()` nor
  lint will say so. `_frame(bb=)` exists for that.
- **The gaps between boxes are load-bearing.** An arrow label is centred on its own run and does
  not scale, so a 150-unit label needs roughly a 190-unit gap.
- **Branch flows need explicit `via` waypoints.** BPMN routes orthogonally and the automatic
  anchor is wrong for every fan-out — a bare diagonal drops the condition label on a task box.
- **A group's border must clear the shapes *outside* it as well as those inside.**
- **Each batch is one script, not one file per figure**, so a set stays a family and regenerates
  whole. Register with the family's `@figure("name")` decorator, which is also where `compact()`
  belongs.

## The two registers

Hand-drawn — `sketch=1`, Caveat — **except BPMN**, which is `Diagram(..., sketch=False,
font=PLAIN)` with Plex Sans labels. The reason is in the section itself: it puts the delegates'
hand-drawn paper flow beside the same flow as BPMN — *"a notation the rest of the industry
already reads"* — and a hand-drawn BPMN collapses that contrast. BPMN keeps the Field Guide
palette, so the section still belongs to the deck, and Caveat then reads as **our annotation on
top of a standard diagram**. Ian approved this after the fact, 2026-09-02.

**Red is scarcer in BPMN** — the five workflow-pattern figures are vocabulary and carry none.

**There is no third register.** A run may split its *vocabulary* — boxes and call arrows for one
movement, hexagons and packets for another — while both halves stay hand-drawn Caveat. A
vocabulary split is a way of drawing an argument; a register split is a statement about what kind
of thing the diagram is. Do not confuse the two.

**Print is a third medium, though, and `reference_cards.py` says so**: no `compact()`, no entry
in `reads_at.py` (the back row is not holding the card), canvas at A4's own 1 : 1.414, Plex Sans
in both cards, and the one red idea carried as a **mark as well as a colour**, because a venue's
printer is not ours to choose.

## Two things about the output that are easy to get wrong

**Bold is a real axis setting, not a synthetic thickening.** Both bundled faces are variable —
Caveat 400–700, Plex Sans 100–700 — so `_text(..., weight=700)` and `note(..., weight=700)` set
the weight axis. A faked bold would thicken by a fixed amount at every size. `note`'s weight also
travels out to the `.drawio` as `fontStyle=1`.

**The `.drawio` BPMN style strings were written without a renderer to open them.** The previews
come from our own SVG and do not check draw.io's styles at all. If a `.drawio` opens with the
wrong glyph in a circle or a diamond, `Diagram._drawio_bpmn` is where to look — the PNG will look
right and the editable file will not.

Text is outlined to vector paths, so previews are faithful **without installing fonts** —
necessary rather than clever: librsvg here ignores `@font-face` data URIs and Caveat/Plex are not
installed, so anything else silently falls back to Helvetica. **Helvetica itself renders fine**,
which is what makes `repatch_steps.py` possible: it is draw.io's own default face, so repainted
numbers are indistinguishable from an export.

## After any `diagram.py` edit

**Rebuild all eleven families and check `git status`.** Every existing figure must come back
**byte-identical**; if one moves, the change was not additive. Ten seconds, and it has caught
real regressions — note cell ids once came from `id(n)`, a memory address, so every rebuild
rewrote every `.drawio`.

```bash
for f in eip_figures coupling_grids if_later queues_streams integration_styles \
         app_shapes conversations bpmn_hotel bpmn_shopping paper_flow flow_reactive; do
  python3 tools/$f.py > /dev/null; done
git status --short resources/
```

A full rebuild is about three minutes.

## Before believing a figure is blocked

**Test the assumption.** Four wrong blockers have been reported to Ian, every one the same shape:
something assumed absent and never checked. *"There is no render"* — there was, under the other
naming convention. *"There is no drawio CLI so he must re-export"* — true about the CLI, but the
numbers were reachable another way, and `tools/repatch_steps.py` now does it in seconds. *"These
are Ian's to draw"* — a **capability** assumed absent, recorded before the tooling existed and
never retested against 37 built figures.

**"Editable" is not the same as "has the thing in it."** Three `.drawio` sources were recorded
for months as the BPMN card's basis, making it *a layout job, not a redraw*. Every shape in all
three has `value=""` — unlabelled icon sheets. `session-work/resource_text_index.py` decodes a
`.drawio` in seconds and settles it.

**A remap can separate two red layers without a re-export** — `tools/repaint_paper_reds.py`
un-blends against the paper to recover draw.io's own alpha. **Patch the `.drawio` as well as the
`.png`**, or the next export puts the old colour straight back.

**And a figure's own foot text is a contract with a handout that does not exist yet.**
`bpmn-the-six` ends *"every other task type, event and gateway is on the reference card in your
pack"* — written a week before anyone drew one, and it made the card's scope non-negotiable.
**Grep the deck for what it has already been promised.**
