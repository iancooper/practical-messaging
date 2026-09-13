#!/usr/bin/env python3
"""Paper Flow artwork for Day 2 — the notation delegates draw with by hand.

    python3 tools/paper_flow.py             # rebuild all
    python3 tools/paper_flow.py --list

`resources/Paper Office.drawio` (2021, editable, not currently linked from any
outline) already defines the phone / inbox / outbox / fax / chair / desk glyphs and
three role cards. It does NOT cover the three things the slide actually leans on --
**the file**, the **organisational boundary bar**, and **dashed vs. solid
arrows** -- so this key is a build, not a relink.

Paper moving and a phone call are separated by the DASH, not by hue. They were red
and blue until 2026-09-07, which said it twice and cost this family its red: Departure
carried seven red arrows and none of them was the figure's idea. Carbon now carries
paper and the phone alike, and red is spent once per figure, as everywhere else. The
one exception is `paper-guest-cycle`, where the hand-offs ARE the single red idea. The glyph vocabulary is matched to
it deliberately: a desk is a rectangle with corner brackets, a tray is a document
sitting in a shallow tray, so the legend and the ~15 worked flows read as one hand.

Hand-drawn register here, unlike the BPMN family: delegates reproduce this notation
with a pen within the hour, so it has to look like something a person could draw.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, COMMENT, MUTED, INK, CARBON      # noqa: E402

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

    # Paper moving and a phone call are separated by the DASH, not by hue. They used
    # to be red and blue, which said it twice and cost the family its red: Departure
    # had seven red arrows on it and none of them was the idea.
    d.arrow((88, 412), (150, 412), dashed=True)
    d.arrow((88, 444), (150, 444))
    d.note(TX, 410, "dashed — paper moving", CARBON, 15, anchor="start")
    d.note(TX, 444, "solid — a phone call or a fax", CARBON, 15, anchor="start")

    d.step(116, 492, 2)
    d.note(TX, 497, "numbered steps show the sequence", INK, 15, anchor="start")

    # ---- the desk -------------------------------------------------------------
    d.note(752, 92, "a desk", INK, 15)
    d.desk(560, 106, 384, 132)
    d.tray(596, 132, 64, 46, "in-tray")
    d.folder(716, 132, 64, 46, "the file")
    d.tray(844, 132, 64, 46, "out-tray", out=True)

    # ---- the one rule, drawn ---------------------------------------------------
    d.note(752, 300, "and the only rule", COMMENT, 15)
    d.desk(560, 318, 160, 120)
    d.desk(784, 318, 160, 120)
    ot = d.tray(648, 348, 54, 42, out=True)
    it = d.tray(800, 348, 54, 42)
    d.arrow(ot, it, dashed=True, sides=("r", "l"))
    d.step(752, 408, 4)
    d.note(640, 462, "one desk", INK, 14)
    d.note(864, 462, "the next desk", INK, 14)
    return d


# **The 24 arrows, and not one of them was invented here.** They are Ian's, lifted
# out of `archive/Practical Messaging -  Day 2 - 2025.pptx` slide 66 -- 24 `rightArrow`
# shapes over the same four flows, with a `<p:timing>` tree that revealed them in 22
# clicks. `REVIEW.md` R4-13 quotes why they existed: *"I added arrows to the diagram,
# colour-coded for synchronous and asynchronous communication and progressively showed
# the arrows so that the flow could be seen. For this reason it did not matter that the
# scale was small."* Rule 4 -- the file was opened, not assumed.
#
# Each arrow was read as start/end **fractions of the flow picture it sits on**, so it
# lands in the same place relative to the drawing even though our 2x2 grid orders the
# four flows differently from his. Two of the 24 ran off the top of their own panel in
# his layout, where the panels touched; here they are clamped into the cell and marked
# below.
#
# **The colours are not his.** His were Office theme accents -- `#4F81BD` and `#4BACC6`,
# two blues that read almost the same at slide size and would have been the only
# off-palette colours in either deck. Ian ruled 2026-09-12 for the house pair, and for
# this assignment of it: **asynchronous is CARBON and synchronous is MUTED**, because
# twenty against four is the section's whole argument and the phone call is the part
# that should recede. `styles.md` puts muted on lines rather than letters, and a block
# arrow is a line.
#
# `layer` is the click. Ian chose **8, two per flow**, over his own 22 and over 4 --
# Day 2 spends 208 clicks across 128 slides, so 22 on one picture is a tenth of the
# deck's whole budget. Order Placement has no synchronous arrow at all, so its two
# clicks split its paper run; Order Confirmation's pair is one of each.
#
#   layer  what you say while you click it
#   -----  ----------------------------------------------------------------
#     1    the phone call that starts it                    Onboarding, sync
#     2    and everything after it is paper                 Onboarding, 7
#     3    the customer rings, and gets transferred         Customer Order, 2 sync
#     4    the order becomes paper too                      Customer Order, 4
#     5    the fax goes out                                 Order Placement
#     6    and the office keeps working while it is gone    Order Placement, 7
#     7    the confirmation arrives on its own, later       Confirmation, async
#     8    only now does anyone pick up the phone           Confirmation, sync
#
# **`weight` is the SHAFT, and that is half of what the .pptx records.** In OOXML a
# `rightArrow`'s `cy` is the height of the whole shape -- the head's wings included --
# and the default `adj1` puts the shaft at half of it. Reading `cy` straight across as
# a shaft thickness drew every arrow at exactly twice Ian's, which obliterated the flow
# the arrows exist to let you see. Caught by compositing a click and looking at it; the
# ratios all matched on paper, which is why arithmetic alone would not have found it.
#
# (x1, y1, x2, y2, weight, sync, layer), in montage canvas units.
MONTAGE_TRACES = [
    # ---- Restaurant Onboarding, cell (40, 96) ----
    (196.1, 145.2, 361.1, 145.2, 17.25, True,  1),   # the phone call
    (399.0, 241.9, 437.2, 131.4, 17.25, False, 2),
    (212.5, 244.8, 383.6, 244.8, 17.25, False, 2),
    (118.4, 367.6, 114.4, 276.0, 17.25, False, 2),
    (171.0, 277.9, 203.5, 370.5, 17.25, False, 2),
    (407.2, 286.3, 236.1, 286.3, 17.25, False, 2),
    (500.9, 454.6, 398.8, 429.8, 18.55, False, 2),
    (446.4, 374.5, 493.4, 267.8, 17.25, False, 2),
    # ---- Customer Order, cell (580, 96) ----
    (758.5, 200.6, 915.7, 200.6, 16.00, True,  3),   # the phone call
    (971.3, 341.5, 1033.4, 309.9, 16.00, True,  3),  # and the transfer
    (675.2, 194.2, 918.7, 101.6, 16.00, False, 4),   # CLAMPED: ran off his panel top
    (1004.5, 204.8, 1032.1, 106.6, 17.15, False, 4),
    (936.2, 332.4, 950.5, 231.3, 17.15, False, 4),
    (998.1, 417.4, 1006.6, 357.2, 19.20, False, 4),
    # ---- Order Placement, cell (40, 522) -- no synchronous arrow at all ----
    (462.5, 619.8, 470.9, 562.3, 18.35, False, 5),   # the fax goes out
    (197.4, 593.2, 356.2, 593.2, 15.25, False, 6),
    (379.4, 645.2, 220.6, 645.2, 15.25, False, 6),
    (66.1, 721.7, 109.7, 627.3, 15.25, False, 6),
    (102.2, 821.0, 137.7, 723.2, 15.25, False, 6),
    (67.5, 737.8, 179.2, 812.5, 15.25, False, 6),
    (174.4, 666.0, 169.7, 770.0, 15.25, False, 6),
    (489.5, 793.2, 469.1, 665.0, 18.35, False, 6),
    # ---- Order Confirmation, cell (580, 522) ----
    (1055.0, 661.9, 1071.3, 527.6, 19.85, False, 7),  # CLAMPED: ran off his panel top
    (936.2, 661.1, 761.3, 661.1, 16.50, True,  8),    # only now, the phone
]

MONTAGE_LAYERS = 8
MONTAGE_W, MONTAGE_H = 1140, 944


def _montage(traced=False):
    """The close of the *see one*: all four takeaway flows at once. Composition, not
    drawing -- every source is an existing editable .drawio in resources/, embedded
    here as a data URI so the montage does not depend on them staying put.

    The red line is the slide's own callout, and it is the reason the four flows were
    walked separately first.

    `traced` adds all 24 of Ian's arrows at once -- the static form, for the recap on
    *Full Flow, End to End*, which has already watched the animated one.
    """
    d = Diagram("The Worked Flows — Just Paper Takeaway", w=MONTAGE_W, h=MONTAGE_H)
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
        d.note(x + 260, y + 396, name, INK, 16)
    if traced:
        for x1, y1, x2, y2, wt, sync, _ in MONTAGE_TRACES:
            d.trace((x1, y1), (x2, y2), weight=wt, sync=sync)
    return d


@figure("paper-worked-flows-montage")
def worked_flows_montage():
    """The base: the four flows, no arrows. Layer 0 of the animated form, and this is
    still the file the outline links -- it has not changed a byte."""
    return _montage()


@figure("paper-worked-flows-montage-complete")
def worked_flows_montage_complete():
    """All 24 arrows at once, static. *Full Flow, End to End* shows this: the room has
    already watched them arrive one click at a time on slide 23, so repeating the
    reveal there would re-teach what it is supposed to be recapping. Ian, 2026-09-12."""
    return _montage(traced=True)


# **The eight overlays, one per click.** Each is its own Diagram on the montage's
# canvas with nothing in it but that click's arrows, so rsvg paints no ground and the
# PNG is transparent -- a few KB against the base's 1.3MB. `build_deck.py` stacks them
# at the base's rect, one reveal step each.
#
# They are registered in the loop rather than written out eight times so the count
# lives in one place, `MONTAGE_LAYERS`, next to the traces it counts.
def _montage_layer(k):
    def fn():
        d = Diagram(f"The Worked Flows — arrows, click {k}",
                    w=MONTAGE_W, h=MONTAGE_H, transparent=True)
        for x1, y1, x2, y2, wt, sync, layer in MONTAGE_TRACES:
            if layer == k:
                d.trace((x1, y1), (x2, y2), weight=wt, sync=sync, layer=layer)
        return d
    fn.__doc__ = (f"Click {k} of the montage reveal: "
                  f"{sum(1 for t in MONTAGE_TRACES if t[6] == k)} arrows, transparent.")
    return fn


for _k in range(1, MONTAGE_LAYERS + 1):
    figure(f"paper-worked-flows-montage-l{_k}")(_montage_layer(_k))


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
           COMMENT, 15)

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
    d.note(818, 462, "the room, free again — and a guest who may rebook", COMMENT, 15)
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
    d.note(1128, 180, "filed here all week —\nthat is Occupancy's flow", COMMENT, 14)

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
    d.arrow(guest, fda, "asks to check out", sides=("r", "l"), lx=-152, ly=44)
    d.step(452, 470, 1)

    # reading the file is part of step 2, so it is this flow's red, not context grey
    d.arrow(sf, fda, "take the stay file", accent=True, dashed=True,
            sides=("l", "r"), lx=-30, ly=30)   # the one idea: see the docstring

    d.arrow(a_out, g_in, "the bill", dashed=True,
            sides=("l", "t"), lx=196, ly=-8)
    d.step(620, 292, 2)

    # step 3 branches: settling the bill and handing the key back are one turn
    # this arrow crosses the boundary bar at its midpoint, so the label cannot sit
    # there: it goes up and to the right, into the gap between the bar and the desk
    d.arrow(g_out, b_in, "the payment", dashed=True,
            sides=("r", "l"), lx=52, ly=-38)
    d.arrow(g_out, b_in, "the key", dashed=True,
            sides=("b", "b"), via=[(342, 636), (638, 636)], lx=142, ly=20)
    d.step(250, 556, 3)

    d.arrow(fdb, sf, "the receipt", dashed=True,
            sides=("r", "b"), ly=-14)
    d.arrow(b_out, h_in, "room vacated", dashed=True,
            sides=("b", "t"), lx=142)
    d.step(1012, 502, 4)

    d.arrow(hk, rooms, "free again", dashed=True,
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
        d.note(x + 6, 78, label, INK, 13, anchor="start")
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
        d.note(210, y + 106, rule, INK, 16, anchor="start")
        d.note(W / 2, y + 190, "put paper here", INK, 18)
        d.note(W / 2, y + 340, "nobody shouts across the office", ANNOTATION, 17)
    return d


@figure("paper-the-desk")
def the_desk():
    """*The Frame*, Day 2 §2 — the desk with overflowing trays and a phone.

    **This replaces a watermarked stock photograph.** The image in the deck was a
    Getty / Comstock comp with the watermark, the agency name and the asset id all
    visible on it — the same class of problem as the Hohpe & Woolf figures and the
    setupmyhotel infographic, and the same answer: draw our own.

    **No red note, deliberately.** It sits beside two photographs as one of three
    establishing images at the very top of the day, and it is not making an argument
    — the section opener does that. The BPMN workflow-pattern figures carry no red
    for the same reason: vocabulary, not argument.

    The in-tray overflows and the out-tray does not, which is the only editorial
    choice in it and it is the true one — work arrives faster than a desk clears it,
    and that is the whole reason a queue is a place rather than an event.
    """
    d = Diagram("The Desk", w=940, h=460)

    d.desk(60, 96, 820, 300)

    # the in-tray, overflowing -- the stack is drawn leaning, as a real one does
    d.tray(146, 250, 104, 76)
    for i, (dx, dy) in enumerate(((6, 196), (-4, 172), (10, 148))):
        d.doc(164 + dx, dy, 72, 46)
    d.note(198, 356, "IN", INK, 20)

    d.folder(322, 254, 84, 60, "the file")

    d.phone(478, 244, 130, 88)
    d.note(543, 358, "a telephone, for when it cannot wait", COMMENT, 14)

    d.tray(700, 250, 104, 76, out=True)
    d.doc(718, 196, 72, 46)
    d.note(752, 356, "OUT", INK, 20)
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
