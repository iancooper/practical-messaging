# tools/

Build tooling for Phase 2 artwork. Style spec is `../styles.md`.

## `diagram.py`

Emits a diagram as **both** editable `.drawio` XML **and** a `.png` preview, from one definition.

```
python3 tools/diagram.py --check          # verify renderer + fonts
python3 tools/diagram.py --demo [path]    # render the worked example
```

**Why both from one source.** The `.drawio` file is the canonical, editable artefact — it matches the ~40
sources already in `resources/` and opens in draw.io. But there is **no drawio CLI on this machine**, so
nothing can render it locally to check the work. Maintaining a separate preview by hand across 12 EIP
figures plus 14 Day 2 markers guarantees the two drift apart. Emitting them together means they cannot.

### Library use

```python
import sys; sys.path.insert(0, "tools")
from diagram import Diagram, ANNOTATION, MUTED

d = Diagram("Dead Letter Channel", w=340, h=170)
snd  = d.box(10, 40, 84, 50, "Sender")
rcv  = d.box(246, 40, 84, 50, "Receiver")
dlq  = d.box(246, 116, 84, 40, "Dead Letter", accent=True)
pipe = d.pipe(126, 54, 88, 22)
d.arrow(snd, pipe)
d.arrow(pipe, rcv)
d.arrow(pipe, dlq, "undeliverable", accent=True)
d.note(170, 24, "the message the receiver could not take", MUTED, 14)

d.save("resources/eip-dead-letter-channel")   # -> .drawio + .png
```

**Elements:** `box`, `group` (a labelled container — *your application*, *messaging gateway*),
`msg` (a message on a channel), `cylinder` (a database), `pipe` (an EIP channel), `note` (free text),
`arrow` (carbon, with head), `attach` (dashed muted tie — a service to its database).

`box` and `note` take multi-line labels — `"Message\nPump"` stacks and block-centres.

**Routing.** `arrow` picks the edge that faces its target. Override it when the automatic choice is
wrong — which it is for any fan-out, because all the arrows want to leave the same side:

```python
d.arrow(pipe, sub, sides=("r", "l"))                     # pin both ends
d.arrow(pump, pipe, "receive()", accent=True,            # a return path, routed round
        via=[(356, 58), (93, 58)], sides=("t", "t"))
d.arrow(rcv, dlq, "cannot read it", lx=-62)              # nudge a label off the line
```

`src` and `dst` may also be a bare `(x, y)` point, for an arrow that comes from off-diagram.

**`accent=True`** paints an element or arrow in annotation red. Per `styles.md`, **red marks the one thing
the diagram is about** — if two things are red, the diagram is doing two jobs.

### How it works

- **Shapes** are wobbled by an SVG turbulence-displacement filter, matching draw.io's `sketch=1`.
  **Text is deliberately not wobbled** so labels stay legible.
- **Text is outlined to vector paths** with fontTools, so previews are faithful with **no system font
  install**. This is necessary rather than clever: librsvg here ignores `@font-face` data URIs (verified),
  and Caveat/Plex are not installed, so anything else silently falls back to Helvetica.

## `eip_figures.py`

The 12 EIP figures that replaced the Hohpe & Woolf illustrations in `outlines/DayOne.md`, as one script,
so the set stays a family — same canvas widths, same label voice, same convention for what red means.

```
python3 tools/eip_figures.py                    # rebuild all 12 into resources/
python3 tools/eip_figures.py eip-dead-letter-channel   # just one
python3 tools/eip_figures.py --list
```

**Read the renders before believing them.** The first pass had a missing arrow and four labels sitting on
top of strokes; none of it was visible in the source. Every figure was eyeballed as a PNG and fixed.

Conventions held across the set, and worth holding for the next batch:

- **one red idea per figure**, stated as a red note at the top — the sentence the presenter says out loud
- a **muted note** names the pattern element where the name is the thing being taught (*dead letter
  channel*, *invalid message channel*), and a second muted note at the bottom carries the caveat
- **paired figures contrast through red**: *Polling Consumer* reds `receive()`, *Event-Driven Consumer*
  reds the push; *Invalid Message* diverts from the **receiver**, *Dead Letter* diverts from the
  **channel** — which is the distinction the two slides keep getting confused about

## `fonts/`

`Caveat.ttf`, `IBMPlexSans-Variable.ttf`, `IBMPlexMono-Regular.ttf` — all **SIL OFL 1.1**, so commercial
training use, PowerPoint embedding and printed handouts are all permitted. From
`github.com/google/fonts`.

These are for the **preview renderer only** and are not installed system-wide.

> **Phase 3 will need them installed**, because PowerPoint cannot use a font that is not on the machine:
> `cp tools/fonts/*.ttf ~/Library/Fonts/`
> Not done — that is a change to Ian's machine and his call. IBM Plex **Serif** is not here yet; add it
> when a diagram needs a serif label, or at the start of Phase 3.
