---
name: review-sheet
description: Build and publish a Practical Messaging artwork review sheet — the page Ian reviews figures on, because he cannot see PNGs in a terminal. Carries the generator's requirements (inlined data URIs, styles.md palette, an address on every claim, light in both themes), the publish etiquette, and the seven sheets already out. Use when a batch of artwork needs review, when findings come back, or when asked to republish a sheet.
---

# Review sheets

**Ian cannot review PNGs in a terminal, and he reviews by looking.** Every finding on this work
so far — six on legibility, two rulings on the composed figures — arrived through one of these
pages. A batch of artwork is not reviewed until one has been up.

## ⚑ The etiquette, which comes before the page

**A publish needs Ian's say-so, every time.** The first attempt at the batch-three sheet was
**refused by the auto-mode classifier** — *"the user never asked for a review web page"* — and
that was **correct, not a tool fault**. It went through once he said *"go ahead"*.

- **Ask before publishing. Do not route around a refusal.**
- **Offer the sheet in the same `AskUserQuestion` as the decision it illustrates.** Both
  2026-09-07 sheets were approved that way before they were built, and that is the pattern to
  keep.
- If he has not said yes: build the file, hand over the path, stop.
- **His answer often exceeds the options offered** — read it as prose, not as a selection.
  *"Does Versioning move?"* came back as *"drop Versioning **and** Observability."*

## What the page has to do

Load `artifact-design` before writing it. Then, five requirements, each of which has a reason:

1. **Inline every PNG as a base64 data URI.** The artifact CSP blocks local files and external
   images — a linked image is simply not there, with no visible error.
2. **Set the page in `styles.md`'s own palette and faces**, so the red on the page is the red in
   the figures. A sheet in some other red is asking him about a colour he is not being shown.
   `ink #181B1F` · `paper #FDFCFA` · `carbon #1D4E6B` · `annotation #C0453B` · `manila #F3EFE6` ·
   `rule #E0D9C8` · `comment #2F5D3A`; Plex Serif titles, Plex Sans body, Caveat for callouts.
   Fonts come from `fonts.googleapis.com`, which is on the allowlist — give every face a real
   fallback stack.
3. **Give every claim an address he can quote back** — `A4·1`, `B2·2`. **He reads line by line
   and pushes back by line number**, and both rulings that came back on sheet 7 came back by
   address. A sheet without addresses costs a round trip working out what he means.
4. **Keep the plate light in *both* themes.** The page renders in the viewer's theme, and **a
   printed card cannot be dark-moded** — a reference card shown on a dark ground is not the
   artefact being reviewed. Define the full light palette on bare `:root`, and pin the figure
   plates light under `@media (prefers-color-scheme: dark)` and `:root[data-theme="dark"]`.
5. **Say what is being asked.** A sheet that shows work without naming the decision gets looked
   at and not answered. Sheet 7 asked two questions and got two rulings; the sheet before it left
   RPC's red implicit and it has never been answered.

## Structure that has worked

Sections **A**, **B**, … one per group of figures, each item **A1**, **A2**, … Under each figure:
what it argues in one line, what its **one red idea** is, and — where there is a question — the
question stated as a question, in `annotation`, with its own address. A short opening plate
saying what the batch is and what is being asked. Numbers where they exist: `reads_at` before and
after, the aspect, the width.

## The generator — `tools/review_sheet.py`, and it is committed

Seven sheets were written into scratchpads and died with their sessions (`build_ba2.py`, then
`sheet.py`). **The eighth was not**, and the five requirements above are now enforced in code:

```bash
python3 tools/review_sheet.py <spec.json> -o <out.html>
```

The spec is JSON and its shapes are in the module docstring. **Addresses are generated, not
written** — item *n* of section `A` is `A1`, and its plates are `A1.1`, `A1.2` — so they cannot
drift from the order of the page. Each item takes `argues`, `red`, `rows` (the numbers),
`question` (rendered in `annotation`, with its own address) and, once a ruling comes back,
`verdict`.

**Plates are slide renders, not figure PNGs, when the question is about the layout.** Build them
with `build_deck.py --day N --preview i` — remembering that `--preview` is **zero-based** and the
output filename is that index, so `--preview 75` writes `day2-075.png` and it is slide **76**.
For a before/after: capture the current build, edit the outline, build and capture again, then
`git checkout` the outline and rebuild. Copy the PNGs out of `build/preview/` first — it is not
cleared between runs, and `build/` is gitignored, so a spec that points at it is not reproducible
from a later session.

