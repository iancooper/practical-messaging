#!/usr/bin/env python3
"""The eight legacy BPMN images for Day 2's Process Automation section, redrawn.

Mostly the shopping / food-ordering family, plus `bpmn-the-six`, which is vocabulary
rather than a flow and replaces three legend sheets at once.

    python3 tools/bpmn_shopping.py                  # rebuild all
    python3 tools/bpmn_shopping.py bpmn-elements
    python3 tools/bpmn_shopping.py --list

**Why this is a redraw and not the restyle the plan first called for.** Seven of the
eight legacy BPMN images have editable `.drawio` sources, so §8 recorded them as an
edit to `strokeColor` / `fontFamily`. That was optimistic: there is **no drawio CLI,
no soffice and no inkscape** on this machine (checked, not assumed), so a style edit
would leave the `.png` stale -- and the `.png` is what the deck shows. Drawing them
through `diagram.py` emits both files from one definition, which is the whole reason
that tool exists.

Same register as `bpmn_hotel.py`, and for the same reason -- straight strokes, Plex
Sans labels. The two families sit in the same section and must read as one.

**This family stays in the shopping domain on purpose.** D2-10 moved the *hotel*
examples off pizza, but these are the section's **see-one**: the taught example, in a
domain the room already met on Day 1, against the hotel flow the delegates drew
themselves. `Shopping Flow with Pools` is the working two-pool collaboration;
`bpmn-hotel-pools-and-lanes` is the one-pool-with-five-lanes that fails. Both are
needed, and they are not duplicates of each other.

Two originals are improved rather than copied, and both times because the slide's own
text asks for something the picture did not show -- see `bpmn_elements` and
`bpmn_shopping_choreography`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, MUTED, INK, PLAIN          # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
FIGURES = {}


def figure(name):
    def wrap(fn):
        FIGURES[name] = fn
        return fn
    return wrap


def D(title, w, h):
    """Straight-stroked, Plex Sans -- the BPMN register, per plan §8.5."""
    return Diagram(title, w=w, h=h, sketch=False, font=PLAIN)


@figure("bpmn-elements")
def bpmn_elements():
    """*BPMN — The Elements.* The original is an unlabelled six-shape flow with one
    kind of arrow on it. The slide's body text is **two** kinds of arrow, and its
    callout is *sequence flow is what happens at a desk; message flow is what happens
    between desks* -- so the picture was missing the half the slide argues about.

    This one names the six elements and draws a second participant, so the message
    flow has somewhere to go. Red is spent on the token line, which the presenter
    note marks load-bearing.
    """
    d = D("BPMN — The Elements", 940, 452)
    d.note(470, 32, "the token follows the sequence flow — no token crosses a "
                    "message flow", ANNOTATION, 17)

    d.pool(20, 62, 900, 214, "One Participant")
    st = d.event(96, 168, "start")
    tk = d.task(146, 142, 126, 52, "Task")
    ev = d.event(320, 168, "intermediate", "message")
    gw = d.gateway(400, 168, "parallel")
    ta = d.task(456, 98, 150, 46, "Task")
    tb = d.task(456, 192, 150, 46, "Task")
    gj = d.gateway(664, 168, "parallel")
    en = d.event(734, 168, "end")

    d.flow(st, tk, sides=("r", "l"))
    d.flow(tk, ev, sides=("r", "l"))
    d.flow(ev, gw, sides=("r", "l"))
    d.flow(gw, ta, via=[(400, 121)], sides=("t", "l"))
    d.flow(gw, tb, via=[(400, 215)], sides=("b", "l"))
    d.flow(ta, gj, via=[(664, 121)], sides=("r", "t"))
    d.flow(tb, gj, via=[(664, 215)], sides=("r", "b"))
    d.flow(gj, en, sides=("r", "l"))

    # the second participant, so the message flow has somewhere to come from
    d.pool(20, 316, 900, 100, "Another Participant")
    ot = d.task(258, 340, 150, 46, "Task")
    d.flow(ot, ev, "message flow", message=True, accent=True,
           via=[(320, 340)], sides=("t", "b"), lx=50, ly=52)

    for x, y, t in ((96, 212, "start event"), (209, 210, "task — work gets done"),
                    (320, 134, "event"), (400, 258, "gateway"),
                    (734, 212, "end event"), (662, 90, "sequence flow")):
        d.note(x, y, t, MUTED, 12)
    return d


@figure("bpmn-ordering-flow")
def ordering_flow():
    """*BPMN.* The takeaway see-one: the notation on a flow the room already knows.
    Five user tasks and a message end event, exactly as the original."""
    d = D("BPMN — Order Food", 1160, 190)
    st = d.event(56, 96, "start", None, "Order Food")
    xs, prev = 106, st
    for label in ("Enter Location", "Choose Restaurant",
                  "Add Menu Choices\nto Basket", "Checkout Basket"):
        t = d.task(xs, 70, 190, 54, label, marker="user")
        d.flow(prev, t, sides=("r", "l"))
        prev, xs = t, xs + 234
    en = d.event(1100, 96, "end", "message", "Checked Out")
    d.flow(prev, en, sides=("r", "l"))
    return d


@figure("bpmn-shopping-as-sequence")
def shopping_as_sequence():
    """*Orchestration.* One participant's perspective, and the presenter note names
    it: this is the conductor from round 4, holding the routing slip. Red says what
    the slide's bullets say -- control, state and decisions are all local."""
    d = D("Checkout Basket — as an Orchestration", 1270, 218)
    d.note(635, 32, "one participant holds the whole process — control, state and "
                    "the decisions are all local to it", ANNOTATION, 17)
    st = d.event(56, 124, "start")
    xs, prev = 106, st
    for label in ("Create Basket", "Validate Choice", "Price Basket",
                  "Validate Delivery\nInformation", "Validate Payment\nInformation"):
        t = d.task(xs, 98, 186, 54, label, marker="service")
        d.flow(prev, t, sides=("r", "l"))
        prev, xs = t, xs + 214
    en = d.event(1212, 124, "end", "message", "Checked Out\nBasket")
    d.flow(prev, en, sides=("r", "l"))
    return d


