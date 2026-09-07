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

These replace the 2021 exports (s32-s35), which each carried three paragraphs of blue
commentary because the slides underneath them were bare. The rewritten slides carry
that prose as bullets, so the figures do not repeat it.

Hand-drawn register, like the rest of Day 1.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, COMMENT, INK      # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
FIGURES = {}

# the shared stage
W, MID = 1200, 600
GT, GH = 140, 190                 # every process container, top and height
BOX_Y, BOX_H = 196, 88            # every application box -- so all four line up
BT = 128                          # where the boundary line starts


def figure(name):
    def wrap(fn):
        FIGURES[name] = fn
        return fn
    return wrap


def _frame(title, idea, bb, h=530, lg=(60, 400), rg=(740, 400),
           left="producer process", right="consumer process"):
    """The stage: the red idea, the boundary down to `bb`, and a container per side.

    `lg` / `rg` are (x, width) -- RPC needs narrower containers, because it is the one
    style with two boxes a side and an arrow label that has to sit clear of the line.
    """
    d = Diagram(title, w=W, h=h)
    d.note(MID, 48, idea, ANNOTATION, 19)
    d.note(MID, 112, "the process boundary", INK, 16)
    d.rule(MID, BT, 0, INK, 2.6, h=bb - BT)
    d.group(lg[0], GT, lg[1], GH, left)
    d.group(rg[0], GT, rg[1], GH, right)
    return d


@figure("style-file-transfer")
def file_transfer():
    """*File Transfer.* One file across the boundary, and the whole agreement is what
    is in it and where it lives. Red is on the file because the slide's claim is that
    the file **is** the contract -- and the second comment is the slide's own *hold
    that thought*, which the section cashes two slides later on *Why Messaging*."""
    d = _frame("File Transfer",
               "the file is the contract — its format and where it lives, "
               "and nothing else is agreed", bb=336, h=520)

    src = d.box(110, BOX_Y, 280, BOX_H, "Application")
    dst = d.box(810, BOX_Y, 280, BOX_H, "Application")
    # a sheet on the line, centred on the arrows' own height so they stay level. It
    # has a PAPER fill, so the rule disappears behind it and comes out below -- which
    # is the reading: the file is the only thing that crosses
    f = d.doc(556, 184, 88, 112, accent=True)

    d.arrow(src, f, "writes it", sides=("r", "l"), ly=-7)
    d.arrow(f, dst, "reads it, later", sides=("r", "l"), ly=-7)
    d.note(MID, 372, "a file, in a directory both can reach", INK, 17)

    d.note(MID, 432, "nobody has to be up at the same time — the file waits in the "
                     "directory until somebody comes for it", COMMENT, 16)
    d.note(MID, 472, "and a file is a message: a batch of them, in a channel that "
                     "happens to be a filesystem", COMMENT, 16)
    return d


@figure("style-shared-database")
def shared_database():
    """*Shared Database.* The one figure where something on the far side of the
    boundary is reached *through*: two ORMs on one schema, and neither process owns
    it. Red is on the schema rather than on the reach, because the slide's verdict is
    about ownership -- the change propagates whether the reader wanted it or not."""
    d = _frame("Shared Database",
               "nobody owns the schema — a change reaches every reader "
               "whether they wanted it or not", bb=448, h=610)

    d.box(100, BOX_Y, 212, BOX_H, "Application")
    orm_w = d.box(332, BOX_Y, 78, BOX_H, "ORM")
    orm_r = d.box(790, BOX_Y, 78, BOX_H, "ORM")
    d.box(888, BOX_Y, 212, BOX_H, "Application")
    db = d.cylinder(536, 352, 128, 96, accent=True)

    d.arrow(orm_w, db, "writes", sides=("b", "l"), via=[(371, 400)], ly=-8)
    # the extra waypoint is not geometry, it is where the label lands: _mid takes the
    # middle SEGMENT, so without it "reads" sits on the vertical run and the pair
    # stops being a mirror of itself
    d.arrow(db, orm_r, "reads", sides=("r", "b"), via=[(664, 400), (829, 400)], ly=-8)
    d.note(MID, 486, "one schema", INK, 17)

    d.note(MID, 534, "not temporally coupled — neither has to be up when the other "
                     "is. what couples them is the shared mutable schema", COMMENT, 16)
    d.note(MID, 574, "and that is the boundary itself, handed back: you are agreeing "
                     "release dates across teams again", COMMENT, 16)
    return d


