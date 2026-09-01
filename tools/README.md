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

**Elements:** `box`, `cylinder` (a database), `pipe` (an EIP channel), `note` (free text),
`arrow` (carbon, with head), `attach` (dashed muted tie — a service to its database).

**`accent=True`** paints an element or arrow in annotation red. Per `styles.md`, **red marks the one thing
the diagram is about** — if two things are red, the diagram is doing two jobs.

### How it works

- **Shapes** are wobbled by an SVG turbulence-displacement filter, matching draw.io's `sketch=1`.
  **Text is deliberately not wobbled** so labels stay legible.
- **Text is outlined to vector paths** with fontTools, so previews are faithful with **no system font
  install**. This is necessary rather than clever: librsvg here ignores `@font-face` data URIs (verified),
  and Caveat/Plex are not installed, so anything else silently falls back to Helvetica.

## `fonts/`

`Caveat.ttf`, `IBMPlexSans-Variable.ttf`, `IBMPlexMono-Regular.ttf` — all **SIL OFL 1.1**, so commercial
training use, PowerPoint embedding and printed handouts are all permitted. From
`github.com/google/fonts`.

These are for the **preview renderer only** and are not installed system-wide.

> **Phase 3 will need them installed**, because PowerPoint cannot use a font that is not on the machine:
> `cp tools/fonts/*.ttf ~/Library/Fonts/`
> Not done — that is a change to Ian's machine and his call. IBM Plex **Serif** is not here yet; add it
> when a diagram needs a serif label, or at the start of Phase 3.