@figure("bpmn-shopping-collaboration")
def shopping_collaboration():
    """*Collaboration*, and the figure three slides lean on -- Tokens, Collaboration
    and Choreography, and Pools and Lanes. Two pools, five message flows, and every
    message flow crossing the boundary the paper notation drew as a heavy bar."""
    d = D("Shopping — a Collaboration", 1330, 470)
    d.note(665, 30, "each pool runs its own sequence flow; the only thing crossing "
                    "between them is a message", ANNOTATION, 17)

    d.pool(20, 58, 1290, 150, "Customer")
    cs = d.event(96, 132, "start", None, "Order Food")
    cust, xs = [], 146
    for label in ("Enter Location", "Choose Restaurant",
                  "Add Menu Choices\nto Basket", "Checkout Basket"):
        cust.append(d.task(xs, 106, 176, 52, label, marker="user"))
        xs += 214
    ce = d.event(1250, 132, "end")
    d.flow(cs, cust[0], sides=("r", "l"))
    for a, b in zip(cust, cust[1:]):
        d.flow(a, b, sides=("r", "l"))
    d.flow(cust[-1], ce, sides=("r", "l"))

    d.pool(20, 300, 1290, 150, "Shopping")
    ss = d.event(96, 374, "start")
    shop, xs = [], 146
    for label in ("Create Basket", "Validate Choice", "Price Basket",
                  "Validate Delivery\nInformation", "Validate Payment\nInformation"):
        shop.append(d.task(xs, 348, 176, 52, label, marker="service"))
        xs += 214
    se = d.event(1250, 374, "end", "message", "Checked Out\nBasket")
    d.flow(ss, shop[0], sides=("r", "l"))
    for a, b in zip(shop, shop[1:]):
        d.flow(a, b, sides=("r", "l"))
    d.flow(shop[-1], se, sides=("r", "l"))

    # the five messages, and they are the only things that cross
    for src, dst, label, ly in (
            (cust[1], shop[0], "Begin Shopping", 0),
            (cust[2], shop[1], "Add Item to Basket", -28),
            (shop[2], cust[2], "Basket Price", 28),
            (cust[3], shop[3], "Checkout Basket", -28),
            (shop[4], cust[3], "Valid Basket", 28)):
        d.flow(src, dst, label, message=True, accent=True,
               sides=("b", "t") if src in cust else ("t", "b"), ly=ly)
    return d


