#!/usr/bin/env python3
"""Day 1 §3 *Integration Styles* -- the four styles, one drawing each.

    python3 tools/integration_styles.py               # rebuild all four
    python3 tools/integration_styles.py style-messaging
    python3 tools/integration_styles.py --list

**Why they are one script, and why they share a frame.** The section does not compare
four mechanisms, it scores four answers to the same question -- *what does this hand
back of what the process boundary bought you?* -- and then plots all four on §2's grid
(`grid-integration-styles`). So the four figures are the same stage set every time:
the boundary down the middle, a process either side of it, and the style's own
apparatus straddling the line. `_frame()` draws the stage; each figure only puts its
own mechanism on it. Change the frame and all four move together, exactly as
`coupling_grids._frame()` keeps the three plots of one grid in step.

**The boundary is drawn, not implied.** §2 ends on `coupling-scale-boundary`, where a
line across Myers' scale takes Content and Common coupling off the table. This is the
same line, turned on its side because these two processes sit side by side, and it is
what makes Shared Database's figure an argument rather than an illustration: its
apparatus is the only one that a *reader* on the far side reaches through.
**Ian confirmed it stays on all four, 2026-09-07.**

**How far the line runs is the figure's decision, not the frame's** -- `_frame(bb=)`.
Each style crosses the boundary at a different depth (a file at the middle, a database
below it, an RPC return path lower still), and the line has to reach what crosses it
and stop before the caption that names it. Nothing is centred on `MID` inside the
line's span; a 2.6pt ink rule through a label is exactly the defect the legibility pass
was about.

**The reds are the grid.** Three figures red what the two parties agree *about* -- the
file, the schema, the message -- and one reds *when* they must both be up. That is the
two axes, in the order the section meets them, and it is why the RPC figure spends its
red on the wait and leaves the call in carbon.

**File Transfer and Messaging share a strip, and that is the point of them.** Ian,
2026-09-07: *"Messaging repeats File Transfer's composition, but the fix is asking what
does the locking, partitioning etc."* Both figures end on the **same four questions** in
the same four columns; only the answers change, from *you* to the broker. That is the
"out of the box" idea drawn rather than asserted, and it takes back information the 2021
exports carried in their blue commentary boxes and the rewrite had dropped. It also
makes the repeated composition deliberate: two slides that look alike with one row of
words different is a comparison; two slides that look alike for no reason is a mistake.

The four questions are *Why Messaging*'s own list -- ordering, locking and competing
consumers, delivery guarantees, granularity and timeliness. These figures **pose** them;
that slide scores them and states the verdict. Posing a question two slides before
answering it is a setup, and File Transfer's own text asks for exactly that: *"Hold that
thought -- the last slide of this section is about everything you did not get with it."*

**Canvas width is a legibility decision here, not a layout one.** The label floor is in
canvas units, so what it means on a slide depends entirely on how wide the canvas is: a
460-unit EIP figure's 18pt reads across a room at about 32 real points, and the same 18
on a 1200-unit canvas reads at 13. These were 1200 and are now **1000**, which is what
took their commentary from roughly 12 real points to 16. Aspect matters as much as
width -- a figure wider than about 2.2:1 is fitted by width on a 16:9 slide, and
anything squarer is fitted by height, which shrinks every label in it again.

These replace the 2021 exports (s32-s35), which each carried three paragraphs of blue
commentary because the slides underneath them were bare. The rewritten slides carry the
argument as bullets, so the figures do not repeat it -- what they keep is the part a
picture says better than a line of text.

Hand-drawn register, like the rest of Day 1.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, COMMENT, MUTED, INK      # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
FIGURES = {}

# the shared stage
W, MID = 1000, 500
GT, GH = 124, 176                 # every process container, top and height
BOX_Y, BOX_H = 170, 88            # every application box -- so all four line up
BT = 108                          # where the boundary line starts

# The four questions a file leaves you and a broker answers, in one order, used by two
# figures. They live here rather than in each figure so the two strips cannot drift
# apart -- and the two strips being identical bar one row IS the comparison.
QUESTIONS = ("in what order?", "who locks it?", "did it land?", "when do I look?")
COL_X = (170, 390, 610, 830)


# Every figure in this run is compacted to this width before it is written. The label
# floor is in canvas units and the figure is scaled to fit its slide, so a wide canvas
# is not more detail -- it is smaller type in the room. 890 is where the 18pt diagram
# floor meets the deck's 18pt body floor at full slide width. `Diagram.compact` shrinks
# the distances and leaves the type alone; see its docstring.
TARGET_W = 890


def figure(name):
    """Register a figure -- and compact it on the way out.

    **The compaction belongs here, not in `main()`.** Put it in `main()` and
    `lint_figures.py` measures the geometry as it was written rather than as it is
    rendered, and a label sitting on a stroke stays invisible for as long as the two
    disagree. One definition, and everything downstream sees the same drawing.
    """
    def wrap(fn):
        def build():
            return fn().compact(TARGET_W)
        build.__doc__ = fn.__doc__
        build.__name__ = fn.__name__
        FIGURES[name] = build
        return fn
    return wrap


def _frame(title, idea, bb, h=470, lg=(40, 390), rg=(570, 390),
           left="producer process", right="consumer process"):
    """The stage: the red idea, the boundary down to `bb`, and a container per side.

    `lg` / `rg` are (x, width) -- RPC needs narrower containers, because it is the one
    style with two boxes a side and an arrow label that has to sit clear of the line.
    """
    d = Diagram(title, w=W, h=h)
    d.note(MID, 44, idea, ANNOTATION, 21)
    d.note(MID, 100, "the process boundary", INK, 18)
    d.rule(MID, BT, 0, INK, 2.6, h=bb - BT)
    d.group(lg[0], GT, lg[1], GH, left)
    d.group(rg[0], GT, rg[1], GH, right)
    return d


def _strip(d, y, header, answers):
    """The four questions, and who answers them. Identical geometry both times, so the
    answers are the only thing a reader has to compare."""
    d.note(MID, y, header, COMMENT, 18)
    d.rule(60, y + 22, 880, MUTED, 1.1)
    for x, q, a in zip(COL_X, QUESTIONS, answers):
        d.note(x, y + 52, q, COMMENT, 18)
        d.note(x, y + 84, a, INK, 18)


@figure("style-file-transfer")
def file_transfer():
    """*File Transfer.* One file across the boundary, and the whole agreement is what
    is in it and where it lives. Red is on the file because the slide's claim is that
    the file **is** the contract -- and the strip underneath is that claim's other half,
    *nothing else is agreed*, made countable."""
    d = _frame("File Transfer",
               "the file is the contract — its format and where it lives, "
               "and nothing else is agreed", bb=270, h=570,
               lg=(40, 390), rg=(570, 390))

    src = d.box(70, BOX_Y, 240, BOX_H, "Application")
    dst = d.box(690, BOX_Y, 240, BOX_H, "Application")
    # a sheet on the line, centred on the arrows' own height so they stay level. It has
    # a PAPER fill, so the rule disappears behind it and comes out below -- which is the
    # reading: the file is the only thing that crosses
    f = d.doc(464, 158, 72, 112, accent=True)

    # `lx` is text-space and does NOT scale with `compact`, so these are post-compaction
    # units: each label steps off the container's dashed edge and sits inside its own
    # process, which is also what it means -- writing is the producer's act.
    d.arrow(src, f, "writes it", sides=("r", "l"), ly=-8, lx=-6)
    d.arrow(f, dst, "reads it", sides=("r", "l"), ly=-8, lx=6)
    # "later" moved off the arrow and into the caption: at 18pt it was long enough to
    # land on the consumer container's border, and it says more here anyway
    d.note(MID, 322, "a file, in a directory both can reach — "
                     "it waits there until somebody comes for it", INK, 18)

    _strip(d, 380, "and every one of these is yours to write",
           ("none", "you do", "nothing says", "you decide"))

    d.note(MID, 542, "a file is a message: a batch of them, in a channel that happens "
                     "to be a filesystem", COMMENT, 18)
    return d


@figure("style-shared-database")
def shared_database():
    """*Shared Database.* The one figure where something on the far side of the boundary
    is reached *through*: two ORMs on one schema, and neither process owns it. Red is on
    the schema rather than on the reach, because the slide's verdict is about ownership
    -- the change propagates whether the reader wanted it or not.

    No strip. The four questions are about a channel, and this style does not have one;
    its problem sits upstream of them.
    """
    d = _frame("Shared Database",
               "nobody owns the schema — a change reaches every reader "
               "whether they wanted it or not", bb=428, h=570)

    d.box(62, BOX_Y, 200, BOX_H, "Application")
    orm_w = d.box(282, BOX_Y, 80, BOX_H, "ORM")
    orm_r = d.box(638, BOX_Y, 80, BOX_H, "ORM")
    d.box(738, BOX_Y, 200, BOX_H, "Application")
    db = d.cylinder(436, 336, 128, 92, accent=True)

    d.arrow(orm_w, db, "writes", sides=("b", "l"), via=[(322, 382)], ly=-8)
    # the extra waypoint is not geometry, it is where the label lands: _mid takes the
    # middle SEGMENT, so without it "reads" sits on the vertical run and the pair stops
    # being a mirror of itself
    d.arrow(db, orm_r, "reads", sides=("r", "b"), via=[(564, 382), (678, 382)], ly=-8)
    d.note(MID, 466, "one schema", INK, 18)

    d.note(MID, 508, "not temporally coupled — neither has to be up when the other is. "
                     "what couples them is the shared mutable schema", COMMENT, 18)
    d.note(MID, 542, "and that is the boundary itself, handed back: you are agreeing "
                     "release dates across teams again", COMMENT, 18)
    return d


@figure("style-rpc")
def rpc():
    """*Remote Procedure Call.* The only figure that spends its red on the clock rather
    than on the thing agreed, because RPC is the only style that loses on the *second*
    axis -- and a room that writes HTTP all day already knows what a call looks like, so
    the drawing spends itself on the waiting instead.

    The control half is carried where it actually lives: the arrow's label is an
    operation name rather than data, and the comment underneath says so.
    """
    d = _frame("Remote Procedure Call",
               "the only style that loses on both axes at once — you say what to do, "
               "and you wait while it is done", bb=350, h=480,
               lg=(40, 300), rg=(660, 300),
               left="client process", right="server process")

    d.box(58, BOX_Y, 180, BOX_H, "Application")
    stub = d.box(256, BOX_Y, 72, BOX_H, "Stub")
    proxy = d.box(672, BOX_Y, 72, BOX_H, "Proxy")
    d.box(762, BOX_Y, 180, BOX_H, "Application")

    # Both labels are pushed off MID, because the boundary rule runs through it. The
    # offsets are text-space and do not scale, so every time `compact` gets a harder
    # target this label closes on the Stub it starts from: -94 was right on a
    # 1000-unit canvas, -75 on an 890-unit one, and -60 once the target became the
    # *effective* width and the stage came in at 778. It has to clear two things, the
    # Stub on its left and the client container's dashed edge, and it now sits between
    # them. **Re-measure it after any change to `TARGET_W`** -- this is the one label
    # in the family that has moved every single time.
    d.arrow(stub, proxy, "PlaceOrder(order)", lx=-60, ly=-8)
    d.arrow(proxy, stub, "the result", sides=("b", "b"),
            via=[(708, 336), (292, 336)], lx=98)

    d.icon(292, 142, "clock", accent=True, r=14)
    d.note(292, 106, "blocked until it comes back", ANNOTATION, 18)

    d.note(MID, 406, "an operation name, not data — you are telling the other side what "
                     "to do, which is control coupling", COMMENT, 18)
    d.note(MID, 440, "and both must be up at the same moment, so an outage here is not "
                     "a delay, it is a failure", COMMENT, 18)
    return d


@figure("style-messaging")
def messaging():
    """*Messaging.* Deliberately File Transfer's composition again, because the two land
    in the same cell of the grid and the figure should not pretend otherwise. The strip
    is what makes the repetition an argument: **the same four questions, already
    answered.** Everything the broker does for you is something a directory would have
    left you to write.

    The three coupling glosses that stood here -- *a command is control coupled*, and so
    on -- came out to make room. They restated the slide's own bullets word for word,
    which is the failure the 2021 exports were full of, and `grid-integration-styles`
    already makes that point better by drawing Messaging as a span rather than a point.
    The strip is information the deck has nowhere else.

    The red envelope is the one centred on the boundary, so the message is literally what
    crosses.
    """
    d = _frame("Messaging",
               "the coupling is a decision here, not a property of the style — "
               "it is whatever you put in the message", bb=270, h=570,
               lg=(40, 380), rg=(580, 380))

    # the same two boxes in the same places as File Transfer, on purpose
    src = d.box(70, BOX_Y, 240, BOX_H, "Application")
    dst = d.box(690, BOX_Y, 240, BOX_H, "Application")
    pipe = d.pipe(440, 186, 120, 56)
    for x in (449, 487, 525):
        d.msg(x, 200, w=26, h=20, accent=(x == 487))

    # short labels, because the pipe's mouth ellipse reaches 19 units back from its left
    # edge and a longer one lands in it
    d.arrow(src, pipe, "writes it", sides=("r", "l"), ly=-8, lx=-6)
    d.arrow(pipe, dst, "reads it", sides=("r", "l"), ly=-8, lx=6)
    d.note(MID, 322, "a channel", INK, 18)

    _strip(d, 380, "the same four questions — and the broker has answered them",
           ("the channel", "the broker", "an ack", "poll, or be pushed"))

    d.note(MID, 542, "the other three styles fix where you sit on the coupled-about "
                     "axis; this is the one that leaves it open", COMMENT, 18)
    return d


def main(argv):
    if "--list" in argv:
        for n in FIGURES:
            print(n)
        return 0
    only = [a for a in argv if not a.startswith("--")]
    for name, fn in FIGURES.items():
        if only and name not in only:
            continue
        dg = fn()
        _, png = dg.save(os.path.join(OUT, name))
        print(f"  {name:<28} {dg.w}x{dg.h}  {os.path.getsize(png):>8,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
