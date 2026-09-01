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

**Layout.** Text left, **diagram in a fixed manila panel on the right**, roughly **1.15 : 0.85**. Every
diagram gets a consistent home rather than floating in whitespace. A **kicker** — the section name, Plex
Mono, uppercase, tracked — sits above the title.

Slides with no diagram use the full width but keep the same left margin and kicker.

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
| `annotation` | `#C0453B` | the red dashed arrows: paper moving between trays |
| `manila` | `#F3EFE6` | the file, the folder, the desk — and the diagram panel |
| `rule` | `#E0D9C8` | panel edges, hairlines |
| `muted` | `#8A8578` | secondary diagram labels, dashed guides |

**Annotation red is reserved.** It marks the one thing the slide is actually about — not decoration, and
never more than one idea per diagram. Carbon blue carries flow and structure; ink carries everything else.

---

## Diagrams

- **Hand-drawn register.** Wobbled strokes (`sketch=1` in draw.io; a turbulence displacement filter in the
  SVG preview), Caveat labels, ink stroke, carbon arrows.
- **Source of truth is `.drawio` XML** in `resources/`, so every diagram stays editable in draw.io and
  matches the ~40 sources already there.
- **Stroke** 1.6–1.8px at diagram scale. **Rounded corners**, `r=4`.
- **Databases** as cylinders, attached to their service with a dashed `muted` line.
- **One idea in red.** If two things are red, the diagram is doing two jobs.

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

---

## Open

- ☑ **Plex Mono confirmed** for kickers, labels and code (2026-09-01).
- ☐ **System font install.** `tools/fonts/` holds the OFL files for the preview renderer, which outlines
  glyphs to paths and needs no install. **PowerPoint does need them installed** for Phase 3:
  `cp tools/fonts/*.ttf ~/Library/Fonts/`. Not done — Ian's machine, Ian's call.
- ☐ **IBM Plex Serif** is not yet in `tools/fonts/`; only Sans, Mono and Caveat are. Add it when the first
  diagram needs a serif label, or in Phase 3.
