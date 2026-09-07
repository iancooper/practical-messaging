#!/usr/bin/env python3
"""§Conversations' two figures -- plan §8 class D, and the 2021 redraw Ian asked for.

    python3 tools/conversations.py                  # rebuild both
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
nowhere else said so. The two lifelines are `MUTED` hairlines at 1.1pt, which is what
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


def participants(d, lx, rx, top, bottom, w=220, h=96,
                 left="Requestor", right="Provider"):
    """The two parties and the lifelines they talk down, given as centre-lines.

    **Both figures in this module draw the same two boxes, so they are drawn here.**
    `lx` and `rx` are the *centres*, because every exchange in the module is anchored
    to a lifeline rather than to a box edge, and a figure that has to compute
    `x + w / 2` at every call site will get one of them wrong.

    The lifelines are `MUTED` hairlines: they are guides, which is what muted is for,
    and they must stay clearly unlike the 2.6pt ink rule §1 and §3 use for a process
    boundary.
    """
    d.box(lx - w / 2, top, w, h, left)
    d.box(rx - w / 2, top, w, h, right)
    d.rule(lx, top + h, 0, MUTED, 1.1, h=bottom - top - h)
    d.rule(rx, top + h, 0, MUTED, 1.1, h=bottom - top - h)


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

    participants(d, 170, 1030, 130, 550, h=100)

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

    participants(d, 440, 970, 120, 630)

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
