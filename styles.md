# Visual style — Practical Messaging

**Settled 2026-09-01.** This file is the **authoritative style spec**. `REDEVELOPMENT-PLAN.md` §13 records
*why* it was chosen; this file records *what to build*. Phase 2 artwork and Phase 3 slides both work to it.

Reference: the three directions rendered side by side —
https://claude.ai/code/artifact/45339596-b57a-4132-9e3e-121599954c61

---

## The direction — C, "Field Guide"

**A serious typographic frame with the hand-drawn work living inside it.**

The hand-drawn quality is an **asset, not the fault**. Delegates reproduce the in-tray / out-tray notation
with a pen during the Paper Flow exercise, so the drawings have to look like something a person could
draw. "Professional" here means doing the hand-drawn thing *deliberately*, inside a frame that is
typographically serious — not replacing it with a corporate template.

**What was actually failing** (measured from both `.pptx` files, not impression):

| | |
|---|---|
| **4:3** | Both decks were 10 × 7.5in — letterboxed on every modern screen |
| **Chalkboard everywhere** | 908 runs on Day 2, 398 on Day 1, carrying every heading *and* every body line |
| **8pt body** | 227 runs at 8pt on Day 1; 12pt next most common. Unreadable four rows back |

---

## Canvas

**16:9 — 13.333 × 7.5 in** (12192000 × 6858000 EMU).

**Three kinds of slide carry no outline entry**: the **cover**, a **section card** (`## Section` —
manila ground, a 0.10in `annotation` bar across the top, the section name at **40pt** and its blurb in
`comment`), and a **group card** (`#group:` + `#divider:` — see below).

**⚑ A group card must read as subordinate to a section card, and the whole design is that contrast.**
Ian asked, 2026-09-12, for a header on each of Day 2's four movements; a movement is one beat inside
*Flow and Reactive Programming*, so a card that looked like a section card would announce a section that
does not exist. So the group card is **paper, no bar, and its title is 29pt** — the same weight as any
slide title — over a `carbon` Plex Mono eyebrow (the part of the group title before the em dash) and one
line of `comment`. Ian chose this over manila-without-the-bar and over a 40pt rule, both of which kept
too much of the section card's weight. **It is opt-in**: `#group:` alone still only sets the kicker, and
`#divider:` is what makes the slide, because Day 2 has six groups and four cards.

**The eyebrow is `carbon`, not `muted`**, though the agreed mock-up said muted — muted is **3.6:1** on
paper and is for lines, not letters. Carbon is also right on its own terms: the four-colour rule gives
carbon to *where does it go?*, and *Movement A* is an address.

**Layout.** A **kicker** — the section name, Plex Mono, uppercase, tracked — sits above the title on
every slide, and a **folio** — the slide number — sits in the bottom-left margin of every slide but
the cover. The folio is an address, not a piece of the slide: same face and same colour as the
kicker, two points smaller, and **below the bottom margin**, where the figure stage already stops. Below it there are three arrangements, and **what decides between them is whether the
picture carries type**:

| the slide has | layout |
|---|---|
| a **drawing** (`.png`) | **the figure leads.** Title, the callout if there is one, then the figure at the **full content width**. |
| **photographs** (`.jpg`) | text left, photographs in a fixed **manila panel** on the right, **1.15 : 0.85**. |
| no picture | full width, same left margin and kicker. |
| `#layout: side` | text left, the **drawing** right, **0.47 : 0.53**. Opt-in per entry, and the entry does not split. |

**⚑ The fourth arrangement is an override, and it is meant to be one.** Ian asked for it on six §4.4
slides — *"shrink the diagram… put the text on the left… It's too weird to read the words, then show the
diagram here"* — where the argument and the picture are one thought. It costs the drawing most of what
the figure-leads rule was written to protect, so **the builder reports what each `side` slide costs its
figure by name**, every run, rather than absorbing it. On the six as built: 49–71%, against 85–101% as
full-width figure slides. Reach for it when the words and the picture have to be read together, not to
save a slide.

