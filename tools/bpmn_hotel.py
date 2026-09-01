#!/usr/bin/env python3
"""The hotel BPMN figures for Day 2's Process Automation section.

Replaces the pizza-domain originals (D2-10 moved the section to the hotel, which is
the domain the room has been in since the Paper Flow exercise). Step names come from
the delegates' own paper flow -- `resources/Pre-Arrival Guest Flow.drawio` -- so the
BPMN says back to them what they wrote on paper an hour earlier.

    python3 tools/bpmn_hotel.py                     # rebuild all
    python3 tools/bpmn_hotel.py bpmn-hotel-p1-sequence
    python3 tools/bpmn_hotel.py --list

Two deliberate departures from the rest of Phase 2, both driven by the section:

  * NO SKETCH WOBBLE. The section opens by putting the delegates' hand-drawn paper
    flow beside the same flow in BPMN -- "a notation the rest of the industry already
    reads". A hand-drawn BPMN collapses that contrast, which is the teaching move.
  * LABELS IN PLEX SANS, not Caveat. Same reason: this is a formal notation. Caveat
    then reads as *our annotation on top of a standard diagram*, which is what the
    red callouts are.

Red is scarcer here than in the EIP set. The five workflow-pattern figures are
vocabulary and carry none; red is spent only where the section is making its
argument -- that no token crosses a message flow, and that a choreography has no
owner.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, MUTED, INK, CARBON, PLAIN    # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
FIGURES = {}


def figure(name):
    def wrap(fn):
        FIGURES[name] = fn
        return fn
    return wrap


def D(title, w, h):
    """Every figure in this family is straight-stroked and set in Plex Sans."""
    return Diagram(title, w=w, h=h, sketch=False, font=PLAIN)


# ---- the five workflow patterns ---------------------------------------------

@figure("bpmn-hotel-p1-sequence")
def p1_sequence():
    d = D("Pattern 1 — Sequence", 500, 150)
    d.pool(18, 26, 464, 88, "Booking Team")
    a = d.task(76, 44, 150, 52, "Take the Call", marker="user")
    b = d.task(286, 44, 168, 52, "Create Booking\nRequest")
    d.flow(a, b, sides=("r", "l"))
    d.note(250, 138, "one activity follows another — a sequence flow, and the token "
                     "moves with it", MUTED, 13)
    return d


@figure("bpmn-hotel-p2-parallel-split")
def p2_parallel_split():
    d = D("Pattern 2 — Parallel Split", 540, 230)
    ev = d.event(58, 105, "intermediate", "message", "Booking\nAccepted")
    gw = d.gateway(176, 105, "parallel")
    a = d.task(238, 30, 176, 52, "Take Payment")
    b = d.task(238, 128, 176, 52, "Prepare Booking\nConfirmation")
    d.flow(ev, gw, sides=("r", "l"))
    d.flow(gw, a, via=[(176, 56)], sides=("t", "l"))
    d.flow(gw, b, via=[(176, 154)], sides=("b", "l"))
    d.note(300, 214, "the gateway forks: both branches run, and the token splits in two",
           MUTED, 13)
    return d


@figure("bpmn-hotel-p3-join")
def p3_join():
    d = D("Pattern 3 — Synchronization", 560, 230)
    a = d.task(24, 30, 176, 52, "Take Payment")
    b = d.task(24, 128, 176, 52, "Prepare Booking\nConfirmation")
    gw = d.gateway(268, 105, "parallel")
    c = d.task(336, 79, 176, 52, "Confirm to Guest", marker="send")
    d.flow(a, gw, via=[(268, 56)], sides=("r", "t"))
    d.flow(b, gw, via=[(268, 154)], sides=("r", "b"))
    d.flow(gw, c, sides=("r", "l"))
    d.note(280, 214, "the join waits for both — the guest is not told until payment has "
                     "cleared and the confirmation is ready", MUTED, 13)
    return d


@figure("bpmn-hotel-p4-exclusive-choice")
def p4_exclusive_choice():
    d = D("Pattern 4 — Exclusive Choice", 600, 230)
    ev = d.event(88, 100, "start", "message", "Booking Request")
    t = d.task(152, 74, 156, 52, "Check Availability")
    gw = d.gateway(352, 100, "exclusive")
    a = d.task(414, 24, 166, 48, "Accept Booking", marker="send")
    b = d.task(414, 128, 166, 48, "Reject Booking", marker="send")
    d.flow(ev, t, sides=("r", "l"))
    d.flow(t, gw, sides=("r", "l"))
    d.flow(gw, a, "room free", via=[(352, 48)], sides=("t", "l"), ly=-2)
    d.flow(gw, b, "hotel full", via=[(352, 152)], sides=("b", "l"), ly=-2)
    d.note(300, 214, "one path only — this is step 7 on the flow you drew, "
                     "Respond with Booking Accept/Reject", MUTED, 13)
    return d


@figure("bpmn-hotel-p5-simple-merge")
def p5_simple_merge():
    d = D("Pattern 5 — Simple Merge", 600, 250)
    m = d.event(74, 56, "intermediate", "message", "Confirmation\nReceived")
    t = d.event(74, 170, "intermediate", "timer", "Chase the Agency")
    a = d.task(228, 87, 156, 52, "Check the Booking")
    b = d.task(422, 87, 156, 52, "Pack for the Trip")
    d.flow(m, a, sides=("r", "l"))
    d.flow(t, a, sides=("r", "l"))
    d.flow(a, b, sides=("r", "l"))
    d.note(300, 234, "no gateway: the paths were never concurrent, so there is "
                     "nothing to synchronise", MUTED, 13)
    return d


# ---- the three orchestrations ------------------------------------------------

@figure("bpmn-hotel-guest-pool")
def guest_pool():
    d = D("Hotel Example — Guest Pool", 800, 350)
    d.pool(18, 20, 764, 274, "Guest")
    st = d.event(86, 150, "start", None, "Plan the Trip")
    ph = d.task(130, 124, 148, 52, "Phone the Agency", marker="send")
    cf = d.event(348, 150, "intermediate", "message", "Confirmation")
    gw = d.gateway(432, 150, "exclusive")
    pay = d.task(508, 124, 148, 52, "Pay for the Booking")
    end = d.event(712, 150, "end", None, "Trip Booked")
    els = d.event(538, 66, "end", None, "Book Elsewhere")
    tm = d.event(348, 250, "intermediate", "timer", "no reply")
    ch = d.task(410, 226, 148, 48, "Chase the Agency", marker="send")
    d.flow(st, ph, sides=("r", "l"))
    d.flow(ph, cf, sides=("r", "l"))
    d.flow(cf, gw, sides=("r", "l"))
    d.flow(gw, pay, "accepted", sides=("r", "l"), ly=-2)
    d.flow(pay, end, sides=("r", "l"))
    d.flow(gw, els, "rejected", via=[(432, 66)], sides=("t", "l"), ly=-2)
    d.flow(cf, tm, sides=("b", "t"))
    d.flow(tm, ch, sides=("r", "l"))
    d.flow(ch, cf, via=[(600, 250), (600, 200), (316, 200), (316, 150)],
           sides=("r", "l"))
    d.note(400, 328, "one participant, one token, all of the control local to it — "
                     "this is the conductor from round 4", MUTED, 13)
    return d


@figure("bpmn-hotel-agency-pool")
def agency_pool():
    """No gateway here on purpose. Pattern 4 already taught the exclusive gateway,
    and the accept/reject branch drawn in this lane collided with the flow coming up
    from the fax operator -- so this figure shows what the slide's marker asks for
    and nothing more: create, fax, receive, take payment, confirm."""
    d = D("Hotel Example — Just Paper Hotels Pool", 980, 350)
    d.pool(18, 20, 944, 282, "Just Paper Hotels",
           lanes=[(141, "Booking Team"), (141, "Fax Operator")])
    st = d.event(112, 90, "start", "message", "Call Received")
    tc = d.task(158, 66, 132, 48, "Take the Call", marker="user")
    cr = d.task(326, 66, 152, 48, "Create Booking\nRequest")
    fx = d.task(326, 208, 152, 48, "Fax the Hotel", marker="send")
    rx = d.event(556, 232, "intermediate", "message", "Accept / Reject")
    tp = d.task(610, 66, 132, 48, "Take Payment")
    cg = d.task(770, 66, 148, 48, "Confirm to Guest", marker="send")
    d.flow(st, tc, sides=("r", "l"))
    d.flow(tc, cr, sides=("r", "l"))
    d.flow(cr, fx, via=[(402, 161)], sides=("b", "t"))
    d.flow(fx, rx, sides=("r", "l"))
    d.flow(rx, tp, via=[(556, 140), (676, 140)], sides=("t", "b"))
    d.flow(tp, cg, sides=("r", "l"))
    d.note(490, 328, "two lanes, one token: the fax operator and the booking team are "
                     "the same participant, so control flows between them", MUTED, 13)
    return d


@figure("bpmn-hotel-hotel-pool")
def hotel_pool():
    d = D("Hotel Example — The Hotel Pool", 900, 350)
    d.pool(18, 20, 864, 282, "The Hotel",
           lanes=[(141, "Concierge"), (141, "Front Desk")])
    st = d.event(142, 62, "start", "message", "Booking Request")
    ti = d.task(196, 38, 150, 48, "Take Request\nfrom Inbox")
    ca = d.task(400, 178, 156, 48, "Check Availability")
    gw = d.gateway(622, 202, "exclusive")
    ac = d.task(712, 38, 146, 48, "Accept Booking", marker="send")
    rj = d.task(712, 178, 146, 48, "Reject Booking", marker="send")
    d.flow(st, ti, sides=("r", "l"))
    d.flow(ti, ca, via=[(271, 132), (478, 132)], sides=("b", "t"))
    d.flow(ca, gw, sides=("r", "l"))
    d.flow(gw, ac, "room free", via=[(622, 62)], sides=("t", "l"), ly=-2)
    d.flow(gw, rj, "hotel full", sides=("r", "l"), ly=-2)
    d.note(450, 328, "the same shape a third time — which is the point of showing it "
                     "a third time", MUTED, 13)
    return d


@figure("bpmn-hotel-pools-and-lanes")
def pools_and_lanes():
    """The attempt that does NOT work -- five lanes in one pool. Red marks why."""
    d = D("Hotel Example — Pools and Lanes", 800, 470)
    d.pool(18, 56, 764, 360, "One pool, five lanes",
           lanes=[(72, "Guest"), (72, "Booking Team"), (72, "Fax Operator"),
                  (72, "Concierge"), (72, "Front Desk")], accent=True)
    a = d.task(120, 70, 152, 44, "Phone the Agency", marker="send")
    b = d.task(316, 142, 152, 44, "Create Booking\nRequest", size=11)
    c = d.task(316, 214, 152, 44, "Fax the Hotel", marker="send")
    e = d.task(512, 286, 152, 44, "Take Request\nfrom Inbox", size=11)
    f = d.task(512, 358, 152, 44, "Check Availability")
    d.flow(a, b, via=[(294, 92), (294, 164)], sides=("r", "l"))
    d.flow(b, c, sides=("b", "t"))
    d.flow(c, e, via=[(490, 236), (490, 308)], sides=("r", "l"))
    d.flow(e, f, sides=("b", "t"))
    d.note(400, 34, "a message event refers to a message from outside — "
                    "and drawn this way, there is no outside", ANNOTATION, 17)
    d.note(400, 446, "some tasks here are about the interaction, others are oblivious "
                     "to it. One token cannot be both.", MUTED, 13)
    return d


@figure("bpmn-hotel-collaboration")
def collaboration():
    """Three pools with message flows between them. This is the figure that carries
    the section's load-bearing line, so it is the one that gets the red."""
    d = D("Just Paper Hotels Collaboration", 820, 586)
    d.pool(18, 56, 784, 96, "Guest")
    d.pool(18, 208, 784, 180, "Just Paper Hotels",
           lanes=[(90, "Booking Team"), (90, "Fax Operator")])
    d.pool(18, 444, 784, 96, "The Hotel")

    g1 = d.task(130, 82, 148, 44, "Phone the Agency", marker="send")
    g2 = d.task(578, 82, 148, 44, "Pay for the Booking")
    a1 = d.task(130, 231, 148, 44, "Create Booking\nRequest", size=11)
    a2 = d.task(578, 231, 148, 44, "Confirm to Guest", marker="send")
    a3 = d.task(316, 321, 148, 44, "Fax the Hotel", marker="send")
    h1 = d.task(316, 470, 148, 44, "Check Availability")
    h2 = d.task(500, 470, 148, 44, "Accept / Reject", marker="send")

    d.flow(g1, a1, "booking request", message=True, sides=("b", "t"), lx=66)
    d.flow(a1, a3, via=[(204, 343)], sides=("b", "l"))
    d.flow(a3, h1, "fax", message=True, sides=("b", "t"), lx=22)
    d.flow(h1, h2, sides=("r", "l"))
    d.flow(h2, a2, "accept / reject", message=True,
           via=[(574, 420), (652, 420)], sides=("t", "b"), lx=-58)
    d.flow(a2, g2, "confirmation", message=True, sides=("t", "b"), lx=-62)

    d.note(410, 32, "no token crosses a message flow", ANNOTATION, 18)
    d.note(410, 568, "sequence flow is what happens at a desk. Message flow is what "
                     "happens between desks.", MUTED, 13)
    return d


