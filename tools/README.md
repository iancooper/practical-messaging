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

**Dataflow / FBP elements:** `node` (a component: a hexagon with named ports) and `packet` (an
information packet: a dashed rounded square).

```python
n = d.node(450, 180, 300, 156, "Take Order", ins=("in", "alt_in"), outs=("out",))
d.arrow(d.packet(190, 245, label="IP"), n["ports"]["in"], sides=("r", "l"))
d.arrow(n["ports"]["out0"], other["ports"]["in0"], sides=("r", "l"))
```

`node` owns the reading direction for the whole Day 2 flow run — **in-ports on the left, out-ports on the
right, data flows left to right** — so no figure has to decide it again. Its left and right vertices are
flattened into short vertical edges, which is why a second or third port still lands on a stroke. Ports
come back in `["ports"]` keyed **by name and positionally** (`in0`, `in1`, `out0` …), so an unnamed dot
still has a handle. `accent_ports=("out",)` reds one port and its label without reddening the component.

`packet` is deliberately **not** `msg`. An envelope is a message sitting on a channel and the EIP and
queue families own it; an information packet is a value in flight between ports, with a lifetime that
ends when a component consumes it. Two ideas, two shapes.

**BPMN elements:** `pool` (a participant, with optional lanes), `task` (`marker=` send / receive / user /
service / compensate), `event` (`start` / `intermediate` / `end`, `symbol=` message / timer /
compensation), `gateway` (`exclusive` / `parallel`), `choreo` (a choreography task with its two
participant bands), and `flow` — which draws a **sequence flow** solid with a filled head, or a
**message flow** dashed with an open circle and a hollow head. They are different calls because they are
different things, and Day 2 spends a section on the difference.

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

### Label sizes are a floor, not a per-call decision

`Diagram._legible()` runs at the top of **both** serialisers and raises every label to the floor for what
it is — **17pt** for anything that names something in the drawing, **14pt** for a muted remark of ours.
Pass a smaller `size=` and it will be raised; pass a larger one and it is kept. It is idempotent, so the
`.drawio` and the `.png` can never disagree about a size.

**The floor is per-face, and that is the whole point.** IBM Plex Sans's x-height is `0.516`em against
Caveat's `0.400` (OS/2 `sxHeight`, both at 1000upm), so **13pt of Plex reads across a room as 17pt of
Caveat**. Comparing the two registers by their point numbers is what let the labels drift in the first
place: the BPMN family looked like the worst offender when it was the one family already at the floor.
`_pt(caveat_pt, face)` does the conversion, and `_legible()` sweeps only the hand-drawn register — a BPMN
figure keeps the scale it was drawn at, including the two crowded ones that squeeze a task to 10–11pt.

Edge labels are the one text a figure cannot override, and they were the smallest thing on the slide.
`_edge_pt(e)` puts them at the floor too: **17pt** on a hand-drawn arrow, **13pt** on a BPMN flow.

The floor a note gets depends on its **colour**, which is how the two are kept in step: a note in
`COMMENT` is a remark and floors at `ASIDE_PT`; anything else is content and floors at `CONTENT_PT`. So
the way to make a note bigger is to say what it *is*, not to pass a number.

### `MUTED` is for lines, not letters

`MUTED` measures 3.6:1 on the paper — the only colour in the palette under 4.5:1 — so it is reserved for
`rule()` hairlines, gridlines and dashed ties. Text that used to be muted is `COMMENT` (`#2F5D3A`), which
is 7.5:1. A muted *edge* still draws a grey stroke, but its **label** is set in `COMMENT`, because the
stroke is a guide and the label is text.

### How it works

- **Shapes** are wobbled by an SVG turbulence-displacement filter, matching draw.io's `sketch=1`.
  **Text is deliberately not wobbled** so labels stay legible.
- **Text is outlined to vector paths** with fontTools, so previews are faithful with **no system font
  install**. This is necessary rather than clever: librsvg here ignores `@font-face` data URIs (verified),
  and Caveat/Plex are not installed, so anything else silently falls back to Helvetica.

## `lint_figures.py`

```
python3 tools/lint_figures.py                    # all nine families
python3 tools/lint_figures.py bpmn_hotel paper_flow
```

Measures every centred label against the shape it sits in, and every edge label against every node
rect — including the node the edge *ends at*, which is where a right-angled route usually puts it.
Both checks found real defects during the 2026-09-07 label sweep that were invisible in the source:
`Pay for the Booking` stopped fitting its task box; `room free` landed on the message marker of the
task it labels; `the payment` sat on the boundary bar it crosses.

**Run it after any size or geometry change**, then still look at the PNG. It measures overlap; it does
not have taste.

## `bpmn_hotel.py`

The Day 2 Process Automation figures — the eleven hotel BPMN redraws plus the compensation fragment.

```
python3 tools/bpmn_hotel.py                     # rebuild all 12 into resources/
python3 tools/bpmn_hotel.py bpmn-hotel-guest-pool
python3 tools/bpmn_hotel.py --list
```

**This family breaks two house rules on purpose**, both for the same reason. It is built with
`Diagram(..., sketch=False, font=PLAIN)`:

- **no hand-drawn wobble.** The section opens by putting the delegates' own paper flow beside the same
  flow in BPMN — *"a notation the rest of the industry already reads"*. A wobbly BPMN collapses the
  contrast that slide is built on.
- **labels in Plex Sans, not Caveat.** Same reason. Caveat then reads as *our annotation on top of a
  standard diagram*, which is exactly what the red callouts are.

It keeps the Field Guide palette, so the section still belongs to the deck. **Red is scarcer here than in
the EIP set** — the five workflow-pattern figures are vocabulary and carry none; red is spent only where
the section is arguing something (no token crosses a message flow; a choreography has no owner; one pool
with five lanes does not work).

