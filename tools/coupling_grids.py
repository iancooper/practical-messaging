#!/usr/bin/env python3
"""Day 1's conceptual grids -- the coupling scale, and the two-axis grid that carries
the argument of the day.

    python3 tools/coupling_grids.py                 # rebuild all
    python3 tools/coupling_grids.py grid-coupling
    python3 tools/coupling_grids.py --list

**Why these are one script.** Three of the five are *the same grid*, plotted three
times: §2 introduces it with four coupling examples, §3 lands the four integration
styles on it, §5 lands the four exchange patterns. The outline is explicit that this
must be one drawing -- *"reuse the same grid artwork so the call-back is visual, not
just verbal"* -- and its presenter note says delegates should be able to draw it from
memory by the end of the day. `_frame()` therefore draws the axes once and the three
figures differ only in what is plotted on them. If the frame is edited, all three
move together, which is the point.

**These were `Ian to draw` and are not any more.** The recorded reason was that they
are *arguments rather than illustrations*. That was written before the tooling had
drawn anything; thirty-seven figures later it does not hold, since `bpmn-elements`,
the guest cycle and Departure are all arguments too. What is true is that they are
conceptual enough to want a hard review, which is a different thing from being
undrawable.

Hand-drawn register, like the rest of Day 1.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, COMMENT, MUTED, INK, CARBON      # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
FIGURES = {}

# the shared frame. Five coupling columns, two temporal bands.
L, R, T, MID, B = 260, 980, 150, 320, 490
COLS = ("Content", "Common", "Control", "Stamp", "Data")
STEP = (R - L) / len(COLS)
X = {name: L + STEP / 2 + i * STEP for i, name in enumerate(COLS)}


# Every figure in this script is compacted to this width before it is written. The
# label floor is in canvas units and the figure is scaled to fit its slide, so a wide
# canvas is not more detail -- it is smaller type in the room. 890 is where the 18pt
# diagram floor meets the deck's 18pt body floor at full slide width. `Diagram.compact`
# shrinks the distances and leaves the type alone; see its docstring.
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


def _frame(title_note):
    """The two axes, drawn identically every time. Nothing is plotted here."""
    d = Diagram(title_note, w=1060, h=640)

    # the plot area
    d.rule(L, T, R - L)
    d.rule(L, B, R - L)
    d.rule(L, T, 0, h=B - T)
    d.rule(R, T, 0, h=B - T)
    for i in range(1, len(COLS)):
        d.rule(L + i * STEP, T, 0, MUTED, 0.7, h=B - T)

    # the line that matters: must we both be up?
    d.rule(L, MID, R - L, INK, 2.4)

    # y axis -- named to the left, because the bands are the answer, not a scale
    d.note(238, 126, "must we both be up?", INK, 16, anchor="end")
    d.note(238, 218, "no —\nboth can be down", INK, 14, anchor="end")
    d.note(238, 392, "yes —\nboth must be up", INK, 14, anchor="end")

    # x axis
    for name in COLS:
        d.note(X[name], B + 26, name, INK, 15)
    d.note(X["Content"], B + 50, "tightest", INK, 13)
    d.note(X["Data"], B + 50, "loosest", INK, 13)
    d.note(620, B + 88, "what are we coupled about?", INK, 16)
    return d


@figure("grid-coupling")
def grid_coupling():
    """§2 *Two Axes, Not One Scale* -- the grid's first appearance, and the four
    examples the slide names. The red line is the slide's own callout."""
    d = _frame("Two Axes, Not One Scale")
    d.note(530, 48, "“loosely coupled” is a question with two answers", ANNOTATION, 19)

    d.point(X["Common"], 208, "a shared database")
    d.point(X["Stamp"], 208, "an event carrying\na whole entity")
    # 268 put the second line's descenders through the "must we both be up?" rule
    # once the frame was compacted -- it was a unit clear at 1060 and is not at 890.
    # Where a point sits *within* a band carries nothing, so the fix is to raise it.
    d.point(X["Control"], 248, "a command message\nwith a what-to-do flag")
    # wrapped, because at 890 one line of it reached the Data column's own border
    d.point(X["Data"], 398, "gRPC with\na flat DTO")
    return d


@figure("grid-integration-styles")
def grid_integration_styles():
    """§3 *Integration Styles* -- the same frame, the four styles on it. Messaging is
    a **span**, not a point, because the table's entry for it is *your choice*; that
    is the whole reason the section ends on messaging rather than on file transfer,
    which lands in the same cell and cannot move out of it."""
    d = _frame("The Four Integration Styles, on the Same Grid")
    d.note(530, 48, "file transfer and messaging land in the same cell — "
                    "only one of them can move", ANNOTATION, 19)

    d.point(X["Common"], 208, "Shared Database")
    d.point(X["Data"], 208, "File Transfer")
    d.point(X["Control"], 398, "Remote Procedure Call")

    span_l, span_r = X["Control"] - 26, X["Data"] + 34
    d.rule(span_l, 292, span_r - span_l, ANNOTATION, 3.0)
    d.rule(span_l, 284, 0, ANNOTATION, 3.0, h=16)
    d.rule(span_r, 284, 0, ANNOTATION, 3.0, h=16)
    d.note((span_l + span_r) / 2, 274, "Messaging — your choice", ANNOTATION, 15)
    return d


