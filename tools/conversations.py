#!/usr/bin/env python3
"""§Conversations' one drawn figure -- plan §8 class D.

    python3 tools/conversations.py                  # rebuild
    python3 tools/conversations.py --list

**A family of one, and it should not stay that way.** §Conversations still carries
three pictures from the 2021 deck -- `Practical Messaging - Day 2 - 2024 - 25/27/29.png`
on *Messaging or Eventing?* -- and they are whole exported slides, complete with their
old titles, their red commentary boxes and a `Ian Cooper 25` footer. They are *linked*,
so they do not show up as work outstanding, but they are the last three pictures on
Day 1 that are not ours. **Redrawing them is the obvious next batch, and this module is
where they would go** -- they are the same two participants having the same kind of
conversation. It is an offer on Ian's desk, not a decision taken here.

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

    d.box(60, 130, 220, 100, "Requestor")
    d.box(920, 130, 220, 100, "Provider")
    d.rule(170, 230, 0, MUTED, 1.1, h=320)
    d.rule(1030, 230, 0, MUTED, 1.1, h=320)

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