**⚑ Amended 2026-09-08, and the amendment is load-bearing.** This originally put *every* diagram in the
manila panel. The panel gives a figure **4.6in**; Phase 2 sized every label so the figure reads at 18pt
displayed **12.4in** wide (plan §8 items 9, 10, 18, 19). Measured, a figure in the panel read at **37–53%**
of the size it had been measured at — an 18.0pt label landing at 7–9 real points, on 84 of the 106 slides
carrying a picture. **Two settled decisions, months apart, that cancelled each other.** Ian chose the
figure. Full width restores ~97%; the built decks measure 91% (Day 1) and 96% (Day 2), median.

**A photograph tolerates being small; a labelled drawing does not.** That is the whole distinction, and
the file extension carries it — every photograph in `resources/` is a `.jpg` and every drawing a `.png`.

**One labelled figure per slide.** Two sharing a stage each take about half its linear size, which is the
tax the panel charged in the first place. Where the reader genuinely has to compare two pictures, the
answer is a **composed figure**, not two small ones — see `tools/conversations.py`, which merged three
2021 exports into one for exactly this reason.

**An entry may become two slides**: the argument, then the picture. The **callout goes with the picture**
— it is the line the presenter says aloud about what is on screen — and both slides keep the same title,
so the pair reads as one thought with the picture revealed. Plan §8 item 23a.

---

## Type

All three faces are **SIL Open Font License 1.1** — commercial training use, PowerPoint embedding and
printed handouts are all permitted. Local copies live in `tools/fonts/`.

| role | face | treatment |
|---|---|---|
| Slide titles | **IBM Plex Serif** | 600 weight, −0.01em tracking |
| Body | **IBM Plex Sans** | 400/600 |
| Kickers, labels, specs, code | **IBM Plex Mono** | uppercase + `.16em` tracking for kickers; replaces Consolas for code |
| Callouts (`▎`) and diagram labels | **Caveat** | **500/700** |

### The one rule that matters

> **Caveat never carries body copy.** Callouts and diagram labels only.

This is the discipline that separates this style from the old deck, where a handwriting face carried
everything. Break it and the deck reads as personal again.

### Sizes

| | |
|---|---|
| **Body floor** | **18pt** |
| **Sub-items** | **16pt permitted** — the only exception |
| **Nothing below 16pt** | ever |

Expect the floor to force content off crowded slides. **That is intended** — it will find the slides doing
too much, and it is a content decision as much as a design one.

---

## Palette

Taken from the Paper Flow notation rather than invented, which is why it does not fight the ~40 existing
editable `resources/*.drawio` diagrams.

| token | hex | where it already exists in the course |
|---|---|---|
| `ink` | `#181B1F` | everything a clerk writes by hand |
| `paper` | `#FDFCFA` | the slide ground |
| `carbon` | `#1D4E6B` | the carbon copy — which **is** the outbox pattern we teach |
| `annotation` | `#C0453B` | the one idea a figure is about — **not** the paper-moving arrows. That line was this table's own example until R4-15, and it was wrong: the delegate brief's line 35 says *dashed / solid* with **no colour**, `paper-notation-key.png` draws the hand-off in **carbon**, and all eight 2021 flows have now been repainted to agree |
| `manila` | `#F3EFE6` | the file, the folder, the desk — and the diagram panel |
| `rule` | `#E0D9C8` | panel edges, hairlines |
| `muted` | `#8A8578` | hairlines, gridlines, dashed ties — **guides, never text** |
| `comment` | `#2F5D3A` | our remarks *about* the drawing |

**Annotation red is reserved.** It marks the one thing the slide is actually about — not decoration, and
never more than one idea per diagram. Carbon blue carries flow and structure; ink carries everything else.

