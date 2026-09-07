#!/usr/bin/env python3
"""Day 1 §4.5 *Queues and Streams*, plus §4.4's requeue diagram.

    python3 tools/queues_streams.py                 # rebuild all
    python3 tools/queues_streams.py qs-queue-tasks
    python3 tools/queues_streams.py --list

**The section is one long comparison, so the figures are built from one pair of
shapes and never vary them.** A queue is always `pipe` + loose `msg` envelopes; a
stream is always a `log` -- contiguous cells with offsets underneath. Ten slides
argue queue-versus-stream, and if both were drawn as a pipe with envelopes in it the
room would have to be *told* the difference every time instead of seeing it.

Two more constants across the run, for the same reason:

  * **consumers are always on the right, the broker always on the left**, so the
    eye learns one direction and the partition figures do not have to re-teach it.
  * **`lock` / `clock` / `tick` / `cross` mean exactly one thing each** — held, held
    back, has it, has not. They are the only icons in the run.

Red is spent once per figure on the thing that slide is arguing, and the two
*"no such thing"* figures (queues cannot replay, streams cannot requeue) red the
**absence**, which is the only way to draw a thing that is not there.

Hand-drawn register, like the rest of Day 1.
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


# ---- the two shapes, drawn the same way every time ---------------------------

def queue(d, x, y, w=470, h=76, n=4, hold=None, gone=(), locks=()):
    """A queue: a pipe with loose envelopes in it. `hold` reds one envelope, `gone`
    draws envelopes as already deleted, `locks` puts a padlock on the ones being
    worked.

    **A lock sits on its envelope's top-LEFT corner, always.** Arrows to consumers
    leave an envelope from the top or the bottom, and a centred padlock sits exactly
    on the one that goes up. Fixing it here rather than per figure is what keeps the
    ten drawings looking like one set.

    **The head of the queue is the RIGHT-hand envelope**, nearest the consumers, and
    the figures index from the end for that reason. The first pass locked the
    left-hand one, which forced every arrow to cross the whole queue to reach a
    consumer -- the drawing was fighting its own reading direction. Messages enter at
    the capped left end and leave at the right.
    """
    pipe = d.pipe(x, y, w, h)
    step = (w - 60) / n
    cells = []
    for i in range(n):
        cx = x + 44 + i * step
        if i in gone:
            d.icon(cx + 26, y + h / 2, "cross", accent=True, r=15)
        else:
            cells.append(d.msg(cx, y + h / 2 - 18, "", w=52, h=36,
                               accent=(i == hold)))
        if i in locks:
            d.icon(cx, y - 18, "lock", accent=(i == hold))
    return pipe, cells


def stream(d, x, y, w=470, h=64, n=6, start=0):
    """A stream: an append-only log, cells and offsets, nothing ever removed."""
    return d.log(x, y, w, h, n, start=start)


def consumers(d, x, names, y0=110, gap=132, w=190, h=72, accent=None):
    out = []
    for i, name in enumerate(names):
        out.append(d.box(x, y0 + i * gap, w, h, name,
                         accent=(accent is not None and i == accent)))
    return out


# ---- queues ------------------------------------------------------------------

@figure("qs-queue-tasks")
def queue_tasks():
    """*Queues Contain Tasks.* Lock, and read-past -- the two moves the whole queue
    half of the section is built from."""
    d = Diagram("Queues Contain Tasks", w=1080, h=470)
    d.note(540, 44, "the second consumer does not wait — it reads past the locked "
                    "message and locks the next", ANNOTATION, 19)

    pipe, cells = queue(d, 70, 190, n=4, hold=2, locks=(2, 3))
    one = d.box(790, 100, 210, 74, "Consumer One")
    two = d.box(790, 300, 210, 74, "Consumer Two")
    d.arrow(cells[3], one, "locks the one at the head", sides=("t", "l"),
            via=[(447, 137)], lx=64, ly=-14)
    d.arrow(cells[2], two, "reads past it, locks the next", accent=True,
            sides=("b", "l"), via=[(345, 337)], lx=92, ly=18)

    d.note(330, 424, "a message being worked on is locked, so nobody else can\n"
                     "action it — and a task is done once, so a receiver of a\n"
                     "done task discards it", MUTED, 15)
    return d


@figure("qs-queue-lifecycle")
def queue_lifecycle():
    """*Queue Lifecycle — Ack, Fail, Requeue.* The three endings a locked message can
    have. Red is on the dead-letter one, because it is the only ending that is not
    about this message at all -- it is about time having run out."""
    d = Diagram("Queue Lifecycle — Ack, Fail, Requeue", w=1360, h=540)
    d.note(680, 44, "unlocking is not the interesting part — what matters is "
                    "whether anyone else may try again", ANNOTATION, 19)

    pipe, cells = queue(d, 60, 148, w=340, n=3, hold=2, locks=(2,))
    con = d.box(470, 254, 190, 72, "Consumer")
    d.arrow(cells[2], con, "locks", sides=("b", "l"), via=[(273, 290)], lx=64, ly=-16)

    ok = d.box(830, 140, 200, 68, "delete it")
    again = d.box(830, 254, 200, 68, "unlock it")
    dlq = d.box(830, 402, 200, 68, "dead letter", accent=True)

    d.arrow(con, ok, "done", sides=("r", "l"), via=[(745, 290), (745, 174)], ly=-14)
    d.arrow(con, again, "failed", sides=("r", "l"), ly=-14)
    d.arrow(again, dlq, "after N tries", accent=True, sides=("b", "t"), lx=86)
    # icons sit on their box's top-left corner, as locks sit on their envelope's
    d.icon(830, 118, "tick", r=11)
    d.icon(830, 232, "clock", r=11)

    d.note(1054, 178, "nobody else can\nprocess it", MUTED, 14, anchor="start")
    d.note(1054, 276, "available to lock again,\noften after a delay — the\n"
                      "failure may be transient", MUTED, 14, anchor="start")
    d.note(1054, 430, "nobody actioned it in a\nreasonable time, which is a\n"
                      "different problem from a\nbad message", MUTED, 14,
           anchor="start")
    d.note(300, 430, "three endings, and only one of them\n"
                     "is the end of the message", MUTED, 15)
    return d


@figure("qs-queue-competing")
def queue_competing():
    """*Scaling Queues — Competing Consumers.* Deliberately the first figure again
    with one more consumer: scaling a queue introduces nothing new, and the figure
    looking familiar is the argument."""
    d = Diagram("Scaling Queues — Competing Consumers", w=1080, h=560)
    d.note(540, 44, "scaling a queue is the same two moves, more times over — "
                    "lock, read past, lock the next", ANNOTATION, 19)

    pipe, cells = queue(d, 70, 224, n=4, locks=(1, 2, 3))
    cons = [d.box(790, y, 210, 72, n) for y, n in
            ((92, "Consumer One"), (300, "Consumer Two"), (400, "Consumer Three"))]
    d.arrow(cells[3], cons[0], sides=("t", "l"), via=[(447, 128)])
    d.arrow(cells[2], cons[1], sides=("b", "l"), via=[(345, 336)])
    d.arrow(cells[1], cons[2], sides=("b", "l"), via=[(242, 436)])

    d.note(230, 150, "three held, one still waiting", MUTED, 15)
    d.note(340, 510, "add a consumer and throughput goes up — "
                     "nothing about the queue itself changes", MUTED, 15)
    return d


@figure("qs-queue-no-replay")
def queue_no_replay():
    """*Queues — No Archive and Replay.* Drawing a thing that is not there: red goes
    on the gaps where the messages used to be, at the head end they left from,
    because the gap is the slide."""
    d = Diagram("Queues — No Archive and Replay", w=1080, h=420)
    d.note(540, 44, "the message is gone, so there is nothing to replay — "
                    "your only option is to ask the producer again", ANNOTATION, 19)

    pipe, cells = queue(d, 70, 176, n=4, gone=(2, 3))
    d.note(400, 288, "processed, then deleted", ANNOTATION, 15)

    con = d.box(790, 178, 200, 72, "Consumer")
    d.arrow(pipe, con, sides=("r", "l"))
    d.note(540, 372, "a queue holds work that has not been done yet — "
                     "it was never a record of anything", MUTED, 15)
    return d


# ---- streams -----------------------------------------------------------------

@figure("qs-stream-facts")
def stream_facts():
    """*Streams Contain Facts.* Both consumers read everything, and the offset
    belongs to the consumer rather than the broker -- which is the whole difference,
    so each store is drawn under its own consumer and never shared."""
    d = Diagram("Streams Contain Facts", w=1120, h=540)
    d.note(560, 44, "nothing is consumed by reading — both consumers read every "
                    "record, and each remembers how far it got", ANNOTATION, 19)

    log = stream(d, 70, 210, w=560, h=68, n=7)
    d.note(350, 176, "the stream — nothing is ever removed", MUTED, 14)

    for i, (name, off, y) in enumerate((("Consumer One", "4", 100),
                                        ("Consumer Two", "2", 324))):
        con = d.box(790, y, 210, 74, name)
        st = d.cylinder(805, y + 100, 180, 62, f"offset store — {off}")
        d.arrow(log, con, sides=("r", "l"))
        d.arrow(con, st, sides=("b", "t"), muted=True)

    d.note(330, 380, "an offset is a consumer's own bookmark. On restart\n"
                     "it reads the store to find the last record it processed.",
           MUTED, 15)
    d.note(330, 470, "facts are an inverse database — how the current\n"
                     "state was arrived at", MUTED, 15)
    return d


@figure("qs-stream-partitions")
def stream_partitions():
    """*Scaling Streams — Partitions.* Scaling a stream, unlike scaling a queue,
    changes the stream: you have to decide what goes where, and consistent hashing is
    what buys back the ordering the split just cost you. That trade is the red."""
    d = Diagram("Scaling Streams — Partitions", w=1180, h=520)
    d.note(590, 44, "splitting the stream costs you ordering — "
                    "consistent hashing buys it back, one key at a time",
           ANNOTATION, 19)

    for i in range(3):
        y = 110 + i * 118
        log = stream(d, 190, y, w=420, h=52, n=6)
        d.note(176, y + 30, f"partition {i}", MUTED, 14, anchor="end")
        con = d.box(750, y - 4, 190, 64, f"Consumer {i + 1}")
        st = d.cylinder(1000, y - 2, 140, 60, "offset")
        d.arrow(log, con, sides=("r", "l"))
        d.arrow(con, st, sides=("r", "l"), muted=True)

    d.note(590, 470, "each consumer manages the offsets for its own partition — "
                     "there is no shared position", MUTED, 15)
    return d


@figure("qs-stream-consumer-groups")
def stream_consumer_groups():
    """*Scaling Streams — Consumer Groups.* The rule is one consumer per partition
    *at a time*, and the reason is availability, not throughput -- so the red is on
    the consumer that is holding nothing."""
    d = Diagram("Scaling Streams — Consumer Groups", w=1180, h=580)
    d.note(590, 44, "one consumer per partition at a time — the spare is there to "
                    "take over, not to help", ANNOTATION, 19)

    d.group(700, 96, 420, 380, "consumer group")

    for i in range(2):
        y = 132 + i * 130
        log = stream(d, 150, y, w=420, h=52, n=6)
        d.note(136, y + 30, f"partition {i}", MUTED, 14, anchor="end")
        con = d.box(740, y - 8, 230, 68, f"Consumer {i + 1}")
        d.arrow(log, con, sides=("r", "l"))
        d.icon(676, y + 26, "lock")

    d.box(740, 356, 230, 68, "Consumer 3", accent=True)
    d.note(855, 452, "holding nothing, and that is correct", ANNOTATION, 14)

    d.note(430, 528, "a consumer may hold more than one of the group's partitions — "
                     "but a partition is never held by two at once", MUTED, 15)
    return d


@figure("qs-stream-replay")
def stream_replay():
    """*Streams — Archive and Replay.* The offset moves; the log does not. Red is on
    the move, not on the log, because the log doing nothing is the point."""
    d = Diagram("Streams — Archive and Replay", w=1080, h=440)
    d.note(540, 44, "replay is not a feature of the stream — it is a consumer "
                    "moving its own bookmark backwards", ANNOTATION, 19)

    W, N, X0, Y = 600, 8, 90, 190
    log = stream(d, X0, Y, w=W, h=68, n=N)
    cw = W / N
    was, back = X0 + 5.5 * cw, X0 + 1.5 * cw
    d.point(was, Y - 34, "", r=6)
    d.note(was + 8, Y - 56, "was here", MUTED, 14, anchor="start")
    d.point(back, Y - 34, "", r=6, accent=True)
    d.note(back - 8, Y - 56, "reset to here", ANNOTATION, 14, anchor="end")
    d.arrow((was - 12, Y - 34), (back + 12, Y - 34), accent=True)

    con = d.box(810, 186, 200, 74, "Consumer")
    st = d.cylinder(825, 300, 170, 64, "offset store")
    d.arrow(log, con, sides=("r", "l"))
    d.arrow(con, st, sides=("b", "t"), muted=True)
    d.note(390, 332, "nothing was deleted, so the past is still there to be read",
           MUTED, 15)
    return d


@figure("qs-stream-no-requeue")
def stream_no_requeue():
    """*Streams — No Requeue or DLQ.* The other half of the drawing-an-absence pair:
    the queue figure reds messages that are gone, this one reds moves that do not
    exist. Both slides are about what the model cannot do, and they should look like
    a pair."""
    d = Diagram("Streams — No Requeue or DLQ", w=1180, h=520)
    d.note(590, 44, "nothing is locked, so nothing can be put back — requeue and "
                    "dead-letter are queue moves, and there are none here",
           ANNOTATION, 19)

    log = stream(d, 90, 148, w=460, h=62, n=7)
    con = d.box(760, 144, 200, 72, "Consumer")
    st = d.cylinder(775, 254, 170, 62, "offset store")
    d.arrow(log, con, sides=("r", "l"))
    d.arrow(con, st, sides=("b", "t"), muted=True)

    for i, (label, why) in enumerate((
            ("requeue", "there is no lock to release"),
            ("requeue with delay", "and the offset has already moved on"),
            ("dead-letter channel", "nothing was taken out, to put anywhere"))):
        y = 372 + i * 46
        d.icon(116, y, "cross", accent=True, r=12)
        d.note(142, y + 6, label, ANNOTATION, 16, anchor="start")
        d.note(392, y + 6, why, MUTED, 14, anchor="start")

    d.note(900, 392, "instead: ignore and continue (shed load),\n"
                     "retry in place (backpressure), or copy\n"
                     "to a delay or dead-letter stream", MUTED, 15)
    return d


@figure("qs-capability-matrix")
def capability_matrix():
    """*Queues vs. Streams — Capability Matrix.* The section's closing slide, and the
    only figure in the run that shows both models at once.

    **Every row deliberately has one tick and one cross.** That is not a tidy
    coincidence, it is the argument: each thing one model gives you free is a thing
    the other makes you build. A row with two ticks would not discriminate and should
    not be on the slide.

    The first row carries no icons, because *task versus fact* is not a capability --
    it is the thing the other four rows follow from.

    **No "why" column.** The first pass had one, and it read as belonging to whichever
    side it sat next to rather than to the tick it explained. Every reason is on a
    slide earlier in this same run, so the summary does not need to restate them.
    """
    d = Diagram("Queues vs. Streams — Capability Matrix", w=1120, h=600)
    d.note(560, 44, "neither column is the good one — every row you gain on one, "
                    "you give up on the other", ANNOTATION, 19)

    LX, QX, SX = 520, 700, 920
    d.note(QX, 142, "Queue", INK, 22)
    d.note(SX, 142, "Stream", INK, 22)
    d.rule(180, 168, 820, INK, 2.0)

    d.note(LX, 218, "what it carries", INK, 17, anchor="end")
    d.note(QX, 212, "a task —\ndo this", MUTED, 15)
    d.note(SX, 212, "a fact —\nthis happened", MUTED, 15)
    d.rule(180, 256, 820)

    rows = (("ordering", False, True),
            ("archive and replay", False, True),
            ("requeue, and delay", True, False),
            ("lock and read past", True, False))
    for i, (label, q, st) in enumerate(rows):
        y = 312 + i * 68
        d.note(LX, y + 6, label, INK, 17, anchor="end")
        d.icon(QX, y, "tick" if q else "cross", accent=not q, r=13)
        d.icon(SX, y, "tick" if st else "cross", accent=not st, r=13)
        if i < len(rows) - 1:
            d.rule(180, y + 34, 820)

    d.note(560, 560, "a queue is work that has not been done; a stream is a record "
                     "of what happened. Everything else follows.", MUTED, 15)
    return d


# ---- §4.4's requeue diagram, same vocabulary ---------------------------------

@figure("qs-requeue-with-delay")
def requeue_with_delay():
    """§4.4 *Requeue with Delay.* Built in this family rather than with the EIP set
    because it is queue mechanics: a reader meeting it in §4.4 and meeting the
    lifecycle figure in §4.5 has to see the same queue, or the second one teaches the
    shape again instead of the idea."""
    d = Diagram("Requeue with Delay", w=1160, h=490)
    d.note(580, 44, "a transient failure is not a bad message — "
                    "it is the same message at a bad moment", ANNOTATION, 19)

    pipe, cells = queue(d, 70, 152, w=400, n=3, hold=2, locks=(2,))
    con = d.box(590, 154, 200, 72, "Consumer")
    d.arrow(cells[2], con, "locks", sides=("r", "l"), ly=-16)

    d.arrow(con, pipe, "not acked — unlock, and hold it back", accent=True,
            via=[(690, 340), (270, 340)], sides=("b", "b"), ly=24)
    d.icon(480, 312, "clock", accent=True)

    dlq = d.box(920, 154, 200, 72, "dead letter")
    d.arrow(con, dlq, "after N tries", sides=("r", "l"), ly=-22)

    d.note(580, 436, "per-message acknowledgement, a redelivery mechanism, and a way "
                     "to hold a message back —\nask your broker for all three",
           MUTED, 15)
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
