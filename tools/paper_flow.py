#!/usr/bin/env python3
"""Paper Flow artwork for Day 2 — the notation delegates draw with by hand.

    python3 tools/paper_flow.py             # rebuild all
    python3 tools/paper_flow.py --list

`resources/Paper Office.drawio` (2021, editable, not currently linked from any
outline) already defines the phone / inbox / outbox / fax / chair / desk glyphs and
three role cards. It does NOT cover the three things the slide actually leans on --
**the file**, the **organisational boundary bar**, and **red-dashed vs. solid
arrows** -- so this key is a build, not a relink. The glyph vocabulary is matched to
it deliberately: a desk is a rectangle with corner brackets, a tray is a document
sitting in a shallow tray, so the legend and the ~15 worked flows read as one hand.

Hand-drawn register here, unlike the BPMN family: delegates reproduce this notation
with a pen within the hour, so it has to look like something a person could draw.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, MUTED, INK, CARBON      # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
FIGURES = {}


def figure(name):
    def wrap(fn):
        FIGURES[name] = fn
        return fn
    return wrap


@figure("paper-notation-key")
def notation_key():
    """The legend, and the one rule. Doubles as the exercise handout, so it has to
    stand alone off the slide -- every glyph is named in words beside it."""
    d = Diagram("The Desk — In-Tray, Out-Tray, File", w=1000, h=540)

    d.note(500, 42, "every hand-off goes out-tray to in-tray — "
                    "nobody shouts across the office", ANNOTATION, 19)

    # ---- the legend -----------------------------------------------------------
    TX = 186
    d.tray(84, 92, 64, 46)
    d.note(TX, 114, "in-tray — work that has arrived,\nand is not done yet",
           INK, 15, anchor="start")

    d.tray(84, 168, 64, 46, out=True)
    d.note(TX, 190, "out-tray — finished here,\nand not yet collected",
           INK, 15, anchor="start")

    d.folder(84, 244, 64, 46)
    d.note(TX, 260, "the file — what this desk knows,\nwritten down, because the clerk\n"
                    "goes home at five", INK, 15, anchor="start")

    d.bar(112, 330, 48)
    d.note(TX, 358, "a heavy bar — an organisational boundary", INK, 15, anchor="start")

    d.arrow((88, 412), (150, 412), accent=True, dashed=True)
    d.arrow((88, 444), (150, 444))
    d.note(TX, 410, "red dashed — paper moving", ANNOTATION, 15, anchor="start")
    d.note(TX, 444, "solid — a phone call or a fax", CARBON, 15, anchor="start")

    d.step(116, 492, 2)
    d.note(TX, 497, "numbered steps show the sequence", INK, 15, anchor="start")

    # ---- the desk -------------------------------------------------------------
    d.note(752, 92, "a desk", MUTED, 15)
    d.desk(560, 106, 384, 132)
    d.tray(596, 132, 64, 46, "in-tray")
    d.folder(716, 132, 64, 46, "the file")
    d.tray(844, 132, 64, 46, "out-tray", out=True)

    # ---- the one rule, drawn ---------------------------------------------------
    d.note(752, 300, "and the only rule", MUTED, 15)
    d.desk(560, 318, 160, 120)
    d.desk(784, 318, 160, 120)
    ot = d.tray(648, 348, 54, 42, out=True)
    it = d.tray(800, 348, 54, 42)
    d.arrow(ot, it, accent=True, dashed=True, sides=("r", "l"))
    d.step(752, 408, 4)
    d.note(640, 462, "one desk", MUTED, 14)
    d.note(864, 462, "the next desk", MUTED, 14)
    return d


@figure("paper-worked-flows-montage")
def worked_flows_montage():
    """The close of the *see one*: all four takeaway flows at once. Composition, not
    drawing -- every source is an existing editable .drawio in resources/, embedded
    here as a data URI so the montage does not depend on them staying put.

    The red line is the slide's own callout, and it is the reason the four flows were
    walked separately first.
    """
    d = Diagram("The Worked Flows — Just Paper Takeaway", w=1140, h=944)
    d.note(570, 48, "four flows, no `main` — every desk acts because something "
                    "landed in its in-tray", ANNOTATION, 19)
    cells = [
        (40, 96, "Restaurant Onboarding"),
        (580, 96, "Customer Order"),
        (40, 522, "Order Placement"),
        (580, 522, "Order Confirmation"),
    ]
    for x, y, name in cells:
        d.image(x, y, 520, 372, os.path.join(OUT, f"{name}.drawio.png"))
        d.note(x + 260, y + 396, name, MUTED, 16)
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
        print(f"  {name:<26} {dg.w}x{dg.h}  {os.path.getsize(png):>8,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