**Four text colours, and each answers a different question.** *What is this?* → **ink**. *Where does it
go?* → **carbon**. *What is the one thing here?* → **annotation**. *What do we say about it?* →
**comment**. A label that names a part of the drawing is content and takes ink at the content size; a
remark about the drawing takes comment green one step below it. Nothing readable is ever `muted` —
**`muted` is for lines, not letters.** It measures 3.6:1 against the paper, the only colour in the palette
under the 4.5:1 threshold, which is why it looked fine on a laptop and vanished on a projector.

**The comment colour is doing the work that faintness used to do**, which is the point: the deck was
saying "secondary" twice, in size *and* in contrast, and paying for it twice. Ian, reviewing the sweep:
*"I think we might find this isn't just about a different font size or bold, but making it a more readable
colour."* Green also happens to help the ~8% of a developer audience with red-green colour blindness —
not because green is easy for them, but because to a deuteranope annotation red already reads as olive
`#7B7B33`, which the old muted grey `#868678` sat right on top of. The green pulls the two apart.

---

## Diagrams

- **Hand-drawn register.** Wobbled strokes (`sketch=1` in draw.io; a turbulence displacement filter in the
  SVG preview), Caveat labels, ink stroke, carbon arrows.
- **Source of truth is `.drawio` XML** in `resources/`, so every diagram stays editable in draw.io and
  matches the ~40 sources already there.
- **Stroke** 1.6–1.8px at diagram scale. **Rounded corners**, `r=4`.
- **Databases** as cylinders, attached to their service with a dashed `muted` line.
- **One idea in red.** If two things are red, the diagram is doing two jobs.
- **A trace is a block arrow laid OVER a finished drawing, and it is not a diagram element.**
  `Diagram.trace()`. It says *follow this*, and it is deliberately far too big for what is under it —
  which is the licence for the drawing beneath being tiny. **Asynchronous is `carbon`, synchronous is
  `muted`**, because where the two are contrasted the asynchronous case is the argument and the phone
  call is what should recede. A trace carries **no label**: if it needs one, it is an `arrow`. Traces
  are exempt from the 18pt floor for the same reason — there is nothing on them to read.
- **Muted is for *our* annotation, not the notation's own words.** A label that is part of what the
  diagram *is* — a stream's offsets, a port's name, a step number — is **ink at label size**, the same
  size as a box label. `muted` is for the remarks we add on top: the caveat at the foot, the aside
  beside a shape. Getting this backwards makes the content quieter than the commentary, and it does not
  show up until the figure is on a projector. **Stream offsets were 12pt muted until Ian saw them across
  a room.**
- **One floor: 18pt, the same number as the body floor.** Content and commentary are the same size and
  the *colour* is what separates them — which is what the muted-to-comment change already decided, taken
  to its conclusion. The old pair (17 content / 16 aside) said "secondary" twice, in size and in hue, and
  paid for it twice. The 18pt body floor exists because the old deck was unreadable four rows back; a
  diagram label is no more legible than a bullet, so it gets the same number.
- **⚑ That number is in canvas units, so the canvas width decides what it means.** A figure is scaled to
  fit its slide, so 18pt on a 460-unit EIP canvas reads across a room at about 32 real points, and the
  same 18 on a 1200-unit canvas reads at 13. **The floor is not a legibility guarantee on its own** —
  it is a guarantee only once the canvas width is chosen. Roughly, at full slide width, a label reads at
  `18 × 890 / w` real points, so **w ≈ 890 is where the diagram floor meets the body floor**.
- **Aspect matters as much as width.** A 16:9 slide leaves about 2.2 : 1 of usable area for a figure.
  Anything wider than that is fitted by width; anything squarer is fitted by *height*, and then every
  label in it shrinks again. Adding a row of content to a wide figure costs legibility twice over — once
  for the height, once for the aspect. **Cut content or cut width; do not just raise the number.**
- **Spend distance, not type.** What makes a figure wide is usually the gap between things, and a gap
  carries no information. `Diagram.compact(890)` shrinks the geometry and leaves the labels alone; the
  two Day 1 / Day 2 redraw runs are built through it. A shape may not shrink below its own label, and a
  long line of text does not shrink at all — so a caveat that will not fit is a caveat to reword.