@figure("style-rpc")
def rpc():
    """*Remote Procedure Call.* The only figure that spends its red on the clock
    rather than on the thing agreed, because RPC is the only style that loses on the
    *second* axis -- and a room that writes HTTP all day already knows what a call
    looks like, so the drawing spends itself on the waiting instead.

    The control half is carried where it actually lives: the arrow's label is an
    operation name rather than data, and the comment underneath says so.
    """
    d = _frame("Remote Procedure Call",
               "the only style that loses on both axes at once — you say what to do, "
               "and you wait while it is done", bb=380, h=510,
               lg=(60, 340), rg=(800, 340),
               left="client process", right="server process")

    d.box(86, BOX_Y, 200, BOX_H, "Application")
    stub = d.box(306, BOX_Y, 78, BOX_H, "Stub")
    proxy = d.box(816, BOX_Y, 78, BOX_H, "Proxy")
    d.box(914, BOX_Y, 200, BOX_H, "Application")

    # both labels are pushed off MID, because the boundary rule runs through it
    d.arrow(stub, proxy, "PlaceOrder(order)", lx=-104, ly=-7)
    d.arrow(proxy, stub, "the result", sides=("b", "b"),
            via=[(855, 356), (345, 356)], lx=112)

    d.icon(345, 168, "clock", accent=True, r=15)
    d.note(345, 128, "blocked until it comes back", ANNOTATION, 17)

    d.note(MID, 424, "an operation name, not data — you are telling the other side "
                     "what to do, which is control coupling", COMMENT, 16)
    d.note(MID, 464, "and both must be up at the same moment, so an outage here is "
                     "not a delay, it is a failure", COMMENT, 16)
    return d


@figure("style-messaging")
def messaging():
    """*Messaging.* Deliberately the same shape as File Transfer, because the two land
    in the same cell of the grid and the figure should not pretend otherwise. What
    differs is that the thing crossing the boundary has a choice in it -- which is what
    the red note says and what the three lines under the channel spell out, and it is
    the only style where that is true.

    The red envelope is the one centred on the boundary, so the message is literally
    what crosses.
    """
    d = _frame("Messaging",
               "the coupling is a decision here, not a property of the style — "
               "it is whatever you put in the message", bb=296)

    # the same two boxes in the same places as File Transfer, on purpose
    src = d.box(110, BOX_Y, 280, BOX_H, "Application")
    dst = d.box(810, BOX_Y, 280, BOX_H, "Application")
    pipe = d.pipe(530, 208, 140, 64)
    for x in (546, 586, 626):
        d.msg(x, 226, w=28, h=20, accent=(x == 586))

    # short labels, because the pipe's mouth ellipse reaches 21 units back from its
    # left edge and a longer one lands in it
    d.arrow(src, pipe, "writes it", sides=("r", "l"), ly=-7)
    d.arrow(pipe, dst, "reads it", sides=("r", "l"), ly=-7)
    d.note(MID, 322, "a channel", INK, 17)

    # two columns either side of the rule -- which is why they read as a list and not
    # as a caption, and why nothing has to sit on the boundary to say it
    for y, what, kind in ((372, "a command", "control coupled"),
                          (404, "a whole-entity event", "stamp coupled"),
                          (436, "only what the receiver needs", "data coupled")):
        d.note(MID - 24, y, what, INK, 17, anchor="end")
        d.note(MID + 24, y, kind, INK, 17, anchor="start")

    d.note(MID, 494, "the other three styles fix where you sit on the "
                     "coupled-about axis; this is the one that leaves it open",
           COMMENT, 16)
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