@figure("grid-exchange-patterns")
def grid_exchange_patterns():
    """§5 *Choosing an Exchange Pattern* -- the grid's third and last appearance. Four
    patterns sit above the line and one below it, which is the slide's argument: you
    pay temporal coupling only when you block, and only Blocking In-Out blocks."""
    d = _frame("The Five Exchange Patterns, on the Same Grid")
    d.note(530, 48, "only Blocking In-Out sits below the line — "
                    "every other pattern lets both sides be down", ANNOTATION, 19)

    d.point(X["Data"], 208, "Out-Only")
    for y, name in ((188, "In-Only"), (240, "In-Out"), (292, "Out-In")):
        d.point(X["Control"], y, "")
        d.note(X["Control"] + 20, y + 5, name, INK, 15, anchor="start")

    d.point(X["Control"], 398, "", accent=True)
    d.note(X["Control"] + 20, 403, "Blocking In-Out", ANNOTATION, 16, anchor="start")
    return d


@figure("grid-exchange-2x2")
def grid_exchange_2x2():
    """§5 *The Four Exchange Patterns* -- a different drawing from the three above,
    and deliberately so: this one is a definition, not a plot. Two questions, four
    answers, nothing else on it.

    The red is spent on *In and Out are named from the provider's side*, because that
    is the one thing the room gets backwards -- the axis labels are useless to anyone
    who has the direction the wrong way round.
    """
    d = Diagram("The Four Exchange Patterns", w=1000, h=560)
    d.note(500, 48, "In and Out are named from the provider's side — "
                    "In = a message arrives, Out = a message leaves", ANNOTATION, 19)

    CL, CT, CW, CH = 300, 150, 320, 150
    for r, (row, rgloss) in enumerate((("In", "the requestor speaks first"),
                                       ("Out", "the provider speaks first"))):
        d.note(280, CT + r * CH + 64, row, ANNOTATION, 22, anchor="end")
        d.note(280, CT + r * CH + 92, rgloss, INK, 13, anchor="end")
    for c, col in enumerate(("no message back", "a message back")):
        d.note(CL + c * CW + CW / 2, CT - 20, col, INK, 16)

    cells = ((("In-Only", "fire and forget"), ("In-Out", "request-reaction")),
             (("Out-Only", "notification"), ("Out-In", "solicit-response")))
    for r, row in enumerate(cells):
        for c, (name, gloss) in enumerate(row):
            x, y = CL + c * CW, CT + r * CH
            d.box(x, y, CW - 20, CH - 20, "")
            d.note(x + (CW - 20) / 2, y + 60, name, INK, 21)
            d.note(x + (CW - 20) / 2, y + 90, gloss, INK, 14)

    d.note(610, 498, "everything else in this section is one of these four, "
                     "or a composition of them", COMMENT, 15)
    return d


@figure("coupling-scale-boundary")
def coupling_scale_boundary():
    """§2's pivot, and item 7a. Myers' scale drawn **vertically**, tightest at the
    top, with the process boundary as a horizontal line across it -- so *above the
    line* and *below the line* are literal, and the two kinds of coupling you can no
    longer have are literally out of reach.

    That geometry is the argument. A flat left-to-right scale, which is what this
    replaces, cannot show a boundary taking anything off the table.
    """
    d = Diagram("The Coupling Scale, with a Process Boundary Across It", w=980, h=560)
    d.note(490, 44, "the two worst kinds of coupling are the two you cannot have "
                    "any more — that is what you bought", ANNOTATION, 19)

    NAME_X, GLOSS_X, BOUNDARY_Y = 250, 380, 258
    d.note(NAME_X, 104, "tightest", INK, 13)

    rows = ((132, "Content", "one party reaches into the other's internals", True),
            (200, "Common", "both parties share the same mutable store", True),
            (326, "Control", "one party tells the other what to do", False),
            (394, "Stamp", "a whole structure is passed, and part of it used", False),
            (462, "Data", "exactly what is needed is passed, and nothing else", False))
    for y, name, gloss, prevented in rows:
        # the two prevented kinds are what the slide is ABOUT, so they are not the
        # faintest thing on it. The red rule through them and the red "prevented"
        # beside them carry that; greying the name as well said it twice and cost
        # the two most important words on the figure their legibility.
        d.note(NAME_X, y + 7, name, INK, 22)
        d.note(GLOSS_X, y + 6, gloss, COMMENT, 14, anchor="start")
        if prevented:
            d.rule(NAME_X - 62, y, 124, ANNOTATION, 2.4)
            d.note(NAME_X - 82, y + 6, "prevented", ANNOTATION, 14, anchor="end")

    d.note(NAME_X, 506, "loosest", INK, 13)

    d.rule(70, BOUNDARY_Y, 850, INK, 3.4)
    d.note(920, BOUNDARY_Y - 12, "the process boundary", INK, 16, anchor="end")
    d.note(920, BOUNDARY_Y + 30, "separate processes, private data,\n"
                                 "no shared transaction", COMMENT, 14, anchor="end")
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
