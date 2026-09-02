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


@figure("paper-guest-cycle")
def guest_cycle():
    """The map of the domain, and the replacement for the third-party
    setupmyhotel.com infographic on `exercises/Paper Flow.pptx` slide 3.

    Two things ours says that theirs does not, and both are load-bearing. **Onboarding
    is not a guest-cycle stage** -- the guest is not there for it; it is how a hotel is
    in the catalogue at all, so it stands outside the loop and feeds it. And **every
    stage hands the next one a piece of paper**, which is the red idea: the cycle is
    already a chain of hand-offs before anyone has drawn a desk. Slide 4 names those
    artefacts, so they are named here.

    *Departure is the delegates' task* is deliberately NOT marked here. It is slide 4's
    point, and a second red idea would cost this one its own.
    """
    d = Diagram("The Guest Cycle", w=1340, h=500)

    d.note(670, 44, "every stage hands the next one a piece of paper — "
                    "the cycle is a chain of hand-offs before we draw a single desk",
           ANNOTATION, 19)

    # -- outside the loop: how a hotel is in the catalogue at all ----------------
    onb = d.box(60, 118, 190, 84, "Hotel\nOnboarding")
    d.note(155, 224, "not a guest-cycle stage —\nthe guest is not there for it",
           MUTED, 15)

    # -- the cycle proper --------------------------------------------------------
    Y, W, H, GAP = 286, 190, 80, 72
    xs = [330 + i * (W + GAP) for i in range(4)]
    stages = [d.box(x, Y, W, H, n) for x, n in
              zip(xs, ("Pre-Arrival", "Arrival", "Occupancy", "Departure"))]

    # what each stage hands on. Slide 4 states the first three verbatim.
    for a, b, label in zip(stages, stages[1:], ("a booking", "a key", "the invoices")):
        right = a["x"] + W
        d.doc(right + 23, Y + 27, 26, 34)
        d.note(right + 36, Y - 16, label, ANNOTATION, 15)
        d.arrow(a, b, accent=True, dashed=True, sides=("r", "l"))

    # the catalogue comes in from outside the cycle
    d.doc(277, 212, 26, 34)
    d.note(316, 229, "a catalogue of hotels", ANNOTATION, 15, anchor="start")
    d.arrow(onb, stages[0], accent=True, dashed=True, sides=("r", "l"),
            via=[(290, 160), (290, 326)])

    # and the room goes back to it, which is what makes this a cycle
    d.arrow(stages[3], stages[0], via=[(xs[3] + W / 2, 440), (xs[0] + W / 2, 440)],
            sides=("b", "b"), muted=True)
    d.note(818, 462, "the room, free again — and a guest who may rebook", MUTED, 15)
    return d


@figure("Departure")
def departure():
    """The fifth stage of the guest cycle, and the one with no worked flow —
    `exercises/Paper Flow.pptx` slide 4 sets it as the delegate task, verbatim:
    *"Departure is how I get my bill. Show how the flow of bills reaches my file."*

    **This is a facilitator reference answer, not a slide.** It is revealed in block
    1's debrief, after the tables have drawn their own. It is deliberately NOT wired
    into `outlines/DayTwo.md`: putting the answer in front of the room before the task
    destroys see-one/do-one, which is the whole design of the block.

    Two things it has to honour. Slide 4 fixes what the prior stages hand on -- a
    catalogue, a booking, a key, and Occupancy's room-service invoices, which
    Occupancy step 5 files into the Guest Stay File. And the step-numbering rule
    (plan §7): one global ascending sequence, no repeats, no gaps, in the order the
    **arrows** run. Step 3 is where that rule earns its keep -- the guest settles the
    bill and hands the key back in the same turn, so it is drawn **structurally**, one
    number branching to two arrows, rather than as two steps or a repeated number.

    Written as five desk-turns, matching Occupancy's granularity: a number covers a
    desk taking from its in-tray, doing the work, and putting the result in its
    out-tray.
    """
    d = Diagram("Departure", w=1300, h=880)

    d.note(650, 44, "the bill is not written at check-out — it is assembled from "
                    "paper that has been landing in the file all week",
           ANNOTATION, 19)

    d.bar(490, 96, 740)
    d.note(60, 836, "Departure", INK, 26, anchor="start")

    # -- the guest, outside the hotel -------------------------------------------
    guest = d.desk(80, 360, 330, 140, "Guest")
    g_in = d.tray(118, 412, 64, 46)
    d.note(250, 436, "Settle Up", INK, 15)
    g_out = d.tray(310, 412, 64, 46, out=True)

    # -- front desk, first turn: the bill ----------------------------------------
    fda = d.desk(570, 110, 350, 140, "Front Desk")
    d.note(676, 180, "Total the\nInvoices", INK, 15)
    a_out = d.tray(836, 156, 64, 46, out=True)

    # the file the whole task is about
    sf = d.folder(1086, 292, 84, 60, "Guest Stay File")
    d.arrow((1128, 214), sf, muted=True, sides=(None, "t"))
    d.note(1128, 180, "filed here all week —\nthat is Occupancy's flow", MUTED, 14)

    # -- front desk, second turn: the receipt and the room -----------------------
    fdb = d.desk(570, 440, 350, 140, "Front Desk")
    b_in = d.tray(606, 490, 64, 46)
    d.note(762, 512, "File the Receipt", INK, 15)
    b_out = d.tray(836, 490, 64, 46, out=True)

    # -- and the desk that puts the room back on sale ----------------------------
    hk = d.desk(620, 700, 340, 130, "Housekeeping")
    h_in = d.tray(656, 744, 64, 46)
    d.note(830, 768, "Make the Room\nAvailable", INK, 15)
    rooms = d.folder(1086, 722, 84, 60, "Room List")

    # -- the sequence, in the order the arrows run -------------------------------
    d.arrow(guest, fda, "asks to check out", sides=("r", "l"), lx=-58, ly=44)
    d.step(452, 470, 1)

    # reading the file is part of step 2, so it is this flow's red, not context grey
    d.arrow(sf, fda, "take the stay file", accent=True, dashed=True,
            sides=("l", "r"), lx=-30, ly=30)

    d.arrow(a_out, g_in, "the bill", accent=True, dashed=True,
            sides=("l", "t"), lx=196, ly=-26)
    d.step(620, 292, 2)

    # step 3 branches: settling the bill and handing the key back are one turn
    d.arrow(g_out, b_in, "the payment", accent=True, dashed=True,
            sides=("r", "l"), ly=-14)
    d.arrow(g_out, b_in, "the key", accent=True, dashed=True,
            sides=("b", "b"), via=[(342, 636), (638, 636)], lx=142, ly=20)
    d.step(250, 556, 3)

    d.arrow(fdb, sf, "the receipt", accent=True, dashed=True,
            sides=("r", "b"), ly=-14)
    d.arrow(b_out, h_in, "room vacated", accent=True, dashed=True,
            sides=("b", "t"), lx=64)
    d.step(1012, 502, 4)

    d.arrow(hk, rooms, "free again", accent=True, dashed=True,
            sides=("r", "l"), ly=-14)
    d.step(1012, 688, 5)
    return d