- **That number is Caveat points, and the two faces are not on the same scale.** IBM Plex Sans's
  x-height is `0.516`em against Caveat's `0.400`, so **14pt of Plex reads across a room as 18pt of
  Caveat**. The BPMN register is therefore already at the floor at the sizes it was drawn at, and a flat
  "18pt everywhere" would make it a third larger than the deck around it. Compare the two registers by
  x-height, never by point number — comparing point numbers is what let the labels drift.
- **The floor is enforced, not remembered.** `Diagram._legible()` raises every label at render time, so a
  figure cannot quietly ship at 13pt again. Set a size only to go *above* the floor.
- **⚑ `#layout: side` is an agreed exception to all of the above, and it is not small.** The half-stage
  is **6.1in** where every number here was measured at 12.4, so a figure on a `side` slide reads at
  roughly **half** what its canvas width predicts. The **thirteen** of them land at **8.9–12.8 real points**.
  **Ian, 2026-09-12, shown those figures: *"I think that is fine."*** So a `side` slide is not held to
  the 18pt floor — it is held to being **read at a metre, not across the room**, which is what the
  arrangement is for: the words and the picture are one thought and the room has the words beside it.
  **This does not relax the floor anywhere else**, and it is not a licence to put `side` on a figure the
  room has to read on its own. It is also why `reads_at.py` still reports 18.0pt for those figures —
  it measures the full-width stage and is blind to the arrangement (`BACKLOG.md` G12).

### Building them

`tools/diagram.py` emits **both** the `.drawio` source and a `.png` preview from one definition, so the
editable file and the thing you look at can never drift apart. See `tools/README.md`.

```
python3 tools/diagram.py --demo            # render the worked example
python3 tools/diagram.py --check           # verify renderer + fonts
```

---

## Print

Four deliverables are **printed handouts** — AsyncAPI, routing patterns, Paper Flow materials, and the BPMN
reference card. The palette is chosen to survive greyscale: `carbon` and `annotation` differ in value, not
just hue, so they stay distinguishable on a mono office printer.

Handouts use the same type stack at document sizes (body 10–11pt, which is a *print* measure and does not
touch the 16pt slide floor).

**`handouts/print.css` is the house sheet** — one stylesheet for the whole takeaway pack, built by
`handouts/build.sh` through pandoc and WeasyPrint. It implements this file at document sizes: body **11pt**
on a **154mm measure** (about 79 characters, which is a line you can read down a page), Plex Serif headings
in ink and carbon, the palette verbatim, and blockquotes as `comment` on `manila` — because an aside is
*what we say about it*, and because **Caveat never carries body copy**, which rules it out of a handout
entirely. The eight routing figures are capped by **height**, not width, since they run 1.26 : 1 to
3.04 : 1 and a width cap would give the squarest of them a page to itself.

**Three things the sheet must not break**, each found by building a PDF and looking at it:
a preformatted block wraps past **~62 monospace columns**; an arrow glyph inside one falls out of the
monospace face and destroys the alignment, which is why every handout diagram is pure ASCII; and
**WeasyPrint does not synthesise an oblique**, so the italic faces have to be vendored beside the roman
ones or every `*emphasis*` in the pack renders upright without a warning.

---

### Callouts and the substituted face