**Watch the label geometry.** A rotated lane label longer than its lane silently overflows into the next
one — `_rot(..., fit=)` now shrinks it, but the first pass had every lane label stacked on top of its
neighbour. Branch flows want explicit `via` waypoints too: BPMN routes orthogonally, and a bare diagonal
puts the condition label on top of a task box.

> **The draw.io BPMN styles were written without being opened.** There is no drawio CLI here, and the PNG
> is rendered from our own SVG, so it does *not* check them. If a `.drawio` opens with the wrong glyph in
> a circle or a diamond, `Diagram._drawio_bpmn` is the place to look.

## `integration_styles.py`

The four Day 1 §3 figures that replace the 2021 Integration Styles exports (s32–s35).

```
python3 tools/integration_styles.py              # rebuild all four into resources/
python3 tools/integration_styles.py style-rpc
python3 tools/integration_styles.py --list
```

**One stage, four figures.** `_frame()` draws the process boundary down the middle and a dashed container
either side; each figure adds only its own apparatus. The section scores four answers to one question, so
four differently-composed drawings would make a reader re-learn the layout before they could compare
anything. It is `coupling_grids._frame()`'s device, for the same reason.

**How far the boundary rule runs is the figure's call — `_frame(bb=)`.** A 2.6pt ink rule down the middle
strikes through anything centred on `MID`, so the rule stops above the caption that names the apparatus,
and each style crosses the line at a different depth: a file at the arrows' own height, a database below
them, an RPC return path lower still. Nothing is centred on `MID` inside the rule's span.

**Red is the grid.** Three figures red what the two sides agree *about* (the file, the schema, the
message); RPC reds the clock, because it is the only style that also loses on *when*. Its control coupling
rides in carbon on the `PlaceOrder(order)` label instead. Messaging repeats File Transfer's composition on
purpose — the two land in the same cell of `grid-integration-styles`, and the next slide says so.

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

## `flow_reactive.py`

The 25 figures of Day 2 §*Flow and Reactive Programming* — run 2 of the redraw.

```
python3 tools/flow_reactive.py                  # rebuild all 25 into resources/
python3 tools/flow_reactive.py flow-bulkhead
python3 tools/flow_reactive.py --list
```

**The run has two vocabularies and never mixes them, because the section is an argument in two halves.**
Movement B — *how would you build that?*, the wrong answer — is **boxes joined by call arrows**: somebody
is in charge and you can see who, because every arrow starts at a caller. Movements C and D are
**hexagons with ports and dashed-square packets**. A reader who sees a hexagon knows nothing is in
charge; a reader who sees a box knows something is. A *dataflow node* and an *FBP component* are the
**same** glyph on purpose — the outline says FBP is a subclass of dataflow, so drawing them differently
would argue they are different things.

An arc is a plain carbon arrow; a **buffered** arc is run 1's `pipe` with packets in it, because a
bounded buffer is a queue and a reader who met the pipe on Day 1 should not be taught the shape twice.

Conventions carried from the EIP and queue sets: one red idea per figure stated as a red note at the top,
a muted note at the foot for the caveat, and **paired figures contrasting through red** — the class and
the service red the same encapsulated data (*same idea, bigger unit* is the claim); the gateway is red in
*Feature Envy* and its **absence** is red in *Partitioning and Dataflow*; the lookup port reds the pause,
Build Lookup reds the absence of one; backpressure reds a signal going back, load-shedding reds packets
leaving the drawing.

**What only showed up in the PNG.** A leader line aimed at a port crossed the hexagon body, and re-aimed
struck through the port's own label — fixed by reddening the ports instead of annotating them. A
full-size cross over a named component struck through its own name, twice — fixed by putting the name
above the hexagon. The circuit-breaker figure was laid out consumer-first, so its feed arrow ran
backwards through the consumer's label and its outbound call crossed the queue. A pipe's mouth ellipse
sat on a process boundary and swallowed an out-port label. None of it was visible in the source.

## `repatch_steps.py`

```
python3 tools/repatch_steps.py "resources/Pre-Arrival Guest Flow" resources/Arrival
```

Repaints **only the step numbers** of a paper-flow PNG from its `.drawio`. The paper flows are hand-made
draw.io files whose renders draw.io exported, and there is **no drawio CLI here** — so renumbering a step
would otherwise leave the `.png` stale, and the `.png` is what the deck shows.

It finds the blue `#3333FF` glyph clusters in the image, matches each to a numbered cell by position,
paints the old glyph out in white and redraws the new value in **Helvetica** at the same centre, size and
colour. Helvetica is draw.io's default face and librsvg *can* reach it here, so the result is
indistinguishable from an export; if draw.io ever does re-export the file, its output supersedes this and
the two agree.

It refuses to run if the glyph count and the numbered-cell count disagree, rather than guessing.

**Rebuild anything that embeds the render afterwards** — e.g.
`python3 tools/bpmn_hotel.py bpmn-your-flow-side-by-side`.

## `fonts/`

`Caveat.ttf`, `IBMPlexSans-Variable.ttf`, `IBMPlexMono-Regular.ttf` — all **SIL OFL 1.1**, so commercial
training use, PowerPoint embedding and printed handouts are all permitted. From
`github.com/google/fonts`.

These are for the **preview renderer only** and are not installed system-wide.

> **Phase 3 will need them installed**, because PowerPoint cannot use a font that is not on the machine:
> `cp tools/fonts/*.ttf ~/Library/Fonts/`
> Not done — that is a change to Ian's machine and his call. IBM Plex **Serif** is not here yet; add it
> when a diagram needs a serif label, or at the start of Phase 3.