@figure("bpmn-hotel-choreography")
def choreography():
    """The same exchange with every participant's insides removed. In a choreography
    task the two bands name who speaks and who is spoken to; the initiator's band is
    the unshaded one. Nothing here belongs to anybody."""
    d = D("Hotel Example — BPMN Choreography", 820, 286)
    steps = [
        (60, "Booking Request", "Guest", "Just Paper Hotels"),
        (248, "Fax the Booking", "Just Paper Hotels", "The Hotel"),
        (436, "Accept / Reject", "The Hotel", "Just Paper Hotels"),
        (624, "Booking Confirmed", "Just Paper Hotels", "Guest"),
    ]
    boxes = [d.choreo(x, 110, 168, 96, label, top, bottom)
             for x, label, top, bottom in steps]
    for a, b in zip(boxes, boxes[1:]):
        d.flow(a, b, sides=("r", "l"))
    d.note(410, 58, "no owner, no token, no shared state — only the order of the "
                    "messages", ANNOTATION, 17)
    d.note(410, 256, "the unshaded band is who speaks first. Past here the flow goes "
                     "blind — the event horizon.", MUTED, 13)
    return d


# ---- compensation -------------------------------------------------------------

@figure("bpmn-compensation-fragment")
def compensation_fragment():
    d = D("Compensation, attached to the task", 560, 270)
    do = d.task(70, 64, 180, 60, "Take Payment")
    ev = d.event(210, 124, "intermediate", "compensation", None, r=15)
    undo = d.task(330, 168, 180, 64, "Refund the Card", marker="compensate")
    d.arrow(ev, undo, dashed=True, muted=True, sides=("b", "l"),
            via=[(210, 198)])
    d.note(112, 166, "compensation event,\nattached to the task", MUTED, 13)
    d.note(280, 34, "the undo lives with the task it undoes", ANNOTATION, 17)
    d.note(280, 254, "you cannot roll back across desks, so for every do you write "
                     "an undo", MUTED, 13)
    return d


