#!/usr/bin/env python3
"""The two If-Later figures for Day 1 §6.3 -- plan §8 item 6.

    python3 tools/if_later.py                       # rebuild both
    python3 tools/if_later.py if-later-stream
    python3 tools/if_later.py --list

**They are a pair, and they contrast through red**, which is the convention the 12
EIP figures set. Both slides describe the same trick -- a versioned Summary Event
means a later message supersedes an earlier one -- but they spend it on different
problems, so each figure reds the mechanism its own slide introduces:

  * **stream** reds the **discard**: v2 arrives after v3 and is thrown away.
  * **queue** reds the **read-past**: the second consumer does not wait for the first.

Getting that the wrong way round would make them look like the same picture drawn
twice, which is what the section is trying not to be.

**Read order is drawn, not implied.** Both figures lay the envelopes out left to right
in the order the consumer takes them, and say so, because the natural EIP reading --
nearest the consumer is next -- gives the opposite answer and the whole point of these
slides is which message was seen when.

Hand-drawn register, like the rest of Day 1.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, COMMENT, MUTED, INK          # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
FIGURES = {}


def figure(name):
    def wrap(fn):
        FIGURES[name] = fn
        return fn
    return wrap


@figure("if-later-stream")
def if_later_stream():
    """*If Later, Stream.* The consumer reads v1, then v3, then v2 -- and discards the
    last one. The slide's own sequence, and the presenter note's reason: with complete
    versions you can write v2 without ever seeing v1, because v2 either overwrites or
    includes it.

    The red is on the **discard**, because that is the counter-intuitive half: a
    message is dropped and nothing is broken. On a delta stream the same drop would
    leave the replica permanently wrong, which is the previous slide's argument.
    """
    d = Diagram("If Later — on a Stream", w=1120, h=440)
    d.note(560, 44, "the late message is discarded, not repaired — "
                    "v3 already says everything v2 says", ANNOTATION, 19)

    d.note(430, 108, "the consumer reads left to right", COMMENT, 14)
    pipe = d.pipe(110, 150, 660, 72)

    for x, ver, verdict, col in (
            (190, "12345 v1", "read 1st — apply", INK),
            (400, "12345 v3", "read 2nd — apply,\nit is later", INK),
            (610, "12345 v2", "read 3rd — discard,\nit is earlier", ANNOTATION)):
        d.note(x + 26, 138, ver, INK, 15)
        d.msg(x, 168, "", w=52, h=36, accent=col is ANNOTATION)
        d.note(x + 26, 258, verdict, col, 14)

    con = d.box(830, 152, 220, 84, "Consumer\napplying write-if-later")
    d.arrow(pipe, con, sides=("r", "l"))
    store = d.cylinder(860, 318, 160, 78, "the replica\n12345 is at v3")
    d.arrow(con, store, sides=("b", "t"))

    d.note(430, 320, "a Summary Event is complete in itself, so a version\n"
                     "that arrives late is not a gap — it is just old", COMMENT, 15)
    return d


@figure("if-later-queue")
def if_later_queue():
    """*If Later, Queue.* Competing consumers on a queue, and **read-past** -- the
    second consumer takes v2 rather than waiting behind v1.

    The red is on the read-past, because that is what this slide adds: the stream
    figure has already made discarding safe, and what is new here is that two
    consumers may run at once without a sequencer. The store note carries the
    consequence -- whichever finishes last, v2 is what remains.

    The slide's caveat is drawn as a muted note rather than left to the presenter:
    where a message genuinely must be ordered, this does not apply, and requeue with
    delay or a sequencer is the answer.
    """
    d = Diagram("If Later — on a Queue with Competing Consumers", w=1120, h=600)
    d.note(560, 44, "the second consumer reads past and takes v2 — "
                    "it does not wait for the first", ANNOTATION, 19)

    d.note(360, 108, "the consumer reads left to right", COMMENT, 14)
    pipe = d.pipe(90, 150, 540, 72)
    for x, ver, accent in ((150, "12345 v1", False), (330, "12345 v2", True),
                           (510, "12345 v3", False)):
        d.note(x + 26, 138, ver, INK, 15)
        d.msg(x, 168, "", w=52, h=36, accent=accent)

    a = d.box(760, 116, 210, 76, "Consumer A")
    b = d.box(760, 262, 210, 76, "Consumer B")
    d.arrow(pipe, a, "takes v1", sides=("r", "l"), ly=-16)
    d.arrow(pipe, b, "reads past, takes v2", accent=True, sides=("r", "l"),
            lx=-26, ly=18)

    store = d.cylinder(785, 424, 160, 78, "the replica\n12345 is at v2")
    # A's write has to go round the outside: straight down would cut through B
    d.arrow(a, store, "writes v1", sides=("r", "r"),
            via=[(1035, 154), (1035, 463)], lx=-8)
    d.arrow(b, store, "writes v2", sides=("b", "t"), lx=52)
    d.note(865, 538, "whichever of them finishes last, v2 is what remains",
           COMMENT, 15)

    d.note(300, 330, "this is a queue, not a stream — it carries messages,\n"
                     "and a message that must be ordered cannot use it.\n"
                     "For those, requeue with delay, or a sequencer.", COMMENT, 15)
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
        print(f"  {name:<22} {dg.w}x{dg.h}  {os.path.getsize(png):>8,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
