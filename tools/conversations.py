#!/usr/bin/env python3
"""§Conversations' three figures -- plan §8 class D, and the 2021 redraw Ian asked for.

    python3 tools/conversations.py                  # rebuild all three
    python3 tools/conversations.py conversation-timeout
    python3 tools/conversations.py --list

**The 2021 exports are gone.** §Conversations used to carry three pictures from the old
deck -- `Practical Messaging - Day 2 - 2024 - 25/27/29.png` on *Messaging or
Eventing?* -- whole exported slides, complete with their old titles, their red
commentary boxes and a footer. They were *linked*, so they never showed up as work
outstanding, and they were the last three pictures on Day 1 that were not ours. Ian
asked for them, 2026-09-07, and **`conversation-messaging-or-eventing` replaces all
three**.

**Three images became one, because the slide's argument is a fork and a fork needs both
sides in one frame.** Two figures side by side on a 16:9 slide are each fitted to about
half its width, so an 890-unit canvas would read at nine real points instead of
eighteen -- **splitting a figure across a slide halves its type**. `bpmn-the-six` made
the same trade for the same reason.

**Why the marker's stopwatch became a drawing.** The `#image:` line asked for an icon
of a timer. The slide's callout is *a timeout does not tell you the request failed, it
tells you that you do not know*, and an icon cannot say that -- what says it is the
three things that are all still possible when the clock runs out, which is also the
reason the next bullet demands idempotence. Rule 3: read the slide, not the marker.

**Time runs down the page, and that is a vocabulary choice rather than a register
one.** Everything here is hand-drawn Caveat like the rest of Day 1; what is new is that
vertical position means *when*, because a conversation is a sequence and the deck has
nowhere else said so. The lifelines are `MUTED` hairlines at 1.1pt, which is what
`muted` is for -- they are guides. They are deliberately nothing like the 2.6pt ink
rule §1 and §3 use for a process boundary.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, COMMENT, MUTED, INK      # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
FIGURES = {}

TARGET_W = 890      # where the 18pt diagram floor meets the 18pt body floor


def figure(name):
    """Register a figure -- and compact it on the way out, never in `main()`."""
    def wrap(fn):
        def build():
            return fn().compact(TARGET_W)
        build.__doc__ = fn.__doc__
        build.__name__ = fn.__name__
        FIGURES[name] = build
        return fn
    return wrap


def lifelines(d, parties, top, bottom, w=220, h=96):
    """The parties and the lifelines they talk down. `parties` is a sequence of
    `(centre_x, name)`.

    **Every figure in this module draws the same boxes, so they are drawn here.**
    The x is the *centre*, because every exchange in the module is anchored to a
    lifeline rather than to a box edge, and a figure that has to compute `x + w / 2`
    at every call site will get one of them wrong.

    **Boxes first, then rules**, so a lifeline can never be painted over the box of
    the party to its left -- and so that adding a third party did not reorder the two
    figures that were here before it.

    The lifelines are `MUTED` hairlines: they are guides, which is what muted is for,
    and they must stay clearly unlike the 2.6pt ink rule §1 and §3 use for a process
    boundary.
    """
    for cx, name in parties:
        d.box(cx - w / 2, top, w, h, name)
    for cx, _ in parties:
        d.rule(cx, top + h, 0, MUTED, 1.1, h=bottom - top - h)


@figure("conversation-timeout")
def conversation_timeout():
    """*In-Out — When Nothing Comes Back at All.* The retry, and why it forces
    idempotence.

    **The red is on the clock, and the clock is the only thing the requestor knows.**
    Everything either side of it -- whether the request arrived, whether the answer was
    lost, whether the provider is still working -- is unavailable to it, and the three
    of them sit together in the gap because they are indistinguishable from where the
    requestor stands. That is the slide's callout drawn rather than asserted.

    The second `greet()` is not red. Retrying is the ordinary thing to do; what the
    slide adds is the *bill* for it, which is the note under the provider.
    """
    d = Diagram("When Nothing Comes Back at All", w=1200, h=640)
    d.note(600, 46, "a timeout does not tell you it failed — "
                    "it tells you that you do not know", ANNOTATION, 21)

    lifelines(d, [(170, "Requestor"), (1030, "Provider")], 130, 550, h=100)

    d.arrow((170, 286), (1030, 286), "greet()")
    d.icon(170, 350, "clock", accent=True, r=19)
    d.note(212, 356, "the timeout expires, and nothing has come back",
           ANNOTATION, 18, anchor="start")
    d.note(600, 412, "it never arrived  ·  the answer was lost  ·  "
                     "it is still being worked on", COMMENT, 18)
    d.arrow((170, 470), (1030, 470), "greet() — again")
    d.arrow((1030, 530), (170, 530), "acknowledge()")

    d.note(600, 596, "so the provider has to be idempotent, or de-duplicate what it "
                     "has already seen", COMMENT, 18)
    return d


@figure("conversation-messaging-or-eventing")
def messaging_or_eventing():
    """*Messaging or Eventing?* -- the first fork in the whole section, and the one
    that decides most of the rest. Replaces the three 2021 exports.

    **One pair of participants, three exchanges down them.** The 2021 set drew the same
    two boxes three times on three slides, which makes the reader re-establish who is
    who before they can compare anything. Here they are established once and the three
    patterns are three exchanges on the same two lifelines, so the only thing that
    changes between them is the arrow -- which is the whole point.

    **Requestor stays on the left in all three, including Out-Only.** It is tempting to
    swap the boxes for the eventing row so its arrow still points right; that would
    destroy the figure. The claim is that *the arrow turns round*, and an arrow only
    turns round against something that does not.

    **Red is on the notification**, because the reversal is the fork: a requestor that
    speaks first is addressing someone, and a provider that speaks first is addressing
    nobody. The slide's table says that in words; this says it in one direction change.

    The foot comment carries the one thing the drawing implies and the slide does not
    say here -- In-Out needs two arrows because a channel only goes one way. That is
    §Conversations' opening slide earning its keep two slides later.
    """
    d = Diagram("Messaging or Eventing?", w=1520, h=700)
    d.note(760, 46, "the arrow turns round — and with it, "
                    "whether you are addressing anyone", ANNOTATION, 21)

    lifelines(d, [(440, "Requestor"), (970, "Provider")], 120, 630)

    d.note(300, 296, "In-Only", INK, 18, anchor="end")
    d.arrow((440, 290), (970, 290), "request()")

    d.note(300, 406, "In-Out", INK, 18, anchor="end")
    d.arrow((440, 384), (970, 384), "request()")
    d.arrow((970, 434), (440, 434), "reaction()")

    d.note(1030, 306, "the requestor speaks first —\nit is addressing someone",
           COMMENT, 18, anchor="start")

    # The fork, and it is named on both sides. A horizontal ink rule already means "the
    # line that divides the answers" in `coupling_grids`; this is the same use of it,
    # one section along. The two words are the slide's own column heads, so they are
    # ink -- without them the rule is a divide the reader has to infer from the glosses.
    d.rule(60, 510, 1400, INK, 2.4)
    d.note(60, 484, "messaging", INK, 18, anchor="start")
    d.note(60, 552, "eventing", INK, 18, anchor="start")

    d.note(300, 592, "Out-Only", INK, 18, anchor="end")
    d.arrow((970, 586), (440, 586), "notification()", accent=True)
    d.note(1030, 602, "the provider speaks first —\nit is addressing nobody",
           COMMENT, 18, anchor="start")

    d.note(760, 674, "In-Out needs two arrows because a channel only goes one way",
           COMMENT, 18)
    return d


@figure("conversation-out-in")
def out_in():
    """*Out-In (Solicit-Response).* The provider canvasses, and the question expires.

    **Why this slide needed a picture of its own rather than a fourth row on
    `messaging_or_eventing`.** That figure's argument is the messaging/eventing fork
    and its slide's own table does not list Out-In, so a fourth exchange there would
    be answering a question the slide had not asked. What Out-In adds is not another
    direction: it is a *shape*. One provider, several subscribers, and an answer with
    a shelf life -- none of which fits on a single pair of lifelines.

    **Three lifelines, because two would make this In-Out with the roles swapped.**
    Mechanically that is exactly what it is, and drawing it that way would teach
    nothing the previous slide has not. The reason a provider speaks first *and* wants
    an answer is that it does not know who is willing, and "who is willing" needs more
    than one candidate on the page to be a question at all.

    **The nouns are the slide's own -- Delivery and two Couriers -- not Requestor and
    Provider.** The other two figures in this module are abstract because their slides
    are; this slide teaches through its example, and relabelling it would make the
    reader carry the mapping. The roles still hold their sides: the couriers are
    requestors and stay left, Delivery is the provider and stays right, so the arrow
    still leaves from the right exactly as it does for Out-Only.

    **Red is on the expiry, and that is one idea in three marks** -- the clock, the
    late `ready()`, and nothing else. The slide's coupling bullet is that both parties
    may be down and it still works, *but* a late answer is worthless; so the figure
    must not red the second courier for being unavailable. It is not unavailable. It
    answered. It answered after the work was gone, which is a different failure and is
    the one the foot comment names.
    """
    d = Diagram("Out-In (Solicit-Response)", w=1440, h=660)
    d.note(720, 46, "the provider asks who is willing — and the question expires",
           ANNOTATION, 21)

    lifelines(d, [(150, "Courier A"), (380, "Courier B"), (1290, "Delivery")],
              100, 590, w=200, h=90)

    # Both solicitations are the same message, so only the first is named. Labelling
    # the second would read as a second, different call.
    d.arrow((1290, 232), (380, 232), "solicit()")
    d.arrow((1290, 272), (150, 272))
    # The gloss belongs to the two solicitations above it, so it has to sit much
    # closer to them than to the `ready()` below -- at equal spacing it reads as an
    # annotation on the reply instead, which is the opposite of what it says.
    d.note(840, 316, "to every subscriber — it knows they exist, not who they are",
           COMMENT, 18)

    d.arrow((150, 402), (1290, 402), "ready()")

    d.icon(1290, 452, "clock", accent=True, r=19)
    d.note(1244, 458, "the solicitation expires", ANNOTATION, 18, anchor="end")

    d.arrow((380, 512), (1290, 512), "ready()", accent=True)
    d.note(840, 562, "too late to be useful — the work is already allocated",
           COMMENT, 18)

    d.note(720, 634, "a late answer is a timeout problem, not an availability one — "
                     "both of you were up", COMMENT, 18)
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