# ---- the side-by-side that opens the section ---------------------------------

@figure("bpmn-your-flow-side-by-side")
def your_flow_side_by_side():
    """The delegates' own Pre-Arrival flow beside the same flow as BPMN.

    This is the only figure in Phase 2 that embeds an existing artefact rather than
    drawing it: the left half has to be the thing the room actually made, or the
    slide's promise -- you drew this an hour ago -- is not kept. The BPMN half is a
    compact recomposition of the collaboration figure, sized to sit beside a portrait
    image without either half shrinking to nothing.
    """
    d = D("Your Flow, in the Standard Notation", 1240, 600)
    d.image(30, 66, 398, 480, os.path.join(OUT, "Pre-Arrival Guest Flow.png"))

    d.pool(470, 96, 740, 92, "Guest")
    d.pool(470, 226, 740, 160,
           "Just Paper Hotels", lanes=[(80, "Booking Team"), (80, "Fax Operator")])
    d.pool(470, 424, 740, 92, "The Hotel")

    g1 = d.task(560, 120, 130, 44, "Phone the Agency", marker="send", size=11)
    g2 = d.task(886, 120, 138, 44, "Pay for the Booking", size=11)
    a1 = d.task(560, 244, 130, 44, "Create Booking\nRequest", size=10)
    a2 = d.task(886, 244, 138, 44, "Confirm to Guest", marker="send", size=11)
    a3 = d.task(720, 324, 130, 44, "Fax the Hotel", marker="send", size=11)
    h1 = d.task(720, 448, 130, 44, "Check Availability", size=11)
    h2 = d.task(890, 448, 130, 44, "Accept / Reject", marker="send", size=11)

    d.flow(g1, a1, message=True, sides=("b", "t"))
    d.flow(a1, a3, via=[(625, 346)], sides=("b", "l"))
    d.flow(a3, h1, message=True, sides=("b", "t"))
    d.flow(h1, h2, sides=("r", "l"))
    d.flow(h2, a2, message=True, sides=("t", "b"))
    d.flow(a2, g2, message=True, sides=("t", "b"))

    d.note(620, 40, "you already had every concept — this is only the vocabulary",
           ANNOTATION, 18)
    d.note(229, 574, "the desk, the tray, the heavy bar", MUTED, 14)
    d.note(840, 574, "the task, the message flow, the pool", MUTED, 14)
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
        d = fn()
        _, png = d.save(os.path.join(OUT, name))
        print(f"  {name:<34} {d.w}x{d.h}  {os.path.getsize(png):>8,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