@figure("paper-document-card")
def document_card():
    """The half-A5 document card, for the exercise. Print four to an A4 sheet.

    **The header strip is the whole design.** Three boxes -- type, correlation id,
    reply-to -- across the top of an otherwise blank card. It makes delegates use a
    correlation id without being told to, and makes *reply-to* a property of the
    document rather than something everybody just knows.

    Both become load-bearing in round 3: the correlation id is how you tell a
    duplicate from a new request, and reply-to is why a resend reaches the right
    desk. So the strip is left deliberately unexplained -- a table hits the problem
    in round 2, with two documents in an in-tray and no way to tell which request one
    of them answers, and then you point at the box they left blank.

    Drawn at 2:1.4, which is half-A5 in landscape, and mono-safe.
    """
    W, H = 600, 420
    d = Diagram("Document Card", w=W, h=H)

    d.box(20, 20, W - 40, H - 40, "")

    # -- the header strip -------------------------------------------------------
    fields = (("TYPE", 52, 168), ("CORRELATION ID", 236, 168), ("REPLY-TO", 424, 128))
    for label, x, w in fields:
        d.note(x + 6, 78, label, MUTED, 13, anchor="start")
        d.rule(x, 92, w, INK, 1.4)
    d.note(300, 128, "one card is one document — fill the strip in before you send it",
           ANNOTATION, 15)

    # -- the body: ruled, because a blank box invites a diagram -----------------
    for i in range(6):
        d.rule(52, 186 + i * 38, W - 104)
    return d


@figure("paper-tray-sheets")
def tray_sheets():
    """The in-tray and out-tray sheets. Print two to an A4, cut in half, two per desk.

    A tray is a sheet of paper you put paper on. The cheapness is the point: the room
    has to believe a queue is a *physical place*, and a labelled sheet of A4 is more
    convincing than a slide.

    The glyph on each sheet is the same one the notation key teaches, so a delegate
    who has read the key recognises the tray on the table without being told.
    """
    W, H = 620, 880
    d = Diagram("Tray Sheets", w=W, h=H)

    for i, (title, out, rule) in enumerate((
            ("IN-TRAY", False, "work that has arrived, and is not done yet"),
            ("OUT-TRAY", True, "finished here, and not yet collected"))):
        y = 30 + i * 430
        d.desk(24, y, W - 48, 390)
        d.tray(70, y + 44, 96, 70, out=out)
        d.note(210, y + 66, title, INK, 34, anchor="start")
        d.note(210, y + 106, rule, MUTED, 16, anchor="start")
        d.note(W / 2, y + 190, "put paper here", MUTED, 18)
        d.note(W / 2, y + 340, "nobody shouts across the office", ANNOTATION, 17)
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