## Publishing, and republishing

- Publish with the `Artifact` tool. Keep the `<title>` a short, stable name; pass a `favicon`
  on the first publish only.
- **When findings come back, apply them and republish the same artifact** so the addresses keep
  meaning what they meant — pass its `url`, and **`action: "read"` it first**: a publish to an
  artifact this conversation has not read is refused.
- **Scratchpads are per-session**, so "republish the same path" only works inside one session.
  From a fresh one you need the URL, which is in the table below.
- Show the rulings on the republished sheet — sheet 7 came back with both its calls marked in
  green, so the page records what was decided rather than what was asked.
- **Record the sheet and its state** in the table below — this skill is its home — and in
  `BACKLOG.md` F3.

## The seven so far

| sheet | url fragment | state |
|---|---|---|
| EIP | `b40f4cbe-2e48-49c7-bfd6-6b08e99c6710` | ✅ approved, one reword applied |
| BPMN | `7202244e-cbad-47ee-8192-444411c344df` | ✅ approved 2026-09-02 — *"straight-stroked and set in Plex Sans ⇒ agreed"* |
| The Artwork Sheet | `65063d42-0c09-441f-ae2f-eba020814824` | ⚑ part-reviewed — 56 figures up 2026-09-03, 2 findings in and applied, the rest unread |
| The Legibility Floor | `e95f4eb1-94f1-499c-96db-1c0fbc1d148e` | ⚑ awaiting him |
| Muted Is For Lines | `421ddeb9-8353-4f27-98c2-f7c97bf4de12` | ⚑ awaiting him |
| Four Answers, One Stage | `c75acd57-ab6a-4740-918f-af39a6823a08` | ✅ approved 2026-09-07 — *"this looks much better"*. **RPC's red is the one item he never answered**; closed unless he reopens it |
| Four Composed, Two Printed | `40b2a941-5ce3-4260-a882-a4c33e442383` | ✅ reviewed 2026-09-09, both calls answered. `B2·2` approved, **`A4·1` overturned**. The cards' 24 BPMN glosses were on it and drew no comment — **seen, not approved** |
| BPMN on a Half Stage | `3dc05399-3d6a-4fce-a39a-95a544444e47` | ✅ **ruled 2026-09-12, same day, all three addresses.** ⚑ **And two of the three answers were not options on the card** — he asked for an arrangement the builder did not have. Republished with the rulings as verdicts. §R4's three BPMN `side` merges (R4-40/41/42), each shown as it ships beside the full-width slide it replaced. Two of the three read at ~6.0 and ~6.6pt against the **8.9–12.8pt** band Ian ruled. **The first sheet built by `tools/review_sheet.py`** |

| Day One Drawings, Reseated | `525f44f7-9057-4ff6-a39d-fe5854358da0` | ⚑ **published 2026-09-12, awaiting his look.** `BACKLOG.md` **F7** — the 13 Day 1 `side` slides after `SIDE_FIG_RISE`, three shown before and after, ten as they ship, and a section bounding what the change cannot touch |

**Four are still awaiting him.** Sheet 8 went up and came back the same day.

**⚑ Measure the thing the sheet claims, do not eyeball it from the render.** Sheet 9's first draft
grouped the 13 slides by how far they moved, from *looking* at them — and had **two of the extremes
backwards**, because the eye reads the height of the *text* and the rule reads the slack left by the
*figure*. Importing `build_deck` and diffing the image `y` between two values of the constant took two
minutes and produced a table that is right. A sheet's numbers are the part Ian trusts; earn them.

## What his review has actually been about

**Legibility, not the drawings.** Six findings, each the same defect one level up — a label that
is the notation's own word, set at note size in note colour → the colour itself → the floor → the
floor's *units*. Five are now enforced in `diagram.py` rather than remembered.

**Nothing has been questioned about the content, the vocabulary split or the red pairing yet.**
Do not read approval of a batch as approval of those.

**⚑ And a sheet's options are a starting point, not a menu.** Sheet 8 offered keep / revert / revert
two of three on each item, and two of the three answers were **none of them** — he described an
arrangement the builder did not have, and it turned out to be strictly better than either option
offered, recovering 47 percentage points where reverting would have recovered them at the cost of a
slide. **Put the numbers and the pictures up; do not assume the answer space is the one you drew.**

And the sharpest thing a sheet has produced: **the arithmetic was right and the drawing was still
wrong.** Every number behind the composed lookup figure held up, and it took a reader looking at
it to say it was confusing. That is what the sheets are for.
