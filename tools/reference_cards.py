#!/usr/bin/env python3
"""The two delegate reference cards — one per pack, one A4 side each.

    python3 tools/reference_cards.py            # rebuild both
    python3 tools/reference_cards.py --list

**These are print, not slides**, and that changes three things about them.

1. **No `compact()`.** Every other family is fitted to a 16:9 stage and its labels
   are sized for a room. These are held at arm's length, so the canvas is A4's own
   1 : 1.414 and the type is sized for paper. `tools/reads_at.py` does not list them
   and should not — its whole question is "can the back row read this", and the back
   row is not holding the card.
2. **Plex Sans throughout, in both cards.** `styles.md` reserves Caveat for callouts
   and diagram labels; a lookup table is neither. The BPMN card is Plex anyway,
   being BPMN. The Day 1 card is Plex because it is a *table of other people's
   product names* — `AMQP 0-9-1`, `gRPC` — and a hand face makes those look like our
   remarks about them rather than the things themselves.
3. **Mono-safe.** The one red idea also carries a filled dot, because a printed card
   goes through whatever machine the venue has. Red alone would come out as grey and
   the mark would stop meaning anything.

**Why there are two.** Ian settled *one card per pack* on 2026-09-08 (plan §8 item 8),
over a Day 1 side on the back of the BPMN card. A delegate holding the Day 1 card is
being asked *which integration style*; one holding the Day 2 card is reading a BPMN
diagram. They are not the same moment, and they are eight hours apart.

**The BPMN card is the only place in either day that shows an element the deck does
not use.** That is deliberate and the slide says so out loud: *BPMN — Tasks, Events
and Gateways* teaches six, its presenter note is *"do not read the lists"*, and its
figure's foot reads *"every other task type, event and gateway is on the reference
card in your pack"*. This is that card, so the promise has to be kept in full — all
eight task types, all nine event triggers, all five gateways. Drawing them cost the
fifteen BPMN glyphs `bpmn_shopping.py` predicted it would; they are in `diagram.py`
now, and every existing figure still rebuilds byte-identical.

**The three `.drawio` sources carry no text at all.** `Task Types.drawio`,
`Event Types.drawio` and `Gateway Types.drawio` are unlabelled icon sheets — every
`value=""` — so "lay out from the sources" was always going to mean draw them. The
element *set* is taken from them; the words are the outline's own.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import (Diagram, _Outliner, ANNOTATION, COMMENT, MUTED,   # noqa: E402
                     INK, PLAIN)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
FIGURES = {}

# A4 portrait, 1 : 1.4142. Rendered at scale 3 this is 2400 x 3393, which is 290dpi
# on an A4 side -- past what any office printer resolves, and small enough to mail.
W, H = 800, 1131
M = 46                      # side margin
COL = (M, 414)              # the two column origins
CW = 340                    # usable width in a column


def card(title):
    """Straight-stroked, Plex Sans -- see the module docstring."""
    return Diagram(title, w=W, h=H, sketch=False, font=PLAIN)


def figure(name):
    def wrap(fn):
        FIGURES[name] = fn
        return fn
    return wrap


def _head(d, y, text, gloss):
    """A block heading with its one-line definition ranged right against it."""
    d.note(M, y, text, INK, 21, anchor="start", font=PLAIN)
    d.note(W - M, y, gloss, COMMENT, 14, anchor="end", font=PLAIN)
    d.rule(M, y + 12, W - 2 * M, INK, 1.3)


def _entry(d, x, y, name, gloss, six=False, tx=98):
    """The text half of a legend row: the element's name, then what it means.

    `six` marks one of the six the deck actually uses. It is the card's single red
    idea, and it is a **dot as well as a colour** -- see the module docstring on
    printing.
    """
    if six:
        d.point(x + tx + 6, y - 5, r=4.5, accent=True)
    d.note(x + tx + (20 if six else 0), y, name, INK, 16, anchor="start", font=PLAIN)
    d.note(x + tx, y + 19, gloss, COMMENT, 13.5, anchor="start", font=PLAIN)


# ---------------------------------------------------------------------------
#  Day 2 -- BPMN
# ---------------------------------------------------------------------------

TASKS = (
    # marker, name, gloss, one-of-the-six
    (None,      "Generic",       "work; how it happens is not modelled", False),
    ("service", "Service",       "calls something that is not a person", True),
    ("receive", "Receive",       "waits for a message to arrive",        True),
    ("send",    "Send",          "sends a message and carries on",       False),
    ("user",    "User",          "a person does it, helped by software", False),
    ("manual",  "Manual",        "a person does it, no software at all", False),
    ("rule",    "Business Rule", "asks a rules engine for a decision",   False),
    ("script",  "Script",        "the engine runs the script itself",    False),
)

EVENTS = (
    # symbol, name, gloss, one-of-the-six
    (None,           "None",         "no trigger — the ring alone says when", False),
    ("message",      "Message",      "something arrived from another party", True),
    ("timer",        "Timer",        "enough time passed",                   True),
    ("signal",       "Signal",       "a broadcast; anyone listening reacts", False),
    ("compensation", "Compensation", "undo work that already completed",     False),
    ("conditional",  "Conditional",  "a condition became true",              False),
    ("escalation",   "Escalation",   "hand it up; someone else deals with it", False),
    ("parallel",     "Parallel",     "several triggers, and all happened",   False),
    ("cancel",       "Cancel",       "a transaction is being abandoned",     False),
)

GATEWAYS = (
    ("exclusive", "Exclusive",   "one path, and only one",     True),
    ("inclusive", "Inclusive",   "every path that is true",    False),
    ("parallel",  "Parallel",    "every path; token splits",   True),
    ("complex",   "Complex",     "the rule is on the diagram", False),
    ("event",     "Event-based", "first event picks the path", False),
)


@figure("card-bpmn-reference")
def bpmn_reference():
    """The Day 2 pack's card: every task type, event trigger and gateway.

    **The ring key is the half that is not on any slide.** The deck only ever draws
    a start event, an end event and a catching intermediate one, so a delegate
    reading somebody else's diagram meets throwing and non-interrupting events for
    the first time with no idea they are a different thing. The symbol says *what*
    and the ring says *when and which way it points*, and that is a rule, not a list
    -- so it is drawn as one, six glyphs across the middle of the card.
    """
    d = card("BPMN — Reference Card")

    d.note(M, 54, "BPMN — Reference Card", INK, 27, anchor="start", font=PLAIN)
    d.note(W - M, 54, "Day 2 · Process Automation", COMMENT, 14, anchor="end",
           font=PLAIN)
    d.note(M, 82, "the six with a red dot do nearly all the work — the rest are here "
                  "so you can read someone else's diagram",
           ANNOTATION, 14.5, anchor="start", font=PLAIN)
    d.rule(M, 98, W - 2 * M, INK, 1.8)

    # ---- tasks ---------------------------------------------------------------
    _head(d, 140, "TASKS", "atomic activities — where the work gets done")
    for i, (marker, name, gloss, six) in enumerate(TASKS):
        x, y = COL[i // 4], 178 + (i % 4) * 54
        d.task(x, y, 82, 40, "", marker=marker)
        _entry(d, x, y + 18, name, gloss, six)

    d.note(M, 408, "and two markers, which any of the eight can carry:",
           COMMENT, 13.5, anchor="start", font=PLAIN)
    for i, (name, gloss, sub, dbl) in enumerate((
            ("Loop", "repeats until its condition is met", "loop", False),
            ("Transaction", "commits or compensates as a whole", None, True))):
        x, y = COL[i], 424
        d.task(x, y, 82, 40, "", sub=sub, double=dbl)
        _entry(d, x, y + 18, name, gloss)

    # ---- events --------------------------------------------------------------
    _head(d, 508, "EVENTS", "something happens: a flow begins, ends or is interrupted")
    for i, (symbol, name, gloss, six) in enumerate(EVENTS):
        x, y = COL[i // 5], 542 + (i % 5) * 52
        d.event(x + 24, y + 6, "intermediate", symbol, "", r=21)
        _entry(d, x, y + 4, name, gloss, six, tx=62)

    d.note(M, 806, "the symbol says WHAT; the ring says when, and which way it points:",
           COMMENT, 13.5, anchor="start", font=PLAIN)
    for i, (kind, sym, fill, nonint, text) in enumerate((
            ("start",        None,      False, False, "start — begins a flow"),
            ("intermediate", None,      False, False, "intermediate — during a flow"),
            ("end",          None,      False, False, "end — finishes a flow"),
            ("intermediate", "message", False, False, "catching — this flow waits"),
            ("intermediate", "message", True,  False, "throwing — this flow raises it"),
            ("intermediate", "message", False, True,  "non-interrupting — flow goes on"))):
        x = M + (i % 3) * 236
        y = 834 + (i // 3) * 50
        d.event(x + 18, y, kind, sym, "", r=16, filled=fill, nonint=nonint)
        d.note(x + 40, y + 5, text, INK, 13.5, anchor="start", font=PLAIN)

    # ---- gateways ------------------------------------------------------------
    _head(d, 950, "GATEWAYS", "branch and converge sequence flow")
    for i, (kind, name, gloss, six) in enumerate(GATEWAYS):
        x = M + (i % 3) * 236
        y = 980 + (i // 3) * 58
        d.gateway(x + 26, y + 16, kind, "", r=23)
        _entry(d, x, y + 12, name, gloss, six, tx=62)
    return d


# ---------------------------------------------------------------------------
#  Day 1 -- coupling, the four styles, and what people actually use
# ---------------------------------------------------------------------------

# Myers' scale, tightest first, with the glosses §Coupling uses. The first two are
# `prevented`: drawing a process boundary takes them off the table, which is the
# payoff the section opens on.
SCALE = (
    ("Content", "one party reaches into the other's internals", True),
    ("Common",  "both parties share the same mutable store", True),
    ("Control", "you say what to DO, not what happened", False),
    ("Stamp",   "a whole structure passed, and part of it used", False),
    ("Data",    "exactly what is needed, and nothing else", False),
)

# *Must We Both Be Up?*, verbatim. The bolded cells are the ones the slide bolds.
TEMPORAL = (
    ("Shape",             "Request → Reply",  False, "Store and forward",      False),
    ("Both present?",     "Yes",              False, "No — pick it up later",  False),
    ("Analogy",           "A phone call",     False, "Snail mail",             False),
    ("Temporal coupling", "Introduces it",    True,  "Avoids it",              True),
)

# *Why Messaging*, verbatim -- including the verdict on Messaging, which is
# "your choice" and not "data". Plan §8 item 9 records why that correction matters:
# it is the whole reason the rest of the course exists.
STYLES = (
    ("File Transfer",         "Data",        False, "No",  False,
     "Nothing — but you get nothing either"),
    ("Shared Database",       "Common",      True,  "No",  False,
     "The boundary itself"),
    ("Remote Procedure Call", "Control",     True,  "Yes", True,
     "Independent availability"),
    ("Messaging",             "Your choice", True,  "No",  False,
     "Nothing"),
)

# The broker list taken off *Must We Both Be Up?* by the overflow pass -- plan §8
# item 8 records it verbatim, and this card is now its only home. The tag beside
# each is what it IS, in this course's vocabulary: S3 is on the asynchronous side
# because it is file transfer, and file transfer is a channel that happens to be a
# filesystem.
OPTIONS = (
    ("SYNCHRONOUS", "both parties up, request and reply", (
        ("OpenAPI", "HTTP, and a schema for it"),
        ("GraphQL", "the client says what it wants"),
        ("gRPC", "binary RPC over HTTP/2"),
        ("Thrift", "binary RPC"),
        ("SOAP", "RPC in XML, over anything"),
    )),
    ("ASYNCHRONOUS", "store and forward; nobody waits", (
        ("SQS", "queue"),
        ("Kafka", "stream"),
        ("AMQP 0-9-1 (RMQ)", "queues, routed by the broker"),
        ("AMQP 1-0", "a wire protocol, not a broker"),
        ("MQTT", "publish-subscribe, for devices"),
        ("S3", "file transfer, in a bucket"),
    )),
)


def _row(d, y, cells, size=13.5):
    """One line of a table: (x, text, bold, colour) per cell."""
    for x, text, bold, col in cells:
        d.note(x, y, text, col, size, anchor="start", font=PLAIN,
               weight=700 if bold else None)


@figure("card-integration-options")
def integration_options():
    """The Day 1 pack's card: the two axes, the four styles scored on them, and
    what people actually reach for.

    **Its job is the question, not the list.** Plan §8 item 8 records this card as
    the home of the broker list the overflow pass took off *Must We Both Be Up?*,
    and it also says what a delegate holding it is being asked: *which integration
    style*. Eleven product names cannot answer that on their own, so the axes and
    the scoring table come with them — and Ian settled it that way on 2026-09-09.

    **The scale is the slide's own drawing, turned on its side.**
    `coupling-scale-boundary` runs Myers' scale vertically with the boundary as a
    rule across it and the two prevented kinds struck through in red. The same
    idiom is used here so a delegate recognises it, and for the same reason: a
    boundary can only be shown taking something off the table if there is an
    above-the-line and a below-the-line.
    """
    d = card("Integration Options — Reference Card")

    d.note(M, 54, "Integration Options", INK, 27, anchor="start", font=PLAIN)
    d.note(W - M, 54, "Day 1 · Coupling and Integration Styles", COMMENT, 14,
           anchor="end", font=PLAIN)
    d.note(M, 82, "“loosely coupled” is a question with two answers — what are we "
                  "coupled about, and must we both be up",
           ANNOTATION, 14.5, anchor="start", font=PLAIN)
    d.rule(M, 98, W - 2 * M, INK, 1.8)

    # ---- axis one: what are we coupled about? --------------------------------
    _head(d, 138, "WHAT ARE WE COUPLED ABOUT?", "Myers' scale, tightest first")
    for i, (name, gloss, prevented) in enumerate(SCALE):
        y = 178 + i * 30 + (34 if i >= 2 else 0)
        d.note(M + 4, y, name, INK, 16, anchor="start", font=PLAIN)
        d.note(M + 132, y, gloss, COMMENT, 13.5, anchor="start", font=PLAIN)
        if prevented:
            # The strike has to end with the word. Measured rather than guessed:
            # a fixed width leaves a red dash hanging off the shorter name, which
            # reads as a leader line to the gloss instead of a deletion.
            adv = _Outliner.outline(name, PLAIN, 16, 0, 0, "middle")[1]
            d.rule(M, y - 5, adv + 12, ANNOTATION, 2.2)
    d.rule(M, 224, W - 2 * M, INK, 3)
    d.note(W - M, 244, "the process boundary prevents the top two — private data, "
                       "no shared transaction", INK, 13.5, anchor="end", font=PLAIN)

    # ---- axis two: must we both be up? ---------------------------------------
    _head(d, 374, "MUST WE BOTH BE UP?", "the axis that multiplies your outages")
    C2 = (M + 4, 268, 530)
    _row(d, 410, ((C2[0], "", False, INK),
                  (C2[1], "Synchronous conversation", False, INK),
                  (C2[2], "Asynchronous conversation", False, INK)), size=15)
    d.rule(M, 420, W - 2 * M, MUTED, 1.1)
    for i, (label, a, ab, b, bb) in enumerate(TEMPORAL):
        y = 446 + i * 26
        _row(d, y, ((C2[0], label, False, COMMENT),
                    (C2[1], a, ab, INK),
                    (C2[2], b, bb, INK)))
    d.note(M + 4, 560, "call four services at 99.9% and wait for each: you are at "
                       "99.6% before anything has actually failed",
           COMMENT, 13.5, anchor="start", font=PLAIN)

    # ---- the four styles, scored on both axes --------------------------------
    _head(d, 606, "FOUR STYLES", "the two axes, answered")
    C4 = (M + 4, 262, 402, 500)
    _row(d, 642, ((C4[0], "Style", False, COMMENT),
                  (C4[1], "Coupled about", False, COMMENT),
                  (C4[2], "Both up?", False, COMMENT),
                  (C4[3], "What it hands back", False, COMMENT)), size=13)
    d.rule(M, 652, W - 2 * M, MUTED, 1.1)
    for i, (name, about, ab, up, ub, back) in enumerate(STYLES):
        y = 678 + i * 28
        _row(d, y, ((C4[0], name, False, INK),
                    (C4[1], about, ab, INK),
                    (C4[2], up, ub, INK),
                    (C4[3], back, False, COMMENT)))
    d.note(M + 4, 798, "File Transfer and Messaging land in the same cell — what "
                       "separates them: ordering, locking, delivery and "
                       "timeliness",
           COMMENT, 13.5, anchor="start", font=PLAIN)

    # ---- and what people actually use ----------------------------------------
    _head(d, 846, "OPTIONS", "the same two answers, in products")
    for c, (head, gloss, items) in enumerate(OPTIONS):
        x = COL[c]
        d.note(x + 4, 882, head, INK, 15, anchor="start", font=PLAIN)
        d.note(x + 4, 901, gloss, COMMENT, 13, anchor="start", font=PLAIN)
        for i, (name, tag) in enumerate(items):
            y = 930 + i * 26
            d.note(x + 4, y, name, INK, 14.5, anchor="start", font=PLAIN)
            d.note(x + 140, y, tag, COMMENT, 12.5, anchor="start", font=PLAIN)
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