**A callout's reserve is `n` lines of Caveat, and PowerPoint may need `n + 1`.** Caveat is not installed
on the presenting machine, so PowerPoint substitutes a wider face, the callout wraps once more than the
layout reserved, and everything below it — prose, or the figure — is 1.06em too high. Ian saw it on Day 2
slides 7 and 82. **It is not the first-baseline model** (Caveat's lift is 0.008em) and not the reserve,
which R3-14 already fixed.

**The fix is `cp tools/fonts/*.ttf ~/Library/Fonts/`**, because a wider face is also the *wrong* face and
nothing in the builder can make a fallback look like handwriting. The builder's job is only to make the
risk visible: it re-wraps every callout at **`SUBST_W` = 0.90** of its measure and names any that would
gain a line. That number is **a guard calibrated on Ian's two observations** (93.7% and 90.6%), not a
measurement — there is no PowerPoint here to measure the substitute with.

## Open

- ☑ **Plex Mono confirmed** for kickers, labels and code (2026-09-01).
- ☑ **IBM Plex Serif** is in `tools/fonts/` — Regular and SemiBold, from Google Fonts, OFL 1.1
  (2026-09-08). Titles are set in **`IBM Plex Serif SemiBold`**, which is the face name the OS exposes
  for the 600 weight; naming the family and asking for bold reaches for a Bold we do not ship.
- ☑ **The italics are vendored too** — `IBMPlexSans-Italic`, `IBMPlexSans-SemiBoldItalic` and
  `IBMPlexSerif-Italic`, same source and same OFL 1.1 (2026-09-10). They are **for the handouts, not for
  the deck**: no figure and no slide sets an italic, `_FONT_FILES` in `tools/diagram.py` names its faces
  one by one rather than globbing the directory, and a rebuild of all eleven families after they landed
  came back byte-identical. They exist because **WeasyPrint does not synthesise an oblique and does not
  warn**, so every `*emphasis*` in both handouts was rendering upright.
- ☐ **System font install — now live, not future.** `tools/fonts/` holds the OFL files for the preview
  renderer, which outlines glyphs to paths and needs no install. **PowerPoint does need them installed**,
  and the built decks name all four faces, so until `cp tools/fonts/*.ttf ~/Library/Fonts/` has been run
  PowerPoint substitutes and the first thing Ian sees is not the deck we built. Ian's machine, Ian's call.
- **⚑ Two registers, two scales — on slides as well as in figures.** Caveat's x-height is 0.400em against
  Plex Sans's 0.516, so **18pt of Plex reads as 23pt of Caveat**. The 18pt body floor above is a *Plex*
  measure: a callout set at 18pt Caveat would sit a fifth below the floor while appearing to obey it.
  Callouts are therefore **24pt**. Same trap as `PROMPT.md` rule 14.

### Sizes as built (`tools/build_deck.py`)

| | |
|---|---|
| slide title | 29pt Plex Serif SemiBold |
| kicker | 12pt Plex Mono, uppercase, 0.16em tracking, carbon |
| folio | 10pt Plex Mono, 0.10em tracking, carbon, bottom left; the cover carries none |

### Text boxes, and why one per paragraph

**A paragraph is one text box in the `.pptx`, not one box per wrapped line.** Ian, 2026-09-10:
*"we want text box per paragraph, bullet, or heading."* The box wraps to the width the layout measured,
so PowerPoint re-wraps to the same breaks when the fonts are installed and **degrades by wrapping rather
than by running off the slide when they are not** — which is what four callouts were doing.

The preview still draws line by line; both back ends read the same op stream, and only the `.pptx` one
coalesces. `_first_baseline()` carries the arithmetic that makes the two agree vertically, and it is a
**model of PowerPoint rather than a measurement of one** — the single place to correct if a built deck
opens with every paragraph a few points off.

### Progressive disclosure

**Slides build by idea, and the builder infers the grouping** — Ian ruled against a marker in the
outline. A lead-in paragraph and the bullets under it arrive together; a table, a code listing, a
quotation or a callout is its own step; a run of bullets with no lead-in is one step, not five; the
picture is its own. Chrome — ground, kicker, title, folio — is step 0 and never animates.
`--no-animation` builds without it.
| body | **18pt** Plex Sans · sub-items 16pt |
| callout | **24pt** Caveat, annotation red, with a red bar. Lines are set **1.06em** apart — Caveat's ascenders look sparse at the body's 1.24 — but the block **reserves the font's own 1.260em ink extent for its last line**, or the next thing sits on the descenders. See `_reserve` in `build_deck.py` |
| table | 15pt Plex Sans, columns proportional to content |
| code | 15pt Plex Mono on manila |
