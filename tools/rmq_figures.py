#!/usr/bin/env python3
"""The 5 RabbitMQ Quick Start figures, redrawn in the house register.

    python3 tools/rmq_figures.py            # -> resources/rmq-*.drawio + .png
    python3 tools/rmq_figures.py --list     # names only

**Why this family exists.** `exercises/Quick-Start-RMQ.pptx` is precursor reading shown
at the §4.2 exercise break -- straight after 132 slides of Field Guide. Its five diagrams
were the only images in either Quick Start deck in a register the house has no
relationship to at all: Arial, orange gradient producer/consumer boxes, red-bordered
annotation panels, and the EIP pattern names in a fifth colour (blue). The Kafka deck's
eleven are Excalidraw -- hand-drawn with handwriting labels, so off-*palette* rather than
off-register, which is G1's complaint and G1's ruling. These five are not.

The originals survive as `resources/{RMQ Primitives,rabbitmq-workflow,direct-exchange,
default-exchange,fanout-exchange}.{png,drawio}`; nothing here overwrites them.

Conventions held across the set, from styles.md:
  * carbon arrows carry flow, ink names the thing, RED MARKS ONE IDEA per figure
  * **the three exchange figures contrast THROUGH red** -- direct reds the key match,
    default reds the queue's own name, fanout reds the key being ignored. That is the
    whole difference between them, so it is the only thing allowed to be red
  * the EIP pattern name is COMMENT green: it is our remark mapping RMQ's vocabulary
    onto the deck's, not a label on a shape in the picture

**Three typos are fixed here for free**, all read out of the originals' own `.drawio`:
*"fowards"*, *"recieve"* (both `fanout-exchange`) and *"association the queue with an
exchange"* (`rabbitmq-workflow`). They are unfixable in the shipped PNGs -- nothing on
this machine re-renders draw.io text -- which is exactly the position G1 §14.3 records.

**The three exchanges are NOT composed into one figure.** They share their apparatus
exactly, which is half the composition test; the outcomes are competing fan patterns
between the same two nodes, which is the half `flow-lookup-two-answers` failed. Ian split
that one back. Three figures, three slides, as the source deck already had it.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagram import Diagram, ANNOTATION, COMMENT, INK      # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "resources")

TARGET_W = 890   # where the diagram floor meets the 18pt body floor

FIGURES = {}


def figure(name):
    """Register a figure -- and compact it on the way out, so `lint_figures.py`
    measures the drawing as rendered rather than as written."""
    def wrap(fn):
        def build():
            return fn().compact(TARGET_W)
        build.__doc__ = fn.__doc__
        build.__name__ = fn.__name__
        FIGURES[name] = build
        return fn
    return wrap


# ---- the shapes, drawn the same way every time -------------------------------

def rmq_queue(d, x, y, w=150, h=54, n=2, accent=False):
    """An RMQ queue: a channel with messages waiting in it.

    **`accent` reds the MESSAGES and never the channel.** What is red in the three
    exchange figures is *the copy arriving*, not the queue -- reddening four whole
    channels made the page shout and said the queue itself was the idea.

    A queue is a `pipe` here and not a `log`, and the distinction is load-bearing for
    §4.5 twenty slides later: a queue's messages leave it, a stream's never do. Drawing
    an AMQP queue as an append-only log would pre-empt the one comparison Day 1 spends
    its last sub-section building.
    """
    pipe = d.pipe(x, y, w, h)
    for i in range(n):
        d.msg(x + 34 + i * 42, y + h / 2 - 15, w=30, h=21, accent=accent)
    return pipe


def exchange(d, x, y, w=230, h=110, label="Exchange"):
    """The exchange: one named box, and nothing inside it.

    **A binding is a relationship, so it is drawn as an EDGE and never as a shape.**
    Two earlier attempts got this wrong in the same way the original did -- the original
    hung a "Recipient List" cylinder off the exchange, and the first draft here nested a
    `bindings` box inside a `group`. Both say the routing table is an object the
    exchange consults. It is not: a binding *is* the arrow, it carries the routing key
    as its label, and an exchange with no arrows leaving it drops everything.

    Drawing it as an edge also fixes three defects at once -- `group` labels are COMMENT
    green by house convention, which mis-coloured every primitive name; arrows leaving a
    nested box crossed their own container's border; and the routing key finally sits on
    the binding it belongs to rather than floating beside a queue mouth.
    """
    return d.box(x, y, w, h, label)


# ---- 1 -- the primitives, and what each one is ------------------------------

@figure("rmq-primitives")
def primitives():
    """The mapping figure, and the only one of the five whose subject is the mapping
    itself: three AMQP primitives on the top line, the pattern each one *is* on the
    bottom. It is the figure that earns the Quick Start its place at §4.2 -- the room
    has just been taught channels and routers abstractly, and this says which AMQP noun
    is which.

    **Two rows, two colours, and that is the whole design.** INK names the primitive
    because it names a shape in the picture; COMMENT names the pattern because it is our
    remark about that shape. The original used a fifth colour -- blue -- for the pattern
    row and black for the primitive row, which is two more colours than the palette has
    and no statement about what either row is.

    **The `Durable` panel is demoted to the foot, and corrected.** It was a second
    heading-and-paragraph block at the top, competing with the figure's actual subject.
    It also stopped one clause short of the thing that catches people: the presenter
    note already says *a message survives a restart only if it was published persistent,
    not because the queue is durable*, and that is the half worth drawing.
    """
    # **The horizontal runs are tight on purpose.** Drawn wider, this figure pinned
    # `compact` at `K_FLOOR` -- the geometry could not shrink far enough to reach 890
    # effective units, so it landed at 894 and every label read 17.9pt. Distance
    # carries no information, so it is the right thing to spend; the four gaps here
    # are the smallest that still let each arrow's head clear the label beside it.
    d = Diagram("RabbitMQ Primitives", w=1450, h=604)
    d.note(725, 44, "a binding is what makes an exchange a router -- "
                    "with none, it drops everything it is given", ANNOTATION, 21)

    prod = d.box(40, 232, 178, 86, "Producer")
    chan = d.pipe(286, 249, 186, 56)
    d.msg(344, 266, w=34, h=24)
    ex = exchange(d, 556, 220, 236, 110, "Exchange")

    qs, cons = [], []
    for i, y in enumerate((124, 246, 368)):
        qs.append(rmq_queue(d, 904, y, w=196, h=62, n=2))
        cons.append(d.box(1222, y + 4, 190, 54, f"Consumer {i + 1}"))

    d.arrow(prod, chan, sides=("r", "l"))
    d.arrow(chan, ex, sides=("r", "l"))
    for q, c in zip(qs, cons):
        # the bindings ARE these three arrows, and they carry the figure's one red
        d.arrow(ex, q, accent=True, sides=("r", "l"))
        d.arrow(q, c, sides=("r", "l"))

    # two mapping rows: INK names the primitive, COMMENT names the pattern it is.
    # **`bindings` belongs in the top row, not on an arrow.** Labelling the middle
    # binding directly put a 62-unit label in a 66-unit gap and lint caught it sitting
    # on the Exchange -- and the figure is height-fitted, so widening the gap to make
    # room would have cost nothing in legibility but a lot in balance. Naming it up
    # here is the better drawing anyway: the AMQ model has THREE primitives, and this
    # is the row that names them, so the row was incomplete while a binding was not on it.
    d.note(379, 218, "a channel", INK, 17)
    d.note(848, 104, "bindings", INK, 17)
    d.note(1002, 98, "queues", INK, 17)

    d.note(379, 344, "Channel", COMMENT, 17)
    d.note(674, 366, "Dynamic Router", COMMENT, 17)
    d.note(1002, 466, "Channel", COMMENT, 17)

    # wrapped, and the wrap is what makes the figure legible: a single line of this
    # length is the widest label on the canvas, so `compact` clamps on it and stops at
    # 894 -- four units wide of target, and every label 0.1pt under the floor for it
    d.note(725, 540, "durable is about the DEFINITION surviving a restart --\n"
                     "a message survives only if it was published persistent",
           COMMENT, 16)
    return d


# ---- 2 -- the four declare steps ---------------------------------------------

@figure("rmq-declare-flow")
def declare_flow():
    """*What your client does before it can send anything.* Four steps, left to right.

    **The four red prose panels are gone and one red sentence replaces them.** The
    original set every one of the four commentaries in red inside a red-ruled box, which
    by this deck's rule means the figure is doing four jobs. It is doing one: the client
    declares its own infrastructure, and the *bind* is the step that actually joins the
    two halves -- the other three only bring things into existence.

    The prose those panels carried is not lost: it is the presenter notes' job, and the
    notes on this slide already carry every sentence of it. Baking 120 words into a PNG
    fights the 18pt floor and cannot be revised without a redraw.
    """
    d = Diagram("Declaring What You Need", w=1500, h=520)
    d.note(750, 40, "the client declares its own infrastructure --\n"
                    "and binding is the step that joins the two", ANNOTATION, 21)

    steps = (
        ("Connect", "one TCP connection,\nmany cheap channels", False),
        ("Declare an\nExchange", "the routing table --\none per routing scope", False),
        ("Declare a\nQueue", "FIFO, and a read message\nis locked until it is acked",
         False),
        ("Bind", "a routing key joins\nthe queue to the exchange", True),
    )
    boxes = []
    for i, (name, gloss, red) in enumerate(steps):
        x = 60 + i * 360
        # r=22, not the default 13, and it is a LEGIBILITY fix rather than a
        # cosmetic one. `compact`'s label-fit clamp is `(advance + 12) / w`, and on a
        # 26-unit step circle carrying an 8-unit digit that is 0.77 -- so `k` could
        # never go below 0.77 and the figure stuck at 1116 wide, every label at
        # 14.4pt. The +12 is box padding; on a marker this small it is half the
        # shape. Widening the circle to 44 units drops the clamp under `K_FLOOR`.
        # ⚑ Fixed HERE and not in `diagram.py`: `paper_flow` draws seven steps of its
        # own, and changing the shared clamp would recompact them -- rule 5.
        d.step(x + 26, 190, i + 1, r=22)
        boxes.append(d.box(x, 216, 260, 96, name, accent=red))
        d.note(x + 130, 356, gloss, COMMENT, 16)

    for a, b in zip(boxes, boxes[1:]):
        d.arrow(a, b, sides=("r", "l"))

    d.note(750, 470, "re-declaring something that already exists is fine,\n"
                     "as long as every parameter agrees", COMMENT, 16)
    return d


# ---- 3, 4, 5 -- the three exchange types -------------------------------------

PITCH = 116   # queue-to-queue, and it is set by the BINDING LABELS, not the queues


def exchange_stage(title, red, queues, published, foot):
    """The apparatus all three exchange figures share: a producer, the key it publishes
    with, the exchange, and a column of queues each reached by a labelled binding.

    `queues` is a list of `(routing_key, gets_a_copy)`. Drawing the queues that do
    **not** get a copy is the whole reason the three figures differ on the page --
    `eip-recipient-list` learned this the same way: *"the pattern only becomes visible
    when one of the channels that exists does not get a copy."* The original drew four
    queues and four arrows for *direct* and three of each for *fanout*, which made them
    the same picture with a different caption.

    **All three carry the SAME THREE QUEUES**, and that is deliberate: the reader is
    meant to compare across the figures, so the only thing allowed to differ between
    them is which arrows fire. Direct binds two queues to one key because sharing a key
    is its particular point; default and fanout name three distinct keys. Fanout's keys
    are real and are ignored anyway, which is a truer picture of the mechanism than
    three queues all labelled "bound" -- AMQP lets you bind to a fanout WITH a key, and
    it still goes everywhere.

    **The canvas height is computed, not chosen.** Dead vertical space is the silent
    way a figure loses label size -- it is squarer, so it is fitted by the stage's
    height and `compact` gives back what the width bought. One earlier figure was
    17.6pt and the whole difference was 104 units of nothing above its foot comment.
    """
    n = len(queues)
    top = 96
    mid = top + (n * PITCH - PITCH + 62) / 2          # centre of the queue column
    h = top + n * PITCH + 58
    d = Diagram(title.replace("\n", " "), w=1320, h=h)

    d.note(660, 44, red, ANNOTATION, 21)
    prod = d.box(40, mid - 43, 176, 86, "Producer")
    ex = exchange(d, 452, mid - 55, 228, 110, title)
    d.arrow(prod, ex, published, sides=("r", "l"), ly=-17)

    for i, (key, taken) in enumerate(queues):
        y = top + i * PITCH
        q = rmq_queue(d, 906, y, w=196, h=62, n=2 if taken else 0, accent=taken)
        # **The key sits over its QUEUE, not on its arrow.** Riding the arrow was the
        # obvious reading -- a routing key labels a binding -- and on the page it
        # failed: four arrows fanning from one box have midpoints far closer together
        # than the queues they reach, so the labels bunched in the middle and stopped
        # saying which queue was which. Centred above the pipe they are unambiguous,
        # and the left edge stays clear for the arrow arriving there.
        d.note(1004, y - 14, key, INK, 16)
        d.arrow(ex, q, sides=("r", "l"),
                accent=taken, muted=not taken, dashed=not taken)

    d.note(660, h - 26, foot, COMMENT, 16)
    return d


@figure("rmq-direct-exchange")
def direct_exchange():
    """Direct: the routing key is an **address**, and every queue bound to that address
    gets a copy. Red is the match.

    **One queue is bound to a different key and gets nothing**, which the original did
    not show -- it drew four queues and four arrows, making direct and fanout the same
    picture with a different caption. The pattern is only visible when a queue that
    exists is passed over.
    """
    return exchange_stage(
        "Direct\nExchange",
        "a direct exchange copies to EVERY queue bound to that routing key -- "
        "the key is an address, not a queue",
        [("orders", True), ("orders", True), ("payments", False)],
        "routing key: orders",
        "bind two queues to one key and both get it -- "
        "which is a recipient list, not point-to-point",
    )


@figure("rmq-default-exchange")
def default_exchange():
    """Default: every queue is bound to the nameless exchange under its own name, for
    free, at the moment it is declared. Red is that the key **is** the queue's name.

    This is the figure the room needs for point-to-point, and the original said so in a
    black side panel. It is the foot comment here, because it is a remark about the
    drawing rather than a second subject in it.
    """
    return exchange_stage(
        "(default)\nnameless",
        "the routing key IS the queue's own name -- nobody bound anything by hand",
        [("orders", True), ("payments", False), ("shipping", False)],
        "routing key: orders",
        "RMQ routes through an exchange in every topology, so this is as close as "
        "AMQP gets to point-to-point: exactly one queue, every time",
    )


@figure("rmq-fanout-exchange")
def fanout_exchange():
    """Fanout: the routing key is **ignored**. Red is the ignoring, which is the only
    thing separating this figure from `rmq-direct-exchange`.

    The consumer binds to the *exchange* rather than to a key, so there is nothing to
    get wrong and nothing to match -- which is why the published key is drawn empty.
    """
    return exchange_stage(
        "Fanout\nExchange",
        "a fanout exchange IGNORES the routing key -- bind to it and you get everything",
        [("orders", True), ("payments", True), ("shipping", True)],
        "routing key: (empty)",
        "every bound queue receives each message, so this is publish-subscribe -- "
        "subscribe by binding, unsubscribe by unbinding",
    )


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