@figure("bpmn-shopping-choreography")
def shopping_choreography():
    """*Choreography and Conversation.* Five choreography tasks, banded with who
    speaks and who is spoken to. No pool owns any of them, which is the slide's line:
    *no single owner of the flow, no centralized control*.

    Two fixes to the original. Its last message reads **"Bakset Validated"**, a typo
    that would go up on a screen; and the *Review Price* label was reused for two
    different messages, which on a slide about correlating messages is exactly the
    wrong thing to be sloppy about -- the second is the validation result.
    """
    d = D("Shopping — a Choreography", 1360, 400)
    d.note(650, 32, "nobody owns this flow — it is the dance, not a dancer",
           ANNOTATION, 17)

    st = d.event(56, 200, "start")
    steps = [("Begin Shopping", "Customer", "Shopping", "Start Shopping", "Basket Created"),
             ("Add Item to Basket", "Customer", "Shopping", "Item Chosen", None),
             ("Basket Price", "Shopping", "Customer", "Review Price", "Basket Priced"),
             ("Checkout Basket", "Customer", "Shopping", "Address & Payment\nDetails", None),
             ("Validate Basket", "Shopping", "Customer", "Basket Checked", "Basket Validated")]
    xs, prev = 106, st
    for label, top, bottom, above, below in steps:
        c = d.choreo(xs, 152, 196, 96, label, top, bottom)
        d.flow(prev, c, sides=("r", "l"))
        d.msg(xs + 84, 100, above, w=28, h=20, label_pos="above")
        if below:
            d.msg(xs + 84, 282, below, w=28, h=20, label_pos="below")
        prev, xs = c, xs + 234
    en = d.event(1298, 200, "end")
    d.flow(prev, en, sides=("r", "l"))
    return d


@figure("bpmn-the-six")
def the_six():
    """*BPMN — Tasks, Events and Gateways.* Replaces **three** legend sheets --
    `Task Types`, `Event Types`, `Gateway Types` -- with one figure of the six the
    deck actually uses.

    **The slide asked for this.** Its callout is already *"Six of them do nearly all
    the work"*, its presenter note is *"do not read the lists"*, and its own `#note:`
    sends the full legends to a delegate reference card -- *a lookup table wants to be
    in the delegate's hand, not on the screen*, the same test that sent Managing
    Asynchronous APIs and the routing patterns to handouts. Three lookup tables on a
    screen were doing the opposite of what the slide says out loud.

    It is also the cheap option, which is rare and worth noting: drawing the three
    legends faithfully would have needed roughly fifteen more BPMN symbols in
    `diagram.py` -- manual, business rule, script, loop and transaction markers;
    signal, escalation, conditional, error, cancel, link and terminate events;
    inclusive, complex and event-based gateways -- every one of them used on that one
    slide and nowhere else in either day.

    All six here already existed in the tool, because all six are the ones the hotel
    and shopping families are built from. That is the same fact the callout is making.
    """
    d = D("BPMN — the Six That Do the Work", 1200, 580)
    d.note(600, 44, "six of them do nearly all the work", ANNOTATION, 19)

    for x, head in ((196, "Tasks"), (600, "Events"), (992, "Gateways")):
        d.note(x, 112, head, INK, 17, font=PLAIN)

    # tasks -- the name goes inside the box, so the gloss sits under it
    for y, marker, name, gloss in (
            (182, "service", "Service", "calls something that is not a person"),
            (352, "receive", "Receive", "waits for a message to arrive")):
        d.task(101, y, 190, 56, name, marker=marker)
        d.note(196, y + 104, gloss, MUTED, 14)

    # events and gateways label themselves underneath, so the gloss drops further
    for cy, symbol, name, gloss in (
            (210, "message", "Message", "something arrived from\nanother participant"),
            (380, "timer", "Timer", "enough time passed,\nand nothing arrived")):
        d.event(600, cy, "intermediate", symbol, name)
        d.note(600, cy + 76, gloss, MUTED, 14)

    for cy, kind, name, gloss in (
            (210, "exclusive", "Exclusive", "one path is taken,\nand only one"),
            (380, "parallel", "Parallel", "every path is taken,\nand the token splits")):
        d.gateway(992, cy, kind, name)
        d.note(992, cy + 76, gloss, MUTED, 14)

    d.note(600, 548, "every other task type, event and gateway is on the reference card "
                     "in your pack", MUTED, 15)
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
        print(f"  {name:<30} {dg.w}x{dg.h}  {os.path.getsize(png):>8,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
