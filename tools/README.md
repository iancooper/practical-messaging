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

**The rest of BPMN's vocabulary exists too, and only the reference card uses it** — `task` also takes
`marker=` manual / script / rule, `sub="loop"` for the marker on the bottom edge and `double=True` for a
transaction's second border; `event` also takes `symbol=` signal / conditional / escalation / cancel /
parallel, plus `filled=` (a **throwing** event, where the deck's own figures only ever catch) and
`nonint=True` (a **non-interrupting** event, dashed rings); `gateway` also takes `inclusive`, `complex`
and `event`. Reach for these on a legend, not in a flow: a diagram in this deck is built from the six on
`bpmn-the-six`, and using a seventh would be arguing something the section does not.

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

`Diagram._legible()` runs at the top of **both** serialisers and raises every label to **18pt** — one
floor for content and commentary alike, matching the deck's body floor. Pass a smaller `size=` and it
will be raised; pass a larger one and it is kept. It is idempotent, so the `.drawio` and the `.png` can
never disagree about a size.

**The two constants are still separate** (`CONTENT_PT`, `ASIDE_PT`) because they answer different
questions and may part company again; they are simply equal now. Size no longer distinguishes a remark
from a name — **colour does**, which is the whole point of the four text colours.

**⚑ A floor in canvas units is not a legibility guarantee.** The figure is scaled to fit its slide, so
18pt on a 460-unit canvas reads at ~32 real points and the same 18 on a 1200-unit canvas reads at ~13.
At full slide width a label reads at roughly `18 × 890 / w` real points. **Choosing `w` is a legibility
decision**, and a wide figure with a lot in it is the combination to avoid — see `styles.md`.

### `Diagram.compact(target)` — shrink the distances, not the type

```python
d.compact(890)          # in the family's `figure` decorator, not in `main()`
```

Scales the **geometry** until the canvas is `target` wide and leaves every label at the size the floor
gave it, then crops to what is left. What makes a figure wide is *distance* — a long arrow run between a
queue and its consumers — and distance carries no information, so it is the right thing to spend. Boxes
are typically three times wider than their text, so a 20–30% shrink brings the label closer to filling
its box, which is an improvement in itself.

Three things bound the shrink, and each of them earned its place:

- **A shape may not go below its own label.** `flow-fbp-component` stops at 950 rather than 890 because
  its `IP` packet would otherwise be narrower than the word in it.
- **Text does not scale**, so one long line sets a floor on the whole figure. When that binds, `compact`
  **names the offending label on stderr** instead of quietly shrinking the drawing to nothing around it —
  which is what it did to five figures before the guard existed. `flow_reactive.caveat()` now wraps and
  balances its own text for the same reason.
- **`K_FLOOR = 0.55`.** Below that it is not a compaction, it is a mistake.

**`MARKS` are moved but not resized** — a lock, a clock, a tick, a cross. They are marks *about* the
drawing, like text, and shrinking them is the same error as shrinking the labels.

**Call it from the family's `figure` decorator.** Put it in `main()` and `lint_figures.py` measures the
geometry as written rather than as rendered — which happened, and hid a note lying across a hexagon for
as long as the two disagreed.

**Expect to re-nudge some labels afterwards.** `lx` / `ly` are text-space offsets and do not scale, so a
label tuned to clear a line at the old spacing may not clear it at the new one. Ten needed adjusting
across the 36 figures of the first run; lint found every one.

**The floor is per-face, and that is the whole point.** IBM Plex Sans's x-height is `0.516`em against
Caveat's `0.400` (OS/2 `sxHeight`, both at 1000upm), so **14pt of Plex reads across a room as 18pt of
Caveat**. Comparing the two registers by their point numbers is what let the labels drift in the first
place: the BPMN family looked like the worst offender when it was the one family already at the floor.
`_pt(caveat_pt, face)` does the conversion, and `_legible()` sweeps only the hand-drawn register — a BPMN
figure keeps the scale it was drawn at, including the two crowded ones that squeeze a task to 10–11pt.

Edge labels are the one text a figure cannot override, and they were the smallest thing on the slide.
`_edge_pt(e)` puts them at the floor too: **18pt** on a hand-drawn arrow, **14pt** on a BPMN flow.

The floor a note gets still depends on its **colour** — a note in `COMMENT` floors at `ASIDE_PT`,
anything else at `CONTENT_PT` — even though the two numbers are equal today. Keep saying what a note *is*
rather than passing a number: that is what will hold if they diverge again.

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
python3 tools/lint_figures.py                    # all twelve families
python3 tools/lint_figures.py bpmn_hotel paper_flow
```

Six checks, and every one of them was added because something shipped:

| check | what it measures |
|---|---|
| overflow | a centred label wider than the shape it sits in |
| off-canvas | a free `note` running past the canvas edge — the only element whose width is not declared |
| note-on-shape | a note lying **across** a shape's stroke. A note *inside* a shape is a technique, not a defect, so only a straddle is reported |
| collision | an edge label landing on a node rect — including the node the edge *ends at* |
| on-its-line | an edge label across its **own** vertical run. On a horizontal run the label sits above the stroke, which is how the whole deck is drawn; on a vertical run there is no "above" |
| on-a-line | an edge label across **another** arrow's vertical run — the same defect with a different owner |
| on-border | an edge label across a container's border, which is exactly where a label between a box and the apparatus wants to land |

**The last five were added during the 18pt sweep and the compaction, and each found a defect nobody had
gone looking for** — three foot comments off their canvases (one from before the sweep), three arrow
labels on dashed container edges, six labels struck through by a vertical arrow across four families, and
a note lying over a hexagon. Two of those figures were on sheets Ian had already approved.
Both checks found real defects during the 2026-09-07 label sweep that were invisible in the source:
`Pay for the Booking` stopped fitting its task box; `room free` landed on the message marker of the
task it labels; `the payment` sat on the boundary bar it crosses.

**Run it after any size or geometry change**, then still look at the PNG. It measures overlap; it does
not have taste.

## `reads_at.py`

What every label actually reads at **in the room**, on a 16:9 slide. `lint_figures.py` measures labels
against shapes; this measures them against the audience, and nothing else does.

```
python3 tools/reads_at.py                    # every family, worst figure each
python3 tools/reads_at.py --all              # every figure
python3 tools/reads_at.py bpmn_hotel paper_flow
python3 tools/reads_at.py --floor 14
```

    reads_at  =  caveat-equivalent size  x  890 / max(w, 2.2 x h)

**Two corrections, and both of them have caught us out.**

- **x-height, not point size.** Plex Sans and Plex Mono are 0.516em against Caveat's 0.400, so 13pt of
  Plex reads as 17pt of Caveat. A survey that ranks families by the number in `size=` names BPMN as the
  worst offender when it is the only family already at the floor.
- **Aspect, not width.** A 16:9 slide leaves about 2.2:1 of usable area. Wider than that is fitted by
  width; **anything squarer is fitted by height, and the width it was drawn at stops mattering.**

**⚑ Which is why "compacted to 890" is not the same as "reads at 18".** The 2026-09-07 sweep targeted
width alone, and width is half the rule — 65 of 92 figures are still under the floor. Plan §8 item 18 has
the numbers and what a real fix would cost. **Run this before saying a family is done.**

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

**File Transfer and Messaging end on the same four questions**, in the same four columns, with only the
answers changed — *none / you do / nothing says / you decide* against *the channel / the broker / an ack /
poll, or be pushed*. `QUESTIONS` and `_strip()` are module-level so the two cannot drift, because the two
strips being identical bar one row **is** the comparison. That is why Messaging repeating File Transfer's
composition is the point of it rather than a problem with it.

**How far the boundary rule runs is the figure's call — `_frame(bb=)`.** A 2.6pt ink rule down the middle
strikes through anything centred on `MID`, so the rule stops above the caption that names the apparatus,
and each style crosses the line at a different depth: a file at the arrows' own height, a database below
them, an RPC return path lower still. Nothing is centred on `MID` inside the rule's span.

**Red is the grid.** Three figures red what the two sides agree *about* (the file, the schema, the
message); RPC reds the clock, because it is the only style that also loses on *when*. Its control coupling
rides in carbon on the `PlaceOrder(order)` label instead. Messaging repeats File Transfer's composition on
purpose — the two land in the same cell of `grid-integration-styles`, and the next slide says so.

## `app_shapes.py`

The four Day 1 drawings that show an **application** rather than a pattern: §1's process-boundary pair and
§4.3's task-queue pair.

```
python3 tools/app_shapes.py                     # rebuild all four into resources/
python3 tools/app_shapes.py boundary-one-service
python3 tools/app_shapes.py --list
```

**One helper, `service()`** — a dashed container, the application inside it, and the store only it can
reach. The store goes **inside** the container, always: a figure that draws a database outside the process
that owns it has conceded §1's argument before the presenter opens their mouth.

**The boundary vocabulary is borrowed, not invented.** `coupling_grids` draws it as an ink rule across
Myers' scale and `integration_styles._frame()` as a vertical ink rule between two dashed containers, so
the settled reading is **dashed box = a process, ink rule = the boundary**. §1 comes first in the deck, so
these two figures are where the room meets the glyph; §3 then reuses it.

**The §1 pair contrasts through red.** `one-service` reds the reach into private data, and the cross sits
**on the rule** rather than on the database — what refuses the reach is the boundary, and a cross on the
store says only *this database is locked*. `two-services` reds the shared transaction, drawn as a scope,
because that is what a transaction is.

**§4.3 says the opposite thing with the same vocabulary, on purpose.** `task-queue-shape` puts everything
inside **one** container over **one** database, because the slide's callout is *one team, one service, one
queue — robustness without reorganising the company*. Drawing a boundary there would teach the room to cut
a new service every time a request is slow.

**The gaps between the boxes are load-bearing.** Every arrow is labelled, an arrow label is centred on its
own run and does not scale under `compact`, so a 150-unit label needs roughly a 190-unit gap or
`lint_figures.py` reports it sitting on the box it leaves. That is what set the x positions.

## `conversations.py`

§Conversations' one drawn figure — `conversation-timeout`, for *In-Out — When Nothing Comes Back at All*.

```
python3 tools/conversations.py
```

**A family of one, and it should not stay that way.** That section still carries three 2021 pictures —
`Practical Messaging - Day 2 - 2024 - 25/27/29.png` — which are whole exported slides, old titles, red
commentary boxes and a footer included. They are *linked*, so they do not appear as work outstanding, and
they are the last three pictures on Day 1 that are not ours. **This module is where their redraws would
go.** It is an offer, not a decision taken.

**Time runs down the page**, which is a vocabulary choice and not a register one: everything is hand-drawn
Caveat like the rest of Day 1, and what is new is that vertical position means *when*. The lifelines are
`MUTED` 1.1pt hairlines — guides, which is what muted is for — and deliberately nothing like the 2.6pt ink
rule §1 and §3 use for a boundary.

## `eip_figures.py`

Day 1's pattern figures — the 12 that replaced the Hohpe & Woolf illustrations in `outlines/DayOne.md`,
plus `eip-the-big-picture`, §4's opener. One script, so the set stays a family: same label voice, same
convention for what red means.

**Eight more were added for the routing handout** (plan §10) and they are in this family rather than one
of their own, because `eip-content-enricher` — the ninth pattern of that set and the one that stayed on
Day 1 — is already here. **They go in `handouts/Routing-Patterns.md`, not on a slide**, so `reads_at`'s
question is the wrong one for them; they were held to the floor anyway (18.0–24.3) rather than given a
print exemption, because a figure that reads across a room also reads on paper and the exemption would
have to be defended per figure.

**The three routers contrast through red**, and it is the sub-set's whole argument: all three answer
*who decides where this message goes*, and the red says who — Content Based Router reds the **router**,
Dynamic Router the **control channel**, Recipient List the **list on the message**. Splitter and
Aggregator pair the same way and carry the same three parts across both figures.

**The opener is the odd one out and knows it.** The twelve are 460–600 units wide and already read at
27–35 real points, so they are not compacted; the map is denser, so it calls `.compact(890)` itself, at
the end of its own builder rather than in `figure()` — which keeps the linter and the renderer looking at
the same geometry. It is a *composition over this family's vocabulary*: domain code, a gateway, a channel,
an endpoint with a pump, all of them drawn elsewhere in the twelve. It must not invent a shape the section
never picks up again, which is why the 2021 marker's *channel adapter* is not on it.

**It also carries §4's build order, as a list rather than a strip of columns.** Text does not scale when
`compact` runs, so five columns inside 890 units leaves 178 units each and the shortest of the five
questions is wider than that. The list is not a compromise; it is the only shape that fits the floor.

```
python3 tools/eip_figures.py                    # rebuild all 21 into resources/
python3 tools/eip_figures.py eip-dead-letter-channel   # just one
python3 tools/eip_figures.py --list
```

**Read the renders before believing them.** The first pass had a missing arrow and four labels sitting on
top of strokes; none of it was visible in the source. Every figure was eyeballed as a PNG and fixed.

Conventions held across the set, and worth holding for the next batch:

- **one red idea per figure**, stated as a red note at the top — the sentence the presenter says out loud
- **a name is ink and a remark is `COMMENT` green.** This list used to say a *muted* note names the
  pattern element; that was the defect rather than the convention and it cost two review rounds —
  `MUTED` is for lines, not letters. A bottom note in `COMMENT` still carries the caveat
- **paired figures contrast through red**: *Polling Consumer* reds `receive()`, *Event-Driven Consumer*
  reds the push; *Invalid Message* diverts from the **receiver**, *Dead Letter* diverts from the
  **channel** — which is the distinction the two slides keep getting confused about

## `asyncapi_figures.py`

One figure, `asyncapi-virtuous-cycle`, for the *Managing Asynchronous APIs* handout. **A twelfth
family rather than a thirteenth `eip_figures` entry**, because that module is the twenty-one Hohpe &
Woolf replacements and a virtuous cycle is neither a pattern of theirs nor a slide of ours.

**Handout figures do not `compact()`** — the same as the eight routing figures at the end of
`eip_figures.py`. They are not fitted to a slide stage.

**⚑ And a handout figure's size is set by its canvas WIDTH alone.** `handouts/print.css` fits a
figure to the 154mm text block, so **printed letter size is `154 / w`** — a 560-unit canvas gives an
18pt label about 14 printed points, and an 852-unit canvas gives it 9. `reads_at.py` will pass both,
because it measures against a projector and not against paper. Take the width from **measured
advances** rather than from the eye:

```python
from diagram import _Outliner, HAND
_Outliner.outline("Provisioning", HAND, 18, 0, 0)[1]      # -> 72.3 units
```

Every guess behind this figure's first draft was 30–50% high, and the drawing was 292 units wider
than its content needed as a result.

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

## `reference_cards.py`

The two **delegate reference cards** — one A4 side per pack. Plan §8 item 8.

```
python3 tools/reference_cards.py            # rebuild both into resources/
python3 tools/reference_cards.py --list
```

| figure | pack | carries |
|---|---|---|
| `card-bpmn-reference` | Day 2 | 8 task types + loop and transaction, 9 event triggers + a key to the rings, 5 gateways |
| `card-integration-options` | Day 1 | Myers' scale with the boundary across it, *Must We Both Be Up?*, the four styles scored, and 11 products |

**These are print, not slides,** which is the only reason this family looks different from the others.

- **No `compact()` and no entry in `reads_at.py`.** Everything else is fitted to a 16:9 stage and its
  labels sized for a room; these are held at arm's length. The canvas is A4's own 1 : 1.414 —
  800 × 1131, which is 2400 × 3393 at scale 3, about 290 dpi on the page. `lint_figures.py` still
  applies, and is run as `python3 tools/lint_figures.py reference_cards`.
- **Plex Sans in both, including the Day 1 one.** `styles.md` reserves Caveat for callouts and diagram
  labels; a lookup table is neither, and setting *gRPC* or *AMQP 0-9-1* in a hand face makes another
  company's product name read as our remark about it.
- **Mono-safe.** Each card spends its one red idea on a mark as well as a colour — the six BPMN elements
  the deck uses carry a **red dot**, not just red type — because a venue's printer is not ours to choose.

**The BPMN card is why `diagram.py` grew fifteen BPMN glyphs.** `bpmn-the-six`'s foot says *"every other
task type, event and gateway is on the reference card in your pack"*, so a card carrying only the six
would have made that figure lie. The additions are `manual` / `script` / `rule` task markers, `task(sub=)`
for the loop marker and `task(double=)` for a transaction, the `signal` / `conditional` / `escalation` /
`cancel` / `parallel` event symbols, `event(filled=)` and `event(nonint=)` for throwing and
non-interrupting rings, and the `inclusive` / `complex` / `event` gateways. All additive: the other eleven
families rebuild byte-identical.

**The three `.drawio` sources have no text in them at all** — `Task Types.drawio`, `Event Types.drawio`
and `Gateway Types.drawio` are unlabelled icon sheets, every `value=""`. The element *set* came from
them; every word came from the outline. Checked before it was reported, per rule 4.

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
